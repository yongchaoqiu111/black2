import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login(credentials) {
    return apiClient.post('/auth/login', credentials)
  },
  
  register(userData) {
    return apiClient.post('/auth/register', userData)
  },
  
  registerAI(aiData) {
    return apiClient.post('/auth/register/ai', aiData)
  },
  
  verifyApiKey(apiKey) {
    return apiClient.post('/auth/verify-ai-key', { apiKey })
  },
  
  getProfile() {
    return apiClient.get('/auth/profile')
  },
  
  updateProfile(profileData) {
    return apiClient.put('/auth/profile', profileData)
  }
}

// Products API
export const productsApi = {
  getAll(params = {}) {
    return apiClient.get('/products', { params })
  },
  
  getById(productId) {
    return apiClient.get(`/products/${productId}`)
  },
  
  create(productData) {
    return apiClient.post('/products', productData)
  },
  
  update(productId, productData) {
    return apiClient.put(`/products/${productId}`, productData)
  },
  
  delete(productId) {
    return apiClient.delete(`/products/${productId}`)
  },
  
  search(query, params = {}) {
    return apiClient.get('/products/search', { 
      params: { q: query, ...params } 
    })
  }
}

// Orders API
export const ordersApi = {
  getAll(params = {}) {
    return apiClient.get('/transactions', { params })
  },
  
  getById(orderId) {
    return apiClient.get(`/transactions/${orderId}`)
  },
  
  create(orderData) {
    return apiClient.post('/transactions', orderData)
  },
  
  cancel(orderId) {
    return apiClient.post(`/transactions/${orderId}/cancel`)
  },
  
  complete(orderId) {
    return apiClient.post(`/transactions/${orderId}/complete`)
  },
  
  dispute(orderId, data) {
    return apiClient.post(`/transactions/${orderId}/dispute`, data)
  },
  
  refund(orderId) {
    return apiClient.post(`/transactions/${orderId}/refund`)
  }
}

// Wallet API
export const walletApi = {
  // Human wallet
  getHumanWallet(address) {
    return apiClient.get(`/wallets/human/${address}`)
  },
  
  // AI wallet
  getAIWallet(address) {
    return apiClient.get(`/wallets/ai/${address}`)
  },
  
  // Generate AI wallet from master
  generateAIWallet(aiIndex = 0) {
    return apiClient.get('/wallets/ai/generate', { params: { ai_index: aiIndex } })
  },
  
  getBalance() {
    return apiClient.get('/wallet/balance')
  },
  
  deposit(depositData) {
    return apiClient.post('/wallet/deposit', depositData)
  },
  
  withdraw(withdrawData) {
    return apiClient.post('/wallet/withdraw', withdrawData)
  },
  
  getTransactions(params = {}) {
    return apiClient.get('/wallet/transactions', { params })
  }
}

// Chat API
export const chatApi = {
  getConversations() {
    return apiClient.get('/chat/conversations')
  },
  
  getMessages(conversationId, params = {}) {
    return apiClient.get(`/chat/messages/${conversationId}`, { params })
  },
  
  sendMessage(messageData) {
    return apiClient.post('/chat/messages', messageData)
  },
  
  markAsRead(conversationId) {
    return apiClient.post(`/chat/conversations/${conversationId}/read`)
  }
}

// AI Config API
export const aiConfigApi = {
  getConfig(userId) {
    return apiClient.get(`/ai/config/${userId}`)
  },
  
  updateConfig(userId, configData) {
    return apiClient.put(`/ai/config/${userId}`, configData)
  },
  
  testConnection(userId) {
    return apiClient.post(`/ai/test-connection/${userId}`)
  },
  
  getAnalytics(userId, params = {}) {
    return apiClient.get(`/ai/analytics/${userId}`, { params })
  }
}

// Upload API
export const uploadApi = {
  uploadFile(formData) {
    return apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  uploadMultiple(files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    return apiClient.post('/upload/multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// Notification Settings API
export const notificationApi = {
  // 获取通知设置
  getSettings() {
    return apiClient.get('/notifications/settings')
  },
  
  // 保存通知设置
  saveSettings(settingsData) {
    return apiClient.put('/notifications/settings', settingsData)
  },
  
  // 测试OpenClaw推送
  testOpenClaw(deviceId, apiKey) {
    return apiClient.post('/notifications/test/openclaw', { deviceId, apiKey })
  },
  
  // 获取AI代理统计数据
  getStats() {
    return apiClient.get('/notifications/stats')
  },
  
  // 订阅浏览器推送
  subscribeWebPush(subscriptionData) {
    return apiClient.post('/notifications/webpush/subscribe', subscriptionData)
  },
  
  // 取消订阅浏览器推送
  unsubscribeWebPush() {
    return apiClient.post('/notifications/webpush/unsubscribe')
  }
}

export default apiClient
