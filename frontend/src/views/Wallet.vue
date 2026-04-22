<template>
  <div class="min-h-screen bg-gray-50 pt-24 pb-12">
    <div class="max-w-6xl mx-auto px-4 md:px-6">
      
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">My Wallet</h1>
        <p class="text-gray-600">Manage your funds and transactions</p>
      </div>

      <!-- Balance Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- USDT TRC20 Balance -->
        <div class="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <i class="fa-solid fa-coins text-2xl"></i>
            </div>
            <span class="text-sm opacity-80">TRC20 Network</span>
          </div>
          <div class="text-3xl font-bold mb-1">${{ balances.USDT_TRC20.toFixed(2) }}</div>
          <div class="text-sm opacity-80">USDT (TRC20)</div>
        </div>

        <!-- USDT ERC20 Balance -->
        <div class="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <i class="fa-solid fa-coins text-2xl"></i>
            </div>
            <span class="text-sm opacity-80">ERC20 Network</span>
          </div>
          <div class="text-3xl font-bold mb-1">${{ balances.USDT_ERC20.toFixed(2) }}</div>
          <div class="text-sm opacity-80">USDT (ERC20)</div>
        </div>

        <!-- Total Balance -->
        <div class="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-6 text-white shadow-lg">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <i class="fa-solid fa-wallet text-2xl"></i>
            </div>
            <span class="text-sm opacity-80">Total Balance</span>
          </div>
          <div class="text-3xl font-bold mb-1">${{ totalBalance.toFixed(2) }}</div>
          <div class="text-sm opacity-80">All Networks</div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <button 
          @click="showDepositModal = true"
          class="bg-white border border-gray-200 rounded-lg p-4 hover:border-purple-500 hover:shadow-md transition-all text-center"
        >
          <i class="fa-solid fa-arrow-down text-2xl text-green-600 mb-2"></i>
          <div class="font-medium text-gray-900">Deposit</div>
        </button>
        
        <button 
          @click="showWithdrawModal = true"
          class="bg-white border border-gray-200 rounded-lg p-4 hover:border-purple-500 hover:shadow-md transition-all text-center"
        >
          <i class="fa-solid fa-arrow-up text-2xl text-red-600 mb-2"></i>
          <div class="font-medium text-gray-900">Withdraw</div>
        </button>
        
        <router-link 
          to="/shop"
          class="bg-white border border-gray-200 rounded-lg p-4 hover:border-purple-500 hover:shadow-md transition-all text-center"
        >
          <i class="fa-solid fa-shopping-bag text-2xl text-purple-600 mb-2"></i>
          <div class="font-medium text-gray-900">Shop</div>
        </router-link>
        
        <router-link 
          to="/orders"
          class="bg-white border border-gray-200 rounded-lg p-4 hover:border-purple-500 hover:shadow-md transition-all text-center"
        >
          <i class="fa-solid fa-receipt text-2xl text-blue-600 mb-2"></i>
          <div class="font-medium text-gray-900">Orders</div>
        </router-link>
      </div>

      <!-- Transaction History -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">Transaction History</h2>
          <div class="flex space-x-2">
            <button 
              @click="filterType = 'all'"
              :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors', filterType === 'all' ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200']"
            >
              All
            </button>
            <button 
              @click="filterType = 'deposit'"
              :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors', filterType === 'deposit' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200']"
            >
              Deposits
            </button>
            <button 
              @click="filterType = 'withdrawal'"
              :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors', filterType === 'withdrawal' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200']"
            >
              Withdrawals
            </button>
          </div>
        </div>

        <div v-if="filteredTransactions.length > 0" class="divide-y divide-gray-200">
          <div 
            v-for="tx in filteredTransactions" 
            :key="tx.id"
            class="p-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <div 
                  :class="[
                    'w-12 h-12 rounded-full flex items-center justify-center',
                    tx.type === 'deposit' ? 'bg-green-100' : 'bg-red-100'
                  ]"
                >
                  <i 
                    :class="[
                      'text-xl',
                      tx.type === 'deposit' ? 'fa-solid fa-arrow-down text-green-600' : 'fa-solid fa-arrow-up text-red-600'
                    ]"
                  ></i>
                </div>
                
                <div>
                  <div class="font-semibold text-gray-900">{{ tx.description }}</div>
                  <div class="text-sm text-gray-600">{{ formatDate(tx.date) }}</div>
                  <div class="text-xs text-gray-500 mt-1">
                    <span :class="['inline-block px-2 py-1 rounded', tx.network === 'TRC20' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700']">
                      {{ tx.network }}
                    </span>
                    <span class="ml-2">TX: {{ tx.txHash.substring(0, 8) }}...</span>
                  </div>
                </div>
              </div>
              
              <div class="text-right">
                <div 
                  :class="['text-lg font-bold', tx.type === 'deposit' ? 'text-green-600' : 'text-red-600']"
                >
                  {{ tx.type === 'deposit' ? '+' : '-' }}${{ tx.amount.toFixed(2) }}
                </div>
                <div class="text-sm text-gray-600">USDT</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <i class="fa-solid fa-receipt text-6xl text-gray-300 mb-4"></i>
          <p class="text-gray-600">No transactions yet</p>
        </div>
      </div>
    </div>

    <!-- Deposit Modal -->
    <div v-if="showDepositModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl max-w-md w-full p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-gray-900">Deposit USDT</h3>
          <button @click="showDepositModal = false" class="text-gray-500 hover:text-gray-700">
            <i class="fa-solid fa-times text-xl"></i>
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Select Network</label>
            <select 
              v-model="depositNetwork"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="TRC20">TRC20 (Tron) - Low Fees</option>
              <option value="ERC20">ERC20 (Ethereum) - Universal</option>
            </select>
          </div>
          
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="text-sm text-gray-600 mb-2">充值地址:</div>
            <div class="font-mono text-sm break-all bg-white p-3 rounded border border-gray-200">
              {{ depositNetwork === 'TRC20' ? walletAddresses.TRC20 : walletAddresses.ERC20 }}
            </div>
            <button 
              @click="copyAddress"
              class="mt-2 text-sm text-purple-600 hover:text-purple-700 flex items-center"
            >
              <i class="fa-solid fa-copy mr-1"></i> 复制地址
            </button>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">转账哈希 (TX Hash) *</label>
            <input 
              v-model="depositTxHash"
              type="text"
              placeholder="输入链上转账哈希"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
            <p class="text-xs text-gray-500 mt-1">转账完成后，请输入交易哈希提交审核</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">充值金额 (USDT) *</label>
            <input 
              v-model.number="depositAmount"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <button 
            @click="handleDeposit"
            :disabled="depositLoading"
            class="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50"
          >
            <span v-if="!depositLoading">提交充值申请</span>
            <span v-else>提交中...</span>
          </button>
          
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="flex items-start space-x-2">
              <i class="fa-solid fa-exclamation-triangle text-yellow-600 mt-1"></i>
              <div class="text-sm text-yellow-800">
                <strong>Important:</strong> Only send USDT to this address. Sending other tokens may result in permanent loss.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Withdraw Modal -->
    <div v-if="showWithdrawModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl max-w-md w-full p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-gray-900">Withdraw USDT</h3>
          <button @click="showWithdrawModal = false" class="text-gray-500 hover:text-gray-700">
            <i class="fa-solid fa-times text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="handleWithdraw" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Select Network</label>
            <select 
              v-model="withdrawNetwork"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="TRC20">TRC20 (Tron)</option>
              <option value="ERC20">ERC20 (Ethereum)</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Recipient Address</label>
            <input 
              v-model="withdrawAddress"
              type="text"
              placeholder="Enter USDT address"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Amount (USDT)</label>
            <input 
              v-model.number="withdrawAmount"
              type="number"
              step="0.01"
              min="0"
              :max="withdrawNetwork === 'TRC20' ? balances.USDT_TRC20 : balances.USDT_ERC20"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
            <div class="text-sm text-gray-600 mt-1">
              Available: ${{ withdrawNetwork === 'TRC20' ? balances.USDT_TRC20.toFixed(2) : balances.USDT_ERC20.toFixed(2) }} USDT
            </div>
          </div>
          
          <button 
            type="submit"
            class="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all"
          >
            Confirm Withdrawal
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// Balances
const balances = ref({
  USDT_TRC20: 1250.50,
  USDT_ERC20: 800.00
})

