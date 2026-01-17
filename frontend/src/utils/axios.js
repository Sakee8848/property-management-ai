import axios from 'axios'
import { showToast } from 'vant'
import { mockAPI } from './mock-api'

// 检测是否使用模拟API（当后端不可用时）
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true' || true // 默认使用模拟API

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // 如果使用模拟API，拦截请求
    if (USE_MOCK) {
      return Promise.reject({ __useMock: true, config })
    }
    
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    // 如果是模拟API请求
    if (error.__useMock) {
      const { config } = error
      const { method, url, data } = config
      
      // 路由到模拟API
      try {
        if (url.includes('/auth/login')) {
          const formData = data
          const username = formData.get('username')
          const password = formData.get('password')
          return await mockAPI.login(username, password)
        } else if (url.includes('/auth/register')) {
          return await mockAPI.register(JSON.parse(data))
        } else if (url.includes('/auth/me')) {
          return await mockAPI.getUserInfo()
        } else if (url.includes('/chat/send')) {
          const payload = JSON.parse(data)
          return await mockAPI.sendMessage(payload.content)
        } else if (url.includes('/chat/conversations')) {
          return await mockAPI.getConversations()
        } else if (url.includes('/documents')) {
          return await mockAPI.getDocuments()
        } else if (url.includes('/payments/bills')) {
          return await mockAPI.getBills()
        }
        
        // 默认返回空数据
        return { data: {} }
      } catch (mockError) {
        return Promise.reject(mockError)
      }
    }
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          showToast('登录已过期,请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          setTimeout(() => {
            window.location.href = '/login'
          }, 1500)
          break
        case 403:
          showToast('没有权限访问')
          break
        case 404:
          showToast('请求的资源不存在')
          break
        case 500:
          showToast('服务器错误')
          break
        default:
          showToast(error.response.data?.detail || '请求失败')
      }
    } else {
      showToast('网络错误,请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default instance
