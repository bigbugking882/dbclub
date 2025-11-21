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
      <el-table-column label="操作" width="200" v-if="showActions">
        <template slot-scope="scope">
          <!-- 已报名活动：显示详情和取消报名 -->
          <el-button 
            size="mini" 
            @click="viewActivityDetail(scope.row)"
            v-if="type === 'signed'"
          >
            详情
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="cancelSignup(scope.row)"
            v-if="type === 'signed' && scope.row.status === 0"
          >
            取消报名
          </el-button>
          
          <!-- 我创建的活动：只显示编辑 -->
          <el-button 
            size="mini" 
            type="primary" 
            @click="editActivity(scope.row)"
            v-if="type === 'created'"
          >
            编辑
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 活动详情对话框（只在已报名活动中使用） -->
    <el-dialog 
      :title="currentActivity ? currentActivity.title : '活动详情'" 
      :visible.sync="showDetailDialog"
      width="600px"
      v-if="type === 'signed'"
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
          <el-descriptions-item label="报名状态">
            <el-tag :type="currentActivity.is_signed === 1 ? 'success' : 'info'">
              {{ currentActivity.is_signed === 1 ? '已报名' : '未报名' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="活动描述">
            <div class="activity-content">{{ currentActivity.content || '暂无详细描述' }}</div>
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
import { cancelActivitySignup } from '@/api/activity'
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
      user: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  methods: {
    viewActivityDetail(activity) {
      // 只在已报名活动中显示详情
      if (this.type === 'signed') {
        this.currentActivity = activity
        this.showDetailDialog = true
      }
    },

    cancelSignup(activity) {
      this.$confirm(`确定要取消报名 ${activity.title} 吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        cancelActivitySignup({
          activity_id: activity.activity_id,
          user_id: this.user.id
        }).then(() => {
          this.$message.success('取消报名成功')
          this.$emit('refresh')
        })
      })
    },

    editActivity(activity) {
      this.$message.info(`编辑 ${activity.title}`)
      // 这里可以跳转到编辑页面或打开编辑对话框
      // 例如：this.$router.push(`/edit-activity/${activity.activity_id}`)
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
.activity-detail {
  padding: 10px 0;
}

.activity-content {
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}
</style>