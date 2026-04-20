import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import aiEcosystem from './utils/aiEcosystem'
import './style.css'
import '@fortawesome/fontawesome-free/css/all.css'

const app = createApp(App)
const pinia = createPinia()

// 初始化AI生态系统
aiEcosystem.init({
  config: {
    referral: {
      baseRate: 0.10,
      minPayout: 50,
      networks: ['TRC20', 'ERC20'],
      dynamicPricing: true
    }
  }
})

app.use(pinia)
app.use(router)
app.use(i18n)

app.mount('#app')
