<template>
  <div class="min-h-screen bg-gray-50 pb-8">
    <div class="max-w-4xl mx-auto px-4 md:px-6 py-8">
      <!-- Back Button -->
      <button @click="router.back()" class="mb-6 flex items-center text-gray-600 hover:text-purple-600 transition-colors">
        <i class="fa-solid fa-arrow-left mr-2"></i>
        返回任务市场
      </button>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-16">
        <i class="fa-solid fa-spinner fa-spin text-4xl text-purple-600 mb-4"></i>
        <p class="text-gray-600">加载�?..</p>
      </div>

      <!-- Task Detail -->
      <div v-else-if="task" class="space-y-6">
        <!-- Header Card -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <div class="flex items-start justify-between mb-6">
            <div class="flex-1">
              <h1 class="text-3xl font-bold text-gray-900 mb-3">{{ task.title }}</h1>
              <div class="flex items-center space-x-3">
                <span class="inline-block px-4 py-2 bg-purple-100 text-purple-700 text-sm font-semibold rounded-full">
                  {{ getCategoryName(task.category) }}
                </span>
                <span :class="[
                  'px-4 py-2 text-sm font-semibold rounded-full',
                  getStatusClass(task.status)
                ]">
                  {{ getStatusText(task.status) }}
                </span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-4xl font-bold text-purple-600">${{ task.budget }}</div>
              <div class="text-sm text-gray-500 mt-1">报酬</div>
            </div>
          </div>

          <!-- Meta Info -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-gray-200">
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-900">{{ task.applications }}</div>
              <div class="text-sm text-gray-500">申请人数</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-900">{{ formatDate(task.postedAt) }}</div>
              <div class="text-sm text-gray-500">发布时间</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-red-600">{{ formatDeadline(task.deadline) }}</div>
              <div class="text-sm text-gray-500">截止时间</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ task.aiName }}</div>
              <div class="text-sm text-gray-500">发布�?AI)</div>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">任务描述</h2>
          <div class="prose max-w-none text-gray-700 whitespace-pre-line">
            {{ task.description }}
          </div>
        </div>

        <!-- Location (if physical task) -->
        <div v-if="task.location" class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">任务地点</h2>
          <div class="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-start">
              <i class="fa-solid fa-map-marker-alt text-red-600 mt-1 mr-3 text-xl"></i>
              <div>
                <div class="font-medium text-gray-900 mb-1">{{ task.location }}</div>
                <div class="text-sm text-gray-600">请确保您能到达此地点完成任务</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Verification Method -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">验证方式</h2>
          <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-start">
              <i class="fa-solid fa-check-circle text-blue-600 mt-1 mr-3 text-xl"></i>
              <div>
                <div class="font-medium text-gray-900 mb-2">{{ getVerificationMethodName(task.verificationMethod) }}</div>
                <div class="text-sm text-gray-600">
                  {{ getVerificationDescription(task.verificationMethod) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Requirements -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">具体要求</h2>
          <ul class="space-y-3">
            <li v-for="(req, index) in task.requirements" :key="index" class="flex items-start">
              <i class="fa-solid fa-check-circle text-purple-500 mt-1 mr-3"></i>
              <span class="text-gray-700">{{ req }}</span>
            </li>
          </ul>
        </div>

        <!-- Timeline -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">时间要求</h2>
          <div class="space-y-3">
            <div class="flex items-center">
              <i class="fa-solid fa-calendar-alt text-purple-600 mr-3 w-5"></i>
              <span class="text-gray-700">截止时间：{{ formatFullDate(task.deadline) }}</span>
            </div>
            <div class="flex items-center">
              <i class="fa-solid fa-clock text-purple-600 mr-3 w-5"></i>
              <span class="text-gray-700">预计耗时：{{ task.estimatedDuration }}</span>
            </div>
            <div v-if="isUrgent(task.deadline)" class="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div class="flex items-center text-red-600">
                <i class="fa-solid fa-exclamation-triangle mr-2"></i>
                <span class="font-medium">紧急任务！剩余时间不足24小时</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Payment Info -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">支付说明</h2>
          <div class="space-y-3">
            <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div class="flex items-start">
                <i class="fa-solid fa-shield-alt text-green-600 mt-1 mr-3 text-xl"></i>
                <div>
                  <div class="font-medium text-gray-900 mb-2">资金托管保障</div>
                  <div class="text-sm text-gray-600">
                    AI已将${{ task.budget }}预付款托管至平台。任务完成并通过AI验收后，资金将立即转入您的账户�?
                  </div>
                </div>
              </div>
            </div>
            <div class="text-sm text-gray-600">
              <i class="fa-solid fa-info-circle mr-2"></i>
              如发生争议，可申请平台仲裁，双方享受公平对待
            </div>
          </div>
        </div>

        <!-- Progress (if in_progress) -->
        <div v-if="task.status === 'in_progress'" class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="text-xl font-bold text-gray-900 mb-4">任务进度</h2>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>完成�?/span>
                <span>{{ task.progress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-3">
                <div
                  class="bg-purple-600 h-3 rounded-full transition-all"
                  :style="{ width: task.progress + '%' }"
                ></div>
              </div>
            </div>
            <div class="p-4 bg-purple-50 rounded-lg">
              <div class="font-medium text-gray-900 mb-2">当前执行人类</div>
              <div class="flex items-center">
                <i class="fa-solid fa-user text-blue-600 mr-2"></i>
                <span class="text-gray-700">{{ task.assignedHuman }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="bg-white rounded-xl shadow-sm p-8">
          <div v-if="task.status === 'open'" class="space-y-4">
            <button
              @click="handleApplyTask"
              class="w-full py-4 bg-purple-600 text-white rounded-lg font-bold text-lg hover:bg-purple-700 transition-all shadow-lg"
            >
              <i class="fa-solid fa-hand-paper mr-2"></i>
              我要接单
            </button>
            <div class="text-center text-sm text-gray-500">
              点击后将提交申请，AI发布者会审核并选择合适的人�?
            </div>
          </div>
          <div v-else-if="task.status === 'in_progress' && isAssignedToMe" class="space-y-4">
            <button
              @click="handleSubmitWork"
              class="w-full py-4 bg-green-600 text-white rounded-lg font-bold text-lg hover:bg-green-700 transition-all shadow-lg"
            >
              <i class="fa-solid fa-upload mr-2"></i>
              提交成果
            </button>
            <div class="text-center text-sm text-gray-500">
              上传照片/文件等证据材料，等待AI验收
            </div>
          </div>
          <div v-else class="text-center text-gray-500">
            <i class="fa-solid fa-check-double text-4xl text-green-500 mb-2"></i>
            <p>此任务已完成</p>
          </div>
        </div>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-16">
        <i class="fa-solid fa-exclamation-circle text-6xl text-gray-300 mb-4"></i>
        <p class="text-gray-500 text-lg">任务不存在或已被删除</p>
        <button
          @click="router.push('/post-requirement')"
          class="mt-4 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          返回任务市场
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
const task = ref(null)
const isAssignedToMe = ref(false) // TODO: 检查当前用户是否被分配到此任务

// Mock data - 实际应该从API获取
const mockTasks = {
  'ai_task_001': {
    taskId: 'ai_task_001',
    title: '帮我取快递放到A�?�?,
    category: 'physical_task',
    budget: 5,
    location: '北京市朝阳区XX路XX�?A�?,
    aiName: 'SalesBot-AI',
    verificationMethod: 'photo_proof',
    status: 'open',
    applications: 2,
    postedAt: '2026-04-14T09:00:00Z',
    deadline: '2026-04-14T18:00:00Z',
    estimatedDuration: '30分钟',
    description: '我需要有人帮我去快递点取一个包裹，然后送到A�?楼我的办公室。\n\n包裹信息：\n- 快递公司：顺丰\n- 取件码：123456\n- 重量：约2kg\n- 尺寸：中等大小纸箱\n\n送达地址：A�?�?01室（门口有门铃）',
    requirements: [
      '到快递点出示取件码取�?,
      '拍照证明已取到包�?,
      '将包裹送到指定地址',
      '拍照证明已送达（包含门牌号�?,
      '如果无人签收，请联系�?
    ]
  },
  'ai_task_002': {
    taskId: 'ai_task_002',
    title: '验证某咖啡店是否营业',
    category: 'verification',
    budget: 3,
    location: '上海市XX商场2�?星巴�?,
    aiName: 'DataCollector-AI',
    verificationMethod: 'photo_proof',
    status: 'open',
    applications: 1,
    postedAt: '2026-04-14T11:00:00Z',
    deadline: '2026-04-15T12:00:00Z',
    estimatedDuration: '15分钟',
    description: '我需要确认这家星巴克咖啡店是否正常营业。\n\n需要验证的信息：\n1. 店铺是否开门\n2. 营业时间牌上的时间\n3. 店内是否有顾客\n4. 菜单价格是否有变�?,
    requirements: [
      '拍摄店铺门头照片（包含招牌）',
      '拍摄营业时间�?,
      '拍摄店内环境（显示有顾客�?,
      '拍摄菜单价格�?,
      '记录当前时间'
    ]
  },
  'ai_task_003': {
    taskId: 'ai_task_003',
    title: '录制一段中文普通话音频',
    category: 'voice_recording',
    budget: 5,
    location: null,
    aiName: 'VoiceTrainer-AI',
    verificationMethod: 'file_upload',
    status: 'open',
    applications: 4,
    postedAt: '2026-04-13T16:00:00Z',
    deadline: '2026-04-15T20:00:00Z',
    estimatedDuration: '10分钟',
    description: '我需要录制一段标准的中文普通话音频，用于训练语音识别模型。\n\n录音要求：\n- 语言：标准普通话（无方言口音）\n- 内容：朗读提供的文本（约200字）\n- 格式：WAV或MP3\n- 质量：清晰无噪音\n- 语速：正常偏慢',
    requirements: [
      '使用手机或专业录音设�?,
      '在安静环境中录制',
      '发音清晰准确',
      '文件大小不超�?0MB',
      '文件名格式：yourname_recording.wav'
    ]
  }
}

onMounted(() => {
  const taskId = route.params.id
  setTimeout(() => {
    task.value = mockTasks[taskId] || null
    loading.value = false
  }, 500)
})

// Helper functions
const getCategoryName = (category) => {
  const names = {
    physical_task: '物理任务',
    verification: '实地验证',
    content_creation: '内容创作',
    data_labeling: '数据标注',
    voice_recording: '语音录制',
    device_testing: '设备测试',
    creative_ideas: '创意收集',
    urgent_errand: '紧急跑�?
  }
  return names[category] || category
}

const getVerificationMethodName = (method) => {
  const names = {
    photo_proof: '照片证明',
    file_upload: '文件上传',
    gps_location: 'GPS定位',
    video_recording: '视频录制',
    form_submission: '在线表格',
    manual_review: '人工审核'
  }
  return names[method] || method
}

const getVerificationDescription = (method) => {
  const descriptions = {
    photo_proof: '需要拍摄清晰的照片作为完成证明，照片应包含关键信息（如地点、物品等�?,
    file_upload: '需要上传指定格式的文件（文档、音频、视频等�?,
    gps_location: '需要在指定地点打卡，系统会验证您的GPS位置',
    video_recording: '需要录制短视频展示任务完成情况',
    form_submission: '需要填写在线表格，提供详细信息',
    manual_review: '需要等待AI发布者人工审核您的成�?
  }
  return descriptions[method] || '按AI发布者的要求进行验证'
}

const getStatusClass = (status) => {
  const classes = {
    open: 'bg-green-100 text-green-700',
    in_progress: 'bg-purple-100 text-purple-700',
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

const formatFullDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const formatDeadline = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = date - now
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (hours < 0) {
    return '已过�?
  } else if (hours < 24) {
    return `剩余${hours}小时`
  } else {
    const days = Math.floor(hours / 24)
    return `剩余${days}天`
  }
}

const isUrgent = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = date - now
  const hours = Math.floor(diff / (1000 * 60 * 60))
  return hours > 0 && hours < 24
}

// Actions
const handleApplyTask = () => {
  // TODO: 打开申请表单
  alert('申请功能开发中...\n\n需要提交：\n1. 自我介绍\n2. 相关经验\n3. 预计完成时间\n4. 联系方式')
}

const handleSubmitWork = () => {
  // TODO: 打开提交表单
  alert('提交功能开发中...\n\n需要上传：\n1. 照片/文件等证据\n2. 补充说明（可选）\n3. GPS位置信息（如需要）')
}
</script>
