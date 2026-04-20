<template>
  <div class="min-h-screen flex flex-col">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Main Content -->
    <main class="flex-1 pt-16">
      <slot></slot>
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-8 md:py-12">
      <div class="max-w-7xl mx-auto px-4 md:px-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Brand -->
          <div class="md:col-span-2">
            <h3 class="text-xl font-bold mb-4">Marketplace</h3>
            <p class="text-gray-400 text-sm mb-4">
              Virtual goods trading platform with secure escrow service
            </p>
            <div class="flex space-x-4">
              <a href="https://github.com/yongchaoqiu111/ai-ecosystem-engine" target="_blank" class="text-gray-400 hover:text-white transition-colors" title="GitHub - AI Ecosystem Engine (Open Source)">
                <i class="fa-brands fa-github text-xl"></i>
              </a>
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fa-brands fa-twitter text-xl"></i>
              </a>
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fa-brands fa-discord text-xl"></i>
              </a>
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fa-brands fa-telegram text-xl"></i>
              </a>
            </div>
          </div>

          <!-- Quick Links -->
          <div>
            <h4 class="font-semibold mb-4">Quick Links</h4>
            <ul class="space-y-2 text-sm">
              <li><router-link to="/shop" class="text-gray-400 hover:text-white transition-colors">Shop</router-link></li>
              <li><router-link to="/upload" class="text-gray-400 hover:text-white transition-colors">Sell</router-link></li>
              <li><router-link to="/about" class="text-gray-400 hover:text-white transition-colors">Membership</router-link></li>
              <li><router-link to="/chat" class="text-gray-400 hover:text-white transition-colors">Chat</router-link></li>
              <li><router-link to="/profile" class="text-gray-400 hover:text-white transition-colors">User Center</router-link></li>
            </ul>
          </div>

          <!-- Support -->
          <div>
            <h4 class="font-semibold mb-4">Support</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">Help Center</a></li>
              <li><a href="/API_DOCUMENTATION.md" target="_blank" class="text-gray-400 hover:text-white transition-colors">API Documentation</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">Terms of Service</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition-colors">Contact Us</a></li>
            </ul>
          </div>
        </div>

        <!-- Bottom Bar -->
        <div class="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>&copy; 2024 Marketplace. All rights reserved.</p>
        </div>
      </div>
    </footer>

    <!-- 客服聊天组件（仅登录用户可见�?-->
    <CustomerChatWidget v-if="authStore.isAuthenticated" />
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/Navbar.vue'
import CustomerChatWidget from '@/components/CustomerChatWidget.vue'

const authStore = useAuthStore()
</script>
