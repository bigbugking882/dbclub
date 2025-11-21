<template>
  <div>
    <div class="header">
      校园社团管理系统---管理端
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
            <span slot="title">社团管理</span>
          </el-menu-item>
          <el-menu-item index="2">
            <i class="el-icon-user"></i>
            <span slot="title">成员管理</span>
          </el-menu-item>
          <el-menu-item index="3">
            <i class="el-icon-calendar"></i>
            <span slot="title">活动管理</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容区 -->
      <div class="main">
        <manage-club v-show="active === '1'"></manage-club>
        <manage-member v-show="active === '2'"></manage-member>
        <manage-activity v-show="active === '3'"></manage-activity>
      </div>
    </div>
  </div>
</template>

<script>
import ManageClub from './ManageClub.vue'
import ManageMember from './ManageMember.vue'
import ManageActivity from './ManageActivity.vue'

export default {
  components: {
    ManageClub,
    ManageMember,
    ManageActivity
  },
  data() {
    return {
      active: '1'  // 默认显示社团管理
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