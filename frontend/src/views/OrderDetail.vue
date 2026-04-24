<template>
  <div class="min-h-screen bg-gray-50 pt-24 pb-12">
    <div class="max-w-4xl mx-auto px-4 md:px-6">
      <!-- Back button -->
      <div class="mb-6">
        <router-link to="/orders" class="text-gray-600 hover:text-gray-900 flex items-center">
          <i class="fa-solid fa-arrow-left mr-2"></i>
          返回订单列表
        </router-link>
      </div>

      <div v-if="order" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <!-- Order Header -->
        <div class="border-b border-gray-200 pb-6 mb-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h1 class="text-2xl font-bold text-gray-900 mb-2">订单详情</h1>
              <p class="text-sm text-gray-600">订单号：{{ order.id }}</p>
              <p class="text-sm text-gray-600">创建时间：{{ formatDate(order.createdAt) }}</p>
            </div>
            <div class="text-right">
              <div class="text-3xl font-bold text-purple-600">{{ order.amount }} USDT</div>
              <span :class="getStatusBadgeClass(order.status)">
                {{ getStatusText(order.status) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Transaction Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div class="bg-gray-50 p-4 rounded-lg">
            <h3 class="font-semibold text-gray-900 mb-3">买家信息</h3>
            <div class="space-y-2 text-sm">
              <div>
                <span class="text-gray-600">地址：</span>
                <span class="font-mono">{{ order.fromAddress }}</span>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 p-4 rounded-lg">
            <h3 class="font-semibold text-gray-900 mb-3">卖家信息</h3>
            <div class="space-y-2 text-sm">
              <div>
                <span class="text-gray-600">地址：</span>
                <span class="font-mono">{{ order.toAddress }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Contract Hash -->
        <div class="bg-gray-50 p-4 rounded-lg mb-6">
          <h3 class="font-semibold text-gray-900 mb-3">合同信息</h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="text-gray-600">合同哈希：</span>
              <div class="font-mono text-xs bg-white p-2 rounded mt-1 break-all">{{ order.contractHash }}</div>
            </div>
            <div>
              <span class="text-gray-600">交付物哈希：</span>
              <span class="font-mono text-xs">{{ order.fileHash || '未提交' }}</span>
            </div>
          </div>
        </div>

        <!-- Referral Commission -->
        <div class="bg-blue-50 p-4 rounded-lg mb-6">
          <h3 class="font-semibold text-gray-900 mb-3">推荐分润</h3>
          <div class="space-y-3">
            <div v-if="order.tu1Address" class="flex justify-between items-center bg-white p-3 rounded">
              <div>
                <span class="text-sm text-gray-600">第一代推荐人：</span>
                <span class="font-mono text-xs">{{ order.tu1Address }}</span>
              </div>
              <div class="text-green-600 font-semibold">{{ order.tu1Amount }} USDT (5%)</div>
            </div>
            <div v-if="order.tu2Address" class="flex justify-between items-center bg-white p-3 rounded">
              <div>
                <span class="text-sm text-gray-600">第二代推荐人：</span>
                <span class="font-mono text-xs">{{ order.tu2Address }}</span>
              </div>
              <div class="text-green-600 font-semibold">{{ order.tu2Amount }} USDT (3%)</div>
            </div>
            <div v-if="order.tu3Address" class="flex justify-between items-center bg-white p-3 rounded">
              <div>
                <span class="text-sm text-gray-600">第三代推荐人：</span>
                <span class="font-mono text-xs">{{ order.tu3Address }}</span>
              </div>
              <div class="text-green-600 font-semibold">{{ order.tu3Amount }} USDT (2%)</div>
            </div>
            <div v-if="!order.tu1Address && !order.tu2Address && !order.tu3Address" class="text-sm text-gray-600">
              无推荐人
            </div>
          </div>
        </div>

        <!-- Settlement Status -->
        <div v-if="order.status === 'completed'" class="bg-green-50 p-4 rounded-lg mb-6">
          <h3 class="font-semibold text-gray-900 mb-3">结算状态</h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="text-gray-600">分润状态：</span>
              <span :class="order.settlementStatus === 'completed' ? 'text-green-600' : 'text-yellow-600'">
                {{ order.settlementStatus === 'completed' ? '已完成' : '处理中' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex space-x-4 pt-6 border-t border-gray-200">
          <!-- Paid Status: Buyer can download, confirm receipt, or request refund -->
          <template v-if="order.status === 'paid'">
            <button 
              @click="handleDownload"
              class="flex-1 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              <i class="fa-solid fa-download mr-2"></i>
              下载商品
            </button>
            
            <button 
              @click="handleConfirmReceipt"
              class="flex-1 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
            >
              <i class="fa-solid fa-check mr-2"></i>
              确认收货
            </button>

            <button 
              @click="handleRequestRefund"
              class="flex-1 py-3 bg-orange-600 text-white font-semibold rounded-lg hover:bg-orange-700 transition-colors"
            >
              <i class="fa-solid fa-rotate-left mr-2"></i>
              申请退款
            </button>
          </template>

          <!-- Shipped Status: Buyer can confirm or request refund -->
          <template v-if="order.status === 'shipped'">
            <button 
              @click="handleConfirmReceipt"
              class="flex-1 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
            >
              <i class="fa-solid fa-check mr-2"></i>
              确认收货
            </button>

            <button 
              @click="handleRequestRefund"
              class="flex-1 py-3 bg-orange-600 text-white font-semibold rounded-lg hover:bg-orange-700 transition-colors"
            >
              <i class="fa-solid fa-rotate-left mr-2"></i>
              申请退款
            </button>
          </template>

          <!-- Completed Status: Can download -->
          <button 
            v-if="order.status === 'completed'"
            @click="handleDownload"
            class="flex-1 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            <i class="fa-solid fa-download mr-2"></i>
            下载商品
          </button>

          <!-- Refunded Status -->
          <div v-if="order.status === 'refunded'" class="w-full text-center py-4 text-gray-600">
            <i class="fa-solid fa-check-circle mr-2"></i>
            已退款
          </div>

          <!-- Disputed Status: Waiting for arbitration or can refund -->
          <template v-if="order.status === 'disputed'">
            <!-- Arbitration Progress -->
            <div class="w-full bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <div class="flex items-center text-yellow-800 mb-3">
                <i class="fa-solid fa-triangle-exclamation mr-2"></i>
                <span class="font-semibold">仲裁中</span>
              </div>
              
              <!-- Arbitration Details -->
              <div v-if="arbitrationInfo" class="space-y-3">
                <div class="text-sm">
                  <span class="text-gray-600">买家理由：</span>
                  <p class="mt-1 text-gray-900">{{ arbitrationInfo.buyer_reason }}</p>
                </div>
                
                <div v-if="arbitrationInfo.seller_evidence" class="text-sm">
                  <span class="text-gray-600">卖家证据：</span>
                  <p class="mt-1 text-gray-900">{{ arbitrationInfo.seller_evidence }}</p>
                </div>
                
                <div class="text-sm">
                  <span class="text-gray-600">仲裁状态：</span>
                  <span :class="{
                    'text-blue-600': arbitrationInfo.status === 'evidence_collection',
                    'text-purple-600': arbitrationInfo.status === 'arbitrating',
                    'text-green-600': arbitrationInfo.status === 'completed'
                  }">
                    {{ getArbitrationStatusText(arbitrationInfo.status) }}
                  </span>
                </div>
                
                <div v-if="arbitrationInfo.deadline && arbitrationInfo.status !== 'completed'" class="text-sm">
                  <span class="text-gray-600">剩余时间：</span>
                  <span class="font-mono text-red-600">{{ formatCountdown(arbitrationInfo.deadline) }}</span>
                </div>
                
                <div v-if="arbitrationInfo.verdict" class="text-sm bg-white p-3 rounded mt-2">
                  <span class="text-gray-600">裁决结果：</span>
                  <span :class="arbitrationInfo.verdict === 'buyer_wins' ? 'text-green-600' : 'text-blue-600'" class="font-semibold">
                    {{ arbitrationInfo.verdict === 'buyer_wins' ? '买家胜诉' : '卖家胜诉' }}
                  </span>
                  <p class="mt-1 text-gray-700">{{ arbitrationInfo.verdict_reason }}</p>
                </div>
              </div>
              
              <p v-else class="text-sm text-yellow-700">订单已冻结，等待仲裁委员会处理...</p>
            </div>
            
            <!-- Seller Evidence Submission (only for seller) -->
            <div v-if="isSeller && (!arbitrationInfo || arbitrationInfo.status === 'evidence_collection')" class="mb-4">
              <textarea
                v-model="sellerEvidence"
                placeholder="请输入您的证据和说明..."
                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                rows="4"
              ></textarea>
              <button 
                @click="handleSubmitEvidence"
                :disabled="!sellerEvidence"
                class="mt-2 w-full py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <i class="fa-solid fa-upload mr-2"></i>
                提交证据
              </button>
            </div>
          </template>
          
          <!-- Refund Requested Status: Seller needs to approve/reject -->
          <template v-if="order.status === 'refund_requested'">
            <div class="w-full bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
              <div class="flex items-center text-orange-800 mb-3">
                <i class="fa-solid fa-clock mr-2"></i>
                <span class="font-semibold">退款申请中</span>
              </div>
              
              <div v-if="arbitrationInfo" class="space-y-3">
                <div class="text-sm">
                  <span class="text-gray-600">买家退款理由：</span>
                  <p class="mt-1 text-gray-900">{{ arbitrationInfo.buyer_reason }}</p>
                </div>
                
                <div v-if="arbitrationInfo.deadline" class="text-sm">
                  <span class="text-gray-600">剩余响应时间：</span>
                  <span class="font-mono text-red-600">{{ formatCountdown(arbitrationInfo.deadline) }}</span>
                </div>
                
                <p class="text-sm text-orange-700 mt-2">
                  <i class="fa-solid fa-info-circle mr-1"></i>
                  如果 48 小时内未响应，系统将自动批准退款。
                </p>
              </div>
            </div>
            
            <!-- Seller Approval Buttons -->
            <div v-if="isSeller" class="grid grid-cols-2 gap-4 mb-4">
              <button 
                @click="handleApproveRefund"
                class="py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
              >
                <i class="fa-solid fa-check mr-2"></i>
                同意退款
              </button>
              
              <button 
                @click="handleRejectRefund"
                class="py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
              >
                <i class="fa-solid fa-times mr-2"></i>
                拒绝退款（进入仲裁）
              </button>
            </div>
            
            <div v-else class="w-full text-center py-4 text-gray-600">
              <i class="fa-solid fa-hourglass-half mr-2"></i>
              等待卖家处理退款申请...
            </div>
          </template>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else class="text-center py-16">
        <div class="text-gray-400 text-xl">加载中...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useOrderStore } from '@/stores/orders'
import { ordersApi } from '@/services/api'

const route = useRoute()
const orderStore = useOrderStore()
const order = ref(null)
const arbitrationInfo = ref(null)
const sellerEvidence = ref('')
const isSeller = ref(false)

onMounted(async () => {
  const txId = route.params.id
  try {
    const response = await ordersApi.getById(txId)
    const tx = response.data
    
    // Check if current user is the seller
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
    isSeller.value = currentUser.address === tx.to_address
    
    order.value = {
      id: tx.tx_id,
      amount: tx.amount,
      status: tx.status,
      contractHash: tx.contract_hash,
      fileHash: tx.file_hash,
      createdAt: tx.created_at || new Date().toISOString(),
      txId: tx.tx_id,
      fromAddress: tx.from_address,
      toAddress: tx.to_address,
      tu1Address: tx.tu1_address,
      tu1Amount: tx.tu1_amount,
      tu2Address: tx.tu2_address,
      tu2Amount: tx.tu2_amount,
      tu3Address: tx.tu3_address,
      tu3Amount: tx.tu3_amount,
      settlementStatus: tx.settlement_status
    }
    
    // Load arbitration info if disputed or refund_requested
    if (tx.status === 'disputed' || tx.status === 'refund_requested') {
      await loadArbitrationInfo(txId)
    }
  } catch (error) {
    console.error('Failed to load order:', error)
    alert('加载订单失败')
  }
})

const loadArbitrationInfo = async (txId) => {
  try {
    const response = await fetch(`http://localhost:3000/api/v1/arbitration/${txId}/status`)
    if (response.ok) {
      arbitrationInfo.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to load arbitration info:', error)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getStatusBadgeClass = (status) => {
  const classes = {
    paid: 'px-3 py-1 text-sm font-medium bg-blue-100 text-blue-800 rounded-full',
    shipped: 'px-3 py-1 text-sm font-medium bg-purple-100 text-purple-800 rounded-full',
    completed: 'px-3 py-1 text-sm font-medium bg-green-100 text-green-800 rounded-full',
    refunded: 'px-3 py-1 text-sm font-medium bg-red-100 text-red-800 rounded-full'
  }
  return classes[status] || 'px-3 py-1 text-sm font-medium bg-gray-100 text-gray-800 rounded-full'
}

const getStatusText = (status) => {
  const texts = {
    paid: '已支付/待发货',
    shipped: '已发货/待收货',
    completed: '已完成',
    refunded: '已退款',
    disputed: '仲裁中'
  }
  return texts[status] || status
}

const getArbitrationStatusText = (status) => {
  const texts = {
    evidence_collection: '证据收集中',
    arbitrating: '仲裁判定中',
    completed: '已完成'
  }
  return texts[status] || status
}

const formatCountdown = (deadline) => {
  if (!deadline) return '未知'
  
  const deadlineDate = new Date(deadline)
  const now = new Date()
  const diff = deadlineDate - now
  
  if (diff <= 0) return '已超时'
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  return `${hours}小时${minutes}分钟`
}

const handleConfirmReceipt = async () => {
  if (!confirm('确认收货后将开始分润，确定要确认吗？')) {
    return
  }

  try {
    await ordersApi.complete(order.value.id)
    alert('确认收货成功！分润处理中...')
    // Reload order
    const response = await ordersApi.getById(order.value.id)
    const tx = response.data
    order.value.status = tx.status
    order.value.settlementStatus = tx.settlement_status
  } catch (error) {
    console.error('Failed to confirm receipt:', error)
    alert('确认收货失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleDispute = async () => {
  const reason = prompt('请输入仲裁理由：')
  if (!reason) return

  try {
    const response = await ordersApi.dispute(order.value.id, { reason })
    alert('仲裁申请成功！订单已冻结，卖家有 48 小时提交证据。')
    
    // Reload order to get updated status
    const reloadResponse = await ordersApi.getById(order.value.id)
    order.value.status = reloadResponse.data.status
    
    // Load arbitration info
    await loadArbitrationInfo(order.value.id)
  } catch (error) {
    console.error('Failed to dispute:', error)
    alert('申请仲裁失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleRequestRefund = async () => {
  const reason = prompt('请输入退款理由：')
  if (!reason) return
  
  try {
    const response = await fetch(`http://localhost:3000/api/v1/transactions/${order.value.id}/refund`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ reason })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '申请失败')
    }
    
    alert('退款申请已提交！卖家有 48 小时响应。')
    
    // Reload order
    const reloadResponse = await ordersApi.getById(order.value.id)
    order.value.status = reloadResponse.data.status
    
    // Load arbitration info
    await loadArbitrationInfo(order.value.id)
  } catch (error) {
    console.error('Failed to request refund:', error)
    alert('申请退款失败：' + error.message)
  }
}

const handleApproveRefund = async () => {
  if (!confirm('确认同意退款？款项将立即退回买家账户。')) {
    return
  }
  
  try {
    const response = await fetch(`http://localhost:3000/api/v1/refunds/${order.value.id}/approve`, {
      method: 'POST'
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '操作失败')
    }
    
    alert('已同意退款，款项已退回买家账户。')
    
    // Reload order
    const reloadResponse = await ordersApi.getById(order.value.id)
    order.value.status = reloadResponse.data.status
  } catch (error) {
    console.error('Failed to approve refund:', error)
    alert('操作失败：' + error.message)
  }
}

const handleRejectRefund = async () => {
  const reason = prompt('请输入拒绝退款的理由（将作为仲裁证据）：')
  if (!reason) return
  
  if (!confirm('确认拒绝退款？订单将进入仲裁流程。')) {
    return
  }
  
  try {
    const response = await fetch(`http://localhost:3000/api/v1/refunds/${order.value.id}/reject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ reason })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '操作失败')
    }
    
    alert('已拒绝退款，订单进入仲裁流程。')
    
    // Reload order
    const reloadResponse = await ordersApi.getById(order.value.id)
    order.value.status = reloadResponse.data.status
    
    // Load arbitration info
    await loadArbitrationInfo(order.value.id)
  } catch (error) {
    console.error('Failed to reject refund:', error)
    alert('操作失败：' + error.message)
  }
}

const handleSubmitEvidence = async () => {
  if (!sellerEvidence.value.trim()) {
    alert('请输入证据内容')
    return
  }
  
  try {
    const response = await fetch(`http://localhost:3000/api/v1/arbitration/${order.value.id}/seller-evidence`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        evidence: sellerEvidence.value
      })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '提交失败')
    }
    
    alert('证据提交成功！系统将在 48 小时后自动裁决。')
    sellerEvidence.value = ''
    
    // Reload arbitration info
    await loadArbitrationInfo(order.value.id)
  } catch (error) {
    console.error('Failed to submit evidence:', error)
    alert('提交证据失败：' + error.message)
  }
}

const handleRefund = async () => {
  if (!confirm('确认要申请退款吗？退款金额将返回到您的 AI 钱包。')) {
    return
  }

  try {
    const response = await ordersApi.refund(order.value.id)
    alert(`退款成功！${response.message}`)
    
    // Reload order
    const reloadResponse = await ordersApi.getById(order.value.id)
    order.value.status = reloadResponse.data.status
  } catch (error) {
    console.error('Failed to refund:', error)
    alert('退款失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleDownload = () => {
  // TODO: Implement actual download logic
  alert('下载商品：' + order.value.contractHash)
}
</script>
