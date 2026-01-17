<template>
  <div class="profile-page">
    <!-- 用户信息卡片 -->
    <div class="user-card">
      <van-image
        round
        width="64"
        height="64"
        :src="userStore.userInfo?.avatar_url || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'"
      />
      <div class="user-info">
        <h3>{{ userStore.userInfo?.full_name || userStore.userInfo?.username }}</h3>
        <p>{{ userStore.userInfo?.phone }}</p>
      </div>
    </div>

    <!-- 功能列表 -->
    <van-cell-group>
      <van-cell title="个人信息" is-link @click="handlePersonalInfo" />
      <van-cell title="我的房产" is-link @click="handleProperty" />
      <van-cell title="缴费记录" is-link @click="handlePaymentHistory" />
      <van-cell title="我的投诉" is-link @click="handleComplaints" />
    </van-cell-group>

    <van-cell-group style="margin-top: 12px;">
      <van-cell title="消息通知" is-link @click="handleNotifications" />
      <van-cell title="常见问题" is-link @click="handleFAQ" />
      <van-cell title="关于我们" is-link @click="handleAbout" />
      <van-cell title="设置" is-link @click="handleSettings" />
    </van-cell-group>

    <!-- 退出登录 -->
    <div class="logout-section">
      <van-button block round @click="handleLogout">退出登录</van-button>
    </div>

    <!-- 版本信息 -->
    <div class="version-info">
      <p>物业管理AI助手 v1.0.0</p>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-model="active" route>
      <van-tabbar-item to="/home" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item to="/chat" icon="chat-o">智能咨询</van-tabbar-item>
      <van-tabbar-item to="/bills" icon="bill-o">缴费</van-tabbar-item>
      <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const active = ref(3)

const handlePersonalInfo = () => {
  showToast('个人信息功能开发中')
}

const handleProperty = () => {
  showToast('房产信息功能开发中')
}

const handlePaymentHistory = () => {
  showToast('缴费记录功能开发中')
}

const handleComplaints = () => {
  showToast('投诉记录功能开发中')
}

const handleNotifications = () => {
  showToast('消息通知功能开发中')
}

const handleFAQ = () => {
  showToast('常见问题功能开发中')
}

const handleAbout = () => {
  showToast('关于我们功能开发中')
}

const handleSettings = () => {
  showToast('设置功能开发中')
}

const handleLogout = () => {
  showConfirmDialog({
    title: '提示',
    message: '确定要退出登录吗?',
  })
    .then(() => {
      userStore.logout()
      router.push('/login')
    })
    .catch(() => {
      // 取消
    })
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 60px;
}

.user-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 32px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  color: white;
}

.user-info h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.user-info p {
  font-size: 14px;
  opacity: 0.9;
}

.logout-section {
  padding: 20px 16px;
  margin-top: 32px;
}

.version-info {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 12px;
}
</style>
