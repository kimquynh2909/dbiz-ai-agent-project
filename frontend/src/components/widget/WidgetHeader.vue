<template>
  <div class="widget-header" style="height: var(--chat-subheader-h, 64px); min-height: 64px; display:flex; align-items:center; gap:12px; padding:0 12px; background-color: white; box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);">
    <div class="header-left" style="display:flex; align-items:center; gap:12px;">
      <img v-if="logoSrc" :src="logoSrc" alt="logo" class="logo" />
      <div class="header-info">
        <div class="title">{{ title }}</div>
        <div v-if="support" class="support">{{ support }}</div>
      </div>
    </div>

    <div style="flex:1"></div>

    <div class="header-actions" style="display:flex; align-items:center; gap:8px;">
      <!-- Hamburger first, close button last (close sits on far right) -->
      <button class="icon-button" type="button" aria-label="Mở menu" title="Mở menu" @click="$emit('open-sidebar')">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>

      <button class="icon-button" type="button" aria-label="Thu nhỏ chat" title="Thu nhỏ chat" @click="$emit('close-widget')">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  logoSrc: { type: String, default: '' },
  title: { type: String, default: '' },
  support: { type: String, default: '' }
})

defineEmits(['open-sidebar', 'close-widget'])
</script>

<style scoped>
.logo { width: 44px; height: 44px; border-radius: 8px; object-fit: cover; }
.title { font-weight: 600; color: #111827; }
.support { font-size: 12px; color: #6b7280; }
.icon-button { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 9999px; border: none; background: transparent; color: #475569; cursor: pointer; }
.icon-button:hover { background-color: #f1f5f9; color: #1f2937; }
.icon-button:focus-visible { outline: 2px solid #2563eb; outline-offset: 2px; }
</style>
