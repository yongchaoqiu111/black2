<template>
  <div class="min-h-screen bg-gray-50">
    
    <div class="max-w-7xl mx-auto px-4 md:px-6 py-6 h-[calc(100vh-64px)]">
      <div class="bg-white rounded-lg shadow-sm overflow-hidden h-full flex">
        <!-- Left Sidebar - Conversations List -->
        <div :class="[
          'border-r border-gray-200 bg-white flex-shrink-0 transition-all duration-300',
          showConversationList ? 'w-full md:w-80' : 'hidden md:block md:w-80'
        ]">
          <!-- Header -->
          <div class="p-4 border-b border-gray-200">
            <h2 class="text-lg font-bold text-gray-900 mb-3">Messages</h2>
            <div class="relative">
              <input 
                type="text" 
                v-model="searchQuery"
                placeholder="Search conversations..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-sm"
              />
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <!-- Conversations List -->
          <div class="overflow-y-auto flex-1" style="height: calc(100% - 140px);">
            <div 
              v-for="conversation in filteredConversations" 
              :key="conversation.id"
              @click="selectConversation(conversation)"
              :class="[
                'p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors',
                selectedConversation?.id === conversation.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
              ]"
            >
              <div class="flex items-start space-x-3">
                <!-- Avatar -->
                <div class="relative flex-shrink-0">
                  <div class="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-400"></div>
                  <div v-if="conversation.online" class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
                </div>

                <!-- Conversation Info -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between mb-1">
                    <h3 class="font-semibold text-gray-900 text-sm truncate">{{ conversation.name }}</h3>
                    <span class="text-xs text-gray-500">{{ formatTime(conversation.lastMessageTime) }}</span>
                  </div>
                  <p class="text-sm text-gray-600 truncate">{{ conversation.lastMessage }}</p>
                  <div v-if="conversation.unreadCount > 0" class="mt-1">
                    <span class="inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-white bg-blue-500 rounded-full">
                      {{ conversation.unreadCount }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="filteredConversations.length === 0" class="p-8 text-center">
              <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p class="text-gray-500 text-sm">No conversations found</p>
            </div>
          </div>

          <!-- 官方客服入口（固定在底部�?-->
          <div class="border-t border-gray-200 bg-gradient-to-r from-blue-500 to-blue-600 p-4 cursor-pointer hover:from-blue-600 hover:to-blue-700 transition-all" @click="openOfficialSupport">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fa-solid fa-headset text-white text-lg"></i>
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-white text-sm">官方客服</h3>
                <p class="text-xs text-blue-100">
                  <span v-if="adminOnline" class="flex items-center">
                    <span class="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                    在线 - 点击聊天
                  </span>
                  <span v-else class="flex items-center">
                    <span class="w-2 h-2 bg-gray-300 rounded-full mr-1"></span>
                    离线 - 留言将稍后回�?
                  </span>
                </p>
              </div>
              <svg class="w-5 h-5 text-white flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Right Side - Chat Area -->
        <div :class="[
          'flex-1 flex flex-col',
          !selectedConversation && 'hidden md:flex'
        ]">
          <!-- Chat Header -->
          <div v-if="selectedConversation" class="p-4 border-b border-gray-200 flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <!-- Back Button (Mobile) -->
              <button 
                @click="showConversationList = true"
                class="md:hidden p-2 hover:bg-gray-100 rounded-lg"
              >
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400"></div>
              <div>
                <h3 class="font-semibold text-gray-900">{{ selectedConversation.name }}</h3>
                <p class="text-xs text-gray-500">
                  <span v-if="typingUsers.size > 0" class="text-blue-500 animate-pulse">
                    正在输入...
                  </span>
                  <span v-else>
                    {{ selectedConversation.online ? 'Online' : 'Last seen ' + formatTime(selectedConversation.lastSeen) }}
                  </span>
                </p>
              </div>
            </div>

            <div class="flex items-center space-x-2">
              <button class="p-2 hover:bg-gray-100 rounded-lg" title="View Profile">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </button>
              <button class="p-2 hover:bg-gray-100 rounded-lg" title="More Options">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Messages Area -->
          <div v-if="selectedConversation" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            <div 
              v-for="message in selectedConversation.messages" 
              :key="message.id"
              :class="[
                'flex',
                message.isMe ? 'justify-end' : 'justify-start'
              ]"
            >
              <div :class="[
                'max-w-[75%] md:max-w-[60%]',
                message.isMe ? 'order-2' : 'order-1'
              ]">
                <!-- Message Bubble -->
                <div :class="[
                  'px-4 py-2.5 rounded-2xl relative group',
                  message.isMe 
                    ? 'bg-blue-500 text-white rounded-br-md' 
                    : 'bg-white text-gray-900 border border-gray-200 rounded-bl-md'
                ]">
                  <!-- Show original or translated text -->
                  <p class="text-sm whitespace-pre-wrap break-words">
                    {{ message.showTranslation && message.translatedText ? message.translatedText : message.text }}
                  </p>
                  
                  <!-- Translate Button (only for received messages) -->
                  <button 
                    v-if="!message.isMe && locale !== 'en'"
                    @click="toggleTranslation(message)"
                    :disabled="message.translating"
                    class="absolute -top-2 -right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white border border-gray-300 rounded-full p-1.5 shadow-md hover:bg-gray-50"
                    :title="message.showTranslation ? 'Show Original' : 'Translate to English'"
                  >
                    <i v-if="message.translating" class="fa-solid fa-spinner fa-spin text-xs text-blue-600"></i>
                    <i v-else class="fa-solid fa-language text-xs text-gray-600"></i>
                  </button>
                </div>
                
                <!-- Timestamp -->
                <p :class="[
                  'text-xs mt-1',
                  message.isMe ? 'text-right text-gray-500' : 'text-left text-gray-500'
                ]">
                  {{ formatMessageTime(message.timestamp) }}
                  <span v-if="message.isMe && message.read" class="ml-1">✓✓</span>
                </p>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="flex-1 flex items-center justify-center bg-gray-50">
            <div class="text-center">
              <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p class="text-gray-500 text-lg mb-2">Select a conversation</p>
              <p class="text-gray-400 text-sm">Choose a conversation from the list to start chatting</p>
            </div>
          </div>

          <!-- Message Input -->
          <div v-if="selectedConversation" class="p-4 border-t border-gray-200 bg-white">
            <!-- 离线提示 -->
            <div v-if="!selectedConversation.online" class="mb-3 p-2 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-700">
              <i class="fa-solid fa-info-circle mr-1"></i>
              对方当前离线，消息将转发到其 Telegram/飞书
            </div>
            
            <div class="flex items-end space-x-3">
              <!-- Attach Button -->
              <button class="p-2 hover:bg-gray-100 rounded-lg flex-shrink-0">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
              </button>

              <!-- Text Input -->
              <div class="flex-1">
                <textarea 
                  v-model="newMessage"
                  @keydown.enter.exact.prevent="sendMessage"
                  rows="1"
                  placeholder="Type a message..."
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 resize-none text-sm"
                  style="min-height: 42px; max-height: 120px;"
                ></textarea>
              </div>

              <!-- Send Button -->
              <button 
                @click="sendMessage"
                :disabled="!newMessage.trim()"
                class="p-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { translationService } from '@/utils/translation'
