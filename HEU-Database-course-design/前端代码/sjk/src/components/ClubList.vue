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
      <el-form :model="clubForm" :rules="clubRules" ref="clubForm" label-width="80px">
        <el-form-item label="社团名称" prop="club_name">
          <el-input v-model="clubForm.club_name"></el-input>
        </el-form-item>
        <el-form-item label="社团类别" prop="category">
          <el-select v-model="clubForm.category" placeholder="请选择" style="width: 100%">
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
      :title="currentClub ? currentClub.club_name : '社团详情'" 
      :visible.sync="showClubDetailDialog"
      width="700px"
    >
      <div v-if="currentClub" class="club-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="社团名称">{{ currentClub.club_name }}</el-descriptions-item>
          <el-descriptions-item label="社团类别">{{ currentClub.category }}</el-descriptions-item>
          <el-descriptions-item label="创始人">{{ currentClub.founder_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentClub.create_time) }}</el-descriptions-item>
          <el-descriptions-item label="社团简介" :span="2">
            <div class="club-description">{{ currentClub.description || '暂无简介' }}</div>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 社团成员预览 -->
        <div class="members-preview" style="margin-top: 20px;">
          <h4>社团成员</h4>
          <el-table :data="clubMembersPreview" size="small" v-loading="membersLoading">
            <el-table-column prop="username" label="成员姓名"></el-table-column>
            <el-table-column prop="role" label="角色">
              <template slot-scope="scope">
                <el-tag :type="scope.row.role === 1 ? 'danger' : 'primary'" size="small">
                  {{ scope.row.role === 1 ? '社长' : '社员' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="join_time" label="加入时间"></el-table-column>
          </el-table>
          <div v-if="!membersLoading && clubMembersPreview.length === 0" class="empty-state">
            暂无成员数据
          </div>
        </div>
        
        <!-- 社团活动预览 -->
        <div class="activities-preview" style="margin-top: 20px;">
          <h4>近期活动</h4>
          <el-table :data="clubActivitiesPreview" size="small" v-loading="activitiesLoading">
            <el-table-column prop="title" label="活动名称"></el-table-column>
            <el-table-column prop="location" label="活动地点"></el-table-column>
            <el-table-column prop="start_time" label="开始时间">
              <template slot-scope="scope">
                {{ formatDate(scope.row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template slot-scope="scope">
                <el-tag :type="getActivityStatusType(scope.row.status)" size="small">
                  {{ getActivityStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="!activitiesLoading && clubActivitiesPreview.length === 0" class="empty-state">
            暂无活动数据
          </div>
        </div>
      </div>
      <div slot="footer">
        <el-button @click="showClubDetailDialog = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="handleJoinClub(currentClub)"
          v-if="currentClub && !isClubMember(currentClub)"
        >
          申请加入
        </el-button>
        <el-button 
          type="success" 
          disabled
          v-if="currentClub && isClubMember(currentClub)"
        >
          已加入
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { formatDate } from '@/utils/date'

export default {
  name: 'ClubList',
  data() {
    return {
      clubList: [],
      loading: false,
      showCreateDialog: false,
      showClubDetailDialog: false,
      filterCategory: '',
      currentClub: null,
      clubMembersPreview: [],
      clubActivitiesPreview: [],
      membersLoading: false,
      activitiesLoading: false,
      clubForm: {
        club_name: '',
        category: '',
        description: ''
      },
      clubRules: {
        club_name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
        category: [{ required: true, message: '请选择社团类别', trigger: 'change' }]
      },
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      myClubs: []
    }
  },
  mounted() {
    this.loadClubs()
    this.loadMyClubs()
  },
  methods: {
    async loadClubs() {
      this.loading = true
      try {
        const response = await fetch('http://127.0.0.1:5000/api/clubs')
        const result = await response.json()
        
        if (result.status === 200) {
          let clubs = result.data || []
          if (this.filterCategory) {
            clubs = clubs.filter(club => club.category === this.filterCategory)
          }
          this.clubList = clubs
        } else {
          throw new Error(result.message)
        }
      } catch (error) {
        console.error('加载社团列表失败:', error)
        this.$message.error('加载社团列表失败')
      } finally {
        this.loading = false
      }
    },

    async loadMyClubs() {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/user/${this.user.id}/clubs`)
        const result = await response.json()
        
        if (result.status === 200) {
          this.myClubs = result.data || []
        }
      } catch (error) {
        console.error('加载我的社团失败:', error)
      }
    },

    async handleCreateClub() {
      this.$refs.clubForm.validate(async (valid) => {
        if (valid) {
          try {
            const response = await fetch('http://127.0.0.1:5000/api/club/create', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                ...this.clubForm,
                founder_id: this.user.id
              })
            })
            const result = await response.json()
            
            if (result.status === 200) {
              this.$message.success('创建成功')
              this.showCreateDialog = false
              this.$refs.clubForm.resetFields()
              this.loadClubs()
              this.loadMyClubs()
            } else {
              throw new Error(result.message)
            }
          } catch (error) {
            this.$message.error('创建失败：' + (error.message || '请稍后重试'))
          }
        }
      })
    },

    async handleJoinClub(club) {
      this.$confirm(`确定要申请加入 ${club.club_name} 吗？`, '提示', {
        type: 'info'
      }).then(async () => {
        try {
          const response = await fetch('http://127.0.0.1:5000/api/club/join', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              club_id: club.club_id,
              user_id: this.user.id
            })
          })
          const result = await response.json()
          
          if (result.status === 200) {
            this.$message.success('申请已提交，等待审核')
            this.loadMyClubs()
          } else {
            throw new Error(result.message)
          }
        } catch (error) {
          this.$message.error('申请失败：' + (error.message || '请稍后重试'))
        }
      })
    },

    async viewClubDetail(club) {
      this.currentClub = club
      this.showClubDetailDialog = true
      this.loadClubMembersPreview(club.club_id)
      this.loadClubActivitiesPreview(club.club_id)
    },

    async loadClubMembersPreview(clubId) {
      this.membersLoading = true
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/club/members?club_id=${clubId}&audit_status=1`)
        const result = await response.json()
        
        if (result.status === 200) {
          this.clubMembersPreview = result.data.slice(0, 5) || []
        }
      } catch (error) {
        console.error('加载成员预览失败:', error)
        this.clubMembersPreview = []
      } finally {
        this.membersLoading = false
      }
    },

    async loadClubActivitiesPreview(clubId) {
      this.activitiesLoading = true
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/activities?club_id=${clubId}`)
        const result = await response.json()
        
        if (result.status === 200) {
          this.clubActivitiesPreview = result.data.slice(0, 5) || []
        }
      } catch (error) {
        console.error('加载活动预览失败:', error)
        this.clubActivitiesPreview = []
      } finally {
        this.activitiesLoading = false
      }
    },

    isClubMember(club) {
      return this.myClubs.some(myClub => 
        myClub.club_id === club.club_id && myClub.audit_status === 1
      )
    },

    getCategoryType(category) {
      const types = {
        '学术科技': 'primary',
        '文化体育': 'success', 
        '志愿公益': 'warning'
      }
      return types[category] || 'info'
    },

    getActivityStatusType(status) {
      const types = ['info', 'primary', 'success']
      return types[status] || 'info'
    },

    getActivityStatusText(status) {
      const texts = ['未开始', '进行中', '已结束']
      return texts[status] || '未知'
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
  margin-bottom: 20px;
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

.club-detail {
  padding: 10px 0;
}

.club-description {
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.members-preview h4,
.activities-preview h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: #909399;
  font-size: 14px;
}
</style>