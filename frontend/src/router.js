import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/ai-agents',
    name: 'AIAgents',
    component: () => import('@/pages/AIAgents.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@/pages/Analytics.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/chat',
    redirect: '/'
  },
  {
    path: '/widget',
    name: 'ChatWidget',
    component: () => import('@/pages/Widget.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('@/pages/Knowledge.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/pages/Users.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/pages/ForgotPassword.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/contact-admin',
    name: 'ContactAdmin',
    component: () => import('@/pages/ContactAdmin.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/ocr',
    name: 'OCR',
    component: () => import('@/pages/OCR.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/integrations',
    name: 'Integrations',
    component: () => import('@/pages/Integrations.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/permissions',
    name: 'ChatbotPermissions',
    component: () => import('@/pages/ChatbotPermissions.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
  {
    path: '/ai-agents/:id',
    name: 'AgentDetail',
    component: () => import('@/pages/AgentDetail.vue'),
    meta: { requiresAuth: false, layout: 'AppLayout' }
  },
]

let router = createRouter({
  history: createWebHistory('/ai-agent'),
  routes,
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Thử khôi phục phiên từ server nếu chưa xác thực
  if (!authStore.isAuthenticated) {
    try {
      await authStore.fetchCurrentUser()
    } catch (_) {
      /* ignore */
    }
  }

  // Nếu chưa login và không phải trang /login hay widget thì chuyển hướng
  if (!authStore.isAuthenticated && to.path !== '/login' && to.path !== '/widget') {
    return next({ path: '/login', query: { next: to.fullPath } })
  }
  // Nếu đã login mà vào trang login thì chuyển về dashboard
  if (to.path === '/login' && authStore.isAuthenticated) {
    return next('/')
  }
  next()
})

export default router
