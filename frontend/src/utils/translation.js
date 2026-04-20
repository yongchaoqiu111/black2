/**
 * Translation Service
 * 支持多API轮询调度，自动故障转移
 */

class TranslationService {
  constructor() {
    // API配置（需要您在后端实现）
    this.apis = [
      { name: 'baidu', priority: 1, active: true },
      { name: 'tencent', priority: 2, active: true },
      { name: 'deepl', priority: 3, active: true }
    ]
    
    // 缓存已翻译的内容
    this.cache = new Map()
  }

  /**
   * 翻译文本
   * @param {string} text - 要翻译的文本
   * @param {string} from - 源语言 (auto, zh, en, ja, ko, etc.)
   * @param {string} to - 目标语言
   * @returns {Promise<string>} 翻译后的文本
   */
  async translate(text, from = 'auto', to = 'en') {
    // 检查缓存
    const cacheKey = `${text}_${from}_${to}`
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)
    }

    // 尝试各个API
    let lastError = null
    
    for (const api of this.apis) {
      if (!api.active) continue
      
      try {
        const result = await this.callApi(api.name, text, from, to)
        
        // 缓存结果
        this.cache.set(cacheKey, result)
        
        // 限制缓存大小
        if (this.cache.size > 1000) {
          const firstKey = this.cache.keys().next().value
          this.cache.delete(firstKey)
        }
        
        return result
      } catch (error) {
        console.warn(`API ${api.name} failed:`, error.message)
        lastError = error
        
        // 如果API返回配额超限，标记为不活跃
        if (error.message.includes('quota') || error.message.includes('limit')) {
          api.active = false
          console.log(`API ${api.name} quota exceeded, switching to next API`)
        }
      }
    }

    // 所有API都失败了
    throw new Error('Translation service unavailable: ' + lastError?.message)
  }

  /**
   * 调用具体的翻译API
   * 这里需要您根据实际的后端接口来实现
   */
  async callApi(apiName, text, from, to) {
    // TODO: 替换为您的后端API地址
    const response = await fetch('/api/translate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        api: apiName,
        text: text,
        from: from,
        to: to
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Translation failed')
    }

    const data = await response.json()
    return data.translatedText
  }

  /**
   * 批量翻译
   */
  async translateBatch(messages, to = 'en') {
    const results = []
    
    for (const message of messages) {
      try {
        const translated = await this.translate(message.text, message.from, to)
        results.push({
          ...message,
          translatedText: translated
        })
      } catch (error) {
        console.error(`Failed to translate message ${message.id}:`, error)
        results.push(message) // 保留原文
      }
    }
    
    return results
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cache.clear()
  }

  /**
   * 重置API状态（新月或手动重置）
   */
  resetApis() {
    this.apis.forEach(api => api.active = true)
    this.clearCache()
  }
}

// 创建单例
export const translationService = new TranslationService()
export default translationService
