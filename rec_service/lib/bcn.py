import torch
import torch.nn as nn

class BilateralComplementaryNetwork(nn.Module):
    def __init__(self, featDict, featPosDict, featType_enabled, limitedTargetAPINum = 0, poolingMethod='attention', reductSize=128, baseVectorSize=64, initStd=0.0001, dropoutRate=0.5, device='cuda', flagDebug=False):
        super(BilateralComplementaryNetwork, self).__init__() # 继承父类方法
        self.featDict = featDict
        self.featPosDict = featPosDict
        self.featType_enabled = featType_enabled
        self.reductSize = reductSize            # 特征降维后的维度，同时也是进行特征降维的阈值
        self.baseVectorSize = baseVectorSize    # 双侧互补基向量的维度
        self.device = device
        self.dropoutRate = dropoutRate
        self.initStd = initStd
        self.flag_mask = True
        # 超参数
        self.hiddenUnits_ma = [128] 
        self.hiddenUnits_aa = [256] 
        self.hiddenUnits_merge = [128]
        # 可控制参数
        self.limitedTargetAPINum = limitedTargetAPINum
        self.enableMA = True
        self.enableAA = True
        self.poolingMethod = poolingMethod 
        self.flagDebug = flagDebug
        '''
            selfAttention, attention, average, sum
            Do not change it after model initializing.
        '''  
        
        # 特征降维部分
        ## 确定需要降维的特征
        self.mashupFeats = []
        self.apiFeats = []
        self.reductFeats = []
        for featType in self.featType_enabled:
            for feat in self.featDict['mashup'][featType]:
                self.mashupFeats.append(feat)
                if self.featPosDict[feat][1] - self.featPosDict[feat][0] > self.reductSize: # 注：这个判断很有用
                    self.reductFeats.append(feat)
            for feat in self.featDict['api'][featType]:
                self.apiFeats.append(feat)
                if self.featPosDict['c_' + feat][1] - self.featPosDict['c_' + feat][0] > self.reductSize:
                    self.reductFeats.append(feat)    

        ## 为这些特征定义无偏置的线性层，进行降维
        linearsDict = {}
        for feat in self.reductFeats:
            if feat in self.mashupFeats:
                linearsDict[feat] = nn.Linear(self.featPosDict[feat][1] - self.featPosDict[feat][0], self.reductSize, bias=False)
            elif feat in self.apiFeats:
                linearsDict[feat] = nn.Linear(self.featPosDict['c_' + feat][1] - self.featPosDict['c_' + feat][0], self.reductSize, bias=False)
        self.reductLinearsDict = nn.ModuleDict(linearsDict)
        for parameter in self.reductLinearsDict.values(): # 随机初始化
            nn.init.normal_(parameter.weight, mean=0) # 注意这里的标准差要用默认的
        self.reductLinearsDict.to(self.device)

        # 双侧DNN部分
        ## 统计mashup和api的嵌入大小
        self.mashupEmbeddingSize = 0
        self.apiEmbeddingSize = 0
        for featType in self.featType_enabled:
            for feat in self.featDict['mashup'][featType]:            
                if feat in self.reductFeats:
                    self.mashupEmbeddingSize += self.reductSize
                else:
                    self.mashupEmbeddingSize += featPosDict[feat][1] - featPosDict[feat][0]
        for featType in self.featType_enabled:
            for feat in self.featDict['api'][featType]:
                if feat in self.reductFeats:
                    self.apiEmbeddingSize += self.reductSize
                else:
                    self.apiEmbeddingSize += featPosDict['c_' + feat][1] - featPosDict['c_' + feat][0]

        ## 在mashup-api与api-api侧分别构建DNN，进行特征交互
        self.inputSize_ma = self.mashupEmbeddingSize + self.apiEmbeddingSize
        self.hiddenUnits_ma = [self.inputSize_ma] + self.hiddenUnits_ma + [self.baseVectorSize]
        self.dropout = nn.Dropout(self.dropoutRate)
        self.linears_ma = nn.ModuleList([nn.Linear(self.hiddenUnits_ma[i], self.hiddenUnits_ma[i+1]) for i in range(len(self.hiddenUnits_ma)-1)]).to(self.device)
        self.relus_ma = nn.ModuleList([nn.PReLU() for i in range(len(self.hiddenUnits_ma)-1)]).to(self.device) # 为了可扩展性
        for name, parameter in self.linears_ma.named_parameters():
            if 'weight' in name:
                nn.init.normal_(parameter, mean=0, std=self.initStd)

        self.inputSize_aa = 2 * self.apiEmbeddingSize
        self.hiddenUnits_aa = [self.inputSize_aa] + self.hiddenUnits_aa + [self.baseVectorSize]
        self.linears_aa = nn.ModuleList([nn.Linear(self.hiddenUnits_aa[i], self.hiddenUnits_aa[i+1]) for i in range(len(self.hiddenUnits_aa)-1)]).to(self.device)
        self.relus_aa = nn.ModuleList([nn.PReLU() for i in range(len(self.hiddenUnits_aa)-1)]).to(self.device) # 为了可扩展性
        for name, parameter in self.linears_aa.named_parameters():
            if 'weight' in name:
                nn.init.normal_(parameter, mean=0, std=self.initStd)

        ## 在api-api侧构建注意力层 
        if self.poolingMethod == 'selfAttention':
            # Plan A: 通过线性层实现attention，输入为互补基向量
            self.linear_att = nn.Linear(self.baseVectorSize, 1).to(self.device)
            for name, parameter in self.linear_att.named_parameters():
                if 'weight' in name:
                    nn.init.normal_(parameter, mean=0, std=self.initStd)
            self.relu_att = nn.PReLU().to(self.device)
            self.softmax_att = nn.Softmax(dim=1)
        elif self.poolingMethod == 'attention':
            ## Plan A(varient): 通过线性层实现attention，输入为目标API向量
            self.linear_att = nn.Linear(self.apiEmbeddingSize, 1).to(self.device)
            for name, parameter in self.linear_att.named_parameters():
                if 'weight' in name:
                    nn.init.normal_(parameter, mean=0, std=self.initStd)
            self.relu_att = nn.PReLU().to(self.device)
        self.softmax_att = nn.Softmax(dim=1)

        # 整合DNN部分
        self.hiddenUnits_merge = [2*self.baseVectorSize] + self.hiddenUnits_merge + [1]
        self.linears_merge = nn.ModuleList([nn.Linear(self.hiddenUnits_merge[i], self.hiddenUnits_merge[i+1]) 
                                            for i in range(len(self.hiddenUnits_merge)-1)]).to(self.device)
        for name, parameter in self.linears_merge.named_parameters():
            if 'weight' in name:
                nn.init.normal_(parameter, mean=0, std=self.initStd)
        self.relus_merge = nn.ModuleList([nn.PReLU() for i in range(len(self.hiddenUnits_merge)-1)]).to(self.device) # 为了可扩展性
        self.sigmoid_predict = nn.Sigmoid()

    def __calculateMaxTargetApiNumX(self, x):
        '''[优化]根据输入的x，调整maxApiNum，加快训练速度(注：需要在CPU上运行，GPU单线程能力太差)
        '''
        targetApiMask_x = x[:, self.featPosDict['targetApiMask'][0]:self.featPosDict['targetApiMask'][1]].to('cpu')
        maxTargetAPINum_x = 0
        for i in range(targetApiMask_x.shape[0]):
            for j in range(targetApiMask_x.shape[1]):
                if not targetApiMask_x[i][j]:
                    if j > maxTargetAPINum_x:
                        maxTargetAPINum_x = j 
                    break
        if maxTargetAPINum_x == 0:
            maxTargetAPINum_x = targetApiMask_x.shape[1]
        return maxTargetAPINum_x

    def forward(self, x):
        # 计算一个batch内的最大云API数量，用于优化模型计算速度
        maxTargetAPINum_x = self.__calculateMaxTargetApiNumX(x)
        if self.limitedTargetAPINum and maxTargetAPINum_x > self.limitedTargetAPINum:
            maxTargetAPINum_x = self.limitedTargetAPINum

        targetApiMask_x = x[:, self.featPosDict['targetApiMask'][0]:self.featPosDict['targetApiMask'][1]]   

        # 1、特征降维
        mashupEmbedding = []
        candidateApiEmbedding = []
        targetApiEmbeddings = []

        for featType in self.featType_enabled:
            for feat in self.featDict['mashup'][featType]:
                originalFeatVector = x[:, self.featPosDict[feat][0]:self.featPosDict[feat][1]]
                if feat in self.reductFeats:
                    mashupEmbedding.append(self.reductLinearsDict[feat](originalFeatVector))
                else:
                    mashupEmbedding.append(originalFeatVector)

        for featType in self.featType_enabled:
            for feat in self.featDict['api'][featType]:
                originalFeatVector = x[:, self.featPosDict['c_' + feat][0]:self.featPosDict['c_' + feat][1]]
                if feat in self.reductFeats:
                    candidateApiEmbedding.append(self.reductLinearsDict[feat](originalFeatVector))
                else:
                    candidateApiEmbedding.append(originalFeatVector)

        for i in range(maxTargetAPINum_x):
            newApiEmbedding = []
            for featType in self.featType_enabled:
                for feat in self.featDict['api'][featType]:
                    originalFeatVector = x[:, self.featPosDict['t{}_'.format(i) + feat][0]:self.featPosDict['t{}_'.format(i) + feat][1]]
                    if feat in self.reductFeats:
                        if self.flag_mask:
                            newApiEmbedding.append(self.reductLinearsDict[feat](originalFeatVector) * targetApiMask_x[:, [i]]) # mask
                        else:
                            newApiEmbedding.append(self.reductLinearsDict[feat](originalFeatVector)) 
                    else:
                        newApiEmbedding.append(originalFeatVector)
            targetApiEmbeddings.append(newApiEmbedding)      
            
        # 拼接
        mashupEmbedding = torch.cat(mashupEmbedding, dim=-1) 
        candidateApiEmbedding = torch.cat(candidateApiEmbedding, dim=-1) 
        for i in range(maxTargetAPINum_x):
            targetApiEmbeddings[i] = torch.cat(targetApiEmbeddings[i], dim=-1) 

        if self.flagDebug:
            print('mashupEmbed', mashupEmbedding)

        # 2、mashup-api侧
        baseVector_ma = torch.cat([mashupEmbedding, candidateApiEmbedding], dim=-1)
        if self.enableMA:
            for i in range(len(self.linears_ma)): # dnn
                tmp = self.linears_ma[i](baseVector_ma)
                tmp = self.relus_ma[i](tmp)
                tmp = self.dropout(tmp)
                baseVector_ma = tmp
        else:
            baseVector_ma = torch.zeros([x.shape[0], self.baseVectorSize], dtype=torch.float, device=self.device)

        # 3、api-api侧
        baseVectors_aa = [torch.cat([targetApiEmbeddings[i], candidateApiEmbedding], dim=-1) for i in range(maxTargetAPINum_x)]
        if self.enableAA:
            # dnn
            for i in range(maxTargetAPINum_x):
                for j in range(len(self.linears_aa)): # dnn
                    tmp = self.linears_aa[j](baseVectors_aa[i])
                    tmp = self.relus_aa[j](tmp)
                    tmp = self.dropout(tmp)
                    baseVectors_aa[i] = tmp
            # mask
            if self.flag_mask:
                for i in range(maxTargetAPINum_x):
                    baseVectors_aa[i] = baseVectors_aa[i] * targetApiMask_x[:, [i]] 

            # attention pooling
            attWeights = []
            for i in range(maxTargetAPINum_x):
                if self.poolingMethod == 'selfAttention':
                    aw = self.linear_att(baseVectors_aa[i])
                    aw = self.relu_att(aw)
                elif self.poolingMethod == 'attention':
                    aw = self.linear_att(targetApiEmbeddings[i]) 
                    aw = self.relu_att(aw)
                elif self.poolingMethod == 'average' or self.poolingMethod == 'sum':
                    aw = torch.ones([x.shape[0], 1], dtype=torch.float, device=self.device)
                else:
                    raise Exception('unknown pooling method')
                         
                # mask
                if self.flag_mask:
                    attMaskBias = torch.where(
                        torch.gt(targetApiMask_x[:, [i]], 0.5),
                        torch.full_like(targetApiMask_x[:, [i]], 0),
                        torch.full_like(targetApiMask_x[:, [i]], -torch.inf) # 实际上这里会导致后续变为nan，但不影响结果
                    )
                    aw += attMaskBias                      
                attWeights.append(aw)

            attWeights = torch.cat(attWeights, dim=-1)
            attWeights = self.softmax_att(attWeights)
            if self.poolingMethod != 'sum':
                for i in range(maxTargetAPINum_x): # 注意力
                    baseVectors_aa[i] = baseVectors_aa[i] * attWeights[:,[i]]
            baseVector_aa = baseVectors_aa[0]
            for i in range(1, maxTargetAPINum_x):
                baseVector_aa += baseVectors_aa[i]
        else:
            baseVector_aa = torch.zeros([x.shape[0], self.baseVectorSize], dtype=torch.float, device=self.device)

        if self.flagDebug:
            print('baseVector_ma', baseVector_ma)
            print('baseVector_aa', baseVector_aa)
            
        # 4、双侧聚合
        mergeVector = torch.cat([baseVector_ma, baseVector_aa], dim=-1)    

        for i in range(len(self.linears_merge)): # dnn
            tmp = self.linears_merge[i](mergeVector)
            tmp = self.dropout(tmp)
            mergeVector = tmp

        if self.flagDebug:
            print('mergeVector', mergeVector)
        
        y = self.sigmoid_predict(mergeVector) 
        return y