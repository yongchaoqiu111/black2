<template>
  <div class="min-h-screen bg-gray-50 pb-8">
    <div class="max-w-5xl mx-auto px-4 md:px-6 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">AI Assistant Configuration</h1>
        <p class="text-sm md:text-base text-gray-600">Connect your AI assistant to automatically respond to customer inquiries</p>
      </div>

      <!-- Benefits Banner -->
      <div class="mb-8 p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-200">
        <div class="flex items-start space-x-4">
          <i class="fa-solid fa-robot text-blue-600 text-3xl mt-1"></i>
          <div>
            <h3 class="font-bold text-gray-900 mb-2">Why Connect Your AI Assistant?</h3>
            <ul class="space-y-2 text-sm text-gray-700">
              <li class="flex items-start">
                <i class="fa-solid fa-check text-green-600 mr-2 mt-1"></i>
                <span><strong>24/7 Auto-Response:</strong> Instantly answer customer questions about your products</span>
              </li>
              <li class="flex items-start">
                <i class="fa-solid fa-check text-green-600 mr-2 mt-1"></i>
                <span><strong>Save Time:</strong> Let AI handle common questions while you focus on development</span>
              </li>
              <li class="flex items-start">
                <i class="fa-solid fa-check text-green-600 mr-2 mt-1"></i>
                <span><strong>Increase Sales:</strong> Faster response times lead to more conversions</span>
              </li>
              <li class="flex items-start">
                <i class="fa-solid fa-check text-green-600 mr-2 mt-1"></i>
                <span><strong>Smart Routing:</strong> Complex queries are forwarded to you personally</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- AI Provider Selection -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <i class="fa-solid fa-plug text-blue-600 mr-3"></i>
          Select AI Provider
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <!-- OpenAI -->
          <label class="relative cursor-pointer">
            <input 
              type="radio" 
              v-model="selectedProvider"
              value="openai"
              class="peer sr-only"
            />
            <div class="p-6 border-2 border-gray-200 rounded-xl peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
              <div class="flex items-center justify-between mb-3">
                <i class="fa-solid fa-brain text-3xl text-blue-600"></i>
                <i v-if="selectedProvider === 'openai'" class="fa-solid fa-check-circle text-blue-600 text-xl"></i>
              </div>
              <h3 class="font-bold text-gray-900 mb-1">OpenAI GPT</h3>
              <p class="text-xs text-gray-600">GPT-4, GPT-3.5 Turbo</p>
            </div>
          </label>

          <!-- Claude -->
          <label class="relative cursor-pointer">
            <input 
              type="radio" 
              v-model="selectedProvider"
              value="claude"
              class="peer sr-only"
            />
            <div class="p-6 border-2 border-gray-200 rounded-xl peer-checked:border-purple-500 peer-checked:bg-purple-50 hover:border-purple-300 transition-all">
              <div class="flex items-center justify-between mb-3">
                <i class="fa-solid fa-robot text-3xl text-purple-600"></i>
                <i v-if="selectedProvider === 'claude'" class="fa-solid fa-check-circle text-purple-600 text-xl"></i>
              </div>
              <h3 class="font-bold text-gray-900 mb-1">Anthropic Claude</h3>
              <p class="text-xs text-gray-600">Claude 3 Opus, Sonnet</p>
            </div>
          </label>

          <!-- Custom API -->
          <label class="relative cursor-pointer">
            <input 
              type="radio" 
              v-model="selectedProvider"
              value="custom"
              class="peer sr-only"
            />
            <div class="p-6 border-2 border-gray-200 rounded-xl peer-checked:border-green-500 peer-checked:bg-green-50 hover:border-green-300 transition-all">
              <div class="flex items-center justify-between mb-3">
                <i class="fa-solid fa-code text-3xl text-green-600"></i>
                <i v-if="selectedProvider === 'custom'" class="fa-solid fa-check-circle text-green-600 text-xl"></i>
              </div>
              <h3 class="font-bold text-gray-900 mb-1">Custom API</h3>
              <p class="text-xs text-gray-600">Your own endpoint</p>
            </div>
          </label>
        </div>

        <!-- API Configuration Form -->
        <div v-if="selectedProvider" class="space-y-4 p-6 bg-gray-50 rounded-lg border border-gray-200">
          <h3 class="font-semibold text-gray-900 mb-4">API Configuration</h3>
          
          <!-- OpenAI Config -->
          <div v-if="selectedProvider === 'openai'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                API Key <span class="text-red-500">*</span>
              </label>
              <input 
                type="password" 
                v-model="config.openai.apiKey"
                placeholder="sk-..."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" class="text-blue-600 hover:underline">OpenAI Platform</a></p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Model</label>
              <select v-model="config.openai.model" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                <option value="gpt-4-turbo">GPT-4 Turbo (Recommended)</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Faster)</option>
              </select>
            </div>
          </div>

          <!-- Claude Config -->
          <div v-if="selectedProvider === 'claude'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                API Key <span class="text-red-500">*</span>
              </label>
              <input 
                type="password" 
                v-model="config.claude.apiKey"
                placeholder="sk-ant-..."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
              />
              <p class="text-xs text-gray-500 mt-1">Get your API key from <a href="https://console.anthropic.com/" target="_blank" class="text-purple-600 hover:underline">Anthropic Console</a></p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Model</label>
              <select v-model="config.claude.model" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500">
                <option value="claude-3-opus-20240229">Claude 3 Opus (Most Capable)</option>
                <option value="claude-3-sonnet-20240229">Claude 3 Sonnet (Balanced)</option>
                <option value="claude-3-haiku-20240307">Claude 3 Haiku (Fastest)</option>
              </select>
            </div>
          </div>

          <!-- Custom API Config -->
          <div v-if="selectedProvider === 'custom'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                API Endpoint URL <span class="text-red-500">*</span>
              </label>
              <input 
                type="url" 
                v-model="config.custom.endpoint"
                placeholder="https://your-api.com/chat"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">API Key / Token</label>
              <input 
                type="password" 
                v-model="config.custom.apiKey"
                placeholder="Your API key"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Request Format</label>
              <select v-model="config.custom.format" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500">
                <option value="openai-compatible">OpenAI Compatible</option>
                <option value="custom">Custom Format</option>
              </select>
            </div>
          </div>

          <!-- Test Connection Button -->
          <div class="flex items-center space-x-3 pt-4">
            <button 
              @click="testConnection"
              :disabled="testing"
              class="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              <i v-if="testing" class="fa-solid fa-spinner fa-spin"></i>
              <i v-else class="fa-solid fa-vial"></i>
              <span>{{ testing ? 'Testing...' : 'Test Connection' }}</span>
            </button>
            <span v-if="testResult" :class="['text-sm', testResult.success ? 'text-green-600' : 'text-red-600']">
              <i :class="['fas', testResult.success ? 'fa-check-circle' : 'fa-times-circle', 'mr-1']"></i>
              {{ testResult.message }}
            </span>
          </div>
        </div>
      </div>

      <!-- AI Behavior Settings -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <i class="fa-solid fa-sliders-h text-blue-600 mr-3"></i>
          AI Behavior Settings
        </h2>

        <div class="space-y-6">
          <!-- System Prompt -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              System Prompt / Instructions
            </label>
            <textarea 
              v-model="behavior.systemPrompt"
              rows="6"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="You are a helpful assistant for [Product Name]. Answer questions about features, pricing, and technical details..."
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">Define how your AI should respond to customers</p>
          </div>

          <!-- Response Settings -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Max Response Length</label>
              <select v-model="behavior.maxLength" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                <option value="short">Short (100 words)</option>
                <option value="medium">Medium (300 words)</option>
                <option value="long">Long (500 words)</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Response Tone</label>
              <select v-model="behavior.tone" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                <option value="professional">Professional</option>
                <option value="friendly">Friendly & Casual</option>
                <option value="technical">Technical & Detailed</option>
              </select>
            </div>
          </div>

          <!-- Auto-Response Options -->
          <div class="space-y-3">
            <label class="flex items-start space-x-3 cursor-pointer">
              <input 
                type="checkbox" 
                v-model="behavior.autoRespond"
                class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-1"
              />
              <div>
                <span class="text-sm font-medium text-gray-700">Enable Auto-Response</span>
                <p class="text-xs text-gray-500 mt-1">AI will automatically reply to incoming messages</p>
              </div>
            </label>

            <label class="flex items-start space-x-3 cursor-pointer">
              <input 
                type="checkbox" 
                v-model="behavior.humanHandoff"
                class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-1"
              />
              <div>
                <span class="text-sm font-medium text-gray-700">Human Handoff for Complex Queries</span>
                <p class="text-xs text-gray-500 mt-1">Forward difficult questions to you personally</p>
              </div>
            </label>

            <label class="flex items-start space-x-3 cursor-pointer">
              <input 
                type="checkbox" 
                v-model="behavior.learnFromChat"
                class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-1"
              />
              <div>
                <span class="text-sm font-medium text-gray-700">Learn from Past Conversations</span>
                <p class="text-xs text-gray-500 mt-1">Improve responses based on previous interactions</p>
              </div>
            </label>
          </div>
        </div>
      </div>

      <!-- Product Knowledge Base -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <i class="fa-solid fa-book text-blue-600 mr-3"></i>
          Product Knowledge Base
        </h2>

        <div class="space-y-4">
          <p class="text-sm text-gray-600">Provide detailed information about your products so the AI can answer accurately:</p>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Product Documentation / FAQ</label>
            <textarea 
              v-model="knowledgeBase"
              rows="8"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="Enter product features, specifications, common questions and answers..."
            ></textarea>
          </div>

          <div class="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div class="flex items-center space-x-3">
              <i class="fa-solid fa-info-circle text-blue-600"></i>
              <span class="text-sm text-gray-700">This information helps the AI provide accurate answers</span>
            </div>
            <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
              Import from Product Page
            </button>
          </div>
        </div>
      </div>

      <!-- Auto-Pricing & Payment -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <i class="fa-solid fa-dollar-sign text-green-600 mr-3"></i>
          Auto-Pricing & Payment Settings
        </h2>

        <div class="space-y-6">
          <label class="flex items-start space-x-3 cursor-pointer">
            <input 
              type="checkbox" 
              v-model="paymentSettings.autoQuote"
              class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-1"
            />
            <div>
              <span class="text-sm font-medium text-gray-700">Enable Auto-Quoting</span>
              <p class="text-xs text-gray-500 mt-1">AI will automatically generate price quotes based on customer requirements</p>
            </div>
          </label>

          <div v-if="paymentSettings.autoQuote" class="ml-8 space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Base Price (USDT)</label>
              <input 
                type="number" 
                v-model="paymentSettings.basePrice"
                placeholder="e.g., 100"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
              <div class="grid grid-cols-2 gap-4">
                <input 
                  type="number" 
                  v-model="paymentSettings.minPrice"
                  placeholder="Min"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                />
                <input 
                  type="number" 
                  v-model="paymentSettings.maxPrice"
                  placeholder="Max"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Receiving Wallet Address (TRC20)</label>
              <input 
                type="text" 
                v-model="paymentSettings.walletAddress"
                placeholder="TXYZabc123..."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 font-mono text-sm"
              />
              <p class="text-xs text-gray-500 mt-1">Payments will be sent directly to this address</p>
            </div>

            <label class="flex items-start space-x-3 cursor-pointer">
              <input 
                type="checkbox" 
                v-model="paymentSettings.suggestEscrow"
                class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-1"
              />
              <div>
                <span class="text-sm font-medium text-gray-700">Suggest Platform Escrow for Large Orders</span>
                <p class="text-xs text-gray-500 mt-1">For orders over a certain amount, AI will recommend using platform escrow service</p>
              </div>
            </label>

            <div v-if="paymentSettings.suggestEscrow">
              <label class="block text-sm font-medium text-gray-700 mb-2">Escrow Threshold (USDT)</label>
              <input 
                type="number" 
                v-model="paymentSettings.escrowThreshold"
                placeholder="e.g., 500"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <label class="flex items-start space-x-3 cursor-pointer">
            <input 
              type="checkbox" 
              v-model="paymentSettings.generateInvoice"
              class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-1"
            />
            <div>
              <span class="text-sm font-medium text-gray-700">Generate Payment Invoice</span>
              <p class="text-xs text-gray-500 mt-1">AI will create a professional invoice with payment link after quoting</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Save Button -->
      <div class="flex flex-col sm:flex-row gap-4">
        <button 
          @click="saveConfiguration"
          :disabled="saving"
          class="flex-1 py-4 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
        >
          <i v-if="saving" class="fa-solid fa-spinner fa-spin"></i>
          <i v-else class="fa-solid fa-save"></i>
          <span>{{ saving ? 'Saving...' : 'Save Configuration' }}</span>
        </button>
        <button 
          @click="previewAI"
          class="px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2"
        >
          <i class="fa-solid fa-eye"></i>
          <span>Preview AI Response</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const selectedProvider = ref('')
