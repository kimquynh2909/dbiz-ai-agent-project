<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-3xl"
    :panel-class="'bg-white rounded-xl w-full max-h-[85vh] shadow-xl overflow-hidden'"
    @close="emit('close')"
  >
    <div class="flex items-center justify-between p-6 border-b">
      <div>
        <h3 class="text-lg font-bold text-gray-900">Danh sách người dùng</h3>
        <p v-if="roleInfo" class="text-sm text-gray-500 mt-1">
          {{ roleInfo.roleName }} • {{ totalUsers }} người dùng
        </p>
        <p v-if="roleInfo?.description" class="text-xs text-gray-400 mt-1">
          {{ roleInfo.description }}
        </p>
      </div>
      <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">
        <XIcon class="w-6 h-6" />
      </button>
    </div>

    <div class="p-6 space-y-4 overflow-y-auto max-h-[calc(85vh-5rem)]">
      <div v-if="loading" class="flex flex-col items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="text-sm text-gray-500 mt-3">Đang tải danh sách người dùng...</p>
      </div>

      <template v-else>
        <div v-if="error" class="bg-red-50 border border-red-200 text-sm text-red-700 rounded-lg p-4">
          {{ error }}
        </div>

        <div v-else-if="!users.length" class="text-center text-gray-500 py-10">
          Vai trò này chưa có người dùng nào.
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div v-for="user in users" :key="userKey(user)" class="py-4 flex items-start justify-between gap-4">
            <div class="flex items-center">
              <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-sm font-medium text-gray-600">
                {{ userInitial(user) }}
              </div>
              <div class="ml-3">
                <div class="text-sm font-semibold text-gray-900">
                  {{ user.full_name || user.name || 'Không rõ tên' }}
                </div>
                <div class="text-xs text-gray-500">
                  {{ user.email || user.name }}
                </div>
              </div>
            </div>
            <div class="text-right">
              <span
                :class="[
                  'inline-flex items-center px-2 py-1 text-xs font-medium rounded-full',
                  (user.enabled ?? 1) ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                ]"
              >
                {{ (user.enabled ?? 1) ? 'Đang hoạt động' : 'Đã khóa' }}
              </span>
              <div v-if="user.last_login" class="text-xs text-gray-400 mt-1">
                Lần đăng nhập cuối: {{ user.last_login }}
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </ModalBase>
</template>

<script setup>
import { computed } from 'vue'
import { X as XIcon } from 'lucide-vue-next'
import ModalBase from '@/components/common/ModalBase.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  roleInfo: {
    type: Object,
    default: null
  },
  users: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close'])

const totalUsers = computed(() => props.users.length || props.roleInfo?.userCount || 0)

const userInitial = (user) => {
  const input = user?.full_name || user?.name || user?.email || '?'
  return (input.charAt(0) || '?').toUpperCase()
}

const userKey = (user) => user?.email || user?.name || user?.id || Math.random().toString(36)
</script>
