<template>
  <div
    class="chat-page-wrapper"
    style="--chat-subheader-h: 80px; --chat-input-h: calc(72px + env(safe-area-inset-bottom))"
  >
    <ChatSidebar
      :class="[
        'shrink-0 transition-all duration-200',
        'hidden lg:block', // Ẩn trên mobile, hiển thị trên desktop
        sidebarCollapsed ? 'w-20 bg-white border-r border-blue-100 shadow-sm' : 'w-80',
      ]"
      :conversations="conversations"
      :current-conversation-id="currentConversation?.id"
      :sidebar-visible="sidebarVisible"
      :collapsed="sidebarCollapsed"
      @new-chat="startNewChat"
      @select-conversation="selectConversation"
      @clear-history="clearHistory"
      @close-sidebar="sidebarVisible = false"
      @update:collapsed="sidebarCollapsed = $event"
      @search-chats="openSearchDialog"
      @delete-conversation="confirmDeleteConversationById"
    />

    <!-- Cột chat chính: flex-col + min-h-0 để con được phép co và scroll -->
    <!-- Trên mobile: full width, trên desktop: flex-1 -->
    <div class="main-chat-area w-full lg:flex-1 bg-gray-50 flex flex-col overflow-hidden min-h-0">
      <ChatHeader
        :assistant-name="chatConfig?.assistant_name || 'Ms.Sunny'"
        :support-info="chatConfig?.support_info || 'AI Assistant thông minh'"
        :avatar-image="chatConfig?.avatar_image || chatbotAvatar"
        :allow-delete="!!currentConversation?.id"
        @toggle-sidebar="sidebarVisible = !sidebarVisible"
        @delete-conversation="confirmDeleteCurrent"
      />

      <!-- Vùng scroll DUY NHẤT: flex-1 + min-h-0 + overflow-y-auto, bỏ padding-bottom để tránh đệm kép -->
      <div
        ref="messagesContainer"
        class="flex-1 min-h-0 overflow-y-auto px-3 sm:px-6 py-4 chat-messages"
        style="scroll-behavior: smooth"
      >
        <WelcomeMessage
          v-if="messages.length === 0"
          :greeting-message="
            chatConfig?.greeting_message || `Xin chào! Tôi là ${chatConfig?.assistant_name || 'Ms.Sunny'} 👋`
          "
          :description="
            chatConfig?.description || 'Tôi là AI Assistant thông minh của bạn. Hãy hỏi tôi bất cứ điều gì!'
          "
          :avatar-image="chatConfig?.avatar_image || chatbotAvatar"
          :quick-questions="quickQuestions"
          @select-question="sendSuggestion"
        />

        <!-- Note: nếu muốn full-width, đổi max-w-5xl -> w-full -->
        <div v-else class="full-width space-y-8">
          <ChatMessages
            :messages="messages"
            :is-thinking="isThinking"
            :avatar-image="chatbotAvatar"
            :format-message="formatMessage"
            @feedback="provideFeedback"
          />
        </div>
      </div>

      <div class="shrink-0">
        <ChatInput v-model="inputMessage" :disabled="isInputDisabled" @submit="sendMessage" />
      </div>
    </div>

    <ImageModal :image="selectedImage" @close="closeImageModal" />

    <ConfirmModal
      :visible="showConfirmModal"
      :message="confirmModalMessage"
      @confirm="acceptConfirm"
      @cancel="closeConfirmModal"
    />

    <ChatSearchDialog
      :visible="showSearchDialog"
      :conversations="conversations"
      @close="showSearchDialog = false"
      @select="handleSearchSelect"
      @new-chat="handleSearchNewChat"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useChatStore } from '@/stores/chat'
import { deleteConversation } from '@/services/chatService'
import { deleteAllConversations } from '@/services/chatService'
import { loadConversations as fetchConversations } from '@/services/chatService'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatHeader from '@/components/chat/ChatHeader.vue'
import ChatMessages from '@/components/chat/ChatMessages.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import WelcomeMessage from '@/components/common/WelcomeMessage.vue'
import ImageModal from '@/components/modals/ImageModal.vue'
import ConfirmModal from '@/components/modals/ConfirmModal.vue'
import ChatSearchDialog from '@/components/chat/ChatSearchDialog.vue'
import chatbotAvatar from '@/assets/chatbot.png'
import { useChatFormatter } from '@/composables/useChatFormatter'
import { useChatConfig } from '@/composables/useChatConfig'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useScrollHelpers } from '@/composables/useScrollHelpers'
import { useAuthStore } from '@/stores/auth'
import { checkAndResumeStreaming, cleanupStreamListeners } from '@/utils/streamingResume'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const { t } = useI18n()
const chatStore = useChatStore()
const chatConfigs = useChatConfig()
const messagesContainer = ref(null)
const sidebarVisible = ref(false)
const sidebarCollapsed = ref(false)
const inputMessage = ref('')
const selectedImage = ref(null)
const showSearchDialog = ref(false)
const authStore = useAuthStore()

