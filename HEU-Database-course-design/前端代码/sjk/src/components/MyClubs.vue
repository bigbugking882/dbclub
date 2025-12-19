<template>
  <div class="my-clubs">
    <div class="header">
      <h3>我的社团</h3>
    </div>

    <el-tabs v-model="activeTab" class="club-tabs">
      <el-tab-pane label="我创建的" name="created">
        <ClubTable :clubs="createdClubs" :show-actions="true" @refresh="loadMyClubs" />
      </el-tab-pane>
      <el-tab-pane label="我加入的" name="joined">
        <ClubTable :clubs="joinedClubs" :show-actions="false" />
      </el-tab-pane>
      <el-tab-pane label="待审核" name="pending">
        <ClubTable :clubs="pendingClubs" :show-actions="false" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { getMyClubs } from '@/api/member'
import ClubTable from './ClubTable'

export default {
  name: 'MyClubs',
  components: { ClubTable },
  data() {
    return {
      activeTab: 'created',
      allClubs: [],
      user: JSON.parse(sessionStorage.getItem('user') || '{}')
    }
  },
  computed: {
    createdClubs() {
      return this.allClubs.filter(club => club.role === 1)
    },
    joinedClubs() {
      return this.allClubs.filter(club => club.role === 0 && club.audit_status === 1)
    },
    pendingClubs() {
      return this.allClubs.filter(club => club.audit_status === 0)
    }
  },
  mounted() {
    this.loadMyClubs()
  },
  // 添加监听器，当标签页切换时刷新数据
  watch: {
    activeTab() {
      this.loadMyClubs()
    }
  },
  methods: {
    loadMyClubs() {
      getMyClubs(this.user.id).then(res => {
        this.allClubs = res.data
      })
    }
  }
}
</script>

<style scoped>
.my-clubs {
  padding: 0;
}

.my-clubs .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.club-tabs {
  min-height: 400px;
}

/* 美化标签页样式 */
.club-tabs >>> .el-tabs__header {
  margin-bottom: 20px;
}

.club-tabs >>> .el-tabs__nav-wrap::after {
  height: 1px;
}

.club-tabs >>> .el-tabs__item {
  font-size: 14px;
  font-weight: 500;
}

.club-tabs >>> .el-tabs__active-bar {
  background-color: #409eff;
}


/* 空状态样式 */
.my-clubs >>> .el-empty {
  padding: 40px 0;
}

.my-clubs >>> .el-empty__description {
  margin-top: 8px;
  color: #909399;
}
</style>