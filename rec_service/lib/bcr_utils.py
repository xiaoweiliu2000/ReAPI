import json
import numpy as np
import pandas as pd
import torch
import time
import random
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer, LabelBinarizer
from multiprocessing import Queue, Process

def mpWorker(func, commonArgs, taskQueue:Queue, resQueue:Queue):
    while True:
        try:
            jobNum, args = taskQueue.get(timeout=1) # 一定要设超时，不然会永久阻塞
        except Exception as e: # while判断队列非空以后，进入get语句时，队列变空了
            break
        try:
            if commonArgs is None:
                res = func(*args)
            else:
                res = func(*(args+commonArgs))
            resQueue.put([jobNum, res])
        except:
            pass

def multiProcessFramework(func, argList, processNum:int, flag_show_progress=True, flag_merge_result=False, commonArgs:tuple=None, timeout=5):
    '''多进程执行指定函数的工具框架

        TODO: 加入batch 

        Args:
            func : function
                指定函数
            argList : list[tuple] 
                执行函数的参数列表，每项执行一次
            processNum : int
                进程数
            flag_show_progress : bool
                是否在命令行打印进度
            flag_merge_result : bool
                结果在归并时是否使用“+”，而不是append，这样会导致返回结果降低一个维
            commonArgs : tuple
                函数的公共参数
            timeout : int
                超时等待时间，若结果丢失可尝试调大

        Returns:
            resList : list[res]
                按照argList中的顺序返回对应结果
    '''
    resDict = {}
    # 创建任务队列
    taskQueue = Queue()
    jobNum = 0
    for args in argList:
        taskQueue.put([jobNum, args])
        jobNum += 1
    totalNum = len(argList)
    resQueue = Queue()
    processPool = []
    for i in range(processNum): 
        p = Process(target=mpWorker, args=(func, commonArgs, taskQueue, resQueue))
        processPool.append(p)
    for p in processPool:
        p.start()
    ## 等待子进程完成计算
    while not taskQueue.qsize() == 0:
        if flag_show_progress:
            num = taskQueue.qsize()
            print(' {}/{}  {}%'.format(totalNum - num, totalNum, int((totalNum-num)/totalNum*100)), end = '\r')
            time.sleep(0.01)
        if not resQueue.qsize() == 0:
            jobNum, res  = resQueue.get(timeout=timeout)
            resDict[jobNum] = res
        else:
            if not flag_show_progress:
                time.sleep(0.01)
    ## 读取多进程返回计算结果
    while True:
        try:
            jobNum, res = resQueue.get(timeout=timeout)
            resDict[jobNum] = res
        except:
            break
    ## 等待子进程结束
    for p in processPool:
        p.join()
    if flag_show_progress:
        print('{}/{}  {}%'.format(totalNum, totalNum, 100), end = '\r')
        print('')

    resList = []
    okFlag = True
    for i in range(totalNum):
        try:
            if flag_merge_result:
                resList += resDict[i]
            else:
                resList.append(resDict[i])
        except:
            print('[error] lost: ', i)
            okFlag = False
    if okFlag:
        return resList
    else:
        return None

