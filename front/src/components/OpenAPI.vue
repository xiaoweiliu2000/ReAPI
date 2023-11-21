<template>
    <div style="margin-bottom: 30px;" >
        <el-row align="middle">
            <el-col :span="10" :push="3">
                <el-card shadow="hover" style="width: 85%; height: 100px;">
                    <img src="../assets/reapi_icon_small.svg" style="width: 35px; margin-right: 20px;" />
                    <el-space direction="vertical" alignment="flex-start">
                        <div style="font-size: 18px;">Cloud API for Cloud API Complementary Recommendation</div>
                        <div>By <router-link :to="'/home'" target="_blank">ReAPI</router-link> | Recommendation</div>   
                    </el-space>
                </el-card>
            </el-col>
            <el-col :span="5" :push="7">
                <el-card shadow="hover" style="height: 100px;">
                    <el-row>
                        <el-col :span="8">
                            <el-statistic :value="5" suffix="/5">
                                <template #title>
                                    <el-icon><Promotion /></el-icon>API Rating
                                </template>
                            </el-statistic>
                        </el-col>
                        <el-col :span="8">
                            <el-statistic :value="300" suffix="ms">
                                <template #title>
                                    <el-icon><Timer /></el-icon>Response Time
                                </template>
                            </el-statistic>
                        </el-col>
                        <el-col :span="8">
                            <el-statistic :value="100" suffix="%">
                                <template #title>
                                    <el-icon><Check /></el-icon>Service Level
                                </template>
                            </el-statistic>
                        </el-col>
                    </el-row>
                </el-card>
            </el-col>
        </el-row>
    </div>

    <el-divider style="margin-left: 3%; width: 97%; margin-bottom: 30px;"  />

    <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick" tab-position="left">
        <el-tab-pane label="Documentation" name="first" >
            <el-row :gutter="20">
                <el-col :span="10">
                    <el-card class="docu-card"  shadow="never">
                        <template #header>
                            <span class="docu-title">
                                <b style="color:royalblue;">POST</b> /rec/recommend
                            </span>
                        </template>
                        <el-collapse v-model="activeName_docu">
                            <el-collapse-item name="1">
                                <template #title>
                                    <span class="docu-collapse-content">Request Header</span>
                                </template>
                                <div class="docu-collapse-content" style="text-align: center;">No parameter</div>
                            </el-collapse-item>
                            <el-collapse-item name="2">
                                <template #title>
                                    <span class="docu-collapse-content">Request Query</span>
                                </template>
                                <div class="docu-collapse-content" style="text-align: center;">No parameter</div>
                            </el-collapse-item>
                            <el-collapse-item name="3">
                                <template #title>
                                    <span class="docu-collapse-content">Request Body</span>
                                </template>
                                <pre><code class="language-json line-numbers" style="font-size: 16px;">{{ codes[0] }}</code></pre>
                            </el-collapse-item>
                        </el-collapse>
                    </el-card>
                </el-col>
                <el-col :span="14">
                    <el-tabs type="border-card">
                        <el-tab-pane label="Request Example">
                            <el-tabs type="border-card">
                                <el-tab-pane label="Python">
                                    <pre><code class="language-python line-numbers" style="font-size: 16px;">{{ codes[1] }}</code></pre>
                                </el-tab-pane>
                                <el-tab-pane label="JavaScript">
                                    <pre><code class="language-js line-numbers" style="font-size: 16px;">{{ codes[2] }}</code></pre>
                                </el-tab-pane>
                            </el-tabs>
                        </el-tab-pane>
                        <el-tab-pane label="Successful Response">
                            <pre><code class="language-json line-numbers" style="font-size: 16px;">{{ codes[3] }}</code></pre>
                        </el-tab-pane>
                        <el-tab-pane label="Failure Response">
                            <pre><code class="language-json line-numbers" style="font-size: 16px;">{{ codes[4] }}</code></pre>
                        </el-tab-pane>
                    </el-tabs>
                </el-col>
            </el-row>
        </el-tab-pane>
        <el-tab-pane label="Monitoring" name="second" style="margin-left: -10%;">
            <h1 class="title monitor-title">API Monitoring</h1>
            <el-card class="monitor-card" shadow="hover">
                <el-row>
                    <el-col :span="4">
                        <el-statistic :value="monitorResult.global_request_number" suffix="">
                            <template #title>
                                Total Responses
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="5">
                        <el-statistic :value="monitorResult.global_throughput" suffix="">
                            <template #title>
                                Throughput (in {{ monitorResult.window_size }} seconds)
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="5">
                        <el-statistic :value="monitorResult.global_avg_rt * 1000" suffix="ms">
                            <template #title>
                                Average Response Time (in {{ monitorResult.window_size }} seconds)
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="5">
                        <el-statistic :value="monitorResult.global_max_rt * 1000" suffix="ms">
                            <template #title>
                                Maximum Response Time (in {{ monitorResult.window_size }} seconds)
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="5">
                        <el-statistic :value="monitorResult.global_min_rt * 1000" suffix="ms">
                            <template #title>
                                Minimum Response Time (in {{ monitorResult.window_size }} seconds)
                            </template>
                        </el-statistic>
                    </el-col>
                </el-row>
            </el-card>

            <h1 class="title monitor-title" style="font-size: 24px;">Instance Monitoring</h1>
            <el-tooltip
                content = 'Choose an instance to display its monitoring data.'
                placement = 'right'
            >
                <el-radio-group @change="handleInstanceChange"  v-model="selectedInstance"  size="large" style="margin-top: 0.5%;" >
                    <el-radio-button v-for="(item, index) in monitorResult.monitor_data_list" :label="'inst-' + index" />
                </el-radio-group>
            </el-tooltip>
            <el-card class="monitor-card" shadow="hover">
                <el-row >
                    <el-col :span="4">
                        <el-statistic :value="monitorResult.inst_request_number" suffix="">
                            <template #title>
                                Total Responses
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="5">
                        <el-statistic :value="monitorResult.inst_throughput" suffix="">
                            <template #title>
                                Throughput (in {{ monitorResult.window_size }} seconds)
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="5">
                        <el-statistic :value="monitorResult.inst_avg_rt * 1000" suffix="ms">
                            <template #title>
                                Average Response Time (in {{ monitorResult.window_size }} seconds)
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="5">
                        <el-statistic :value="monitorResult.inst_max_rt * 1000" suffix="ms">
                            <template #title>
                                Maximum Response Time (in {{ monitorResult.window_size }} seconds)
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="5">
                        <el-statistic :value="monitorResult.inst_min_rt * 1000" suffix="ms">
                            <template #title>
                                Minimum Response Time (in {{ monitorResult.window_size }} seconds)
                            </template>
                        </el-statistic>
                    </el-col>
                </el-row>
            </el-card>
            <el-card class="monitor-card" shadow="hover">
                <el-row style="margin-bottom: 2%;">
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_id.substring(0,16)" suffix="">
                            <template #title>
                                ID
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_running_time" suffix="">
                            <template #title>
                                Running Time
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_cpu_count" suffix="">
                            <template #title>
                                Thread Count
                            </template>
                        </el-statistic>
                    </el-col>  
                </el-row>
                <el-row style="margin-bottom: 2%;">
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_mem_percent" suffix="%">
                            <template #title>
                                Memory Usage
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_mem_total - monitorResult.inst_mem_avail" suffix="MB">
                            <template #title>
                                Used Memory
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_mem_total" suffix="MB">
                            <template #title>
                                Total Memory
                            </template>
                        </el-statistic>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_cpu_percent" suffix="%">
                            <template #title>
                                CPU Usage
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_cpu_frequency" suffix="MHz">
                            <template #title>
                                CPU Frequency
                            </template>
                        </el-statistic>
                    </el-col>
                    <el-col :span="8">
                        <el-statistic :value="monitorResult.inst_cpu_temperature" suffix="℃">
                            <template #title>
                                CPU Temperature
                            </template>
                        </el-statistic>
                    </el-col>
                </el-row>
            </el-card>

        </el-tab-pane>
    </el-tabs>
