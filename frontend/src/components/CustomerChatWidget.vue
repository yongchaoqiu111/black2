<template>
  <div class="fixed bottom-6 right-6 z-50">
    <!-- 客服聊天窗口 -->
    <div v-if="isOpen" class="bg-white rounded-lg shadow-2xl w-[380px] h-[520px] flex flex-col border border-gray-200">
      <!-- 头部 -->
      <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
            <i class="fa-solid fa-headset text-lg"></i>
          </div>
          <div>
            <h3 class="font-semibold">在线客服</h3>
            <p class="text-xs opacity-90">
              <span v-if="adminOnline" class="flex items-center">
                <span class="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                客服在线
              </span>
              <span v-else class="flex items-center">
                <span class="w-2 h-2 bg-gray-400 rounded-full mr-1"></span>
                客服离线
              </span>
            </p>
          </div>
        </div>
        <button @click="isOpen = false" class="hover:bg-white hover:bg-opacity-20 rounded-lg p-1.5 transition-colors">
          <i class="fa-solid fa-times"></i>
        </button>
      </div>

      <!-- 消息区域 -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="text-center py-8">
          <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <i class="fa-solid fa-comments text-2xl text-blue-500"></i>
          </div>
          <p class="text-gray-600 text-sm">您好！有什么可以帮助您的？</p>
          <p class="text-gray-400 text-xs mt-1">客服会尽快回复您</p>
        </div>

        <!-- 消息列表 -->
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="[
            'flex',
            message.fromAdmin ? 'justify-start' : 'justify-end'
          ]"
        >
          <div :class="[
            'max-w-[80%] px-4 py-2.5 rounded-2xl text-sm',
            message.fromAdmin 
              ? 'bg-white text-gray-800 border border-gray-200 rounded-bl-md' 
              : 'bg-blue-500 text-white rounded-br-md'
          ]">
            <p class="whitespace-pre-wrap break-words">{{ message.text }}</p>
            <p :class="[
              'text-xs mt-1',
              message.fromAdmin ? 'text-gray-400' : 'text-blue-100'
            ]">
              {{ formatTime(message.timestamp) }}
            </p>
          </div>
        </div>

        <!-- 加载状�?-->
        <div v-if="loading" class="flex justify-start">
          <div class="bg-white border border-gray-200 px-4 py-2.5 rounded-2xl rounded-bl-md">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="p-4 border-t border-gray-200 bg-white">
        <!-- 离线提示 -->
        <div v-if="!adminOnline" class="mb-2 p-2 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-700">
          <i class="fa-solid fa-info-circle mr-1"></i>
          客服当前离线，消息将存储，客服上线后会回复您
        </div>
        
        <div class="flex items-end space-x-2">
          <textarea 
            v-model="newMessage"
            @keydown.enter.exact.prevent="sendMessage"
            rows="1"
            placeholder="输入消息..."
            class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 resize-none text-sm"
            style="min-height: 38px; max-height: 100px;"
          ></textarea>
          <button 
            @click="sendMessage"
            :disabled="!newMessage.trim()"
            class="p-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 浮动按钮 -->
    <button 
      v-if="!isOpen"
      @click="openChat"
      class="w-14 h-14 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-110 flex items-center justify-center relative"
    >
      <i class="fa-solid fa-comments text-xl"></i>
      <!-- 未读消息徽章 -->
      <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
        {{ unreadCount > 9 ? '9+' : unreadCount }}
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getSocket } from '@/utils/websocket'
import { io } from 'socket.io-client'

const authStore = useAuthStore()
let socket = null

const isOpen = ref(false)
const newMessage = ref('')
const messages = ref([])
const adminOnline = ref(false)
const unreadCount = ref(0)
const loading = ref(false)
const messagesContainer = ref(null)

// 打开聊天窗口
const openChat = () => {
  isOpen.value = true
  unreadCount.value = 0
  scrollToBottom()
  
  // 创建独立 Socket 连接
  if (!socket) {
    const socketUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:3000'
    socket = io(socketUrl, {
      transports: ['websocket'],
      autoConnect: true,
      auth: { token: authStore.token }
    })
    
    // 注册事件监听
    socket.on('customer:newMessage', (data) => {
      console.log('📨 [客服] 收到新消�?', data)
      if (data.message && data.message.fromAdmin) {
        messages.value.push({
          id: data.message.id,
          fromAdmin: true,
          text: data.message.text,
          timestamp: data.message.timestamp
        })
        if (!isOpen.value) {
          unreadCount.value++
        } else {
          scrollToBottom()
        }
      }
    })
    
    socket.on('customer:messageSent', (data) => {
      console.log('�?[客服] 消息发送成�?', data)
      loading.value = false
    })
    
    socket.on('customer:adminStatus', (data) => {
      adminOnline.value = data.online
      console.log('👨�?[客服] 客服状�?', data.online ? '在线' : '离线')
    })
  }
  
  // 注册用户到客服系�?
  if (authStore.user) {
    socket.emit('customer:register', {
      userId: authStore.user.id,
      email: authStore.user.email
    })
  }
}

// 发送消�?
const sendMessage = () => {
  if (!newMessage.value.trim() || !authStore.user || !socket) return
  
  const text = newMessage.value.trim()
  
  // 添加本地消息
  messages.value.push({
    id: Date.now(),
    fromAdmin: false,
    text: text,
    timestamp: new Date()
  })
  
  // 发送到服务�?
  socket.emit('customer:sendMessage', {
    userId: authStore.user.id,
    text: text
  })
  
  newMessage.value = ''
  scrollToBottom()
}

// 滚动到底�?
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 格式化时�?
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 监听新消�?
const handleOpenChat = () => {
  openChat()
}

onMounted(() => {
  // 监听打开客服窗口的事�?
  window.addEventListener('openCustomerChat', handleOpenChat)
})

onUnmounted(() => {
  window.removeEventListener('openCustomerChat', handleOpenChat)
  if (socket) {
    socket.disconnect()
    socket = null
  }
})
</script>
