<template>
    <h1 class="title">Mini Wiki</h1>
    <div class="knowledge-collapse">
        <el-collapse v-model="activeNames">
            <el-collapse-item name="0">
                <template #title>
                    <span class="knowledge-collapse-content">Cloud API</span>
                </template>
                <div class="knowledge-collapse-content">
                    Cloud application programming interface (API) is an essential middleware to expose cloud services to users [1]. Cloud APIs permit data transfer and communication with cloud services. With cloud APIs, users can easily access cloud services as they connect to the Internet. Cloud APIs significantly reduce the barriers to employing cloud services, thereby simplifying software development. As a result, cloud APIs are now an integral part of software.   
                </div>
                [1] Basole R C. On the evolution of service ecosystems: A study of the emerging API economy[J]. Handbook of Service Science, Volume II, 2019: 479-495.
            </el-collapse-item>
            <el-collapse-item name="1">
                <template #title>
                    <span class="knowledge-collapse-content">Cloud Service</span>
                </template>
                <div class="knowledge-collapse-content">
                    Cloud services are software or infrastructure resources that are hosted by third-party providers and made available to users through the Internet. By publishing their services to the cloud, cloud service providers can take full advantage of the cloud architecture. Reliable, flexible, and scalable cloud services are provided, while users no longer need to deploy these services locally. With these advantages, cloud services have shown rich applications in areas such as software development, artificial intelligence, and big data analysis [2].   
                </div>
                [2] Lee K Y, Ha N. AI platform to accelerate API economy and ecosystem[C]//2018 International Conference on Information Networking (ICOIN). IEEE, 2018: 848-852.
            </el-collapse-item>
            <el-collapse-item name="2">
                <template #title>
                    <span class="knowledge-collapse-content">Mashup</span>
                </template>
                <div class="knowledge-collapse-content">
                    The emergence of cloud APIs has given rise to a type of lightweight software called mashups, which are composed of cloud APIs [3]. Each mashup invokes several cloud APIs to implement its main functionality. Mashups have gained popularity in recent years due to their lightweight advantage. To ease the development of applications such as mashups, there have been some open cloud API repositories such as ProgrammableWeb and RapidAPI.
                </div>
                [3] Jula A, Sundararajan E, Othman Z. Cloud computing service composition: A systematic literature review[J]. Expert systems with applications, 2014, 41(8): 3809-3824.
            </el-collapse-item>
            <el-collapse-item name="3">
                <template #title>
                    <span class="knowledge-collapse-content">ProgrammableWeb</span>
                </template>
                <div class="knowledge-collapse-content">
                    ProgrammableWeb is a comprehensive online resource and community dedicated to the world of cloud APIs. Founded in 2005, it serves as a central hub for developers, businesses, and enthusiasts interested in exploring, discovering, and integrating APIs to enhance web and application development. Sadly, ProgrammableWeb was shutdown by MuleSoft by the end of 2022 due to commercial reasons. <br>
                    "After 17 years, ProgrammableWeb has shut down operations. Since joining MuleSoft in 2013, ProgrammableWeb has sought to bring awareness to the impact APIs can have on modern businesses. Nearly a decade later it has undoubtedly played a role in helping the wider market understand the power of APIs" [4].
                </div>
                [4] https://www.mulesoft.com/programmableweb
            </el-collapse-item>
        </el-collapse>
    </div>
</template>


  
<script setup>
import { ref,defineProps } from 'vue'
var activeNames = ref(['-1'])

const props = defineProps(['id'])
var wikiName = decodeURIComponent(props.id)

console.log(wikiName)

if (wikiName == 'api')
    activeNames = ref(['1'])
else if (wikiName == 'mashup')
    activeNames = ref(['2'])
else if (wikiName == 'programmableweb')
    activeNames = ref(['3'])

</script>
  
<style>
.knowledge-collapse {
    width:60%;
    margin-left:20%;
    text-align: left;
}
.knowledge-collapse-content {
    font-family: Arial, Helvetica, sans-serif; 
    font-size: 18px
}
</style>