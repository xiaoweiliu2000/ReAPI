<template>
    <el-container>
        <el-main>
            <h1 class="title" style="font-size: 150%;">
                Enter Mashup Information
                <el-tooltip
                    content = "Fill out this form to let us know your preferences for cloud APIs."
                    placement = "right"
                >
                    <el-icon size="18" color="cornflowerblue"><InfoFilled /></el-icon>
                </el-tooltip>
            </h1>
            <el-form :model="form" label-width="150px" style="width: 80%; margin-left: 10%;"> 
                <el-form-item>
                    <template #label>
                        Name
                        <el-tooltip
                            content = "This name will not be used for recommendations, so simply name your mashup as you wish."
                            placement = "right"
                        >
                            <el-icon><QuestionFilled /></el-icon>
                        </el-tooltip>
                    </template>
                    <el-input v-model="form.name" />
                </el-form-item>
                <el-form-item label="Tags">
                    <el-select-v2
                        v-model="form.tags"
                        filterable
                        :options="mashupTagList.data"
                        placeholder="Select or type"
                        style="width: 100%;"
                        :height="500"
                        multiple
                        clearable
                        v-on:change="recommend"
                    />
                </el-form-item>
                <el-form-item label="Type">
                    <el-select-v2
                        v-model="form.type"
                        filterable
                        :options="typeList"
                        placeholder="Select"
                        style="width: 150px;"
                        clearable
                        v-on:change="recommend"
                    />
                </el-form-item>
                <el-form-item>
                    <template #label>
                        Target Cloud APIs
                        <el-tooltip
                            content = "These are the cloud APIs that you have chosen for mashup creation."
                            placement = "right"
                        >
                            <el-icon><QuestionFilled /></el-icon>
                        </el-tooltip>
                    </template>
                    <el-select-v2
                        v-model="form.targetApiList"
                        filterable
                        :options="apiList.data"
                        placeholder="Select or type"
                        style="width: 100%;"
                        :height="500"
                        multiple
                        clearable
                        v-on:change="recommend"
                    />
                </el-form-item>
                <el-form-item>
                    <template #label>
                        Description
                        <el-tooltip
                            content = "This description will not be used for recommendations at this time. We are working on adding textual features to our recommendation workflow."
                            placement = "right"
                        >
                            <el-icon><QuestionFilled /></el-icon>
                        </el-tooltip>
                    </template>
                    <el-input 
                        v-model="form.description" 
                        type="textarea" 
                        :rows="15" 
                        placeholder="Enter the description for this mashup. Note that this description will not be used for recommendations at this time. We are working on improvements to it." 
                    />
                </el-form-item>
            </el-form>
        </el-main>
        <el-aside width="30%">
            <h1 class="title" style="font-size: 150%; margin-top: 45px;">Recommended for you</h1>
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
                        <router-link target="_blank" :to="'/api/' + encodeURIComponent(props.row['ApiName'])">
                            {{ props.row['ApiName'] }}
                        </router-link>                    
                    </template>
                </el-table-column>   
                <el-table-column label="Category" prop="ApiCategory" />
                <el-table-column label = "Option" prop="ApiName">
                    <template #default="props">
                        <el-button @click="addAPI(props.row['ApiName'])" type="primary" text :bg="false">
                            <el-icon size="20" ><CirclePlus /></el-icon>
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-aside>
    </el-container>
</template>
  
<script setup>
import axios from 'axios'
import { reactive } from 'vue'

// do not use same name with ref
const form = reactive({
    name :  '',
    targetApiList: [], 
    tags : [], 
    type : null,
    description : ''
})
const mashupTagList = reactive({
    data : []
})
const apiList = reactive({
    data : []
})
const typeList = [
    {
        value : 'Web',
        label : 'Web'
    },
    {
        value : 'Desktop',
        label : 'Desktop'
    },
    {
        value : 'Mobile',
        label : 'Mobile'
    },
    {
        value : 'Other',
        label : 'Other'
    },
]
var recResult = reactive({
    arr:[]
})
var loading = reactive({
    value:false
})
var mode = reactive({
    data:false
})

function getMashupTagList() {
    var query = `/backend/getPwDataCollection?type=mashupTag`

    axios.get(query).then((res) => {
        for(let i = 0; i < res['data']['list'].length; i++)
            mashupTagList.data.push({
                value : res['data']['list'][i],
                label : res['data']['list'][i]
            })
    }).catch((err) => {
        mashupTagList.data = []
        console.log(err)
    })
}

function addAPI(apiName) {
    form.targetApiList.push(apiName)
    recommend()
}

function getApiList() {
    var query = `/backend/getPwDataCollection?type=api`

    axios.get(query).then((res) => {
        var currentGroup = null
        var currentGroupLabel = null
        for(let i = 0; i < res['data']['list'].length; i++) {
            var label = res['data']['list'][i][0].toUpperCase()
            if (label != currentGroupLabel) {
                if (currentGroup!=null)
                    apiList.data.push(currentGroup)
                currentGroupLabel = label
                currentGroup = {
                    value : currentGroupLabel,
                    label : currentGroupLabel,
                    options : []
                }
            }
            currentGroup.options.push({
                value : res['data']['list'][i],
                label : res['data']['list'][i]
            })
        }
        apiList.data.push(currentGroup)
    }).catch((err) => {
        apiList.data = []
        console.log(err)
    })
}

function recommend() {
    loading.value = true
    var mashupInfo = {
        'MashupName' : form.name,
        'MashupTags' : form.tags,
        'MashupCategory' : form.tags[0],
        'MashupDescription' : form.description,
        'MashupType' : form.type,
        'MashupRelatedAPIs' : form.targetApiList
    }

    if (mashupInfo['MashupTags'].length == 0 && mashupInfo['MashupType'] == null)
        mashupInfo = null
    else if (mashupInfo['MashupType'] == '')
        mashupInfo['MashupType'] = 'NULL'

    var recQuery = '/rec/recommend'
    var recQueryData = {
        'mashupInfo' : mashupInfo,
        'targetApiList' : form.targetApiList,
        'recNum':10,
    }
    if (mode.data)
        recQueryData['mode'] = 'full'
    else
        recQueryData['mode'] = 'minimal'

    if (mashupInfo != null || form.targetApiList.length) {
        axios.post(recQuery, recQueryData).then((res) => {
            loading.value = false
            recResult.arr = res['data']['recommended cloud API list']
        }).catch((err) => {
            loading.value = false
            console.log(err)
        })
    }
    else {
        loading.value = false
        recResult.arr = []
    }
}


getApiList()
getMashupTagList()

</script>

<style>



</style>
