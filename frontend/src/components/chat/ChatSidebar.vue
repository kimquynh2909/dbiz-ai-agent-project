<!-- src/components/chat/ChatSidebar.vue -->
<template>
  <div class="h-full relative group">
    <!-- Mobile overlay -->
    <div v-if="sidebarVisible" class="fixed inset-0 z-40 lg:hidden">
      <div class="absolute inset-0 bg-black/30" @click="emit('closeSidebar')" />

      <!-- Drawer panel (mobile) -->
      <div class="absolute left-0 top-0 bottom-0 w-72 bg-white shadow-xl flex flex-col min-h-0 overflow-hidden">
        <!-- Header / New Chat -->
        <div class="px-4 border-b shrink-0 flex items-center" style="height: var(--chat-subheader-h)">
          <div class="flex w-full gap-2">
            <button
              @click="emit('newChat')"
              class="flex-1 flex items-center justify-center gap-2 bg-sky-100 text-sky-600 px-4 py-2 rounded-lg hover:bg-sky-200 transition-colors"
            >
              <MessageSquarePlusIcon class="w-5 h-5 text-sky-600" />
              <span>{{ $t('chat.newChat') }}</span>
            </button>
            <button
              @click="emit('searchChats')"
              class="p-2 h-10 w-10 flex items-center justify-center rounded-lg border border-sky-200 text-sky-600 hover:bg-sky-50 transition-colors"
            >
              <SearchIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- List (scroll duy nhất) -->
        <div class="flex-1 min-h-0 overflow-y-auto overscroll-contain p-2">
          <div class="flex items-center justify-between gap-2 px-1">
            <h3 class="text-xs font-semibold uppercase tracking-wide text-sky-600">
              {{ $t('chat.conversationListTitle') }}
            </h3>
            <button
              v-if="allowHistoryActions && conversations.length"
              @click="emit('clearHistory')"
              class="text-xs font-medium text-sky-600 hover:text-sky-700 transition-colors"
            >
              {{ $t('chat.clearAll') }}
            </button>
          </div>

          <div class="mt-2 space-y-1">
            <div v-for="conv in conversations" :key="conv.name" class="relative">
              <button
                @click="emit('selectConversation', conv.name)"
                :class="[
                  'peer w-full text-left p-3 rounded-lg transition-colors',
                  currentConversationId === conv.name ? 'bg-sky-50 border-l-4 border-sky-600' : 'hover:bg-sky-50',
                ]"
              >
                <div class="flex items-start gap-3 pr-10">
                  <MessageSquareIcon class="w-5 h-5 text-sky-600 flex-shrink-0 mt-0.5" />
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-gray-900 truncate">{{ conv.title }}</p>
                    <p class="text-xs text-gray-500 mt-1">{{ formatDate(conv.last_message_date) }}</p>
                  </div>
                </div>
              </button>
              <button
                class="hidden peer-hover:flex peer-focus:flex items-center justify-center absolute top-1/2 right-2 -translate-y-1/2 w-8 h-8 rounded-full text-red-500 hover:text-red-600 hover:bg-red-50 transition"
                @click.stop="emit('deleteConversation', conv.name)"
                :title="$t('chat.deleteConversation')"
              >
                <TrashIcon class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div class="h-3" style="padding-bottom: env(safe-area-inset-bottom)"></div>
        </div>
      </div>
    </div>

    <!-- Desktop sidebar cho Chat -->
    <aside
      class="hidden lg:flex sticky left-0 h-full bg-white border-r border-gray-200 flex-col min-h-0 overflow-hidden transition-all duration-200 ease-in-out"
      :class="collapsed ? 'w-20' : 'w-80'"
      :style="asideStyle"
    >
      <!-- Header / New Chat -->
      <div
        :class="[
          'shrink-0 flex transition-all',
          collapsed
            ? 'px-2 flex-col items-center gap-3 py-2 h-auto'
            : 'px-4 border-b border-sky-50 items-center justify-center h-[var(--chat-subheader-h)]',
        ]"
      >
        <template v-if="collapsed">
          <button
            @click="emit('newChat')"
            class="mt-3 w-10 h-10 flex items-center justify-center rounded-full text-sky-600 hover:text-sky-700 transition-colors"
            title="Đoạn chat mới"
          >
            <MessageSquarePlusIcon class="w-6 h-6" />
          </button>
          <button
            @click="emit('searchChats')"
            class="w-10 h-10 flex items-center justify-center rounded-full text-sky-600 hover:text-sky-700 transition-colors"
            title="Tìm kiếm đoạn chat"
          >
            <SearchIcon class="w-6 h-6" />
          </button>
        </template>
        <div v-else class="flex w-full gap-2">
          <button
            @click="emit('newChat')"
            class="flex-1 flex items-center justify-center gap-2 bg-sky-100 text-sky-600 px-4 py-2 rounded-lg hover:bg-sky-200 transition-colors"
          >
            <MessageSquarePlusIcon class="w-5 h-5 text-sky-600" />
            <span>{{ $t('chat.newChat') }}</span>
          </button>
          <button
            @click="emit('searchChats')"
            class="p-2 h-10 w-10 flex items-center justify-center rounded-lg border border-sky-200 text-sky-600 hover:bg-sky-50 transition-colors"
            title="Tìm kiếm đoạn chat"
          >
            <SearchIcon class="w-4 h-4" />
          </button>
        </div>
      </div>

      <template v-if="!collapsed">
        <!-- List (scroll duy nhất) -->
        <div class="flex-1 min-h-0 overflow-y-auto overscroll-contain">
          <div class="p-2">
            <div class="flex items-center justify-between gap-2 px-1">
              <h3 class="text-xs font-semibold uppercase tracking-wide text-sky-600">
                {{ $t('chat.conversationListTitle') }}
              </h3>
              <button
                v-if="allowHistoryActions && conversations.length"
                @click="emit('clearHistory')"
                class="text-xs font-medium text-sky-600 hover:text-sky-700 transition-colors"
              >
                {{ $t('chat.clearAll') }}
              </button>
            </div>

            <div v-if="conversations.length === 0" class="mt-6 text-center text-gray-500">
              <MessageSquareIcon class="w-12 h-12 mx-auto text-gray-300" />
              <p class="mt-2">{{ $t('chat.history') }}</p>
            </div>

            <div v-else class="mt-2 space-y-1">
              <div v-for="conv in conversations" :key="conv.name" class="relative">
                <button
                  @click="emit('selectConversation', conv.name)"
                  :class="[
                    'peer w-full text-left p-3 rounded-lg transition-colors',
                    currentConversationId === conv.name ? 'bg-sky-50 border-l-4 border-sky-600' : 'hover:bg-sky-50',
                  ]"
                >
                  <div class="flex items-start gap-3 pr-10">
                    <MessageSquareIcon class="w-5 h-5 flex-shrink-0 mt-0.5 text-sky-600" />
                    <div class="min-w-0">
                      <p class="text-sm font-semibold text-gray-900 truncate">{{ conv.title }}</p>
                      <p class="text-xs text-gray-500 mt-1">{{ formatDate(conv.last_message_date) }}</p>
                    </div>
                  </div>
                </button>
                <button
                  class="hidden peer-hover:flex peer-focus:flex items-center justify-center absolute top-1/2 right-2 -translate-y-1/2 w-8 h-8 rounded-full text-red-500 hover:text-red-600 hover:bg-red-50 transition"
                  @click.stop="emit('deleteConversation', conv.name)"
                  :title="$t('chat.deleteConversation')"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div class="h-3" style="padding-bottom: env(safe-area-inset-bottom)"></div>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="flex-1 bg-white"></div>
      </template>
    </aside>
    <button
      class="hidden lg:flex items-center justify-center absolute top-1/2 -right-3 transform -translate-y-1/2 w-6 h-6 rounded-full bg-white border border-sky-200 text-sky-600 shadow-sm opacity-0 group-hover:opacity-100 transition"
      @click="emit('update:collapsed', !collapsed)"
      :title="collapsed ? 'Mở rộng' : 'Thu gọn'"
    >
      <component :is="collapsed ? ChevronRightIcon : ChevronLeftIcon" class="w-3 h-3" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  MessageSquarePlus as MessageSquarePlusIcon,
  MessageSquare as MessageSquareIcon,
  Trash as TrashIcon,
  Search as SearchIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

const props = defineProps({
  conversations: { type: Array, required: true },
  currentConversationId: { type: String, default: null },
  sidebarVisible: { type: Boolean, default: false },
  allowHistoryActions: { type: Boolean, default: true },
  collapsed: { type: Boolean, default: false },
})

const emit = defineEmits([
  'newChat',
  'selectConversation',
  'deleteConversation',
  'clearHistory',
  'closeSidebar',
  'searchChats',
  'update:collapsed',
])

const asideStyle = computed(() => ({
  top: 'var(--header-h, 0px)',
  height: 'calc(100dvh - var(--header-h, 0px))',
}))

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return t('chat.timeAgo.today')
  if (days === 1) return t('chat.timeAgo.yesterday')
  if (days < 7) return `${days} ${t('chat.timeAgo.daysAgo')}`
  return d.toLocaleDateString('vi-VN')
}
</script>

<style scoped>
/* Scrollbar gọn gàng (tùy chọn) */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: #f3f4f6;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
