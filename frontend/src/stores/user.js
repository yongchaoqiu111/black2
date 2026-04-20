import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref(false)
  const userInfo = ref({
    username: '',
    avatar: '',
    coins: 1000,
    memberLevel: 'normal'
  })

  function login() {
    isLoggedIn.value = true
  }

  function logout() {
    isLoggedIn.value = false
    userInfo.value = {
      username: '',
      avatar: '',
      coins: 1000,
      memberLevel: 'normal'
    }
  }

  return {
    isLoggedIn,
    userInfo,
    login,
    logout
  }
})
