<template>
  <div class="activity-table">
    <el-table :data="activities" v-loading="loading">
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
              :disabled="scope.row.status !== 0"
            >
              编辑
            </el-button>
            <el-button 
              size="mini" 
              class="cancel-activity-btn"
              @click="cancelActivity(scope.row)"
              :disabled="scope.row.status !== 0"
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
      currentActivity: null
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
          user_id: JSON.parse(localStorage.getItem('user') || '{}').id
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
      this.$message.info(`编辑 ${activity.title}`)
      // 这里可以跳转到编辑页面或打开编辑对话框
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
/* 可以添加一些样式优化 */
.activity-table >>> .el-button {
  margin-bottom: 5px;
}
.activity-table >>> .el-button + .el-button {
  margin-left: 5px;
}

/* 取消活动按钮样式 - 模仿解散社团的红色样式 */
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

.activity-table >>> .cancel-activity-btn:focus {
  background-color: #f56c6c;
  border-color: #f56c6c;
  color: white;
}

.activity-table >>> .cancel-activity-btn.is-disabled {
  background-color: #fbc4c4;
  border-color: #fab6b6;
  color: #fff;
}

.activity-table >>> .cancel-activity-btn.is-disabled:hover {
  background-color: #fbc4c4;
  border-color: #fab6b6;
  color: #fff;
}

/* 活动详情样式 */
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