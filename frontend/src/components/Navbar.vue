<template>
  <nav class="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50 h-16">
    <div class="h-full px-4 md:px-6 flex items-center justify-between">
      
      <!-- Left Side: Search Box -->
      <div class="flex items-center space-x-3">
        <!-- Logo (Mobile Only) -->
        <router-link to="/" class="md:hidden text-xl font-bold text-gray-900 hover:text-gray-700 transition-colors">
          {{ $t('nav.logo') }}
        </router-link>

        <!-- Search Box -->
        <div class="relative hidden md:block">
          <input
            type="text"
            placeholder="Search products..."
            class="w-64 lg:w-80 pl-10 pr-4 py-2 bg-gray-100 border-0 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all"
          />
          <i class="fa-solid fa-search absolute left-3.5 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
        </div>
      </div>

      <!-- Right Side: Icon Navigation -->
      <div class="flex items-center space-x-1">
        <!-- Shop -->
        <router-link to="/shop" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="Shop">
          <i class="fa-solid fa-store text-lg text-gray-600 group-hover:text-gray-900 transition-colors"></i>
        </router-link>

        <!-- AI Agent Hub - AI智能助手 -->
        <router-link to="/ai-agent-hub" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="AI智能助手">
          <i class="fa-solid fa-brain text-lg text-gray-600 group-hover:text-purple-600 transition-colors"></i>
        </router-link>

        <!-- AI Wallet - AI帮人类赚的钱 -->
        <router-link to="/ai-wallet" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="AI收益">
          <i class="fa-solid fa-hand-holding-usd text-lg text-gray-600 group-hover:text-green-600 transition-colors"></i>
          <span class="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full"></span>
        </router-link>

        <!-- Sell Product -->
        <router-link to="/sell" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="Sell Product">
          <i class="fa-solid fa-plus-circle text-lg text-gray-600 group-hover:text-purple-600 transition-colors"></i>
        </router-link>

        <!-- Post Requirement -->
        <router-link to="/post-requirement" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="Post Requirement">
          <i class="fa-solid fa-lightbulb text-lg text-gray-600 group-hover:text-orange-500 transition-colors"></i>
        </router-link>

        <!-- Create -->
        <router-link to="/create" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="Create & Earn">
          <i class="fa-solid fa-plus-circle text-lg text-gray-600 group-hover:text-green-600 transition-colors"></i>
        </router-link>

        <!-- Divider -->
        <div class="w-px h-6 bg-gray-300 mx-2"></div>

        <!-- Language Switch with Dropdown -->
        <div class="relative">
          <button 
            @click="showLangDropdown = !showLangDropdown" 
            class="p-2.5 hover:bg-gray-100 rounded-full transition-colors flex items-center"
            title="Switch Language"
          >
            <i :class="currentLanguageIcon" class="text-lg text-gray-600 hover:text-gray-900 transition-colors"></i>
          </button>

          <!-- Language Dropdown -->
          <div 
            v-if="showLangDropdown"
            class="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50"
          >
            <button
              v-for="lang in languages"
              :key="lang.code"
              @click="selectLanguage(lang.code)"
              :class="[
                'w-full px-4 py-2 text-left hover:bg-gray-100 transition-colors flex items-center space-x-3',
                locale === lang.code ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
              ]"
            >
              <span class="text-lg">{{ lang.flag }}</span>
              <span class="text-sm font-medium">{{ lang.name }}</span>
              <i v-if="locale === lang.code" class="fa-solid fa-check text-blue-600 ml-auto"></i>
            </button>
          </div>
        </div>

        <!-- Cart -->
        <router-link to="/cart" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="Cart">
          <i class="fa-solid fa-shopping-cart text-lg text-gray-600 group-hover:text-gray-900 transition-colors"></i>
          <span v-if="cartStore.totalItems > 0" class="absolute -top-0.5 -right-0.5 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold border-2 border-white">{{ cartStore.totalItems }}</span>
        </router-link>

        <!-- Chat -->
        <router-link to="/chat" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="Chat">
          <i class="fa-solid fa-comments text-lg text-gray-600 group-hover:text-gray-900 transition-colors"></i>
          <span class="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white"></span>
        </router-link>

        <!-- Notification Settings -->
        <router-link to="/notification-settings" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors relative group" title="通知设置">
          <i class="fa-solid fa-bell text-lg text-gray-600 group-hover:text-purple-600 transition-colors"></i>
        </router-link>

        <!-- Divider -->
        <div class="w-px h-6 bg-gray-300 mx-2"></div>

        <!-- User Menu -->
        <template v-if="userStore.isLoggedIn">
          <router-link to="/profile" class="w-9 h-9 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 hover:opacity-80 transition-opacity ring-2 ring-transparent hover:ring-purple-500" title="Profile"></router-link>
        </template>
        <template v-else>
          <router-link to="/login" class="p-2.5 hover:bg-gray-100 rounded-full transition-colors" title="Login">
            <i class="fa-solid fa-sign-in-alt text-lg text-gray-600 hover:text-gray-900 transition-colors"></i>
          </router-link>
          <router-link to="/register" class="p-2.5 bg-gray-900 hover:bg-gray-800 rounded-full transition-colors" title="Register">
            <i class="fa-solid fa-user-plus text-lg text-white"></i>
          </router-link>
        </template>



        <!-- Mobile Menu Button -->
        <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 hover:bg-gray-100 rounded-full">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div v-if="mobileMenuOpen" class="md:hidden bg-white border-t border-gray-200">
      <div class="px-4 py-3 space-y-3">
        <router-link to="/shop" class="block text-sm font-medium text-gray-700 hover:text-gray-900 py-2 transition-colors">
          {{ $t('nav.shop') }}
        </router-link>
        <router-link to="/upload" class="block text-sm font-medium text-gray-700 hover:text-gray-900 py-2 transition-colors">
          {{ $t('nav.sell') }}
        </router-link>
        <router-link to="/about" class="block text-sm font-medium text-gray-700 hover:text-gray-900 py-2 transition-colors">
          {{ $t('nav.about') }}
        </router-link>
        <div class="pt-3 border-t border-gray-200">
          <router-link to="/login" class="block text-sm font-medium text-gray-700 hover:text-gray-900 py-2 transition-colors">
            {{ $t('auth.login') }}
          </router-link>
          <router-link to="/register" class="block px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 transition-colors mt-2">
            {{ $t('auth.register') }}
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'

const { locale } = useI18n()
const userStore = useUserStore()
const cartStore = useCartStore()
const mobileMenuOpen = ref(false)
const showLangDropdown = ref(false)

// Language options
const languages = [
  { code: 'zh', name: '中文', flag: '🇨🇳', icon: 'fa-solid fa-globe-asia' },
  { code: 'en', name: 'English', flag: '🇺🇸', icon: 'fa-solid fa-globe-americas' }
]

const currentLanguageIcon = computed(() => {
  const lang = languages.find(l => l.code === locale.value)
  return lang ? lang.icon : 'fa-solid fa-globe'
})

const selectLanguage = (code) => {
  locale.value = code
  localStorage.setItem('locale', code)
  showLangDropdown.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showLangDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