def encodeData(rawData, encoderDict, maxTargetAPINum, featDict, featType_enabled, featPosDict, mashupEncoding=None):
    newData = np.zeros((featPosDict[list(featPosDict.keys())[-1]][1]+1,), dtype=np.int8)
    targetAPINum = len(rawData['target APIs'])
    if targetAPINum > maxTargetAPINum: 
        targetAPINum = maxTargetAPINum
    mashupFeatLen = 0
    apiFeatLen = 0
    for featType in featType_enabled:
        for feat in featDict['mashup'][featType]:
            mashupFeatLen += featPosDict[feat][1] - featPosDict[feat][0]
    for featType in featType_enabled:
        for feat in featDict['api'][featType]:
            apiFeatLen += featPosDict['c_' + feat][1] - featPosDict['c_' + feat][0]
    # 1. mashup encoding
    if mashupEncoding is not None:
        completeFlag = False
        for featType in featType_enabled:
            for feat in featDict['mashup'][featType]: 
                if not completeFlag:
                    newData[featPosDict[feat][0]:featPosDict[feat][0]+mashupFeatLen] = mashupEncoding
                    completeFlag = True
    else:
        for featType in featType_enabled:
            for feat in featDict['mashup'][featType]:
                if rawData['mashup'][feat]:
                    newData[featPosDict[feat][0]:featPosDict[feat][1]] = encoderDict[feat].transform([rawData['mashup'][feat]])[0]
                else:
                    newData[featPosDict[feat][0]:featPosDict[feat][1]] = np.zeros((featPosDict[feat][1] - featPosDict[feat][0],), dtype=np.int8)

    # 2. candidate cloud API encoding
    if 'candidate API encoding' in rawData:
        completeFlag = False
        for featType in featType_enabled:
            for feat in featDict['api'][featType]:
                if not completeFlag:
                    newData[featPosDict['c_' + feat][0]:featPosDict['c_' + feat][0]+apiFeatLen] = rawData['candidate API encoding']
                    completeFlag = True
    else:
        for featType in featType_enabled:
            for feat in featDict['api'][featType]:
                newData[featPosDict['c_' + feat][0]:featPosDict['c_' + feat][1]] = encoderDict[feat].transform([rawData['candidate API'][feat]])[0]

    # 3. target cloud API encoding
    if 'target API encodings' in rawData:
        for i in range(targetAPINum):
            completeFlag = False
            for featType in featType_enabled:
                for feat in featDict['api'][featType]:
                    if not completeFlag:
                        newData[featPosDict['t{}_{}'.format(i, feat)][0]:featPosDict['t{}_{}'.format(i, feat)][0]+apiFeatLen] = rawData['target API encodings'][i]
                        completeFlag = True
    else:
        for i in range(targetAPINum):
            for featType in featType_enabled:
                for feat in featDict['api'][featType]:
                    newData[featPosDict['t{}_{}'.format(i, feat)][0]:featPosDict['t{}_{}'.format(i, feat)][1]] = encoderDict[feat].transform([rawData['target APIs'][i][feat]])[0]

    # 4. padding, 若此mashup的目标API数量小于maxTargetAPINum，则在空缺位置填充0
    for i in range(targetAPINum, maxTargetAPINum):
        completeFlag = False
        for featType in featType_enabled:
            for feat in featDict['api'][featType]:
                if not completeFlag:
                    newData[featPosDict['t{}_{}'.format(i, feat)][0]:featPosDict['t{}_{}'.format(i, feat)][0] + apiFeatLen] = np.zeros((apiFeatLen,), dtype=np.int8)
                    completeFlag = True

    # 5. masking
    # [mask]构建每条数据对应的目标API mask，用来标记哪些目标API是真实数据(1)，哪些目标API是填充的(0)
    maskBits = np.concatenate([np.ones((targetAPINum,)), np.zeros((maxTargetAPINum - targetAPINum,), dtype=np.int8)])
    newData[featPosDict['targetApiMask'][0]:featPosDict['targetApiMask'][1]] = maskBits

    # 6. invoke
    newData[-1] = rawData['invoke']
    return newData

def encodeData_mp(rawDataList, encoderDict, maxTargetAPINum, featDict, featType_enabled, featPosDict, flagPreEncodeMashup=False):
    '''
        flagPreEncodeMashup: 当待编码数据中所有数据条的mashup都一致时，对mashup进行预编码以加速
    '''
    mashupEncoding = None
    if flagPreEncodeMashup: # 预编码mashup
        mashupFeatLen = 0
        for featType in featType_enabled:
            for feat in featDict['mashup'][featType]:
                mashupFeatLen += featPosDict[feat][1] - featPosDict[feat][0]
        mashupEncoding = np.zeros((mashupFeatLen,), dtype=np.int8)
        startPos = -1
        rawData = rawDataList[0]
        for featType in featType_enabled:
            for feat in featDict['mashup'][featType]:
                if startPos == -1:
                    startPos = featPosDict[feat][0]
                if rawData['mashup'][feat]:
                    mashupEncoding[featPosDict[feat][0]-startPos:featPosDict[feat][1]-startPos] = encoderDict[feat].transform([rawData['mashup'][feat]])[0]
                else:
                    mashupEncoding[featPosDict[feat][0]-startPos:featPosDict[feat][1]-startPos] = np.zeros((featPosDict[feat][1] - featPosDict[feat][0],), dtype=np.int8)          
    resList = []
    for rawData in rawDataList:
        resList.append(encodeData(rawData, encoderDict, maxTargetAPINum, featDict, featType_enabled, featPosDict, mashupEncoding))
    return resList

