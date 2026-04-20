<template>
  <div class="min-h-screen bg-gray-50 pt-24 pb-12">
    <div class="max-w-6xl mx-auto px-4 md:px-6">
      
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Shopping Cart</h1>
        <p class="text-gray-600">{{ cartStore.totalItems }} items in your cart</p>
      </div>

      <div v-if="!cartStore.isEmpty" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Cart Items -->
        <div class="lg:col-span-2 space-y-4">
          <div 
            v-for="item in cartStore.items" 
            :key="item.id"
            class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6"
          >
            <div class="flex items-start space-x-4">
              <!-- Product Image -->
              <img 
                :src="item.image" 
                :alt="item.name"
                class="w-24 h-24 object-cover rounded-lg flex-shrink-0"
              />
              
              <!-- Product Info -->
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ item.name }}</h3>
                <p class="text-sm text-gray-600 mb-2">Seller: {{ item.seller }}</p>
                <p class="text-xl font-bold text-purple-600">${{ item.price }} USDT</p>
              </div>
              
              <!-- Quantity Controls -->
              <div class="flex flex-col items-end space-y-3">
                <button 
                  @click="cartStore.removeItem(item.id)"
                  class="text-red-500 hover:text-red-700 transition-colors"
                  title="Remove item"
                >
                  <i class="fa-solid fa-trash-alt"></i>
                </button>
                
                <div class="flex items-center space-x-2">
                  <button 
                    @click="cartStore.updateQuantity(item.id, item.quantity - 1)"
                    class="w-8 h-8 rounded-full border border-gray-300 hover:bg-gray-100 flex items-center justify-center transition-colors"
                  >
                    <i class="fa-solid fa-minus text-xs"></i>
                  </button>
                  <span class="w-12 text-center font-medium">{{ item.quantity }}</span>
                  <button 
                    @click="cartStore.updateQuantity(item.id, item.quantity + 1)"
                    class="w-8 h-8 rounded-full border border-gray-300 hover:bg-gray-100 flex items-center justify-center transition-colors"
                  >
                    <i class="fa-solid fa-plus text-xs"></i>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Subtotal -->
            <div class="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
              <span class="text-sm text-gray-600">Subtotal:</span>
              <span class="text-lg font-bold text-gray-900">${{ (item.price * item.quantity).toFixed(2) }} USDT</span>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-24">
            <h2 class="text-xl font-bold text-gray-900 mb-6">Order Summary</h2>
            
            <div class="space-y-4 mb-6">
              <div class="flex justify-between text-gray-600">
                <span>Subtotal ({{ cartStore.totalItems }} items)</span>
                <span>${{ cartStore.totalPrice.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-gray-600">
                <span>Platform Fee (5%)</span>
                <span>${{ (cartStore.totalPrice * 0.05).toFixed(2) }}</span>
              </div>
              <div class="border-t border-gray-200 pt-4 flex justify-between text-lg font-bold text-gray-900">
                <span>Total</span>
                <span class="text-purple-600">${{ (cartStore.totalPrice * 1.05).toFixed(2) }} USDT</span>
              </div>
            </div>
            
            <!-- Payment Method Selection -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
              <select 
                v-model="selectedPaymentMethod"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="usdt_trc20">USDT (TRC20)</option>
                <option value="usdt_erc20">USDT (ERC20)</option>
                <option value="wallet_balance">Wallet Balance</option>
              </select>
            </div>
            
            <!-- Checkout Button -->
            <button 
              @click="handleCheckout"
              class="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all transform hover:scale-105 shadow-lg"
            >
              Proceed to Checkout
              <i class="fa-solid fa-arrow-right ml-2"></i>
            </button>
            
            <!-- Continue Shopping -->
            <router-link 
              to="/shop"
              class="block mt-4 text-center text-sm text-purple-600 hover:text-purple-700 transition-colors"
            >
              <i class="fa-solid fa-shopping-bag mr-1"></i>
              Continue Shopping
            </router-link>
          </div>
        </div>
      </div>

      <!-- Empty Cart State -->
      <div v-else class="text-center py-20">
        <div class="w-32 h-32 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="fa-solid fa-shopping-cart text-6xl text-gray-400"></i>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
        <p class="text-gray-600 mb-8">Looks like you haven't added anything yet</p>
        <router-link 
          to="/shop"
          class="inline-flex items-center px-8 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
        >
          <i class="fa-solid fa-shopping-bag mr-2"></i>
          Browse Products
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useOrderStore } from '@/stores/orders'

const router = useRouter()
const cartStore = useCartStore()
const orderStore = useOrderStore()

const selectedPaymentMethod = ref('usdt_trc20')

const handleCheckout = () => {
  // Create order
  const order = orderStore.createOrder(cartStore.items, selectedPaymentMethod.value)
  
  // Clear cart
  cartStore.clearCart()
  
  // Redirect to payment page
  router.push({
    name: 'Payment',
    query: { orderId: order.id }
  })
}
</script>