const totalBalance = computed(() => {
  return balances.value.USDT_TRC20 + balances.value.USDT_ERC20
})

// Wallet addresses
const walletAddresses = {
  TRC20: import.meta.env.VITE_PLATFORM_WALLET_TRC20 || 'TAqmqsoQhrRxnFuuo3AQG14PW6TMh4eWW4Z',
  ERC20: import.meta.env.VITE_PLATFORM_WALLET_ERC20 || '0xEf2943958F8781303f05879CC52aDb6bdcaa6AbB'
}

// Modals
const showDepositModal = ref(false)
const showWithdrawModal = ref(false)
const depositNetwork = ref('TRC20')
const depositTxHash = ref('')
const depositAmount = ref(0)
const depositLoading = ref(false)
const withdrawNetwork = ref('TRC20')
const withdrawAddress = ref('')
const withdrawAmount = ref(0)

// Transactions
const transactions = ref([
  {
    id: 'tx1',
    type: 'deposit',
    amount: 500.00,
    network: 'TRC20',
    description: 'Deposit from external wallet',
    date: new Date(Date.now() - 86400000).toISOString(),
    txHash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
  },
  {
    id: 'tx2',
    type: 'withdrawal',
    amount: 200.00,
    network: 'ERC20',
    description: 'Withdrawal to external wallet',
    date: new Date(Date.now() - 172800000).toISOString(),
    txHash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890'
  },
  {
    id: 'tx3',
    type: 'deposit',
    amount: 1000.00,
    network: 'TRC20',
    description: 'Initial deposit',
    date: new Date(Date.now() - 259200000).toISOString(),
    txHash: '0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba'
  }
])

