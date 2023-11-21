import json
from urllib import parse
from config import *
from flask import Flask, request
app = Flask(__name__)

apiDataPath = './apiData.json'
mashupDataPath = './mashupData.json'

def load_data():
    fd_api = open(apiDataPath, 'r')
    fd_mashup = open(mashupDataPath, 'r')
    apiData = json.load(fd_api)
    mashupData = json.load(fd_mashup)
    fd_api.close()
    fd_mashup.close()
    return apiData, mashupData

def process_data(apiData, mashupData):   
    invokeDict = {}
    for m in mashupData:
        # 解析Submitted Date
        if 'Submitted Date' in m:
            timeArr = m['Submitted Date'].split('.')
            if len(timeArr) != 3:
                m['Submitted Date'] = '2000.01.01'
            else:
                m['Submitted Date'] = '{}.{}.{}'.format(timeArr[2], timeArr[0], timeArr[1])
        if 'Related APIs' in m:
            apis = m['Related APIs'].split(', ')
            for api in apis: 
                api = api.strip()
                if api in invokeDict:
                    invokeDict[api] += 1
                else:
                    invokeDict[api] = 1
    for a in apiData:
        if a['Name'] in invokeDict:
            a['Invoked Times'] = invokeDict[a['Name']]
        else:
            invokeDict[a['Name']] = 0
            a['Invoked Times'] = 0
        
def sort_data(dataList, sortMetric, sortOrder):
    reverseFlag = (sortOrder == 'descending')
    if dataList is None or len(dataList) == 0:
        return None
    if sortMetric in dataList[0]: # TODO: temp solution
        defaultKey = dataList[0][sortMetric] 
    try:
        def sort_key(x):
            if sortMetric in x:
                return x[sortMetric]
            else:
                return defaultKey
        return sorted(dataList, key=sort_key, reverse=reverseFlag)
    except:
        return None

def filter_data(dataList, filterMetric, filterValue, precise=False):
    try:
        newList = []
        for d in dataList:
            if not precise:
                if filterMetric in d and filterValue.lower() in d[filterMetric].lower():
                    newList.append(d)
            else:
                if filterMetric in d and filterValue == d[filterMetric]:
                    newList.append(d)
        return newList
    except:
        return None

@app.route('/getPwData', methods=['GET'])
def getPwData():
    filterMetric = request.args.get('filterMetric')
    filterValue = request.args.get('filterValue')
    sortBy = request.args.get('sortBy')
    sortOrder = request.args.get('sortOrder')
    pageNum = request.args.get('pageNum')
    pageSize = request.args.get('pageSize')
    dtype = request.args.get('dtype')
    preciseFlag = request.args.get('precise')
    errorMsg = []

    try: 
        pageNum = int(pageNum)
    except:
        pageNum = None
    try:
        pageSize = int(pageSize)
    except:
        pageSize = None

    if pageNum is None:
        pageNum = 1

    errorMsg = []

    if pageSize is None:
        errorMsg.append('[error] PageSize not specified')
    
    if dtype not in ['api', 'mashup']:
        errorMsg.append('[error] invalid dtype')
    
    if len(errorMsg) != 0:
        return json.dumps(errorMsg)

    if dtype == 'api':
        newData = apiData
    else:
        newData = mashupData

    if preciseFlag is not None and preciseFlag == 'true':
        preciseFlag = True
    else:
        preciseFlag = False
    
    # search
    if filterMetric is not None and filterValue is not None:
        filterValue = parse.unquote(filterValue)
        res = filter_data(newData, filterMetric, filterValue, preciseFlag)
        if res is not None: 
            newData = res
        elif newData is not None and len(newData):
            errorMsg.append('[error] invalid filter metric')
    
    # sort
    if sortBy is not None:
        if dtype == 'api':
            res = sort_data(newData, sortBy, sortOrder)
        else:
            res = sort_data(newData, sortBy, sortOrder)         
        if res is not None: 
            newData = res
        elif newData is not None and len(newData):
            errorMsg.append('[error] invalid sort metric')

    # return json
    startPos = (pageNum - 1) * pageSize
    endPos = pageNum * pageSize
    if endPos > len(newData):
        endPos = len(newData)
    response = []
    try:
        response.append({'status':'Succeed', 'resultCount':len(newData)})
        if newData is not None:
            response += newData[startPos:endPos]
    except:
        errorMsg.append('[error] invalid pageNum')
    response[0]['errorMsg'] = errorMsg
    return json.dumps(response)

# obtain API list / mashup tag list
@app.route('/getPwDataCollection', methods=['GET'])
def getPwDataCollection():
    type = request.args.get('type')
    if type not in ['api', 'mashupTag']:
        type = None
    if type is None:
        response = {
            'status':'Fail', 
            'message':'Type is illegal or not specified.', 
            'list':None
        }
        return response

    if type == 'api':
        apiList = []
        for ad in apiData:
            if ad['Name'] not in apiList:
                apiList.append(ad['Name'].strip())
        response = {
            'status':'Succeed', 
            'message':'Okay', 
            'list':sorted(apiList, key=str.lower)
        }
        return response
    elif type == 'mashupTag':
        tagList = []
        for md in mashupData:
            mtags = md['Tags'].split(', ')
            for mtag in mtags:
                if mtag.strip() not in tagList:
                    tagList.append(mtag.strip())
        response = {
            'status':'Succeed', 
            'message':'Okay', 
            'list':sorted(tagList, key=str.lower)
        }
        return response
    
if __name__ == "__main__":
    apiData, mashupData = load_data()
    process_data(apiData, mashupData)
    app.run(host='0.0.0.0', port=DATA_SERVICE_PORT)