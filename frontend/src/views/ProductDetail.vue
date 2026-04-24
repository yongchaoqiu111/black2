<template>
  <div class="min-h-screen bg-gray-50">
    
    <div class="max-w-7xl mx-auto px-4 md:px-6 py-8">
      <!-- Breadcrumb -->
      <div class="mb-6 text-sm text-gray-600">
        <router-link to="/" class="hover:text-gray-900">Home</router-link>
        <span class="mx-2">/</span>
        <router-link to="/shop" class="hover:text-gray-900">Shop</router-link>
        <span class="mx-2">/</span>
        <span class="text-gray-900">{{ product.name }}</span>
      </div>

      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-0">
          <!-- Left Column - Image Gallery & Video -->
          <div class="p-6">
            <!-- Main Display Area -->
            <div class="aspect-video bg-gray-100 rounded-lg overflow-hidden relative mb-4">
              <!-- Image Carousel -->
              <div v-if="!showVideo" class="relative h-full">
                <img 
                  :src="product.images && product.images[currentImageIndex] ? product.images[currentImageIndex] : ''" 
                  class="w-full h-full object-cover"
                />
                
                <!-- Navigation Arrows -->
                <button 
                  v-if="product.images && product.images.length > 1"
                  @click="prevImage"
                  class="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition-colors shadow-md"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button 
                  v-if="product.images && product.images.length > 1"
                  @click="nextImage"
                  class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition-colors shadow-md"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                <!-- Image Counter -->
                <div class="absolute bottom-3 right-3 bg-black/60 text-white px-3 py-1 rounded-full text-sm">
                  {{ currentImageIndex + 1 }} / {{ (product.images || []).length }}
                </div>
              </div>

              <!-- Video Player -->
              <video 
                v-else
                :src="product.video" 
                controls
                class="w-full h-full object-cover"
              ></video>
              
              <!-- Video Play Button Overlay -->
              <button 
                v-if="product.video && !showVideo"
                @click="showVideo = true"
                class="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors group"
              >
                <div class="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-xl group-hover:scale-110 transition-transform">
                  <svg class="w-10 h-10 text-gray-900 ml-1" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </div>
              </button>
            </div>

            <!-- Thumbnail Gallery -->
            <div class="flex space-x-3 overflow-x-auto pb-2">
              <!-- Video Thumbnail -->
              <div 
                v-if="product.video"
                @click="showVideo = true"
                :class="[
                  'flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden cursor-pointer border-2 relative',
                  showVideo ? 'border-blue-500' : 'border-transparent hover:border-gray-300'
                ]"
              >
                <div class="w-full h-full bg-gray-200 flex items-center justify-center">
                  <svg class="w-8 h-8 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </div>
              </div>

              <!-- Image Thumbnails -->
              <div 
                v-for="(img, index) in (product.images || [])" 
                :key="index"
                @click="selectImage(index)"
                :class="[
                  'flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden cursor-pointer border-2',
                  !showVideo && currentImageIndex === index ? 'border-blue-500' : 'border-transparent hover:border-gray-300'
                ]"
              >
                <img :src="img" class="w-full h-full object-cover" />
              </div>
            </div>
          </div>

          <!-- Right Column - Product Info & Actions -->
          <div class="p-6 border-l border-gray-200">
            <!-- Product Title -->
            <h1 class="text-2xl font-bold text-gray-900 mb-3">{{ product.name }}</h1>

            <!-- Price Section -->
            <div class="mb-6 p-4 bg-red-50 rounded-lg">
              <div class="flex items-baseline space-x-3">
                <span class="text-sm text-gray-600">价格:</span>
                <span class="text-3xl font-bold text-red-600">{{ product.price }} USDT</span>
                <span v-if="product.originalPrice" class="text-lg text-gray-400 line-through">{{ product.originalPrice }} USDT</span>
              </div>
            </div>

            <!-- Seller Info Card -->
            <div class="border border-gray-200 rounded-lg p-4 mb-6">
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-3">
                  <div class="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-400"></div>
                  <div>
                    <p class="font-medium text-gray-900">{{ product.seller }}</p>
                    <p class="text-sm text-gray-600">Online</p>
                  </div>
                </div>
                <button 
                  @click="handleFollow"
                  :class="[
                    'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                    isFollowing 
                      ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' 
                      : 'bg-blue-500 text-white hover:bg-blue-600'
                  ]"
                >
                  {{ isFollowing ? '�?Following' : '+ Follow' }}
                </button>
              </div>
              
              <div class="grid grid-cols-3 gap-4 text-center py-3 border-t border-gray-200">
                <div>
                  <p class="text-lg font-bold text-gray-900">{{ product.sales }}</p>
                  <p class="text-xs text-gray-600">Sales</p>
                </div>
                <div class="border-l border-gray-200">
                  <p class="text-lg font-bold text-gray-900">{{ product.rating }}</p>
                  <p class="text-xs text-gray-600">Rating</p>
                </div>
                <div class="border-l border-gray-200">
                  <p class="text-lg font-bold text-gray-900">{{ product.reviews }}</p>
                  <p class="text-xs text-gray-600">Reviews</p>
                </div>
              </div>
              
              <!-- Seller Risk Level (B2P Protocol) -->
              <div v-if="sellerRiskLevel" class="mt-4 pt-4 border-t border-gray-200">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-medium text-gray-700">交易风险:</span>
                  <span 
                    :class="getRiskColor(sellerRiskLevel.level)" 
                    class="px-3 py-1 rounded-full text-xs font-bold uppercase"
                  >
                    {{ sellerRiskLevel.level.replace('_', ' ') }}
                  </span>
                </div>
                <p class="text-xs text-gray-500 mt-1">基于 B2P 协议的信誉评估</p>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="space-y-3 mb-6">
              <button 
                @click="handleBuyNow"
                class="w-full py-4 bg-red-600 text-white rounded-lg font-bold text-lg hover:bg-red-700 transition-colors shadow-md"
              >
                立即购买
              </button>
              
              <div class="grid grid-cols-2 gap-3">
                <button 
                  @click="handleAddToCart"
                  class="py-3 bg-orange-500 text-white rounded-lg font-medium hover:bg-orange-600 transition-colors"
                >
                  加入购物车
                </button>
                <button 
                  @click="handleFavorite"
                  :class="[
                    'py-3 rounded-lg font-medium transition-colors border-2',
                    isFavorited 
                      ? 'border-red-500 text-red-500 hover:bg-red-50' 
                      : 'border-gray-300 text-gray-700 hover:border-gray-400'
                  ]"
                >
                  <span class="flex items-center justify-center space-x-2">
                    <svg class="w-5 h-5" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    <span>{{ isFavorited ? '已收藏' : '收藏' }}</span>
                  </span>
                </button>
              </div>

              <router-link 
                :to="{ path: '/chat', query: { seller: product.seller, productId: product.id } }"
                class="w-full py-3 border-2 border-blue-500 text-blue-500 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center justify-center space-x-2"
              >
                <i class="fa-solid fa-comments"></i>
                <span>联系卖家</span>
              </router-link>
            </div>

            <!-- Tags -->
            <div>
              <h3 class="text-sm font-semibold text-gray-900 mb-2">TEXT:</h3>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="tag in (product.tags || [])" 
                  :key="tag"
                  class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200 cursor-pointer transition-colors"
                >
                  #{{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Product Details Tabs -->
      <div class="mt-8 bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="border-b border-gray-200">
          <div class="flex">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'px-6 py-4 font-medium transition-colors border-b-2',
                activeTab === tab.id 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              ]"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <div class="p-6">
          <!-- Product Description -->
          <div v-if="activeTab === 'description'" class="prose max-w-none">
            <h3 class="text-xl font-bold text-gray-900 mb-4">Product Introduction</h3>
            <p class="text-gray-600 leading-relaxed mb-4">{{ product.description }}</p>
            
            <h4 class="text-lg font-semibold text-gray-900 mb-3">Features</h4>
            <ul class="list-disc list-inside space-y-2 text-gray-600 mb-6">
              <li v-for="feature in (product.features || [])" :key="feature">{{ feature }}</li>
            </ul>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">Specifications</h4>
            <div class="grid grid-cols-2 gap-4">
              <div v-for="(value, key) in product.specs" :key="key" class="flex justify-between py-2 border-b border-gray-100">
                <span class="text-gray-600">{{ key }}</span>
                <span class="font-medium text-gray-900">{{ value }}</span>
              </div>
            </div>
          </div>

          <!-- Transaction Process -->
          <div v-if="activeTab === 'process'" class="space-y-6">
            <h3 class="text-xl font-bold text-gray-900 mb-6">交易流程</h3>
            <div class="space-y-4">
              <div v-for="(step, index) in transactionSteps" :key="index" class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">
                  {{ index + 1 }}
                </div>
                <div class="flex-1">
                  <h4 class="font-semibold text-gray-900 mb-1">{{ step.title }}</h4>
                  <p class="text-gray-600 text-sm">{{ step.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Anti-Fraud Tips -->
          <div v-if="activeTab === 'safety'" class="space-y-4">
            <h3 class="text-xl font-bold text-gray-900 mb-6">防骗提示</h3>
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
              <div class="flex">
                <svg class="w-6 h-6 text-yellow-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <h4 class="font-semibold text-yellow-800 mb-2">Important Notice</h4>
                  <p class="text-yellow-700 text-sm">Please read these safety tips carefully to protect your interests during the transaction.</p>
                </div>
              </div>
            </div>
            
            <div class="space-y-3">
              <div v-for="(tip, index) in antiFraudTips" :key="index" class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-gray-700 text-sm">{{ tip }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Modal -->
    <div v-if="showContactModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="showContactModal = false"></div>
      <div class="relative bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-900">联系卖家</h3>
          <button @click="showContactModal = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="sendMessage" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Your Message</label>
            <textarea 
              v-model="message"
              rows="5"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="Hello, I'm interested in this product..."
            ></textarea>
          </div>
          
          <button 
            type="submit"
            class="w-full py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
          >
            Send Message
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useOrderStore } from '@/stores/orders'
import { ordersApi } from '@/services/api'
import { useUserStore } from '@/stores/user'
import { useProductStore } from '@/stores/product'
import { useProductDetail, tabs, transactionSteps, antiFraudTips } from '@/composables/useProductDetail'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const orderStore = useOrderStore()
const userStore = useUserStore()
const productStore = useProductStore()

const sellerRiskLevel = ref(null)

// Use composable for UI state and logic
const {
  showVideo,
  currentImageIndex,
  isFollowing,
  isFavorited,
  showContactModal,
  message,
  activeTab,
  selectImage,
  handleFollow,
  handleFavorite
} = useProductDetail()

// Use data from Store
const product = computed(() => {
  const p = productStore.currentProduct || {}
  return {
    id: p.product_id,
    product_id: p.product_id,
    name: p.name || '加载中...',
    description: p.description || '',
    price: p.price || 0,
    originalPrice: p.original_price,
    seller: p.seller_address || '未知卖家',
    sellerAddress: p.seller_address,
    fileHash: p.file_hash,
    video: p.video_url || '',
    images: p.images ? (Array.isArray(p.images) ? p.images : [p.images]) : [],
    features: p.features || [],
    sales: p.sales_count || 0,
    rating: p.rating || 5.0,
    reviews: p.review_count || 0,
    tags: p.tags || []
  }
})

// Implement image navigation with access to product data
const nextImage = () => {
  if (product.value.images.length > 0) {
    currentImageIndex.value = (currentImageIndex.value + 1) % product.value.images.length
  }
}

const prevImage = () => {
  if (product.value.images.length > 0) {
    currentImageIndex.value = currentImageIndex.value === 0 ? product.value.images.length - 1 : currentImageIndex.value - 1
  }
}

// Load product details if not in Store
onMounted(async () => {
  // Priority 1: Use data already in Store (passed from Shop.vue)
  if (productStore.currentProduct) {
    console.log('Using cached product from Store:', productStore.currentProduct.name)
    await fetchSellerRisk(productStore.currentProduct.seller_address)
    return
  }

  // Priority 2: Fallback to API if Store is empty (e.g., direct refresh)
  const productId = route.params.id
  if (productId && productId !== 'undefined') {
    console.log('Fetching product from API:', productId)
    await productStore.getProductById(productId)
    if (productStore.currentProduct) {
      await fetchSellerRisk(productStore.currentProduct.seller_address)
    }
  } else {
    console.error('No product ID found in route or Store')
  }
})

async function fetchSellerRisk(sellerAddress) {
  if (!sellerAddress) return
  try {
    const response = await fetch(`/api/v1/reputation/${sellerAddress}`)
    const data = await response.json()
    sellerRiskLevel.value = {
      level: data.risk_level || 'normal',
      friction_index: data.friction_index
    }
  } catch (e) {
    console.error('Failed to fetch seller risk:', e)
  }
}

function getRiskColor(level) {
  switch (level) {
    case 'low': return 'bg-green-100 text-green-800'
    case 'medium': return 'bg-yellow-100 text-yellow-800'
    case 'high': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const handleBuyNow = async () => {
  // Check if logged in
  if (!userStore.user?.address) {
    alert('请先登录')
    router.push('/login')
    return
  }

  // MUST use AI Wallet Address for transaction settlement
  const buyerAiAddress = userStore.aiWalletAddress || userStore.user?.ai_wallet_address
  if (!buyerAiAddress) {
    alert('系统错误：未检测到您的 AI 钱包地址，请尝试重新登录以同步钱包信息。')
    console.error('AI Wallet Address missing. User:', userStore.user)
    return
  }

  // Validate Seller Address
  const sellerAddress = product.value.sellerAddress || product.value.seller_address
  if (!sellerAddress) {
    alert('商品信息错误：缺少卖家地址，无法创建订单。')
    return
  }

  try {
    // Generate a random contract_hash (mock)
    const contractHash = Array.from({length: 64}, () => Math.floor(Math.random() * 16).toString(16)).join('')
    
    // Create order - strictly use AI wallet address
    const orderData = {
      from_address: buyerAiAddress, // AI Wallet for payment
      to_address: sellerAddress,
      amount: Number(product.value.price),
      currency: 'USDT',
      contract_hash: contractHash,
      file_hash: null
    }
    
    console.log('[Order] Submitting transaction:', orderData)
    const response = await ordersApi.create(orderData)
    console.log('Order created:', response.data)
    
    // X402 Integration: Show Escrow Details
    const escrowId = response.data.x402_escrow_id
    const escrowAddress = response.data.x402_escrow_address
    
    if (escrowId && escrowAddress) {
      alert(`订单创建成功！\n\nX402 托管 ID: ${escrowId}\n托管地址: ${escrowAddress}\n\n请使用您的钱包向该地址支付 ${product.value.price} USDT`)
    } else {
      alert('订单创建成功！订单号：' + response.data.tx_id)
    }
    
    // Refresh order list
    await orderStore.loadOrders()
    
    router.push('/orders')
  } catch (error) {
    console.error('Failed to create order:', error)
    alert('创建订单失败：' + (error.response?.data?.detail || error.message))
  }
}
const handleAddToCart = () => {
  cartStore.addItem(product)
  alert('Added to cart successfully!')
}
const sendMessage = () => {
  alert('Message sent successfully!')
  showContactModal.value = false
  message.value = ''
}
</script>
