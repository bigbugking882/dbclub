<template>
  <div class="my-activities">
    <div class="header">
      <h3>我的活动</h3>
    </div>

    <el-tabs v-model="activeTab" class="activity-tabs">
      <el-tab-pane label="已报名活动" name="signed">
        <ActivityTable 
          :activities="signedActivities" 
          :show-actions="true"
          type="signed"
          @refresh="loadMyActivities"
        />
      </el-tab-pane>
      <el-tab-pane label="我创建的活动" name="created">
        <ActivityTable 
          :activities="createdActivities" 
          :show-actions="true"
          type="created"
          @refresh="loadMyActivities"
        />
      </el-tab-pane>
      <el-tab-pane label="历史活动" name="history">
        <ActivityTable 
          :activities="historyActivities" 
          :show-actions="false"
          type="history"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { getMyActivities } from '@/api/activity'
import ActivityTable from './ActivityTable'

export default {
  name: 'MyActivities',
  components: { ActivityTable },
  data() {
    return {
      activeTab: 'signed',
      signedActivities: [],    // 已报名活动
      createdActivities: [],   // 我创建的活动
      historyActivities: [],   // 历史活动
      user: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  mounted() {
    this.loadMyActivities()
    this.$bus.$on('activity-signed', this.loadMyActivities)
  },
  beforeDestroy() {
    // 组件销毁时移除监听
    this.$bus.$off('activity-signed', this.loadMyActivities)
  },
  methods: {
    loadMyActivities() {
      getMyActivities(this.user.id).then(res => {
        const allActivities = res.data
        // 已报名活动（包括待开始和进行中）
        this.signedActivities = allActivities.filter(activity => 
          activity.is_signed === 1 && activity.status !== 2
        )
        // 我创建的活动
        this.createdActivities = allActivities.filter(activity => 
          activity.creator_id === this.user.id
        )
        // 历史活动（已结束或已取消报名）
        this.historyActivities = allActivities.filter(activity => 
          activity.status === 2 || activity.is_signed === 0
        )
      })
    }
  }
}
</script>

<style scoped>
.my-activities {
  padding: 0;
}

.my-activities .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-tabs {
  min-height: 400px;
}

/* 美化标签页样式 */
.activity-tabs >>> .el-tabs__header {
  margin-bottom: 20px;
}

.activity-tabs >>> .el-tabs__nav-wrap::after {
  height: 1px;
}

.activity-tabs >>> .el-tabs__item {
  font-size: 14px;
  font-weight: 500;
}

.activity-tabs >>> .el-tabs__active-bar {
  background-color: #409eff;
}

/* 空状态样式 */
.my-activities >>> .el-empty {
  padding: 40px 0;
}

.my-activities >>> .el-empty__description {
  margin-top: 8px;
  color: #909399;
}
</style>