<template>
  <el-container>
    <el-header>
      <NaviBar :activeIndex="activeIndex" />
    </el-header>
    <el-main class="myelmain">
      <router-view :key="$route.path + $route.query"></router-view>
    </el-main>
    <el-footer>
      <ReapiFooter />
    </el-footer>
  </el-container>
</template>

<script>
import NaviBar from './components/NaviBar.vue';
import ReapiFooter from './components/ReapiFooter.vue';

export default {
  name: 'App',
  components: {
    NaviBar,
  }
}
</script>


<script setup>
const activeIndex = '/home'
</script>

<style>
#app {
  /* font-family: Avenir, Helvetica, Arial, sans-serif; */
  /* -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale; */
  text-align: center;
  /* color: #2c3e50; */
  margin-top: 0px;
  margin-left: 0px;
  margin-right: 0px;
}

/* 减小页面边距 */
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
}

.el-menu-item.is-disabled {
  cursor: default;
}

.myelmain {
  min-height: calc(85vh); 
}

.noselect {
  -moz-user-select:none;
  -webkit-user-select:none; 
  -ms-user-select:none;
  user-select:none;
}
.myparagraph {
    width: 50%; margin-left: 25%; text-align: left; font-size: 19px; line-height: 150%; font-family: Arial, Helvetica, sans-serif; 
}
.mybutton {    
    font-size: 100%;
}
.title {
    background-image: linear-gradient(to right, #ff0000, #0070c0);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 32px;
}
a {
    text-decoration: none;
    color: cornflowerblue;
}
.el-popper {
    max-width: 60vw;
}
span, p {
    caret-color: transparent;
}
</style>
