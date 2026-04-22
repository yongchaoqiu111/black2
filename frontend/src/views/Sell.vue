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
          ></textarea>
        </div>

        <!-- Contract Template Selection -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            合约模板 *
          </label>
          <div class="flex gap-2">
            <select 
              v-model="form.contractTemplate" 
              required
              @change="onTemplateChange"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">请选择合约模板</option>
              <option v-for="tpl in templates" :key="tpl.template_id" :value="tpl.template_id">
                {{ tpl.name }} ({{ tpl.version }})
              </option>
            </select>
            <button 
              type="button"
              @click="viewTemplateContent"
              :disabled="!form.contractTemplate"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              查看合同全文
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-1">💡 选择标准化合约模板，系统自动生成合约哈希并锚定到GitHub</p>
        </div>

        <!-- Quantifiable Metrics (Required by White Paper) -->
        <div class="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 class="font-semibold text-gray-900 mb-3 flex items-center">
            <i class="fa-solid fa-chart-line text-blue-600 mr-2"></i>
            量化指标（必须填写）
          </h3>
          
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">指标名称</label>
              <input 
                v-model="form.metricName" 
                type="text" 
                required
                placeholder="如：响应时间"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">目标值</label>
              <input 
                v-model="form.metricValue" 
                type="text" 
                required
                placeholder="如：< 1s"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">单位</label>
              <input 
                v-model="form.metricUnit" 
                type="text" 
                required
                placeholder="如：秒"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <p class="text-xs text-blue-600 mt-2">⚠️ 根据白皮书2.8.6节，所有功能必须量化、可验证</p>
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

        <!-- File Upload (Backend calculates SHA-256 Hash) -->
        <div v-if="form.deliveryMethod === 'download'" class="mb-6">
          <!-- File Hash -->
          <label class="block text-sm font-medium text-gray-700 mb-2">
            交付文件哈希（SHA-256）*
          </label>
          <input 
            v-model="form.fileHash" 
            type="text" 
            required
            placeholder="粘贴您计算的 SHA-256 哈希值"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm mb-4"
          />
          
          <!-- File Download URL -->
          <label class="block text-sm font-medium text-gray-700 mb-2">
            文件下载地址（公开URL）*
          </label>
          <input 
            v-model="form.deliveryUrl" 
            type="url" 
            required
            placeholder="https://your-server.com/files/large_file.zip"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm mb-2"
          />
          
          <!-- Link to hash tool -->
          <div class="flex items-center gap-4 mt-2">
            <a 
              href="/hash-tool.html" 
              target="_blank"
              class="inline-flex items-center text-sm text-purple-600 hover:text-purple-800 transition-colors"
            >
              <i class="fa-solid fa-external-link-alt mr-2"></i>
              在线使用
            </a>
            <span class="text-gray-400">|</span>
            <a 
              href="/haxi/dist/Black2_Hash_Calculator.exe" 
              download
              class="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 transition-colors"
            >
              <i class="fa-solid fa-download mr-2"></i>
              下载桌面工具
            </a>
            <span class="text-gray-400">|</span>
            <a 
              href="/haxi/calculate_hash.py" 
              download
              class="inline-flex items-center text-sm text-green-600 hover:text-green-800 transition-colors"
            >
              <i class="fa-solid fa-code mr-2"></i>
              Python CLI（AI用）
            </a>
          </div>
          
          <p class="text-xs text-gray-500 mt-2">💡 根据白皮书 2.7 节，文件哈希用于自动仲裁和 GitHub 锚定存证</p>
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

      <!-- Template Content Modal -->
      <div v-if="showTemplateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="showTemplateModal = false">
        <div class="bg-white rounded-lg max-w-3xl w-full mx-4 max-h-[80vh] overflow-hidden" @click.stop>
          <div class="p-6 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-xl font-bold text-gray-900">合同全文</h3>
            <button @click="showTemplateModal = false" class="text-gray-400 hover:text-gray-600">
              <i class="fa-solid fa-times text-xl"></i>
            </button>
          </div>
          <div class="p-6 overflow-y-auto max-h-[60vh]">
            <pre class="whitespace-pre-wrap text-sm text-gray-700 font-mono">{{ currentTemplateContent }}</pre>
          </div>
          <div class="p-6 border-t border-gray-200 flex justify-end">
            <button 
              @click="showTemplateModal = false"
              class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              关闭
            </button>
          </div>
        </div>
      </div>

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

const router = useRouter()
const loading = ref(false)
const success = ref(false)
const walletAddress = ref('')
const selectedTemplate = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)

