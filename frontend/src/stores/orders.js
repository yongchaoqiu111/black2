import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useOrderStore = defineStore('orders', () => {
  // State
  const orders = ref([])
  
  // Getters
  const pendingOrders = computed(() => {
    return orders.value.filter(order => order.status === 'pending')
  })
  
  const completedOrders = computed(() => {
    return orders.value.filter(order => order.status === 'completed')
  })
  
  const totalSpent = computed(() => {
    return orders.value
      .filter(order => order.status === 'completed')
      .reduce((sum, order) => sum + order.total, 0)
  })
  
  // Actions
  function createOrder(cartItems, paymentMethod) {
    const order = {
      id: `ORD-${Date.now()}`,
      items: [...cartItems],
      total: cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0),
      status: 'pending',
      paymentMethod: paymentMethod,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    orders.value.unshift(order)
    saveToLocalStorage()
    
    return order
  }
  
  function updateOrderStatus(orderId, status) {
    const order = orders.value.find(o => o.id === orderId)
    if (order) {
      order.status = status
      order.updatedAt = new Date().toISOString()
      saveToLocalStorage()
    }
  }
  
  function getOrderById(orderId) {
    return orders.value.find(o => o.id === orderId)
  }
  
  function cancelOrder(orderId) {
    updateOrderStatus(orderId, 'cancelled')
  }
  
  function completeOrder(orderId) {
    updateOrderStatus(orderId, 'completed')
  }
  
  function saveToLocalStorage() {
    localStorage.setItem('orders', JSON.stringify(orders.value))
  }
  
  function loadFromLocalStorage() {
    const saved = localStorage.getItem('orders')
    if (saved) {
      try {
        orders.value = JSON.parse(saved)
      } catch (e) {
        console.error('Failed to load orders from localStorage:', e)
      }
    }
  }
  
  // Initialize
  loadFromLocalStorage()
  
  return {
    orders,
    pendingOrders,
    completedOrders,
    totalSpent,
    createOrder,
    updateOrderStatus,
    getOrderById,
    cancelOrder,
    completeOrder
  }
})