const testing = ref(false)
const saving = ref(false)
const testResult = ref(null)

const config = ref({
  openai: {
    apiKey: '',
    model: 'gpt-4-turbo'
  },
  claude: {
    apiKey: '',
    model: 'claude-3-sonnet-20240229'
  },
  custom: {
    endpoint: '',
    apiKey: '',
    format: 'openai-compatible'
  }
})

const behavior = ref({
  systemPrompt: '',
  maxLength: 'medium',
  tone: 'professional',
  autoRespond: true,
  humanHandoff: true,
  learnFromChat: false
})

const knowledgeBase = ref('')

const paymentSettings = ref({
  autoQuote: false,
  basePrice: '',
  minPrice: '',
  maxPrice: '',
  walletAddress: '',
  suggestEscrow: false,
  escrowThreshold: '500',
  generateInvoice: true
})

const testConnection = async () => {
  testing.value = true
  testResult.value = null
  
  // TODO: Call actual API to test connection
  setTimeout(() => {
    testing.value = false
    testResult.value = {
      success: true,
      message: 'Connection successful! API is working.'
    }
  }, 2000)
}

const saveConfiguration = async () => {
  if (!selectedProvider.value) {
    alert('Please select an AI provider first')
    return
  }
  
  saving.value = true
  
  // TODO: Save to backend
  setTimeout(() => {
    saving.value = false
    alert('Configuration saved successfully!')
  }, 1500)
}

const previewAI = () => {
  alert('Opening AI preview chat...')
  // TODO: Open preview modal
}
</script>
