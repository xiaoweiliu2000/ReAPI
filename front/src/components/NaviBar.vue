<template>
    <el-menu    
        :default-active="$route.path"
        mode="horizontal" 
        :router="true"
        class="noselect"
    >     
      <router-link to="/home" style=" margin-top: 14px;">
        <img src="../assets/reapi_icon.svg" style="width: 100px; margin-left: 30px; margin-right: 20px;" />
      </router-link>
      <el-menu-item style="cursor: default;" disabled>|</el-menu-item>
      <el-menu-item index="/home"><el-icon><HomeFilled /></el-icon>Home</el-menu-item>
      <el-menu-item index="/apihub"><el-icon><MostlyCloudy /></el-icon>Cloud API Hub</el-menu-item>
      <el-menu-item index="/mashuphub" ><el-icon><Menu /></el-icon>Mashup Hub</el-menu-item>
      <el-menu-item index="/knowledge"><el-icon><Management /></el-icon>Knowledge<el-tag round size="small">Beta</el-tag></el-menu-item>
      <el-menu-item index="/easymashup"><el-icon><Opportunity /></el-icon>EasyMashup<el-tag round size="small">Beta</el-tag></el-menu-item>
      <el-menu-item index="/openapi"><el-icon><Lightning /></el-icon>Open API<el-tag round size="small">Beta</el-tag></el-menu-item>
    </el-menu>
</template>
  
<script>
export default {
  name: 'NaviBar',
  props: {
    activeIndex: String,
  }
}
</script>
  
<style>
.noselect {
  -moz-user-select:none;
  -webkit-user-select:none; 
  -ms-user-select:none;
  user-select:none;
}
</style>
  