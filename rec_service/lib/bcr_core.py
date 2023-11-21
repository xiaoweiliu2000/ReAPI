import torch
import torch.nn as nn
from lib.bcr_utils import *
from lib.bcr_config import *
import copy 
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, roc_auc_score, log_loss
from lib.bcn import BilateralComplementaryNetwork
import os
import joblib

class bcrBackendService():
    def __init__(self, flag_retrain_model=False, flag_use_cache=True, test_size = 0.05, compress_level=3, featType_enabled = ['oneHot', 'multiHot'], device='cpu'):
        self.encoderDict = {}
        self.model_bilateral = None
        self.model_mashup = None
        self.model_api = None
        self.apiData = None
        self.mashupData = None
        self.featType_enabled = featType_enabled
        self.featPosDict = {}
        self.maxTargetAPINum = 0

        # 查看是否已经有训练好的模型
        flag_check = True
        for m in MODEL_PATHS:
            if not os.path.exists(MODEL_PATHS[m]):
                flag_check = False
                break
        if not os.path.exists(DICT_PATH):
            flag_check = False
        
        # 训练不同场景下的模型并保存
        if (flag_retrain_model or not flag_check) or not flag_use_cache:
            print('> train models')
            # 训练不同场景下的模型
            model_bilateral, model_mashup, model_api, encoderDict, featPosDict, maxTargetAPINum = train_model(testSize=test_size, featType_enabled=self.featType_enabled, targetDevice=device)
            self.model_bilateral = model_bilateral
            self.model_mashup = model_mashup
            self.model_api = model_api
            self.encoderDict = encoderDict
            self.featPosDict = featPosDict
            self.maxTargetAPINum = maxTargetAPINum
            # 保存检查点
            try:
                joblib.dump(self.model_bilateral, MODEL_PATHS['bilateral'], compress=compress_level)
                joblib.dump(self.model_mashup, MODEL_PATHS['mashup'], compress=compress_level)
                joblib.dump(self.model_api, MODEL_PATHS['api'], compress=compress_level)
                joblib.dump([self.encoderDict, self.featPosDict, self.maxTargetAPINum], DICT_PATH, compress=compress_level)
            except Exception as e:
                print(str(e))
                exit(1)
        else:
            print('> load models')
            try:
                self.model_bilateral = joblib.load(MODEL_PATHS['bilateral'])
                self.model_mashup = joblib.load(MODEL_PATHS['mashup'])
                self.model_api = joblib.load(MODEL_PATHS['api'])
                self.encoderDict, self.featPosDict, self.maxTargetAPINum = joblib.load(DICT_PATH)
            except Exception as e:
                print(str(e))
                exit(1)

        # # 若使用cuda，将模型预载至显存中 多进程使用有bug
        # self.model_bilateral.to(torch.device(device))
        # self.model_mashup.to(torch.device(device))
        # self.model_api.to(torch.device(device))
            
        # 读取数据库
        print('> load database')
        try:
            if flag_use_cache and os.path.exists(DATASET_BIN_PATHs['apiData']) and os.path.exists(DATASET_BIN_PATHs['mashupData']):
                self.mashupData = joblib.load(DATASET_BIN_PATHs['mashupData'])
                self.apiData = joblib.load(DATASET_BIN_PATHs['apiData'])
            else:
                with open(DATASET_PATHs['apiData']) as fd:
                    self.apiData = json.load(fd)
                with open(DATASET_PATHs['mashupData']) as fd:
                    self.mashupData = json.load(fd)
                self.__cleanData()
                joblib.dump(self.mashupData, DATASET_BIN_PATHs['mashupData'], compress=compress_level)
                joblib.dump(self.apiData, DATASET_BIN_PATHs['apiData'], compress=compress_level)
        except Exception as e:
            print(e)
            exit(1)
        
        # 预编码（云API）
        print('> pre-encode')
        try:
            if flag_use_cache and os.path.exists(PRE_ENCODING_PATH):
                self.apiEncodingDict = joblib.load(PRE_ENCODING_PATH)
            else:
                self.apiEncodingDict = self.__preEncoding4api()
                joblib.dump(self.apiEncodingDict, PRE_ENCODING_PATH, compress=compress_level)
        except Exception as e:
            print(e)
            exit(1)

        print('> Initialize complete.')

    def recommend(self, K=10, mashupInfo = None, targetApiList = None, device='cpu', flagShowStatus=False, mode='minimal'):
        '''
            mashupInfo : dict
            targetApiList : list
            mode : str : minimal-只推荐被调用过的云API full-推荐全部云API
        '''
        # 检查目标云API列表的合法性
        if targetApiList is not None:
            newTargetApiList = []
            fullApiList = []
            for ad in self.apiData:
                fullApiList.append(ad['ApiName'])
            for api in targetApiList:
                if api in fullApiList and api not in newTargetApiList:
                    newTargetApiList.append(api)
            targetApiList = newTargetApiList

        if not len(targetApiList):
            targetApiList = None

        if flagShowStatus:
            print('--- input display ---')
            print('1. mashup information')
            print(mashupInfo)
            print('2. target cloud API list')
            print(targetApiList)
            print('---------------------')
            print('> generate recommendation result')

        # 使用模型预测全体云API的被调用概率
        if mashupInfo is not None and targetApiList is not None:
            model= self.model_bilateral
        elif mashupInfo is None and targetApiList is not None:
            model = self.model_api
        elif mashupInfo is not None and targetApiList is None:
            model = self.model_mashup
        else:
            model = self.model_bilateral
        # model.flagDebug = True
        invokeProbabilityList = self.__predict(model, mashupInfo, targetApiList, apiEncodingDict=self.apiEncodingDict, device=device, mode=mode)

        if np.isnan(invokeProbabilityList[0]): # 预测出错
            recList = []
            raise Exception("Internal errors (NaN) occurred during recommendation.")
            return recList

        # 生成推荐列表
        sortIndex = np.array(np.argsort(-invokeProbabilityList))
        if mode == 'full':
            sortList = np.array(self.apiData)[sortIndex]
        else:
            minimalApiData = []
            for ad in self.apiData:
                if ad['Invoked']:
                    minimalApiData.append(ad)
            sortList = np.array(minimalApiData)[sortIndex]
        recList = []
        if targetApiList is not None: # 保证推荐列表里没有目标云API
            count = 0
            for i in range(sortList.shape[0]):
                if sortList[i]['ApiName'] not in targetApiList:
                    recList.append(sortList[i])
                    count += 1
                    if count >= K:
                        break
        else:
            recList = list(sortList[:K])
        return recList
   
    def __cleanData(self):
        '''
            清洗api与mashup源数据
        '''
        # 重复的Mashup/API
        duplicateMashupList = []
        duplicateAPIList = []
        newMashupData = {}
        for md in self.mashupData:
            if md['Name'] in newMashupData:
                duplicateMashupList.append(md)
            newMashupData[md['Name']] = md
        newApiData = {}
        for ad in self.apiData:
            if ad['Name'] in newApiData:
                duplicateAPIList.append(ad)
            newApiData[ad['Name']] = ad

        # 数据清洗 Part 1
        invokedAPIList = [] # 被Mashup调用过的API
        APIList = []

        # 处理一下Related APIs
        for md in self.mashupData:
            md['APIs'] = md['Related APIs'].split(', ')
            for i in range(len(md['APIs'])):
                md['APIs'][i] = md['APIs'][i].strip()
                if md['APIs'][i] not in invokedAPIList:
                    invokedAPIList.append(md['APIs'][i])

        # 得到API列表
        for ad in self.apiData:
            if ad['Name'] not in APIList:
                APIList.append(ad['Name'])

        # 数据清洗 Part 2
        # 删除非法的API调用
        illegalMdList = []
        for md in self.mashupData:
            newList = []
            for i_api in md['APIs']:
                if i_api in APIList:
                    newList.append(i_api)
            md['APIs'] = newList
            if len(md['APIs']) == 0:
                illegalMdList.append(md)

        newMashupData = []
        for md in self.mashupData:
            if md not in illegalMdList:
                newMashupData.append(md)
        self.mashupData = newMashupData

        # 数据清洗 Part 3 
        # 处理标签
        for md in self.mashupData:
            md['TagList'] = md['Tags'].split(', ')
            for tag in md['TagList']:
                tag = tag.strip()
            md['Category'] = md['TagList'][0]
        for ad in self.apiData:
            ad['TagList'] = []
            if 'Primary Category' in ad:
                ad['TagList'].append(ad['Primary Category'])
            if 'Secondary Categories' in ad:
                ad['TagList'] += ad['Secondary Categories'].split(', ')
            for tag in ad['TagList']:
                tag = tag.strip()
        # 删除没有标签的API
        APIList = []
        newApiData = []
        for ad in self.apiData:
            if len(ad['TagList']):
                newApiData.append(ad)
                APIList.append(ad['Name'])
        self.apiData = newApiData

        for md in self.mashupData:
            newList = []
            for i_api in md['APIs']:
                if i_api in APIList:
                    newList.append(i_api)
            md['APIs'] = newList
            if len(md['APIs']) == 0:
                illegalMdList.append(md)
        newMashupData = []
        for md in self.mashupData:
            if md not in illegalMdList:
                newMashupData.append(md)
        self.mashupData = newMashupData

        # 给mashup和API编号
        for i in range(len(self.mashupData)):
            self.mashupData[i]['Id'] = i
        for i in range(len(self.apiData)):
            self.apiData[i]['Id'] = i

        # 特征名称转换
        for md in self.mashupData:
            oldFeat = list(md.keys())
            for feat in featTable['mashup']:
                if feat in md:
                    md[featTable['mashup'][feat]] = md[feat]
                else:
                    md[featTable['mashup'][feat]] = 'NULL'
            for feat in oldFeat:
                md.pop(feat)
        for ad in self.apiData:
            oldFeat = list(ad.keys())
            for feat in featTable['api']:
                if feat in ad:
                    ad[featTable['api'][feat]] = ad[feat]
                else:
                    ad[featTable['api'][feat]] = 'NULL'
            for feat in oldFeat:
                ad.pop(feat)

        # 为被调用过的云API做标记
        for ad in self.apiData:
            if ad['ApiName'] in invokedAPIList:
                ad['Invoked'] = True
            else:
                ad['Invoked'] = False

        print('number of mashups : ', len(self.mashupData))
        print('number of cloud APIs : ', len(self.apiData))
        return
    
    def __preEncoding4api(self):
        '''预计算云API的编码以加速
        '''
        apiFeatLen = 0
        for featType in self.featType_enabled:
            for feat in featDict['api'][featType]:
                apiFeatLen += self.featPosDict['c_' + feat][1] - self.featPosDict['c_' + feat][0]

        apiEncodingDict = {}
        startPos = -1
        for ad in self.apiData:
            newEncoding = np.zeros((apiFeatLen,), dtype=np.int8)
            for featType in self.featType_enabled:
                for feat in featDict['api'][featType]:
                    if startPos == -1:
                        startPos = self.featPosDict['c_' + feat][0]
                    newEncoding[self.featPosDict['c_' + feat][0]-startPos:self.featPosDict['c_' + feat][1]-startPos] = self.encoderDict[feat].transform([ad[feat]])[0]
            apiEncodingDict[ad['ApiName']] = newEncoding

        return apiEncodingDict

    # 生成推荐列表
    def __predict(self, model, mashupInfo = None, targetApiList = None, apiEncodingDict=None, batchSize=64, device='cpu', k=10, threadNum=1, mode='minimal'):
        '''对于所有的云API，生成对应输入，最终预测被调用概率

            Args:
                mode : str : minimal-只推荐被调用过的云API full-推荐全部云API

            Return:
                invokeProbabilityList : list[float] : 按照apiData顺序的被调用概率列表

                apiData, encoderDict, featPosDict, maxTargetAPINum, featType_enabled,
        '''
        # 初始化
        device_t = torch.device(device)
        model.to(device_t)
        model.device = torch.device(device)
        if mashupInfo is None:
            mashupInfo = {}
        if targetApiList is None:
            targetApiList = []
        # flagPreEncodeMashup = False
        # apiEncodingDict = None
        flagPreEncodeMashup = True

        # 初始化索引
        apiNameIndex = {}
        for i in range(len(self.apiData)):
            apiNameIndex[self.apiData[i]['ApiName']] = i
            
        # 建立rawDataList
        rawDataList = []
        for ad in self.apiData:
            # 若为minimal模式，跳过没有被调用过的云API
            if mode == 'minimal':
                if ad['Invoked'] == False:
                    continue

            # 构建rawData
            rawData = {}
            rawData['mashup'] = {}
            for featType in self.featType_enabled:
                for feat in featDict['mashup'][featType]:
                    if feat in mashupInfo:
                        rawData['mashup'][feat] = mashupInfo[feat]
                    else:
                        rawData['mashup'][feat] = None

            rawData['candidate API'] = ad
            if apiEncodingDict is not None: # 预编码
                rawData['candidate API encoding'] = apiEncodingDict[ad['ApiName']]

            rawData['target APIs'] = []
            if apiEncodingDict is not None:
                rawData['target API encodings'] = []
            for targetAPI in targetApiList:
                rawData['target APIs'].append(self.apiData[apiNameIndex[targetAPI]])
                if apiEncodingDict is not None: # 预编码
                    rawData['target API encodings'].append(apiEncodingDict[targetAPI])

            rawData['invoke'] = 0
            rawDataList.append(rawData)

        # 数据编码
        # start = time.time()
        data = np.array(encodeData_mp(rawDataList, self.encoderDict, self.maxTargetAPINum, featDict, self.featType_enabled, self.featPosDict, flagPreEncodeMashup))
        data = data[:,:-1]

        # end = time.time()
        # write_log('DEBUG', 'execution time (encoding) : {:.2f}s'.format(end-start), LOG_PATH)
    
        # 数据加载
        workerNum = 0
        torch.set_num_threads(threadNum) # 在docker环境指定运行核心时，必须设置为1以防止伪死锁
        tensor_data = TensorDataset(torch.from_numpy(data))
        data_loader = DataLoader(tensor_data, shuffle=False, batch_size=batchSize, num_workers=workerNum)

        # 模型预测
        # start = time.time()
        invokeProbabilityList = None
        model.eval()
        with torch.no_grad():
            for index, (x,) in enumerate(data_loader):
                x = x.to(device_t).float()
                y = model(x)
                if invokeProbabilityList is None:
                    invokeProbabilityList = y.cpu().data.numpy().flatten()
                else:
                    invokeProbabilityList = np.concatenate([invokeProbabilityList, y.cpu().data.numpy().flatten()])
        # end = time.time()
        # write_log('DEBUG', 'execution time (predicting) : {:.2f}s'.format(end-start), LOG_PATH)

        return invokeProbabilityList

