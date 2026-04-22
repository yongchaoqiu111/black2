<template>
  <div class="min-h-screen bg-gray-50 pt-24 pb-12">
    <div class="max-w-6xl mx-auto px-4 md:px-6">
      
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">AI 钱包</h1>
        <p class="text-gray-600">管理您的 AI 代理收益和推荐奖励</p>
      </div>

      <!-- Wallet Content -->
      <div class="space-y-6">
        
        <!-- AI Wallet Card -->
        <div class="bg-gradient-to-br from-purple-600 to-blue-600 rounded-2xl p-8 text-white shadow-xl">
          <div class="flex items-center justify-between mb-6">
            <div>
              <p class="text-purple-100 text-sm mb-1">AI 钱包余额</p>
              <div class="flex items-center gap-3">
                <h2 class="text-4xl font-bold">{{ aiWallet?.balance || 0 }} USDT</h2>
                <button 
                  @click="refreshWalletBalance"
                  :disabled="refreshing"
                  class="px-3 py-1 bg-white/20 hover:bg-white/30 rounded-lg text-sm transition-colors disabled:opacity-50"
                >
                  <i class="fa-solid fa-rotate-right" :class="{'animate-spin': refreshing}"></i>
                </button>
              </div>
              <p class="text-purple-200 text-xs mt-2">推荐收益和分润收入</p>
            </div>
            <div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
              <i class="fa-solid fa-robot text-3xl"></i>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4 pt-6 border-t border-white/20">
            <div>
              <p class="text-purple-200 text-xs">总收益</p>
              <p class="text-xl font-semibold">{{ aiWallet?.total_earned || 0 }} USDT</p>
            </div>
            <div>
              <p class="text-purple-200 text-xs">推荐人数</p>
              <p class="text-xl font-semibold">{{ aiWallet?.referral_count || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Human Wallet Card -->
        <div class="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
          <div class="flex items-center justify-between mb-6">
            <div>
              <p class="text-gray-500 text-sm mb-1">人类钱包（积分）</p>
              <h2 class="text-4xl font-bold text-gray-900">{{ humanWallet?.points_balance || 0 }}</h2>
              <p class="text-gray-400 text-xs mt-2">可提现余额</p>
            </div>
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <i class="fa-solid fa-wallet text-3xl text-blue-600"></i>
            </div>
          </div>
          
          <div class="grid grid-cols-3 gap-4 pt-6 border-t border-gray-200">
            <div>
              <p class="text-gray-500 text-xs">冻结</p>
              <p class="text-lg font-semibold text-gray-900">{{ humanWallet?.locked_points || 0 }}</p>
            </div>
            <div>
              <p class="text-gray-500 text-xs">总充值</p>
              <p class="text-lg font-semibold text-gray-900">{{ humanWallet?.total_deposited || 0 }}</p>
            </div>
            <div>
              <p class="text-gray-500 text-xs">总提现</p>
              <p class="text-lg font-semibold text-gray-900">{{ humanWallet?.total_withdrawn || 0 }}</p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-4 mt-6">
            <button 
              @click="refreshBalance"
              :disabled="refreshing"
              class="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              <i class="fa-solid fa-rotate-right mr-2" :class="{'animate-spin': refreshing}"></i>
              {{ refreshing ? '查询中...' : '刷新余额' }}
            </button>
            <button 
              @click="showWithdrawModal = true"
              class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              <i class="fa-solid fa-arrow-right-from-bracket mr-2"></i>
              提现
            </button>
            <button 
              @click="openDepositModal"
              class="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
            >
              <i class="fa-solid fa-plus mr-2"></i>
              充值
            </button>
          </div>
        </div>

        <!-- Wallet Address -->
        <div class="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">钱包地址</h3>
          
          <!-- Human Wallet -->
          <div class="mb-4">
            <p class="text-sm text-gray-500 mb-2">人类钱包（充值/交易）</p>
            <div class="flex items-center gap-3">
              <code class="flex-1 px-4 py-3 bg-gray-100 rounded-lg text-sm font-mono text-gray-700 break-all">
                {{ walletAddress }}
              </code>
              <button 
                @click="copyAddress"
                class="px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                title="复制地址"
              >
                <i class="fa-solid fa-copy"></i>
              </button>
            </div>
          </div>
          
          <!-- AI Wallet -->
          <div>
            <p class="text-sm text-gray-500 mb-2">AI钱包（推荐码/收益）</p>
            <div class="flex items-center gap-3">
              <code class="flex-1 px-4 py-3 bg-purple-100 rounded-lg text-sm font-mono text-purple-700 break-all">
                {{ aiWalletAddress }}
              </code>
              <button 
                @click="copyAIAddress"
                class="px-4 py-3 bg-purple-200 text-purple-700 rounded-lg hover:bg-purple-300 transition-colors"
                title="复制AI地址"
              >
                <i class="fa-solid fa-copy"></i>
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- Withdraw Modal -->
      <div v-if="showWithdrawModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-md w-full p-6">
          <h3 class="text-xl font-bold text-gray-900 mb-4">提现</h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">金额 (USDT)</label>
              <input 
                v-model="withdrawAmount"
                type="number"
                min="50"
                step="0.01"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="最低 50 USDT"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">提现地址</label>
              <input 
                v-model="withdrawAddress"
                type="text"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :placeholder="walletAddress"
              />
            </div>
          </div>

          <div class="flex gap-3 mt-6">
            <button 
              @click="showWithdrawModal = false"
              class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              取消
            </button>
            <button 
              @click="handleWithdraw"
              :disabled="withdrawing"
              class="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {{ withdrawing ? '处理中...' : '确认' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Deposit Modal -->
      <div v-if="showDepositModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-md w-full p-6">
          <h3 class="text-xl font-bold text-gray-900 mb-6">充值</h3>
          
          <!-- Wallet Address -->
          <div class="bg-blue-50 p-4 rounded-lg mb-4">
            <div class="text-sm text-blue-800 mb-2">充值地址 (请转账到此地址):</div>
            <div class="font-mono text-sm break-all bg-white p-3 rounded border border-blue-200">
              {{ depositWalletAddress || '加载中...' }}
            </div>
            <button 
              @click="copyText(depositWalletAddress)"
              class="mt-2 text-sm text-blue-600 hover:text-blue-700 flex items-center"
            >
              <i class="fa-solid fa-copy mr-1"></i> 复制地址
            </button>
          </div>

          <div class="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-4">
            <div class="flex items-start">
              <i class="fa-solid fa-circle-info text-yellow-600 mt-1 mr-2"></i>
              <div class="text-sm text-yellow-800">
                <p class="font-medium mb-1">充值说明：</p>
                <ul class="list-disc list-inside space-y-1">
                  <li>复制上方地址，在您的钱包中转入 USDT-TRC20</li>
                  <li>转账完成后，回到钱包页面点击<strong>"刷新余额"</strong>按钮</li>
                  <li>系统会自动查询链上交易并更新余额</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button 
              @click="showDepositModal = false"
              class="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              关闭
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { walletApi } from '@/services/api'

const userStore = useUserStore()

// Wallet data
const humanWallet = ref(null)
const aiWallet = ref(null)
const loading = ref(false)
const error = ref(null)

// Referral data (flat structure)
const referralRewards = ref([])
const totalReferralEarned = ref(0)
const teamStats = ref({})

// Modals
const showWithdrawModal = ref(false)
const showDepositModal = ref(false)
const withdrawAmount = ref('')
const withdrawAddress = ref('')
const depositTxHash = ref('')
const depositAmount = ref('')
const depositWalletAddress = ref('')
const withdrawing = ref(false)
const depositing = ref(false)
const verifying = ref(false)
const refreshing = ref(false)

// AI 子钱包索引（每个 AI 一个唯一索引）
const AI_WALLET_INDEX = 0

// Wallet address - 从后端 API 获取
const walletAddress = ref('')
const aiWalletAddress = ref('')

const isWalletConnected = computed(() => {
  return walletAddress.value && walletAddress.value !== ''
})

// WebSocket connection
let ws = null

// Connect to WebSocket
const connectWebSocket = () => {
  const userId = userStore.user?.address || `user_${Date.now()}`
  const wsUrl = `ws://localhost:3000/ws/${userId}`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket connected')
    // Request wallet data
    ws.send(JSON.stringify({
      type: 'request_wallet_data',
      ai_index: AI_WALLET_INDEX
    }))
  }
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data)
    
    if (message.type === 'wallet_data' || (message.code === 200 && message.data)) {
      // 接收钱包数据（兼容旧格式和新格式）
      const data = message.data || message
      
      walletAddress.value = data.wallet?.address || ''
      aiWallet.value = {
        total_earned: data.wallet?.total_earned || 0,
        balance_encrypted: data.wallet?.balance_encrypted || true
      }
      humanWallet.value = data.human_wallet || null
      
      // 保存推荐奖励数据
      referralRewards.value = data.referral_rewards || []
      totalReferralEarned.value = data.total_referral_earned || 0
      teamStats.value = data.team_stats || {}
      
      loading.value = false
    }
    
    else if (message.type === 'wallet_update') {
      // 实时更新钱包余额
      if (message.data?.wallet) {
        aiWallet.value = { ...aiWallet.value, ...message.data.wallet }
      }
      if (message.data?.human_wallet) {
        humanWallet.value = { ...humanWallet.value, ...message.data.human_wallet }
      }
    }
    
    else if (message.type === 'error' || message.code === 500) {
      error.value = message.message
      loading.value = false
    }
  }
  
  ws.onerror = (err) => {
    console.error('WebSocket error:', err)
    // Silently fallback to HTTP API
    fetchWalletData()
  }
  
  ws.onclose = () => {
    console.log('WebSocket disconnected')
  }
}

