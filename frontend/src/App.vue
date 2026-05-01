<template>
  <div id="app">
    <Notification />
    <!-- Layout wrapper -->
    <component :is="currentLayout">
      <router-view />
    </component>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import Notification from '@/components/common/Notification.vue'

const route = useRoute()

// Determine layout based on route meta
const currentLayout = computed(() => {
  const layout = route.meta?.layout

  if (layout === 'AppLayout') {
    return AppLayout
  }

  // Default layout (no layout wrapper)
  return 'div'
})
</script>

<style>
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
