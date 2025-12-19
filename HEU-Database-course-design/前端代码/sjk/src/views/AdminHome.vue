<template>
  <div class="admin-home">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>校园社团管理系统 - 管理员端</h2>
          <div class="user-info">
            <span>管理员：{{ user.username }}</span>
            <el-button @click="handleLogout" size="small">退出</el-button>
          </div>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="200px">
          <el-menu
            :default-active="activeMenu"
            class="admin-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="clubs">
              <i class="el-icon-office-building"></i>
              <span>社团管理</span>
            </el-menu-item>
            <el-menu-item index="activities">
              <i class="el-icon-date"></i>
              <span>活动管理</span>
            </el-menu-item>
            <el-menu-item index="members">
              <i class="el-icon-user"></i>
              <span>成员管理</span>
            </el-menu-item>
            <el-menu-item index="users">
              <i class="el-icon-s-custom"></i>
              <span>用户管理</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main>
          <ClubManage v-if="activeMenu === 'clubs'" />
          <ActivityManage v-if="activeMenu === 'activities'" />
          <MemberManage v-if="activeMenu === 'members'" />
          <UserManage v-if="activeMenu === 'users'" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import ClubManage from '@/components/ClubManage'
import ActivityManage from '@/components/ActivityManage'
import MemberManage from '@/components/MemberManage'
import UserManage from '@/components/UserManage'

export default {
  name: 'AdminHome',
  components: { ClubManage, ActivityManage, MemberManage, UserManage },
  data() {
    return {
      activeMenu: 'clubs',
      user: JSON.parse(sessionStorage.getItem('user') || '{}')
    }
  },
  methods: {
    handleLogout() {
      sessionStorage.removeItem('user')
      this.$router.push('/login')
    },
    handleMenuSelect(index) {
      this.activeMenu = index
    }
  }
}
</script>

<style scoped>
.admin-home {
  height: 100vh;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}
.admin-menu {
  height: 100%;
}
::v-deep .el-header {
  background: linear-gradient(90deg, #6da1fcd9 0%, #ffc0f0ff 100%);
  color: #fff;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}
.user-info span {
  color: #fff;
}

::v-deep .admin-menu .el-menu-item {
  font-size: 16px;
  height: 56px;
  line-height: 56px;
}

::v-deep .admin-menu .el-menu-item i {
  font-size: 18px;
  margin-right: 8px;
}

::v-deep .admin-menu .el-menu-item span {
  font-size: 16px;
  font-weight: 500;
}

::v-deep .admin-menu .el-menu-item.is-active {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

::v-deep .admin-menu .el-menu-item:not(.is-active):hover {
  background-color: #f5f7fa;
  color: #409eff;
}
</style>