<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-gray-900">发布商品</h1>
        <p class="text-gray-600 mt-2">上架你的 AI 产品或数字资产</p>
      </div>
    </div>

    <!-- Form -->
    <div class="max-w-4xl mx-auto px-4 py-8">
      <!-- Wallet Address Display -->
      <div v-if="walletAddress" class="mb-6 bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-purple-900">你的钱包地址</p>
            <code class="text-xs text-purple-700 font-mono break-all">{{ walletAddress }}</code>
          </div>
          <button 
            @click="copyWalletAddress"
            class="px-3 py-1.5 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 transition-colors"
          >
            <i class="fa-solid fa-copy mr-1"></i> 复制
          </button>
        </div>
        <p class="text-xs text-purple-600 mt-2">💰 商品销售收入将直接打入此地址</p>
      </div>

      <form @submit.prevent="handleSubmit" class="bg-white rounded-lg shadow-md p-8">
        <!-- Product Name -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            商品名称 *
          </label>
          <input 
            v-model="form.name" 
            type="text" 
            required
            placeholder="例如：USDT 自动发送机器人"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        <!-- Version & System Requirements -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              版本号 *
            </label>
            <input 
              v-model="form.version" 
              type="text" 
              required
              placeholder="v1.0.0"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              适配系统 *
            </label>
            <select 
              v-model="form.systemRequirements" 
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">选择系统</option>
              <option value="windows">Windows</option>
              <option value="macos">macOS</option>
              <option value="linux">Linux</option>
              <option value="cross_platform">跨平台</option>
              <option value="web">Web/浏览器</option>
              <option value="api">API服务</option>
            </select>
          </div>
        </div>

        <!-- Contract Template Selector -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            合同模板 *
          </label>
          <select 
            v-model="form.contractTemplate" 
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">选择合同模板</option>
            <option value="TPL_SOFTWARE_001">软件/工具销售合约</option>
            <option value="TPL_AI_TASK_001">AI定制化任务合约</option>
            <option value="TPL_TRAFFIC_001">AI引流服务合约</option>
            <option value="TPL_DATA_001">数据交付合约</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">选择模板将自动匹配标准化合约字段</p>
        </div>

        <!-- Quantifiable Metrics (Dynamic) -->
        <div class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-blue-900 flex items-center">
              <i class="fa-solid fa-chart-line text-blue-600 mr-2"></i>
              核心功能量化指标 *
            </h3>
            <button 
              type="button"
              @click="addMetric"
              class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
            >
              <i class="fa-solid fa-plus mr-1"></i> 添加
            </button>
          </div>
          
          <div v-for="(metric, index) in form.metrics" :key="index" class="flex gap-2 mb-2">
            <input 
              v-model="metric.name" 
              type="text" 
              placeholder="指标名称（例如：处理速度）"
              class="flex-1 px-3 py-2 border border-gray-300 rounded text-sm"
            />
            <input 
              v-model="metric.value" 
              type="text" 
              placeholder="数值（例如：100次/秒）"
              class="flex-1 px-3 py-2 border border-gray-300 rounded text-sm"
            />
            <button 
              type="button"
              @click="removeMetric(index)"
              class="px-2 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
            >
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
          
          <p v-if="form.metrics.length === 0" class="text-xs text-blue-600 mt-2">
            ⚠️ 请至少添加一个量化指标，这是仲裁的重要依据
          </p>
        </div>

        <!-- Product Description (Contract Content) -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            商品描述 / 合同内容 *
          </label>
          <textarea 
            v-model="form.description" 
            rows="4"
            required
            placeholder="简要描述商品功能和特点..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            @input="checkEffectPromise"
          ></textarea>
          
          <!-- Effect Promise Warning -->
          <div v-if="effectWarning" class="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p class="text-sm text-yellow-800">
              <i class="fa-solid fa-triangle-exclamation mr-1"></i>
              {{ effectWarning }}
            </p>
          </div>
        </div>

        <!-- Contract Terms (Standardized) -->
        <div class="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 class="font-semibold text-gray-900 mb-3 flex items-center">
            <i class="fa-solid fa-file-contract text-purple-600 mr-2"></i>
            合同条款（标准化）
          </h3>
          
          <!-- Delivery Time -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              交付时间 *
            </label>
            <select 
              v-model="form.contract.deliveryTime" 
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">选择交付时间</option>
              <option value="instant">即时交付（自动发送）</option>
              <option value="24h">24 小时内</option>
              <option value="3days">3 天内</option>
              <option value="7days">7 天内</option>
              <option value="custom">自定义</option>
            </select>
          </div>

          <!-- Refund Policy -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              退款政策 *
            </label>
            <select 
              v-model="form.contract.refundPolicy" 
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">选择退款政策</option>
              <option value="no_refund">不支持退款</option>
              <option value="7days">7 天内可退款</option>
              <option value="not_working">仅在不工作时退款</option>
              <option value="partial">部分退款</option>
            </select>
          </div>

          <!-- Usage License -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              使用授权 *
            </label>
            <select 
              v-model="form.contract.license" 
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">选择授权类型</option>
              <option value="personal">个人使用（单用户）</option>
              <option value="commercial">商业使用</option>
              <option value="unlimited">无限授权</option>
              <option value="subscription">订阅制（按月/年）</option>
            </select>
          </div>

          <!-- Support Period -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              技术支持期限
            </label>
            <select 
              v-model="form.contract.supportPeriod" 
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="none">无技术支持</option>
              <option value="30days">30 天</option>
              <option value="90days">90 天</option>
              <option value="1year">1 年</option>
              <option value="lifetime">终身支持</option>
            </select>
          </div>

          <p class="text-xs text-gray-500 mt-2">⚠️ 这些条款将生成标准化合约哈希，用于自动仲裁</p>
        </div>

        <!-- Price -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            价格（美元）*
          </label>
          <input 
            v-model.number="form.price" 
            type="number" 
            required
            min="0"
            step="0.01"
            placeholder="299.00"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        <!-- Category -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            分类 *
          </label>
          <select 
            v-model="form.category" 
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">选择分类</option>
            <option value="software">软件 / 工具</option>
            <option value="data">数据集</option>
            <option value="template">模板</option>
            <option value="service">服务</option>
            <option value="course">课程 / 教程</option>
          </select>
        </div>

        <!-- Seller Name -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            卖家名称 *
          </label>
          <input 
            v-model="form.seller" 
            type="text" 
            required
            placeholder="你的名字或品牌"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        <!-- Tags -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            标签（用逗号分隔）
          </label>
          <input 
            v-model="form.tags" 
            type="text" 
            placeholder="AI, 自动化, 交易"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <p class="text-xs text-gray-500 mt-1">多个标签用逗号分隔</p>
        </div>

        <!-- File Upload with Auto Hash -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            商品文件（自动计算 SHA-256 哈希）
          </label>
          <input 
            type="file" 
            @change="handleFileUpload"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <div v-if="form.fileHash" class="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs font-mono break-all">
            <i class="fa-solid fa-check-circle text-green-600 mr-1"></i>
            文件哈希: {{ form.fileHash }}
          </div>
          <p class="text-xs text-gray-500 mt-1">⚠️ 上传后将自动计算SHA-256哈希，用于合约存证</p>
        </div>

        <!-- Delivery Method -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            交付方式 *
          </label>
          <select 
            v-model="form.deliveryMethod" 
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">选择交付方式</option>
            <option value="api_key">API Key（数字商品）</option>
            <option value="download">文件下载链接</option>
            <option value="manual">人工交付</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">决定买家付款后如何获得商品</p>
        </div>

        <!-- Auto-Confirm Hours -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            自动确认时长（小时）*
          </label>
          <input 
            v-model.number="form.autoConfirmHours" 
            type="number" 
            required
            min="24"
            max="168"
            value="72"
            placeholder="72"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <p class="text-xs text-gray-500 mt-1">⚠️ 买家未主动确认时，系统将在X小时后自动确认并放款（24-168小时）</p>
        </div>

        <!-- Storage Plan -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            数据存储方案 *
          </label>
          <select 
            v-model="form.storagePlan" 
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">选择存储方案</option>
            <option value="30days">30天（$0.5/月）</option>
            <option value="365days">365天（$4/年）</option>
            <option value="10years">10年永久存储（$30）</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">商品文件和合约的存储期限，影响争议期间的证据留存</p>
        </div>

        <!-- Delivery Checklist -->
        <div class="mb-6 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
          <h3 class="font-semibold text-indigo-900 mb-3 flex items-center">
            <i class="fa-solid fa-list-check text-indigo-600 mr-2"></i>
            交付清单 *
          </h3>
          
          <div class="space-y-2">
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.deliveryChecklist.sourceCode" class="w-4 h-4 text-indigo-600" />
              <span class="text-sm text-gray-700">源代码</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.deliveryChecklist.documentation" class="w-4 h-4 text-indigo-600" />
              <span class="text-sm text-gray-700">文档说明</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.deliveryChecklist.apiKey" class="w-4 h-4 text-indigo-600" />
              <span class="text-sm text-gray-700">API Key</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.deliveryChecklist.tutorial" class="w-4 h-4 text-indigo-600" />
              <span class="text-sm text-gray-700">使用教程</span>
            </label>
            <label class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.deliveryChecklist.support" class="w-4 h-4 text-indigo-600" />
              <span class="text-sm text-gray-700">技术支持（首次设置）</span>
            </label>
          </div>
          <p class="text-xs text-indigo-600 mt-3">勾选所有交付内容，作为买家验收的依据</p>
        </div>

        <!-- Reputation Score & Margin -->
        <div class="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-900 flex items-center">
              <i class="fa-solid fa-shield-halved text-purple-600 mr-2"></i>
              信誉与保证金
            </h3>
            <span class="px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full">
              信誉分: {{ form.reputationScore }}/100
            </span>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-gray-500 mb-1">保证金比例</p>
              <p class="text-lg font-semibold text-gray-900">{{ marginPercentage }}%</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 mb-1">需冻结保证金</p>
              <p class="text-lg font-semibold text-purple-900">${{ marginAmount }}</p>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-3">⚠️ 信誉分低于60将无法发布商品，保证金用于违约赔付</p>
        </div>

        <!-- API Key (for API products) -->
        <div v-if="form.deliveryMethod === 'api_key'" class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            API Key / 访问凭证
          </label>
          <input 
            v-model="form.apiKey" 
            type="text" 
            placeholder="sk-xxxxxxxxxxxxx"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
          />
          <p class="text-xs text-gray-500 mt-1">买家付款后自动发送此 API Key</p>
        </div>

        <!-- Trial Price -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            试用价格（可选）
          </label>
          <input 
            v-model.number="form.trialPrice" 
            type="number" 
            min="0"
            step="0.01"
            placeholder="9.99"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <p class="text-xs text-gray-500 mt-1">设置试用版的低价（可选）</p>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-4">
          <button 
            type="submit"
            :disabled="loading"
            class="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            <i class="fa-solid fa-spinner fa-spin mr-2" v-if="loading"></i>
            {{ loading ? '发布中...' : '发布商品' }}
          </button>
          <button 
            type="button"
            @click="resetForm"
            class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            重置
          </button>
        </div>
      </form>

      <!-- Success Message -->
      <div v-if="success" class="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
        <div class="flex items-center">
          <i class="fa-solid fa-check-circle text-green-600 text-xl mr-3"></i>
          <div>
            <h3 class="font-semibold text-green-900">商品发布成功！</h3>
            <p class="text-green-700 text-sm mt-1">你的商品已上架到市场。</p>
          </div>
        </div>
        <button 
          @click="goToShop"
          class="mt-3 text-green-700 hover:text-green-900 text-sm font-medium"
        >
          去商店查看 →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { productsApi } from '@/services/api'