import { 
  initSocket, 
  disconnectSocket,
  joinChatRoom, 
  leaveChatRoom,
  sendChatMessage,
  onNewMessage,
  onTyping,
  sendTyping,
  onAdminStatus,
  registerCustomer
} from '@/utils/websocket'
// Navbar is now in Layout component

const route = useRoute()
const { locale } = useI18n()
const authStore = useAuthStore()
const searchQuery = ref('')
const selectedConversation = ref(null)
const newMessage = ref('')
const showConversationList = ref(true)
const isConnected = ref(false)
const typingUsers = ref(new Set())
const adminOnline = ref(false)

// Mock conversations data (后续替换�?API 加载)
const conversations = ref([
  {
    id: 1,
    name: 'Marketing Pro Studio',
    online: true,
    lastMessage: 'Thanks for your interest! Let me know if you have any questions.',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 5),
    lastSeen: new Date(),
    unreadCount: 2,
    messages: [
      { id: 1, text: 'Hi! I\'m interested in your Marketing Automation Suite.', isMe: false, timestamp: new Date(Date.now() - 1000 * 60 * 30), read: true },
      { id: 2, text: 'Hello! Great to hear from you. What specific features are you looking for?', isMe: true, timestamp: new Date(Date.now() - 1000 * 60 * 25), read: true },
      { id: 3, text: 'I need something that can handle email campaigns and social media scheduling.', isMe: false, timestamp: new Date(Date.now() - 1000 * 60 * 20), read: true },
      { id: 4, text: 'Perfect! Our suite includes both of those features plus analytics dashboard and CRM integration.', isMe: true, timestamp: new Date(Date.now() - 1000 * 60 * 15), read: true },
      { id: 5, text: 'That sounds great! Do you offer any discounts for annual subscriptions?', isMe: false, timestamp: new Date(Date.now() - 1000 * 60 * 10), read: true },
      { id: 6, text: 'Yes! We offer 20% off for annual plans. Would you like me to send you more details?', isMe: true, timestamp: new Date(Date.now() - 1000 * 60 * 5), read: false }
    ]
  },
  {
    id: 2,
    name: 'WebDesign Master',
    online: false,
    lastMessage: 'The template is fully customizable.',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 2),
    lastSeen: new Date(Date.now() - 1000 * 60 * 60),
    unreadCount: 0,
    messages: [
      { id: 1, text: 'Is this template responsive?', isMe: false, timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3), read: true },
      { id: 2, text: 'Yes, it\'s fully responsive and works on all devices.', isMe: true, timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2.5), read: true },
      { id: 3, text: 'Great! Can I customize the colors?', isMe: false, timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), read: true }
    ]
  },
  {
    id: 3,
    name: 'Code Ninja',
    online: true,
    lastMessage: 'I\'ll send you the documentation shortly.',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 5),
    lastSeen: new Date(),
    unreadCount: 1,
    messages: [
      { id: 1, text: 'How do I install this software?', isMe: false, timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6), read: true },
      { id: 2, text: 'It\'s very simple. Just download the package and run the installer.', isMe: true, timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5.5), read: true },
      { id: 3, text: 'Okay, I\'ll send you the documentation shortly.', isMe: true, timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), read: false }
    ]
  }
])

