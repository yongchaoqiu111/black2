import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  // State
  const items = ref([])
  
  // Getters
  const totalItems = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })
  
  const totalPrice = computed(() => {
    return items.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  })
  
  const isEmpty = computed(() => {
    return items.value.length === 0
  })
  
  // Actions
  function addItem(product) {
    const existingItem = items.value.find(item => item.id === product.id)
    
    if (existingItem) {
      existingItem.quantity += 1
    } else {
      items.value.push({
        id: product.id,
        name: product.name,
        price: product.price,
        image: product.image || 'https://via.placeholder.com/100x100?text=Product',
        seller: product.seller,
        quantity: 1,
        addedAt: new Date().toISOString()
      })
    }
    
    saveToLocalStorage()
  }
  
  function removeItem(productId) {
    const index = items.value.findIndex(item => item.id === productId)
    if (index > -1) {
      items.value.splice(index, 1)
      saveToLocalStorage()
    }
  }
  
  function updateQuantity(productId, quantity) {
    const item = items.value.find(item => item.id === productId)
    if (item) {
      if (quantity <= 0) {
        removeItem(productId)
      } else {
        item.quantity = quantity
        saveToLocalStorage()
      }
    }
  }
  
  function clearCart() {
    items.value = []
    saveToLocalStorage()
  }
  
  function saveToLocalStorage() {
    localStorage.setItem('cart', JSON.stringify(items.value))
  }
  
  function loadFromLocalStorage() {
    const saved = localStorage.getItem('cart')
    if (saved) {
      try {
        items.value = JSON.parse(saved)
      } catch (e) {
        console.error('Failed to load cart from localStorage:', e)
      }
    }
  }
  
  // Initialize
  loadFromLocalStorage()
  
  return {
    items,
    totalItems,
    totalPrice,
    isEmpty,
    addItem,
    removeItem,
    updateQuantity,
    clearCart
  }
})
