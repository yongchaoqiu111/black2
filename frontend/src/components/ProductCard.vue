<template>
  <router-link :to="`/product/${product.id}`" class="group cursor-pointer block bg-white rounded-lg overflow-hidden border border-gray-200 hover:border-gray-300 transition-all duration-200 hover:shadow-md">
    <!-- Image -->
    <div class="relative aspect-[4/3] overflow-hidden bg-gray-100">
      <img 
        :src="product.image" 
        :alt="product.name"
        class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-300"
      />
      
      <!-- AI Created Badge -->
      <div v-if="product.aiCreated" class="absolute top-2 left-2 px-2 py-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white text-xs font-semibold rounded-lg shadow-lg flex items-center space-x-1">
        <i class="fa-solid fa-robot"></i>
        <span>AI Created</span>
      </div>
      
      <!-- Quick Actions Overlay -->
      <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-200"></div>
      
      <!-- Favorite Button -->
      <button @click.prevent class="absolute top-2 right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-sm hover:scale-110">
        <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="p-3">
      <!-- Title -->
      <h3 class="text-sm font-medium text-gray-900 mb-1 line-clamp-2 leading-tight group-hover:text-gray-600 transition-colors">
        {{ product.name }}
      </h3>

      <!-- Social Proof - 多人订阅线索 -->
      <div v-if="product.subscribers || product.recentSales" class="flex items-center space-x-2 mb-2">
        <!-- 头像堆叠 -->
        <div class="flex -space-x-2">
          <div v-for="i in Math.min(3, (product.subscribers || 0))" :key="i"
               class="w-5 h-5 rounded-full border-2 border-white bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-[8px] text-white font-bold">
            {{ String.fromCharCode(65 + i) }}
          </div>
        </div>
        <!-- 文字提示 -->
        <span class="text-xs text-gray-500">
          <span v-if="product.recentSales" class="text-green-600 font-semibold">
            {{ product.recentSales }}人刚购买
          </span>
          <span v-else-if="product.subscribers">
            {{ product.subscribers }}人已订阅
          </span>
        </span>
      </div>

      <!-- Seller & Price -->
      <div class="flex items-center justify-between mt-2">
        <div class="flex items-center space-x-2">
          <div class="w-6 h-6 rounded-full bg-gray-200"></div>
          <span class="text-xs text-gray-600 truncate max-w-[80px]">{{ product.seller }}</span>
        </div>
        <div class="text-right">
          <span class="text-sm font-semibold text-gray-900">{{ product.price }} USDT</span>
        </div>
      </div>

      <!-- AI Story Hint - 激发好奇心 -->
      <div v-if="product.aiStory" class="mt-2 pt-2 border-t border-gray-100">
        <div class="flex items-start space-x-2">
          <i class="fa-solid fa-lightbulb text-yellow-500 text-xs mt-0.5"></i>
          <p class="text-xs text-gray-500 italic line-clamp-2">{{ product.aiStory }}</p>
        </div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  product: {
    type: Object,
    required: true
  }
})
</script>
