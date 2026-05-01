<template>
  <div class="chat-wrapper">
    <Chat />
  </div>
</template>

<script setup>
import Chat from '@/pages/Chat.vue'
</script>

<style scoped>
.chat-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

/* Mobile responsive */
@media (max-width: 1023px) {
  .chat-wrapper {
    height: 100%;
    min-height: 0;
    overflow: hidden;
  }
}
</style>

