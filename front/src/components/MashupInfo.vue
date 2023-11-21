<template>
    <el-container style="margin-top: -20px;">
        <el-main style="margin-left: 5%;">
            <h1 class="title" style="font-size: 150%;">Mashup Profile</h1>
            <el-card shadow="hover" round>
                <el-descriptions v-bind="md.data" :column="1" border>
                    <el-descriptions-item label="Name">{{ md.data['Name'] }}</el-descriptions-item>
                    <el-descriptions-item label="Description">{{ md.data['Description'] }}</el-descriptions-item>
                        <el-descriptions-item label="Primary Category">{{ md.data["Primary Category"] }}</el-descriptions-item>
                        <el-descriptions-item label="Sceondary Categories">{{ md.data['Sceondary Categories'] }}</el-descriptions-item>
                        <el-descriptions-item label="Related APIs" >
                            <span v-for="(apiName, index) in md.data['API List']">
                                <!-- [Remove the Spaces at the beginning and end of the string] .replace(/^\s+|\s+$/gm, '')) -->
                                <router-link :to="'/api/'+encodeURIComponent(apiName.replace(/^\s+|\s+$/gm, ''))">{{ apiName }}</router-link>
                                <span v-if="index<md.data['API List'].length-1">, </span>
                            </span>
                        </el-descriptions-item>
                        <el-descriptions-item label="Url">{{ md.data['Url'] }}</el-descriptions-item>
                        <el-descriptions-item label="Company">{{ md.data['Company'] }}</el-descriptions-item>
                        <el-descriptions-item label="Type">{{ md.data['Type'] }}</el-descriptions-item>
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
import { defineProps, reactive } from 'vue'

const props = defineProps(['id'])
var loading = reactive({
    value:true
})
var mashupName = decodeURIComponent(props.id)
var md = reactive({
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
    var mashupInfo = {
        'MashupName' :md.data['Name'],
        'MashupTags' :md.data['Tags'],
        'MashupCategory' :md.data['Tags'],
        'MashupDescription' :md.data['Description'],
        'MashupSubDate' :md.data['Submitted Date'],
        'MashupUrl' :md.data['Url'],
        'MashupCompany' :md.data['Company'],
        'MashupType' :md.data['Type'],
        'MashupFollowerNum' :md.data['FollowerNum'],
        'MashupRelatedAPIs' :md.data['Related APIs']
    }
    mashupInfo['MashupTags'] = mashupInfo['MashupTags'].split(', ')
    mashupInfo['MashupRelatedAPIs'] = mashupInfo['MashupRelatedAPIs'].split(', ')
    mashupInfo['MashupCategory'] = mashupInfo['MashupTags'][0]

    var recQuery = '/rec/recommend'
    var recQueryData = {
        'mashupInfo':mashupInfo,
        'targetApiList':mashupInfo['MashupRelatedAPIs'],
        'recNum':10,
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

function getMashupInfo() {
    var mashupQuery = `/backend/getPwData?pageNum=1&pageSize=10&dtype=mashup`
    mashupQuery += `&filterMetric=Name&filterValue=${encodeURIComponent(mashupName)}`
    axios.get(mashupQuery).then((res) => {
        md.data = res['data'].slice(1)[0]
        recommend()
        md.data["Primary Category"] = md.data['Tags'].split(', ')[0]
        md.data["Sceondary Categories"] = md.data['Tags'].split(', ').slice(1).join(', ')
        md.data["API List"] = md.data["Related APIs"].split(', ')
    }).catch((err) => {
        md.data = {}
        console.log(err)
    })
}

getMashupInfo()
</script>