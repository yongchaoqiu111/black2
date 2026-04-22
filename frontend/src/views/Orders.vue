<template>
  <div class="min-h-screen bg-gray-50 pt-24 pb-12">
    <div class="max-w-6xl mx-auto px-4 md:px-6">
      
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">我的订单</h1>
        <p class="text-gray-600">跟踪和管理您的购买记录</p>
      </div>

      <!-- Order Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">总订单数</span>
            <i class="fa-solid fa-shopping-bag text-purple-600 text-xl"></i>
          </div>
          <div class="text-2xl font-bold text-gray-900">{{ orderStore.orders.length }}</div>
        </div>
        
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">待处理</span>
            <i class="fa-solid fa-clock text-yellow-600 text-xl"></i>
          </div>
          <div class="text-2xl font-bold text-yellow-600">{{ orderStore.pendingOrders.length }}</div>
        </div>
        
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">已完成</span>
            <i class="fa-solid fa-check-circle text-green-600 text-xl"></i>
          </div>
          <div class="text-2xl font-bold text-green-600">{{ orderStore.completedOrders.length }}</div>
        </div>
        
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-600">总消费</span>
            <i class="fa-solid fa-dollar-sign text-blue-600 text-xl"></i>
          </div>
          <div class="text-2xl font-bold text-blue-600">${{ orderStore.totalSpent.toFixed(2) }}</div>
        </div>
      </div>

      <!-- Filter Tabs -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <div class="border-b border-gray-200">
          <div class="flex space-x-1 p-2">
            <button 
              v-for="tab in tabs" 
              :key="tab.value"
              @click="activeTab = tab.value"
              :class="[
                'px-6 py-3 rounded-lg font-medium transition-colors',
                activeTab === tab.value 
                  ? 'bg-purple-600 text-white' 
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >
              {{ tab.label }}
              <span v-if="tab.count" class="ml-2 px-2 py-1 text-xs rounded-full bg-white/20">
                {{ tab.count }}
              </span>
            </button>
          </div>
        </div>

        <!-- Orders List -->
        <div v-if="filteredOrders.length > 0" class="divide-y divide-gray-200">
          <div 
            v-for="order in filteredOrders" 
            :key="order.id"
            class="p-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start justify-between mb-4">
              <div>
                <div class="flex items-center space-x-3 mb-2">
                  <h3 class="font-semibold text-gray-900">{{ order.id }}</h3>
                  <span :class="getStatusBadgeClass(order.status)">
                    {{ getStatusText(order.status) }}
                  </span>
                </div>
                <div class="text-sm text-gray-600">
                  <i class="fa-regular fa-calendar-alt mr-1"></i>
                  {{ formatDate(order.createdAt) }}
                </div>
              </div>
              
              <div class="text-right">
                <div class="text-2xl font-bold text-purple-600">${{ order.total.toFixed(2) }}</div>
                <div class="text-sm text-gray-600">USDT</div>
              </div>
            </div>

            <!-- Order Items -->
            <div class="space-y-3 mb-4">
              <div 
                v-for="item in order.items" 
                :key="item.id"
                class="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg"
              >
                <img 
                  :src="item.image" 
                  :alt="item.name"
                  class="w-16 h-16 object-cover rounded-lg"
                />
                <div class="flex-1">
                  <div class="font-medium text-gray-900">{{ item.name }}</div>
                  <div class="text-sm text-gray-600">数量：{{ item.quantity }}</div>
                </div>
                <div class="font-semibold text-gray-900">${{ (item.price * item.quantity).toFixed(2) }}</div>
              </div>
            </div>

            <!-- Payment Info -->
            <div class="flex items-center justify-between pt-4 border-t border-gray-200">
              <div class="text-sm text-gray-600">
                <i class="fa-solid fa-credit-card mr-1"></i>
                支付方式：{{ getPaymentMethodText(order.paymentMethod) }}
              </div>
              
              <div class="flex space-x-2">
                <router-link 
                  :to="{ name: 'OrderDetail', params: { id: order.id } }"
                  class="px-4 py-2 text-sm font-medium text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                >
                  查看详情
                </router-link>
                                
                <button 
                  v-if="order.status === 'pending'"
                  @click="handleCancelOrder(order.id)"
                  class="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  取消订单
                </button>
                                
                <button 
                  v-if="order.status === 'completed'"
                  @click="handleDownload(order)"
                  class="px-4 py-2 text-sm font-medium text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                >
                  <i class="fa-solid fa-download mr-1"></i>
                  下载
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-16">
          <div class="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <i class="fa-solid fa-receipt text-5xl text-gray-400"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">暂无订单</h3>
          <p class="text-gray-600 mb-6">您还没有下过任何订单</p>
          <router-link 
            to="/shop"
            class="inline-flex items-center px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
          >
            <i class="fa-solid fa-shopping-bag mr-2"></i>
            开始购物
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useOrderStore } from '@/stores/orders'

const orderStore = useOrderStore()

// Load orders on mount
onMounted(async () => {
  await orderStore.loadOrders()
})

const activeTab = ref('all')

const tabs = computed(() => [
  { label: '全部订单', value: 'all', count: null },
  { label: '已支付', value: 'paid', count: orderStore.orders.filter(o => o.status === 'paid').length },
  { label: '已完成', value: 'completed', count: orderStore.completedOrders.length }
])

const filteredOrders = computed(() => {
  if (activeTab.value === 'all') {
    return orderStore.orders
  }
  return orderStore.orders.filter(order => order.status === activeTab.value)
})

// Methods
const getStatusBadgeClass = (status) => {
  const classes = {
    paid: 'px-3 py-1 text-sm font-medium bg-blue-100 text-blue-800 rounded-full',
    shipped: 'px-3 py-1 text-sm font-medium bg-purple-100 text-purple-800 rounded-full',
    completed: 'px-3 py-1 text-sm font-medium bg-green-100 text-green-800 rounded-full',
    refunded: 'px-3 py-1 text-sm font-medium bg-red-100 text-red-800 rounded-full',
    cancelled: 'px-3 py-1 text-sm font-medium bg-gray-100 text-gray-800 rounded-full'
  }
  return classes[status] || classes.paid
}

const getStatusText = (status) => {
  const texts = {
    paid: '已支付',
    shipped: '已发货',
    completed: '已完成',
    refunded: '已退款',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const getPaymentMethodText = (method) => {
  const methods = {
    usdt_trc20: 'USDT (TRC20)',
    usdt_erc20: 'USDT (ERC20)',
    wallet_balance: 'Wallet Balance'
  }
  return methods[method] || method
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const handleCancelOrder = (orderId) => {
  if (confirm('确定要取消这个订单吗？')) {
    orderStore.cancelOrder(orderId)
  }
}

const handleDownload = (order) => {
  // TODO: Implement download logic
  alert(`Downloading products from order ${order.id}`)
}
</script>