// Fetch wallet data via API (fallback)
const fetchWalletData = async () => {
  try {
    loading.value = true
    
    // Use AI wallet address to query AI wallet
    const aiAddress = aiWalletAddress.value || userStore.user?.ai_wallet_address
    
    if (!aiAddress) {
      error.value = 'AI钱包地址不存在'
      loading.value = false
      return
    }
    
    console.log('[FetchWallet] Querying AI wallet:', aiAddress)
    
    // Fetch AI wallet balance
    const aiResponse = await walletApi.getAIWallet(aiAddress)
    aiWallet.value = aiResponse.data
    
    console.log('[FetchWallet] AI wallet data:', aiWallet.value)
    
    // Also fetch human wallet for reference
    const humanAddress = walletAddress.value || userStore.walletAddress
    if (humanAddress) {
      try {
        const humanResponse = await walletApi.getHumanWallet(humanAddress)
        humanWallet.value = humanResponse.data
      } catch (err) {
        console.warn('Failed to fetch human wallet:', err)
      }
    }
    
    loading.value = false
  } catch (err) {
    console.error('Failed to fetch wallet data:', err)
    error.value = err.response?.data?.detail || 'Failed to load wallet'
    loading.value = false
  }
}

// Handle withdrawal
const handleWithdraw = async () => {
  try {
    withdrawing.value = true
    const address = walletAddress.value
    
    if (!withdrawAmount.value || parseFloat(withdrawAmount.value) < 50) {
      alert('Minimum withdrawal is 50 USDT')
      return
    }
    
    const response = await walletApi.withdraw({
      user_address: address,
      amount: parseFloat(withdrawAmount.value),
      withdraw_address: withdrawAddress.value || address
    })
    
    alert(`Withdrawal successful! ID: ${response.data.withdrawal_id}`)
    showWithdrawModal.value = false
    withdrawAmount.value = ''
    withdrawAddress.value = ''
    
    // Refresh wallet data
    await fetchWalletData()
  } catch (err) {
    console.error('Withdrawal failed:', err)
    alert(`Withdrawal failed: ${err.response?.data?.detail || err.message}`)
  } finally {
    withdrawing.value = false
  }
}