def dcr_preprocess(dataPath, featDict, featType_enabled = ['oneHot', 'multiHot']):
    # 读取数据集
    with open(dataPath, 'r') as fd:
        rawDataset = json.load(fd)

    # 统计最大目标API数量
    maxTargetAPINum = 0
    for rd in rawDataset:
        if len(rd['target APIs']) > maxTargetAPINum:
            maxTargetAPINum = len(rd['target APIs'])

    # 特征编码
    # 1、对特征进行汇总
    encodeFeatTypeList = {'oneHot', 'multiHot', 'text'} # 需要编码的特征类型列表
    sumdata = {} 

    for rawData in rawDataset:              
        # mashup
        obj = 'mashup'
        for featType in encodeFeatTypeList:
            for feat in featDict[obj][featType]:
                value = rawData['mashup'][feat]
                if feat not in sumdata:
                    sumdata[feat] = []
                sumdata[feat].append(value)
        # api
        obj = 'api'
        ## candidate api
        for featType in encodeFeatTypeList:
            for feat in featDict[obj][featType]:
                if feat not in sumdata:
                    sumdata[feat] = []
                sumdata[feat].append(rawData["candidate API"][feat])
        ## target apis
        targetApiNum = len(rawData['target APIs'])
        if targetApiNum > maxTargetAPINum: targetApiNum = maxTargetAPINum
        for featType in encodeFeatTypeList:
            for feat in featDict[obj][featType]:
                for i in range(targetApiNum):
                    if feat not in sumdata:
                        sumdata[feat] = []
                    sumdata[feat].append(rawData["target APIs"][i][feat])
        # invoke
        feat = 'invoke'
        value = rawData[feat]
        if feat not in sumdata:
            sumdata[feat] = []
        sumdata[feat].append(value)

    # 2、训练编码器
    encoderDict = {} # 编码器字典
    for feat in featDict['mashup']['oneHot']:
        encoderDict[feat] = LabelBinarizer()
        encoderDict[feat].fit(sumdata[feat])
    for feat in featDict['api']['oneHot']:
        encoderDict[feat] = LabelBinarizer()
        encoderDict[feat].fit(sumdata[feat])
    for feat in featDict['mashup']['multiHot']:
        encoderDict[feat] = MultiLabelBinarizer()
        encoderDict[feat].fit(sumdata[feat])
    for feat in featDict['api']['multiHot']:
        encoderDict[feat] = MultiLabelBinarizer()
        encoderDict[feat].fit(sumdata[feat])
    # 文本编码(暂时不处理)

    # 构建数据集
    # 构造feat_sizes特征查找表
    featPosDict = {} # 记录每个特征对应向量的起始与结束位置([startPos, endPos])，此后可通过startPos:endPos访问此特征 
    featPos = 0    # 辅助变量
    rd = rawDataset[0]
    # mashup
    for featType in featType_enabled:
        for feat in featDict['mashup'][featType]:
            featLen = encoderDict[feat].transform([rd['mashup'][feat]])[0].shape[0]
            featPosDict[feat] = [featPos, featPos + featLen]
            featPos += featLen
    # for feat in featDict['mashup']['dense']:
    #     featPosDict[feat] = [featPos, featPos + 1]
    #     featPos += 1
    # 候选API
    for featType in featType_enabled:
        for feat in featDict['api'][featType]:
            featLen = encoderDict[feat].transform([rd['candidate API'][feat]])[0].shape[0]
            featPosDict['c_' + feat] = [featPos, featPos + featLen]
            featPos += featLen
    # 目标API
    for i in range(maxTargetAPINum):
        for featType in featType_enabled:
            for feat in featDict['api'][featType]:
                featLen = encoderDict[feat].transform([rd['target APIs'][0][feat]])[0].shape[0]
                featPosDict['t{}_'.format(i) + feat] = [featPos, featPos + featLen]
                featPos += featLen
        # for feat in featDict['api']['dense']:
        #     featPosDict['t{}_'.format(i) + feat] = [featPos, featPos + 1]
        #     featPos += 1
    # targetApiMask
    featLen = maxTargetAPINum
    featPosDict['targetApiMask'] = [featPos, featPos + featLen]
    featPos += featLen

    # 3、编码并构建数据集
    argList = []
    inputLen = 100
    for i in range(0, len(rawDataset), inputLen):
        if i + inputLen < len(rawDataset):
            argList.append((rawDataset[i:i+inputLen],))
        else:
            argList.append((rawDataset[i:len(rawDataset)],))
    data = None
    while data is None:
        data = multiProcessFramework(func=encodeData_mp, argList=argList, processNum=24, flag_show_progress=True, flag_merge_result=True, commonArgs=(encoderDict, maxTargetAPINum, featDict, featType_enabled, featPosDict))
    data = np.array(data)
    return data, featPosDict, encoderDict, maxTargetAPINum

