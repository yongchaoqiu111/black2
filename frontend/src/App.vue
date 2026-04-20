<template>
  <Layout>
    <router-view />
  </Layout>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { initSocket, disconnectSocket } from '@/utils/websocket'

// 全局初始化 WebSocket
onMounted(() => {
  const token = localStorage.getItem('token') || 'demo-token'
  initSocket(token)
  console.log('✅ [App] WebSocket 全局初始化完成')
})

onUnmounted(() => {
  disconnectSocket()
  console.log('🔌 [App] WebSocket 已断开')
})
</script>

<style>
</style>
