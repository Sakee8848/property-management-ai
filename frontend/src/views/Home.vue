<template>
  <div class="home-page">
    <!-- 顶部信息栏 -->
    <div class="header-info">
      <div class="property-info">
        <h2>{{ userStore.userInfo?.property_name || '未选择物业' }}</h2>
        <p>{{ userStore.userInfo?.full_name || userStore.userInfo?.username }}</p>
      </div>
      <van-icon name="setting-o" size="24" @click="router.push('/profile')" />
    </div>

    <!-- AI助手快捷入口 -->
    <div class="ai-assistant">
      <div class="ai-avatar">
        <van-icon name="service-o" size="40" color="#fff" />
      </div>
      <div class="ai-info">
        <h3>小管家AI助手</h3>
        <p>有什么可以帮您的吗?</p>
      </div>
      <van-button type="primary" round size="small" @click="router.push('/chat')">
        开始对话
      </van-button>
    </div>

    <!-- 功能菜单 -->
    <div class="function-grid">
      <div class="function-item" @click="router.push('/chat')">
        <van-icon name="chat-o" size="32" color="#1989fa" />
        <span>智能咨询</span>
      </div>
      <div class="function-item" @click="router.push('/bills')">
        <van-icon name="bill-o" size="32" color="#07c160" />
        <span>缴费中心</span>
      </div>
      <div class="function-item" @click="router.push('/documents')">
        <van-icon name="notes-o" size="32" color="#ff976a" />
        <span>文档查询</span>
      </div>
      <div class="function-item" @click="handleRepair">
        <van-icon name="tools-o" size="32" color="#ee0a24" />
        <span>报修服务</span>
      </div>
      <div class="function-item" @click="handleComplaint">
        <van-icon name="warning-o" size="32" color="#ff976a" />
        <span>投诉建议</span>
      </div>
      <div class="function-item" @click="handleNotice">
        <van-icon name="volume-o" size="32" color="#1989fa" />
        <span>公告通知</span>
      </div>
    </div>

    <!-- 最新通知 -->
    <div class="notice-section">
      <div class="section-title">
        <h3>最新通知</h3>
        <van-button plain size="mini" @click="handleNotice">查看更多</van-button>
      </div>
      <van-notice-bar
        left-icon="volume-o"
        text="欢迎使用物业管理AI助手!有任何问题都可以咨询小管家。"
      />
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
import { showToast } from 'vant'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const active = ref(0)

const handleRepair = () => {
  showToast('报修功能开发中')
}

const handleComplaint = () => {
  showToast('投诉建议功能开发中')
}

const handleNotice = () => {
  showToast('通知功能开发中')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 60px;
}

.header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  color: white;
}

.property-info h2 {
  font-size: 20px;
  margin-bottom: 5px;
}

.property-info p {
  font-size: 14px;
  opacity: 0.9;
}

.ai-assistant {
  display: flex;
  align-items: center;
  background: white;
  margin: 16px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.ai-avatar {
  width: 60px;
  height: 60px;
  border-radius: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.ai-info {
  flex: 1;
}

.ai-info h3 {
  font-size: 16px;
  margin-bottom: 4px;
}

.ai-info p {
  font-size: 13px;
  color: #666;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px;
}

.function-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.function-item:active {
  transform: scale(0.95);
}

.function-item span {
  font-size: 13px;
  color: #333;
}

.notice-section {
  margin: 16px;
  background: white;
  padding: 16px;
  border-radius: 12px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title h3 {
  font-size: 16px;
}
</style>
