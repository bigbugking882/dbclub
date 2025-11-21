<template>
  <div class="club-manage">
    <div class="header">
      <h3>社团管理</h3>
      <el-button type="primary" @click="showCreateDialog = true">创建社团</el-button>
    </div>
    
    <el-table :data="clubList" v-loading="loading">
      <el-table-column prop="club_id" label="ID" width="80"></el-table-column>
      <el-table-column prop="club_name" label="社团名称"></el-table-column>
      <el-table-column prop="category" label="类别"></el-table-column>
      <el-table-column prop="founder_name" label="创始人"></el-table-column>
      <el-table-column prop="create_time" label="创建时间"></el-table-column>
      <el-table-column prop="status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
            {{ scope.row.status === 1 ? '正常' : '注销' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button size="mini" @click="editClub(scope.row)">编辑</el-button>
          <el-button 
            size="mini" 
            :type="scope.row.status === 1 ? 'danger' : 'success'"
            @click="toggleClubStatus(scope.row)"
          >
            {{ scope.row.status === 1 ? '注销' : '恢复' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑社团对话框 -->
    <el-dialog 
      :title="isEdit ? '编辑社团' : '创建社团'" 
      :visible.sync="showCreateDialog"
    >
      <el-form :model="clubForm" :rules="clubRules" ref="clubForm">
        <el-form-item label="社团名称" prop="club_name">
          <el-input v-model="clubForm.club_name"></el-input>
        </el-form-item>
        <el-form-item label="社团类别" prop="category">
          <el-select v-model="clubForm.category" placeholder="请选择">
            <el-option label="学术科技" value="学术科技"></el-option>
            <el-option label="文化体育" value="文化体育"></el-option>
            <el-option label="志愿公益" value="志愿公益"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="社团简介" prop="description">
          <el-input type="textarea" v-model="clubForm.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveClub">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getClubs, createClub, updateClub } from '@/api/club'

export default {
  name: 'ClubManage',
  data() {
    return {
      clubList: [],
      loading: false,
      showCreateDialog: false,
      isEdit: false,
      clubForm: {
        club_id: null,
        club_name: '',
        category: '',
        description: ''
      },
      clubRules: {
        club_name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
        category: [{ required: true, message: '请选择社团类别', trigger: 'change' }]
      }
    }
  },
  mounted() {
    this.loadClubs()
  },
  methods: {
    loadClubs() {
      this.loading = true
      getClubs().then(res => {
        this.clubList = res.data
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    editClub(club) {
      this.isEdit = true
      this.clubForm = { ...club }
      this.showCreateDialog = true
    },
    handleSaveClub() {
      this.$refs.clubForm.validate(valid => {
        if (valid) {
          const saveMethod = this.isEdit ? updateClub : createClub
          saveMethod(this.clubForm).then(() => {
            this.$message.success(this.isEdit ? '更新成功' : '创建成功')
            this.showCreateDialog = false
            this.loadClubs()
            this.resetForm()
          })
        }
      })
    },
    toggleClubStatus(club) {
      const newStatus = club.status === 1 ? 0 : 1
      const action = newStatus === 1 ? '恢复' : '注销'
      
      this.$confirm(`确定要${action}这个社团吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        updateClub({
          club_id: club.club_id,
          status: newStatus
        }).then(() => {
          this.$message.success(`${action}成功`)
          this.loadClubs()
        })
      })
    },
    resetForm() {
      this.clubForm = {
        club_id: null,
        club_name: '',
        category: '',
        description: ''
      }
      this.isEdit = false
      this.$refs.clubForm.resetFields()
    }
  }
}
</script>

<style scoped>
.club-manage .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>