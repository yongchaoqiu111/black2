import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ordersApi } from '@/services/api'

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
      .reduce((sum, order) => sum + order.amount, 0)
  })
  
  // Actions
  async function loadOrders() {
    try {
      const response = await ordersApi.getAll()
      console.log('API response:', response.data)
      orders.value = response.data.map(tx => ({
        id: tx.tx_id,
        items: [{
          name: 'Product',
          price: tx.amount,
          quantity: 1,
          image: '/placeholder.png'
        }],
        total: tx.amount,
        amount: tx.amount,
        status: tx.status,
        paymentMethod: 'usdt_trc20',
        contractHash: tx.contract_hash || '',
        fileHash: tx.file_hash || null,
        createdAt: tx.timestamp || new Date().toISOString(),
        txId: tx.tx_id,
        fromAddress: tx.from_address,
        toAddress: tx.to_address,
        tu1Address: tx.tu1_address || null,
        tu1Amount: tx.tu1_amount || 0,
        tu2Address: tx.tu2_address || null,
        tu2Amount: tx.tu2_amount || 0,
        tu3Address: tx.tu3_address || null,
        tu3Amount: tx.tu3_amount || 0,
        settlementStatus: tx.settlement_status || 'pending'
      }))
      console.log('Loaded orders:', orders.value.length)
    } catch (error) {
      console.error('Failed to load orders:', error)
    }
  }
  
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
    loadOrders,
    createOrder,
    updateOrderStatus,
    getOrderById,
    cancelOrder,
    completeOrder
  }
})
