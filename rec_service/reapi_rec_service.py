from lib.bcr_core import *
from lib.bcr_config import *
from lib.common_utils import *
from config import *
from flask import Flask, request
import requests
import sys, signal

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return '<h2> Complementary Cloud API Recommendation Service (Alpha Test) </h2> Version: 0.1 <br> <p> Copyright belongs to Xiaowei Liu and 528Lab at Yanshan University.</p>'

@app.route('/monitor', methods=['GET'])
def monitor():
    cpu_temperature, cpu_freq, cpu_percent, cpu_count = get_cpu_info()
    mem_avail, mem_total, mem_percent = get_memory_info()
    response = {
        "cpu_freq" : cpu_freq,
        "cpu_percent" : cpu_percent,
        "cpu_count" : cpu_count,
        "cpu_temperature" : cpu_temperature,
        "mem_avail" : mem_avail,
        "mem_total" : mem_total,
        "mem_percent" : mem_percent
    }
    return response

@app.route('/recommend', methods=['POST'])
def recommend():
    start = time.time()
    inputJS = request.json
    mashupInfo = None
    targetApiList = []
    recNum = 10
    mode = 'minimal'

    if 'mashupInfo' in inputJS:
        mashupInfo = inputJS['mashupInfo']
    if 'targetApiList' in inputJS:
        targetApiList = inputJS['targetApiList']
    if 'recNum' in inputJS:
        recNum = inputJS['recNum']
    if 'mode' in inputJS:
        mode = inputJS['mode']

    if type(recNum) != type(1) or np.int(recNum) < 1:
        response = {
            'status' : 'Fail',
            'message' : '[formatting error] Invalid K. Check the input.',
            'recommended cloud API list' : []
        }
        return response

    if mashupInfo is None and len(targetApiList) == 0:
        response = {
            'status' : 'Fail',
            'message' : '[formatting error] Both mashupInfo and targetApiList are empty. Check the input.',
            'recommended cloud API list' : []
        }
        return response

    try:
        result = BBS.recommend(K=recNum, mashupInfo=mashupInfo, targetApiList=targetApiList, device=GLOBAL_DEVICE, mode=mode)
    except Exception as e:
        write_log('ERROR', 'Error(s) occurred during making recommendations: {}'.format(str(e)), LOG_PATH)
        response = {
            'status' : 'Fail',
            'message' : '[critical error] Error(s) occurred during making recommendations: {}'.format(str(e)),
            'recommended cloud API list' : []
        }
        return response

    response = {
        'status' : 'Succeed',
        'message' : 'Okay',
        'recommended cloud API list' : result
    }

    end = time.time()
    write_log('TRACE', 'Recommendation complete. Device is {}, processing time is {:.3f}s.'.format(GLOBAL_DEVICE, end-start), LOG_PATH)
    return response

def register(ip, port):
    '''
        Return:
            status : bool
    '''
    inputJSON = {
        'ip' : ip,
        'port' : port,
        'serviceName' : 'recommend',
        'concurrencyNum' : CONCURRENCY_NUM
    }
    header = {
        "Content-Type": "application/json",
    }
    response = requests.post('http://' + load_balancer_addr + '/register', json=inputJSON, headers=header)
    status = response.json()['status']
    if status == 'Succeed':
        return True
    else:
        return False
    
def logout(ip, port):
    inputJSON = {
        'ip' : ip,
        'port' : port,
    }
    header = {
        "Content-Type": "application/json",
    }
    response = requests.post('http://' + load_balancer_addr + '/logout', json=inputJSON, headers=header)

class backendHost():
    def __del__(self, ):
        logout(external_ip, avail_port)

def exitHandler(signum, frame):
    write_log('TRACE', 'Receive exit signal (signum = {}, frame = {}).'.format(signum, frame), LOG_PATH)
    exit(1)

if __name__ == '__main__':
    BBS = bcrBackendService(device=GLOBAL_DEVICE, flag_retrain_model=False, flag_use_cache=True)

    apiData, mashupData = load_data()
    process_data(apiData, mashupData)

    avail_port = get_available_port('0.0.0.0', 10000)
    if avail_port is None:
        write_log('ERROR', 'No available port.', LOG_PATH)
        print('[ERROR] No available port.')
        exit(1)
    external_ip = get_external_ip()

    # set the address for the load balancer
    if len(sys.argv) >= 2:
        load_balancer_addr = sys.argv[1]
    else:
        load_balancer_addr = LOAD_BALANCER_ADDR

    # register this instace to the load balancer
    status = register(external_ip, avail_port)
    if not status:
        write_log('ERROR', 'Fail to register with load balancer.', LOG_PATH)
        print('[ERROR] Fail to register with load balancer.')
        exit(1)

    # exit handler
    # plan A: use destructors for direct running
    bh = backendHost()
    # plan B: signal capture for docker containers
    signal.signal(signal.SIGTERM, exitHandler)

    # start the service
    write_log('TRACE', 'Start BCR backend service.', LOG_PATH)
    app.run(port=avail_port, host='0.0.0.0', debug=False, threaded=False, processes=CONCURRENCY_NUM)