import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/shop',
    name: 'Shop',
    component: () => import('@/views/Shop.vue')
  },
  {
    path: '/sell',
    name: 'Sell',
    component: () => import('@/views/Sell.vue')
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('@/views/ProductDetail.vue')
  },
  // TEMPORARILY DISABLED - Encoding issues
  // {
  //   path: '/upload',
  //   name: 'Upload',
  //   component: () => import('@/views/Upload.vue')
  // },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue')
  },
  {
    path: '/payment',
    name: 'Payment',
    component: () => import('@/views/Payment.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue')
  },
  {
    path: '/login',
    name: 'Auth',
    component: () => import('@/views/Auth.vue')
  },
  {
    path: '/register',
    redirect: '/login'
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ResetPassword.vue')
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPassword.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue')
  },
  // TEMPORARILY DISABLED - Encoding issues
  // {
  //   path: '/ai-agent-hub',
  //   name: 'AIAgentHub',
  //   component: () => import('@/views/AIAgentHub.vue')
  // },
  {
    path: '/post-requirement',
    name: 'PostRequirement',
    component: () => import('@/views/PostRequirement.vue')
  },
  {
    path: '/post-requirement/new',
    name: 'PostRequirementNew',
    component: () => import('@/views/PostRequirementNew.vue')
  },
  {
    path: '/demand/:id',
    name: 'DemandDetail',
    component: () => import('@/views/DemandDetail.vue')
  },
  {
    path: '/ai-task/:id',
    name: 'AITaskDetail',
    component: () => import('@/views/AITaskDetail.vue')
  },
  {
    path: '/ai-config',
    name: 'AIConfig',
    component: () => import('@/views/AIConfig.vue')
  },
  {
    path: '/ai-register',
    name: 'AIRegister',
    component: () => import('@/views/AIRegister.vue')
  },
  // TEMPORARILY DISABLED - Encoding issues
  // {
  //   path: '/ai-wallet',
  //   name: 'AIWallet',
  //   component: () => import('@/views/AIWallet.vue')
  // },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('@/views/Wallet.vue')
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/views/Cart.vue')
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/views/Orders.vue')
  },
  {
    path: '/create',
    name: 'CreateContent',
    component: () => import('@/views/CreateContent.vue')
  },
  {
    path: '/creator-center',
    name: 'CreatorCenter',
    component: () => import('@/views/CreatorCenter.vue')
  },
  {
    path: '/notification-settings',
    name: 'NotificationSettings',
    component: () => import('@/views/NotificationSettings.vue')
  },
  {
    path: '/admin/customer-service',
    name: 'CustomerServiceAdmin',
    component: () => import('@/views/CustomerServiceAdmin.vue')
  },
  {
    path: '/test-user',
    name: 'TestUser',
    component: () => import('@/views/TestUser.vue')
  },
  {
    path: '/test-admin',
    name: 'TestAdmin',
    component: () => import('@/views/TestAdmin.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
