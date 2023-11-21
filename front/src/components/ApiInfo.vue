<template>
    <el-container style="margin-top: -20px;">
        <el-main style="margin-left: 5%;">
            <h1 class="title" style="font-size: 150%;">Cloud API Profile</h1>
            <el-card shadow="hover" round>
                <el-descriptions v-bind="ad.data" :column="1" border>
                    <el-descriptions-item label="Name">{{ ad.data['Name'] }}</el-descriptions-item>
                    <el-descriptions-item label="Description">{{ ad.data['Description'] }}</el-descriptions-item>
                    <el-descriptions-item label="Invoked Times">{{ ad.data['Invoked Times'] }}</el-descriptions-item>
                    <el-descriptions-item label="API Endpoint">{{ ad.data['API Endpoint'] }}</el-descriptions-item>
                    <el-descriptions-item label="API Portal / Home Page">{{ ad.data['API Portal / Home Page']
                    }}</el-descriptions-item>
                    <el-descriptions-item label="Primary Category">{{ ad.data['Primary Category'] }}</el-descriptions-item>
                    <el-descriptions-item label="Secondary Categories">{{ ad.data['Secondary Categories'] }}</el-descriptions-item>
                    <el-descriptions-item label="SSL Support">{{ ad.data['SSL Support'] }}</el-descriptions-item>
                    <el-descriptions-item label="Support Email Address">{{ ad.data['Support Email Address'] }}</el-descriptions-item>
                    <el-descriptions-item label="Version status">{{ ad.data['Version status'] }}</el-descriptions-item>
                    <el-descriptions-item label="Terms Of Service URL">{{ ad.data['Terms Of Service URL'] }}</el-descriptions-item>
                    <el-descriptions-item label="Is the API Design/Description Non-Proprietary ?">{{ ad.data['Is the API Design / Description Non - Proprietary ? '] }}</el-descriptions-item>
                    <el-descriptions-item label="Scope">{{ ad.data['Scope'] }}</el-descriptions-item>
                    <el-descriptions-item label="Device Specific">{{ ad.data['Device Specific'] }}</el-descriptions-item>
                    <el-descriptions-item label="Docs Home Page URL">{{ ad.data['Docs Home Page URL'] }}</el-descriptions-item>
                    <el-descriptions-item label="Architectural Style">{{ ad.data['Architectural Style'] }}</el-descriptions-item>
                    <el-descriptions-item label="Supported Request Formats">{{ ad.data['Supported Request Formats']}}</el-descriptions-item>
                    <el-descriptions-item label="Supported Response Formats">{{ ad.data['Supported Response Formats']}}</el-descriptions-item>
                    <el-descriptions-item label="Is This an Unofficial API?">{{ ad.data['Is This an Unofficial API?']}}</el-descriptions-item>
                    <el-descriptions-item label="Is This a Hypermedia API?">{{ ad.data['Is This a Hypermedia API?']}}</el-descriptions-item>
                    <el-descriptions-item label="Restricted Access ( Requires Provider Approval )">{{ ad.data['Restricted Access ( Requires Provider Approval )'] }}</el-descriptions-item>
                </el-descriptions>
            </el-card>
        </el-main>
        <el-aside width="30%">
            <h1 class="title" style="font-size: 150%; margin-top: 45px;">Recommend for you</h1>
            <el-tooltip
                class="box-item"
                effect="customized"
                content="Recommend from the invoked or all cloud APIs"
                placement="left"
            >
                <el-switch
                    v-model="mode.data"
                    class="mb-2"
                    active-text="All"
                    inactive-text="Invoked"
                    style="margin-top: -20px;margin-bottom: 10px;"
                    @click="recommend"
                />
            </el-tooltip>
            <el-table 
                :data="recResult.arr" 
                style="width: 100%" 
                :row-style="{ height: '60px' }" 
                table-layout="auto" 
                v-loading="loading.value" 
                element-loading-text="Recommending..."
            >
                <el-table-column label="Cloud API" prop="ApiName">  
                    <template #default="props">
                        <router-link :to="'/api/' + encodeURIComponent(props.row['ApiName'])">
                            {{ props.row['ApiName'] }}
                        </router-link>                    
                    </template>
                </el-table-column>   
                <el-table-column label="Category" prop="ApiCategory" />
            </el-table>
        </el-aside>
    </el-container>
</template>

<script setup>
import axios from 'axios'
import { ElTooltip } from 'element-plus'
import { defineProps, reactive} from 'vue'

var loading = reactive({
    value:true
})
const props = defineProps(['id'])
var apiName = decodeURIComponent(props.id)
var ad = reactive({
    data:{}
})
var recResult = reactive({
    arr:[]
})
var mode = reactive({
    data:false
})

function recommend() {
    loading.value = true
    var recQuery = '/rec/recommend'
    var recQueryData = {
        'mashupInfo':null,
        'targetApiList':[apiName],
        'recNum':15,
    }
    if (mode.data)
        recQueryData['mode'] = 'full'
    else
        recQueryData['mode'] = 'minimal'
        
    axios.post(recQuery, recQueryData).then((res) => {
        loading.value = false
        recResult.arr = res['data']['recommended cloud API list']
    }).catch((err) => {
        loading.value = false
        console.log(err)
    })
}

function getApiInfo() {
    var apiQuery = `/backend/getPwData?pageNum=1&pageSize=10&dtype=api`
    apiQuery += `&filterMetric=Name&filterValue=${encodeURIComponent(apiName)}&precise=true`
    axios.get(apiQuery).then((res) => {
        ad.data = res['data'].slice(1)[0]
    }).catch((err) => {
        ad.data = {}
        console.log(err)
    })
}

getApiInfo()
recommend()

</script>

<style>
.el-popper.is-customized {
  /* Set padding to ensure the height is 32px */
  padding: 6px 12px;
  background: linear-gradient(90deg, rgb(159, 229, 151), rgb(204, 229, 129));
}

.el-popper.is-customized .el-popper__arrow::before {
  background: linear-gradient(45deg, #b2e68d, #bce689);
  right: 0;
}

.el-switch {
    caret-color: transparent;
}
.el-table {
    caret-color: transparent;
}
</style>