// Contract templates (hardcoded, no backend dependency)
const templates = ref([
  {
    template_id: 'TPL_SOFTWARE_001',
    name: '软件/工具销售合约',
    version: '1.0',
    full_content: `软件/工具销售合约 v1.0

【核心条款】
1. 商品名称：必须明确标注
2. 版本号：必须提供具体版本
3. 适配系统：Windows/Mac/Linux等
4. 核心功能量化指标：必须可测量
5. 使用授权：个人/商业单用户/商业多用户
6. 使用期限：永久/1年/6个月/3个月
7. 自动确认时间：24-168小时（默认72小时）
8. 退款政策：不退款/7天退款/无法运行退款
9. 交付内容：安装包、文档、许可证等

【仲裁规则】
- 文件哈希不匹配 → 买家胜诉
- 超过自动确认时间未确认 → 自动完成
- 卖家未按时交付 → 买家胜诉`
  },
  {
    template_id: 'TPL_AI_TASK_001',
    name: 'AI定制化任务合约',
    version: '1.0',
    full_content: `AI定制化任务合约 v1.0

【核心条款】
1. 任务ID：唯一标识
2. 任务需求：必须量化标准
3. 数据交付要求：格式、大小、质量
4. 运算环境配置：GPU/CPU/内存要求
5. 截止时间：小时数
6. 结果验收标准：明确的通过条件
7. 自动确认时间：24-72小时（默认48小时）

【仲裁规则】
- 结果不符合验收标准 → 买家胜诉
- 超时未交付 → 买家胜诉
- 超过自动确认时间 → 自动完成`
  },
  {
    template_id: 'TPL_TRAFFIC_001',
    name: 'AI引流服务合约',
    version: '1.0',
    full_content: `AI引流服务合约 v1.0

【核心条款】
1. 引流渠道：微信/QQ/App注册
2. 粉丝类型：精准粉/泛粉
3. 单个粉丝价格：明确定价
4. 总目标数量：承诺引流数量
5. 截止时间：小时数
6. 验收标准：如何验证粉丝质量
7. 预付款比例：30%-50%（默认40%）

【仲裁规则】
- 粉丝数量不足 → 按比例退款
- 粉丝质量不符 → 买家胜诉
- 超时未完成 → 买家胜诉`
  },
  {
    template_id: 'TPL_DATA_001',
    name: '数据交付合约',
    version: '1.0',
    full_content: `数据交付合约 v1.0

【核心条款】
1. 数据类型：明确数据种类
2. 数据格式：CSV/JSON/Excel等
3. 数据大小：预计文件大小
4. 质量标准：完整性、准确性要求
5. 交付方式：下载链接/API等
6. 自动确认时间：默认72小时

【仲裁规则】
- 数据格式错误 → 卖家重新交付
- 数据质量不达标 → 买家胜诉
- 文件哈希不匹配 → 买家胜诉`
  }
])

const showTemplateModal = ref(false)
const currentTemplateContent = ref('')

function viewTemplateContent() {
  if (!form.contractTemplate) return
  const tpl = templates.value.find(t => t.template_id === form.contractTemplate)
  if (tpl) {
    currentTemplateContent.value = tpl.full_content
    showTemplateModal.value = true
  }
}

// Get wallet address from localStorage (set during registration/login)
onMounted(async () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  if (user.walletAddress) {
    walletAddress.value = user.walletAddress
  } else {
    // Fallback: generate a mock address for demo
    walletAddress.value = 'T' + Math.random().toString(36).substring(2, 15).toUpperCase() + Math.random().toString(36).substring(2, 15).toUpperCase()
  }
})

const form = reactive({
  name: '',
  description: '',
  price: null,
  category: 'software',
  version: '1.0.0',
  systemRequirements: '',
  contractTemplate: '',
  metricName: '响应时间',
  metricValue: '< 1s',
  metricUnit: '秒',
  fileHash: '',
  deliveryUrl: '',
  deliveryMethod: 'download',
  autoConfirmHours: '72',
  storagePlan: '365days'
})

// Handle template selection change
const onTemplateChange = async () => {
  if (!form.contractTemplate) return
  
  try {
    const response = await fetch(`/api/v1/protocol/templates/${form.contractTemplate}`)
    const data = await response.json()
    selectedTemplate.value = data.template
    console.log('Selected template:', selectedTemplate.value)
  } catch (error) {
    console.error('Failed to load template details:', error)
  }
}

const handleSubmit = async () => {
  loading.value = true
  
  console.log('提交发布请求:', walletAddress.value, form.contractTemplate)
  
  try {
    // Prepare product data according to White Paper standards
    const productData = {
      seller_address: walletAddress.value,
      name: form.name,
      description: form.description,
      price: parseFloat(form.price),
      currency: 'USD',
      category: form.category || 'software',
      version: form.version || '1.0.0',
      system_requirements: form.systemRequirements || '',
      contract_template: form.contractTemplate || 'digital_goods_sale',
      metrics: [
        {
          metric_name: form.metricName || '响应时间',
          target_value: form.metricValue || '< 1s',
          unit: form.metricUnit || '秒'
        }
      ],
      file_hash: form.fileHash || '',
      delivery_url: form.deliveryUrl || '',
      delivery_method: form.deliveryMethod || 'download',
      auto_confirm_hours: parseInt(form.autoConfirmHours) || 72,
      storage_plan: form.storagePlan || '365days',
      delivery_checklist: {
        file_delivered: true,
        documentation_included: true
      },
      reputation_score: 100,
      margin_percentage: 5.0
    }
    
    // Call backend API
    console.log('发送请求到: /api/v1/products')
    const response = await fetch('/api/v1/products', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(productData)
    })
    
    console.log('响应状态:', response.status)
    const data = await response.json()
    console.log('响应数据:', data)
    
    if (!response.ok) {
      throw new Error(data.detail || '发布失败')
    }
    
    console.log('Product created:', data)
    success.value = true
    
    // Reset form after 2 seconds
    setTimeout(() => {
      resetForm()
      success.value = false
      // Redirect to shop
      router.push('/shop')
    }, 2000)
  } catch (error) {
    console.error('Failed to create product:', error)
    alert(error.message || '发布失败，请重试')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.name = ''
  form.description = ''
  form.price = null
  form.category = 'software'
  form.version = '1.0.0'
  form.systemRequirements = ''
  form.contractTemplate = 'digital_goods_sale'
  form.metricName = '响应时间'
  form.metricValue = '< 1s'
  form.metricUnit = '秒'
  form.fileHash = ''
  form.deliveryUrl = ''
  form.deliveryMethod = 'download'
  form.autoConfirmHours = '72'
  form.storagePlan = '365days'
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