def train_model(neg2pos=3, featType_enabled = ['oneHot', 'multiHot'], testSize=0.1, learningRate=5e-4, batchSize=128, targetDevice='cuda', weightDecay=1e-5, epochs=20, threadNum=4):
    # 数据读取与预处理
    print('data prepocess...')
    dataPath = DATA_HOME + 'dataset_unfixed(neg2pos={}).json'.format(neg2pos)
    data, featPosDict, encoderDict, maxTargetAPINum = dcr_preprocess(dataPath=dataPath, featDict=featDict, featType_enabled=featType_enabled)

    # 构建训练集与测试集
    print('generate training set...', end='')
    seed = 2023528
    train, test = train_test_split(data, test_size=testSize, random_state=seed)
    train_x = train[:,:-1]
    train_y = train[:,[-1]]
    test_x = test[:,:-1]
    test_y = test[:,[-1]]
    print('complete')

    # 加载数据
    print('load data...', end='')
    workerNum = 0
    torch.set_num_threads(threadNum)
    train_tensor_data = TensorDataset(torch.from_numpy(train_x), torch.from_numpy(np.array(train_y)))
    train_loader = DataLoader(train_tensor_data, shuffle=True, batch_size=batchSize, num_workers=workerNum)
    test_tensor_data = TensorDataset(torch.from_numpy(np.array(test_x)), torch.from_numpy(np.array(test_y)))
    test_loader = DataLoader(test_tensor_data, batch_size=batchSize, num_workers=workerNum)
    print('complete')

    # 双侧模型
    print('train bilateral BCN...')
    setup_seed(3086)
    poolingMethod = 'attention'
    model_bilateral = BilateralComplementaryNetwork(poolingMethod = poolingMethod, featDict=featDict, featPosDict=featPosDict, featType_enabled=featType_enabled, device=targetDevice).to(targetDevice)
    optimizer = torch.optim.Adam(params=model_bilateral.parameters(), lr=learningRate, weight_decay=weightDecay)
    loss_func = torch.nn.BCELoss().to(targetDevice)
    model_bilateral.flag_mask = True
    model_bilateral.enableAA = True
    model_bilateral.enableMA = True
    epochs = 20

    for epoch in range(epochs):
        model_bilateral.train()
        total_loss, total_len = 0, 0
        for index, (x, y) in enumerate(train_loader):
            x, y = x.to(targetDevice).float(), y.to(targetDevice).float()
            y_pre = model_bilateral(x)
            loss = loss_func(y_pre, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(y)
            total_len += len(y)
        train_loss = total_loss / total_len

        model_bilateral.eval()
        labels, predicts = [], []
        with torch.no_grad(): 
            for index, (x, y) in enumerate(test_loader):
                x, y = x.to(targetDevice).float(), y.to(targetDevice).float()
                y_pre = model_bilateral(x)
                labels.extend(y.tolist())
                predicts.extend(y_pre.tolist())
                rmse = np.sqrt(mean_squared_error(np.array(labels), np.array(predicts)))
                auc = roc_auc_score(np.array(labels), np.array(predicts))
                log_loss1 = log_loss(np.array(labels), np.array(predicts))  
        print("epoch {}, train loss is {}, val rmse is {}, val auc is {}, val log_loss is {}".format(epoch+1, train_loss, rmse, auc, log_loss1))

    # mashup侧模型
    print('train mashup-side BCN...')
    poolingMethod = 'attention'
    model_mashup = copy.deepcopy(model_bilateral)
    optimizer = torch.optim.Adam(params=model_mashup.parameters(), lr=learningRate, weight_decay=weightDecay)
    loss_func = torch.nn.BCELoss().to(targetDevice)
    setup_seed(3086)
    model_mashup.flag_mask = True
    model_mashup.enableAA = False
    model_mashup.enableMA = True
    epochs = 5

    for epoch in range(epochs):
        model_mashup.train()
        total_loss, total_len = 0, 0
        for index, (x, y) in enumerate(train_loader):
            x, y = x.to(targetDevice).float(), y.to(targetDevice).float()
            y_pre = model_mashup(x)
            loss = loss_func(y_pre, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(y)
            total_len += len(y)
        train_loss = total_loss / total_len

        model_mashup.eval()
        labels, predicts = [], []
        with torch.no_grad(): 
            for index, (x, y) in enumerate(test_loader):
                x, y = x.to(targetDevice).float(), y.to(targetDevice).float()
                y_pre = model_mashup(x)
                labels.extend(y.tolist())
                predicts.extend(y_pre.tolist())
                rmse = np.sqrt(mean_squared_error(np.array(labels), np.array(predicts)))
                auc = roc_auc_score(np.array(labels), np.array(predicts))
                log_loss1 = log_loss(np.array(labels), np.array(predicts))  
        print("epoch {}, train loss is {}, val rmse is {}, val auc is {}, val log_loss is {}".format(epoch+1, train_loss, rmse, auc, log_loss1))

    # 目标云API侧模型
    print('train target cloud API-side BCN...')
    poolingMethod = 'attention'
    model_api = copy.deepcopy(model_bilateral)
    optimizer = torch.optim.Adam(params=model_api.parameters(), lr=learningRate, weight_decay=weightDecay)
    loss_func = torch.nn.BCELoss().to(targetDevice)
    setup_seed(3086)
    model_api.flag_mask = True
    model_api.enableAA = True
    model_api.enableMA = False
    epochs = 5

    for epoch in range(epochs):
        model_api.train()
        total_loss, total_len = 0, 0
        for index, (x, y) in enumerate(train_loader):
            x, y = x.to(targetDevice).float(), y.to(targetDevice).float()
            y_pre = model_api(x)
            loss = loss_func(y_pre, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(y)
            total_len += len(y)
        train_loss = total_loss / total_len

        model_api.eval()
        labels, predicts = [], []
        with torch.no_grad(): 
            for index, (x, y) in enumerate(test_loader):
                x, y = x.to(targetDevice).float(), y.to(targetDevice).float()
                y_pre = model_api(x)
                labels.extend(y.tolist())
                predicts.extend(y_pre.tolist())
                rmse = np.sqrt(mean_squared_error(np.array(labels), np.array(predicts)))
                auc = roc_auc_score(np.array(labels), np.array(predicts))
                log_loss1 = log_loss(np.array(labels), np.array(predicts))  
        print("epoch {}, train loss is {}, val rmse is {}, val auc is {}, val log_loss is {}".format(epoch+1, train_loss, rmse, auc, log_loss1))

    return model_bilateral, model_mashup, model_api, encoderDict, featPosDict, maxTargetAPINum