<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <i class="fa-solid fa-headset text-white text-lg"></i>
            </div>
            <h1 class="text-xl font-bold text-gray-900">客服管理中心</h1>
          </div>
          
          <div class="flex items-center space-x-4">
            <!-- 在线状态切�?-->
            <button 
              @click="toggleOnlineStatus"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-colors',
                adminOnline 
                  ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              ]"
            >
              <span v-if="adminOnline" class="flex items-center">
                <span class="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                在线
              </span>
              <span v-else class="flex items-center">
                <span class="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                离线
              </span>
            </button>
            
            <a href="/" class="text-gray-600 hover:text-gray-900">
              <i class="fa-solid fa-arrow-left mr-1"></i>
              返回首页
            </a>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-12 gap-6">
        <!-- 左侧：对话列�?-->
        <div class="col-span-4 bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="p-4 border-b border-gray-200">
            <h2 class="font-semibold text-gray-900">对话列表</h2>
            <p class="text-sm text-gray-500 mt-1">{{ conversations.length }} 个对�?/p>
          </div>
          
          <div class="overflow-y-auto" style="max-height: calc(100vh - 280px);">
            <div v-if="conversations.length === 0" class="p-8 text-center text-gray-500">
              <i class="fa-solid fa-inbox text-4xl mb-3 text-gray-300"></i>
              <p>暂无对话</p>
            </div>
            
            <div 
              v-for="conversation in conversations" 
              :key="conversation.id"
              @click="selectConversation(conversation)"
              :class="[
                'p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors',
                selectedConversation?.id === conversation.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
              ]"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2">
                    <h3 class="font-medium text-gray-900 truncate">{{ conversation.userEmail }}</h3>
                    <span v-if="conversation.unreadCount > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
                      {{ conversation.unreadCount }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-500 mt-1 truncate">
                    {{ getLastMessage(conversation) }}
                  </p>
                  <p class="text-xs text-gray-400 mt-1">
                    {{ formatTime(conversation.lastMessageAt) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：聊天区�?-->
        <div class="col-span-8 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col" style="height: calc(100vh - 200px);">
          <div v-if="!selectedConversation" class="flex-1 flex items-center justify-center text-gray-400">
            <div class="text-center">
              <i class="fa-solid fa-comments text-6xl mb-4 text-gray-300"></i>
              <p class="text-lg">选择一个对话开始聊�?/p>
            </div>
          </div>

          <template v-else>
            <!-- 聊天头部 -->
            <div class="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-blue-100">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                    {{ selectedConversation.userEmail.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <h3 class="font-semibold text-gray-900">{{ selectedConversation.userEmail }}</h3>
                    <p class="text-sm text-gray-600">
                      <span v-if="isUserOnline(selectedConversation.userId)" class="text-green-600">
                        <i class="fa-solid fa-circle text-xs mr-1"></i>在线
                      </span>
                      <span v-else class="text-gray-500">
                        <i class="fa-solid fa-circle text-xs mr-1"></i>离线
                      </span>
                      <span v-if="selectedConversation.telegramChatId" class="ml-2 text-blue-600">
                        <i class="fa-brands fa-telegram mr-1"></i>已绑�?Telegram
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 消息区域 -->
            <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
              <div v-if="currentMessages.length === 0" class="text-center py-8 text-gray-500">
                <i class="fa-solid fa-comment-dots text-4xl mb-3 text-gray-300"></i>
                <p>暂无消息，开始对话吧�?/p>
              </div>

              <div 
                v-for="message in currentMessages" 
                :key="message.id"
                :class="[
                  'flex',
                  message.fromAdmin ? 'justify-end' : 'justify-start'
                ]"
              >
                <div :class="[
                  'max-w-[70%] px-4 py-2.5 rounded-2xl text-sm',
                  message.fromAdmin 
                    ? 'bg-blue-500 text-white rounded-br-md' 
                    : 'bg-white text-gray-800 border border-gray-200 rounded-bl-md'
                ]">
                  <p class="whitespace-pre-wrap break-words">{{ message.text }}</p>
                  <p :class="[
                    'text-xs mt-1',
                    message.fromAdmin ? 'text-blue-100' : 'text-gray-400'
                  ]">
                    {{ formatTime(message.timestamp) }}
                  </p>
                </div>
              </div>
            </div>

            <!-- 输入区域 -->
            <div class="p-4 border-t border-gray-200 bg-white">
              <!-- 离线用户提示 -->
              <div v-if="!isUserOnline(selectedConversation.userId) && selectedConversation.telegramChatId" class="mb-2 p-2 bg-green-50 border border-green-200 rounded-lg text-xs text-green-700">
                <i class="fa-brands fa-telegram mr-1"></i>
                用户已离线，消息将转发到 Telegram
              </div>
              
              <div class="flex items-end space-x-2">
                <textarea 
                  v-model="newMessage"
                  @keydown.enter.exact.prevent="sendMessage"
                  rows="1"
                  placeholder="输入回复..."
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
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { io } from 'socket.io-client'

let socket = null

const adminOnline = ref(false)
const conversations = ref([])
const selectedConversation = ref(null)
const messages = ref({}) // conversationId -> messages[]
const newMessage = ref('')
const messagesContainer = ref(null)

// 当前选中对话的消�?
const currentMessages = computed(() => {
  if (!selectedConversation.value) return []
  return messages.value[selectedConversation.value.id] || []
})

// 选择对话
const selectConversation = (conversation) => {
  selectedConversation.value = conversation
  
  // 如果还没有加载该对话的消息，请求历史消息
  if (!messages.value[conversation.id]) {
    loadConversationHistory(conversation.id)
  }
  
  // 清除未读�?
  conversation.unreadCount = 0
  
  scrollToBottom()
}

// 加载对话历史
const loadConversationHistory = (conversationId) => {
  if (socket) {
    socket.emit('customer:getHistory', { conversationId })
  }
}

// 发送消�?
const sendMessage = () => {
  if (!newMessage.value.trim() || !selectedConversation.value || !socket) return
  
  const text = newMessage.value.trim()
  
  socket.emit('customer:adminReply', {
    conversationId: selectedConversation.value.id,
    userId: selectedConversation.value.userId,
    text: text
  })
  
  // 添加本地消息
  if (!messages.value[selectedConversation.value.id]) {
    messages.value[selectedConversation.value.id] = []
  }
  
  messages.value[selectedConversation.value.id].push({
    id: Date.now(),
    fromAdmin: true,
    text: text,
    timestamp: new Date()
  })
  
  newMessage.value = ''
  scrollToBottom()
}

// 切换在线状�?
const toggleOnlineStatus = () => {
  adminOnline.value = !adminOnline.value
  if (socket) {
    socket.emit('customer:setAdminStatus', { online: adminOnline.value })
  }
}

// 检查用户是否在�?
const isUserOnline = (userId) => {
  // 这里可以从后端获取在线用户列�?
  // 暂时简单实�?
  return false
}

// 获取最后一条消�?
const getLastMessage = (conversation) => {
  const msgs = messages.value[conversation.id]
  if (msgs && msgs.length > 0) {
    return msgs[msgs.length - 1].text
  }
  return '暂无消息'
}

// 格式化时�?
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // 如果是今天，只显示时�?
  if (diff < 24 * 60 * 60 * 1000 && date.getDate() === now.getDate()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  
  // 否则显示日期
  return date.toLocaleDateString()
}

// 滚动到底�?
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// WebSocket 事件监听
onMounted(() => {
  // 初始�?Socket（不需�?token，直接连接）
  const socketUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:3000'
  socket = io(socketUrl, {
    transports: ['websocket'],
    autoConnect: true,
    query: { admin: 'true' }
  })
  
  // 监听新对�?
  socket.on('customer:newConversation', (data) => {
    console.log('📨 [客服后台] 新对�?', data)
    conversations.value.unshift(data.conversation)
  })
  
  // 监听新消�?
  socket.on('customer:newMessage', (data) => {
    console.log('💬 [客服后台] 新消�?', data)
    
    const { conversationId, message } = data
    
    // 更新对话列表
    const conv = conversations.value.find(c => c.id === conversationId)
    if (conv) {
      conv.lastMessageAt = message.timestamp
      if (selectedConversation.value?.id !== conversationId) {
        conv.unreadCount = (conv.unreadCount || 0) + 1
      }
      
      // 移到最前面
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      conversations.value.unshift(conv)
    }
    
    // 添加消息
    if (!messages.value[conversationId]) {
      messages.value[conversationId] = []
    }
    messages.value[conversationId].push(message)
    
    // 如果是当前选中的对话，滚动到底�?
    if (selectedConversation.value?.id === conversationId) {
      scrollToBottom()
    }
  })
  
  // 监听对话历史
  socket.on('customer:conversationHistory', (data) => {
    console.log('📜 [客服后台] 对话历史:', data)
    messages.value[data.conversationId] = data.messages
    scrollToBottom()
  })
  
  // 监听管理员状态确�?
  socket.on('customer:adminStatusConfirmed', (data) => {
    console.log('�?[客服后台] 管理员状态已设置:', data)
  })
  
  // 监听客服在线状态广�?
  socket.on('customer:adminStatus', ({ online }) => {
    console.log('📡 [客服后台] 在线状态更�?', online)
    adminOnline.value = online
  })
  
  // 自动设置为在�?
  setTimeout(() => {
    socket.emit('customer:registerAdmin')
    adminOnline.value = true
    socket.emit('customer:setAdminStatus', { online: true })
  }, 500)
})

onUnmounted(() => {
  if (socket) {
    socket.off('customer:newConversation')
    socket.off('customer:newMessage')
    socket.off('customer:conversationHistory')
    socket.off('customer:adminStatusConfirmed')
    socket.off('customer:adminStatus')
    socket.disconnect()
  }
})
</script>