const conversations = ref([])
const currentConversation = computed(() => chatStore.currentConversation)
const messages = computed(() => chatStore.currentMessages)
const isThinking = computed(() => chatStore.isThinking)
const chatConfig = computed(() => chatConfigs.chatConfig.value)
const quickQuestions = computed(() => chatConfigs.quickQuestions.value || [])

// Kiểm tra xem có message nào đang streaming không
const hasActiveStreaming = computed(() => {
  return messages.value.some((msg) => msg.streaming === true)
})

// Input disabled khi đang thinking hoặc có message đang streaming
const isInputDisabled = computed(() => isThinking.value || hasActiveStreaming.value)

// Streaming resume states
const activeStreams = ref([])
const streamingMessageIndexes = ref(new Set())

const {
  visible: showConfirmModal,
  message: confirmModalMessage,
  open: openConfirmModal,
  close: closeConfirmModal,
  accept: acceptConfirm,
} = useConfirmDialog()

const { scrollToBottom, scrollToTop } = useScrollHelpers(messagesContainer)
const { formatMessage, attachInlineImageHandler, detachInlineImageHandler } = useChatFormatter(messages, selectedImage)

const startNewChat = async () => {
  try {
    if (!chatConfig.value) {
      await chatConfigs.loadChatbotConfig()
    }
  } catch (err) {
    console.error('Error loading chatbot config before starting new chat:', err)
  }

  chatStore.clearCurrentConversation()
  inputMessage.value = ''
  scrollToTop()
}

const selectConversation = async (conversationId) => {
  // Cleanup old streams trước khi load conversation mới
  if (activeStreams.value.length > 0) {
    await cleanupStreamListeners(activeStreams.value, {
      conversation_name: currentConversation.value?.name || currentConversation.value?.id,
    })
    activeStreams.value = []
    streamingMessageIndexes.value.clear()
  }

  await chatStore.loadConversation(conversationId)

  // Check và resume streaming nếu có message đang stream
  const loadedMessages = chatStore.currentMessages
  console.log(
    '📋 Loaded messages:',
    loadedMessages.map((m) => ({
      role: m.role,
      is_streaming: m.is_streaming,
      stream_key: m.stream_key,
      content_length: m.content?.length,
    }))
  )

  if (loadedMessages && loadedMessages.length > 0) {
    const streamKeys = await checkAndResumeStreaming(
      loadedMessages,
      // Callback khi nhận chunk mới
      (messageIndex, chunkData) => {
        if (chatStore.currentMessages[messageIndex]) {
          // Append chunk vào content
          chatStore.currentMessages[messageIndex].content += chunkData.content || ''
          streamingMessageIndexes.value.add(messageIndex)
          // Auto scroll
          nextTick(() => scrollToBottom())
        }
      },
      // Callback khi stream hoàn tất
      (messageIndex, completeData) => {
        if (chatStore.currentMessages[messageIndex]) {
          chatStore.currentMessages[messageIndex].content = completeData.content || ''
          chatStore.currentMessages[messageIndex].is_streaming = 0
          chatStore.currentMessages[messageIndex].stream_key = null
          streamingMessageIndexes.value.delete(messageIndex)

          // Tắt thinking nếu không còn stream nào
          if (streamingMessageIndexes.value.size === 0) {
            chatStore.thinking = false
            console.log('All streams completed, hiding thinking indicator')
          }
        }
      }
    )

    activeStreams.value = streamKeys

    // KHÔNG set thinking = true khi resume streaming
    // Vì message thật đã có trong list với is_streaming=1 rồi
    // Nếu set thinking=true sẽ tạo thêm message ảo duplicate
    if (streamKeys.length > 0) {
      console.log('Active streams detected, resuming without thinking indicator')
    }
  }

  setTimeout(() => {
    scrollToBottom()
  }, 100)
}

