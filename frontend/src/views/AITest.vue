<template>
  <div class="min-h-screen bg-gray-50 pt-24 pb-12">
    <div class="max-w-6xl mx-auto px-4 md:px-6">
      
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">AI 业务测试</h1>
        <p class="text-gray-600">测试 AI Agent API 接口</p>
      </div>

      <!-- WebSocket Connection -->
      <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200 mb-6">
        <h2 class="text-xl font-bold mb-4">WebSocket 连接</h2>
        <div class="flex gap-4">
          <input 
            v-model="aiAddress" 
            placeholder="输入 AI 钱包地址"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
          />
          <button 
            @click="connectWebSocket"
            :disabled="wsConnected"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ wsConnected ? '已连接' : '连接' }}
          </button>
        </div>
        <div v-if="wsConnected" class="mt-2 text-green-600 text-sm">
          ✓ WebSocket 已连接
        </div>
      </div>

      <!-- Query Buttons -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <button 
          @click="queryBalance"
          class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          查询余额
        </button>
        
        <button 
          @click="queryReferrals"
          class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          查询推荐奖励
        </button>
        
        <button 
          @click="queryProducts"
          class="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
        >
          查询商品列表
        </button>
      </div>

      <!-- Results Display -->
      <div v-if="result" class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
        <h3 class="text-lg font-bold mb-4">返回数据</h3>
        <pre class="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm">{{ JSON.stringify(result, null, 2) }}</pre>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6 mt-6">
        <h3 class="text-lg font-bold text-red-600 mb-2">错误</h3>
        <p class="text-red-700">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const aiAddress = ref('')
const wsConnected = ref(false)
const result = ref(null)
const error = ref(null)
let ws = null

// Connect to WebSocket
const connectWebSocket = () => {
  if (!aiAddress.value) {
    error.value = '请输入 AI 钱包地址'
    return
  }
  
  const wsUrl = `ws://localhost:3000/ws/ai/${aiAddress.value}`
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    wsConnected.value = true
    error.value = null
    console.log('WebSocket connected')
  }
  
  ws.onmessage = (event) => {
    result.value = JSON.parse(event.data)
  }
  
  ws.onerror = (err) => {
    error.value = 'WebSocket 连接失败'
    console.error('WebSocket error:', err)
  }
  
  ws.onclose = () => {
    wsConnected.value = false
  }
}

// Query balance via WebSocket
const queryBalance = () => {
  if (!ws || !wsConnected.value) {
    error.value = '请先连接 WebSocket'
    return
  }
  
  ws.send(JSON.stringify({
    type: 'query_balance'
  }))
}

// Query referrals via WebSocket
const queryReferrals = () => {
  if (!ws || !wsConnected.value) {
    error.value = '请先连接 WebSocket'
    return
  }
  
  ws.send(JSON.stringify({
    type: 'query_referrals'
  }))
}

// Query products via HTTP
const queryProducts = async () => {
  try {
    const response = await fetch('http://localhost:3000/api/v1/ai/products?limit=10')
    result.value = await response.json()
    error.value = null
  } catch (err) {
    error.value = err.message
  }
}
</script>
