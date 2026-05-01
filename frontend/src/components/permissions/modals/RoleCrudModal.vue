<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-2xl"
    :panel-class="'bg-white rounded-xl max-h-[90vh] w-full overflow-y-auto'"
    @close="emit('close')"
  >
    <div class="flex items-center justify-between p-6 border-b">
      <h3 class="text-lg font-bold text-gray-900">
        {{ mode === 'create' ? 'Thêm vai trò mới' : 'Chỉnh sửa vai trò' }}
      </h3>
      <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">
        <XIcon class="w-6 h-6" />
      </button>
    </div>

    <div class="p-6 space-y-4">
      <div v-if="loading" class="flex flex-col items-center justify-center py-10">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="text-sm text-gray-500 mt-3">Đang tải thông tin vai trò...</p>
      </div>

      <template v-else>
        <div v-if="error" class="bg-red-50 border border-red-200 text-sm text-red-700 rounded-lg p-3">
          {{ error }}
        </div>

        <form @submit.prevent="emit('submit')" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Tên vai trò *</label>
            <input
              :value="formState.role_name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateField('role_name', $event.target.value)"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Mô tả</label>
            <textarea
              :value="formState.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="updateField('description', $event.target.value)"
            ></textarea>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Ưu tiên</label>
              <input
                :value="formState.priority"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                @input="updateNumber('priority', $event.target.value)"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Ghi chú</label>
              <input
                :value="formState.icon"
                type="text"
                placeholder="Biểu tượng hoặc chữ cái"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                @input="updateField('icon', $event.target.value)"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Màu hiển thị</label>
            <input
              :value="formState.color"
              type="color"
              class="h-10 w-16 border border-gray-300 rounded-lg"
              @input="updateField('color', $event.target.value)"
            />
          </div>

          <div class="flex items-center space-x-2">
            <input
              id="role-active"
              type="checkbox"
              :checked="formState.is_active"
              class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              @change="updateField('is_active', $event.target.checked)"
            />
            <label for="role-active" class="text-sm text-gray-700">Kích hoạt vai trò</label>
          </div>

          <div class="flex items-center space-x-2">
            <input
              id="role-user-management"
              type="checkbox"
              :checked="formState.user_management"
              class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              @change="updateField('user_management', $event.target.checked)"
            />
            <label for="role-user-management" class="text-sm text-gray-700">Quản lý người dùng</label>
          </div>

          <div class="flex items-center justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              @click="emit('close')"
              class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Hủy
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed flex items-center"
            >
              <span
                v-if="saving"
                class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"
              ></span>
              Lưu vai trò
            </button>
          </div>
        </form>
      </template>
    </div>
  </ModalBase>
</template>

<script setup>
import { computed } from 'vue'
import { X as XIcon } from 'lucide-vue-next'
import ModalBase from '@/components/common/ModalBase.vue'

const DEFAULT_FORM = {
  id: '',
  role_name: '',
  description: '',
  is_active: true,
  priority: 1,
  color: '#6b7280',
  icon: '',
  user_management: false
}

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'create'
  },
  loading: {
    type: Boolean,
    default: false
  },
  saving: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  form: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['close', 'submit', 'update:form'])

const formState = computed(() => ({
  ...DEFAULT_FORM,
  ...(props.form || {})
}))

const updateField = (field, value) => {
    emit('update:form', {
      ...formState.value,
      [field]: value
    })
}

const updateNumber = (field, value) => {
  const numericValue = Number(value)
  updateField(field, Number.isNaN(numericValue) ? 0 : numericValue)
}
</script>
