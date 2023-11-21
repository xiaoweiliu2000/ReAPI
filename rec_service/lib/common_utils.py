import json
import psutil
from lib.bcr_config import DATASET_PATHs

# 加载完整数据
def load_data():
    fd_api = open(DATASET_PATHs['apiData'], 'r')
    fd_mashup = open(DATASET_PATHs['mashupData'], 'r')
    apiData = json.load(fd_api)
    mashupData = json.load(fd_mashup)
    fd_api.close()
    fd_mashup.close()
    return apiData, mashupData

# 数据处理
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
        # 计算API被调用次数
        if 'Related APIs' in m:
            apis = m['Related APIs'].split(', ')
            for api in apis: 
                api = api.strip()
                if api in invokeDict:
                    invokeDict[api] += 1
                else:
                    invokeDict[api] = 1
    for a in apiData:
        # 增加API被调用次数特征
        if a['Name'] in invokeDict:
            a['Invoked Times'] = invokeDict[a['Name']]
        else:
            invokeDict[a['Name']] = 0
            a['Invoked Times'] = 0
        
# 按照指定指标进行排序
def sort_data(dataList, sortMetric, sortOrder):
    '''
        sortOrder : str : descending / ascending
    '''
    reverseFlag = (sortOrder == 'descending')
    if dataList is None or len(dataList) == 0:
        return []
    if sortMetric in dataList[0]: # 缺失值处理，没有sortMetric的项均偷懒视为第0项的对应值，这样就不需要处理不同数据类型了
        defaultKey = dataList[0][sortMetric] 
    try:
        def sort_key(x):
            if sortMetric in x:
                return x[sortMetric]
            else: # 缺失值处理
                return defaultKey
        return sorted(dataList, key=sort_key, reverse=reverseFlag)
    except:
        return None

def filter_data(dataList, filterMetric, filterValue):
    try:
        newList = []
        for d in dataList:
            if filterMetric in d and filterValue.lower() in d[filterMetric].lower():
                newList.append(d)
        return newList
    except:
        return None

def get_cpu_info():
    cpu_temperature = 0
    cpu_freq = 0
    cpu_percent = 0
    cpu_count = 0
    try:
        # 获取CPU温度
        temperatures = psutil.sensors_temperatures()
        cpu_temperatures = temperatures['coretemp']
        for sensor in cpu_temperatures:
            if sensor.label == 'Package id 0':
                cpu_temperature = sensor.current
    except:
        pass
    try:
        # 获取CPU占用
        cpu_freq = psutil.cpu_freq().current
        cpu_percent = psutil.cpu_percent(0.1)
        cpu_count = psutil.cpu_count()
    except:
        pass
    return cpu_temperature, cpu_freq, cpu_percent, cpu_count


def get_memory_info():
    mem_avail = 0
    mem_total = 0
    mem_percent = 0
    try:
        meminfo = psutil.virtual_memory()
        mem_avail = meminfo.available / 1024 / 1024
        mem_total = meminfo.total / 1024 / 1024
        mem_percent = meminfo.percent
    except:
        pass
    return mem_avail, mem_total, mem_percent
