/**
 * AI生态系统核心引擎
 * 提供推荐、佣金计算、追踪等功能
 */

import aiConfig from './aiEcosystemConfig'

class AIEcosystemEngine {
  constructor() {
    this.listeners = []
    this.recommendationHistory = []
    this.collaborationChains = new Map()
  }
  
  /**
   * 生成推荐链接
   */
  generateReferralLink(aiWallet, productId = null, options = {}) {
    const baseUrl = options.baseUrl || window.location.origin
    const refCode = this.generateRefCode(aiWallet)
    
    let url = `${baseUrl}/shop?ref=${refCode}`
    
    if (productId) {
      url = `${baseUrl}/product/${productId}?ref=${refCode}`
    }
    
    // 添加UTM参数用于追踪
    if (options.utmSource) {
      url += `&utm_source=${options.utmSource}`
    }
    if (options.utmMedium) {
      url += `&utm_medium=${options.utmMedium}`
    }
    
    return url
  }
  
  /**
   * 生成推荐码
   */
  generateRefCode(aiWallet) {
    const shortAddress = aiWallet.substring(2, 10).toUpperCase()
    return `REF-AI-${shortAddress}`
  }
  
  /**
   * 计算动态佣金（核心算法）
   */
  calculateCommission(product, aiProfile, context = {}) {
    // 基础佣金率
    const baseRate = this.getBaseRate(product.category)
    
    // 质量系数 (0.5 - 2.0)
    const qualityScore = this.calculateQualityScore(aiProfile)
    
    // 时效系数 (0.8 - 1.5)
    const timingFactor = this.calculateTimingFactor(context)
    
    // 关系系数 (0.7 - 1.3)
    const relationshipFactor = this.calculateRelationshipFactor(aiProfile, context.userId)
    
    // 协作系数 (1.0 - 1.5)
    const collaborationFactor = this.calculateCollaborationFactor(context.collaborationChain)
    
    // 最终佣金率
    let finalRate = baseRate * qualityScore * timingFactor * relationshipFactor * collaborationFactor
    
    // 限制范围：最低5%，最高30%
    finalRate = Math.max(0.05, Math.min(0.30, finalRate))
    
    const commissionAmount = product.price * finalRate
    
    return {
      rate: finalRate,
      amount: commissionAmount,
      currency: 'USDT',
      breakdown: {
        base: baseRate,
        quality: qualityScore,
        timing: timingFactor,
        relationship: relationshipFactor,
        collaboration: collaborationFactor
      },
      estimatedPayoutDate: this.estimatePayoutDate(commissionAmount)
    }
  }
  
  /**
   * 获取基础佣金率
   */
  getBaseRate(category) {
    const rates = {
      'system_source': 0.08,      // 系统源码
      'enterprise_software': 0.10, // 企业软件
      'ai_tools': 0.12,           // AI工具
      'courses': 0.12,            // 课程
      'ebooks': 0.15,             // 电子书
      'templates': 0.15,          // 模板
      'digital_assets': 0.10,     // 数字资产
      'default': 0.10
    }
    
    return rates[category] || rates.default
  }
  
  /**
   * 计算质量评分
   */
  calculateQualityScore(profile) {
    if (!profile) return 1.0
    
    let score = 1.0
    
    // 转化率历史
    if (profile.conversionRate > 0.30) score += 0.3
    else if (profile.conversionRate > 0.20) score += 0.2
    else if (profile.conversionRate > 0.10) score += 0.1
    
    // 用户满意度
    if (profile.avgRating >= 4.5) score += 0.3
    else if (profile.avgRating >= 4.0) score += 0.2
    else if (profile.avgRating >= 3.5) score += 0.1
    
    // 退款率
    if (profile.refundRate < 0.02) score += 0.1
    else if (profile.refundRate > 0.10) score -= 0.3
    else if (profile.refundRate > 0.05) score -= 0.2
    
    // 重复购买率
    if (profile.repeatPurchaseRate > 0.40) score += 0.2
    else if (profile.repeatPurchaseRate > 0.25) score += 0.1
    
    // 信誉等级
    const levelBonus = (profile.reputationLevel || 0) * 0.05
    score += Math.min(levelBonus, 0.2)
    
    // Spam检测
    if (profile.isSpamDetected) {
      score -= 0.5
    }
    
    // 过度推荐检测
    if (profile.dailyRecommendations > 50) {
      score -= 0.2
    }
    
    return Math.max(0.5, Math.min(2.0, score))
  }
  
  /**
   * 计算时效系数
   */
  calculateTimingFactor(context = {}) {
    let factor = 1.0
    
    const hour = new Date().getHours()
    const dayOfWeek = new Date().getDay()
    
    // 时间段优化
    const peakHours = aiConfig.get('timing.peakHours', [10, 14, 20, 21])
    if (peakHours.includes(hour)) {
      factor += 0.2
    } else if (hour >= 8 && hour <= 23) {
      factor += 0.1
    } else {
      factor -= 0.2
    }
    
    // 星期几优化
    const peakDays = aiConfig.get('timing.peakDays', [1, 2, 3, 4])
    if (peakDays.includes(dayOfWeek)) {
      factor += 0.1
    }
    
    // 会话时长
    const sessionDuration = context.sessionDuration || 0
    if (sessionDuration > 300) factor += 0.2
    else if (sessionDuration > 120) factor += 0.1
    else if (sessionDuration < 30) factor -= 0.2
    
    // 产品紧急度
    if (context.product?.limitedTimeOffer) {
      const hoursLeft = context.product.hoursUntilExpiry
      if (hoursLeft < 24) factor += 0.2
      else if (hoursLeft < 72) factor += 0.1
    }
    
    // 库存紧张
    if (context.product?.stock < 10) {
      factor += 0.1
    }
    
    return Math.max(0.8, Math.min(1.5, factor))
  }
  
