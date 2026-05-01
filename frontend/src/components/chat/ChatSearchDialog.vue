<template>
  <transition name="fade">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-start justify-center bg-black/40 backdrop-blur-sm p-4" @click.self="close">
      <div class="w-full max-w-xl mt-16 bg-white border border-blue-100 rounded-3xl shadow-2xl overflow-hidden">
        <div class="flex items-center gap-3 px-6 py-4 border-b border-blue-50">
          <div class="p-2 rounded-full bg-blue-50 text-blue-600">
            <SearchIcon class="w-4 h-4" />
          </div>
          <input
            ref="searchInput"
            v-model="keyword"
            type="text"
            class="flex-1 border-none bg-transparent focus:outline-none text-gray-800 placeholder:text-gray-400 text-base"
            placeholder="Tìm kiếm đoạn chat..."
          />
          <button @click="close" class="p-2 text-gray-400 hover:text-blue-500 transition">
            <XIcon class="w-5 h-5" />
          </button>
        </div>

        <div class="max-h-[60vh] overflow-y-auto">
          <div class="px-6 py-4 border-b border-blue-50">
            <button
              @click="selectNewChat"
              class="w-full flex items-center gap-3 px-3 py-2 rounded-xl border border-blue-100 text-blue-600 hover:bg-blue-50 transition-colors"
            >
              <MessageSquarePlusIcon class="w-5 h-5" />
              <span class="font-semibold">Đoạn chat mới</span>
            </button>
          </div>

          <div v-if="groupedResults.length === 0" class="px-6 py-12 text-center text-sm text-gray-500">
            Không tìm thấy đoạn chat phù hợp.
          </div>

          <div v-else class="divide-y divide-blue-50">
            <div v-for="section in groupedResults" :key="section.label" class="px-6 py-4 space-y-3">
              <p class="text-xs uppercase tracking-wide text-blue-400 font-semibold">{{ section.label }}</p>
              <div class="space-y-2">
                <button
                  v-for="conv in section.items"
                  :key="conv.name"
                  @click="selectConversation(conv.name)"
                  class="w-full flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-blue-50 transition-colors text-left"
                >
                  <MessageSquareIcon class="w-4 h-4 text-blue-400 flex-shrink-0" />
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-800 truncate">{{ conv.title || 'Không có tiêu đề' }}</p>
                    <p class="text-xs text-gray-400">{{ formatLabel(conv.last_message_date) }}</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { MessageSquare as MessageSquareIcon, MessageSquarePlus as MessageSquarePlusIcon, Search as SearchIcon, X as XIcon } from 'lucide-vue-next'

const props = defineProps({
  visible: { type: Boolean, default: false },
  conversations: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'select', 'new-chat'])
const keyword = ref('')
const searchInput = ref(null)

watch(
  () => props.visible,
  (val) => {
    if (val) {
      keyword.value = ''
      requestAnimationFrame(() => {
        searchInput.value?.focus()
      })
    }
  }
)

const filtered = computed(() => {
  const term = keyword.value.trim().toLowerCase()
  const words = term ? term.split(/\s+/).filter(Boolean) : []
  const list = Array.isArray(props.conversations) ? props.conversations.slice() : []
  list.sort((a, b) => {
    const da = a.last_message_date ? new Date(a.last_message_date).getTime() : 0
    const db = b.last_message_date ? new Date(b.last_message_date).getTime() : 0
    return db - da
  })
  if (!term) return list
  return list.filter((conv) => {
    const haystacks = []
    haystacks.push((conv.title || '').toLowerCase())
    const dateLabel = formatLabel(conv.last_message_date).toLowerCase()
    haystacks.push(dateLabel)
    const dateIso = conv.last_message_date ? new Date(conv.last_message_date).toISOString().slice(0, 10) : ''
    if (dateIso) haystacks.push(dateIso)

    return words.every((word) => haystacks.some((h) => h.includes(word)))
  })
})

const groupedResults = computed(() => {
  const groups = []
  const map = new Map()
  filtered.value.forEach((conv) => {
    const label = formatGroup(conv.last_message_date)
    if (!map.has(label)) {
      const section = { label, items: [] }
      map.set(label, section)
      groups.push(section)
    }
    map.get(label).items.push(conv)
  })
  return groups
})

function formatGroup(date) {
  if (!date) return 'Cũ hơn'
  const now = new Date()
  const target = new Date(date)
  const diffMs = now - target
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays <= 0) return 'Hôm nay'
  if (diffDays === 1) return 'Hôm qua'
  if (diffDays < 7) return `${diffDays} ngày trước`
  if (diffDays < 30) return 'Trong 30 ngày qua'
  return 'Cũ hơn'
}

function formatLabel(date) {
  if (!date) return 'Không xác định'
  try {
    return new Date(date).toLocaleString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return date
  }
}

function close() {
  emit('close')
}

function selectConversation(id) {
  emit('select', id)
  emit('close')
}

function selectNewChat() {
  emit('new-chat')
  emit('close')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
