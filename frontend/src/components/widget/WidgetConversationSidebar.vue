<template>
  <transition name="slide">
    <div v-if="isOpen" class="widget-sidebar-overlay" @click="emit('close')">
      <div class="widget-sidebar" @click.stop>
        <!-- Header -->
        <div class="sidebar-header">
          <h3 class="sidebar-title">Lịch sử hội thoại</h3>
          <button @click="emit('close')" class="close-btn" title="Đóng">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- New Conversation Button -->
        <div class="sidebar-actions">
          <button @click="emit('new-conversation')" class="new-conversation-btn">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            <span>Cuộc hội thoại mới</span>
          </button>
        </div>

        <!-- Conversations List -->
        <div class="sidebar-content">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p class="text-sm text-gray-500">Đang tải...</p>
          </div>
          
          <div v-else-if="conversations.length === 0" class="empty-state">
            <svg class="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            <p class="text-sm text-gray-500">Chưa có cuộc hội thoại nào</p>
          </div>

          <div v-else class="conversations-list">
            <div
              v-for="conversation in conversations"
              :key="conversation.name"
              :class="['conversation-item', { active: conversation.name === currentConversationId }]"
              @click="emit('select-conversation', conversation.name)"
            >
              <div class="conversation-icon">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                </svg>
              </div>
              <div class="conversation-info">
                <div class="conversation-title">{{ conversation.title || 'Cuộc hội thoại' }}</div>
                <div class="conversation-date">{{ formatDate(conversation.creation) }}</div>
              </div>
              <button 
                v-if="conversation.name === currentConversationId"
                @click.stop="emit('delete-conversation', conversation.name)"
                class="delete-btn"
                title="Xóa cuộc hội thoại"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  conversations: {
    type: Array,
    default: () => []
  },
  currentConversationId: {
    type: String,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'new-conversation', 'select-conversation', 'delete-conversation'])

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Vừa xong'
  if (diffMins < 60) return `${diffMins} phút trước`
  if (diffHours < 24) return `${diffHours} giờ trước`
  if (diffDays < 7) return `${diffDays} ngày trước`
  
  return date.toLocaleDateString('vi-VN', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric' 
  })
}
</script>

<style scoped>
.widget-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: flex;
  justify-content: flex-start;
  pointer-events: auto;
}

.widget-sidebar {
  width: 280px;
  height: 100%;
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  pointer-events: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  padding: 6px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.sidebar-actions {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.new-conversation-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #2563eb;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.new-conversation-btn:hover {
  background: #eff6ff;
  border-color: #2563eb;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.conversations-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.conversation-item:hover {
  background: #f9fafb;
  border-color: #e5e7eb;
}

.conversation-item.active {
  background: #eff6ff;
  border-color: #2563eb;
}

.conversation-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 6px;
  color: #6b7280;
}

.conversation-item.active .conversation-icon {
  background: #dbeafe;
  color: #2563eb;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-date {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.delete-btn {
  flex-shrink: 0;
  padding: 6px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #ef4444;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
}

.conversation-item:hover .delete-btn,
.conversation-item.active .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #fee2e2;
}

/* Transition animations */
.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
}

.slide-enter-active .widget-sidebar,
.slide-leave-active .widget-sidebar {
  transition: transform 0.3s ease;
}

.slide-enter-from .widget-sidebar,
.slide-leave-to .widget-sidebar {
  transform: translateX(-100%);
}

/* Scrollbar */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
