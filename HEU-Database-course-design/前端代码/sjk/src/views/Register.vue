<template>
  <div class="register-container">
    <el-card class="register-card">
      <h2>用户注册</h2>
      <el-form :model="registerForm" :rules="rules" ref="registerForm">
        <el-form-item prop="telephone">
          <el-input 
            v-model="registerForm.telephone" 
            placeholder="手机号"
            prefix-icon="el-icon-phone"
          ></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="密码"
            prefix-icon="el-icon-lock"
          ></el-input>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="确认密码"
            prefix-icon="el-icon-lock"
          ></el-input>
        </el-form-item>
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="用户名（可选）"
            prefix-icon="el-icon-user"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            style="width:100%" 
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="links">
        <router-link to="/login">已有账号？立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script>
/* eslint-disable */
import { userRegister } from '@/api/user'

export default {
  name: 'Register',
  data() {
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        telephone: '',
        password: '',
        confirmPassword: '',
        username: ''
      },
      loading: false,
      rules: {
        telephone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validatePass2, trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    handleRegister() {
      this.$refs.registerForm.validate(valid => {
        if (valid) {
          this.loading = true
          const registerData = {
            telephone: this.registerForm.telephone,
            password: this.registerForm.password,
            username: this.registerForm.username || undefined
          }
          
          userRegister(registerData).then(() => {
            this.loading = false
            this.$message.success('注册成功')
            this.$router.push('/login')
          }).catch(() => {
            this.loading = false
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.register-card {
  width: 400px;
  padding: 20px;
}
.links {
  text-align: center;
  margin-top: 20px;
}
</style>