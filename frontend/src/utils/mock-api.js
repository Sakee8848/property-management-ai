// 模拟API - 用于开发和测试
export const mockAPI = {
  // 模拟登录
  login: (username, password) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: {
            access_token: 'mock-token-' + Date.now(),
            token_type: 'bearer',
            user: {
              id: 1,
              username: username,
              email: username + '@example.com',
              role: 'owner',
              property_id: 1
            }
          }
        })
      }, 500)
    })
  },

  // 模拟注册
  register: (data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: { success: true } })
      }, 500)
    })
  },

  // 模拟获取用户信息
  getUserInfo: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: {
            id: 1,
            username: 'demo_user',
            email: 'demo@example.com',
            role: 'owner',
            property_id: 1
          }
        })
      }, 300)
    })
  },

  // 模拟发送消息
  sendMessage: (content) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const responses = {
          '物业费怎么缴纳？': {
            content: '您可以通过以下方式缴纳物业费：\n\n1. 在线缴费：点击"缴费中心"选择账单进行支付\n2. 微信支付：关注物业公众号进行缴费\n3. 支付宝：搜索"物业缴费"小程序\n4. 现场缴费：到物业服务中心办理\n\n物业费缴费期限为每月月底前，逾期将产生滞纳金。',
            sources: [{ document_id: 1, title: '物业缴费指南', score: 0.95 }]
          },
          '如何报修？': {
            content: '报修服务流程：\n\n1. 在线报修：点击首页"报修服务"填写报修信息\n2. 电话报修：拨打物业服务热线 400-123-4567\n3. 现场报修：到物业服务中心前台登记\n\n我们承诺：\n- 紧急维修30分钟内响应\n- 一般维修24小时内处理',
            sources: [{ document_id: 2, title: '报修服务指南', score: 0.92 }]
          }
        }

        const response = responses[content] || {
          content: '感谢您的咨询！我是物业AI助手小管家。\n\n您的问题已记录，我会为您查询相关信息。如需紧急帮助，请拨打物业服务热线：400-123-4567',
          sources: []
        }

        resolve({
          data: {
            id: Date.now(),
            role: 'assistant',
            content: response.content,
            sources: response.sources,
            created_at: new Date().toISOString()
          }
        })
      }, 1000)
    })
  },

  // 模拟获取会话列表
  getConversations: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: [] })
      }, 300)
    })
  },

  // 模拟获取文档列表
  getDocuments: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: [] })
      }, 300)
    })
  },

  // 模拟获取账单列表
  getBills: () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: [
            {
              id: 1,
              bill_number: 'BILL202401001',
              fee_type: 'property',
              amount: 1500,
              late_fee: 0,
              total_amount: 1500,
              billing_period: '2024-01',
              due_date: '2024-01-31',
              status: 'pending',
              created_at: '2024-01-01T00:00:00'
            }
          ]
        })
      }, 300)
    })
  }
}
