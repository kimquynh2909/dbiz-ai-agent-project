<template>
  <div class="bg-white px-3 sm:px-6 border-b flex items-center justify-between flex-shrink-0" style="height: var(--chat-subheader-h)">
    <button @click.stop="emit('toggleSidebar')" class="lg:hidden p-2 text-gray-600 mr-2 sm:mr-3">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
    </button>
    
    <div class="flex items-center space-x-2 sm:space-x-4 flex-1 min-w-0">
      <div class="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center shadow-md flex-shrink-0">
        <img :src="avatarImage" alt="Ms.Sunny" class="w-8 h-8 sm:w-10 sm:h-10 object-contain" />
      </div>
      <div class="min-w-0 flex-1">
        <h2 class="text-base sm:text-xl font-bold text-gray-900 truncate">{{ assistantName }}</h2>
        <p class="text-xs sm:text-sm text-gray-500 truncate">{{ supportInfo }}</p>
      </div>
    </div>
    
    <div class="flex items-center space-x-2 sm:space-x-3 flex-shrink-0">
      <span class="px-2 sm:px-3 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium whitespace-nowrap">
        Online
      </span>
      <button
        v-if="showCloseButton"
        @click.stop="emit('closeWidget')"
        class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
        type="button"
        aria-label="Thu nhỏ chat"
        title="Thu nhỏ chat"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
      <div v-if="allowDelete" class="relative" ref="menuRef">
        <button @click.stop="showMenu = !showMenu" class="p-2 text-gray-400 hover:text-gray-600 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01"/>
          </svg>
        </button>
        <div v-if="showMenu" class="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <button
            @click="handleDelete"
            class="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white"
            :disabled="!allowDelete"
          >
            Xóa cuộc hội thoại
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  assistantName: {
    type: String,
    default: 'Ms.Sunny'
  },
  supportInfo: {
    type: String,
    default: 'AI Assistant thông minh'
  },
  avatarImage: {
    type: String,
    required: true
  },
  allowDelete: {
    type: Boolean,
    default: true
  },
  showCloseButton: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggleSidebar', 'deleteConversation', 'closeWidget'])

const showMenu = ref(false)
const menuRef = ref(null)

const handleDelete = () => {
  showMenu.value = false
  emit('deleteConversation')
}

const handleClickOutside = (event) => {
  if (!menuRef.value) return
  if (!menuRef.value.contains(event.target)) {
    showMenu.value = false
  }
}

onMounted(() => {
  if (props.allowDelete) {
    window.addEventListener('click', handleClickOutside)
  }
})

onBeforeUnmount(() => {
  if (props.allowDelete) {
    window.removeEventListener('click', handleClickOutside)
  }
})
</script>
