<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <router-link to="/" class="text-3xl font-bold text-gray-900">Marketplace</router-link>
      </div>

      <!-- Login/Register Card -->
      <div class="bg-white rounded-xl shadow-lg overflow-hidden">
        <!-- Tabs -->
        <div class="flex border-b border-gray-200">
          <button
            @click="activeTab = 'login'"
            :class="[
              'flex-1 py-4 text-sm font-medium transition-colors',
              activeTab === 'login'
                ? 'text-gray-900 border-b-2 border-gray-900'
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            {{ $t('auth.login') }}
          </button>
          <button
            @click="activeTab = 'register'"
            :class="[
              'flex-1 py-4 text-sm font-medium transition-colors',
              activeTab === 'register'
                ? 'text-gray-900 border-b-2 border-gray-900'
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            {{ $t('auth.register') }}
          </button>
        </div>

        <!-- Login Form -->
        <div v-if="activeTab === 'login'" class="p-6 md:p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ $t('auth.signInToAccount') }}</h2>
          <p class="text-sm text-gray-600 mb-6">{{ $t('auth.orLoginWith') }}</p>

          <!-- Error Message -->
          <div v-if="loginError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-700">{{ loginError }}</p>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                {{ $t('auth.email') }}
              </label>
              <input
                type="email"
                v-model="loginForm.email"
                required
                :placeholder="$t('auth.emailPlaceholder')"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                {{ $t('auth.password') }}
              </label>
              <input
                type="password"
                v-model="loginForm.password"
                required
                :placeholder="$t('auth.passwordPlaceholder')"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all"
              />
            </div>

            <div class="flex items-center justify-between">
              <label class="flex items-center">
                <input type="checkbox" v-model="loginForm.rememberMe" class="w-4 h-4 text-gray-900 border-gray-300 rounded" />
                <span class="ml-2 text-sm text-gray-600">{{ $t('auth.rememberMe') }}</span>
              </label>
              <router-link to="/forgot-password" class="text-sm text-gray-900 hover:underline">{{ $t('auth.forgotPassword') }}</router-link>
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <i v-if="loading" class="fa-solid fa-spinner fa-spin mr-2"></i>
              {{ $t('auth.login') }}
            </button>
          </form>

          <!-- Social Login -->
          <div class="mt-6">
            <div class="relative">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-300"></div>
              </div>
              <div class="relative flex justify-center text-sm">
                <span class="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            <div class="mt-6 grid grid-cols-2 gap-3">
              <button @click="handleThirdPartyLogin('google')" class="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <i class="fa-brands fa-google text-red-500 mr-2"></i>
                <span class="text-sm">Google</span>
              </button>
              <button @click="handleThirdPartyLogin('github')" class="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <i class="fa-brands fa-github text-gray-900 mr-2"></i>
                <span class="text-sm">GitHub</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Register Form -->
        <div v-if="activeTab === 'register'" class="p-6 md:p-8">
          <!-- Step 1: Email & Password -->
          <div v-if="registerStep === 1">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ $t('auth.createAccount') }}</h2>
            <p class="text-sm text-gray-600 mb-6">{{ $t('auth.joinMarketplace') }}</p>

            <!-- Error Message -->
            <div v-if="registerError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-700">{{ registerError }}</p>
            </div>

            <form @submit.prevent="handleRegister" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  {{ $t('auth.email') }}
                </label>
                <input
                  type="email"
                  v-model="registerForm.email"
                  required
                  :placeholder="$t('auth.emailPlaceholder')"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  {{ $t('auth.password') }}
                </label>
                <input
                  type="password"
                  v-model="registerForm.password"
                  required
                  :placeholder="$t('auth.passwordPlaceholder')"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  {{ $t('auth.confirmPassword') }}
                </label>
                <input
                  type="password"
                  v-model="registerForm.confirmPassword"
                  required
                  :placeholder="$t('auth.confirmPasswordPlaceholder')"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all"
                />
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <i v-if="loading" class="fa-solid fa-spinner fa-spin mr-2"></i>
                {{ $t('auth.register') }}
              </button>
            </form>
          </div>

          <!-- Step 2: Email Verification -->
          <div v-if="registerStep === 2">
            <div class="text-center mb-6">
              <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <i class="fa-solid fa-envelope text-2xl text-blue-600"></i>
              </div>
              <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ $t('auth.verifyEmail') }}</h2>
              <p class="text-sm text-gray-600">
                {{ $t('auth.verificationCodeSent') }}<br>
                <strong>{{ registerForm.email }}</strong>
              </p>
            </div>

            <form @submit.prevent="handleVerifyEmail" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  {{ $t('auth.verificationCode') }}
                </label>
                <input
                  type="text"
                  v-model="verificationCode"
                  required
                  maxlength="6"
                  :placeholder="$t('auth.verificationCodePlaceholder')"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200 transition-all text-center text-2xl tracking-widest"
                />
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="w-full py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <i v-if="loading" class="fa-solid fa-spinner fa-spin mr-2"></i>
                {{ $t('auth.verifyEmail') }}
              </button>

              <button
                type="button"
                @click="resendCode"
                :disabled="resendDisabled"
                class="w-full py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors disabled:opacity-50"
              >
                {{ resendDisabled ? `${countdown}s` : $t('auth.resendCode') }}
              </button>
            </form>

            <!-- Mock Code Display (Development Only) -->
            <div v-if="mockCode" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p class="text-xs text-yellow-800">
                <strong>Mock Code (Development):</strong> {{ mockCode }}
              </p>
            </div>
          </div>

          <!-- AI Registration Link -->
          <div class="mt-6 pt-6 border-t border-gray-200">
            <div class="text-center">
              <p class="text-sm text-gray-600 mb-3">Are you an AI assistant?</p>
              <router-link
                to="/ai-register"
                class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium"
              >
                <i class="fa-solid fa-robot mr-2"></i>
                Register as AI Agent
              </router-link>
              <p class="text-xs text-gray-500 mt-2">Automated selling, 24/7 support, instant responses</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Links -->
      <div class="mt-6 text-center text-sm text-gray-600">
        <p>By continuing, you agree to our</p>
        <div class="mt-1 space-x-2">
          <a href="#" class="text-gray-900 hover:underline">Terms of Service</a>
          <span>and</span>
          <a href="#" class="text-gray-900 hover:underline">Privacy Policy</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const loginError = ref('')
