from flask import Flask, request
from utils import *
from config import *
import requests
import random
import threading
from queue import Queue
import json, os, sys

INSTANCE_CACHE_FILE_LOCK = threading.Lock()

app = Flask(__name__)

class serviceInstance():
    def __init__(self, instInfo):
        self.ip = instInfo['ip']
        self.port = instInfo['port']
        self.id = str2md5('{}:{}'.format(self.ip, self.port))
        self.serviceName = instInfo['serviceName']          # the name of the service corresponding to this instance  
        self.concurrencyNum = instInfo['concurrencyNum']    # maximim concurrent processing number inside this insatance 
        self.loadNum = 0
        self.mutex = threading.Lock()
        # 负载监控
        self.mem_avail = 0
        self.mem_total = 0
        self.mem_percent = 0
        self.cpu_freq = 0
        self.cpu_percent = 0
        self.cpu_count = 0
        self.cpu_temperature = 0
        # QoS监控
        self.responseNum = 0 # number of all responses 
        self.startTime = time.time() # start time
        self.rtQueue = Queue() # rt queue for qos statistics
    
    def collectInfo(self):
        info = {}
        # collect load data
        info['id'] = self.id
        info['mem_avail'] = self.mem_avail
        info['mem_total'] = self.mem_total
        info['mem_percent'] = self.mem_percent 
        info['cpu_freq'] = self.cpu_freq 
        info['cpu_percent'] = self.cpu_percent 
        info['cpu_count'] = self.cpu_count 
        info['cpu_temperature'] = self.cpu_temperature 
        # collect qos data
        self.updateRtQueue()
        info['running_time'] = time.time() - self.startTime
        info['total_response_number'] = self.responseNum
        avg_rt = 0 # average rt in the window
        min_rt = 0 # minimum rt in the window
        max_rt = 0 # maximum rt in the window
        throughput = 0 # number of responses in the window, i.e. throughput
        rtList = self.rtQueue.queue
        for (rttimestamp, rt) in rtList:
            avg_rt += rt
            if min_rt == 0 or rt < min_rt:
                min_rt = rt
            if max_rt == 0 or rt > max_rt:
                max_rt = rt
        throughput = len(rtList)
        if throughput:
            avg_rt = avg_rt / throughput
        info['avg_rt'] = avg_rt
        info['min_rt'] = min_rt
        info['max_rt'] = max_rt
        info['throughput'] = throughput
        info['rt_window'] = QOS_QUEUE_WINDOW
        return info
    
    def updateRtQueue(self):
        while True: # maintain the rt queue
            if self.rtQueue.empty():
                break
            if time.time() - self.rtQueue.queue[0][0] > QOS_QUEUE_WINDOW:
                self.rtQueue.get()
                continue
            else:
                break

class apiLoadBalancer():
    def __init__(self, ):
        # registered instance list
        self.instList = []
        self.readInstanceList()
        # exclusive lock
        self.mutex = threading.Lock()
        # qos monitoring
        self.responseNum = 0 # total number of responses
        self.startTime = time.time() # start time
        self.rtQueue = Queue() # rt queue for qos statistics

    def register(self, instInfo):
        '''register new instance
        '''
        # record the information of the instance
        newInstance = serviceInstance(instInfo)
        self.instList.append(newInstance)       
        return True
    
    def logout(self, instInfo):
        target_i = -1
        for i in range(len(self.instList)):
            if self.instList[i].ip == instInfo['ip'] and self.instList[i].port == instInfo['port']:
                target_i = i
                break
        if target_i != -1:
            self.instList.pop(target_i)
            return True
        else:
            return False
        
    def collectInfo(self):
        info = {}
        # collect qos
        self.updateRtQueue()
        info['running_time'] = time.time() - self.startTime
        info['total_response_number'] = self.responseNum
        avg_rt = 0 
        min_rt = 0 
        max_rt = 0 
        throughput = 0
        rtList = self.rtQueue.queue
        for (rttimestamp, rt) in rtList:
            avg_rt += rt
            if min_rt == 0 or rt < min_rt:
                min_rt = rt
            if max_rt == 0 or rt > max_rt:
                max_rt = rt
        throughput = len(rtList)
        if throughput:
            avg_rt = avg_rt / throughput
        info['avg_rt'] = avg_rt
        info['min_rt'] = min_rt
        info['max_rt'] = max_rt
        info['throughput'] = throughput
        info['rt_window'] = QOS_QUEUE_WINDOW
        return info
        
    def updateRtQueue(self):
        while True: 
            if self.rtQueue.empty():
                break
            if time.time() - self.rtQueue.queue[0][0] > QOS_QUEUE_WINDOW:
                self.rtQueue.get()
                continue
            else:
                break

    def dumpInstanceList(self):
        dumpJson = []
        for instance in self.instList:
            instInfo = {
                'ip' : instance.ip,
                'port' : instance.port,
                'serviceName' : instance.serviceName,
                'concurrencyNum' : instance.concurrencyNum
            }
            dumpJson.append(instInfo)
        INSTANCE_CACHE_FILE_LOCK.acquire()
        with open(INSTANCE_CACHE_FILE, 'w') as fd:
            json.dump(dumpJson, fd)
        INSTANCE_CACHE_FILE_LOCK.release()

    def readInstanceList(self):
        if not os.path.exists(INSTANCE_CACHE_FILE):
            return
        INSTANCE_CACHE_FILE_LOCK.acquire()
        with open(INSTANCE_CACHE_FILE, 'r') as fd:
            dumpJson = json.load(fd)
        INSTANCE_CACHE_FILE_LOCK.release()
        newInstList = []
        for instInfo in dumpJson:    
            try: # check if this instance is available
                response = requests.get('http://{}:{}/monitor'.format(instInfo["ip"], instInfo["port"]))
                newInstList.append(serviceInstance(instInfo))
            except:
                continue
        self.instList += newInstList

