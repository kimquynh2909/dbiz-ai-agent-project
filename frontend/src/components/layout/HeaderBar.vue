<template>
  <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
    <div class="flex items-center justify-between h-16 px-6">
      <button @click="$emit('toggle-sidebar')" class="lg:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100">
        <MenuIcon class="w-6 h-6" />
      </button>

      <div class="flex-1 lg:flex lg:items-center lg:justify-between">
        <div class="hidden lg:block">
          <h2 class="text-xl font-semibold text-gray-900">{{ pageTitle }}</h2>
          <p class="text-sm text-gray-500">{{ pageDescription }}</p>
        </div>

        <div class="flex items-center space-x-3 ml-auto">
          <div class="relative">
            <select v-model="localLocale" @change="onChangeLanguage"
                    class="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-gray-700 hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors cursor-pointer">
              <option value="vi">🇻🇳 Tiếng Việt</option>
              <option value="en">🇺🇸 English</option>
            </select>
            <div class="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
              <ChevronDownIcon class="w-4 h-4 text-gray-400" />
            </div>
          </div>

          <button class="relative p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
            <BellIcon class="w-5 h-5" />
            <span class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full flex items-center justify-center">
              <span class="w-1.5 h-1.5 bg-white rounded-full"></span>
            </span>
          </button>

          <ProfileDropdown
            :current-user="currentUser"
            :open="profileOpen"
            @toggle="emitToggleProfile"
            @logout="emitLogout"
            @go-to-profile="$emit('go-to-profile')"
            @go-to-settings="$emit('go-to-settings')"
          />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ChevronDown as ChevronDownIcon, Bell as BellIcon, Menu as MenuIcon } from 'lucide-vue-next'
import ProfileDropdown from './ProfileDropdown.vue'



// ===== Props nhận từ layout cha =====
const props = defineProps({
  pageTitle: { type: String, default: '' }, // tiêu đề trang
  pageDescription: { type: String, default: '' }, // mô tả trang
  currentLocale: { type: String, default: 'vi' }, // ngôn ngữ hiện tại
  currentUser: { type: Object, default: null } // thông tin user hiện tại
})

// ===== Emit các sự kiện ra ngoài =====
const emit = defineEmits([
  'toggle-sidebar',
  'change-language',
  'go-to-profile',
  'go-to-settings',
  'logout',
  'toggle-profile'
])

// ===== State nội bộ component =====
const localLocale = ref(props.currentLocale) // ngôn ngữ dropdown
const profileOpen = ref(false) // trạng thái dropdown profile

// ===== Watcher: đồng bộ ngôn ngữ khi props thay đổi =====
watch(() => props.currentLocale, (v) => { localLocale.value = v })

// ===== Các hàm xử lý sự kiện UI =====
// Đổi ngôn ngữ giao diện
function onChangeLanguage() {
  emit('change-language', localLocale.value)
}

// Đổi trạng thái dropdown profile
function emitToggleProfile() {
  profileOpen.value = !profileOpen.value
  emit('toggle-profile')
}

// Đăng xuất
function emitLogout() {
  emit('logout')
}
</script>