</template>
  
<script setup>
import axios from 'axios'
import { onMounted, onUnmounted, ref, reactive } from 'vue'
import Prism from "prismjs"

const activeName = ref('first')
const activeName_docu = ref(['3'])
var selectedInstance = ref('inst-0')
var selectedInstanceIndex = 0

var monitorResult = reactive({
    monitor_data_list:[],
    window_size : 0,
    global_avg_rt : 0,
    global_throughput : 0,
    global_max_rt : 0,
    global_min_rt : 0,
    global_request_number : 0,
    inst_request_number : 0,
    inst_avg_rt : 0,
    inst_max_rt : 0,
    inst_min_rt : 0,
    inst_throughput : 0,
    inst_id : 'N/A',
    inst_mem_avail : 0,
    inst_mem_total : 0,
    inst_mem_percent : 0,
    inst_cpu_frequency : 0,
    inst_cpu_percent : 0,
    inst_cpu_count : 0,
    inst_cpu_temperature : 0,
    inst_running_time : 0
})
let timer
 
const handleInstanceChange = () => {
    selectedInstanceIndex = selectedInstance.value.substring(5)
    monitor()
}

const handleClick = () => {
    monitor()
}

// 监控docker负载与QoS
function monitor() {
    var recQuery = '/rec/monitor'
    axios.get(recQuery).then((res) => {
        monitorResult.monitor_data_list = res['data']['monitor_data_list']
        monitorResult.window_size = res['data']['window_size']
        monitorResult.global_throughput = res['data']['global_monitor_data']['throughput']
        monitorResult.global_avg_rt = res['data']['global_monitor_data']['avg_rt']
        monitorResult.global_max_rt = res['data']['global_monitor_data']['max_rt']
        monitorResult.global_min_rt = res['data']['global_monitor_data']['min_rt']
        monitorResult.global_request_number = res['data']['global_monitor_data']['total_response_number']
        

        if (selectedInstanceIndex < monitorResult.monitor_data_list.length) {
            monitorResult.inst_request_number = monitorResult.monitor_data_list[selectedInstanceIndex]['total_response_number']
            monitorResult.inst_avg_rt = monitorResult.monitor_data_list[selectedInstanceIndex]['avg_rt']
            monitorResult.inst_max_rt = monitorResult.monitor_data_list[selectedInstanceIndex]['max_rt']
            monitorResult.inst_min_rt = monitorResult.monitor_data_list[selectedInstanceIndex]['min_rt']
            monitorResult.inst_id = monitorResult.monitor_data_list[selectedInstanceIndex]['id']
            monitorResult.inst_mem_avail = monitorResult.monitor_data_list[selectedInstanceIndex]['mem_avail']
            monitorResult.inst_mem_total = monitorResult.monitor_data_list[selectedInstanceIndex]['mem_total']
            monitorResult.inst_mem_percent = monitorResult.monitor_data_list[selectedInstanceIndex]['mem_percent']
            monitorResult.inst_cpu_frequency = monitorResult.monitor_data_list[selectedInstanceIndex]['cpu_freq']
            monitorResult.inst_cpu_percent = monitorResult.monitor_data_list[selectedInstanceIndex]['cpu_percent']
            monitorResult.inst_cpu_count = monitorResult.monitor_data_list[selectedInstanceIndex]['cpu_count']
            monitorResult.inst_cpu_temperature = monitorResult.monitor_data_list[selectedInstanceIndex]['cpu_temperature']
            monitorResult.inst_running_time = monitorResult.monitor_data_list[selectedInstanceIndex]['running_time']
            monitorResult.inst_throughput = monitorResult.monitor_data_list[selectedInstanceIndex]['throughput']
            if (monitorResult.inst_cpu_temperature == 0)
                monitorResult.inst_cpu_temperature = 'N/A'

            let running_time = monitorResult.inst_running_time
            let run_day = (running_time / (3600 * 24)) >> 0
            running_time -= run_day * 3600 * 24
            let run_hour = (running_time / 3600) >> 0
            running_time -= run_hour * 3600
            let run_min = (running_time / 60) >> 0
            running_time -= run_min * 60
            let run_second = (running_time) >> 0
            if (run_day)
            monitorResult.inst_running_time = `${run_day} d ${run_hour } h ${run_min} m ${run_second} s`
            else if (run_hour) 
                monitorResult.inst_running_time = `${run_hour } h ${run_min} m ${run_second} s`
            else if (run_min) 
                monitorResult.inst_running_time = `${run_min} m ${run_second} s`
            else
                monitorResult.inst_running_time = `${run_second} s`
        }
    }).catch((err) => {
        console.log(err)
    })
}

