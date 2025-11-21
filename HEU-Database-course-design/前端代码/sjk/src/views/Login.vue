<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>校园社团管理系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginForm">
        <el-form-item prop="telephone">
          <el-input 
            v-model="loginForm.telephone" 
            placeholder="手机号"
            prefix-icon="el-icon-phone"
          ></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="密码"
            prefix-icon="el-icon-lock"
            @keyup.enter.native="handleLogin"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            style="width:100%" 
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="links">
        <router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script>
/* eslint-disable */
import { userLogin } from '@/api/user'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        telephone: '',
        password: ''
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
        ]
      }
    }
  },
  methods: {
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          userLogin(this.loginForm).then(res => {
            this.loading = false
            const user = res.data
            localStorage.setItem('user', JSON.stringify(user))
            
            if (user.role === 2) {
              this.$router.push('/admin')
            } else {
              this.$router.push('/user')
            }
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
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #6af39ce1 0%, #bc8debd8 100%);
}
.login-card {
  width: 400px;
  padding: 20px;
}
.links {
  text-align: center;
  margin-top: 20px;
}
</style>