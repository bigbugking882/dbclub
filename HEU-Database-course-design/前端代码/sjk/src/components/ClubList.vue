<template>
  <div class="club-list">
    <div class="header">
      <h3>社团列表</h3>
      <el-button type="primary" @click="showCreateDialog = true">创建社团</el-button>
    </div>
    
    <div class="filter">
      <el-select v-model="filterCategory" placeholder="筛选类别" @change="loadClubs">
        <el-option label="全部类别" value=""></el-option>
        <el-option label="学术科技" value="学术科技"></el-option>
        <el-option label="文化体育" value="文化体育"></el-option>
        <el-option label="志愿公益" value="志愿公益"></el-option>
      </el-select>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8" v-for="club in clubList" :key="club.club_id" class="club-card-col">
        <el-card class="club-card">
          <div slot="header" class="club-header">
            <h4>{{ club.club_name }}</h4>
            <el-tag :type="getCategoryType(club.category)">{{ club.category }}</el-tag>
          </div>
          <div class="club-content">
            <p class="club-desc">{{ club.description || '暂无简介' }}</p>
            <div class="club-info">
              <span>创始人: {{ club.founder_name }}</span>
              <span>创建时间: {{ formatDate(club.create_time) }}</span>
            </div>
          </div>
          <div class="club-actions">
            <el-button type="primary" size="mini" @click="handleJoinClub(club)">加入社团</el-button>
            <el-button size="mini" @click="viewClubDetail(club)">查看详情</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建社团对话框 -->
    <el-dialog title="创建社团" :visible.sync="showCreateDialog">
      <el-form :model="clubForm" :rules="clubRules" ref="clubForm">
        <el-form-item label="社团名称" prop="club_name">
          <el-input v-model="clubForm.club_name"></el-input>
        </el-form-item>
        <el-form-item label="社团类别" prop="category">
          <el-select v-model="clubForm.category" placeholder="请选择">
            <el-option label="学术科技" value="学术科技"></el-option>
            <el-option label="文化体育" value="文化体育"></el-option>
            <el-option label="志愿公益" value="志愿公益"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="社团简介" prop="description">
          <el-input type="textarea" v-model="clubForm.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateClub">创建</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// 导入所有需要的API函数
import { getClubs, createClub } from '@/api/club'
import { joinClub } from '@/api/member'
import { formatDate } from '@/utils/date'

export default {
  name: 'ClubList',
  data() {
    return {
      clubList: [],
      loading: false,
      showCreateDialog: false,
      filterCategory: '',
      clubForm: {
        club_name: '',
        category: '',
        description: ''
      },
      clubRules: {
        club_name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
        category: [{ required: true, message: '请选择社团类别', trigger: 'change' }]
      },
      user: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  mounted() {
    this.loadClubs()
  },
  methods: {
    loadClubs() {
      this.loading = true
      // 使用 getClubs 函数
      getClubs().then(res => {
        let clubs = res.data
        if (this.filterCategory) {
          clubs = clubs.filter(club => club.category === this.filterCategory)
        }
        this.clubList = clubs
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    handleCreateClub() {
      this.$refs.clubForm.validate(valid => {
        if (valid) {
          // 使用 createClub 函数
          createClub({
            ...this.clubForm,
            founder_id: this.user.id
          }).then((res) => {
            // 显示审核提示
            this.$message.success(res.message || '创建成功，等待管理员审核')
            this.showCreateDialog = false
            this.$refs.clubForm.resetFields()
            this.loadClubs()
          }).catch(error => {
            this.$message.error('创建失败: ' + (error.message || '未知错误'))
          })
        }
      })
    },
    handleJoinClub(club) {
      this.$confirm(`确定要加入 ${club.club_name} 吗？`, '提示', {
        type: 'info'
      }).then(() => {
        // 使用 joinClub 函数
        joinClub({
          club_id: club.club_id,
          user_id: this.user.id
        }).then(() => {
          this.$message.success('申请已提交，等待审核')
        })
      })
    },
    viewClubDetail(club) {
      this.$message.info(`查看 ${club.club_name} 的详情`)
    },
    getCategoryType(category) {
      const types = {
        '学术科技': 'primary',
        '文化体育': 'success', 
        '志愿公益': 'warning'
      }
      return types[category] || 'info'
    },
    formatDate
  }
}
</script>

<style scoped>
.club-list .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter {
  margin-bottom: 20px;
}
.club-card-col {
  margin-bottom: 20px;
}
.club-card {
  height: 300px;
  display: flex;
  flex-direction: column;
}
.club-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.club-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.club-desc {
  flex: 1;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
.club-info {
  margin-top: 10px;
  font-size: 14px;
  color: #999;
  display: flex;
  flex-direction: column;
}
.club-actions {
  margin-top: 10px;
  text-align: right;
}
</style>