const filteredConversations = computed(() => {
  if (!searchQuery.value) return conversations.value
  return conversations.value.filter(conv => 
    conv.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const selectConversation = (conversation) => {
  // 离开之前的聊天室
  if (selectedConversation.value) {
    leaveChatRoom(selectedConversation.value.id)
  }
  
  selectedConversation.value = conversation
  conversation.unreadCount = 0
  showConversationList.value = false
  
  // 加入新的聊天�?
  joinChatRoom(conversation.id)
  
  // Scroll to bottom of messages
  setTimeout(() => {
    const messagesContainer = document.querySelector('.overflow-y-auto')
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight
    }
  }, 100)
}

const sendMessage = () => {
  if (!newMessage.value.trim() || !selectedConversation.value) return
  
  // 通过 WebSocket 发送消�?
  sendChatMessage({
    roomId: selectedConversation.value.id,
    text: newMessage.value
  })
  
  // 本地立即显示（乐观更新）
  const message = {
    id: Date.now(),
    text: newMessage.value,
    isMe: true,
    timestamp: new Date(),
    read: false
  }
  
  selectedConversation.value.messages.push(message)
  selectedConversation.value.lastMessage = newMessage.value
  selectedConversation.value.lastMessageTime = new Date()
  
  newMessage.value = ''
  
  // 取消输入状�?
  sendTyping(selectedConversation.value.id, false)
}

const formatTime = (date) => {
  const now = new Date()
  const diff = now - date
  
  if (diff < 1000 * 60) return 'Just now'
  if (diff < 1000 * 60 * 60) return `${Math.floor(diff / (1000 * 60))}m ago`
  if (diff < 1000 * 60 * 60 * 24) return `${Math.floor(diff / (1000 * 60 * 60))}h ago`
  return date.toLocaleDateString()
}

const formatMessageTime = (date) => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Toggle translation for a message
const toggleTranslation = async (message) => {
  // If already showing translation, switch back to original
  if (message.showTranslation) {
    message.showTranslation = false
    return
  }

  // If already has cached translation, use it
  if (message.translatedText) {
    message.showTranslation = true
    return
  }

  // Start translation
  message.translating = true
  
  try {
    // Use translation service with auto-failover
    const translatedText = await translationService.translate(
      message.text,
      'auto',  // Auto-detect source language
      'en'     // Target language (English)
    )
    
    message.translatedText = translatedText
    message.showTranslation = true
  } catch (error) {
    console.error('Translation failed:', error)
    alert('Translation service is currently unavailable. Please try again later.')
  } finally {
    message.translating = false
  }
}

// 打开官方客服聊天
const openOfficialSupport = () => {
  if (authStore.user) {
    registerCustomer({
      userId: authStore.user.id,
      email: authStore.user.email
    })
  }
  
  // 触发全局事件，打开客服窗口
  window.dispatchEvent(new CustomEvent('openCustomerChat'))
}

// Auto-select conversation if coming from product detail page
onMounted(() => {
  // WebSocket 已在 App.vue 全局初始�?
  isConnected.value = true
  
  // 监听客服在线状�?
  onAdminStatus((data) => {
    adminOnline.value = data.online
    console.log('👨‍�?[聊天页] 客服状�?', data.online ? '在线' : '离线')
  })
  
  // 监听新消�?
  onNewMessage((data) => {
      console.log('📨 收到新消�?', data)
      
      // 找到对应的会�?
      const conversation = conversations.value.find(c => c.id === data.roomId)
      if (conversation) {
        // 添加消息
        conversation.messages.push({
          id: data.id,
          text: data.text,
          isMe: false,
          timestamp: new Date(data.timestamp),
          read: true
        })
        
        // 更新最后一条消�?
        conversation.lastMessage = data.text
        conversation.lastMessageTime = new Date(data.timestamp)
        
        // 如果当前不在该会话，增加未读�?
        if (selectedConversation.value?.id !== data.roomId) {
          conversation.unreadCount++
        }
      }
    })
    
    // 监听输入状�?
    onTyping((data) => {
      if (data.isTyping) {
        typingUsers.value.add(data.userId)
      } else {
        typingUsers.value.delete(data.userId)
      }
    })
  
  const { seller, productId } = route.query
  if (seller) {
    // Find or create conversation with this seller
    const existingConv = conversations.value.find(c => c.name === seller)
    if (existingConv) {
      selectConversation(existingConv)
    }
  }
})

// 组件卸载时离开聊天室（不断开 WebSocket�?
onUnmounted(() => {
  if (selectedConversation.value) {
    leaveChatRoom(selectedConversation.value.id)
  }
})
</script>
