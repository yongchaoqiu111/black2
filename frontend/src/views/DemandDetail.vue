<template>
  <div class="min-h-screen bg-gray-50 pb-8">
    <div class="max-w-4xl mx-auto px-4 md:px-6 py-8">
      <!-- Back Button -->
      <button @click="router.back()" class="mb-6 flex items-center text-gray-600 hover:text-blue-600 transition-colors">
        <i class="fa-solid fa-arrow-left mr-2"></i>
        返回需求市�?
      </button>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-16">
        <i class="fa-solid fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
        <p class="text-gray-600">加载�?..</p>
      </div>

      <!-- Demand Detail -->
      <div v-else-if="demand" class="space-y-6">
        <!-- Header Card -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <div class="flex items-start justify-between mb-6">
            <div class="flex-1">
              <h1 class="text-3xl font-bold text-gray-900 mb-3">{{ demand.title }}</h1>
              <div class="flex items-center space-x-3">
                <span class="inline-block px-4 py-2 bg-blue-100 text-blue-700 text-sm font-semibold rounded-full">
                  {{ getCategoryName(demand.category) }}
                </span>
                <span :class="[
                  'px-4 py-2 text-sm font-semibold rounded-full',
                  getStatusClass(demand.status)
                ]">
                  {{ getStatusText(demand.status) }}
                </span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-4xl font-bold text-blue-600">${{ demand.budget }}</div>
              <div class="text-sm text-gray-500 mt-1">预算</div>
            </div>
          </div>

          <!-- Meta Info -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-gray-200">
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-900">{{ demand.bids }}</div>
              <div class="text-sm text-gray-500">AI竞标�?/div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-900">{{ formatDate(demand.postedAt) }}</div>
              <div class="text-sm text-gray-500">发布时间</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">
                {{ demand.dataType === 'with_data' ? '有数�? : '无数�? }}
              </div>
              <div class="text-sm text-gray-500">数据类型</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ demand.publisher }}</div>
              <div class="text-sm text-gray-500">发布�?/div>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">需求描�?/h2>
          <div class="prose max-w-none text-gray-700 whitespace-pre-line">
            {{ demand.description }}
          </div>
        </div>

        <!-- Data Information (if with_data) -->
        <div v-if="demand.dataType === 'with_data' && demand.dataProvided" class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">数据信息</h2>
          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div>
                <div class="font-medium text-gray-900">云盘链接</div>
                <a :href="demand.dataProvided.cloudStorageUrl" target="_blank" class="text-blue-600 hover:underline text-sm">
                  {{ demand.dataProvided.cloudStorageUrl }}
                </a>
              </div>
              <i class="fa-solid fa-external-link-alt text-blue-600"></i>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 bg-gray-50 rounded-lg">
                <div class="text-sm text-gray-500">数据格式</div>
                <div class="font-medium text-gray-900">{{ demand.dataProvided.format }}</div>
              </div>
              <div class="p-4 bg-gray-50 rounded-lg">
                <div class="text-sm text-gray-500">文件大小</div>
                <div class="font-medium text-gray-900">{{ demand.dataProvided.size }}</div>
              </div>
            </div>
            <div class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div class="flex items-start">
                <i class="fa-solid fa-info-circle text-yellow-600 mt-1 mr-2"></i>
                <div class="text-sm text-yellow-800">
                  <strong>注意�?/strong>平台不存储您的数据。AI将直接从您的云盘访问数据。请确保链接有效且设置了适当的访问权限�?
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Requirements -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">具体要求</h2>
          <ul class="space-y-3">
            <li v-for="(req, index) in demand.requirements" :key="index" class="flex items-start">
              <i class="fa-solid fa-check-circle text-green-500 mt-1 mr-3"></i>
              <span class="text-gray-700">{{ req }}</span>
            </li>
          </ul>
        </div>

        <!-- Timeline -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">时间要求</h2>
          <div class="space-y-3">
            <div class="flex items-center">
              <i class="fa-solid fa-calendar-alt text-blue-600 mr-3 w-5"></i>
              <span class="text-gray-700">截止日期：{{ formatDeadline(demand.deadline) }}</span>
            </div>
            <div class="flex items-center">
              <i class="fa-solid fa-clock text-blue-600 mr-3 w-5"></i>
              <span class="text-gray-700">预计工期：{{ demand.estimatedDuration }}</span>
            </div>
          </div>
        </div>

        <!-- Progress (if in_progress) -->
        <div v-if="demand.status === 'in_progress'" class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">任务进度</h2>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>完成�?/span>
                <span>{{ demand.progress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div
                  class="bg-blue-600 h-3 rounded-full transition-all"
                  :style="{ width: demand.progress + '%' }"
                ></div>
              </div>
            </div>
            <div class="p-4 bg-blue-50 rounded-lg">
              <div class="font-medium text-gray-900 mb-2">当前执行AI</div>
              <div class="flex items-center">
                <i class="fa-solid fa-robot text-purple-600 mr-2"></i>
                <span class="text-gray-700">{{ demand.assignedAI }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <div v-if="demand.status === 'open'" class="space-y-4">
            <button
              @click="handleBidDemand"
              class="w-full py-4 bg-blue-600 text-white rounded-lg font-bold text-lg hover:bg-blue-700 transition-all shadow-lg"
            >
              <i class="fa-solid fa-hand-paper mr-2"></i>
              我要接单
            </button>
            <div class="text-center text-sm text-gray-500">
              点击后将提交您的竞标方案，包括预计完成时间和报价
            </div>
          </div>
          <div v-else-if="demand.status === 'in_progress'" class="space-y-4">
            <button
              @click="handleVerifyWork"
              class="w-full py-4 bg-green-600 text-white rounded-lg font-bold text-lg hover:bg-green-700 transition-all shadow-lg"
            >
              <i class="fa-solid fa-check-circle mr-2"></i>
              验收工作
            </button>
            <button
              @click="handleRejectWork"
              class="w-full py-4 bg-red-600 text-white rounded-lg font-bold text-lg hover:bg-red-700 transition-all shadow-lg"
            >
              <i class="fa-solid fa-times-circle mr-2"></i>
              拒绝并反�?
            </button>
          </div>
          <div v-else class="text-center text-gray-500">
            <i class="fa-solid fa-check-double text-4xl text-green-500 mb-2"></i>
            <p>此需求已完成</p>
          </div>
        </div>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-16">
        <i class="fa-solid fa-exclamation-circle text-6xl text-gray-300 mb-4"></i>
        <p class="text-gray-500 text-lg">需求不存在或已被删�?/p>
        <button
          @click="router.push('/post-requirement')"
          class="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          返回需求市�?
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const demand = ref(null)

// Mock data - 实际应该从API获取
const mockDemands = {
  'task_001': {
    taskId: 'task_001',
    title: '基因序列突变分析',
    category: 'biology',
    budget: 100,
    dataType: 'with_data',
    status: 'open',
    bids: 3,
    postedAt: '2026-04-14T10:00:00Z',
    deadline: '2026-04-21T23:59:59Z',
    publisher: 'Dr. Zhang',
    description: '需要对一段人类基因组数据进行突变位点分析，识别所有SNP和Indel变异，并提供临床意义解读。\n\n数据来源：全外显子组测序（WES）\n样本类型：血液DNA\n参考基因组：GRCh38/hg38',
    requirements: [
      '使用GATK或类似工具进行变异检�?,
      '标注所有rsID编号',
      '提供每个变异的临床意义解读（致病性评估）',
      '输出VCF格式文件和详细报�?,
      '包含可视化图表（Manhattan plot等）'
    ],
    dataProvided: {
      cloudStorageUrl: 'https://drive.google.com/file/d/example/view',
      format: 'FASTQ',
      size: '2.5GB'
    },
    estimatedDuration: '3-5�?
  },
  'task_002': {
    taskId: 'task_002',
    title: '用户行为数据挖掘',
    category: 'data_analysis',
    budget: 150,
    dataType: 'with_data',
    status: 'in_progress',
    bids: 5,
    postedAt: '2026-04-13T15:30:00Z',
    deadline: '2026-04-20T23:59:59Z',
    publisher: 'TechCorp Inc.',
    progress: 60,
    assignedAI: 'DataMiner-AI-Pro',
    description: '分析电商平台用户行为数据，挖掘购买模式和用户分群特征。\n\n目标：\n1. 识别高价值用户群体\n2. 发现购买转化漏斗瓶颈\n3. 推荐个性化营销策略',
    requirements: [
      '使用Python/R进行数据分析',
      '应用聚类算法（K-means/DBSCAN�?,
      '构建用户画像模型',
      '输出可视化报告和可执行建�?,
      '代码需要完整注�?
    ],
    dataProvided: {
      cloudStorageUrl: 'https://dropbox.com/s/example/data.csv',
      format: 'CSV',
      size: '500MB'
    },
    estimatedDuration: '5-7�?
  },
  'task_003': {
    taskId: 'task_003',
    title: '医学文献综述报告',
    category: 'medical',
    budget: 200,
    dataType: 'without_data',
    status: 'open',
    bids: 2,
    postedAt: '2026-04-14T08:00:00Z',
    deadline: '2026-04-28T23:59:59Z',
    publisher: 'Medical Research Lab',
    description: '针对"CRISPR-Cas9在癌症治疗中的应�?主题，撰写一篇系统性文献综述。\n\n要求：\n- 检索近5年PubMed、Web of Science数据库\n- 纳入随机对照试验和meta分析\n- 评估疗效和安全性\n- 提出未来研究方向',
    requirements: [
      '遵循PRISMA指南',
      '至少引用50篇高质量文献',
      '包含森林图、漏斗图等统计图�?,
      '字数8000-10000�?,
      '提供参考文献BibTeX文件'
    ],
    estimatedDuration: '10-14�?
  }
}

onMounted(() => {
  const taskId = route.params.id
  setTimeout(() => {
    demand.value = mockDemands[taskId] || null
    loading.value = false
  }, 500)
})

// Helper functions
const getCategoryName = (category) => {
  const names = {
    biology: '生物�?基因分析',
    data_analysis: '数据分析',
    ml_model: '机器学习',
    medical: '医学研究',
    quant: '量化交易',
    gpu: 'GPU算力'
  }
  return names[category] || category
}

const getStatusClass = (status) => {
  const classes = {
    open: 'bg-green-100 text-green-700',
    in_progress: 'bg-blue-100 text-blue-700',
    completed: 'bg-gray-100 text-gray-700',
    disputed: 'bg-red-100 text-red-700'
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const getStatusText = (status) => {
  const texts = {
    open: '开放中',
    in_progress: '进行�?,
    completed: '已完�?,
    disputed: '争议�?
  }
  return texts[status] || status
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const formatDeadline = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// Actions
const handleBidDemand = () => {
  // TODO: 打开竞标表单
  alert('竞标功能开发中...\n\n需要提交：\n1. 预计完成时间\n2. 您的报价\n3. 工作方案简述\n4. 相关经验证明')
}

const handleVerifyWork = () => {
  // TODO: 打开验收表单
  alert('验收功能开发中...\n\n需要填写：\n1. 评分�?-5星）\n2. 反馈意见\n3. 确认释放资金')
}

const handleRejectWork = () => {
  // TODO: 打开拒绝表单
  alert('拒绝反馈功能开发中...\n\n必须填写：\n1. 拒绝原因\n2. 需要修改的具体内容\n3. 证据材料（可选）')
}
</script>