const router = useRouter()
const loading = ref(false)
const success = ref(false)
const walletAddress = ref('')
const effectWarning = ref('')

// Effect promise keywords for detection
const effectKeywords = [
  '可提升', '可提高', '可帮助', '可实现', '能保证', '确保',
  '盈利', '赚钱', '收益', '业绩', '转化率提升',
  '一定', '保证', 'guaranteed', 'promise', 'ensure profit',
  '可解决所有问题', '无风险', '稳赚'
]

const checkEffectPromise = () => {
  if (!form.description) {
    effectWarning.value = ''
    return
  }
  
  const detected = effectKeywords.filter(kw => form.description.toLowerCase().includes(kw.toLowerCase()))
  
  if (detected.length > 0) {
    effectWarning.value = '⚠️ 检测到效果承诺内容。根据协议规则，一旦买家投诉效果未达预期，仲裁将直接判定卖家违约，全额退款并扣除保证金。'
  } else {
    effectWarning.value = ''
  }
}

// Get wallet address from localStorage (set during registration/login)
onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  if (user.walletAddress) {
    walletAddress.value = user.walletAddress
    // Load reputation score from user data
    form.reputationScore = user.reputationScore || 100
  } else {
    // Fallback: generate a mock address for demo
    walletAddress.value = 'T' + Math.random().toString(36).substring(2, 15).toUpperCase() + Math.random().toString(36).substring(2, 15).toUpperCase()
    form.reputationScore = 100
  }
})

