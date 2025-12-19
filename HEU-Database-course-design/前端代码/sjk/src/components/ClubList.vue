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

    <!-- 社团详情对话框 -->
    <el-dialog 
      :title="currentClub ? currentClub.club_name + ' - 详情' : '社团详情'" 
      :visible.sync="showDetailDialog" 
      width="500px"
    >
      <div v-if="currentClub" class="club-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="社团名称">{{ currentClub.club_name }}</el-descriptions-item>
          <el-descriptions-item label="社团类别">
            <el-tag :type="getCategoryType(currentClub.category)">
              {{ currentClub.category }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创始人">{{ currentClub.founder_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentClub.create_time) }}</el-descriptions-item>
          <el-descriptions-item label="社团状态">
            <el-tag :type="currentClub.status === 1 ? 'success' : 'danger'">
              {{ currentClub.status === 1 ? '正常运行' : '已停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="社团简介">
            <div class="description-content">
              {{ currentClub.description || '暂无简介' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 统计信息 -->
        <div class="stats-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="stat-card">
                <div class="stat-icon member-icon">
                  <i class="el-icon-user"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ clubStats.total_members || 0 }}</div>
                  <div class="stat-label">总成员数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="stat-card">
                <div class="stat-icon activity-icon">
                  <i class="el-icon-date"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ activityStats.total_activities || 0 }}</div>
                  <div class="stat-label">总活动数</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      <div slot="footer">
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="handleJoinClub(currentClub)"
          :disabled="!currentClub || !( (currentClub.audit_status === 1) || (currentClub.status === 1) )"
        >
          加入社团
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// 导入所有需要的API函数
import { getClubs, createClub } from '@/api/club'
import { joinClub } from '@/api/member'
import { formatDate } from '@/utils/date'

// 导入新增的API函数
import { getClubDetail } from '@/api/club'

export default {
  name: 'ClubList',
  data() {
    return {
      clubList: [],
      loading: false,
      showCreateDialog: false,
      showDetailDialog: false,
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
      user: JSON.parse(sessionStorage.getItem('user') || '{}'),
      
      // 社团详情相关数据
      currentClub: null,
      clubStats: {},
      activityStats: {}
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
      if (!club) return
      const clubName = club.club_name || club.name || ''
      const clubId = club.club_id || club.id || club.clubId
      this.$confirm(`确定要加入 ${clubName} 吗？`, '提示', {
        type: 'info'
      }).then(() => {
        // 使用 joinClub 函数，兼容不同 id 字段名
        joinClub({
          club_id: clubId,
          user_id: this.user.id
        }).then(() => {
          this.$message.success('申请已提交，等待审核')
        }).catch(err => {
          console.error('加入社团失败:', err)
          this.$message.error('加入社团失败')
        })
      }).catch(() => {
        // 用户取消操作，无需提示
      })
    },
    viewClubDetail(club) {
      this.currentClub = club
      this.showDetailDialog = true
      this.loadClubDetail(club.club_id)
    },
    loadClubDetail(clubId) {
      // 重置数据
      this.clubStats = {}
      this.activityStats = {}

      // 使用新增的API函数获取社团详情
      getClubDetail(clubId).then(res => {
        if (res.status === 200 && res.data) {
          const data = res.data
          const info = data.club_info || {}
          // 保留从列表中已有字段，避免请求返回字段命名不一致导致短暂丢失
          const merged = Object.assign({}, this.currentClub || {}, info)
          // 兼容可能的字段名：founder_name / founderName / founder
          if (!merged.founder_name) {
            merged.founder_name = info.founder_name || info.founderName || (info.founder && (info.founder.name || info.founder.username)) || (this.currentClub && this.currentClub.founder_name) || ''
          }
          this.currentClub = merged
          this.clubStats = data.stats || {}
          this.activityStats = data.activity_stats || {}
        }
      }).catch(error => {
        console.error('加载社团详情失败:', error)
        this.$message.error('加载社团详情失败')
      })
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
  font-size: 16px;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
.club-info {
  margin-top: 10px;
  font-size: 15px;
  color: #999;
  display: flex;
  flex-direction: column;
}
.club-actions {
  margin-top: 10px;
  text-align: right;
}

/* 社团详情样式 */
.club-detail {
  max-height: 360px; /* 调低对话框内详情高度 */
  overflow: visible; /* 去掉滚动条，允许内容超出 */
  padding-right: 10px;
}

/* 描述内容样式 */
.description-content {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.5;
  min-height: 60px;
}

/* 统计信息样式 */
.stats-section {
  margin: 20px 0;
}
.stat-card {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  height: 40px;
}
.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 20px;
  color: white;
}
.member-icon {
  background-color: #409EFF;
}
.activity-icon {
  background-color: #67C23A;
}
.stat-info {
  flex: 1;
}
.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}
.stat-label {
  margin-top: 5px;
  font-size: 14px;
  color: #606266;
}
</style>
<!-- 以下规则使用深度选择器，确保在 Dialog 被插入到 body 时样式仍能生效 -->
<style scoped>
::v-deep .el-dialog__body .club-detail {
  padding-bottom: 60px !important; /* 确保有足够空间与 footer 分隔 */
}
::v-deep .el-dialog__body .stats-section {
  margin-bottom: 28px !important;
}
</style>