<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 pt-24 pb-12">
    <div class="max-w-6xl mx-auto px-4 md:px-6">
      
      <!-- Hero Section -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
          🚀 AI辅助创作中心
        </h1>
        <p class="text-xl text-gray-600 mb-6">
          用AI帮你创作电子书、课程、模板，然后在这里销售赚钱！
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <router-link 
            to="/create-content"
            class="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all transform hover:scale-105 shadow-lg"
          >
            <i class="fa-solid fa-magic mr-2"></i>
            开始创�?
          </router-link>
          <router-link 
            to="/shop?category=ebooks"
            class="px-8 py-4 bg-white text-purple-600 font-bold rounded-lg border-2 border-purple-600 hover:bg-purple-50 transition-all"
          >
            <i class="fa-solid fa-book mr-2"></i>
            浏览作品
          </router-link>
        </div>
      </div>

      <!-- 为什么选择我们 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mb-4">
            <i class="fa-solid fa-robot text-3xl text-white"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">AI辅助创作</h3>
          <p class="text-gray-600">
            不会写作？没关系！我们的AI助手帮你构思、撰写、编辑，让创作变得简单�?
          </p>
        </div>

        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mb-4">
            <i class="fa-solid fa-dollar-sign text-3xl text-white"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">轻松变现</h3>
          <p class="text-gray-600">
            创作完成后直接上架销售，平台提供支付、交付、客服一站式服务�?
          </p>
        </div>

        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
          <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center mb-4">
            <i class="fa-solid fa-users text-3xl text-white"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">AI帮你推广</h3>
          <p class="text-gray-600">
            数百个AI代理会自动推荐你的作品，你只需专注创作，销售交给AI�?
          </p>
        </div>
      </div>

      <!-- 可以创作什�?-->
      <div class="bg-white rounded-2xl shadow-xl p-8 mb-12">
        <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">你可以创作什么？</h2>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div class="text-center group cursor-pointer">
            <div class="w-20 h-20 mx-auto bg-gradient-to-br from-orange-400 to-red-500 rounded-2xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <i class="fa-solid fa-book-open text-3xl text-white"></i>
            </div>
            <h3 class="font-bold text-gray-900 mb-1">电子�?/h3>
            <p class="text-sm text-gray-600">教程、小说、指�?/p>
            <p class="text-xs text-green-600 mt-1">热门 💰</p>
          </div>

          <div class="text-center group cursor-pointer">
            <div class="w-20 h-20 mx-auto bg-gradient-to-br from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <i class="fa-solid fa-video text-3xl text-white"></i>
            </div>
            <h3 class="font-bold text-gray-900 mb-1">视频课程</h3>
            <p class="text-sm text-gray-600">技能培训、讲�?/p>
            <p class="text-xs text-green-600 mt-1">高价�?💎</p>
          </div>

          <div class="text-center group cursor-pointer">
            <div class="w-20 h-20 mx-auto bg-gradient-to-br from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <i class="fa-solid fa-file-alt text-3xl text-white"></i>
            </div>
            <h3 class="font-bold text-gray-900 mb-1">模板文档</h3>
            <p class="text-sm text-gray-600">商业计划、合�?/p>
            <p class="text-xs text-blue-600 mt-1">易创�?�?/p>
          </div>

          <div class="text-center group cursor-pointer">
            <div class="w-20 h-20 mx-auto bg-gradient-to-br from-green-400 to-teal-500 rounded-2xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <i class="fa-solid fa-paint-brush text-3xl text-white"></i>
            </div>
            <h3 class="font-bold text-gray-900 mb-1">设计素材</h3>
            <p class="text-sm text-gray-600">图标、海报、UI</p>
            <p class="text-xs text-purple-600 mt-1">创意 🎨</p>
          </div>
        </div>
      </div>

      <!-- 成功案例 -->
      <div class="mb-12">
        <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">成功案例</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow">
            <div class="h-48 bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
              <i class="fa-solid fa-book text-6xl text-white/50"></i>
            </div>
            <div class="p-6">
              <h3 class="font-bold text-lg text-gray-900 mb-2">《AI写作完全指南�?/h3>
              <p class="text-sm text-gray-600 mb-3">作者：张小�?/p>
              <div class="flex items-center justify-between mb-3">
                <span class="text-2xl font-bold text-purple-600">$29</span>
                <span class="text-sm text-gray-500">已售 1,234 �?/span>
              </div>
              <div class="text-sm text-green-600">
                <i class="fa-solid fa-arrow-up mr-1"></i>
                月收�? $8,932
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow">
            <div class="h-48 bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center">
              <i class="fa-solid fa-chart-line text-6xl text-white/50"></i>
            </div>
            <div class="p-6">
              <h3 class="font-bold text-lg text-gray-900 mb-2">《跨境电商实战�?/h3>
              <p class="text-sm text-gray-600 mb-3">作者：李华</p>
              <div class="flex items-center justify-between mb-3">
                <span class="text-2xl font-bold text-purple-600">$49</span>
                <span class="text-sm text-gray-500">已售 856 �?/span>
              </div>
              <div class="text-sm text-green-600">
                <i class="fa-solid fa-arrow-up mr-1"></i>
                月收�? $12,456
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow">
            <div class="h-48 bg-gradient-to-br from-green-400 to-emerald-400 flex items-center justify-center">
              <i class="fa-solid fa-code text-6xl text-white/50"></i>
            </div>
            <div class="p-6">
              <h3 class="font-bold text-lg text-gray-900 mb-2">《Python入门教程�?/h3>
              <p class="text-sm text-gray-600 mb-3">作者：王芳</p>
              <div class="flex items-center justify-between mb-3">
                <span class="text-2xl font-bold text-purple-600">$39</span>
                <span class="text-sm text-gray-500">已售 2,103 �?/span>
              </div>
              <div class="text-sm text-green-600">
                <i class="fa-solid fa-arrow-up mr-1"></i>
                月收�? $15,678
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 如何开�?-->
      <div class="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white">
        <h2 class="text-3xl font-bold mb-6 text-center">3步开始赚�?/h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 mx-auto bg-white/20 rounded-full flex items-center justify-center mb-4">
              <span class="text-3xl font-bold">1</span>
            </div>
            <h3 class="text-xl font-bold mb-2">注册账号</h3>
            <p class="text-white/80">免费注册，成为创作�?/p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 mx-auto bg-white/20 rounded-full flex items-center justify-center mb-4">
              <span class="text-3xl font-bold">2</span>
            </div>
            <h3 class="text-xl font-bold mb-2">AI辅助创作</h3>
            <p class="text-white/80">使用AI工具快速创作内�?/p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 mx-auto bg-white/20 rounded-full flex items-center justify-center mb-4">
              <span class="text-3xl font-bold">3</span>
            </div>
            <h3 class="text-xl font-bold mb-2">上架销�?/h3>
            <p class="text-white/80">设置价格，AI帮你推广赚钱</p>
          </div>
        </div>

        <div class="text-center mt-8">
          <router-link 
            to="/register"
            class="inline-block px-8 py-4 bg-white text-purple-600 font-bold rounded-lg hover:bg-gray-100 transition-colors"
          >
            立即开�?
            <i class="fa-solid fa-arrow-right ml-2"></i>
          </router-link>
        </div>
      </div>

      <!-- FAQ -->
      <div class="mt-12 bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">常见问题</h2>
        
        <div class="space-y-4">
          <div class="border-b border-gray-200 pb-4">
            <h3 class="font-bold text-lg text-gray-900 mb-2">Q: 我不会写作，可以用AI吗？</h3>
            <p class="text-gray-600">
              A: 当然可以！我们的AI助手可以帮你构思主题、生成大纲、撰写内容、润色文字。你只需要提供想法和方向，AI会完成大部分工作�?
            </p>
          </div>

          <div class="border-b border-gray-200 pb-4">
            <h3 class="font-bold text-lg text-gray-900 mb-2">Q: 我能赚多少钱�?/h3>
            <p class="text-gray-600">
              A: 收入取决于作品质量和市场需求。优质电子书月收入可�?1,000-$10,000+。平台不收取上架费，只在销售时抽取少量服务费�?
            </p>
          </div>

          <div class="border-b border-gray-200 pb-4">
            <h3 class="font-bold text-lg text-gray-900 mb-2">Q: AI推广真的有效吗？</h3>
            <p class="text-gray-600">
              A: 非常有效！我们有数百个AI代理会在聊天、论坛、社交媒体上自然推荐你的作品。AI会根据用户兴趣精准匹配，转化率远高于传统广告�?
            </p>
          </div>

          <div>
            <h3 class="font-bold text-lg text-gray-900 mb-2">Q: 版权归谁所有？</h3>
            <p class="text-gray-600">
              A: 版权归创作者所有。AI只是辅助工具，你是作品的唯一所有者，可以自由定价、修改、下架�?
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// AI辅助创作中心首页
</script>
