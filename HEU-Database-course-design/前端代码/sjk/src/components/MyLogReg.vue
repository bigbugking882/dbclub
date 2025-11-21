<template>
  <div class="container">
    <!-- 登录表单 -->
    <div class="login_box" v-show="target == 1">
      <div class="head">校园社团管理系统</div>
      <el-form label-width="0" class="login_form" :model="login_form" :rules="login_rules" ref="login_form">
        <el-form-item prop="userortel">
          <el-input v-model="login_form.userortel" spellcheck="false" placeholder="手机号"></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="login_form.password" show-password spellcheck="false" placeholder="密码"></el-input>
        </el-form-item>
        <el-form-item class="btns">
          <el-button type="primary" @click="llogin()">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="operate">
        <span id="op1" @click="change(2)">注册</span>
        <span id="op2" @click="change(3)">忘记密码</span>
      </div>
    </div>

    <!-- 注册表单 -->
    <div class="reg_box" v-show="target == 2">
      <div class="head">校园社团管理系统</div>
      <el-form class="reg_form" :model="reg_form" :rules="reg_rules" ref="reg_form">
        <el-form-item prop="username">
          <el-input v-model="reg_form.username" spellcheck="false" placeholder="用户名"></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="reg_form.password" show-password spellcheck="false" placeholder="密码(6-12位)"></el-input>
        </el-form-item>
        <el-form-item prop="telephone">
          <el-input v-model="reg_form.telephone" spellcheck="false" placeholder="手机号码"></el-input>
        </el-form-item>
        <el-form-item prop="vercode">
          <el-input v-model="reg_form.vercode" placeholder="验证码" style="width:230px"></el-input>
          <span 
            style="width:120px;font-size:16px;cursor:pointer" 
            @click="send_vercode_pre()"
            v-show="getcode_show"
          >
            获取验证码
          </span>
          <span style="width:120px;font-size:16px" v-show="!getcode_show">
            {{ time_count }}s后重新获取
          </span>
        </el-form-item>
        <el-form-item class="btns">
          <el-button type="primary" @click="zhuce()">注册</el-button>
        </el-form-item>
      </el-form>
      <div>
        <span @click="change(1)" style="margin-left:210px;color:#000;opacity:.5;cursor:pointer;">登录</span>
      </div>
    </div>

    <!-- 找回密码 -->
    <div class="forget_box" v-show="target == 3">
      <div class="head">校园社团管理系统</div>
      <el-form class="reg_form" :model="findback_form" :rules="findback_rules" ref="findback_form">
        <el-form-item prop="telephone">
          <el-input v-model="findback_form.telephone" placeholder="手机号码"></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="findback_form.password" show-password placeholder="新密码"></el-input>
        </el-form-item>
        <el-form-item prop="vercode">
          <el-input v-model="findback_form.vercode" placeholder="验证码" style="width:230px"></el-input>
          <span 
            style="width:120px;font-size:16px;cursor:pointer" 
            @click="send_findback_vercode()"
            v-show="getcode_show"
          >
            获取验证码
          </span>
          <span style="width:120px;font-size:16px" v-show="!getcode_show">
            {{ time_count }}s后重新获取
          </span>
        </el-form-item>
        <el-form-item class="btns">
          <el-button type="primary" @click="findback()">确认修改</el-button>
        </el-form-item>
      </el-form>
      <div>
        <span @click="change(1)" style="margin-left:210px;color:#000;opacity:.5;cursor:pointer;">登录</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MyLogReg',
  data() {
    const checkMobile = (rule, value, cb) => {
      const regMobile = /^\d{11}$/;
      return regMobile.test(value) ? cb() : cb(new Error('手机号码格式不正确'));
    };
    return {
      target: 1,
      getcode_show: true,
      time_count: 60,
      timer: null,
      login_form: { userortel: '', password: '' },
      reg_form: { username: '', password: '', telephone: '', vercode: '' },
      findback_form: { telephone: '', password: '', vercode: '' },
      login_rules: {
        userortel: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { validator: checkMobile, trigger: 'blur' }
        ],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
      },
      reg_rules: {
        username: [{ required: true, message: '请设置用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请设置密码', trigger: 'blur' }],
        telephone: [
          { required: true, message: '请绑定手机号', trigger: 'blur' },
          { validator: checkMobile, trigger: 'blur' }
        ]
      },
      findback_rules: {
        telephone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { validator: checkMobile, trigger: 'blur' }
        ],
        password: [{ required: true, message: '请输入新密码', trigger: 'blur' }]
      }
    };
  },
  methods: {
    change(type) {
      this.target = type;
      this.clearTimer();
    },
    clearTimer() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
        this.getcode_show = true;
        this.time_count = 60;
      }
    },
    setInterval() {
      this.getcode_show = false;
      this.timer = setInterval(() => {
        if (this.time_count > 0) {
          this.time_count--;
        } else {
          this.clearTimer();
        }
      }, 1000);
    },
    send_vercode_pre() {
      this.$refs.reg_form.validateField('telephone', (err) => {
        if (!err) this.send_vercode();
      });
    },
    send_vercode() {
      this.$axios.post('/api/user/get_vercode', {
        telephone: this.reg_form.telephone
      }).then(res => {
        if (res.data.code === 200) {
          this.$message.success('验证码发送成功');
          this.setInterval();
        } else {
          this.$message.error(res.data.msg);
        }
      });
    },
    send_findback_vercode() {
      this.$axios.post('/api/user/get_vercode', {
        telephone: this.findback_form.telephone
      }).then(res => {
        if (res.data.code === 200) {
          this.$message.success('验证码发送成功');
          this.setInterval();
        } else {
          this.$message.error(res.data.msg);
        }
      });
    },
    zhuce() {
      this.$refs.reg_form.validate(valid => {
        if (valid && this.reg_form.vercode) {
          this.$axios.post('/api/user/register', this.reg_form).then(res => {
            if (res.data.code === 200) {
              this.$message.success('注册成功');
              this.target = 1;
            } else {
              this.$message.error(res.data.msg);
            }
          });
        }
      });
    },
    llogin() {
      this.$refs.login_form.validate(valid => {
        if (valid) {
          this.$axios.post('/api/user/login', {
            telephone: this.login_form.userortel,
            password: this.login_form.password
          }).then(res => {
            if (res.data.code === 200) {
              localStorage.setItem('token', res.data.token);
              localStorage.setItem('role', res.data.user.role);
              this.$router.push(res.data.user.role === 0 ? '/user' : '/manage');
            } else {
              this.$message.error(res.data.msg);
            }
          });
        }
      });
    },
    findback() {
      this.$refs.findback_form.validate(valid => {
        if (valid && this.findback_form.vercode) {
          this.$axios.post('/api/user/reset_pwd', this.findback_form).then(res => {
            if (res.data.code === 200) {
              this.$message.success('密码重置成功');
              this.target = 1;
            } else {
              this.$message.error(res.data.msg);
            }
          });
        }
      });
    }
  },
  beforeDestroy() {
    this.clearTimer();
  }
};
</script>

<style lang="less" scoped>
.container {
  background-color: #2b4b6b;
  height: 100vh;
  width: 100%;
}
.head {
  text-align: center;
  height: 50px;
  line-height: 50px;
  font-size: larger;
}
.login_box, .reg_box, .forget_box {
  background-color: white;
  border-radius: 3px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
.login_box {
  height: 300px;
  width: 450px;
}
.reg_box {
  height: 400px;
  width: 450px;
}
.forget_box {
  height: 350px;
  width: 450px;
}
.el-form-item {
  width: 350px;
  margin-left: 50px;
}
.btns {
  text-align: center;
  margin-top: 20px;
}
.operate {
  text-align: center;
  color: #000;
  opacity: 0.5;
  font-size: 16px;
  margin-top: 10px;
}
#op1 {
  padding: 0 15px;
  border-right: 1px solid #bdb9b9;
  cursor: pointer;
}
#op2 {
  padding: 0 15px;
  cursor: pointer;
}
</style>