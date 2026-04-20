import { io } from 'socket.io-client'

// Socket.io客户端实例（单例）
let socket = null
let reconnectTimer = null

// 连接配置
const WS_CONFIG = {
  url: import.meta.env.VITE_WS_URL || 'ws://localhost:3000',
  transports: ['websocket'],
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  timeout: 20000,
  autoConnect: false
}

/**
 * 初始化WebSocket连接
 * @param {string} token - JWT Token
 */
export const initSocket = (token) => {
  if (!token) {
    console.error('❌ [WebSocket] Token不存在，无法建立连接')
    return null
  }

  // ✅ 如果已有连接，先断开（防止重复监听）
  if (socket) {
    console.log('🔄 [WebSocket] 检测到旧连接，先断开...')
    socket.off()
    socket.disconnect()
    socket = null
  }

  console.log('🔑 [WebSocket] 使用Token连接:', token.substring(0, 20) + '...')
  console.log('🔌 [WebSocket] 连接地址:', WS_CONFIG.url)

  // 创建新连接
  socket = io(WS_CONFIG.url, {
    ...WS_CONFIG,
    auth: { token }
  })

  // === 连接事件 ===
  socket.on('connect', () => {
    console.log('✅ [WebSocket] 连接成功, Socket ID:', socket.id)
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  })

  // 断开连接
  socket.on('disconnect', (reason) => {
    console.warn('⚠️ [WebSocket] 连接断开:', reason)
    
    // 如果是服务器主动断开，尝试重连
    if (reason === 'io server disconnect') {
      console.log('🔄 [WebSocket] 服务器断开，准备重连...')
      reconnectTimer = setTimeout(() => {
        socket.connect()
      }, 2000)
    }
  })

  // 重连中
  socket.on('reconnecting', (attemptNumber) => {
    console.log(`🔄 [WebSocket] 重连中... 第${attemptNumber}次尝试`)
  })

  // 重连成功
  socket.on('reconnect', (attemptNumber) => {
    console.log(`✅ [WebSocket] 重连成功！尝试次数: ${attemptNumber}`)
  })

  // 重连失败
  socket.on('reconnect_failed', () => {
    console.error('❌ [WebSocket] 重连失败，请检查网络连接')
  })

  // 连接错误
  socket.on('connect_error', (error) => {
    console.error('❌ [WebSocket] 连接错误:', error.message)
  })

  // 认证错误
  socket.on('auth_error', (error) => {
    console.error('❌ [WebSocket] 认证失败:', error)
    // Token过期或无效，跳转到登录页
    localStorage.removeItem('token')
    window.location.href = '/login'
  })

  return socket
}

/**
 * 获取Socket实例
 */
export const getSocket = () => {
  if (!socket) {
    console.warn('⚠️ [WebSocket] Socket未初始化，请先调用initSocket()')
    return null
  }
  return socket
}

/**
 * 断开连接
 */
export const disconnectSocket = () => {
  if (socket) {
    console.log('🔌 [WebSocket] 主动断开连接')
    socket.off()
    socket.disconnect()
    socket = null
    
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }
}

// ==================== 客服系统事件 ====================

/**
 * 注册用户到客服系统
 */
export const registerCustomer = (data) => {
  const sock = getSocket()
  if (sock && sock.connected) {
    console.log('👤 [客服] 注册用户:', data)
    sock.emit('customer:register', data)
  }
}

/**
 * 发送客服消息
 */
export const sendCustomerMessage = (data) => {
  const sock = getSocket()
  if (sock && sock.connected) {
    console.log('💬 [客服] 发送消息:', data)
    sock.emit('customer:sendMessage', data)
  } else {
    console.error('❌ [客服] WebSocket未连接，无法发送消息')
  }
}

/**
 * 监听客服新消息（来自管理员）
 */
export const onCustomerNewMessage = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('customer:newMessage', callback)
  }
}

/**
 * 监听消息发送确认
 */
export const onCustomerMessageSent = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('customer:messageSent', callback)
  }
}

/**
 * 监听客服在线状态
 */
export const onAdminStatus = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('customer:adminStatus', callback)
  }
}

/**
 * 绑定 Telegram
 */
export const bindTelegram = (data) => {
  const sock = getSocket()
  if (sock && sock.connected) {
    console.log('📱 [客服] 绑定 Telegram:', data)
    sock.emit('customer:bindTelegram', data)
  }
}

// ==================== 聊天系统事件 ====================

/**
 * 加入聊天室
 */
export const joinChatRoom = (roomId) => {
  const sock = getSocket()
  if (sock) {
    sock.emit('chat:join', { roomId })
    console.log('✅ [WebSocket] 加入聊天室:', roomId)
  }
}

/**
 * 离开聊天室
 */
export const leaveChatRoom = (roomId) => {
  const sock = getSocket()
  if (sock) {
    sock.emit('chat:leave', { roomId })
    console.log('✅ [WebSocket] 离开聊天室:', roomId)
  }
}

/**
 * 发送聊天消息
 */
export const sendChatMessage = (data) => {
  const sock = getSocket()
  if (sock && sock.connected) {
    sock.emit('chat:message', data)
  }
}

/**
 * 监听新消息
 */
export const onNewMessage = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('chat:newMessage', callback)
  }
}

/**
 * 监听输入状态
 */
export const onTyping = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('chat:typing', callback)
  }
}

/**
 * 发送输入状态
 */
export const sendTyping = (roomId, isTyping) => {
  const sock = getSocket()
  if (sock) {
    sock.emit('chat:typing', { roomId, isTyping })
  }
}

// ==================== 订单系统事件 ====================

/**
 * 监听订单状态更新
 */
export const onOrderUpdate = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('order:updated', callback)
  }
}

/**
 * 监听支付确认
 */
export const onPaymentConfirmed = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('payment:confirmed', callback)
  }
}

// ==================== 通知系统事件 ====================

/**
 * 监听系统通知
 */
export const onNotification = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('notification:new', callback)
  }
}

/**
 * 监听AI代理状态
 */
export const onAIAgentStatus = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('ai:agentStatus', callback)
  }
}

// ==================== 商品系统事件 ====================

/**
 * 监听商品价格更新
 */
export const onPriceUpdate = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('product:priceUpdate', callback)
  }
}

/**
 * 监听库存变化
 */
export const onStockUpdate = (callback) => {
  const sock = getSocket()
  if (sock) {
    sock.on('product:stockUpdate', callback)
  }
}
