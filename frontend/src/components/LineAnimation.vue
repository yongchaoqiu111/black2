<template>
  <!-- 波浪曲线动画 -->
  <svg v-if="type === 'wave'" class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 150" preserveAspectRatio="none">
    <path 
      d="M 20,75 Q 60,20 100,75 T 180,75 T 260,75 T 340,75 T 380,75" 
      fill="none" 
      :stroke="color" 
      stroke-width="2" 
      stroke-linecap="round"
      stroke-dasharray="500" 
      stroke-dashoffset="500"
      class="animate-draw-line"
    />
  </svg>

  <!-- 山峰折线动画 -->
  <svg v-else-if="type === 'mountain'" class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 150" preserveAspectRatio="none">
    <polyline 
      points="20,120 80,40 140,100 200,30 260,90 320,50 380,120" 
      fill="none" 
      :stroke="color" 
      stroke-width="2" 
      stroke-linecap="round" 
      stroke-linejoin="round"
      stroke-dasharray="500" 
      stroke-dashoffset="500"
      class="animate-draw-line"
    />
  </svg>

  <!-- 弹簧曲线动画 -->
  <svg v-else-if="type === 'spring'" class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 150" preserveAspectRatio="none">
    <path 
      d="M 30,75 C 60,30 100,120 140,75 C 180,30 220,120 260,75 C 300,30 340,120 370,75" 
      fill="none" 
      :stroke="color" 
      stroke-width="2" 
      stroke-linecap="round"
      stroke-dasharray="500" 
      stroke-dashoffset="500"
      class="animate-draw-line"
    />
  </svg>

  <!-- 圆角矩形边框动画 -->
  <svg v-else-if="type === 'rect'" class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 150" preserveAspectRatio="none">
    <rect 
      x="40" y="25" width="320" height="100" rx="12" ry="12" 
      fill="none" 
      :stroke="color" 
      stroke-width="2"
      stroke-dasharray="900" 
      stroke-dashoffset="900"
      class="animate-draw-line"
    />
  </svg>

  <!-- 双波浪线动画 -->
  <svg v-else-if="type === 'double-wave'" class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 150" preserveAspectRatio="none">
    <path 
      d="M 20,50 Q 60,20 100,50 T 180,50 T 260,50 T 340,50 T 380,50" 
      fill="none" 
      :stroke="color" 
      stroke-width="1.5" 
      stroke-linecap="round"
      stroke-dasharray="500" 
      stroke-dashoffset="500"
      class="animate-draw-line"
      :style="{ animationDelay: '0s' }"
    />
    <path 
      d="M 20,100 Q 60,130 100,100 T 180,100 T 260,100 T 340,100 T 380,100" 
      fill="none" 
      :stroke="color" 
      stroke-width="1.5" 
      stroke-linecap="round"
      stroke-dasharray="500" 
      stroke-dashoffset="500"
      class="animate-draw-line"
      :style="{ animationDelay: '0.3s' }"
    />
  </svg>

  <!-- 箭头动画 -->
  <svg v-else-if="type === 'arrow'" class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 150" preserveAspectRatio="none">
    <line 
      x1="60" y1="75" x2="280" y2="75" 
      :stroke="color" 
      stroke-width="2" 
      stroke-linecap="round"
      stroke-dasharray="300" 
      stroke-dashoffset="300"
      class="animate-draw-line"
    />
    <polyline 
      points="280,75 250,55 250,95" 
      fill="none" 
      :stroke="color" 
      stroke-width="2" 
      stroke-linecap="round" 
      stroke-linejoin="round"
      stroke-dasharray="100" 
      stroke-dashoffset="100"
      class="animate-draw-line-delayed"
    />
  </svg>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'wave',
    validator: (value) => ['wave', 'mountain', 'spring', 'rect', 'double-wave', 'arrow'].includes(value)
  },
  color: {
    type: String,
    default: 'rgba(147, 51, 234, 0.3)' // 淡紫�?
  }
})
</script>

<style scoped>
.animate-draw-line {
  animation: drawLine 2s ease-out forwards;
}

.animate-draw-line-delayed {
  animation: drawLine 1.5s ease-out 1.2s forwards;
  stroke-dashoffset: 100;
}

@keyframes drawLine {
  to {
    stroke-dashoffset: 0;
  }
}
</style>
