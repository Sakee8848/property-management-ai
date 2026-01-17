<template>
  <div class="chat-page">
    <!-- 顶部导航 -->
    <van-nav-bar
      title="小管家AI助手"
      left-arrow
      @click-left="router.back()"
    >
      <template #right>
        <van-icon name="more-o" @click="showHistory = true" />
      </template>
    </van-nav-bar>

    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef">
      <div v-if="messages.length === 0" class="welcome">
        <van-icon name="service-o" size="60" color="#667eea" />
        <h3>您好!我是小管家</h3>
        <p>有什么可以帮您的吗?</p>
        
        <!-- 快捷问题 -->
        <div class="quick-questions">
          <van-button
            plain
            size="small"
            v-for="q in quickQuestions"
            :key="q"
            @click="sendMessage(q)"
          >
            {{ q }}
          </van-button>
        </div>
      </div>

      <div
        v-for="msg in messages"
        :key="msg.id"
        :class="['message-item', msg.role]"
      >
        <div class="message-avatar">
          <van-icon
            :name="msg.role === 'user' ? 'user-o' : 'service-o'"
            size="24"
          />
        </div>
        <div class="message-content">
          <div class="message-bubble">{{ msg.content }}</div>
          <div class="message-time">{{ formatTime(msg.created_at) }}</div>
          
          <!-- 显示引用的文档 -->
          <div v-if="msg.sources && msg.sources.length > 0" class="message-sources">
            <van-tag
              v-for="source in msg.sources"
              :key="source.document_id"
              size="mini"
              type="primary"
            >
              📄 {{ source.title }}
            </van-tag>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="message-item assistant">
        <div class="message-avatar">
          <van-icon name="service-o" size="24" />
        </div>
        <div class="message-content">
          <div class="message-bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-bar">
      <van-field
        v-model="inputMessage"
        placeholder="请输入您的问题..."
        @keyup.enter="handleSend"
      />
      <van-button
        type="primary"
        size="small"
        round
        @click="handleSend"
        :disabled="!inputMessage.trim() || loading"
      >
        发送
      </van-button>
    </div>

    <!-- 历史会话弹窗 -->
    <van-popup
      v-model:show="showHistory"
      position="right"
      :style="{ width: '80%', height: '100%' }"
    >
      <div class="history-popup">
        <h3>历史会话</h3>
        <van-list>
          <van-cell
            v-for="conv in conversations"
            :key="conv.id"
            :title="conv.title"
            is-link
            @click="loadConversation(conv.id)"
          />
        </van-list>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import axios from '../utils/axios'

const router = useRouter()

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const showHistory = ref(false)
const conversations = ref([])
const currentConversationId = ref(null)
const messageListRef = ref(null)

const quickQuestions = [
  '物业费怎么缴纳?',
  '如何报修?',
  '停车位规定是什么?',
  '装修需要什么手续?'
]

onMounted(() => {
  fetchConversations()
})

const handleSend = async () => {
  if (!inputMessage.value.trim() || loading.value) return
  
  await sendMessage(inputMessage.value)
}

const sendMessage = async (content) => {
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: content,
    created_at: new Date().toISOString()
  }
  
  messages.value.push(userMessage)
  inputMessage.value = ''
  
  scrollToBottom()
  
  loading.value = true
  
  try {
    const response = await axios.post('/api/chat/send', {
      content: content,
      conversation_id: currentConversationId.value
    })
    
    if (!currentConversationId.value) {
      currentConversationId.value = response.data.conversation_id
    }
    
    messages.value.push({
      id: response.data.id,
      role: 'assistant',
      content: response.data.content,
      sources: response.data.sources,
      created_at: response.data.created_at
    })
    
    scrollToBottom()
  } catch (error) {
    showToast('发送消息失败')
  } finally {
    loading.value = false
  }
}

const fetchConversations = async () => {
  try {
    const response = await axios.get('/api/chat/conversations')
    conversations.value = response.data
  } catch (error) {
    console.error('获取会话列表失败:', error)
  }
}

const loadConversation = async (conversationId) => {
  try {
    const response = await axios.get(`/api/chat/conversations/${conversationId}`)
    currentConversationId.value = conversationId
    messages.value = response.data.messages
    showHistory.value = false
    scrollToBottom()
  } catch (error) {
    showToast('加载会话失败')
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.chat-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.welcome {
  text-align: center;
  padding: 40px 20px;
}

.welcome h3 {
  margin: 16px 0 8px;
  font-size: 18px;
}

.welcome p {
  color: #666;
  margin-bottom: 24px;
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 300px;
  margin: 0 auto;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: #07c160;
}

.message-content {
  max-width: 70%;
}

.message-item.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-bubble {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-item.user .message-bubble {
  background: #667eea;
  color: white;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

.message-sources {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.typing {
  display: flex;
  gap: 4px;
  padding: 16px;
}

.typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.input-bar {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: white;
  border-top: 1px solid #eee;
}

.history-popup {
  padding: 20px;
  height: 100%;
}

.history-popup h3 {
  margin-bottom: 16px;
}
</style>
