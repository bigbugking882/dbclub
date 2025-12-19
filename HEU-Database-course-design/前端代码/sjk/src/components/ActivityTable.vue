<template>
  <div class="activity-table">
    <el-table :data="activities" v-loading="loading">
      <el-table-column label="序号" width="80">
        <template slot-scope="scope">
          {{ scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column prop="title" label="活动名称"></el-table-column>
      <el-table-column prop="club_name" label="主办社团"></el-table-column>
      <el-table-column prop="location" label="活动地点"></el-table-column>
      <el-table-column prop="start_time" label="开始时间">
        <template slot-scope="scope">
          {{ formatDate(scope.row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="end_time" label="结束时间">
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
      <el-table-column prop="is_signed" label="报名状态" v-if="type === 'signed'">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_signed === 1 ? 'success' : 'info'">
            {{ scope.row.is_signed === 1 ? '已报名' : '未报名' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" v-if="showActions">
        <template slot-scope="scope">
          <!-- 已报名活动的操作 -->
          <template v-if="type === 'signed'">
            <el-button 
              size="mini" 
              @click="viewActivityDetail(scope.row)"
            >
              详情
            </el-button>
            <el-button 
              size="mini" 
              type="danger" 
              @click="cancelSignup(scope.row)"
              :disabled="scope.row.status !== 0"
            >
              取消报名
            </el-button>
          </template>
          
          <!-- 我创建的活动操作 -->
          <template v-if="type === 'created'">
            <el-button 
              size="mini" 
              type="primary" 
              @click="editActivity(scope.row)"
              :disabled="![0, 3].includes(scope.row.status)"
            >
              编辑
            </el-button>
            <el-button 
              size="mini" 
              class="cancel-activity-btn"
              @click="cancelActivity(scope.row)"
              :disabled="![0, 3].includes(scope.row.status)"
            >
              取消活动
            </el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <!-- 活动详情对话框 -->
    <el-dialog 
      :title="currentActivity ? currentActivity.title : '活动详情'" 
      :visible.sync="showDetailDialog"
      width="600px"
    >
      <div v-if="currentActivity" class="activity-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="活动名称">{{ currentActivity.title }}</el-descriptions-item>
          <el-descriptions-item label="主办社团">{{ currentActivity.club_name }}</el-descriptions-item>
          <el-descriptions-item label="活动地点">{{ currentActivity.location }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(currentActivity.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDate(currentActivity.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="活动状态">
            <el-tag :type="getStatusType(currentActivity.status)">
              {{ getStatusText(currentActivity.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="报名状态" v-if="type === 'signed'">
            <el-tag :type="currentActivity.is_signed === 1 ? 'success' : 'info'">
              {{ currentActivity.is_signed === 1 ? '已报名' : '未报名' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="活动描述">
            <div class="activity-content">
              {{ currentActivity.content || '暂无详细描述' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div slot="footer">
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </div>
    </el-dialog>

    <!-- 编辑活动对话框 -->
    <el-dialog 
      :title="isEdit ? '编辑活动' : '创建活动'" 
      :visible.sync="showActivityForm"
      width="600px"
    >
      <el-form :model="activityForm" :rules="activityRules" ref="activityForm" label-width="100px">
        <el-form-item label="活动名称" prop="title">
          <el-input v-model="activityForm.title"></el-input>
        </el-form-item>
        <el-form-item label="活动地点" prop="location">
          <el-input v-model="activityForm.location"></el-input>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="activityForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            value-format="yyyy-MM-dd HH:mm:ss"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="activityForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            value-format="yyyy-MM-dd HH:mm:ss"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="活动描述" prop="content">
          <el-input type="textarea" v-model="activityForm.content" :rows="4"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showActivityForm = false">取消</el-button>
        <el-button type="primary" @click="saveActivity">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { cancelActivitySignup, updateActivity } from '@/api/activity'
import { formatDate } from '@/utils/date'

export default {
  name: 'ActivityTable',
  props: {
    activities: {
      type: Array,
      default: () => []
    },
    showActions: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'signed'
    }
  },
  data() {
    return {
      loading: false,
      showDetailDialog: false,
      currentActivity: null,
      // 编辑活动相关
      showActivityForm: false,
      isEdit: false,
      activityForm: {
        activity_id: null,
        title: '',
        club_id: null,
        location: '',
        start_time: '',
        end_time: '',
        content: ''
      },
      activityRules: {
        title: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
        location: [{ required: true, message: '请输入活动地点', trigger: 'blur' }],
        start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
        end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
      }
    }
  },
  methods: {
    viewActivityDetail(activity) {
      this.currentActivity = activity
      this.showDetailDialog = true
    },
    
    cancelSignup(activity) {
      this.$confirm(`确定要取消报名 ${activity.title} 吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        this.loading = true
        cancelActivitySignup({
          activity_id: activity.activity_id,
          user_id: JSON.parse(sessionStorage.getItem('user') || '{}').id
        }).then(() => {
          this.loading = false
          this.$message.success('取消报名成功')
          this.$emit('refresh')
        }).catch(error => {
          this.loading = false
          this.$message.error('取消报名失败: ' + (error.message || '未知错误'))
        })
      })
    },
    
    editActivity(activity) {
      this.isEdit = true
      this.activityForm = { ...activity }
      this.activityForm.start_time = new Date(activity.start_time)
      this.activityForm.end_time = new Date(activity.end_time)
      this.showActivityForm = true
    },
    
    saveActivity() {
      this.$refs.activityForm.validate(valid => {
        if (valid) {
          updateActivity(this.activityForm).then(() => {
            this.$message.success('活动更新成功')
            this.showActivityForm = false
            this.$emit('refresh')
          }).catch(error => {
            this.$message.error('更新失败: ' + (error.message || '未知错误'))
          })
        }
      })
    },
    
    cancelActivity(activity) {
      this.$confirm(
        `确定要取消未开始的活动 "${activity.title}" 吗？此操作不可恢复！`,
        '取消活动',
        {
          type: 'warning',
          confirmButtonText: '确定取消',
          cancelButtonText: '再想想'
        }
      ).then(() => {
        this.loading = true
        // 更新活动状态为已结束（状态2）来表示活动已取消
        updateActivity({
          activity_id: activity.activity_id,
          status: 2 // 设置为已结束状态
        }).then(() => {
          this.loading = false
          this.$message.success('活动取消成功')
          this.$emit('refresh')
        }).catch(error => {
          this.loading = false
          this.$message.error('取消活动失败: ' + (error.message || '未知错误'))
        })
      }).catch(() => {
        this.$message.info('已取消操作')
      })
    },
    
    getStatusType(status) {
      const types = ['info', 'primary', 'success', 'warning', 'danger']
      return types[status] || 'warning'
    },
    
    getStatusText(status) {
      const texts = ['未开始', '进行中', '已结束', '待审核', '未通过']
      return texts[status] || '待审核'
    },
    
    formatDate
  }
}
</script>

<style scoped>
/* 原有样式保持不变 */
.activity-table >>> .el-button {
  margin-bottom: 5px;
}
.activity-table >>> .el-button + .el-button {
  margin-left: 5px;
}

/* 取消活动按钮样式 */
.activity-table >>> .cancel-activity-btn {
  background-color: #f56c6c;
  border-color: #f56c6c;
  color: white;
}

.activity-table >>> .cancel-activity-btn:hover {
  background-color: #f78989;
  border-color: #f78989;
  color: white;
}

.activity-detail {
  padding: 10px 0;
}

.activity-content {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.5;
}
</style>