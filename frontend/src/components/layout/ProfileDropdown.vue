<template>
  <div class="relative">
    <button @click="$emit('toggle')"
            class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 transition-colors">
      <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
        <UserIcon class="w-5 h-5 text-white" />
      </div>
      <div class="hidden sm:block text-left">
        <p class="text-sm font-medium text-gray-900">{{ currentUser?.name }}</p>
        <p class="text-xs text-gray-500">{{ currentUser?.email }}</p>
      </div>
      <ChevronDownIcon class="w-4 h-4 text-gray-500" />
    </button>

    <div v-if="open" class="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
      <div class="px-4 py-3 border-b border-gray-100">
        <p class="text-sm font-medium text-gray-900">{{ currentUser?.name }}</p>
        <p class="text-xs text-gray-500">{{ currentUser?.email }}</p>
      </div>
      <button @click="$emit('go-to-profile')"
              class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center">
        <UserIcon class="w-4 h-4 mr-3" />
        Thông tin cá nhân
      </button>
      <button @click="$emit('go-to-settings')"
              class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center">
        <SettingsIcon class="w-4 h-4 mr-3" />
        Cài đặt
      </button>
      <div class="border-t border-gray-100"></div>
      <button @click="$emit('logout')"
              class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center">
        <LogOutIcon class="w-4 h-4 mr-3" />
        Đăng xuất
      </button>
    </div>
  </div>
</template>

<script setup>

// ===== IMPORT ICONS =====
import {
  ChevronDown as ChevronDownIcon,
  User as UserIcon,
  Settings as SettingsIcon,
  LogOut as LogOutIcon
} from 'lucide-vue-next'

// ===== PROPS NHẬN TỪ COMPONENT CHA =====
const props = defineProps({
  currentUser: { type: Object, required: true }, // thông tin user hiện tại
  open: { type: Boolean, required: true } // trạng thái dropdown
})

// ===== EMIT SỰ KIỆN RA NGOÀI =====
const emit = defineEmits([
  'toggle', // mở/đóng dropdown
  'logout', // đăng xuất
  'go-to-profile', // chuyển sang trang cá nhân
  'go-to-settings' // chuyển sang trang cài đặt
])
</script>
