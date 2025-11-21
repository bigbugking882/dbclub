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
          <el-button size="mini" @click="viewActivityDetail(scope.row)">详情</el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="cancelSignup(scope.row)"
            v-if="type === 'signed' && scope.row.status === 0"
          >
            取消报名
          </el-button>
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
      loading: false
    }
  },
  methods: {
    viewActivityDetail(activity) {
      this.$message.info(`查看 ${activity.title} 的详情`)
    },
    cancelSignup(activity) {
      this.$confirm(`确定要取消报名 ${activity.title} 吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        cancelActivitySignup({
          activity_id: activity.activity_id,
          user_id: JSON.parse(localStorage.getItem('user') || '{}').id
        }).then(() => {
          this.$message.success('取消报名成功')
          this.$emit('refresh')
        })
      })
    },
    editActivity(activity) {
      this.$message.info(`编辑 ${activity.title}`)
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