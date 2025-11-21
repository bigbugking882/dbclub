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
      <el-table-column prop="status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button 
            size="mini" 
            type="primary"
            @click="handleSignup(scope.row)"
            :disabled="scope.row.status !== 0"
            class="action-button"
          >
            报名
          </el-button>
          <el-button 
            size="mini" 
            @click="viewActivityDetail(scope.row)"
            class="action-button"
          >
            详情
          </el-button>
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
  </div>
</template>

<script>
// 导入所有需要的API函数
import { getActivities, createActivity, signupActivity } from '@/api/activity'
import { getClubs } from '@/api/club'
import { getMyClubs } from '@/api/member'
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
      filterClub: '',
      filterStatus: '',
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
  },
  methods: {
    loadActivities() {
      this.loading = true
      const params = {}
      if (this.filterClub) params.club_id = this.filterClub
      if (this.filterStatus) params.status = this.filterStatus
      
      // 使用 getActivities 函数
      getActivities(params).then(res => {
        this.activityList = res.data
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    loadClubs() {
      // 使用 getClubs 函数
      getClubs().then(res => {
        this.clubList = res.data
      })
    },
    loadMyClubs() {
      // 使用 getMyClubs 函数
      getMyClubs(this.user.id).then(res => {
        this.myClubs = res.data.filter(club => club.audit_status === 1)
      })
    },
    handleCreateActivity() {
      this.$refs.activityForm.validate(valid => {
        if (valid) {
          // 使用 createActivity 函数
          createActivity(this.activityForm).then((res) => {
            // 显示审核提示
            this.$message.success(res.message || '创建成功，等待管理员审核')
            this.showCreateDialog = false
            this.$refs.activityForm.resetFields()
            this.loadActivities()
          }).catch(error => {
            this.$message.error('创建失败: ' + (error.message || '未知错误'))
          })
        }
      })
    },
    handleSignup(activity) {
      this.$confirm(`确定要报名参加 ${activity.title} 吗？`, '提示', {
        type: 'info'
      }).then(() => {
        // 使用 signupActivity 函数
        signupActivity({
          activity_id: activity.activity_id,
          user_id: this.user.id
        }).then(() => {
          this.$message.success('报名成功')
          this.$bus.$emit('activity-signed')
        })
      })
    },
    viewActivityDetail(activity) {
      this.$message.info(`查看 ${activity.title} 的详情`)
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
}
.filter .el-select {
  width: 150px;
  margin-right: 10px;
}

/* 统一按钮样式 */
.activity-list >>> .action-button {
  min-width: 60px;
  height: 28px;
  line-height: 28px;
  padding: 0 12px;
  font-size: 12px;
}

/* 确保报名和详情按钮大小一致 */
.activity-list >>> .el-button--mini {
  min-width: 60px;
  height: 28px;
  line-height: 28px;
  padding: 0 12px;
}
</style>