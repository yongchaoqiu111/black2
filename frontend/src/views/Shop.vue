<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-gray-900">Shop</h1>
        <p class="text-gray-600 mt-2">Browse and purchase AI products</p>
      </div>
    </div>

    <!-- Product Grid -->
    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="product in products" 
          :key="product.id"
          @click="goToProduct(product.id)"
          class="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-xl transition-shadow"
        >
          <!-- Product Image -->
          <div class="h-48 bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <i class="fa-solid fa-box text-white text-6xl"></i>
          </div>
          
          <!-- Product Info -->
          <div class="p-4">
            <h3 class="font-semibold text-lg text-gray-900 mb-2">{{ product.name }}</h3>
            <p class="text-gray-600 text-sm mb-3 line-clamp-2">{{ product.description }}</p>
            
            <div class="flex items-center justify-between">
              <span class="text-2xl font-bold text-purple-600">${{ product.price }}</span>
              <button class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                View Details
              </button>
            </div>
            
            <!-- Seller Info -->
            <div class="mt-3 pt-3 border-t border-gray-200">
              <div class="flex items-center text-sm text-gray-500">
                <i class="fa-solid fa-user-circle mr-2"></i>
                <span>{{ product.seller }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="products.length === 0" class="text-center py-16">
        <i class="fa-solid fa-inbox text-6xl text-gray-300 mb-4"></i>
        <p class="text-gray-500 text-lg">No products available</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const products = ref([])
const loading = ref(true)

// Load products from backend
onMounted(async () => {
  try {
    const response = await fetch('/api/v1/products')
    const data = await response.json()
    
    if (response.ok && data.products) {
      products.value = data.products
    }
  } catch (error) {
    console.error('Failed to load products:', error)
  } finally {
    loading.value = false
  }
})

const goToProduct = (id) => {
  router.push(`/product/${id}`)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