onMounted(() => {
    Prism.highlightAll()
    setTimeout(() => {
        Prism.highlightAll()
    }, 100)
    timer = setInterval(() => {
        if (activeName.value == "second") {
            monitor()
        }
    }, 1000)
})

onUnmounted(() => {
    clearInterval(timer);
});

const codes = [`{
    "mashupInfo": {
        "MashupName": "name of the mashup",
        "MashupTags": [
            "tag 1",
            "tag 2",
            "..."
        ],
        "MashupCategory": "category of the mashup (usually the first tag)",
        "MashupDescription": "description of the mashup",
        "MashupType": "type of the mashup",
    },
    "targetApiList": [
        "target cloud API 1",
        "target cloud API 2",
        "..."
    ],
    "recNum": 10, # number of recommended cloud APIs
    "mode": "work mode (full or minimal)" # recommend based on the full dataset or the minimal dataset
}`,

`import requests

def recommend():
    url_head = 'http://10.20.122.47:8080'
    url_body = '/rec/recommend'
    url = url_head + url_body
    mashupInfo = {
        "MashupName": "Christmas List App",
        "MashupTags": [
            "Gifts",
            "eCommerce",
            "Social",
            "Tools",
        ],
        "MashupCategory": "Gifts",
        "MashupDescription": "ChristmasListApp.com is a free online and mobile tool for making and managing Christmas gift lists. Add gifts to your wish lists from any site with the Christmas List App web application or Chrome Extension. Or add gifts by searching popular eCommerce sites like Amazon, ebay, and Walmart. Christmas List App also allows you to easily share your wish lists with family and friends.",
        "MashupType": "Web",
    }
    targetApiList = ["eBay Finding", "Facebook", "Google Plus", "Twitter", "Parsebot", "Amazon Product Advertising", "Prosperent", "Skimlinks Link Monetization"]
    recNum = 10
    data = {
        'mashupInfo' : mashupInfo,
        'targetApiList' : targetApiList,
        'recNum' : recNum,
        'mode' : 'full'
    }
    response = requests.post(url=url, json=data)
    result = response.json()
`,

`import axios from 'axios'  

function recommend() {
    var mashupInfo = {
        "MashupName": "Christmas List App",
        "MashupTags": [
            "Gifts",
            "eCommerce",
            "Social",
            "Tools",
        ],
        "MashupCategory": "Gifts",
        "MashupDescription": "ChristmasListApp.com is a free online and mobile tool for making and managing Christmas gift lists. Add gifts to your wish lists from any site with the Christmas List App web application or Chrome Extension. Or add gifts by searching popular eCommerce sites like Amazon, ebay, and Walmart. Christmas List App also allows you to easily share your wish lists with family and friends.",
        "MashupType": "Web",
    }
    var targetApiList = ["eBay Finding", "Facebook", "Google Plus", "Twitter", "Parsebot", "Amazon Product Advertising", "Prosperent", "Skimlinks Link Monetization"]
    var recQuery = '/rec/recommend'
    var recQueryData = {
        'mashupInfo' : mashupInfo,
        'targetApiList' : targetApiList,
        'recNum' : 10,
        'mode' : 'full'
    }
    axios.post(recQuery, recQueryData).then((res) => {
        recResult.arr = res['data']['recommended cloud API list']
    }).catch((err) => {
        console.log(err)
    })
}`,

`{
    "status": "Succeed",
    "message": "Okay",
    "recommended cloud API list": [...] # info of recommended cloud APIs
}`,

`{
    "status": "Fail",
    "message": "Error Message",
    "recommended cloud API list": []
}`
]

</script>
  
<style>
.demo-tabs {
    margin-left: 2%;
}
.docu-collapse-content {
    font-size: 16px;
    text-align: left;
}
.docu-card {
    height: 90vh;  
    margin-left: 2%;
}
.docu-title {
    text-align: left;
    font-size: 18px;
}
.monitor-title {
    font-size: 24px;
}
.monitor-card {
    margin-top: 2%;
    margin-bottom: 2%;
    margin-left: 20%;
    width: 60%;
}
</style>