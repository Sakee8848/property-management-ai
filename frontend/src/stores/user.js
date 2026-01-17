import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../utils/axios'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  // 登录
  const login = async (username, password) => {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post('/api/auth/login', formData)
      
      token.value = response.data.access_token
      userInfo.value = response.data.user
      
      localStorage.setItem('token', token.value)
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败'
      }
    }
  }

  // 注册
  const register = async (data) => {
    try {
      await axios.post('/api/auth/register', data)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '注册失败'
      }
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const response = await axios.get('/api/auth/me')
      userInfo.value = response.data
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  return {
    token,
    userInfo,
    login,
    register,
    logout,
    fetchUserInfo
  }
})
