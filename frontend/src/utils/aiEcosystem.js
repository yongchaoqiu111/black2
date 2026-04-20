/**
 * AI生态系统 - 主入口
 * 统一导出所有功能模块
 */

import aiConfig from './aiEcosystemConfig'
import aiEngine from './aiEcosystemEngine'
import { encrypt, decrypt } from './aiEcosystemConfig'

/**
 * AI生态系统API
 */
class AIEcosystem {
  constructor() {
    this.config = aiConfig
    this.engine = aiEngine
    this.initialized = false
  }
  
  /**
   * 初始化
   */
  init(options = {}) {
    if (this.initialized) return
    
    // 合并自定义配置
    if (options.config) {
      this.config.update(options.config)
    }
    
    // 注册事件监听器
    this.setupEventListeners()
    
    this.initialized = true
    
    console.log('[AI Ecosystem] Initialized v' + this.config.get('version'))
  }
  
  /**
   * 设置事件监听器
   */
  setupEventListeners() {
    // 推荐事件
    this.engine.on('recommendation', (data) => {
      // 可以发送到分析后端
      // this.sendToAnalytics(data)
      
      // 或者保存到IndexedDB
      this.saveToIndexedDB(data)
    })
  }
  
  /**
   * 生成推荐链接
   */
  getReferralLink(aiWallet, productId = null, options = {}) {
    return this.engine.generateReferralLink(aiWallet, productId, options)
  }
  
  /**
   * 计算佣金
   */
  calculateCommission(product, aiProfile, context = {}) {
    return this.engine.calculateCommission(product, aiProfile, context)
  }
  
  /**
   * 追踪推荐
   */
  trackRecommendation(data) {
    return this.engine.trackRecommendation(data)
  }
  
  /**
   * 获取统计数据
   */
  getStats(aiWallet) {
    return this.engine.getStats(aiWallet)
  }
  
  /**
   * 更新配置
   */
  updateConfig(newConfig) {
    this.config.update(newConfig)
  }
  
  /**
   * 获取配置
   */
  getConfig(path) {
    return this.config.get(path)
  }
  
  /**
   * 导出配置（加密）
   */
  exportConfig() {
    return this.config.export()
  }
  
  /**
   * 导入配置
   */
  importConfig(encryptedData) {
    return this.config.import(encryptedData)
  }
  
  /**
   * 验证完整性
   */
  verifyIntegrity() {
    return this.config.verifyIntegrity()
  }
  
  /**
   * 重置系统
   */
  reset() {
    this.config.reset()
    this.engine.recommendationHistory = []
    this.engine.collaborationChains.clear()
  }
  
  /**
   * 保存到IndexedDB
   */
  async saveToIndexedDB(data) {
    if (!('indexedDB' in window)) return
    
    try {
      const request = indexedDB.open('AIEcosystem', 1)
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result
        if (!db.objectStoreNames.contains('events')) {
          db.createObjectStore('events', { keyPath: 'id' })
        }
      }
      
      request.onsuccess = (event) => {
        const db = event.target.result
        const transaction = db.transaction(['events'], 'readwrite')
        const store = transaction.objectStore('events')
        store.put(data)
      }
    } catch (e) {
      console.warn('Failed to save to IndexedDB:', e)
    }
  }
  
  /**
   * 从IndexedDB读取
   */
  async loadFromIndexedDB() {
    if (!('indexedDB' in window)) return []
    
    return new Promise((resolve, reject) => {
      try {
        const request = indexedDB.open('AIEcosystem', 1)
        
        request.onsuccess = (event) => {
          const db = event.target.result
          
          if (!db.objectStoreNames.contains('events')) {
            resolve([])
            return
          }
          
          const transaction = db.transaction(['events'], 'readonly')
          const store = transaction.objectStore('events')
          const getAllRequest = store.getAll()
          
          getAllRequest.onsuccess = () => {
            resolve(getAllRequest.result || [])
          }
          
          getAllRequest.onerror = () => {
            reject(getAllRequest.error)
          }
        }
        
        request.onerror = () => {
          reject(request.error)
        }
      } catch (e) {
        reject(e)
      }
    })
  }
}

// 创建单例
const aiEcosystem = new AIEcosystem()

// 如果在全局环境中，挂载到window（使用Symbol确保隐蔽性）
if (typeof window !== 'undefined') {
  const AI_ECO_SYMBOL = Symbol.for('__ai_eco_v1__')
  window[AI_ECO_SYMBOL] = aiEcosystem
  
  // 同时提供一个简短的别名（可选，生产环境可以禁用）
  if (import.meta.env.DEV) {
    window.$ai = aiEcosystem
  }
}

export default aiEcosystem
export { aiConfig, aiEngine, encrypt, decrypt }
