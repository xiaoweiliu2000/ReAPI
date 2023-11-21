import time
from multiprocessing import Queue, Process
from config import *

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
    
def write_log(type, content, path=LOG_PATH, mode='local'):
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

import hashlib

def str2md5(str):
    md5 = hashlib.md5()
    byte_string = str.encode()
    md5.update(byte_string)
    md5_result = md5.hexdigest()
    return md5_result