class myMultiLabelEncoder():
    def __init__(self) -> None:
        self.labelList = []  # 标签最大的种类数
        self.maxLabelNum = 0 # 一组多标签内最大的标签数量

    def fit(self, y):
        self.labelList = []
        self.maxLabelNum  = 0
        for multiLabels in y:
            if len(multiLabels) > self.maxLabelNum:
                self.maxLabelNum = len(multiLabels)
            for label in multiLabels:
                if label not in self.labelList:
                    self.labelList.append(label)

    def transform(self, y):
        result = []
        for i in range(len(y)):
            newLabels = []
            for j in range(self.maxLabelNum):
                if j < len(y[i]):
                    newLabels.append(self.labelList.index(y[i][j]) + 1)
                else:
                    newLabels.append(0)
            result.append(newLabels)
        return np.array(result)

    def fit_transform(self, y):
        self.fit(y)
        result = self.transform(y)
        return result

def dcr_preprocess_se(dataPath, fixedTargetAPINum, featDict, featType_enabled = ['oneHot', 'multiHot']):
    '''deepctr专用版

        input : 
            dataPath : str
            fixedTargetAPINum : int : 要读取的数据集中的固定目标API数量，为0时会做特殊对齐处理

        return :
            data
            multiHotLenDict
            maxTargetAPINum : 对齐后的最大（固定）目标API数量
    '''
    # 读取数据集
    with open(dataPath, 'r') as fd:
        rawDataset = json.load(fd)

    if fixedTargetAPINum == 0:
        # 统计数据集中最大的目标API数量
        maxTargetAPINum = 0
        for rawData in rawDataset:
            if len(rawData['target APIs']) > maxTargetAPINum:
                maxTargetAPINum = len(rawData['target APIs'])
    else:
        maxTargetAPINum = fixedTargetAPINum

    data = {} 
    for rawData in rawDataset:
        # mashup
        obj = 'mashup'
        for featType in featDict[obj]:
            for feat in featDict[obj][featType]:
                value = rawData['mashup'][feat]
                if feat not in data:
                    data[feat] = []
                data[feat].append(value)
        # api
        obj = 'api'
        ## candidate api
        for featType in featDict[obj]:
            for feat in featDict[obj][featType]:
                if 'CC' in feat:
                    continue
                value = rawData["candidate API"][feat]
                featName = 'c_' + feat
                if featName not in data:
                    data[featName] = []
                data[featName].append(value)
        ## target apis
        if fixedTargetAPINum:
            for i in range(fixedTargetAPINum): # 这里不写死，且目标云API数量不固定的话，后面会错位
                for featType in featDict[obj]:
                    for feat in featDict[obj][featType]:
                        value = rawData["target APIs"][i][feat]
                        featName = 't{}_'.format(i) + feat
                        if featName not in data:
                            data[featName] = []
                        data[featName].append(value)
        else:
            for i in range(maxTargetAPINum):
                for featType in featDict[obj]:
                    for feat in featDict[obj][featType]:
                        if len(rawData['target APIs']) > i:
                            value = rawData["target APIs"][i][feat]
                        else: 
                            value = rawData["target APIs"][0][feat]
                            if type(value) == int:
                                value = -1
                            elif type(value) == str:
                                value = 'None'
                            elif type(value) == list:
                                value = ['None']
                            elif type(value) == float:
                                value = 0
                            else:
                                print('undefined value type in dcr_preprocess_se')
                        featName = 't{}_'.format(i) + feat
                        if featName not in data:
                            data[featName] = []
                        data[featName].append(value) 

        # invoke
        feat = 'invoke'
        value = rawData[feat]
        if feat not in data:
            data[feat] = []
        data[feat].append(value)

    # 特征编码(oneHot)
    oneHotFeatures = []
    oneHotFeatures += featDict['mashup']['oneHot']
    for feat in featDict['api']['oneHot']:
        oneHotFeatures.append('c_' + feat)
    if fixedTargetAPINum:
        for i in range(fixedTargetAPINum):
            for feat in featDict['api']['oneHot']:
                oneHotFeatures.append('t{}_{}'.format(i, feat))
    else:
        for i in range(maxTargetAPINum):
            for feat in featDict['api']['oneHot']:
                oneHotFeatures.append('t{}_{}'.format(i, feat))
    for feat in oneHotFeatures:
        lbe = LabelEncoder()
        data[feat] = lbe.fit_transform(data[feat])

    # 特征编码(multiHot)
    multiHotFeatures = []
    multiHotLenDict = {}
    multiHotFeatures += featDict['mashup']['multiHot']
    for feat in featDict['api']['multiHot']:
        multiHotFeatures.append('c_' + feat)
    if fixedTargetAPINum:
        for i in range(fixedTargetAPINum):
            for feat in featDict['api']['multiHot']:
                multiHotFeatures.append('t{}_{}'.format(i, feat))
    else:
        for i in range(maxTargetAPINum):
            for feat in featDict['api']['multiHot']:
                multiHotFeatures.append('t{}_{}'.format(i, feat))
    for feat in multiHotFeatures:
        mlbe = myMultiLabelEncoder()
        data[feat] = mlbe.fit_transform(data[feat])
        multiHotLenDict[feat] = [len(mlbe.labelList), mlbe.maxLabelNum]

    return data, multiHotLenDict, maxTargetAPINum

