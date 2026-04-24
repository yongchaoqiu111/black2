import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // Load from localStorage on init
  const savedUser = localStorage.getItem('user')
  const savedToken = localStorage.getItem('token')
  
  const isLoggedIn = ref(!!savedToken)
  const user = ref(savedUser ? JSON.parse(savedUser) : null)
  const userInfo = ref({
    username: '',
    avatar: '',
    coins: 1000,
    memberLevel: 'normal'
  })

  // Computed wallet addresses
  const walletAddress = computed(() => {
    return user.value?.address || user.value?.wallet_address || null
  })
  
  const aiWalletAddress = computed(() => {
    return user.value?.ai_wallet_address || user.value?.ai_address || null
  })

  function login(userData) {
    isLoggedIn.value = true
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function logout() {
    isLoggedIn.value = false
    user.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('walletAddress') // Clear any cached wallet address
    userInfo.value = {
      username: '',
      avatar: '',
      coins: 1000,
      memberLevel: 'normal'
    }
  }

  function setUser(userData) {
    user.value = userData
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    }
  }

  return {
    isLoggedIn,
    user,
    userInfo,
    walletAddress,
    aiWalletAddress,
    login,
    logout,
    setUser
  }
})
