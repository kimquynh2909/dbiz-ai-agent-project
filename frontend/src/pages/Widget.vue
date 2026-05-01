<template>
  <div class="dbiz-widget-wrapper">
    <!-- Conversation Sidebar -->
    <WidgetConversationSidebar
      :is-open="sidebarOpen"
      :conversations="conversationList"
      :current-conversation-id="currentConversation?.name"
      :loading="isLoadingConversations"
      @close="sidebarOpen = false"
      @new-conversation="createNewConversation"
      @select-conversation="selectConversation"
      @delete-conversation="deleteConversation"
    />

    <div class="flex-1 flex overflow-hidden min-h-0" style="height: 100%; min-height: 0">
      <div class="main-chat-area flex-1 flex flex-col bg-gray-50">
        <!-- Debug/Test Panel (toggle by ?debug=1) -->
        <div v-if="debugMode" class="bg-yellow-50 border-b border-yellow-200 p-3">
          <div class="max-w-5xl mx-auto">
            <div class="flex flex-col md:flex-row gap-3">
              <div class="flex-1 bg-white border border-yellow-200 rounded-lg p-3">
                <div class="text-xs font-semibold text-yellow-700 mb-2">Frappe Login (test)</div>
                <div class="flex items-center gap-2">
                  <input v-model="loginUser" type="text" placeholder="Username" class="input" />
                  <input
                    v-model="loginPass"
                    :type="showPass ? 'text' : 'password'"
                    placeholder="Password"
                    class="input"
                  />
                  <button @click="showPass = !showPass" class="btn">{{ showPass ? 'Hide' : 'Show' }}</button>
                </div>
                <div v-if="loginError" class="text-xs text-red-600 mt-1">{{ loginError }}</div>
                <div v-if="loginInfo" class="text-xs text-green-700 mt-1">{{ loginInfo }}</div>
              </div>
              <div class="flex-1 bg-white border border-yellow-200 rounded-lg p-3">
                <div class="text-xs font-semibold text-yellow-700 mb-2">External Identity (extUser)</div>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
                  <input v-model="extUser" type="text" placeholder="extUser (ID)" class="input" />
                  <input v-model="extName" type="text" placeholder="Name" class="input" />
                  <input v-model="extEmail" type="email" placeholder="Email" class="input" />
                  <input v-model="extOrg" type="text" placeholder="Org" class="input" />
                  <input v-model="extTs" type="text" placeholder="ts (epoch)" class="input" />
                  <input v-model="extSig" type="text" placeholder="sig (hmac hex)" class="input" />
                </div>
                <div class="flex items-center gap-2 mt-2">
                  <input
                    v-model="extSecret"
                    :type="showSecret ? 'text' : 'password'"
                    placeholder="Shared secret (dev only)"
                    class="input"
                  />
                  <button @click="showSecret = !showSecret" class="btn">{{ showSecret ? 'Hide' : 'Show' }}</button>
                  <button @click="genTimestamp" class="btn">Gen ts</button>
                  <button @click="genSignature" class="btn">Sign</button>
                  <button @click="applyExternal" class="btn btn-primary">Apply</button>
                </div>
                <div class="text-[11px] text-gray-500 mt-1">
                  HMAC-SHA256 over "extUser|ts" with server secret (conf dbiz_embed_secret)
                </div>
              </div>
            </div>
          </div>
        </div>

        <WidgetHeader
          :logo-src="chatConfig?.avatar_image || chatbotAvatar"
          :title="chatConfig?.assistant_name || 'Ms.Sunny'"
          :support="chatConfig?.support_info || 'AI Assistant thông minh'"
          @close-widget="closeWidget"
          @open-sidebar="toggleSidebar"
        />

        <div
          ref="messagesContainer"
          class="flex-1 overflow-y-auto px-4 py-3 pb-6 chat-messages min-h-0"
          style="scroll-behavior: smooth"
        >
          <WidgetWelcomeMessage
            v-if="messages.length === 0"
            :welcome-text="
              chatConfig?.greeting_message || `Xin chào! Tôi là ${chatConfig?.assistant_name || 'Ms.Sunny'} 👋`
            "
            :avatar-image="chatConfig?.avatar_image || chatbotAvatar"
            :suggestions="quickQuestions"
            @select-suggestion="sendSuggestion"
          />

          <div v-else class="w-full mx-auto space-y-6">
            <ChatMessages
              :messages="messages"
              :is-thinking="isThinking"
              :avatar-image="chatbotAvatar"
              :format-message="formatMessage"
              :avatar-size="8"
              @feedback="provideFeedback"
            />
          </div>
        </div>

        <ChatInput v-model="inputMessage" :disabled="isInputDisabled" @submit="sendMessage" />
      </div>

      <ImageModal :image="selectedImage" @close="closeImageModal" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import WidgetHeader from '@/components/widget/WidgetHeader.vue'
