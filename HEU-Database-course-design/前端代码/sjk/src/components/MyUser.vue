<template>
  <div>
    <div class="header">
      校园社团管理系统---用户端
    </div>
    <div class="body">
      <!-- 左侧菜单 -->
      <div class="liner">
        <el-menu 
          default-active="1" 
          class="el-menu-vertical-demo" 
          background-color="#545c64" 
          text-color="#fff"
          active-text-color="#ffd04b" 
          @select="handleSelect"
        >
          <el-menu-item index="1">
            <i class="el-icon-sitemap"></i>
            <span slot="title">社团列表</span>
          </el-menu-item>
          <el-menu-item index="2">
            <i class="el-icon-user"></i>
            <span slot="title">我的社团</span>
          </el-menu-item>
          <el-menu-item index="3">
            <i class="el-icon-calendar"></i>
            <span slot="title">活动报名</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容区 -->
      <div class="main">
        <user-club-list v-show="active === '1'"></user-club-list>
        <user-my-club v-show="active === '2'"></user-my-club>
        <user-activity v-show="active === '3'"></user-activity>
      </div>
    </div>
  </div>
</template>

<script>
import UserClubList from './UserClubList.vue'
import UserMyClub from './UserMyClub.vue'
import UserActivity from './UserActivity.vue'

export default {
  components: {
    UserClubList,
    UserMyClub,
    UserActivity
  },
  data() {
    return {
      active: '1'
    }
  },
  methods: {
    handleSelect(index) {
      this.active = index
    }
  }
}
</script>

<style scoped>
/* 与MyManage.vue样式一致 */
.header {
  width: 100%;
  height: 10vh;
  line-height: 10vh;
  font-size: 25px;
  font-weight: 800;
  background-color: #e3e3e3;
  padding-left: 20px;
}
.body {
  width: 100%;
  height: 90vh;
  display: flex;
}
.liner {
  width: 15%;
  height: 100%;
}
.main {
  width: 85%;
  padding: 20px;
  overflow-y: auto;
}
</style>