<template>
  <div class="activity-list">
    <div class="header">
      <h3>活动中心</h3>
      <el-button 
        type="primary" 
        @click="showCreateDialog = true"
        v-if="hasCreatePermission"
      >
        创建活动
      </el-button>
    </div>

    <div class="filter">
      <el-select v-model="filterClub" placeholder="筛选社团" @change="loadActivities">
        <el-option label="全部社团" value=""></el-option>
        <el-option 
          v-for="club in clubList" 
          :key="club.club_id" 
          :label="club.club_name" 
          :value="club.club_id"
        ></el-option>
      </el-select>
      <el-select v-model="filterStatus" placeholder="活动状态" @change="loadActivities">
        <el-option label="全部状态" value=""></el-option>
        <el-option label="未开始" value="0"></el-option>
        <el-option label="进行中" value="1"></el-option>
        <el-option label="已结束" value="2"></el-option>
      </el-select>
    </div>

    <el-table :data="activityList" v-loading="loading">
      <el-table-column prop="title" label="活动名称"></el-table-column>
      <el-table-column prop="club_name" label="主办社团"></el-table-column>
      <el-table-column prop="location" label="活动地点"></el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="180">
        <template slot-scope="scope">
          {{ formatDate(scope.row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="end_time" label="结束时间" width="180">
        <template slot-scope="scope">
          {{ formatDate(scope.row.end_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button 
            size="mini" 
            type="primary"
            @click="handleSignup(scope.row)"
            :disabled="scope.row.status !== 0 || isActivitySigned(scope.row)"
          >
            {{ isActivitySigned(scope.row) ? '已报名' : '报名' }}
          </el-button>
          <el-button size="mini" @click="viewActivityDetail(scope.row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建活动对话框 -->
    <el-dialog 
      title="创建活动" 
      :visible.sync="showCreateDialog" 
      width="600px"
      center
    >
      <el-form :model="activityForm" :rules="activityRules" ref="activityForm" label-width="100px">
        <el-form-item label="活动名称" prop="title">
          <el-input 
            v-model="activityForm.title" 
            placeholder="请输入活动名称，如：Python编程讲座"
            maxlength="50"
            show-word-limit
          ></el-input>
        </el-form-item>
        <el-form-item label="所属社团" prop="club_id">
          <el-select 
            v-model="activityForm.club_id" 
            placeholder="请选择社团" 
            style="width: 100%"
            :disabled="myClubs.length === 0"
          >
            <el-option 
              v-for="club in myClubs" 
              :key="club.club_id" 
              :label="club.club_name" 
              :value="club.club_id"
            ></el-option>
          </el-select>
          <div v-if="myClubs.length === 0" style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
            您还没有加入任何社团，请先加入社团再创建活动
          </div>
        </el-form-item>
        <el-form-item label="活动地点" prop="location">
          <el-input 
            v-model="activityForm.location" 
            placeholder="请输入活动地点，如：教学楼201教室"
          ></el-input>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="activityForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            value-format="yyyy-MM-dd HH:mm:ss"
            style="width: 100%"
            :picker-options="{
              disabledDate(time) {
                return time.getTime() < Date.now() - 8.64e7;
              }
            }"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="activityForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            value-format="yyyy-MM-dd HH:mm:ss"
            style="width: 100%"
            :picker-options="{
              disabledDate(time) {
                return time.getTime() < Date.now() - 8.64e7;
              }
            }"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="活动描述" prop="content">
          <el-input 
            type="textarea" 
            v-model="activityForm.content" 
            placeholder="请详细描述活动内容、流程、注意事项等"
            :rows="4"
            maxlength="500"
            show-word-limit
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showCreateDialog = false" size="medium">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleCreateActivity" 
          size="medium"
          :disabled="myClubs.length === 0"
        >
          创建活动
        </el-button>
      </div>
    </el-dialog>

    <!-- 活动详情对话框 -->
    <el-dialog 
      :title="currentActivity ? currentActivity.title : '活动详情'" 
      :visible.sync="showActivityDetailDialog"
      width="700px"
    >
      <div v-if="currentActivity" class="activity-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="活动名称">{{ currentActivity.title }}</el-descriptions-item>
          <el-descriptions-item label="主办社团">{{ currentActivity.club_name }}</el-descriptions-item>
          <el-descriptions-item label="活动地点">{{ currentActivity.location }}</el-descriptions-item>
          <el-descriptions-item label="活动状态">
            <el-tag :type="getStatusType(currentActivity.status)">
              {{ getStatusText(currentActivity.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(currentActivity.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDate(currentActivity.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="活动描述" :span="2">
            <div class="activity-content">{{ currentActivity.content || '暂无详细描述' }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div slot="footer">
        <el-button @click="showActivityDetailDialog = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="handleSignup(currentActivity)"
          v-if="currentActivity && currentActivity.status === 0 && !isActivitySigned(currentActivity)"
        >
          立即报名
        </el-button>
        <el-button 
          type="info" 
          disabled
          v-if="currentActivity && currentActivity.status !== 0"
        >
          {{ currentActivity.status === 1 ? '活动进行中' : '活动已结束' }}
        </el-button>
        <el-button 
          type="success" 
          disabled
          v-if="currentActivity && isActivitySigned(currentActivity)"
        >
          已报名
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { formatDate } from '@/utils/date'

export default {
  name: 'ActivityList',
  data() {
    return {
      activityList: [],
      clubList: [],
      myClubs: [],
      loading: false,
      showCreateDialog: false,
      showActivityDetailDialog: false,
      filterClub: '',
      filterStatus: '',
      currentActivity: null,
      signedActivities: [],
      activityForm: {
        title: '',
        club_id: null,
        location: '',
        start_time: '',
        end_time: '',
        content: ''
      },
      activityRules: {
        title: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
        club_id: [{ required: true, message: '请选择社团', trigger: 'change' }],
        location: [{ required: true, message: '请输入活动地点', trigger: 'blur' }],
        start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
        end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
      },
      user: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  computed: {
    hasCreatePermission() {
      return this.myClubs.length > 0
    }
  },
  mounted() {
    this.loadActivities()
    this.loadClubs()
    this.loadMyClubs()
    this.loadSignedActivities()
  },
  methods: {
    async loadActivities() {
      this.loading = true
      try {
        const params = new URLSearchParams()
        if (this.filterClub) params.append('club_id', this.filterClub)
        if (this.filterStatus) params.append('status', this.filterStatus)
        
        const response = await fetch(`http://127.0.0.1:5000/api/activities?${params}`)
        const result = await response.json()
        
        if (result.status === 200) {
          this.activityList = result.data || []
        } else {
          throw new Error(result.message)
        }
      } catch (error) {
        console.error('加载活动列表失败:', error)
        this.$message.error('加载活动列表失败')
      } finally {
        this.loading = false
      }
    },

    async loadClubs() {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/clubs')
        const result = await response.json()
        
        if (result.status === 200) {
          this.clubList = result.data || []
        }
      } catch (error) {
        console.error('加载社团列表失败:', error)
      }
    },

    async loadMyClubs() {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/user/${this.user.id}/clubs`)
        const result = await response.json()
        
        if (result.status === 200) {
          this.myClubs = result.data.filter(club => club.audit_status === 1) || []
        }
      } catch (error) {
        console.error('加载我的社团失败:', error)
      }
    },

    async loadSignedActivities() {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/user/${this.user.id}/activities`)
        const result = await response.json()
        
        if (result.status === 200) {
          this.signedActivities = result.data.filter(activity => activity.is_signed === 1) || []
        }
      } catch (error) {
        console.error('加载已报名活动失败:', error)
      }
    },

    async handleCreateActivity() {
      this.$refs.activityForm.validate(async (valid) => {
        if (valid) {
          try {
            const response = await fetch('http://127.0.0.1:5000/api/activity/create', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(this.activityForm)
            })
            const result = await response.json()
            
            if (result.status === 200) {
              this.$message.success('创建成功')
              this.showCreateDialog = false
              this.$refs.activityForm.resetFields()
              this.loadActivities()
            } else {
              throw new Error(result.message)
            }
          } catch (error) {
            this.$message.error('创建失败：' + (error.message || '请稍后重试'))
          }
        }
      })
    },

    async handleSignup(activity) {
      this.$confirm(`确定要报名参加 ${activity.title} 吗？`, '提示', {
        type: 'info'
      }).then(async () => {
        try {
          const response = await fetch('http://127.0.0.1:5000/api/activity/signup', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              activity_id: activity.activity_id,
              user_id: this.user.id
            })
          })
          const result = await response.json()
          
          if (result.status === 200) {
            this.$message.success('报名成功')
            this.loadSignedActivities()
          } else {
            throw new Error(result.message)
          }
        } catch (error) {
          this.$message.error('报名失败：' + (error.message || '请稍后重试'))
        }
      })
    },

    viewActivityDetail(activity) {
      this.currentActivity = activity
      this.showActivityDetailDialog = true
    },

    isActivitySigned(activity) {
      return this.signedActivities.some(signed => signed.activity_id === activity.activity_id)
    },

    getStatusType(status) {
      const types = ['info', 'primary', 'success']
      return types[status] || 'info'
    },

    getStatusText(status) {
      const texts = ['未开始', '进行中', '已结束']
      return texts[status] || '未知'
    },

    formatDate
  }
}
</script>

<style scoped>
.activity-list .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter .el-select {
  width: 150px;
  margin-right: 10px;
  margin-bottom: 20px;
}

.activity-detail {
  padding: 10px 0;
}

.activity-content {
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.dialog-footer {
  text-align: center;
}
</style>