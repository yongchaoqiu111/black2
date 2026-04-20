<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-6">📱 用户�?(固定ID: user_001)</h1>
      
      <div class="bg-white rounded-lg shadow p-6 mb-4">
        <div class="flex items-center justify-between mb-4">
          <span class="text-lg font-semibold">客服状�?</span>
          <span :class="adminOnline ? 'text-green-500' : 'text-red-500'">
            {{ adminOnline ? '在线' : '离线' }}
          </span>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6 h-96 overflow-y-auto mb-4" ref="messageContainer">
        <div v-for="msg in messages" :key="msg.id" 
             :class="['mb-2', msg.fromAdmin ? 'text-right' : 'text-left']">
          <div :class="['inline-block px-4 py-2 rounded-lg max-w-xs', 
                       msg.fromAdmin ? 'bg-blue-500 text-white' : 'bg-gray-200']">
            {{ msg.text }}
          </div>
        </div>
      </div>

      <div class="flex gap-2">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage"
          placeholder="输入消息..."
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
const adminOnline = ref(false)
const messageContainer = ref(null)

const FIXED_USER_ID = 'user_001'

onMounted(() => {
  // 连接 WebSocket
  socket.value = io('https://ai656.top', {
    transports: ['websocket'],
    auth: { token: 'test_token' }
  })

  // 注册用户
  socket.value.on('connect', () => {
    console.log('�?[用户端] 已连�?)
    
    // 注册到客服系�?
    socket.value.emit('customer:register', {
      userId: FIXED_USER_ID,
      email: 'user001@test.com'
    })
  })

  // 监听客服状�?
  socket.value.on('customer:adminStatus', (data) => {
    adminOnline.value = data.online
    console.log('👨‍�?[用户端] 客服状�?', data.online ? '在线' : '离线')
  })

  // 监听新消�?
  socket.value.on('customer:newMessage', (data) => {
    if (data.message && data.message.fromAdmin) {
      messages.value.push({
        id: data.message.id,
        fromAdmin: true,
        text: data.message.text,
        timestamp: new Date()
      })
      scrollToBottom()
    }
  })

  // 监听发送确�?
  socket.value.on('customer:messageSent', (data) => {
    console.log('�?[用户端] 消息发送成�?', data)
  })
})

const sendMessage = () => {
  if (!newMessage.value.trim() || !socket.value) return
  
  const text = newMessage.value.trim()
  
  // 添加本地消息
  messages.value.push({
    id: Date.now(),
    fromAdmin: false,
    text: text,
    timestamp: new Date()
  })
  
  // 发送到服务�?
  socket.value.emit('customer:sendMessage', {
    userId: FIXED_USER_ID,
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
