<template>
  <div class="login-page">
    <div class="header">
      <h1>物业管理AI助手</h1>
      <p class="subtitle">智能服务 贴心管家</p>
    </div>

    <van-form @submit="handleLogin" class="login-form">
      <van-cell-group inset>
        <van-field
          v-model="loginForm.username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请输入用户名' }]"
        />
        <van-field
          v-model="loginForm.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请输入密码' }]"
        />
      </van-cell-group>
      
      <div class="button-group">
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
        >
          登录
        </van-button>
        
        <van-button
          round
          block
          plain
          type="primary"
          @click="showRegister = true"
          class="register-btn"
        >
          注册账号
        </van-button>
      </div>
    </van-form>

    <!-- 注册弹窗 -->
    <van-popup v-model:show="showRegister" position="bottom" :style="{ height: '70%' }">
      <div class="register-popup">
        <h3>注册新账号</h3>
        <van-form @submit="handleRegister">
          <van-cell-group>
            <van-field
              v-model="registerForm.username"
              name="username"
              label="用户名"
              placeholder="请输入用户名"
              :rules="[{ required: true, message: '请输入用户名' }]"
            />
            <van-field
              v-model="registerForm.email"
              name="email"
              label="邮箱"
              placeholder="请输入邮箱"
              :rules="[{ required: true, message: '请输入邮箱' }]"
            />
            <van-field
              v-model="registerForm.phone"
              name="phone"
              label="手机号"
              placeholder="请输入手机号"
              :rules="[{ required: true, message: '请输入手机号' }]"
            />
            <van-field
              v-model="registerForm.full_name"
              name="full_name"
              label="姓名"
              placeholder="请输入真实姓名"
            />
            <van-field
              v-model="registerForm.password"
              type="password"
              name="password"
              label="密码"
              placeholder="请输入密码"
              :rules="[{ required: true, message: '请输入密码' }]"
            />
          </van-cell-group>
          
          <div class="button-group">
            <van-button round block type="primary" native-type="submit" :loading="registerLoading">
              注册
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const registerLoading = ref(false)
const showRegister = ref(false)

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  phone: '',
  full_name: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    const result = await userStore.login(loginForm.value.username, loginForm.value.password)
    if (result.success) {
      showToast('登录成功')
      router.push('/home')
    } else {
      showToast(result.message)
    }
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  registerLoading.value = true
  try {
    const result = await userStore.register(registerForm.value)
    if (result.success) {
      showToast('注册成功,请登录')
      showRegister.value = false
      registerForm.value = {
        username: '',
        email: '',
        phone: '',
        full_name: '',
        password: ''
      }
    } else {
      showToast(result.message)
    }
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 20px;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 60px;
}

.header h1 {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.login-form {
  max-width: 400px;
  margin: 0 auto;
}

.button-group {
  padding: 24px 16px;
}

.register-btn {
  margin-top: 12px;
}

.register-popup {
  padding: 20px;
}

.register-popup h3 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 20px;
}
</style>