def my_shuffle(data, random_state=None):
    originState = random.getstate()
    random.seed(random_state)

    newDataIndex = []
    for key in data:
        dataIndex = list(range(len(data[key])))
        break
    while len(dataIndex):
        i = random.randint(0, len(dataIndex)-1)
        newDataIndex.append(dataIndex.pop(i))

    newData = {}
    for i in newDataIndex:
        for key in data:
            if key not in newData:
                newData[key] = [data[key][i]]
            else:
                newData[key].append(data[key][i])

    random.setstate(originState)
    return newData

def my_train_test_split(data, test_size, random_state=None, flag_shuffle=True):
    originState = random.getstate()
    train = []
    test = []

    if flag_shuffle:
        data = my_shuffle(data, random_state=random_state)

    # 随机生成训练集与测试集索引
    random.seed(random_state)
    for key in data:
        trainIndexList = list(range(len(data[key])))
        count = int(test_size * len(data[key]))
        break
    testIndexList = []
    while count > 0:
        i = random.randint(0, len(trainIndexList)-1)
        testIndexList.append(trainIndexList.pop(i))
        count -= 1

    # 生成训练集与测试集
    train = {}
    test = {}
    for i in trainIndexList:
        for key in data:
            if key not in train:
                train[key] = [data[key][i]]
            else:
                train[key].append(data[key][i])
    for i in testIndexList:
        for key in data:
            if key not in test:
                test[key] = [data[key][i]]
            else:
                test[key].append(data[key][i])

    # 转成np.array
    for key in data:
        train[key] = np.array(train[key])
        test[key] = np.array(test[key])

    random.setstate(originState)
    return train, test

