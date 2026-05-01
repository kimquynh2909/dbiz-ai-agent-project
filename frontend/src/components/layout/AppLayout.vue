<template>
  <!-- Gốc: khóa theo viewport, tránh min-h-screen gây lệch -->
  <div
    class="min-h-screen min-h-0 overflow-y-auto lg:h-screen lg:overflow-hidden lg:grid lg:grid-cols-[var(--sb-w)_1fr]"
    :style="{
      '--sb-w': sidebarCollapsed ? '5rem' : '18rem',
      '--header-h': '4rem',
    }"
  >
    <Sidebar
      class="shrink-0"
      :sidebar-collapsed="sidebarCollapsed"
      :sidebar-open="sidebarOpen"
      :current-user="currentUser"
      :logo="{ logo: dbizLogo, minilogo }"
      @toggle-collapse="toggleSidebar"
      @update:sidebarOpen="(val) => (sidebarOpen = val)"
      @logout="logout"
    />

    <!-- Cột phải = flex-col, KHÓA chiều cao đúng cách -->
    <div ref="mainRef" class="flex flex-col min-h-0 overflow-hidden">
      <HeaderBar
        class="shrink-0"
        :page-title="getPageTitle()"
        :page-description="getPageDescription()"
        :current-locale="currentLocale"
        :current-user="currentUser"
        @toggle-sidebar="sidebarOpen = !sidebarOpen"
        @change-language="
          (loc) => {
            currentLocale = loc
            changeLanguage()
          }
        "
        @go-to-profile="goToProfile"
        @go-to-settings="goToSettings"
        @logout="logout"
      />

      <main class="flex-1 min-h-0 overflow-hidden flex flex-col">
        <div
          ref="mainContentRef"
          class="flex-1 min-h-0 overflow-y-auto overflow-x-hidden bg-gray-50"
          :style="{
            height: isMobile ? 'calc(100dvh - var(--header-h, 4rem))' : 'calc(100vh - var(--header-h, 4rem))'
          }"
        >
          <router-view class="w-full h-full min-h-0" />
        </div>
      </main>
    </div>

    <!-- Backdrop mobile -->
    <div v-if="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import dbizLogo from '@/assets/dbizlogodark.png'
import minilogo from '@/assets/minilogo.png'
import Sidebar from './Sidebar.vue'
import HeaderBar from './HeaderBar.vue'
import { mainMenu, systemMenu } from '@/data/sidebar'

const sidebarOpen = ref(false)
const sidebarCollapsed = ref(false)
const mainRef = ref(null)
const mainContentRef = ref(null)
const windowWidth = ref(window.innerWidth)

const router = useRouter()
const route = useRoute()
const { locale, t } = useI18n()
const currentLocale = ref(locale.value)
const authStore = useAuthStore()
const currentUser = computed(() => authStore.user || authStore.currentUser)

// Detect mobile
const isMobile = computed(() => windowWidth.value < 1024)

const handleResize = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

function getPageTitle() {
  const item = [...mainMenu, ...systemMenu].find((i) => i.path === route.path)
  return item && item.titleKey ? t(item.titleKey) : t('sidebar.defaultTitle')
}
function getPageDescription() {
  const item = [...mainMenu, ...systemMenu].find((i) => i.path === route.path)
  return item && item.descriptionKey ? t(item.descriptionKey) : ''
}
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
function changeLanguage() {
  locale.value = currentLocale.value
  localStorage.setItem('locale', currentLocale.value)
}
function goToProfile() {
  router.push('/profile')
}
function goToSettings() {
  router.push('/settings')
}

async function logout() {
  try {
    const result = await authStore.logout?.()
    if (result && !result.success) console.warn('Logout API failed, but clearing local state...')
  } catch (e) {
    console.warn('authStore.logout error (ignored):', e)
  } finally {
    localStorage.clear()
    sessionStorage.clear()
    window.location.href = '/ai-agent/login'
  }
}
</script>

<style scoped>
/* Nếu bạn có vùng scroll trong sidebar, dùng class này cho container bên trong Sidebar */
.sidebar-scroll {
  height: calc(100% - 5rem);
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* Tránh áp CSS toàn cục “.h-screen { overflow: hidden }” vì sẽ ảnh hưởng modal */
</style>