// Handle deposit
// 打开充值弹窗
const openDepositModal = async () => {
  // 检查钱包地址是否存在
  if (!walletAddress.value) {
    alert('钱包地址未加载，请刷新页面')
    return
  }
  
  showDepositModal.value = true
  depositTxHash.value = ''
  depositAmount.value = ''
  
  console.log('[Deposit] Loading address for user:', walletAddress.value)
  
  // 加载充值地址
  try {
    const address = walletAddress.value
    const response = await fetch(`/api/v1/deposits/wallet-address?user_address=${encodeURIComponent(address)}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || '获取充值地址失败')
    }
    
    console.log('[Deposit] Wallet address loaded:', data.wallet_address)
    depositWalletAddress.value = data.wallet_address
  } catch (err) {
    console.error('Failed to load deposit address:', err)
    alert(`获取充值地址失败: ${err.message}`)
  }
}

// 刷新余额 - 查询链上最新交易
const refreshBalance = async () => {
  try {
    refreshing.value = true
    const address = walletAddress.value
    
    const response = await fetch('/api/v1/deposits/refresh-balance', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        user_address: address
      })
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || '查询失败')
    }
    
    if (data.balance_updated) {
      alert(`发现 ${data.new_deposits} 笔新充值，共 ${data.total_amount.toFixed(2)} USDT`)
      // 更新本地钱包数据
      humanWallet.value.points_balance = data.wallet.points_balance
      humanWallet.value.total_deposited = data.wallet.total_deposited
    } else {
      alert('没有新的充值记录')
    }
  } catch (err) {
    console.error('Refresh balance failed:', err)
    alert(`查询失败: ${err.message}`)
  } finally {
    refreshing.value = false
  }
}

// 刷新 AI 钱包余额
const refreshWalletBalance = async () => {
  try {
    refreshing.value = true
    await fetchWalletData()
    alert('余额已刷新')
  } catch (err) {
    console.error('Refresh wallet failed:', err)
    alert('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 步骤 2: 验证链上交易
const verifyDeposit = async () => {
  try {
    if (!depositTxHash.value) {
      alert('请输入交易哈希')
      return
    }
    
    verifying.value = true
    const address = walletAddress.value
    
    const response = await fetch('/api/v1/deposits/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        user_address: address,
        tx_hash: depositTxHash.value
      })
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || '验证失败')
    }
    
    alert(`充值成功！金额: ${data.amount} USDT`)
    showDepositModal.value = false
    depositTxHash.value = ''
    depositAmount.value = ''
    depositWalletAddress.value = ''
    
    // Refresh wallet data
    await fetchWalletData()
  } catch (err) {
    console.error('Verify deposit failed:', err)
    alert(`验证失败: ${err.message}`)
  } finally {
    verifying.value = false
  }
}

const handleDeposit = async () => {
  // Deprecated: replaced by getDepositAddress and verifyDeposit
  alert('请使用新的充值流程')
}

// Copy address
const copyAddress = async () => {
  try {
    await navigator.clipboard.writeText(walletAddress.value)
    alert('人类钱包地址已复制！')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const copyAIAddress = async () => {
  try {
    await navigator.clipboard.writeText(aiWalletAddress.value)
    alert('AI钱包地址已复制！')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('已复制！')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// 页面加载时连接 WebSocket
onMounted(() => {
  // 优先从 userStore 加载钱包地址（后端注册时已生成）
  const storedAddress = userStore.walletAddress
  const storedAIAddress = userStore.user?.ai_wallet_address
  
  if (storedAddress) {
    walletAddress.value = storedAddress
    console.log('[AIWallet] Loaded human wallet from userStore:', storedAddress)
  }
  
  if (storedAIAddress) {
    aiWalletAddress.value = storedAIAddress
    console.log('[AIWallet] Loaded AI wallet from userStore:', storedAIAddress)
  }
  
  // 加载钱包数据
  if (storedAddress || storedAIAddress) {
    fetchWalletData()
  } else {
    console.log('[AIWallet] No wallet addresses in userStore, trying WebSocket/API')
    connectWebSocket()
  }
})

// 组件卸载时关闭 WebSocket
onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>