const sendMessage = async () => {
  // Không cho gửi nếu đang thinking hoặc có message đang streaming
  if (!inputMessage.value.trim() || isInputDisabled.value) return
  const message = inputMessage.value
  inputMessage.value = ''
  await chatStore.sendMessage(message, authStore.currentUser)
  scrollToBottom()
}

const sendSuggestion = (suggestion) => {
  inputMessage.value = suggestion
  sendMessage()
}

const openSearchDialog = () => {
  showSearchDialog.value = true
}

const handleSearchSelect = async (conversationId) => {
  showSearchDialog.value = false
  await selectConversation(conversationId)
}

const handleSearchNewChat = () => {
  showSearchDialog.value = false
  startNewChat()
}

const clearHistory = async () => {
  openConfirmModal({
    message: t('chat.confirmClearHistory'),
    onConfirm: async () => {
      try {
        await deleteAllConversations()
        const result = await fetchConversations()
        conversations.value = result
      } catch (err) {
        console.error('❌ Failed to delete all conversations:', err)
      }
    },
  })
}

const confirmDeleteConversationById = (conversationId) => {
  if (!conversationId) return
  const conversation = conversations.value.find((item) => item.name === conversationId || item.id === conversationId)
  const title = conversation?.title || conversation?.name || conversationId

  openConfirmModal({
    message: t('chat.confirmDeleteConversation', { title }),
    onConfirm: async () => {
      try {
        await deleteConversation(conversationId)
        const result = await fetchConversations()
        conversations.value = result

        const currentId = currentConversation.value?.id || currentConversation.value?.name
        if (currentId === conversationId) {
          chatStore.clearCurrentConversation()
        }
      } catch (err) {
        console.error('Delete conversation error:', err)
        notificationStore.notify(t('chat.error') || 'Xóa cuộc hội thoại thất bại', 'error')
      }
    },
  })
}

const confirmDeleteCurrent = () => {
  if (!currentConversation.value || !currentConversation.value.id) return
  confirmDeleteConversationById(currentConversation.value.id)
}

const closeImageModal = () => {
  selectedImage.value = null
}

const provideFeedback = async (messageId, helpful) => {
  await chatStore.provideFeedback(messageId, helpful)
}

// Hàm reload conversations
const reloadConversations = async () => {
  const result = await fetchConversations()
  conversations.value = result
}

// Subscribe to conversation title updates
let unsubscribeTitleUpdate = null

onMounted(async () => {
  await chatConfigs.loadChatbotConfig()
  console.log('Chat config loaded on mount:', chatConfig.value)
  await reloadConversations()
  if (messages.value.length === 0) {
    scrollToTop()
  }
  attachInlineImageHandler(messagesContainer)

  // Lắng nghe sự kiện cập nhật title từ Socket.IO
  try {
    const { subscribeToGenericEvent } = await import('@/utils/socket')
    unsubscribeTitleUpdate = await subscribeToGenericEvent('conversation_title_updated', async (data) => {
      if (data?.event === 'conversation_title_updated') {
        console.log('Conversation title updated, reloading sidebar...')
        await reloadConversations()
      }
    })
  } catch (e) {
    console.warn('Could not subscribe to title updates:', e)
  }
})

onBeforeUnmount(async () => {
  detachInlineImageHandler(messagesContainer)
  if (unsubscribeTitleUpdate) {
    unsubscribeTitleUpdate()
  }

  // Cleanup all active stream listeners
  if (activeStreams.value.length > 0) {
    await cleanupStreamListeners(activeStreams.value, {
      conversation_name: currentConversation.value?.name || currentConversation.value?.id,
    })
  }
})
</script>

<style scoped>
.chat-page-wrapper {
  display: flex;
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
}

/* Mobile responsive */
@media (max-width: 1023px) {
  .chat-page-wrapper {
    flex-direction: column;
  }
  
  .main-chat-area {
    width: 100%;
    flex: 1;
  }
}

.chat-messages {
  /* Scroll mượt + không làm dãn parent */
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  /* BỎ đệm đáy để tránh double padding với ChatInput */
  padding-bottom: 0;
}

/* Chống nở nội dung gây dãn */
.chat-messages img {
  max-width: 100%;
  height: auto;
}
.chat-messages pre {
  max-width: 100%;
  overflow: auto;
}
.chat-messages p,
.chat-messages code {
  overflow-wrap: anywhere;
  word-break: break-word;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}
.chat-messages::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}
.chat-messages::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.main-chat-area {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0; /* quan trọng với flex child */
  overflow: hidden;
}
</style>
