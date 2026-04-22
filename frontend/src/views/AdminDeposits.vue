<template>
  <div class="min-h-screen bg-gray-50 pt-24 pb-12">
    <div class="max-w-6xl mx-auto px-4 md:px-6">
      
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">充值管理</h1>
        <p class="text-gray-600">手动充值、批量充值、查看充值记录</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <div class="text-sm text-gray-600 mb-1">总记录数</div>
          <div class="text-2xl font-bold text-blue-600">{{ deposits.length }}</div>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <div class="text-sm text-gray-600 mb-1">已确认</div>
          <div class="text-2xl font-bold text-green-600">{{ confirmedCount }}</div>
        </div>
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <div class="text-sm text-gray-600 mb-1">总金额</div>
          <div class="text-2xl font-bold text-purple-600">${{ totalAmount.toFixed(2) }}</div>
        </div>
      </div>

      <!-- Manual Deposit Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Single Deposit -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">
            <i class="fa-solid fa-plus-circle text-green-600 mr-2"></i>
            手动充值（单个用户）
          </h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">用户地址 *</label>
              <input 
                v-model="manualForm.userAddress"
                type="text"
                placeholder="0x123..."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">充值金额 (USDT) *</label>
              <input 
                v-model.number="manualForm.amount"
                type="number"
                step="0.01"
                min="0"
                placeholder="100.00"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">备注</label>
              <input 
                v-model="manualForm.reason"
                type="text"
                placeholder="活动奖励 / 测试充值 / 客服补偿"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <button 
              @click="handleManualDeposit"
              :disabled="manualLoading"
              class="w-full py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              <span v-if="!manualLoading">确认充值</span>
              <span v-else>充值中...</span>
            </button>
          </div>
        </div>

        <!-- Batch Deposit -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h3 class="text-lg font-bold text-gray-900 mb-4">
            <i class="fa-solid fa-layer-group text-purple-600 mr-2"></i>
            批量充值（AI 多层销售测试）
          </h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">JSON 格式充值列表 *</label>
              <textarea 
                v-model="batchForm.jsonData"
                rows="8"
                placeholder='[
  {"user_address": "0x123...", "amount": 1000, "reason": "AI销售奖励"},
  {"user_address": "0x456...", "amount": 2000, "reason": "测试充值"}
]'
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-xs"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">支持批量输入，每笔充值包含 user_address、amount、reason</p>
            </div>
            
            <button 
              @click="handleBatchDeposit"
              :disabled="batchLoading"
              class="w-full py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              <span v-if="!batchLoading">批量充值</span>
              <span v-else>处理中...</span>
            </button>
            
            <div v-if="batchResult" class="bg-gray-50 p-4 rounded-lg">
              <div class="text-sm font-medium text-gray-900 mb-2">处理结果：</div>
              <div class="text-sm text-gray-600">成功: {{ batchResult.successful?.length || 0 }} 笔</div>
              <div class="text-sm text-gray-600">失败: {{ batchResult.failed?.length || 0 }} 笔</div>
              <div class="text-sm text-purple-600 font-semibold mt-1">总金额: ${{ batchResult.total_amount?.toFixed(2) || 0 }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Deposits List -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">充值记录</h2>
          <button 
            @click="loadDeposits"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
          >
            <i class="fa-solid fa-rotate-right mr-1"></i> 刷新
          </button>
        </div>

        <div v-if="loading" class="p-12 text-center">
          <i class="fa-solid fa-spinner fa-spin text-3xl text-purple-600"></i>
          <p class="text-gray-600 mt-4">加载中...</p>
        </div>

        <div v-else-if="deposits.length === 0" class="p-12 text-center">
          <i class="fa-solid fa-inbox text-6xl text-gray-300 mb-4"></i>
          <p class="text-gray-600">暂无充值记录</p>
        </div>

        <div v-else class="divide-y divide-gray-200 max-h-96 overflow-y-auto">
          <div 
            v-for="deposit in deposits" 
            :key="deposit.id"
            class="p-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <div 
                  :class="[
                    'w-12 h-12 rounded-full flex items-center justify-center',
                    deposit.status === 'confirmed' ? 'bg-green-100' : 'bg-yellow-100'
                  ]"
                >
                  <i 
                    :class="[
                      'text-xl',
                      deposit.status === 'confirmed' ? 'fa-solid fa-check text-green-600' : 'fa-solid fa-clock text-yellow-600'
                    ]"
                  ></i>
                </div>
                
                <div>
                  <div class="font-semibold text-gray-900">充值申请 #{{ deposit.id }}</div>
                  <div class="text-sm text-gray-600 mt-1">
                    <span class="font-mono">{{ deposit.user_address?.substring(0, 10) }}...{{ deposit.user_address?.substring(deposit.user_address.length - 8) }}</span>
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    TX: <span class="font-mono">{{ (deposit.tx_hash || '').substring(0, 16) }}...</span>
                  </div>
                  <div v-if="deposit.notes" class="text-xs text-blue-600 mt-1">
                    备注: {{ deposit.notes }}
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    {{ formatDate(deposit.created_at) }}
                  </div>
                </div>
              </div>
              
              <div class="text-right">
                <div class="text-lg font-bold text-purple-600">${{ deposit.amount?.toFixed(2) }}</div>
                <div class="text-sm mt-2">
                  <span 
                    :class="[
                      'inline-block px-3 py-1 rounded-full text-xs font-medium',
                      deposit.status === 'confirmed' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-yellow-100 text-yellow-700'
                    ]"
                  >
                    {{ deposit.status === 'confirmed' ? '已确认' : '待审核' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const deposits = ref([])
const loading = ref(true)

// 手动充值表单
const manualForm = ref({
  userAddress: '',
  amount: null,
  reason: ''
})
const manualLoading = ref(false)

// 批量充值表单
const batchForm = ref({
  jsonData: ''
})
const batchLoading = ref(false)
const batchResult = ref(null)

const confirmedCount = computed(() => {
  return deposits.value.filter(d => d.status === 'confirmed').length
})

const totalAmount = computed(() => {
  return deposits.value.reduce((sum, d) => sum + (d.amount || 0), 0)
})

const loadDeposits = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/v1/admin/deposits')
    const data = await response.json()
    
    if (response.ok && data.deposits) {
      deposits.value = data.deposits
    }
  } catch (error) {
    console.error('Failed to load deposits:', error)
  } finally {
    loading.value = false
  }
}

