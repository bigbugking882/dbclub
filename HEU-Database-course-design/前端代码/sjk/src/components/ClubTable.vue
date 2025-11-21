<template>
  <div class="club-table">
    <el-table :data="clubs" v-loading="loading">
      <el-table-column prop="club_name" label="社团名称"></el-table-column>
      <el-table-column prop="category" label="类别"></el-table-column>
      <el-table-column prop="description" label="简介">
        <template slot-scope="scope">
          {{ scope.row.description || '暂无简介' }}
        </template>
      </el-table-column>
      <el-table-column prop="role" label="我的角色">
        <template slot-scope="scope">
          <el-tag :type="getRoleType(scope.row.role)">
            {{ getRoleText(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="audit_status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.audit_status)">
            {{ getStatusText(scope.row.audit_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" v-if="showActions">
        <template slot-scope="scope">
          <el-button size="mini" @click="manageClub(scope.row)">管理</el-button>
          <el-button size="mini" type="danger" @click="deleteClub(scope.row)">解散</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'ClubTable',
  props: {
    clubs: {
      type: Array,
      default: () => []
    },
    showActions: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      loading: false
    }
  },
  methods: {
    manageClub(club) {
      this.$message.info(`管理社团: ${club.club_name}`)
    },
    deleteClub(club) {
      this.$confirm(`确定要解散 ${club.club_name} 吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        this.$message.success('解散成功')
        this.$emit('refresh')
      })
    },
    getRoleType(role) {
      const types = ['', 'danger', 'success']
      return types[role] || ''
    },
    getRoleText(role) {
      const texts = ['社员', '社长', '管理员']
      return texts[role] || '未知'
    },
    getStatusType(status) {
      const types = ['warning', 'success', 'danger']
      return types[status] || 'info'
    },
    getStatusText(status) {
      const texts = ['待审核', '已通过', '已拒绝']
      return texts[status] || '未知'
    }
  }
}
</script>