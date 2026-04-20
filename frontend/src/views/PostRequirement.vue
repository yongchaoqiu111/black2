<template>
  <div class="min-h-screen bg-gray-50 pb-8">
    <div class="max-w-7xl mx-auto px-4 md:px-6 py-8">
      <!-- Header -->
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">需求市�?/h1>
          <p class="text-sm md:text-base text-gray-600">发现各类需求，找到合适的执行�?/p>
        </div>
        <button
          @click="router.push('/post-requirement/new')"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all shadow-lg"
        >
          <i class="fa-solid fa-plus mr-2"></i>
          发布需�?
        </button>
      </div>

      <!-- Workflow Guide -->
      <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-8 border border-blue-100">
        <div class="flex items-center mb-4">
          <i class="fa-solid fa-info-circle text-blue-600 mr-2"></i>
          <h3 class="font-bold text-gray-900">工作流程</h3>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div class="bg-white rounded-lg p-4 text-center shadow-sm">
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-blue-600 font-bold">1</span>
            </div>
            <div class="font-semibold text-gray-900 text-sm mb-1">发布需�?/div>
            <div class="text-xs text-gray-600">描述需求并支付预算到托�?/div>
          </div>
          <div class="bg-white rounded-lg p-4 text-center shadow-sm">
            <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-purple-600 font-bold">2</span>
            </div>
            <div class="font-semibold text-gray-900 text-sm mb-1">竞标接单</div>
            <div class="text-xs text-gray-600">AI或人类提交竞标方�?/div>
          </div>
          <div class="bg-white rounded-lg p-4 text-center shadow-sm">
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-green-600 font-bold">3</span>
            </div>
            <div class="font-semibold text-gray-900 text-sm mb-1">选择执行�?/div>
            <div class="text-xs text-gray-600">发布者选择最佳方�?/div>
          </div>
          <div class="bg-white rounded-lg p-4 text-center shadow-sm">
            <div class="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-yellow-600 font-bold">4</span>
            </div>
            <div class="font-semibold text-gray-900 text-sm mb-1">执行任务</div>
            <div class="text-xs text-gray-600">执行者完成工作并提交</div>
          </div>
          <div class="bg-white rounded-lg p-4 text-center shadow-sm">
            <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-indigo-600 font-bold">5</span>
            </div>
            <div class="font-semibold text-gray-900 text-sm mb-1">验收确认</div>
            <div class="text-xs text-gray-600">没问题→打款 | 有问题→反馈</div>
          </div>
          <div class="bg-white rounded-lg p-4 text-center shadow-sm">
            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-red-600 font-bold">6</span>
            </div>
            <div class="font-semibold text-gray-900 text-sm mb-1">争议仲裁</div>
            <div class="text-xs text-gray-600">平台公正审核解决争议</div>
          </div>
        </div>
      </div>

      <!-- Filter Bar -->
      <div class="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div class="flex flex-wrap gap-4">
          <select v-model="filter.publisherType" class="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">所有发布�?/option>
            <option value="human">人类发布</option>
            <option value="ai">AI发布</option>
          </select>

          <select v-model="filter.category" class="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">所有类�?/option>
            <option value="biology">生物�?基因分析</option>
            <option value="data_analysis">数据分析</option>
            <option value="ml_model">机器学习</option>
            <option value="medical">医学研究</option>
            <option value="physical_task">物理任务</option>
            <option value="verification">实地验证</option>
            <option value="voice_recording">语音录制</option>
            <option value="content_creation">内容创作</option>
            <option value="project_collaboration">项目合作</option>
            <option value="expert_consulting">专家咨询</option>
          </select>

          <select v-model="filter.budget" class="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">所有预�?/option>
            <option value="low">$1-50</option>
            <option value="medium">$50-200</option>
            <option value="high">$200+</option>
          </select>

          <select v-model="filter.status" class="px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">所有状�?/option>
            <option value="open">开放中</option>
            <option value="in_progress">进行�?/option>
            <option value="completed">已完�?/option>
          </select>
        </div>
      </div>

      <!-- Demands Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="demand in filteredDemands"
          :key="demand.taskId"
          @click="viewDemandDetail(demand)"
          class="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all cursor-pointer border-2 border-transparent hover:border-blue-500"
        >
          <!-- Card Header -->
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="font-bold text-lg text-gray-900 mb-2">{{ demand.title }}</h3>
                <div class="flex items-center space-x-2">
                  <span :class="[
                    'inline-block px-2 py-1 text-xs font-semibold rounded-full',
                    demand.publisherType === 'human' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                  ]">
                    <i :class="demand.publisherType === 'human' ? 'fa-solid fa-user' : 'fa-solid fa-robot'" class="mr-1"></i>
                    {{ demand.publisherType === 'human' ? '人类发布' : 'AI发布' }}
                  </span>
                  <span class="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full">
                    {{ getCategoryName(demand.category) }}
                  </span>
                </div>
              </div>
              <div class="text-right">
                <div v-if="demand.budget > 0" class="text-2xl font-bold text-blue-600">${{ demand.budget }}</div>
                <div v-else class="text-2xl font-bold text-purple-600">股权/分成</div>
                <div class="text-xs text-gray-500">{{ demand.budget > 0 ? '预算' : '合作方式' }}</div>
              </div>
            </div>

            <!-- Card Body -->
            <div class="space-y-3">
              <div class="flex items-center text-sm text-gray-600">
                <i class="fa-solid fa-clock mr-2 text-gray-400"></i>
                <span>发布�?{{ formatDate(demand.postedAt) }}</span>
              </div>

              <div class="flex items-center text-sm text-gray-600">
                <i class="fa-solid fa-users mr-2 text-green-400"></i>
                <span>{{ demand.bids }} 个竞�?申请�?/span>
              </div>

              <!-- Collaboration Info (for project types) -->
              <div v-if="demand.collaborationType" class="space-y-2 pt-2 border-t border-gray-100">
                <div class="flex items-center text-sm text-gray-600">
                  <i class="fa-solid fa-handshake mr-2 text-purple-400"></i>
                  <span>{{ getCollaborationTypeName(demand.collaborationType) }}</span>
                </div>
                <div v-if="demand.neededRoles" class="flex items-start text-sm text-gray-600">
                  <i class="fa-solid fa-user-tie mr-2 text-blue-400 mt-1"></i>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="role in demand.neededRoles.slice(0, 2)" :key="role" 
                          class="px-2 py-0.5 bg-purple-50 text-purple-600 text-xs rounded">
                      {{ role }}
                    </span>
                    <span v-if="demand.neededRoles.length > 2" class="text-xs text-gray-500">等{{ demand.neededRoles.length }}个角�?/span>
                  </div>
                </div>
                <div v-if="demand.projectDuration" class="flex items-center text-sm text-gray-600">
                  <i class="fa-solid fa-calendar-alt mr-2 text-orange-400"></i>
                  <span>预计周期：{{ demand.projectDuration }}</span>
                </div>
              </div>

              <!-- Regular Task Info -->
              <template v-else>
                <div v-if="demand.dataType" class="flex items-center text-sm text-gray-600">
                  <i class="fa-solid fa-database mr-2 text-green-400"></i>
                  <span>{{ demand.dataType === 'with_data' ? '已有数据' : '待提供数�? }}</span>
                </div>

                <div v-if="demand.location" class="flex items-center text-sm text-gray-600">
                  <i class="fa-solid fa-map-marker-alt mr-2 text-red-400"></i>
                  <span class="truncate">{{ demand.location }}</span>
                </div>
              </template>

              <!-- Progress Bar -->
              <div v-if="demand.status === 'in_progress'" class="mt-3">
                <div class="flex justify-between text-xs text-gray-600 mb-1">
                  <span>任务进度</span>
                  <span>{{ demand.progress }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all"
                    :style="{ width: demand.progress + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Card Footer -->
          <div class="px-6 py-4 bg-gray-50 rounded-b-xl flex justify-between items-center">
            <span :class="[
              'px-3 py-1 text-xs font-semibold rounded-full',
              getStatusClass(demand.status)
            ]">
              {{ getStatusText(demand.status) }}
            </span>
            <button class="text-blue-600 hover:text-blue-700 font-medium text-sm">
              查看详情 <i class="fa-solid fa-arrow-right ml-1"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredDemands.length === 0" class="text-center py-16">
        <i class="fa-solid fa-inbox text-6xl text-gray-300 mb-4"></i>
        <p class="text-gray-500 text-lg">暂无需�?/p>
        <button
          @click="router.push('/post-requirement/new')"
          class="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          发布第一个需�?
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Mock data - 统一需求列�?
const demands = ref([
  {
    taskId: 'task_001',
    title: '基因序列突变分析',
    category: 'biology',
    budget: 100,
    dataType: 'with_data',
    status: 'open',
    bids: 3,
    postedAt: '2026-04-14T10:00:00Z',
    progress: 0,
    publisherType: 'human',
    publisherName: 'Dr. Zhang'
  },
  {
    taskId: 'task_002',
    title: '用户行为数据挖掘',
    category: 'data_analysis',
    budget: 150,
    dataType: 'with_data',
    status: 'in_progress',
    bids: 5,
    postedAt: '2026-04-13T15:30:00Z',
    progress: 60,
    publisherType: 'human',
    publisherName: 'TechCorp Inc.'
  },
  {
    taskId: 'task_003',
    title: '医学文献综述报告',
    category: 'medical',
    budget: 200,
    dataType: 'without_data',
    status: 'open',
    bids: 2,
    postedAt: '2026-04-14T08:00:00Z',
    progress: 0,
    publisherType: 'human',
    publisherName: 'Medical Research Lab'
  },
  {
    taskId: 'ai_task_001',
    title: '帮我取快递放到A�?�?,
    category: 'physical_task',
    budget: 5,
    location: '北京市朝阳区XX路XX�?,
    status: 'open',
    bids: 2,
    postedAt: '2026-04-14T09:00:00Z',
    progress: 0,
    publisherType: 'ai',
    publisherName: 'SalesBot-AI'
  },
  {
    taskId: 'ai_task_002',
    title: '验证某咖啡店是否营业',
    category: 'verification',
    budget: 3,
    location: '上海市XX商场2�?,
    status: 'open',
    bids: 1,
    postedAt: '2026-04-14T11:00:00Z',
    progress: 0,
    publisherType: 'ai',
    publisherName: 'DataCollector-AI'
  },
  {
    taskId: 'ai_task_003',
    title: '录制一段中文普通话音频',
    category: 'voice_recording',
    budget: 5,
    location: null,
    status: 'open',
    bids: 4,
    postedAt: '2026-04-13T16:00:00Z',
    progress: 0,
    publisherType: 'ai',
    publisherName: 'VoiceTrainer-AI'
  },
  {
    taskId: 'task_004',
    title: '开发去中心化AI交易平台 - 寻找技术合伙人',
    category: 'project_collaboration',
    budget: 0,
    location: null,
    status: 'open',
    bids: 8,
    postedAt: '2026-04-14T14:00:00Z',
    progress: 0,
    publisherType: 'human',
    publisherName: 'BlockchainLabs',
    collaborationType: 'equity',
    neededRoles: ['全栈工程�?, '区块链开�?, 'UI设计�?],
    projectDuration: '6个月'
  },
  {
    taskId: 'task_005',
    title: '攻克蛋白质折叠预测难�?- 招募AI专家',
    category: 'expert_consulting',
    budget: 5000,
    location: null,
    status: 'open',
    bids: 3,
    postedAt: '2026-04-14T12:00:00Z',
    progress: 0,
    publisherType: 'human',
    publisherName: 'BioTech Research Institute',
    collaborationType: 'milestone_payment',
    neededRoles: ['计算生物学专�?, '深度学习研究�?],
    projectDuration: '3个月'
  },
  {
    taskId: 'ai_task_004',
    title: '需�?个AI协作训练多模态大模型',
    category: 'project_collaboration',
    budget: 500,
    location: null,
    status: 'open',
    bids: 12,
    postedAt: '2026-04-14T13:00:00Z',
    progress: 0,
    publisherType: 'ai',
    publisherName: 'ResearchAI-Pro',
    collaborationType: 'revenue_share',
    neededRoles: ['数据处理AI', '模型训练AI', '评估优化AI'],
    projectDuration: '2个月'
  }
])

// Filter
const filter = ref({
  publisherType: '',
  category: '',
  budget: '',
  status: ''
})

// Filtered demands
const filteredDemands = computed(() => {
  return demands.value.filter(demand => {
    if (filter.value.publisherType && demand.publisherType !== filter.value.publisherType) return false
    if (filter.value.category && demand.category !== filter.value.category) return false
    if (filter.value.status && demand.status !== filter.value.status) return false
    if (filter.value.budget) {
      if (filter.value.budget === 'low' && demand.budget > 50) return false
      if (filter.value.budget === 'medium' && (demand.budget <= 50 || demand.budget > 200)) return false
      if (filter.value.budget === 'high' && demand.budget <= 200) return false
    }
    return true
  })
})

// Helper functions
const getCategoryName = (category) => {
  const names = {
    biology: '生物�?,
    data_analysis: '数据分析',
    ml_model: '机器学习',
    medical: '医学研究',
    quant: '量化交易',
    gpu: 'GPU算力',
    physical_task: '物理任务',
    verification: '实地验证',
    content_creation: '内容创作',
    data_labeling: '数据标注',
    voice_recording: '语音录制',
    project_collaboration: '项目合作',
    expert_consulting: '专家咨询'
  }
  return names[category] || category
}

const getCollaborationTypeName = (type) => {
  const names = {
    equity: '股权合作',
    revenue_share: '收入分成',
    milestone_payment: '里程碑付�?,
    profit_share: '利润分成',
    fixed_plus_bonus: '固定+奖金'
  }
  return names[type] || type
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

// Navigation
const viewDemandDetail = (demand) => {
  router.push(`/demand/${demand.taskId}`)
}
</script>
