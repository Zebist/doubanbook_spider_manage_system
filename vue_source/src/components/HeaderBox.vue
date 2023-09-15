<template>
    <!-- 固定的顶部导航栏 -->
    <div class="top-nav" height="auto">
      <div class="nav-content">
        <!-- 左侧标题 -->
        <h1 class="nav-title">爬虫管理系统</h1>
        <!-- 右侧按钮 -->
        <el-button id="sync_btn" type="primary" @click="startCrawling">开始爬取</el-button>
      </div>
    </div>
</template>

<script>
import { Message } from 'element-ui';
export default {
  methods: {
    startCrawling() {
      // 触发爬虫爬取数据
      this.$axios.post("api/spider_center/")
            .then(response => {
              Message({
                type: 'success',
                message: response.data.message,
                duration: 3000,
              });
            })
            .catch(error => {
                console.error(error);
                Message({
                  type: 'error',
                  message: '服务异常，请稍候再试！',
                  duration: 3000,
                });
            });
    }
  }
};
</script>

<style scoped>
/* 顶部导航条 */
.top-nav {
  color: #409EFF;
  border-bottom: 1px solid #ccc;
  margin: 0 auto;
  /* position: fixed;
  top: 10px;
  left: 0;
  right: 0;
  z-index: 100;
   */
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
/* 标题 */
.nav-title {
  font-size: 45px;
  font-weight: bold;
  border-bottom: 3px solid #409EFF;
  margin: 0;
  padding: 20px;
  padding-bottom: 30px;  /* 抵消按钮的margin-bottom */
}

.nav-title:hover {
    background: #d9ecff;
    cursor: pointer;
}


/* 爬取按钮 */
#sync_btn {
  font-size: 35px;
  padding: 33px;
  background: #409eff;
  color: #fff;
  border-radius: 15px;
  margin-bottom: 10px;
}

#sync_btn:hover {
  background: #337ecc;
}

</style>