import WidgetConversationSidebar from '@/components/widget/WidgetConversationSidebar.vue'
import ChatMessages from '@/components/chat/ChatMessages.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import WidgetWelcomeMessage from '@/components/widget/WidgetWelcomeMessage.vue'
import ImageModal from '@/components/modals/ImageModal.vue'
import chatbotAvatar from '@/assets/chatbot.png'
import { useChatFormatter } from '@/composables/useChatFormatter'
import { useChatConfig } from '@/composables/useChatConfig'
import { useScrollHelpers } from '@/composables/useScrollHelpers'
import { checkAndResumeStreaming, cleanupStreamListeners } from '@/utils/streamingResume'

const { t, locale } = useI18n()
const chatStore = useChatStore()
const messagesContainer = ref(null)
const inputMessage = ref('')
const selectedImage = ref(null)
const debugMode = ref(false)
const loginUser = ref('')
const loginPass = ref('')
const showPass = ref(false)
const loginLoading = ref(false)
const loginError = ref('')
const loginInfo = ref('')

// Sidebar state
const sidebarOpen = ref(false)
const isLoadingConversations = ref(false)

// External identity testing fields
const extUser = ref('')
const extName = ref('')
const extEmail = ref('')
const extOrg = ref('')
const extTs = ref('')
const extSig = ref('')
const extSecret = ref('')
const showSecret = ref(false)

const messages = computed(() => chatStore.currentMessages)
const isThinking = computed(() => chatStore.isThinking)
const conversationList = computed(() => chatStore.conversationList)
const currentConversation = computed(() => chatStore.currentConversation)

// Kiểm tra xem có message nào đang streaming không
const hasActiveStreaming = computed(() => {
  return messages.value.some((msg) => msg.streaming === true)
})

// Input disabled khi đang thinking hoặc có message đang streaming
const isInputDisabled = computed(() => isThinking.value || hasActiveStreaming.value)

const { chatConfig, quickQuestions, loadChatbotConfig } = useChatConfig()

const { scrollToBottom, scrollToTop } = useScrollHelpers(messagesContainer)

const { formatMessage, attachInlineImageHandler, detachInlineImageHandler } = useChatFormatter(messages, selectedImage)
const authStore = useAuthStore()

// parent origin allowed to communicate with this iframe (for postMessage)
const allowedParentOrigin = ref('*')

const sendMessage = async () => {
  // Không cho gửi nếu đang thinking hoặc có message đang streaming
  if (!inputMessage.value.trim() || isInputDisabled.value) return
  const message = inputMessage.value
  inputMessage.value = ''
  await chatStore.sendMessage(message)
  scrollToBottom()
}

const sendSuggestion = (suggestion) => {
  // WidgetWelcomeMessage emits the suggestion object, need to extract text
  const text =
    typeof suggestion === 'string'
      ? suggestion
      : suggestion?.question_text || suggestion?.text || suggestion?.title || ''
  if (!text) return
  inputMessage.value = text
  sendMessage()
}

const closeWidget = () => {
  // Send message to parent window to close the widget
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: 'DBIZ_CHAT:CLOSE' }, '*')
    }
  } catch (e) {
    console.warn('Failed to close widget', e)
  }
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
  if (sidebarOpen.value) {
    loadConversations()
  }
}

const loadConversations = async () => {
  isLoadingConversations.value = true
  try {
    await chatStore.loadConversations()
  } catch (error) {
    console.error('Failed to load conversations:', error)
  } finally {
    isLoadingConversations.value = false
  }
}

const createNewConversation = () => {
  chatStore.clearCurrentConversation()
  sidebarOpen.value = false
}

const selectConversation = async (conversationName) => {
  try {
    await chatStore.loadConversation(conversationName)
    sidebarOpen.value = false
    scrollToBottom()

    // Kiểm tra và resume streaming nếu có
    const loadedMessages = chatStore.currentMessages
    if (loadedMessages && loadedMessages.length > 0) {
      await checkAndResumeStreaming(
        loadedMessages,
        // Callback khi nhận chunk mới
        (messageIndex, chunkData) => {
          if (chatStore.currentMessages[messageIndex]) {
            chatStore.currentMessages[messageIndex].content += chunkData.content || ''
            chatStore.currentMessages[messageIndex].streaming = true
          }
        },
        // Callback khi stream hoàn tất
        (messageIndex, completeData) => {
          if (chatStore.currentMessages[messageIndex]) {
            chatStore.currentMessages[messageIndex].content =
              completeData.content || chatStore.currentMessages[messageIndex].content
            chatStore.currentMessages[messageIndex].streaming = false
            chatStore.currentMessages[messageIndex].is_streaming = 0
            chatStore.currentMessages[messageIndex].stream_key = null
          }
        }
      )
    }
  } catch (error) {
    console.error('Failed to load conversation:', error)
  }
}

const deleteConversation = async (conversationName) => {
  if (!confirm('Bạn có chắc chắn muốn xóa cuộc hội thoại này?')) return

  try {
    await chatStore.deleteConversation(conversationName)
    if (currentConversation.value?.name === conversationName) {
      chatStore.clearCurrentConversation()
    }
    await loadConversations()
  } catch (error) {
    console.error('Failed to delete conversation:', error)
  }
}

const closeImageModal = () => {
  selectedImage.value = null
}

