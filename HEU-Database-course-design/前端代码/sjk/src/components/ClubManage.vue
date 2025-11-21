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
          <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
            {{ scope.row.status === 1 ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template slot-scope="scope">
          <el-button size="mini" @click="editClub(scope.row)">编辑</el-button>
          <el-button 
            size="mini" 
            class="status-toggle-btn"
            @click="toggleClubStatus(scope.row)"
          >
            {{ scope.row.status === 1 ? '停用' : '启用' }}
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="deleteClub(scope.row)"
            v-if="scope.row.status === 1"
          >
            解散
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑社团对话框 -->
    <el-dialog 
      :title="isEdit ? '编辑社团' : '创建社团'" 
      :visible.sync="showCreateDialog"
      width="500px"
    >
      <el-form :model="clubForm" :rules="clubRules" ref="clubForm" label-width="80px">
        <el-form-item label="社团名称" prop="club_name">
          <el-input v-model="clubForm.club_name" placeholder="请输入社团名称"></el-input>
        </el-form-item>
        <el-form-item label="社团类别" prop="category">
          <el-select v-model="clubForm.category" placeholder="请选择" style="width: 100%">
            <el-option label="学术科技" value="学术科技"></el-option>
            <el-option label="文化体育" value="文化体育"></el-option>
            <el-option label="志愿公益" value="志愿公益"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="社团简介" prop="description">
          <el-input 
            type="textarea" 
            v-model="clubForm.description" 
            placeholder="请输入社团简介"
            :rows="4"
          ></el-input>
        </el-form-item>
        <!-- 在管理端创建社团时选择创始人 -->
        <el-form-item label="创始人" prop="founder_id" v-if="!isEdit">
          <el-select v-model="clubForm.founder_id" placeholder="请选择创始人" style="width: 100%">
            <el-option 
              v-for="user in userList" 
              :key="user.id" 
              :label="user.username" 
              :value="user.id"
            ></el-option>
          </el-select>
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
import { getClubs, createClub, updateClub, deleteClub } from '@/api/club'
import { getUsers } from '@/api/user'

export default {
  name: 'ClubManage',
  data() {
    return {
      clubList: [],
      userList: [], // 用户列表用于选择创始人
      loading: false,
      showCreateDialog: false,
      isEdit: false,
      clubForm: {
        club_id: null,
        club_name: '',
        category: '',
        description: '',
        founder_id: null // 添加创始人ID字段
      },
      clubRules: {
        club_name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
        category: [{ required: true, message: '请选择社团类别', trigger: 'change' }],
        founder_id: [{ required: true, message: '请选择创始人', trigger: 'change' }] // 添加创始人验证规则
      }
    }
  },
  mounted() {
    this.loadClubs()
    this.loadUsers() // 加载用户列表
  },
  methods: {
    loadClubs() {
      this.loading = true
      getClubs().then(res => {
        // 显示所有社团，包括停用的
        console.log('加载的社团数据:', res.data) // 调试用，查看返回的数据
        this.clubList = res.data || []
        this.loading = false
      }).catch((error) => {
        this.loading = false
        console.error('加载社团列表失败:', error)
        this.$message.error('加载社团列表失败')
      })
    },
    loadUsers() {
      getUsers().then(res => {
        this.userList = res.data
      })
    },
    editClub(club) {
      this.isEdit = true
      this.clubForm = { 
        club_id: club.club_id,
        club_name: club.club_name,
        category: club.category,
        description: club.description || '',
        founder_id: club.founder_id // 编辑时也设置创始人ID
      }
      this.showCreateDialog = true
    },
    handleSaveClub() {
      this.$refs.clubForm.validate(valid => {
        if (valid) {
          const saveMethod = this.isEdit ? updateClub : createClub
          
          // 准备提交的数据
          const submitData = { ...this.clubForm }
          
          // 如果是编辑，可能不需要 founder_id，根据后端API调整
          if (this.isEdit) {
            // 编辑时可能不需要更新创始人，根据实际需求调整
            delete submitData.founder_id
          }
          
          saveMethod(submitData).then(() => {
            this.$message.success(this.isEdit ? '更新成功' : '创建成功')
            this.showCreateDialog = false
            this.loadClubs()
            this.resetForm()
          }).catch(error => {
            this.$message.error('操作失败：' + (error.message || '未知错误'))
          })
        }
      })
    },
    toggleClubStatus(club) {
      const newStatus = club.status === 1 ? 0 : 1
      const action = newStatus === 1 ? '启用' : '停用'
      
      this.$confirm(`确定要${action} "${club.club_name}" 社团吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        this.loading = true
        updateClub({
          club_id: club.club_id,
          status: newStatus
        }).then(() => {
          this.loading = false
          this.$message.success(`${action}成功`)
          this.loadClubs()
        }).catch(error => {
          this.loading = false
          this.$message.error(`${action}失败：` + (error.message || '未知错误'))
        })
      }).catch(() => {
        this.$message.info('已取消操作')
      })
    },
    deleteClub(club) {
      this.$confirm(
        `确定要永久解散 "${club.club_name}" 社团吗？此操作将删除社团所有相关数据，且不可恢复！`, 
        '警告', 
        {
          type: 'warning',
          confirmButtonText: '确定解散',
          confirmButtonClass: 'el-button--danger',
          cancelButtonText: '取消',
          dangerouslyUseHTMLString: true
        }
      ).then(() => {
        this.loading = true
        deleteClub(club.club_id).then(res => {
          this.loading = false
          if (res.status === 200) {
            this.$message.success('解散社团成功')
            this.loadClubs()
          } else {
            this.$message.error(res.message || '解散失败')
          }
        }).catch(error => {
          this.loading = false
          console.error('解散社团错误:', error)
          this.$message.error('解散失败：' + (error.message || '未知错误'))
        })
      }).catch(() => {
        this.$message.info('已取消解散操作')
      })
    },
    resetForm() {
      this.clubForm = {
        club_id: null,
        club_name: '',
        category: '',
        description: '',
        founder_id: null
      }
      this.isEdit = false
      if (this.$refs.clubForm) {
        this.$refs.clubForm.resetFields()
      }
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

/* 停用/启用按钮样式 - 使用更美观的蓝色系 */
.club-manage >>> .status-toggle-btn {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
}

.club-manage >>> .status-toggle-btn:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
  color: white;
}

.club-manage >>> .status-toggle-btn:focus {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
}

/* 停用状态标签使用灰色，更中性 */
.club-manage >>> .el-tag--info {
  background-color: #909399;
  border-color: #909399;
  color: white;
}

/* 解散按钮样式保持原有的danger红色 */
.club-manage >>> .el-button--danger {
  background-color: #f56c6c;
  border-color: #f56c6c;
}

.club-manage >>> .el-button--danger:hover {
  background-color: #f78989;
  border-color: #f78989;
}
</style>