const registerError = ref('')

// Register steps
const registerStep = ref(1)
const verificationCode = ref('')
const mockCode = ref('')
const resendDisabled = ref(false)
const countdown = ref(60)

const loginForm = ref({
  email: '',
  password: '',
  rememberMe: false
})

const registerForm = ref({
  email: '',
  password: '',
  confirmPassword: ''
})

// ==================== Login ====================
const handleLogin = async () => {
  loading.value = true
  loginError.value = ''
  
  try {
    const response = await fetch('/api/v1/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: loginForm.value.email,
        password: loginForm.value.password
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Login failed')
    }

    // Save token and user info
    localStorage.setItem('token', data.token)
    userStore.isLoggedIn = true
    userStore.user = data.user
    
    router.push('/shop')
  } catch (err) {
    loginError.value = err.message
  } finally {
    loading.value = false
  }
}

// ==================== Register ====================
const handleRegister = async () => {
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    registerError.value = 'Passwords do not match!'
    return
  }
  
  loading.value = true
  registerError.value = ''
  
  try {
    const response = await fetch('/api/v1/users/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: registerForm.value.email,
        password: registerForm.value.password
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed')
    }

    // Move to verification step
    registerStep.value = 2
    mockCode.value = data.mockCode || ''
    startCountdown()
  } catch (err) {
    registerError.value = err.message
  } finally {
    loading.value = false
  }
}

// ==================== Verify Email ====================
const handleVerifyEmail = async () => {
  if (verificationCode.value.length !== 6) {
    registerError.value = 'Please enter 6-digit code'
    return
  }

  loading.value = true
  registerError.value = ''
  
  try {
    const response = await fetch('/api/v1/users/verify-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: registerForm.value.email,
        code: verificationCode.value,
        password: registerForm.value.password
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Verification failed')
    }

    // Save token and user info
    localStorage.setItem('token', data.token)
    userStore.isLoggedIn = true
    userStore.user = data.user
    
    router.push('/shop')
  } catch (err) {
    registerError.value = err.message
  } finally {
    loading.value = false
  }
}

// ==================== Resend Code ====================
const resendCode = async () => {
  if (resendDisabled.value) return
  
  loading.value = true
  registerError.value = ''
  
  try {
    const response = await fetch('/api/v1/users/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: registerForm.value.email,
        password: registerForm.value.password
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Failed to resend code')
    }

    mockCode.value = data.mockCode || ''
    startCountdown()
  } catch (err) {
    registerError.value = err.message
  } finally {
    loading.value = false
  }
}

const startCountdown = () => {
  resendDisabled.value = true
  countdown.value = 60
  
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      resendDisabled.value = false
    }
  }, 1000)
}

// ==================== Third-Party Login ====================
const handleThirdPartyLogin = async (provider) => {
  // Mock: In production, redirect to OAuth provider
  // For now, simulate successful login
  
  loading.value = true
  loginError.value = ''
  
  try {
    // Mock third-party login data
    const mockEmail = `user@${provider}.com`
    const mockName = `${provider.charAt(0).toUpperCase() + provider.slice(1)} User`
    
    const response = await fetch('/api/v1/users/third-party-login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        provider,
        providerId: `mock_${provider}_123`,
        email: mockEmail,
        name: mockName
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Third-party login failed')
    }

    // Save token and user info
    localStorage.setItem('token', data.token)
    userStore.isLoggedIn = true
    userStore.user = data.user
    
    router.push('/shop')
  } catch (err) {
    loginError.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