const provideFeedback = async (messageId, helpful) => {
  await chatStore.provideFeedback(messageId, helpful)
}

const parseQuery = () => {
  try {
    const params = new URLSearchParams(window.location.search)
    const loc = params.get('locale')
    if (loc) {
      locale.value = loc
      localStorage.setItem('locale', loc)
    }
    const dbg = params.get('debug') || params.get('dev')
    if (dbg === '1' || dbg === 'true') debugMode.value = true
    const extUserParam = params.get('extUser')
    if (extUserParam) {
      chatStore.setExternalIdentity({
        extUser: extUserParam,
        extName: params.get('extName') || undefined,
        extEmail: params.get('extEmail') || undefined,
        extOrg: params.get('extOrg') || undefined,
        ts: params.get('ts') || undefined,
        sig: params.get('sig') || undefined,
      })
      // prefill debug inputs as well
      if (debugMode.value) {
        extUser.value = extUserParam
        extName.value = params.get('extName') || ''
        extEmail.value = params.get('extEmail') || ''
        extOrg.value = params.get('extOrg') || ''
        extTs.value = params.get('ts') || ''
        extSig.value = params.get('sig') || ''
      }
    }

    // Allow only provided parent origin to send messages
    const po = params.get('parent_origin')
    if (po) {
      allowedParentOrigin.value = po
    }
  } catch (e) {
    /* noop */
  }
}

onMounted(async () => {
  parseQuery()
  await loadChatbotConfig()
  attachInlineImageHandler(messagesContainer)

  // Kiểm tra và resume streaming nếu có conversation đang active
  if (currentConversation.value?.name && messages.value.length > 0) {
    await checkAndResumeStreaming(
      messages.value,
      // Callback khi nhận chunk mới
      (messageIndex, chunkData) => {
        if (chatStore.currentMessages[messageIndex]) {
          chatStore.currentMessages[messageIndex].content += chunkData.content || ''
          chatStore.currentMessages[messageIndex].streaming = true
        }
      },
      // Callback khi stream hoàn tất
      (messageIndex, completeData) => {
        if (chatStore.currentMessages[messageIndex]) {
          chatStore.currentMessages[messageIndex].content =
            completeData.content || chatStore.currentMessages[messageIndex].content
          chatStore.currentMessages[messageIndex].streaming = false
          chatStore.currentMessages[messageIndex].is_streaming = 0
          chatStore.currentMessages[messageIndex].stream_key = null
        }
      }
    )
  }

  try {
    window.addEventListener('message', async (event) => {
      try {
        if (
          allowedParentOrigin.value &&
          allowedParentOrigin.value !== '*' &&
          event.origin !== allowedParentOrigin.value
        ) {
          return
        }
        const data = event.data || {}
        if (data && data.type === 'DBIZ_WIDGET_AUTH' && data.action === 'login') {
          const { username, password } = data.payload || {}
          if (username && password && !authStore.isAuthenticated) {
            loginError.value = ''
            const res = await authStore.login(username, password)
            if (res?.success) {
              loginInfo.value = 'Logged in'
            } else {
              loginError.value = res?.error || 'Login failed'
            }
          }
        }
      } catch (e) {}
    })
  } catch (e) {}
})

onBeforeUnmount(() => {
  detachInlineImageHandler()
  cleanupStreamListeners()
})

const genTimestamp = () => {
  extTs.value = String(Math.floor(Date.now() / 1000))
}

const genSignature = async () => {
  if (!extUser.value || !extTs.value || !extSecret.value) return
  try {
    // Browser HMAC-SHA256 via SubtleCrypto
    const enc = new TextEncoder()
    const key = await window.crypto.subtle.importKey(
      'raw',
      enc.encode(extSecret.value),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    )
    const data = enc.encode(`${extUser.value}|${extTs.value}`)
    const sigBuf = await window.crypto.subtle.sign('HMAC', key, data)
    const hex = Array.from(new Uint8Array(sigBuf))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('')
    extSig.value = hex
  } catch (e) {
    console.error('Sign error', e)
  }
}

const applyExternal = () => {
  if (!extUser.value) return
  chatStore.setExternalIdentity({
    extUser: extUser.value,
    extName: extName.value || undefined,
    extEmail: extEmail.value || undefined,
    extOrg: extOrg.value || undefined,
    ts: extTs.value || undefined,
    sig: extSig.value || undefined,
  })
  loginInfo.value = 'External identity applied'
}
</script>

<style scoped>
.input {
  @apply w-full border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500;
}
.btn {
  @apply px-3 py-1.5 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50;
}
.btn-primary {
  @apply bg-blue-600 text-white border-blue-600 hover:bg-blue-700;
}
.dbiz-widget-wrapper {
  height: 100vh;
  width: 100%;
  background: #fff;
  display: flex;
  flex-direction: column;
}
.chat-messages {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  overflow-y: auto;
  min-height: 0;
  padding-bottom: calc(var(--input-height, 72px) + env(safe-area-inset-bottom));
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
  height: 100%;
  min-height: 0;
  overflow: hidden;
}
</style>
