<template>
  <div class="user-home">
    <el-container class="layout-container">
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-content">
          <h2 class="title">校园社团管理系统 - 用户端</h2>
          <div class="user-info">
            <span class="welcome-text">用户：{{ user.username }}</span>
            <el-button @click="handleLogout" size="small" class="logout-btn">退出</el-button>
          </div>
        </div>
      </el-header>
      
      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <el-card class="content-card">
          <el-tabs v-model="activeTab" class="main-tabs">
            <el-tab-pane label="社团浏览" name="clubs">
              <ClubList @create-club="showCreateClub = true" />
            </el-tab-pane>
            <el-tab-pane label="活动中心" name="activities">
              <ActivityList />
            </el-tab-pane>
            <el-tab-pane label="我的社团" name="myClubs">
              <MyClubs />
            </el-tab-pane>
            <el-tab-pane label="我的活动" name="myActivities">
              <MyActivities />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-main>
    </el-container>
    
    <!-- 创建社团对话框 -->
    <el-dialog 
      title="创建社团" 
      :visible.sync="showCreateClub"
      width="500px"
      center
    >
      <el-form :model="clubForm" :rules="clubRules" ref="clubForm" label-width="80px">
        <el-form-item label="社团名称" prop="club_name">
          <el-input v-model="clubForm.club_name" placeholder="请输入社团名称"></el-input>
        </el-form-item>
        <el-form-item label="社团类别" prop="category">
          <el-select v-model="clubForm.category" placeholder="请选择类别" style="width: 100%">
            <el-option label="学术科技" value="学术科技"></el-option>
            <el-option label="文化体育" value="文化体育"></el-option>
            <el-option label="志愿公益" value="志愿公益"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="社团简介" prop="description">
          <el-input 
            type="textarea" 
            v-model="clubForm.description" 
            placeholder="请输入社团简介"
            :rows="3"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showCreateClub = false" size="medium">取消</el-button>
        <el-button type="primary" @click="handleCreateClub" size="medium">创建</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import ClubList from '@/components/ClubList'
import ActivityList from '@/components/ActivityList'
import MyClubs from '@/components/MyClubs'
import { createClub } from '@/api/club'
import MyActivities from '@/components/MyActivities'

export default {
  name: 'UserHome',
  components: { ClubList, ActivityList, MyClubs, MyActivities },
  data() {
    return {
      activeTab: 'clubs',
      showCreateClub: false,
      user: JSON.parse(sessionStorage.getItem('user') || '{}'),
      clubForm: {
        club_name: '',
        category: '',
        description: ''
      },
      clubRules: {
        club_name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
        category: [{ required: true, message: '请选择社团类别', trigger: 'change' }]
      }
    }
  },
  methods: {
    handleLogout() {
      this.$confirm('确定要退出登录吗？', '提示', {
        type: 'warning'
      }).then(() => {
        sessionStorage.removeItem('user')
        this.$router.push('/login')
      })
    },
    handleCreateClub() {
      this.$refs.clubForm.validate(valid => {
        if (valid) {
          createClub({
            ...this.clubForm,
            founder_id: this.user.id
          }).then(() => {
            this.$message.success('创建成功')
            this.showCreateClub = false
            this.$refs.clubForm.resetFields()
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.user-home {
  height: 100vh;
  background: #f5f7fa;
}

.layout-container {
  height: 100%;
}

/* 头部样式修改为与管理端一致 */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.welcome-text {
  display: flex;
  align-items: center;
  gap: 20px;
}

.main-content {
  padding: 20px;
  background: #f5f7fa;
}

.content-card {
  min-height: calc(100vh - 120px);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.main-tabs {
  min-height: 500px;
}

.main-tabs >>> .el-tabs__item {
  font-size: 16px;
  font-weight: 500;
  height: 50px;
  line-height: 50px;
  padding: 0 24px;
}

.main-tabs >>> .el-tabs__nav-wrap::after {
  height: 1px;
}

.main-tabs >>> .el-tabs__active-bar {
  height: 3px;
  background-color: #409eff;
}

.main-tabs >>> .el-tabs__item.is-active {
  color: #409eff;
  font-weight: 600;
}

.main-tabs >>> .el-tabs__item:hover {
  color: #409eff;
}

.dialog-footer {
  text-align: center;
}
</style>