// 手动充值
const handleManualDeposit = async () => {
  if (!manualForm.value.userAddress || !manualForm.value.amount) {
    alert('请填写用户地址和充值金额')
    return
  }
  
  if (!confirm(`确认为 ${manualForm.value.userAddress.substring(0, 10)}... 充值 $${manualForm.value.amount} ?`)) {
    return
  }
  
  manualLoading.value = true
  
  try {
    const response = await fetch('/api/v1/admin/deposits/manual', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_address: manualForm.value.userAddress,
        amount: manualForm.value.amount,
        reason: manualForm.value.reason || '手动充值'
      })
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || '充值失败')
    }
    
    alert(`充值成功！金额: $${data.amount}`)
    
    // 清空表单
    manualForm.value.userAddress = ''
    manualForm.value.amount = null
    manualForm.value.reason = ''
    
    // 刷新列表
    loadDeposits()
  } catch (error) {
    console.error('Manual deposit failed:', error)
    alert(error.message || '充值失败，请重试')
  } finally {
    manualLoading.value = false
  }
}

// 批量充值
const handleBatchDeposit = async () => {
  if (!batchForm.value.jsonData.trim()) {
    alert('请填写充值列表 JSON')
    return
  }
  
  let depositsList
  try {
    depositsList = JSON.parse(batchForm.value.jsonData)
    if (!Array.isArray(depositsList)) {
      throw new Error('JSON 必须是一个数组')
    }
  } catch (error) {
    alert('JSON 格式错误: ' + error.message)
    return
  }
  
  if (!confirm(`确认批量充值 ${depositsList.length} 笔？`)) {
    return
  }
  
  batchLoading.value = true
  batchResult.value = null
  
  try {
    const response = await fetch('/api/v1/admin/deposits/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deposits: depositsList })
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || '批量充值失败')
    }
    
    batchResult.value = data
    
    alert(`批量充值完成！成功 ${data.successful.length} 笔，失败 ${data.failed.length} 笔`)
    
    // 清空表单
    batchForm.value.jsonData = ''
    
    // 刷新列表
    loadDeposits()
  } catch (error) {
    console.error('Batch deposit failed:', error)
    alert(error.message || '批量充值失败，请重试')
  } finally {
    batchLoading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadDeposits()
})
</script>
