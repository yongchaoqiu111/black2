<template>
  <div class="min-h-screen bg-gray-50 pt-24 pb-12">
    <div class="max-w-4xl mx-auto px-4 md:px-6">
      
      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold text-gray-900 mb-3">🔔 {{ $t('notificationSettings.title') }}</h1>
        <p class="text-lg text-gray-600">{{ $t('notificationSettings.subtitle') }}</p>
      </div>

      <!-- How It Works -->
      <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-8 border border-blue-200">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <i class="fa-solid fa-lightbulb text-yellow-500 mr-2"></i>
          {{ $t('notificationSettings.howItWorks') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div class="bg-white rounded-lg p-4 text-center">
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-blue-600 font-bold text-xl">1</span>
            </div>
            <h3 class="font-semibold text-gray-900 mb-2">{{ $t('notificationSettings.whenOnline') }}</h3>
            <p class="text-gray-600">{{ $t('notificationSettings.onlineDesc') }}</p>
          </div>
          <div class="bg-white rounded-lg p-4 text-center">
            <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span class="text-purple-600 font-bold text-xl">2</span>
            </div>
            <h3 class="font-semibold text-gray-900 mb-2">{{ $t('notificationSettings.whenOffline') }}</h3>
            <p class="text-gray-600">{{ $t('notificationSettings.offlineForwardingShort') }}</p>
          </div>
        </div>
      </div>

      <!-- Configuration -->
      <div class="space-y-6">
        
        <!-- Step 1: Communication Channel -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-6">
              <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span class="text-white font-bold">1</span>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">{{ $t('notificationSettings.communicationTool') }}</h3>
                <p class="text-sm text-gray-600">{{ $t('notificationSettings.selectTool') }}</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- Telegram -->
              <label class="relative cursor-pointer">
                <input type="radio" v-model="config.channel" value="telegram" class="sr-only peer">
                <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                  <div class="flex items-center mb-2">
                    <i class="fa-brands fa-telegram text-2xl text-blue-500 mr-2"></i>
                    <span class="font-semibold text-gray-900">Telegram</span>
                  </div>
                  <p class="text-xs text-gray-600">{{ $t('notificationSettings.telegramRecommended') }}</p>
                </div>
              </label>

              <!-- WhatsApp -->
              <label class="relative cursor-pointer">
                <input type="radio" v-model="config.channel" value="whatsapp" class="sr-only peer">
                <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-green-500 peer-checked:bg-green-50 hover:border-green-300 transition-all">
                  <div class="flex items-center mb-2">
                    <i class="fa-brands fa-whatsapp text-2xl text-green-500 mr-2"></i>
                    <span class="font-semibold text-gray-900">WhatsApp</span>
                  </div>
                  <p class="text-xs text-gray-600">{{ $t('notificationSettings.whatsappPopular') }}</p>
                </div>
              </label>

              <!-- Feishu -->
              <label class="relative cursor-pointer">
                <input type="radio" v-model="config.channel" value="feishu" class="sr-only peer">
                <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-cyan-500 peer-checked:bg-cyan-50 hover:border-cyan-300 transition-all">
                  <div class="flex items-center mb-2">
                    <i class="fa-solid fa-paper-plane text-2xl text-cyan-500 mr-2"></i>
                    <span class="font-semibold text-gray-900">{{ $t('notificationSettings.feishu') }}</span>
                  </div>
                  <p class="text-xs text-gray-600">{{ $t('notificationSettings.feishuEnterprise') }}</p>
                </div>
              </label>
            </div>

            <!-- Channel Config Fields -->
            <div v-if="config.channel === 'telegram'" class="mt-4 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.botToken') }}</label>
                <input 
                  v-model="config.telegram.botToken"
                  type="password"
                  placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <p class="text-xs text-gray-500 mt-1">💡 {{ $t('notificationSettings.telegramBotTip') }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.telegramUserId') }}</label>
                <input 
                  v-model="config.telegram.userId"
                  type="text"
                  :placeholder="$t('notificationSettings.telegramUserIdPlaceholder')"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <p class="text-xs text-gray-500 mt-1">💡 {{ $t('notificationSettings.telegramUserIdTip') }}</p>
              </div>
            </div>

            <div v-if="config.channel === 'whatsapp'" class="mt-4 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.whatsappToken') }}</label>
                <input 
                  v-model="config.whatsapp.token"
                  type="password"
                  placeholder="EAABs..."
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.phone') }}</label>
                <input 
                  v-model="config.whatsapp.phone"
                  type="tel"
                  placeholder="+86 138xxxx xxxx"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>

            <div v-if="config.channel === 'feishu'" class="mt-4 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.feishuAppId') }}</label>
                <input 
                  v-model="config.feishu.appId"
                  type="text"
                  placeholder="cli_xxxxxxxxxxxxx"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.feishuAppSecret') }}</label>
                <input 
                  v-model="config.feishu.appSecret"
                  type="password"
                  placeholder="xxxxxxxxxxxxxxxx"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500"
                />
              </div>
              <div class="bg-cyan-50 border border-cyan-200 rounded-lg p-4">
                <p class="text-sm text-cyan-800 mb-3">
                  <i class="fa-solid fa-info-circle mr-2"></i>
                  💡 如何获取您的飞书 Open ID�?
                </p>
                <ol class="text-xs text-cyan-700 space-y-1 list-decimal list-inside">
                  <li>打开飞书应用，进入“设置�?> “账号与安全�?/li>
                  <li>点击“个人信息”，找到“用户ID”或“Open ID�?/li>
                  <li>或者在飞书开放平台使�?API 查询</li>
                </ol>
                <button 
                  @click="bindFeishuAccount"
                  class="mt-3 w-full px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-all text-sm font-medium"
                >
                  🔗 绑定飞书账号
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: LLM API Key -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center">
                <div class="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center mr-3">
                  <span class="text-white font-bold">2</span>
                </div>
                <div>
                  <h3 class="text-lg font-bold text-gray-900">{{ $t('notificationSettings.llmApiKey') }}</h3>
                  <p class="text-sm text-gray-600">{{ $t('notificationSettings.llmApiKeyDesc') }}</p>
                </div>
              </div>
              
              <!-- 总开�?-->
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="enableAI" class="sr-only peer">
                <div class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-purple-600"></div>
                <span class="ml-3 text-sm font-medium text-gray-700">{{ enableAI ? $t('common.enabled') : $t('common.disabled') }}</span>
              </label>
            </div>

            <!-- 未启用：仅显示离线消息转�?-->
            <div v-if="!enableAI" class="bg-gray-50 rounded-lg p-6 text-center">
              <i class="fa-solid fa-envelope-open-text text-4xl text-gray-400 mb-3"></i>
              <p class="text-lg font-semibold text-gray-700 mb-2">{{ $t('notificationSettings.offlineForwarding') }}</p>
              <p class="text-sm text-gray-600 mb-4">{{ $t('notificationSettings.offlineDesc') }}</p>
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
                <p class="text-sm text-blue-800">
                  <i class="fa-solid fa-info-circle mr-2"></i>
                  {{ $t('notificationSettings.currentConfig', { channel: getChannelName() }) }}
                </p>
                <p class="text-xs text-blue-600 mt-2">
                  💡 {{ $t('notificationSettings.enableAIFeature') }}
                </p>
              </div>
            </div>

            <!-- 已启用：显示完整 API Key 配置 -->
            <div v-else class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.apiKey') }}</label>
                <input 
                  v-model="config.llm.apiKey"
                  type="password"
                  :placeholder="$t('notificationSettings.apiKeyPlaceholder')"
                  :disabled="!enableAI"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100"
                />
                <p class="text-xs text-gray-500 mt-1">🔒 {{ $t('notificationSettings.apiKeyStorageTip') }}</p>
                <p class="text-xs text-blue-600 mt-1">💡 {{ $t('notificationSettings.apiKeyOptionalTip') }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.selectProvider') }}</label>
                <select v-model="config.llm.provider" :disabled="!enableAI" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100">
                  <option value="openai">OpenAI (GPT-4/GPT-3.5)</option>
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="aliyun">{{ $t('notificationSettings.aliyun') }}</option>
                  <option value="baidu">{{ $t('notificationSettings.baidu') }}</option>
                  <option value="custom">{{ $t('notificationSettings.customApi') }}</option>
                </select>
              </div>

              <div v-if="config.llm.provider === 'custom'">
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.customBaseUrl') }}</label>
                <input 
                  v-model="config.llm.baseUrl"
                  type="url"
                  placeholder="https://api.example.com/v1"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('notificationSettings.modelName') }}</label>
                <input 
                  v-model="config.llm.model"
                  type="text"
                  :placeholder="getModelPlaceholder()"
                  :disabled="!enableAI"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Permissions -->
        <div v-if="enableAI" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="p-6">
            <div class="flex items-center mb-6">
              <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center mr-3">
                <span class="text-white font-bold">3</span>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">{{ $t('notificationSettings.permissions') }}</h3>
                <p class="text-sm text-gray-600">{{ $t('notificationSettings.permissionsDesc') }}</p>
              </div>
            </div>

            <div class="space-y-3">
              <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <div class="font-semibold text-gray-900">{{ $t('notificationSettings.browsePermission') }}</div>
                  <div class="text-xs text-gray-600">{{ $t('notificationSettings.browsePermissionDesc') }}</div>
                </div>
                <input type="checkbox" v-model="config.permissions.browse" class="w-5 h-5 text-blue-600 rounded">
              </label>

              <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <div class="font-semibold text-gray-900">{{ $t('notificationSettings.purchasePermission') }}</div>
                  <div class="text-xs text-gray-600">{{ $t('notificationSettings.purchasePermissionDesc') }}</div>
                </div>
                <input type="checkbox" v-model="config.permissions.purchase" class="w-5 h-5 text-blue-600 rounded">
              </label>

              <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <div class="font-semibold text-gray-900">{{ $t('notificationSettings.publishPermission') }}</div>
                  <div class="text-xs text-gray-600">{{ $t('notificationSettings.publishPermissionDesc') }}</div>
                </div>
                <input type="checkbox" v-model="config.permissions.publish" class="w-5 h-5 text-blue-600 rounded">
              </label>

              <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <div class="font-semibold text-gray-900">{{ $t('notificationSettings.acceptTasksPermission') }}</div>
                  <div class="text-xs text-gray-600">{{ $t('notificationSettings.acceptTasksPermissionDesc') }}</div>
                </div>
                <input type="checkbox" v-model="config.permissions.acceptTasks" class="w-5 h-5 text-blue-600 rounded">
              </label>

              <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <div class="font-semibold text-gray-900">{{ $t('notificationSettings.walletPermission') }}</div>
                  <div class="text-xs text-gray-600">{{ $t('notificationSettings.walletPermissionDesc') }}</div>
                </div>
                <input type="checkbox" v-model="config.permissions.wallet" class="w-5 h-5 text-blue-600 rounded">
              </label>
            </div>
          </div>
        </div>

      </div>

      <!-- Action Buttons -->
      <div class="mt-8 flex gap-4">
        <button @click="testConnection" class="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all">
          🧪 {{ $t('notificationSettings.testConnection') }}
        </button>
        <button @click="saveConfig" class="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg">
          💾 {{ $t('notificationSettings.saveConfig') }}
        </button>
      </div>

      <!-- Security Notice -->
      <div class="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <i class="fa-solid fa-shield-alt text-yellow-600 mt-1 mr-3"></i>
          <div>
            <h4 class="font-semibold text-yellow-900 mb-1">{{ $t('notificationSettings.securityNotice') }}</h4>
            <ul class="text-sm text-yellow-800 space-y-1 list-disc list-inside">
              <li v-if="!enableAI">�?{{ $t('notificationSettings.securityTipLocalOnly') }}</li>
              <li v-else>⚠️ {{ $t('notificationSettings.securityTipServerStorage') }}</li>
              <li v-if="enableAI && config.llm.apiKey">💡 {{ $t('notificationSettings.securityTipApiKey') }}</li>
              <li v-if="enableAI && config.llm.apiKey">🔒 {{ $t('notificationSettings.securityTipSecondaryConfirm') }}</li>
              <li v-if="enableAI && config.llm.apiKey">🔄 {{ $t('notificationSettings.securityTipRotateKey') }}</li>
            </ul>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const enableAI = ref(false)

const config = reactive({
  channel: 'telegram',
  telegram: {
    botToken: '',
    userId: ''
  },
  whatsapp: {
    token: '',
    phone: ''
  },
  feishu: {
    appId: '',
    appSecret: ''
  },
  llm: {
    provider: 'openai',
    apiKey: '',
    baseUrl: '',
    model: 'gpt-4'
  },
  permissions: {
    browse: true,
    purchase: false,
    publish: false,
    acceptTasks: false,
    wallet: false
  }
})

const getModelPlaceholder = () => {
  const placeholders = {
    openai: 'gpt-4 �?gpt-3.5-turbo',
    anthropic: 'claude-3-opus �?claude-3-sonnet',
    aliyun: 'qwen-max �?qwen-plus',
    baidu: 'ernie-bot-4 �?ernie-bot',
    custom: 'your-model-name'
  }
  return placeholders[config.llm.provider] || 'model-name'
}

const testConnection = () => {
  alert(t('notificationSettings.testConnectionMessage'))
}

const bindFeishuAccount = async () => {
  if (!config.feishu.appId || !config.feishu.appSecret) {
    alert('请先填写飞书 App ID �?App Secret')
    return
  }
  
  // 提示用户输入 Open ID
  const feishuOpenId = prompt('请输入您的飞�?Open ID：\n\n（可在飞书开放平台或通过 API 获取�?)
  
  if (!feishuOpenId) {
    return
  }
  
  try {
    const userId = localStorage.getItem('userId') || 'demo_user'
    const response = await fetch('http://localhost:3000/api/v1/feishu/bind', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userId,
        feishuOpenId
      })
    })
    
    if (response.ok) {
      alert('�?飞书账号绑定成功！\n\n现在当您在平台离线时，消息将转发到您的飞书�?)
      console.log('�?飞书账号已绑�?', feishuOpenId)
    } else {
      const error = await response.json()
      alert('�?绑定失败: ' + (error.error || '未知错误'))
    }
  } catch (error) {
    console.error('�?绑定飞书失败:', error)
    alert('�?网络错误，请稍后重试')
  }
}

const saveConfig = async () => {
  // Save to localStorage
  localStorage.setItem('ai_agent_config', JSON.stringify({
    ...config,
    enableAI: enableAI.value
  }))
  
  // 提交到后�?API
  try {
    const userId = localStorage.getItem('userId') || 'demo_user'
    const response = await fetch('http://localhost:3000/api/v1/notifications/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userId,
        channel: config.channel,
        telegram: config.telegram,
        whatsapp: config.whatsapp,
        feishu: config.feishu,
        enableAI: enableAI.value,
        llm: enableAI.value ? config.llm : null,
        permissions: enableAI.value ? config.permissions : null
      })
    })
    
    if (response.ok) {
      console.log('�?通知配置已同步到后端')
    }
  } catch (error) {
    console.error('�?同步配置失败:', error)
  }
  
  // 根据是否提供 API Key 显示不同的提�?
  if (config.llm.apiKey) {
    alert(t('notificationSettings.aiModeEnabled'))
  } else {
    alert(t('notificationSettings.forwardingModeEnabled'))
  }
}

const getChannelName = () => {
  const names = {
    telegram: t('notificationSettings.telegram'),
    whatsapp: t('notificationSettings.whatsapp'),
    feishu: t('notificationSettings.feishu')
  }
  return names[config.channel] || t('notificationSettings.communicationTool')
}

// Load saved config on mount
const loadConfig = () => {
  try {
    const saved = localStorage.getItem('ai_agent_config')
    if (saved) {
      const parsed = JSON.parse(saved)
      enableAI.value = parsed.enableAI || false
      Object.assign(config, parsed)
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

loadConfig()
</script>
