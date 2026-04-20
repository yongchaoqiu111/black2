<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-6">👨‍�?客服�?(固定ID: admin_001)</h1>
      
      <!-- Telegram 绑定表单 -->
      <div class="bg-white rounded-lg shadow p-6 mb-4">
        <h2 class="text-xl font-semibold mb-4">📱 绑定 Telegram（接收离线消息）</h2>
        <div class="flex gap-2">
          <input 
            v-model="telegramChatId" 
            placeholder="输入你的 Telegram Chat ID（纯数字�?
            class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button 
            @click="bindTelegram"
            class="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            绑定
          </button>
        </div>
        <p class="mt-2 text-xs text-gray-500">💡 提示：搜�?@userinfobot 获取你的 Chat ID</p>
        <p v-if="bindStatus" :class="['mt-2 text-sm', bindSuccess ? 'text-green-600' : 'text-red-600']">
          {{ bindStatus }}
        </p>
      </div>

      <div class="bg-white rounded-lg shadow p-6 mb-4">
        <div class="flex items-center justify-between">
          <span class="text-lg font-semibold">我的状�?</span>
          <button 
            @click="toggleOnline"
            :class="['px-4 py-2 rounded-lg', online ? 'bg-green-500' : 'bg-red-500', 'text-white']"
          >
            {{ online ? '在线' : '离线' }}
          </button>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6 h-96 overflow-y-auto mb-4" ref="messageContainer">
        <div v-for="msg in messages" :key="msg.id" 
             :class="['mb-2', msg.fromAdmin ? 'text-right' : 'text-left']">
          <div :class="['inline-block px-4 py-2 rounded-lg max-w-xs', 
                       msg.fromAdmin ? 'bg-blue-500 text-white' : 'bg-gray-200']">
            <div v-if="!msg.fromAdmin" class="text-xs text-gray-500 mb-1">
              用户: {{ msg.userId }}
            </div>
            {{ msg.text }}
          </div>
        </div>
      </div>

      <div class="flex gap-2">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage"
          placeholder="回复消息..."
          class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button 
          @click="sendMessage"
          class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          发�?
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { io } from 'socket.io-client'

const socket = ref(null)
const messages = ref([])
const newMessage = ref('')
const online = ref(false)
const messageContainer = ref(null)
const telegramChatId = ref('')
const bindStatus = ref('')
const bindSuccess = ref(false)

const FIXED_ADMIN_ID = 'admin_001'

onMounted(() => {
  // 连接 WebSocket（带 admin=true�?
  socket.value = io('https://ai656.top', {
    transports: ['websocket'],
    query: { admin: 'true' }
  })

  // 注册为管理员
  socket.value.on('connect', () => {
    console.log('�?[客服端] 已连�?)
    
    // 注册到管理员房间
    socket.value.emit('customer:registerAdmin')
  })

  // 监听用户消息
  socket.value.on('customer:newMessage', (data) => {
    console.log('📨 [客服端] 收到用户消息:', data)
    
    if (data.message && !data.message.fromAdmin) {
      messages.value.push({
        id: data.message.id,
        fromAdmin: false,
        userId: data.user?.userId || 'unknown',
        text: data.message.text,
        timestamp: new Date()
      })
      scrollToBottom()
    }
  })

  // 监听发送确�?
  socket.value.on('customer:messageSent', (data) => {
    console.log('�?[客服端] 消息发送成�?', data)
  })
})

// 绑定 Telegram
const bindTelegram = async () => {
  const chatId = telegramChatId.value.trim()
  
  if (!chatId) {
    bindStatus.value = '�?请输�?Chat ID'
    bindSuccess.value = false
    return
  }
  
  // 验证必须是纯数字
  if (!/^\d+$/.test(chatId)) {
    bindStatus.value = '�?请输入纯数字 Chat ID（不�?Bot Token�?
    bindSuccess.value = false
    return
  }
  
  // 验证长度（Telegram Chat ID 通常�?8-12 位数字）
  if (chatId.length < 5 || chatId.length > 15) {
    bindStatus.value = '�?Chat ID 长度不正�?
    bindSuccess.value = false
    return
  }
  
  try {
    bindStatus.value = '绑定�?..'
    const response = await fetch('https://ai656.top/api/telegram/bind', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userId: FIXED_ADMIN_ID,
        telegramChatId: chatId
      })
    })
    
    const result = await response.json()
    if (result.success) {
      bindStatus.value = '�?绑定成功！离线消息将转发到你�?Telegram'
      bindSuccess.value = true
      console.log('📱 [客服端] Telegram 绑定成功, Chat ID:', chatId)
    } else {
      bindStatus.value = '�?绑定失败: ' + (result.message || '未知错误')
      bindSuccess.value = false
    }
  } catch (error) {
    bindStatus.value = '�?网络错误'
    bindSuccess.value = false
    console.error('�?[客服端] Telegram 绑定失败:', error)
  }
}

const toggleOnline = () => {
  online.value = !online.value
  if (socket.value) {
    socket.value.emit('customer:setAdminStatus', { online: online.value })
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim() || !socket.value) return
  
  const text = newMessage.value.trim()
  
  // 添加本地消息
  messages.value.push({
    id: Date.now(),
    fromAdmin: true,
    text: text,
    timestamp: new Date()
  })
  
  // 发送到服务器（广播给所有用户）
  socket.value.emit('customer:adminReply', {
    conversationId: 'general',
    userId: 'user_001', // 固定发给 user_001
    text: text
  })
  
  newMessage.value = ''
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
})
</script>