def get_hit(y_true, y_pred, k):
    '''计算此列表中是否有命中项目(hit@k)

        Args:
            y_true : list : 真实值列表
            y_pred : list : 预测值列表
            k : int : @k
        
        Return:
            bool : 0/1
    '''
    # 排序后判断是否命中
    df = pd.DataFrame({"y_pred":y_pred, "y_true":y_true})
    df = df.sort_values(by="y_pred", ascending=False) 
    df = df.iloc[0:k, :]  
    df = df.to_numpy()
    for i in range(k):
        if df[i][1] == 1:
            return 1
    return 0
'''
    在变长阶数的场景中，由于只有一个mashup真实调用过的API可以作为候选API，y_true中最多只有一个1
    这会导致topk中能够命中的个数最大为1，进而recall@k与hit@k等价，且precision@k的最大值被限制在1/k
    因此最多计算hit@k/HR@k即可。即变长阶数场景下只适合计算排序指标中的命中率指标，且命中率指标一定会偏低，因为可供命中的项目只有一个
'''

def get_ndcg(y_true, y_pred, k):
    '''计算此列表的ndcg@k

        Args: 
            y_true : list : 真实值列表
            y_pred : list : 预测值列表
            k : int : @k
    '''
    def _get_dcg(y_true, y_pred, k):
        df = pd.DataFrame({"y_pred":y_pred, "y_true":y_true})
        df = df.sort_values(by="y_pred", ascending=False)  # 对y_pred进行降序排列，越排在前面的，越接近label=1
        df = df.iloc[0:k, :]  # 取前K个
        dcg = 0
        i = 1
        for y_true_i in df["y_true"]:
            dcg += (2 ** y_true_i - 1) / np.log2(1 + i)
            i += 1
        return dcg

    dcg = _get_dcg(y_true, y_pred, k)
    idcg = _get_dcg(y_true, y_true, k)
    ndcg = dcg / idcg
    return ndcg

def get_precision(y_true, y_pred, k):
    '''计算此列表的准确率(precision@k)

        Args:
            y_true : list : 真实值列表
            y_pred : list : 预测值列表
            k : int : @k
        
        Return:
            float
    '''
    df = pd.DataFrame({"y_pred":y_pred, "y_true":y_true})
    df = df.sort_values(by="y_pred", ascending=False) 
    df = df.iloc[0:k, :]  
    df = df.to_numpy()
    count0 = 0 # 分子是topk中命中的个数
    count1 = k # 分母是k
    for i in range(k):
        if df[i][1]:
            count0 += 1
    return count0 / count1

def get_recall(y_true, y_pred, k):
    '''计算此列表的召回率(recall@k)

        Args:
            y_true : list : 真实值列表
            y_pred : list : 预测值列表
            k : int : @k
        
        Return:
            float
    '''
    df = pd.DataFrame({"y_pred":y_pred, "y_true":y_true})
    df = df.sort_values(by="y_pred", ascending=False) 
    df = df.iloc[0:k, :]  
    df = df.to_numpy()
    count0 = 0 # 分子是topk中命中的个数
    count1 = 0 # 分母是y_true中1的个数
    for i in range(len(y_true)):
        if y_true[i]:
            count1 += 1
    for i in range(k):
        if df[i][1]:
            count0 += 1
    return count0 / count1

def onehot2int(oneHotEncodingVector):
    '''将oneHot编码向量转换回int
    '''
    length = len(oneHotEncodingVector)
    for i in range(length):
        if oneHotEncodingVector[i]:
            return length - i
    return None

def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True

def write_log(type, content, path, mode='local'):
    '''写日志

        Input:
            type : str : TRACE / DEBUG / INFO / WARN / ERROR / FATAL
            content : str : log content
            mode : str : local (write to local files) / TODO
            path : str : log path

        Return:
            bool : succeed or fail
    '''
    if mode == 'local':
        try:
            fd = open(path, 'a+')
            currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            logStr = '{} [{}] {}\n'.format(currentTime, type, content)
            fd.write(logStr)
            fd.close()
        except Exception as e:
            print(str(e))
            return False
        return True
    else:
        return False
    
import socket
def port_is_available(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(socket.SHUT_WR)
        return False
    except:
        return True
    
def get_available_port(ip, start_port, max_search_length=100):
    for i in range(max_search_length):
        if port_is_available(ip, start_port+i):
            return start_port + i
    return None

def get_external_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    return ip