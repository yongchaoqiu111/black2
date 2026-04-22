<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <router-link to="/" class="text-3xl font-bold text-gray-900">Marketplace</router-link>
      </div>

      <!-- Forgot Password Card -->
      <div v-if="mode === 'forgot'" class="bg-white rounded-xl shadow-lg p-8">
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <i class="fa-solid fa-lock text-2xl text-blue-600"></i>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">TEXT</h2>
          <p class="text-sm text-gray-600">TEXT</p>
        </div>

        <form @submit.prevent="handleForgotPassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              TEXT
            </label>
            <input
              type="email"
              v-model="form.email"
              required
              :placeholder="$t('auth.emailPlaceholder')"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <i v-if="loading" class="fa-solid fa-spinner fa-spin mr-2"></i>
            TEXT
          </button>
        </form>

        <!-- Success Message -->
        <div v-if="success" class="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-start">
            <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
            <div class="text-sm text-green-800">
              <p class="font-semibold mb-1">{{ success }}</p>
              <p v-if="mockLink" class="mt-2 text-xs text-green-700">
                <strong>Mock Link (Development):</strong><br>
                <a :href="mockLink" class="underline break-all">{{ mockLink }}</a>
              </p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-start">
            <i class="fa-solid fa-exclamation-circle text-red-500 mt-1 mr-3"></i>
            <div class="text-sm text-red-800">
              <p class="font-semibold">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Back to Login -->
        <div class="mt-6 text-center">
          <router-link to="/login" class="text-sm text-gray-900 hover:underline flex items-center justify-center">
            <i class="fa-solid fa-arrow-left mr-2"></i>
            TEXT
          </router-link>
        </div>
      </div>

      <!-- Reset Password Card (with token) -->
      <div v-if="mode === 'reset'" class="bg-white rounded-xl shadow-lg p-8">
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <i class="fa-solid fa-key text-2xl text-green-600"></i>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">TEXT</h2>
          <p class="text-sm text-gray-600">TEXT</p>
        </div>

        <form @submit.prevent="handleResetPassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              TEXT
            </label>
            <input
              type="password"
              v-model="resetForm.newPassword"
              required
              minlength="6"
              :placeholder="$t('auth.newPasswordPlaceholder')"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              TEXT
            </label>
            <input
              type="password"
              v-model="resetForm.confirmPassword"
              required
              minlength="6"
              :placeholder="$t('auth.confirmPassword2Placeholder')"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <i v-if="loading" class="fa-solid fa-spinner fa-spin mr-2"></i>
            TEXT
          </button>
        </form>

        <!-- Error Message -->
        <div v-if="error" class="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-start">
            <i class="fa-solid fa-exclamation-circle text-red-500 mt-1 mr-3"></i>
            <div class="text-sm text-red-800">
              <p class="font-semibold">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Back to Login -->
        <div class="mt-6 text-center">
          <router-link to="/login" class="text-sm text-gray-900 hover:underline flex items-center justify-center">
            <i class="fa-solid fa-arrow-left mr-2"></i>
            TEXT
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Determine mode based on URL parameters
const mode = ref(route.query.token ? 'reset' : 'forgot')

const form = ref({
  email: ''
})

const resetForm = ref({
  newPassword: '',
  confirmPassword: ''
})

const loading = ref(false)
const success = ref('')
const error = ref('')
const mockLink = ref('')

// ==================== Forgot Password ====================
const handleForgotPassword = async () => {
  loading.value = true
  success.value = ''
  error.value = ''
  mockLink.value = ''

  try {
    const response = await fetch('http://localhost:3001/api/v1/users/forgot-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email: form.value.email })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Failed to send reset link')
    }

    success.value = data.message
    mockLink.value = data.mockLink || ''
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// ==================== Reset Password ====================
const handleResetPassword = async () => {
  if (resetForm.value.newPassword !== resetForm.value.confirmPassword) {
    error.value = 'Passwords do not match!'
    return
  }

  if (resetForm.value.newPassword.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await fetch('http://localhost:3001/api/v1/users/reset-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        token: route.query.token,
        email: route.query.email,
        newPassword: resetForm.value.newPassword
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Failed to reset password')
    }

    // Success - redirect to login
    alert('Password reset successful! Please login with your new password.')
    router.push('/auth')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Validate token on mount
onMounted(() => {
  if (mode.value === 'reset') {
    if (!route.query.token || !route.query.email) {
      error.value = 'Invalid reset link. Please request a new one.'
      setTimeout(() => {
        router.push('/forgot-password')
      }, 3000)
    }
  }
})
</script>
