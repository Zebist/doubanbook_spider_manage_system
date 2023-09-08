<template>
  <div id="app">
    <el-container>
      <el-header style="height: auto;">
        <HeaderBox class="header-box" />
      </el-header>
      <el-main>
        <TableBox class="table-box" />
      </el-main>
      <el-footer />
    </el-container>
  </div>
</template>

<script>
import HeaderBox from './components/HeaderBox.vue'
import TableBox from './components/TableBox.vue'

export default {
  name: 'App',
  components: {
    HeaderBox,
    TableBox,
  }
}
</script>

<style>
#app {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, antarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif, Microsoft Yahei,Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
.header-box, .table-box {
    width: 90%;
    margin: 0 auto;
}
</style>
