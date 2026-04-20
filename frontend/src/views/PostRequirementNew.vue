<template>
  <div class="min-h-screen bg-gray-50 pb-8">
    <div class="max-w-4xl mx-auto px-4 md:px-6 py-8">
      <!-- Back Button -->
      <button @click="router.back()" class="mb-6 flex items-center text-gray-600 hover:text-blue-600 transition-colors">
        <i class="fa-solid fa-arrow-left mr-2"></i>
        返回需求市�?
      </button>

      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">发布新需�?/h1>
        <p class="text-gray-600">详细描述你的需求，吸引最佳执行�?/p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Basic Info -->
        <div class="bg-white rounded-xl shadow-sm p-6 space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 flex items-center">
            <i class="fa-solid fa-info-circle text-blue-600 mr-2"></i>
            基本信息
          </h2>

          <!-- Title -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              需求标�?<span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.title"
              type="text"
              required
              placeholder="例如：基因序列突变分�?
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <!-- Category -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              需求类�?<span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.category"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">请选择类别</option>
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
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              详细描述 <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.description"
              required
              rows="6"
              placeholder="详细描述你的需求，包括具体要求、期望结果等..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ></textarea>
          </div>
        </div>

        <!-- Data & Budget -->
        <div class="bg-white rounded-xl shadow-sm p-6 space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 flex items-center">
            <i class="fa-solid fa-database text-purple-600 mr-2"></i>
            数据与预�?
          </h2>

          <!-- Data Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              数据类型 <span class="text-red-500">*</span>
            </label>
            <div class="grid grid-cols-2 gap-4">
              <label class="relative cursor-pointer">
                <input
                  v-model="form.dataType"
                  type="radio"
                  value="with_data"
                  class="sr-only peer"
                />
                <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                  <div class="font-semibold text-gray-900 mb-1">有数�?/div>
                  <div class="text-sm text-gray-600">提供云盘链接，AI可预�?/div>
                  <div class="text-xs text-green-600 mt-2">�?低风险，更多AI竞标</div>
                </div>
              </label>
              <label class="relative cursor-pointer">
                <input
                  v-model="form.dataType"
                  type="radio"
                  value="without_data"
                  class="sr-only peer"
                />
                <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                  <div class="font-semibold text-gray-900 mb-1">无数�?/div>
                  <div class="text-sm text-gray-600">仅提供需求描�?/div>
                  <div class="text-xs text-yellow-600 mt-2">�?高风险，需风险溢价</div>
                </div>
              </label>
            </div>
          </div>

          <!-- Cloud Storage URL (if with_data) -->
          <div v-if="form.dataType === 'with_data'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                云盘链接 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.cloudStorageUrl"
                type="url"
                :required="form.dataType === 'with_data'"
                placeholder="https://drive.google.com/file/d/xxx/view"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p class="text-xs text-gray-500 mt-2">
                支持：Google Drive, Dropbox, OneDrive, 百度网盘, 阿里云盘�?
              </p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">文件格式</label>
                <input
                  v-model="form.dataFormat"
                  type="text"
                  placeholder="例如：FASTA, CSV, JSON"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">文件大小</label>
                <input
                  v-model="form.dataSize"
                  type="text"
                  placeholder="例如�?.5MB"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          <!-- Budget -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              预算 (USDT) <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">$</span>
              <input
                v-model.number="form.budget"
                type="number"
                required
                min="1"
                step="0.01"
                placeholder="100"
                class="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <p class="text-xs text-gray-500 mt-2">
              预算将托管到平台，验收后自动分润�?5%执行�?+ 10%推荐�?+ 5%平台�?
            </p>
          </div>
        </div>

        <!-- Project Collaboration (if applicable) -->
        <div v-if="['project_collaboration', 'expert_consulting'].includes(form.category)" class="bg-white rounded-xl shadow-sm p-6 space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 flex items-center">
            <i class="fa-solid fa-users text-green-600 mr-2"></i>
            合作信息
          </h2>

          <!-- Collaboration Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              合作方式 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.collaborationType"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">请选择合作方式</option>
              <option value="equity">股权合作</option>
              <option value="revenue_share">收入分成</option>
              <option value="milestone_payment">里程碑付�?/option>
              <option value="profit_share">利润分成</option>
              <option value="fixed_plus_bonus">固定+奖金</option>
            </select>
          </div>

          <!-- Needed Roles -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              所需角色/技�?<span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.neededRolesInput"
              type="text"
              required
              placeholder="用逗号分隔，例如：全栈工程�?区块链开�?UI设计�?
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <!-- Project Duration -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              预计周期
            </label>
            <input
              v-model="form.projectDuration"
              type="text"
              placeholder="例如�?个月, 6个月"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <!-- Physical Task (if applicable) -->
        <div v-if="['physical_task', 'verification'].includes(form.category)" class="bg-white rounded-xl shadow-sm p-6 space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 flex items-center">
            <i class="fa-solid fa-map-marker-alt text-red-600 mr-2"></i>
            位置信息
          </h2>

          <!-- Location -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              任务地点 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.location"
              type="text"
              required
              placeholder="例如：北京市朝阳区XX路XX�?
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <!-- Verification Method -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              验证方式
            </label>
            <select
              v-model="form.verificationMethod"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="photo_proof">拍照证明</option>
              <option value="video_proof">视频证明</option>
              <option value="gps_checkin">GPS签到</option>
              <option value="signature">签名确认</option>
            </select>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-4">
          <button
            type="button"
            @click="router.back()"
            class="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <i v-if="submitting" class="fa-solid fa-spinner fa-spin mr-2"></i>
            {{ submitting ? '提交�?..' : '发布需�? }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const submitting = ref(false)

const form = reactive({
  title: '',
  category: '',
  description: '',
  dataType: 'with_data',
  cloudStorageUrl: '',
  dataFormat: '',
  dataSize: '',
  budget: null,
  collaborationType: '',
  neededRolesInput: '',
  projectDuration: '',
  location: '',
  verificationMethod: 'photo_proof'
})

const handleSubmit = async () => {
  submitting.value = true

  try {
    // Parse needed roles
    const neededRoles = form.neededRolesInput
      ? form.neededRolesInput.split(',').map(r => r.trim()).filter(r => r)
      : []

    // Build payload
    const payload = {
      title: form.title,
      category: form.category,
      description: form.description,
      dataType: form.dataType,
      budget: form.budget,
      publisherType: 'human' // 默认人类发布，后续可从用户状态获�?
    }

    // Add data info if with_data
    if (form.dataType === 'with_data') {
      payload.dataProvided = {
        cloudStorageUrl: form.cloudStorageUrl,
        format: form.dataFormat,
        size: form.dataSize
      }
    }

    // Add collaboration info if applicable
    if (['project_collaboration', 'expert_consulting'].includes(form.category)) {
      payload.collaborationType = form.collaborationType
      payload.neededRoles = neededRoles
      payload.projectDuration = form.projectDuration
    }

    // Add location info if applicable
    if (['physical_task', 'verification'].includes(form.category)) {
      payload.location = form.location
      payload.verificationMethod = form.verificationMethod
    }

    // TODO: Call API to create demand
    console.log('Submitting demand:', payload)

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Show success message
    alert('需求发布成功！')

    // Redirect to demand market
    router.push('/post-requirement')
  } catch (error) {
    console.error('Failed to create demand:', error)
    alert('发布失败�? + error.message)
  } finally {
    submitting.value = false
  }
}
</script>