const filterType = ref('all')

const filteredTransactions = computed(() => {
  if (filterType.value === 'all') {
    return transactions.value
  }
  return transactions.value.filter(tx => tx.type === filterType.value)
})

// Methods
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const copyAddress = () => {
  const address = depositNetwork.value === 'TRC20' ? walletAddresses.TRC20 : walletAddresses.ERC20
  navigator.clipboard.writeText(address)
  alert('地址已复制到剪贴板！')
}

const handleDeposit = async () => {
  if (!depositTxHash.value || !depositAmount.value) {
    alert('请填写转账哈希和充值金额')
    return
  }
  
  const userAddress = userStore.walletAddress
  
  if (!userAddress) {
    alert('钱包地址未加载，请刷新页面')
    return
  }
  
  depositLoading.value = true
  
  try {
    const response = await fetch('/api/v1/deposits', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        user_address: userAddress,
        tx_hash: depositTxHash.value,
        amount: depositAmount.value
      })
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || '充值失败')
    }
    
    alert(`充值申请已提交！金额: $${depositAmount.value}`)
    showDepositModal.value = false
    depositTxHash.value = ''
    depositAmount.value = 0
    
    // Reload wallet data
    loadWalletData()
  } catch (error) {
    console.error('Deposit failed:', error)
    alert(error.message || '充值失败，请重试')
  } finally {
    depositLoading.value = false
  }
}

const loadWalletData = async () => {
  try {
    const userAddress = userStore.walletAddress
    
    if (!userAddress) return
    
    const response = await fetch(`/api/v1/wallets/${userAddress}`)
    const data = await response.json()
    
    if (response.ok && data.wallet) {
      balances.value.USDT_TRC20 = data.wallet.points_balance || 0
      // For now, put all balance in TRC20
      balances.value.USDT_ERC20 = 0
    }
  } catch (error) {
    console.error('Failed to load wallet data:', error)
  }
}

const loadTransactions = async () => {
  try {
    const userAddress = userStore.walletAddress
    
    if (!userAddress) return
    
    const response = await fetch(`/api/v1/transactions?address=${userAddress}&limit=20`)
    const data = await response.json()
    
    if (response.ok && data.transactions) {
      transactions.value = data.transactions.map(tx => ({
        id: tx.tx_id,
        type: tx.type === 'deposit' ? 'deposit' : 'withdrawal',
        amount: tx.amount,
        network: tx.network || 'TRC20',
        description: tx.description || 'Transaction',
        date: tx.timestamp || tx.created_at,
        txHash: tx.tx_hash || tx.tx_id
      }))
    }
  } catch (error) {
    console.error('Failed to load transactions:', error)
  }
}

onMounted(() => {
  loadWalletData()
  loadTransactions()
})
</script>
