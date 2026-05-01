<template>
  <div
    :class="[
      'bg-gradient-to-b from-gray-900 via-gray-900 to-black shadow-2xl transform transition-all duration-300',
      'flex flex-col min-h-0',
      sidebarCollapsed ? 'w-20' : 'w-72',
      'fixed inset-y-0 left-0 z-50',
      { '-translate-x-full': !sidebarOpen, 'translate-x-0': sidebarOpen },
      'lg:static lg:inset-auto lg:z-auto lg:transform-none lg:h-full'
    ]"
    style="height: 100%;"
  >
    <!-- Header/logo -->
    <div class="flex items-center h-20 px-6 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 border-b border-blue-400/30 relative shrink-0">
      <div class="flex items-center justify-center flex-1">
        <img
          :src="sidebarCollapsed ? logo.minilogo : logo.logo"
          alt="DBIZ Autonomous Logo"
          :class="[
            'object-contain filter brightness-0 invert transition-all duration-300',
            sidebarCollapsed ? 'w-10 h-10' : 'w-40 h-12'
          ]"
        />
      </div>

      <!-- Collapse (desktop) -->
      <button
        @click="$emit('toggle-collapse')"
        class="absolute right-10 text-white hover:text-cyan-300 p-1 rounded-lg hover:bg-white/10 transition-colors hidden lg:inline-flex"
        title="Toggle collapse"
      >
        <component :is="sidebarCollapsed ? ChevronRight : ChevronLeft" class="w-5 h-5" />
      </button>

      <!-- Close (mobile) -->
      <button
        @click="$emit('update:sidebarOpen', false)"
        class="lg:hidden absolute right-4 text-white hover:text-cyan-300"
        title="Close"
      >
        <X class="w-6 h-6" />
      </button>
    </div>

    <!-- Nội dung cuộn DUY NHẤT -->
    <nav class="flex-1 min-h-0 overflow-y-auto px-4 py-6 space-y-2 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-800">
      <div v-if="!sidebarCollapsed" class="mb-6">
        <h3 class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ $t('sidebar.mainMenu') }}</h3>
      </div>

      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200"
        :class="isActive(item.path)
          ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-500/30'
          : 'text-gray-300 hover:bg-gray-800/50 hover:text-white'"
      >
        <component
          :is="item.icon"
          class="w-5 h-5 transition-colors flex-shrink-0"
          :class="[
            isActive(item.path) ? 'text-white' : 'text-gray-400 group-hover:text-cyan-400',
            sidebarCollapsed ? 'mr-0' : 'mr-4'
          ]"
        />
        <span v-if="!sidebarCollapsed" class="flex-1">{{ $t(item.label) }}</span>
        <span
          v-if="item.badge && !sidebarCollapsed"
          class="ml-2 px-2 py-1 text-xs rounded-full"
          :class="isActive(item.path) ? 'bg-white/20 text-white' : 'bg-gray-700 text-gray-300'"
        >
          {{ item.badge }}
        </span>
        <ChevronRight v-if="isActive(item.path) && !sidebarCollapsed" class="w-4 h-4 text-white ml-2" />
      </router-link>

      <div v-if="!sidebarCollapsed" class="my-6 border-t border-gray-700/50"></div>

      <div v-if="!sidebarCollapsed" class="mb-4">
        <h3 class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ $t('sidebar.system') }}</h3>
      </div>

      <router-link
        v-for="item in systemMenuItems"
        :key="item.path"
        :to="item.path"
        class="group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200"
        :class="isActive(item.path)
          ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-500/30'
          : 'text-gray-300 hover:bg-gray-800/50 hover:text-white'"
      >
        <component
          :is="item.icon"
          class="w-5 h-5 transition-colors flex-shrink-0"
          :class="[
            isActive(item.path) ? 'text-white' : 'text-gray-400 group-hover:text-cyan-400',
            sidebarCollapsed ? 'mr-0' : 'mr-4'
          ]"
        />
        <span v-if="!sidebarCollapsed" class="flex-1">{{ $t(item.label) }}</span>
        <ChevronRight v-if="isActive(item.path) && !sidebarCollapsed" class="w-4 h-4 text-white ml-2" />
      </router-link>

      <div class="h-3" style="padding-bottom: env(safe-area-inset-bottom)"></div>
    </nav>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { mainMenu, systemMenu } from '@/data/sidebar'
import { ChevronRight, ChevronLeft, X } from 'lucide-vue-next'

const props = defineProps({
  sidebarCollapsed: { type: Boolean, required: true },
  sidebarOpen: { type: Boolean, required: true },
  currentUser: { type: Object, required: true },
  logo: { type: Object, required: true },
})
const emit = defineEmits(['toggle-collapse', 'update:sidebarOpen', 'logout'])

const route = useRoute()
function isActive(path) { return route.path === path }

const menuItems = mainMenu.map(item => ({
  path: item.path,
  label: item.label,
  icon: item.icon,
  title: item.title,
  description: item.description
}))
const systemMenuItems = systemMenu.map(item => ({
  path: item.path,
  label: item.label,
  icon: item.icon,
  title: item.title,
  description: item.description
}))
</script>

<style scoped>
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #111827; }
::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4b5563; }
</style>