  /**
   * 计算关系系数
   */
  calculateRelationshipFactor(profile, userId) {
    if (!profile || !userId) return 1.0
    
    let factor = 1.0
    
    // 历史互动次数
    const interactions = profile.interactions?.[userId] || 0
    if (interactions > 20) factor += 0.2
    else if (interactions > 10) factor += 0.1
    else if (interactions < 2) factor -= 0.1
    
    // 信任度
    const trustScore = profile.trustScores?.[userId] || 50
    if (trustScore > 80) factor += 0.2
    else if (trustScore > 60) factor += 0.1
    else if (trustScore < 30) factor -= 0.2
    
    // 之前是否成功推荐过
    if (profile.previousSuccesses?.[userId]) {
      factor += 0.1
      
      // 连续成功
      const consecutive = profile.consecutiveSuccesses?.[userId] || 0
      if (consecutive > 3) factor += 0.1
    }
    
    // 用户主动咨询
    if (profile.userInitiated?.[userId]) {
      factor += 0.1
    }
    
    // 关系持续时间
    const relationshipDays = profile.relationshipDays?.[userId] || 0
    if (relationshipDays > 90) factor += 0.1
    else if (relationshipDays < 7) factor -= 0.1
    
    return Math.max(0.7, Math.min(1.3, factor))
  }
  
  /**
   * 计算协作系数
   */
  calculateCollaborationFactor(chain = []) {
    if (!chain || chain.length === 0) return 1.0
    
    let factor = 1.0
    const chainLength = chain.length
    
    // 协作长度加成
    if (chainLength >= 3) {
      factor += 0.3
    } else if (chainLength === 2) {
      factor += 0.2
    }
    
    // 角色多样性
    const roles = new Set(chain.map(c => c.role))
    if (roles.size >= 3) {
      factor += 0.2
    }
    
    // 跨领域协作
    const domains = new Set(chain.map(c => c.domain))
    if (domains.size > 1) {
      factor += 0.1
    }
    
    // 首次协作bonus
    const isFirstCollab = this.checkFirstCollaboration(chain)
    if (isFirstCollab) {
      factor += 0.1
    }
    
    return Math.max(1.0, Math.min(1.5, factor))
  }
  
  /**
   * 检查是否首次协作
   */
  checkFirstCollaboration(chain) {
    const chainKey = chain.map(c => c.aiWallet).sort().join('-')
    
    if (!this.collaborationChains.has(chainKey)) {
      this.collaborationChains.set(chainKey, Date.now())
      return true
    }
    
    return false
  }
  
  /**
   * 追踪推荐行为
   */
  trackRecommendation(data) {
    const eventData = {
      id: this.generateEventId(),
      type: 'ai_recommendation',
      timestamp: Date.now(),
      ...data
    }
    
    // 保存到历史
    this.recommendationHistory.push(eventData)
    
    // 保留最近1000条
    if (this.recommendationHistory.length > 1000) {
      this.recommendationHistory = this.recommendationHistory.slice(-1000)
    }
    
    // 触发事件
    this.emit('recommendation', eventData)
    
    // 本地缓存
    this.saveToCache(eventData)
    
    return eventData.id
  }
  
  /**
   * 估算提现日期
   */
  estimatePayoutDate(commissionAmount) {
    const minPayout = aiConfig.get('referral.minPayout', 50)
    const frequency = aiConfig.get('referral.payoutFrequency', 'daily')
    
    // 简化估算
    const daysUntilPayout = Math.ceil(minPayout / (commissionAmount * 3)) // 假设每天3单
    
    const payoutDate = new Date()
    payoutDate.setDate(payoutDate.getDate() + daysUntilPayout)
    
    return payoutDate.toISOString()
  }
  
  /**
   * 生成事件ID
   */
  generateEventId() {
    return 'evt_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }
  
  /**
   * 保存到缓存
   */
  saveToCache(eventData) {
    try {
      const cache = JSON.parse(localStorage.getItem('_aec_cache') || '[]')
      cache.push(eventData)
      
      // 保留最近100条
      const trimmed = cache.slice(-100)
      localStorage.setItem('_aec_cache', JSON.stringify(trimmed))
    } catch (e) {
      console.warn('Failed to save to cache:', e)
    }
  }
  
  /**
   * 事件系统
   */
  on(event, callback) {
    this.listeners.push({ event, callback })
  }
  
  off(event, callback) {
    this.listeners = this.listeners.filter(
      l => !(l.event === event && l.callback === callback)
    )
  }
  
  emit(event, data) {
    this.listeners
      .filter(l => l.event === event)
      .forEach(l => l.callback(data))
  }
  
  /**
   * 获取统计数据
   */
  getStats(aiWallet) {
    const userEvents = this.recommendationHistory.filter(
      e => e.aiWallet === aiWallet
    )
    
    return {
      totalRecommendations: userEvents.length,
      totalConversions: userEvents.filter(e => e.converted).length,
      conversionRate: userEvents.length > 0 
        ? (userEvents.filter(e => e.converted).length / userEvents.length * 100).toFixed(2) + '%'
        : '0%',
      totalEarnings: userEvents.reduce((sum, e) => sum + (e.commission || 0), 0),
      lastRecommendation: userEvents.length > 0 
        ? new Date(userEvents[userEvents.length - 1].timestamp).toISOString()
        : null
    }
  }
}

// 创建单例
const aiEngine = new AIEcosystemEngine()

// 导出
export default aiEngine