const form = reactive({
  name: '',
  description: '',
  price: null,
  version: '',
  systemRequirements: '',
  contractTemplate: '',
  metrics: [],
  category: '',
  seller: '',
  tags: '',
  fileHash: '',
  deliveryMethod: '',
  apiKey: '',
  trialPrice: null,
  autoConfirmHours: 72,
  storagePlan: '',
  deliveryChecklist: {
    sourceCode: false,
    documentation: false,
    apiKey: false,
    tutorial: false,
    support: false
  },
  reputationScore: 100,
  contract: {
    deliveryTime: '',
    refundPolicy: '',
    license: '',
    supportPeriod: 'none'
  }
})

const addMetric = () => {
  form.metrics.push({ name: '', value: '' })
}

const removeMetric = (index) => {
  form.metrics.splice(index, 1)
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    // Calculate SHA-256 hash of the file
    const buffer = await file.arrayBuffer()
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
    form.fileHash = hashHex
  } catch (error) {
    console.error('Error calculating file hash:', error)
    alert('文件哈希计算失败')
  }
}

// Computed margin based on reputation score
const marginPercentage = computed(() => {
  const score = form.reputationScore
  if (score >= 90) return 5
  if (score >= 80) return 10
  if (score >= 70) return 15
  if (score >= 60) return 20
  return 0 // Below 60 cannot publish
})

