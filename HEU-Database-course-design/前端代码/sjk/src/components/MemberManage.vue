<template>
  <div class="member-manage">
    <div class="header">
      <h3>成员管理</h3>
      <div class="filters">
        <el-select v-model="filterClub" placeholder="选择社团" @change="loadMembers">
          <el-option label="全部社团" value=""></el-option>
          <el-option 
            v-for="club in clubList" 
            :key="club.club_id" 
            :label="club.club_name" 
            :value="club.club_id"
          ></el-option>
        </el-select>
        <el-select v-model="filterStatus" placeholder="审核状态" @change="loadMembers">
          <el-option label="全部状态" value=""></el-option>
          <el-option label="待审核" value="0"></el-option>
          <el-option label="已通过" value="1"></el-option>
          <el-option label="已拒绝" value="2"></el-option>
        </el-select>
      </div>
    </div>
    
    <el-table :data="memberList" v-loading="loading">
      <el-table-column prop="member_id" label="ID" width="80"></el-table-column>
      <el-table-column prop="username" label="用户名"></el-table-column>
      <el-table-column prop="telephone" label="手机号"></el-table-column>
      <el-table-column prop="club_name" label="社团"></el-table-column>
      <el-table-column prop="role" label="角色">
        <template slot-scope="scope">
          <el-tag :type="scope.row.role === 1 ? 'danger' : 'primary'">
            {{ getRoleText(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="join_time" label="加入时间"></el-table-column>
      <el-table-column prop="audit_status" label="审核状态">
        <template slot-scope="scope">
          <el-tag :type="getAuditType(scope.row.audit_status)">
            {{ getAuditText(scope.row.audit_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button 
            v-if="scope.row.audit_status === 0"
            size="mini" 
            type="success"
            @click="handleAudit(scope.row, 1)"
          >
            通过
          </el-button>
          <el-button 
            v-if="scope.row.audit_status === 0"
            size="mini" 
            type="danger"
            @click="handleAudit(scope.row, 2)"
          >
            拒绝
          </el-button>
          <el-button 
            v-if="scope.row.audit_status === 1"
            size="mini" 
            type="danger"
            @click="removeMember(scope.row)"
          >
            移除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { getClubMembers, auditMember, removeMember } from '@/api/member'
import { getClubs } from '@/api/club'

export default {
  name: 'MemberManage',
  data() {
    return {
      memberList: [],
      clubList: [],
      loading: false,
      filterClub: '',
      filterStatus: ''
    }
  },
  mounted() {
    this.loadMembers()
    this.loadClubs()
  },
  methods: {
    loadMembers() {
      this.loading = true
      const params = {}
      if (this.filterClub) params.club_id = this.filterClub
      if (this.filterStatus) params.audit_status = this.filterStatus
      
      getClubMembers(params).then(res => {
        this.memberList = res.data
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    loadClubs() {
      getClubs().then(res => {
        this.clubList = res.data
      })
    },
    handleAudit(member, status) {
      const action = status === 1 ? '通过' : '拒绝'
      this.$confirm(`确定要${action}这个成员的申请吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        auditMember(member.member_id, status).then(() => {
          this.$message.success(`${action}成功`)
          this.loadMembers()
        })
      })
    },
    removeMember(member) {
      this.$confirm('确定要移除这个成员吗？', '提示', {
        type: 'warning'
      }).then(() => {
        removeMember(member.member_id).then(() => {
          this.$message.success('移除成功')
          this.loadMembers()
        })
      })
    },
    getRoleText(role) {
      const texts = ['社员', '社长', '管理员']
      return texts[role] || '未知'
    },
    getAuditType(status) {
      const types = ['warning', 'success', 'danger']
      return types[status] || 'info'
    },
    getAuditText(status) {
      const texts = ['待审核', '已通过', '已拒绝']
      return texts[status] || '未知'
    }
  }
}
</script>

<style scoped>
.member-manage .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.filters .el-select {
  width: 150px;
  margin-right: 10px;
}
</style>