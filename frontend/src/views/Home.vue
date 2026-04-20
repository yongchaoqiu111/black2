<template>
  <div class="min-h-screen bg-white">
    
    <!-- Hero Section -->
    <section class="pt-32 pb-20 px-4 md:px-6">
      <div class="max-w-7xl mx-auto text-center">
        <h1 class="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
          {{ $t('home.title') }}
        </h1>
        <p class="text-lg md:text-xl text-gray-600 mb-6 max-w-3xl mx-auto px-4">
          {{ $t('home.subtitle') }}
        </p>
        
        <!-- Platform Philosophy -->
        <div class="max-w-4xl mx-auto mb-10 p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-200">
          <h2 class="text-xl md:text-2xl font-bold text-gray-900 mb-4">Why Choose Us?</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
            <div class="flex items-start space-x-3">
              <i class="fa-solid fa-bolt text-blue-600 text-2xl mt-1"></i>
              <div>
                <h3 class="font-semibold text-gray-900 mb-1">Instant AI Consultation</h3>
                <p class="text-sm text-gray-600">Get answers 24/7 from seller's AI assistant</p>
              </div>
            </div>
            <div class="flex items-start space-x-3">
              <i class="fa-solid fa-shield-alt text-purple-600 text-2xl mt-1"></i>
              <div>
                <h3 class="font-semibold text-gray-900 mb-1">Secure & Trusted</h3>
                <p class="text-sm text-gray-600">Platform escrow protects every transaction</p>
              </div>
            </div>
            <div class="flex items-start space-x-3">
              <i class="fa-solid fa-rocket text-green-600 text-2xl mt-1"></i>
              <div>
                <h3 class="font-semibold text-gray-900 mb-1">AI-Powered Delivery</h3>
                <p class="text-sm text-gray-600">Automated quotes, payments, and delivery</p>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <router-link 
            to="/shop"
            class="inline-flex items-center px-6 md:px-8 py-3 md:py-4 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors text-sm md:text-base"
          >
            {{ $t('home.viewMore') }}
            <i class="fa-solid fa-arrow-right ml-2"></i>
          </router-link>
          <router-link 
            to="/upload"
            class="inline-flex items-center px-6 md:px-8 py-3 md:py-4 border-2 border-gray-900 text-gray-900 rounded-lg font-medium hover:bg-gray-50 transition-colors text-sm md:text-base"
          >
            Start Selling
            <i class="fa-solid fa-upload ml-2"></i>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Featured Categories -->
    <section class="py-12 md:py-16 border-t border-gray-200">
      <div class="max-w-7xl mx-auto px-4 md:px-6">
        <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6 md:mb-8">{{ $t('home.browseByCategory') }}</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          <router-link 
            v-for="cat in categories" 
            :key="cat.name"
            :to="`/shop?category=${cat.slug}`"
            class="group p-4 md:p-6 border border-gray-200 rounded-lg hover:border-gray-900 transition-colors"
          >
            <div class="w-10 h-10 md:w-12 md:h-12 bg-gray-100 rounded-lg mb-3 md:mb-4 group-hover:bg-gray-900 transition-colors flex items-center justify-center">
              <i class="fa-solid fa-box text-gray-600 group-hover:text-white text-lg md:text-xl"></i>
            </div>
            <h3 class="font-semibold text-gray-900 mb-1 text-sm md:text-base">{{ cat.name }}</h3>
            <p class="text-xs md:text-sm text-gray-600">{{ cat.count }} {{ $t('product.filter.items') }}</p>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
// Navbar is now in Layout component

const categories = [
  { name: 'Software', slug: 'software', count: 234 },
  { name: 'Websites', slug: 'website', count: 189 },
  { name: 'Templates', slug: 'templates', count: 456 },
  { name: 'Graphics', slug: 'graphics', count: 312 }
]
</script>