const marginAmount = computed(() => {
  if (!form.price) return 0
  return (form.price * marginPercentage.value / 100).toFixed(2)
})

const handleSubmit = async () => {
  loading.value = true
  
  // Validate metrics
  if (form.metrics.length === 0) {
    alert('请至少添加一个量化指标')
    loading.value = false
    return
  }
  
  // Check reputation score
  if (form.reputationScore < 60) {
    alert('您的信誉分低于60，无法发布商品')
    loading.value = false
    return
  }
  
  try {
    // Prepare product data for API
    const productData = {
      seller_address: walletAddress.value,
      name: form.name,
      description: form.description,
      price: form.price,
      currency: 'USD',
      category: form.category,
      version: form.version,
      system_requirements: form.systemRequirements,
      contract_template: form.contractTemplate,
      metrics: form.metrics.map(m => ({ name: m.name, value: m.value })),
      file_hash: form.fileHash,
      delivery_method: form.deliveryMethod,
      auto_confirm_hours: form.autoConfirmHours,
      storage_plan: form.storagePlan,
      delivery_checklist: form.deliveryChecklist,
      reputation_score: form.reputationScore,
      margin_percentage: marginPercentage.value
    }
    
    console.log('Submitting product data:', productData)
    
    // Call API to create product
    const response = await productsApi.create(productData)
    
    console.log('Product created:', response.data)
    
    loading.value = false
    success.value = true
    
    // Reset form after 2 seconds
    setTimeout(() => {
      resetForm()
      success.value = false
    }, 3000)
    
  } catch (error) {
    console.error('Error creating product:', error)
    loading.value = false
    
    // Show error message
    const errorMessage = error.response?.data?.detail || error.message || '发布失败，请重试'
    alert(`错误: ${errorMessage}`)
  }
}

const resetForm = () => {
  form.name = ''
  form.description = ''
  form.price = null
  form.version = ''
  form.systemRequirements = ''
  form.contractTemplate = ''
  form.metrics = []
  form.category = ''
  form.seller = ''
  form.tags = ''
  form.fileHash = ''
  form.deliveryMethod = ''
  form.apiKey = ''
  form.trialPrice = null
  form.autoConfirmHours = 72
  form.storagePlan = ''
  form.deliveryChecklist = {
    sourceCode: false,
    documentation: false,
    apiKey: false,
    tutorial: false,
    support: false
  }
  form.contract = {
    deliveryTime: '',
    refundPolicy: '',
    license: '',
    supportPeriod: 'none'
  }
  effectWarning.value = ''
}

const copyWalletAddress = () => {
  navigator.clipboard.writeText(walletAddress.value)
  alert('钱包地址已复制！')
}

const goToShop = () => {
  router.push('/shop')
}
</script>

<style scoped>
/* No additional styles needed */
</style>
