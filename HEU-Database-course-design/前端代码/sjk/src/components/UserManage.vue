<template>
  <div class="user-manage">
    <div class="header">
      <h3>用户管理</h3>
    </div>
    
    <el-table :data="userList" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="username" label="用户名"></el-table-column>
      <el-table-column prop="telephone" label="手机号"></el-table-column>
      <el-table-column prop="role" label="角色">
        <template slot-scope="scope">
          <el-tag :type="getRoleType(scope.row.role)">
            {{ getRoleText(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="注册时间"></el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button size="mini" @click="editUser(scope.row)">编辑</el-button>
          <el-button 
            size="mini" 
            :type="scope.row.role === 2 ? 'danger' : 'success'"
            @click="toggleUserRole(scope.row)"
          >
            {{ scope.row.role === 2 ? '取消管理员' : '设为管理员' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 编辑用户对话框 -->
    <el-dialog title="编辑用户" :visible.sync="showEditDialog">
      <el-form :model="userForm" :rules="userRules" ref="userForm">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username"></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="telephone">
          <el-input v-model="userForm.telephone" disabled></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="留空则不修改"></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role">
            <el-option label="普通用户" :value="0"></el-option>
            <el-option label="社团管理员" :value="1"></el-option>
            <el-option label="系统管理员" :value="2"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getUsers, updateUser } from '@/api/user'

export default {
  name: 'UserManage',
  data() {
    return {
      userList: [],
      loading: false,
      showEditDialog: false,
      userForm: {
        id: null,
        username: '',
        telephone: '',
        password: '',
        role: 0
      },
      userRules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        role: [{ required: true, message: '请选择角色', trigger: 'change' }]
      }
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    loadUsers() {
      this.loading = true
      getUsers().then(res => {
        this.userList = res.data
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    editUser(user) {
      this.userForm = { ...user, password: '' }
      this.showEditDialog = true
    },
    handleSaveUser() {
      this.$refs.userForm.validate(valid => {
        if (valid) {
          const updateData = { ...this.userForm }
          if (!updateData.password) {
            delete updateData.password
          }
          
          updateUser(updateData).then(() => {
            this.$message.success('更新成功')
            this.showEditDialog = false
            this.loadUsers()
          })
        }
      })
    },
    toggleUserRole(user) {
      const newRole = user.role === 2 ? 0 : 2
      const action = newRole === 2 ? '设为管理员' : '取消管理员'
      
      this.$confirm(`确定要${action}吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        updateUser({
          id: user.id,
          role: newRole
        }).then(() => {
          this.$message.success(`${action}成功`)
          this.loadUsers()
        })
      })
    },
    getRoleType(role) {
      const types = ['', 'success', 'danger']
      return types[role] || ''
    },
    getRoleText(role) {
      const texts = ['普通用户', '社团管理员', '系统管理员']
      return texts[role] || '未知'
    }
  }
}
</script>