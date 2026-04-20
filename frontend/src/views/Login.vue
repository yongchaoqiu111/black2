<template>
  <div class="min-h-screen bg-white pt-16 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
        <p class="text-gray-600">Sign in to your account</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
          <input 
            type="email" 
            v-model="email"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
          <input 
            type="password" 
            v-model="password"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
            placeholder="•••••••�?
          />
        </div>

        <button 
          type="submit"
          class="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors"
        >
          Sign In
        </button>
      </form>

      <p class="text-center mt-6 text-sm text-gray-600">
        Don't have an account? 
        <router-link to="/register" class="text-gray-900 font-medium hover:underline">Sign up</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const password = ref('')

const handleLogin = () => {
  userStore.login()
  router.push('/')
}
</script>
