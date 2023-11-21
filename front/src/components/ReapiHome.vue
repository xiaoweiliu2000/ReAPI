<template>
    <img src="../assets/reapi_icon.svg" style="width: 200px; margin-top: 20px; margin-bottom: 20px;" class="noselect" />

    <h1 class="title">Hello, welcome to ReAPI !</h1>
    <p class="myparagraph">ReAPI is a free, open knowledge base and experimental online <router-link :to="'/knowledge/api'">cloud API</router-link> complementary <b style="color: red;">re</b>commendation platform for cloud API ecology. ReAPI was built to help developers easily build <router-link :to="'/knowledge/mashup'">mashup</router-link>s with cloud APIs, and to help researchers explore how to build practical, user-friendly, high-performance cloud API recommendation services. </p> 
    <p class="myparagraph">The data for the cloud API knowledge base was <b style="color: red;">re</b>stored from <router-link :to="'/knowledge/programmableweb'">ProgrammableWeb</router-link>, which was a common admitted cloud API repository in academia. We claim that the data will only be used for academic research purposes. Moreover, another data source will be added soon, which is collected from a living, <b style="color: red;">re</b>al-world, large-scale cloud API ecosystem that is never explored before.</p>
    <p class="myparagraph">We plan to release our source code and data for this project as soon as it is completed. </p>

    <h1 class="title">Explore</h1>
    <p class="myparagraph">Browse thousands of cloud APIs and mashups. Explore real-world cloud API ecosystems freely. </p> 
    <el-space wrap>
        <router-link to="/apihub">
            <el-button size="large" color="#0070c0" class="mybutton" plain><el-icon><MostlyCloudy /></el-icon>&nbsp;Cloud API Hub</el-button> 
        </router-link>
        <router-link to="/mashuphub">
            <el-button size="large" color="#0070c0" class="mybutton" plain><el-icon><Menu /></el-icon>&nbsp;Mashup Hub</el-button>
        </router-link>
    </el-space>

    <h1 class="title">Recommend</h1>
    <p class="myparagraph">Cloud API complementary recommendation techniques have been seamlessly integrated into the browsing scenarios, which will help you quickly find the cloud API you want.</p>

    <h1 class="title">Learn</h1>
    <p class="myparagraph">Read our carefully chosen and user-uploaded articles on cloud API ecology. Be free to learn about cloud APIs and share your knowledge.</p>
    <router-link to="/knowledge">
        <el-button size="large" color="#0070c0" class="mybutton" plain><el-icon><Management /></el-icon>&nbsp;Knowledge</el-button> 
    </router-link>
    
    <h1 class="title">Create</h1>
    <p class="myparagraph">Create a new mashup easily with our experimental AI-driven tool EasyMashup, powered by cloud API complementary recommendation techniques.</p>
    <router-link to="/easymashup">
        <el-button size="large" color="#0070c0" class="mybutton" plain><el-icon><Opportunity /></el-icon>&nbsp;EasyMashup</el-button> 
    </router-link>

    <h1 class="title">Open</h1>
    <p class="myparagraph"><b>A cloud API for cloud API complementary recommendation</b> is implemented and available for open access. Thanks to program optimization, distributed computing, and specialized load balancing algorithms, our online cloud API complementary recommendation service can respond within 300 milliseconds and handle 50+ concurrent requests per second. We also open the real-time load  and Quality of Service (QoS) monitoring data of this cloud API for researchers.</p>

    <router-link to="/openapi">
        <el-button size="large" color="#0070c0" class="mybutton" plain><el-icon><Lightning /></el-icon>&nbsp;Open API</el-button>
    </router-link>
</template>
  
<script setup>
</script>
  
<style>
</style>