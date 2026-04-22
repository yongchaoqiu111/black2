<template>
  <div class="min-h-screen bg-gray-50">
    
    <div class="max-w-4xl mx-auto px-4 md:px-6 py-8">
      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">TEXT</h1>
        <p class="text-sm md:text-base text-gray-600">TEXT</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8">
        <!-- Left Column - Payment Info -->
        <div class="space-y-6">
          <!-- Order Summary -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-4">TEXT</h2>
            
            <div class="space-y-3 pb-4 border-b border-gray-200">
              <div class="flex justify-between">
                <span class="text-gray-600">TEXT</span>
                <span class="font-medium text-gray-900">{{ order.productName }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">TEXT</span>
                <span class="font-medium text-gray-900">{{ order.seller }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">TEXT</span>
                <span class="font-medium text-gray-900">1</span>
              </div>
            </div>

            <div class="pt-4">
              <div class="flex justify-between items-center">
                <span class="text-lg font-semibold text-gray-900">TEXT</span>
                <div class="text-right">
                  <span class="text-2xl font-bold text-blue-600">${{ order.amount }}</span>
                  <p class="text-sm text-gray-500">�?{{ order.usdtAmount }} USDT</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Network Selection -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <h2 class="text-lg font-bold text-gray-900 mb-4">TEXT</h2>
            
            <div class="space-y-3">
              <!-- TRC20 Option -->
              <label 
                :class="[
                  'relative flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all',
                  selectedNetwork === 'trc20' 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <input 
                  type="radio" 
                  name="network" 
                  value="trc20"
                  v-model="selectedNetwork"
                  class="mt-1 w-4 h-4 text-blue-600"
                />
                <div class="ml-3 flex-1">
                  <div class="flex items-center justify-between">
                    <span class="font-semibold text-gray-900">TEXT</span>
                    <span class="px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded">TEXT</span>
                  </div>
                  <p class="text-sm text-gray-600 mt-1">TEXT</p>
                  <p class="text-xs text-gray-500 mt-1">TEXT: ~1 USDT</p>
                </div>
              </label>

              <!-- ERC20 Option -->
              <label 
                :class="[
                  'relative flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all',
                  selectedNetwork === 'erc20' 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <input 
                  type="radio" 
                  name="network" 
                  value="erc20"
                  v-model="selectedNetwork"
                  class="mt-1 w-4 h-4 text-blue-600"
                />
                <div class="ml-3 flex-1">
                  <div class="flex items-center justify-between">
                    <span class="font-semibold text-gray-900">TEXT</span>
                  </div>
                  <p class="text-sm text-gray-600 mt-1">TEXT</p>
                  <p class="text-xs text-gray-500 mt-1">TEXT: ~5-15 USDT</p>
                </div>
              </label>
            </div>

            <!-- Warning -->
            <div class="mt-4 p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded">
              <div class="flex">
                <svg class="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <p class="text-sm text-yellow-700">
                  <strong>TEXT:</strong> TEXT
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column - QR Code & Address -->
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h2 class="text-lg font-bold text-gray-900 mb-6 text-center">TEXT</h2>

          <!-- QR Code -->
          <div class="flex justify-center mb-6">
            <div class="p-4 bg-white border-2 border-gray-200 rounded-lg">
              <!-- Simulated QR Code -->
              <div class="w-48 h-48 md:w-56 md:h-56 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg flex items-center justify-center relative overflow-hidden">
                <div class="absolute inset-0 grid grid-cols-8 grid-rows-8 gap-0.5 p-2">
                  <div v-for="i in 64" :key="i" 
                    :class="[
                      'rounded-sm',
                      Math.random() > 0.5 ? 'bg-gray-900' : 'bg-white'
                    ]"
                  ></div>
                </div>
                <!-- Center Logo -->
                <div class="absolute inset-0 flex items-center justify-center">
                  <div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center shadow-md">
                    <span class="text-xs font-bold text-blue-600">USDT</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Network Badge -->
          <div class="text-center mb-4">
            <span :class="[
              'inline-block px-4 py-2 rounded-full text-sm font-bold',
              selectedNetwork === 'trc20' ? 'bg-green-100 text-green-700' : 'bg-purple-100 text-purple-700'
            ]">
              {{ selectedNetwork === 'trc20' ? 'TRC20 Network' : 'ERC20 Network' }}
            </span>
          </div>

          <!-- Wallet Address -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">TEXT</label>
            <div class="relative">
              <input 
                type="text" 
                :value="currentAddress"
                readonly
                class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg bg-gray-50 text-sm font-mono text-gray-700"
              />
              <button 
                @click="copyAddress"
                class="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-gray-200 rounded-lg transition-colors"
                title="Copy Address"
              >
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
            <p v-if="copied" class="text-sm text-green-600 mt-2 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              TEXT
            </p>
          </div>

          <!-- Amount to Pay -->
          <div class="mb-6 p-4 bg-blue-50 rounded-lg">
            <label class="block text-sm font-medium text-gray-700 mb-2">TEXT</label>
            <div class="flex items-baseline space-x-2">
              <span class="text-3xl font-bold text-blue-600">{{ order.usdtAmount }}</span>
              <span class="text-lg font-semibold text-gray-700">USDT</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">TEXT</p>
          </div>

          <!-- Payment Status -->
          <div class="border-t border-gray-200 pt-6">
            <div class="flex items-center justify-center space-x-2 mb-4">
              <div class="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></div>
              <span class="text-sm font-medium text-gray-700">TEXT</span>
            </div>
            
            <div class="text-center">
              <p class="text-xs text-gray-500 mb-4">Payment will be confirmed automatically after blockchain verification</p>
              
              <button 
                @click="checkPayment"
                :disabled="checkingPayment"
                class="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <svg v-if="checkingPayment" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ checkingPayment ? $t('payment.checking') : $t('payment.iHavePaid') }}
              </button>
            </div>
          </div>

          <!-- Timer -->
          <div class="mt-4 text-center">
            <p class="text-sm text-gray-600">
              TEXT: 
              <span class="font-bold text-red-600">{{ formatTime(paymentTimeout) }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Payment Instructions -->
      <div class="mt-8 bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-lg font-bold text-gray-900 mb-4">TEXT</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="flex items-start space-x-3">
            <div class="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold flex-shrink-0">1</div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-1">TEXT</h3>
              <p class="text-sm text-gray-600">TEXT</p>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <div class="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold flex-shrink-0">2</div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-1">TEXT</h3>
              <p class="text-sm text-gray-600">TEXT</p>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <div class="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold flex-shrink-0">3</div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-1">TEXT</h3>
              <p class="text-sm text-gray-600">TEXT</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Success Modal -->
    <div v-if="showSuccessModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50"></div>
      <div class="relative bg-white rounded-lg max-w-md w-full p-8 shadow-xl text-center">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">TEXT</h3>
        <p class="text-gray-600 mb-6">TEXT</p>
        <button 
          @click="goToDownload"
          class="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          TEXT
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '@/components/Navbar.vue'

const router = useRouter()
const selectedNetwork = ref('trc20')
const copied = ref(false)
const checkingPayment = ref(false)
const showSuccessModal = ref(false)
const paymentTimeout = ref(1800) // 30 minutes in seconds

let timerInterval = null

// Mock order data
const order = ref({
  productName: 'Premium Marketing Automation Suite',
  seller: 'Marketing Pro Studio',
  amount: 299,
  usdtAmount: 299
})

// Wallet addresses
const addresses = {
  trc20: 'TXYZabc123def456ghi789jkl012mno345pqr',
  erc20: '0x1234567890abcdef1234567890abcdef12345678'
}

const currentAddress = computed(() => addresses[selectedNetwork.value])

const copyAddress = async () => {
  try {
    await navigator.clipboard.writeText(currentAddress.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = currentAddress.value
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}

const checkPayment = () => {
  checkingPayment.value = true
  
  // Simulate payment verification
  setTimeout(() => {
    checkingPayment.value = false
    showSuccessModal.value = true
  }, 3000)
}

const goToDownload = () => {
  router.push('/shop')
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// Start countdown timer
onMounted(() => {
  timerInterval = setInterval(() => {
    if (paymentTimeout.value > 0) {
      paymentTimeout.value--
    } else {
      clearInterval(timerInterval)
      alert('Payment timeout. Please create a new order.')
      router.push('/shop')
    }
  }, 1000)
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>
