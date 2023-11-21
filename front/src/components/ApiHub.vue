<template>
    <el-tooltip class="box-item" effect="dark" content="Back to top" placement="left" :hide-after="0">
        <el-backtop :right="80" :bottom="140" class="bigCircleButton" />
    </el-tooltip>
    <div style="width: 75%; margin: auto;">
        <div style="width: 600px;">
            <el-input v-model="filterValue" size="large" placeholder="Search cloud APIs ..." class="input-with-select"
                style="margin-top: 20px;" @keyup.enter.native="searchAPIData">
                <template #prepend>
                    <el-select v-model="filterMetric" placeholder="Select" style="width: 110px" size="large">
                        <el-option label="Name" value="Name" />
                        <el-option label="Category" value="Primary Category" />
                    </el-select>
                </template>
                <template #append>
                    <el-button :icon="Search" @click="searchAPIData" />
                </template>
            </el-input>
        </div>
        <el-form style="margin-top: 20px;">
            <el-form-item label="sort by">
                <el-radio-group v-model="sortBy" @change=getAPIData>
                    <el-radio label="default">Default</el-radio>
                    <el-radio label="Name">Name</el-radio>
                    <el-radio label="Primary Category">Category</el-radio>
                    <el-radio label="Invoked Times">Invoked Times</el-radio>
                </el-radio-group>
            </el-form-item>
            <el-form-item label="sort order">
                <el-radio-group v-model="sortOrder" @change=getAPIData>
                    <el-radio label="ascending">Ascending</el-radio>
                    <el-radio label="descending">Descending</el-radio>
                </el-radio-group>
            </el-form-item>
            <el-form-item>
                <el-text class="mx-1">Found {{ resultCount.value }} cloud API<span v-if="(resultCount.value > 1)">s</span>.</el-text>
            </el-form-item>
        </el-form>

        <el-card class="box-card" shadow="hover">
            <el-table :data="tableData.arr" style="width: 100%" :row-style="{height:'60px'}" table-layout="auto">
                <el-table-column label="Name" prop="Name">  
                    <template #default="props">
                        <router-link target="_blank" :to="'/api/' + encodeURIComponent(props.row['Name'])">
                            {{ props.row['Name'] }}
                        </router-link>                    
                    </template>
                </el-table-column>   
                <el-table-column label="Description"  prop="Description" :show-overflow-tooltip="true" min-width="200%"/>
                <el-table-column label="Category" prop="Primary Category" />
                <el-table-column label="Invoked Times" prop="Invoked Times" />
            </el-table>

            <!-- page indicator -->
            <div style="position: relative; height: 30px; margin-top: 15px;">
                <el-pagination 
                    v-model:current-page="currentPage" 
                    :background="false" 
                    layout="prev, pager, next, jumper"
                    :total="resultCount.value" 
                    :page-size="pageSize"
                    @current-change="getAPIData"
                    style="position: absolute; left: 50%; transform: translateX(-50%); height: 30px;" 
                />
            </div>
        </el-card>
    </div>
</template>
  
<script setup>
import axios from 'axios'
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { reactive } from '@vue/reactivity';

const filterValue = ref('')
const filterMetric = ref('Name')
const sortBy = ref('default')
const sortOrder = ref('ascending')
const currentPage = ref(1)
var searchFlag = false

var pageSize = 25
var resultCount = reactive({
    value:0
})
var tableData = reactive({
    arr:[]
})

function searchAPIData() {
    searchFlag = true
    getAPIData()
}

function getAPIData() {
    var api = `/backend/getPwData?pageNum=${currentPage.value}&pageSize=${pageSize}&dtype=api`
    // sort
    if(sortBy.value != 'default')
        api += `&sortBy=${sortBy.value}&sortOrder=${sortOrder.value}`
    // search
    if(searchFlag == true)
        api += `&filterMetric=${filterMetric.value}&filterValue=${filterValue.value}`

    axios.get(api).then((res)=>{
        resultCount.value = res['data'][0]['resultCount']
        tableData.arr = res['data'].slice(1)
        //console.log(res['data'])
        //console.log(res['data'][0]) 
        // processAPIData(tableData.arr)
      }).catch((err)=>{
        tableData.arr = []
        console.log(err)
      })
}   

// initial setup
getAPIData()

</script>

<style>

</style>