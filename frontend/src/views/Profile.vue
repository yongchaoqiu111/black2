<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 md:px-6 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{{ $t('user.center') }}</h1>
        <p class="text-sm md:text-base text-gray-600">Manage your account and services</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Sidebar Menu -->
        <aside class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow-sm overflow-hidden">
            <!-- User Info -->
            <div class="p-6 border-b border-gray-200">
              <div class="flex items-center space-x-4">
                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-purple-400 to-pink-400"></div>
                <div>
                  <h3 class="font-semibold text-gray-900">{{ userStore.user?.name || 'User' }}</h3>
                  <p class="text-sm text-gray-600">{{ userStore.user?.email || 'user@example.com' }}</p>
                  <span class="inline-block mt-2 px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full">
                    VIP Member
                  </span>
                </div>
              </div>
            </div>

            <!-- Menu Items -->
            <nav class="p-4 space-y-1">
              <button
                v-for="item in menuItems"
                :key="item.id"
                @click="activeSection = item.id"
                :class="[
                  'w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors',
                  activeSection === item.id
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                ]"
              >
                <i :class="item.icon"></i>
                <span class="text-sm font-medium">{{ item.label }}</span>
              </button>
            </nav>
          </div>
        </aside>

        <!-- Main Content -->
        <main class="lg:col-span-3">
          <!-- Balance Overview -->
          <div v-if="activeSection === 'overview'" class="space-y-6">
            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-white rounded-lg shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <i class="fa-solid fa-wallet text-blue-600 text-xl"></i>
                  </div>
                  <span class="text-xs text-gray-500">USDT</span>
                </div>
                <h3 class="text-2xl font-bold text-gray-900 mb-1">1,234.56</h3>
                <p class="text-sm text-gray-600">{{ $t('user.balance') }}</p>
              </div>

              <div class="bg-white rounded-lg shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <i class="fa-solid fa-crown text-purple-600 text-xl"></i>
                  </div>
                  <span class="text-xs text-green-600 font-semibold">Active</span>
                </div>
                <h3 class="text-2xl font-bold text-gray-900 mb-1">VIP</h3>
                <p class="text-sm text-gray-600">{{ $t('user.memberLevel') }}</p>
              </div>

              <div class="bg-white rounded-lg shadow-sm p-6">
                <div class="flex items-center justify-between mb-4">
                  <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <i class="fa-solid fa-shopping-bag text-green-600 text-xl"></i>
                  </div>
                  <span class="text-xs text-gray-500">Total</span>
                </div>
                <h3 class="text-2xl font-bold text-gray-900 mb-1">28</h3>
                <p class="text-sm text-gray-600">My Products</p>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="bg-white rounded-lg shadow-sm p-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button @click="activeSection = 'recharge'" class="p-4 border border-gray-200 rounded-lg hover:border-gray-900 hover:bg-gray-50 transition-all text-center">
                  <i class="fa-solid fa-plus-circle text-2xl text-blue-600 mb-2"></i>
                  <p class="text-sm font-medium text-gray-900">{{ $t('user.recharge') }}</p>
                </button>
                <button @click="activeSection = 'withdraw'" class="p-4 border border-gray-200 rounded-lg hover:border-gray-900 hover:bg-gray-50 transition-all text-center">
                  <i class="fa-solid fa-minus-circle text-2xl text-green-600 mb-2"></i>
                  <p class="text-sm font-medium text-gray-900">{{ $t('user.withdraw') }}</p>
                </button>
                <button @click="activeSection = 'products'" class="p-4 border border-gray-200 rounded-lg hover:border-gray-900 hover:bg-gray-50 transition-all text-center">
                  <i class="fa-solid fa-box text-2xl text-purple-600 mb-2"></i>
                  <p class="text-sm font-medium text-gray-900">{{ $t('user.myProducts') }}</p>
                </button>
                <button @click="activeSection = 'services'" class="p-4 border border-gray-200 rounded-lg hover:border-gray-900 hover:bg-gray-50 transition-all text-center">
                  <i class="fa-solid fa-concierge-bell text-2xl text-orange-600 mb-2"></i>
                  <p class="text-sm font-medium text-gray-900">{{ $t('user.myServices') }}</p>
                </button>
              </div>
            </div>
          </div>

          <!-- Recharge -->
          <div v-if="activeSection === 'recharge'" class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-6">{{ $t('user.recharge') }}</h3>
            
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Amount (USDT)</label>
                <input
                  type="number"
                  v-model="rechargeAmount"
                  placeholder="Enter amount"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
                <div class="grid grid-cols-2 gap-4">
                  <label class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-gray-900 transition-colors">
                    <input type="radio" name="payment" value="usdt" class="mr-2" checked />
                    <span class="font-medium">USDT (TRC20)</span>
                  </label>
                  <label class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-gray-900 transition-colors">
                    <input type="radio" name="payment" value="btc" class="mr-2" />
                    <span class="font-medium">Bitcoin</span>
                  </label>
                </div>
              </div>

              <button class="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors">
                Proceed to Payment
              </button>
            </div>
          </div>

          <!-- Withdraw -->
          <div v-if="activeSection === 'withdraw'" class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-6">{{ $t('user.withdraw') }}</h3>
            
            <div class="space-y-6">
              <div class="p-4 bg-blue-50 rounded-lg">
                <p class="text-sm text-gray-700">Available Balance: <span class="font-bold">1,234.56 USDT</span></p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Withdrawal Amount (USDT)</label>
                <input
                  type="number"
                  v-model="withdrawAmount"
                  placeholder="Enter amount"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Wallet Address (TRC20)</label>
                <input
                  type="text"
                  v-model="withdrawAddress"
                  placeholder="Enter your USDT TRC20 address"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
                />
              </div>

              <button class="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors">
                Request Withdrawal
              </button>
            </div>
          </div>

          <!-- My Products -->
          <div v-if="activeSection === 'products'" class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-6">{{ $t('user.myProducts') }}</h3>
            
            <div class="space-y-4">
              <div v-for="product in myProducts" :key="product.id" class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-400 transition-colors">
                <div class="flex items-center space-x-4">
                  <div class="w-16 h-16 bg-gray-200 rounded-lg"></div>
                  <div>
                    <h4 class="font-semibold text-gray-900">{{ product.name }}</h4>
                    <p class="text-sm text-gray-600">{{ product.price }} USDT</p>
                    <span :class="['inline-block mt-1 px-2 py-1 text-xs rounded', product.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800']">
                      {{ product.status }}
                    </span>
                  </div>
                </div>
                <div class="flex space-x-2">
                  <button class="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">Edit</button>
                  <button class="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm hover:bg-gray-800">View</button>
                </div>
              </div>
            </div>
          </div>

          <!-- My Services -->
          <div v-if="activeSection === 'services'" class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-6">{{ $t('user.myServices') }}</h3>
            
            <div class="space-y-4">
              <div v-for="service in myServices" :key="service.id" class="p-4 border border-gray-200 rounded-lg">
                <div class="flex items-start justify-between mb-3">
                  <div>
                    <h4 class="font-semibold text-gray-900">{{ service.title }}</h4>
                    <p class="text-sm text-gray-600">{{ service.seller }}</p>
                  </div>
                  <span :class="['px-3 py-1 text-xs rounded-full', getStatusColor(service.status)]">
                    {{ service.status }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-600">Order #{{ service.orderId }}</span>
                  <span class="font-semibold text-gray-900">{{ service.amount }} USDT</span>
                </div>
                <div class="mt-3 flex space-x-2">
                  <button class="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">Contact Seller</button>
                  <button v-if="service.status === 'completed'" class="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm hover:bg-gray-800">Download</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Customer Support -->
          <div v-if="activeSection === 'support'" class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-6">{{ $t('user.customerSupport') }}</h3>
            
            <div class="space-y-6">
              <div class="p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
                <div class="flex items-center space-x-4 mb-4">
                  <div class="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-md">
                    <i class="fa-solid fa-headset text-2xl text-blue-600"></i>
                  </div>
                  <div>
                    <h4 class="font-bold text-gray-900">VIP Exclusive Support</h4>
                    <p class="text-sm text-gray-600">24/7 Priority Assistance</p>
                  </div>
                </div>
                <p class="text-sm text-gray-700 mb-4">As a VIP member, you have access to our dedicated support team for faster response times.</p>
                <button @click="router.push('/chat')" class="px-6 py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors">
                  Start Chat
                </button>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 border border-gray-200 rounded-lg">
                  <i class="fa-solid fa-envelope text-blue-600 text-2xl mb-2"></i>
                  <h4 class="font-semibold text-gray-900 mb-1">Email Support</h4>
                  <p class="text-sm text-gray-600">support@marketplace.com</p>
                </div>
                <div class="p-4 border border-gray-200 rounded-lg">
                  <i class="fa-brands fa-telegram text-blue-600 text-2xl mb-2"></i>
                  <h4 class="font-semibold text-gray-900 mb-1">Telegram</h4>
                  <p class="text-sm text-gray-600">@MarketplaceSupport</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeSection = ref('overview')
const rechargeAmount = ref('')
const withdrawAmount = ref('')
const withdrawAddress = ref('')

const menuItems = [
  { id: 'overview', label: 'Overview', icon: 'fa-solid fa-home' },
  { id: 'recharge', label: 'Recharge', icon: 'fa-solid fa-plus-circle' },
  { id: 'withdraw', label: 'Withdraw', icon: 'fa-solid fa-minus-circle' },
  { id: 'products', label: 'My Products', icon: 'fa-solid fa-box' },
  { id: 'services', label: 'My Services', icon: 'fa-solid fa-concierge-bell' },
  { id: 'support', label: 'Customer Support', icon: 'fa-solid fa-headset' }
]

const myProducts = ref([
  { id: 1, name: 'Marketing Automation Suite', price: 299, status: 'active' },
  { id: 2, name: 'SEO Optimization Tool', price: 199, status: 'active' },
  { id: 3, name: 'Social Media Manager', price: 149, status: 'draft' }
])

const myServices = ref([
  { id: 1, title: 'Custom Website Development', seller: 'WebDesign Pro', status: 'in_progress', orderId: '12345', amount: 500 },
  { id: 2, title: 'Logo Design Service', seller: 'Creative Studio', status: 'completed', orderId: '12346', amount: 150 }
])

const getStatusColor = (status) => {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}
</script>