@app.route('/', methods=['GET', 'POST'])
def index():
    return '<h2> Load Balancing Service for Online Cloud API Recommendation (Alpha Test) </h2> Version: 0.1 <br> <p> Copyright belongs to Xiaowei Liu and 528Lab at Yanshan University.</p>'

@app.route('/register', methods=['POST'])
def registerService():
    inputJS = request.json
    status = loadBanana.register(inputJS)
    response = {}
    if status:
        response['status'] = 'Succeed'
        loadBanana.dumpInstanceList()
    else:
        response['status'] = 'Fail'
    return response

@app.route('/logout', methods=['POST'])
def logoutService():
    inputJS = request.json
    status = loadBanana.logout(inputJS)
    response = {}
    if status:
        logContent = 'Service instace logout (ip = {}, port = {}).'.format(inputJS['ip'], inputJS['port'])
        write_log('DEBUG', logContent)
        loadBanana.dumpInstanceList()
        response['status'] = 'Succeed'
    else:
        logContent = 'Service instace fails to logout (ip = {}, port = {}).'.format(inputJS['ip'], inputJS['port'])
        write_log('DEBUG', logContent)
        response['status'] = 'Fail'
    return response

@app.route('/recommend', methods=['POST'])
def distributeLoad():
    '''
        distribure load to instances
    '''
    # check if there are available instances
    if not len(loadBanana.instList):
        response = {
            'status' : 'Fail',
            'message' : 'Recommending service is currently unavailable due to lack of living instance.'
        }
        write_log('ERROR', 'Cannot response due to lack of living instance.', LOG_PATH)
        return response
    
    retryTimes = 0
    rtStart_global = time.time()
    
    while True:
        # strategy: distribute loads according to the number of loads in instances
        if True:
            # collect number of loads
            loadNumList = []
            for i in range(len(loadBanana.instList)):
                loadNumList.append(loadBanana.instList[i].loadNum)
                if loadBanana.instList[i].mem_percent > MEM_PERCENT_ALERT:
                    loadNumList[i] += 9999
            # find the instance with the minimum number of loads
            selectedIndex = loadNumList.index(min(loadNumList))
            selectedInst = loadBanana.instList[selectedIndex]
        
        # if the load exceeds the instance capacity, wait
        if selectedInst.loadNum >= INSTANCE_QUEUE_SIZE or selectedInst.mem_percent > MEM_PERCENT_ALERT:
            time.sleep(1 + 0.1 * random.random())
            retryTimes += 1
            if retryTimes > MAX_RETRY:
                response = {
                    'status' : 'Fail',
                    'message' : 'The recommendation service is busy (number of retries exceeded the maximum). Please try later.'
                }
                write_log('WARN', 'Number of retries exceeded the maximum.', LOG_PATH)
                return response
            continue
        else:
            # print('allocate', loadNumList)
            break
    
    # send load to the selected instance
    selectedInst.mutex.acquire()
    selectedInst.loadNum += 1
    selectedInst.mutex.release()

    rtStart = time.time()
    response = requests.post('http://{}:{}/recommend'.format(selectedInst.ip, selectedInst.port), json=request.json, headers=request.headers)
    rtEnd = time.time()

    # update information
    selectedInst.mutex.acquire()
    selectedInst.loadNum -= 1
    selectedInst.responseNum += 1
    selectedInst.rtQueue.put([time.time(), rtEnd - rtStart])
    selectedInst.updateRtQueue()
    selectedInst.mutex.release()
    loadBanana.mutex.acquire()
    loadBanana.responseNum += 1
    loadBanana.rtQueue.put([time.time(), rtEnd - rtStart_global])
    loadBanana.updateRtQueue()
    loadBanana.mutex.release()

    loadNumList = []
    for i in range(len(loadBanana.instList)):
        loadNumList.append(loadBanana.instList[i].loadNum)
    print('finish', loadNumList)

    return response.json()

@app.route('/monitor', methods=['GET'])
def getMonitorData():
    response = {
        'window_size' : QOS_QUEUE_WINDOW,
        'monitor_data_list' : [],
        'global_monitor_data' : loadBanana.collectInfo()
    }
    for instance in loadBanana.instList:
        info = instance.collectInfo()
        response['monitor_data_list'].append(info)
    return response

def monitorLoad(instance):
    response = requests.get('http://{}:{}/monitor'.format(instance.ip, instance.port))
    r = response.json()
    instance.mutex.acquire()
    instance.mem_avail = r['mem_avail']
    instance.mem_total = r['mem_total']
    instance.mem_percent = r['mem_percent']
    instance.cpu_freq = r['cpu_freq']
    instance.cpu_percent = r['cpu_percent']
    instance.cpu_count = r['cpu_count']
    instance.cpu_temperature = r['cpu_temperature']
    instance.mutex.release()

def monitorHost():
    while True:
        start = time.time()

        # fork subprocess
        for instance in loadBanana.instList:
            workthread = threading.Thread(target=monitorLoad, args=(instance,))
            workthread.start()

        # keep the time
        while True:
            now = time.time()
            if now - start > 1:
                break
            else:
                time.sleep(0.01)


if __name__ == '__main__':
    loadBanana = apiLoadBalancer()
    monitorThread = threading.Thread(target=monitorHost)
    monitorThread.start()
    write_log('TRACE', 'Start api load balancing service.')
    app.run(port=9000, host='0.0.0.0', debug=False, threaded=True)