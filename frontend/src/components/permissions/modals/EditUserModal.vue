<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-3xl"
    :panel-class="'bg-white rounded-xl w-full max-h-[90vh] overflow-y-auto'"
    @close="emit('close')"
  >
    <template #default>
      <div class="flex items-center justify-between p-6 border-b">
        <div>
          <h3 class="text-lg font-bold text-gray-900">
            {{ currentForm.full_name || currentForm.email || 'Chỉnh sửa người dùng' }}
          </h3>
          <p class="text-sm text-gray-500 mt-1">{{ currentForm.email }}</p>
        </div>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">
          <XIcon class="w-6 h-6" />
        </button>
      </div>

      <div class="p-6 space-y-4">
        <div v-if="isLoading" class="flex flex-col items-center justify-center py-10">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="text-sm text-gray-500 mt-3">Đang tải thông tin người dùng...</p>
        </div>

        <template v-else>
          <div v-if="displayError" class="bg-red-50 border border-red-200 text-sm text-red-700 rounded-lg p-3">
            {{ displayError }}
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Họ và tên</label>
                <input
                  :value="currentForm.full_name"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateField('full_name', $event.target.value)"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  :value="currentForm.email"
                  type="email"
                  disabled
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Tên</label>
                <input
                  :value="currentForm.first_name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateField('first_name', $event.target.value)"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Họ</label>
                <input
                  :value="currentForm.last_name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateField('last_name', $event.target.value)"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
                <input
                  :value="currentForm.mobile_no"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateField('mobile_no', $event.target.value)"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Điện thoại bàn</label>
                <input
                  :value="currentForm.phone"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @input="updateField('phone', $event.target.value)"
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Ngôn ngữ</label>
                <select
                  :value="currentForm.language"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @change="updateField('language', $event.target.value)"
                >
                  <option value="vi">Tiếng Việt</option>
                  <option value="en">English</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Múi giờ</label>
                <select
                  :value="currentForm.time_zone"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @change="updateField('time_zone', $event.target.value)"
                >
                  <option value="Asia/Ho_Chi_Minh">Asia/Ho_Chi_Minh</option>
                  <option value="Asia/Bangkok">Asia/Bangkok</option>
                  <option value="UTC">UTC</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Vai trò
                <span class="text-xs font-normal text-gray-500 ml-2">
                  ({{ currentForm.roles?.length || 0 }} đã chọn)
                </span>
              </label>
              <div class="border border-gray-300 rounded-lg p-3 max-h-64 overflow-y-auto space-y-2">
                <div v-for="role in rolesToUse" :key="role.id || role.name" class="flex items-center justify-between">
                  <label :for="`role-checkbox-${role.id || role.name}`" class="flex items-center">
                    <input
                      :id="`role-checkbox-${role.id || role.name}`"
                      type="checkbox"
                      :value="role.id || role.name"
                      :checked="currentForm.roles?.includes(role.id || role.name)"
                      class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      @change="toggleRole(role.id || role.name, $event.target.checked)"
                    />
                    <span class="ml-2 text-sm text-gray-700">{{ role.role_name || role.name }}</span>
                  </label>
                  <span v-if="role.description" class="text-xs text-gray-400">{{ role.description }}</span>
                </div>
                <p v-if="!rolesToUse.length" class="text-sm text-gray-400">Không có vai trò nào</p>
              </div>
            </div>

            <div class="flex items-center space-x-2">
              <input
                id="user-enabled-toggle"
                type="checkbox"
                :checked="currentForm.enabled"
                class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                @change="updateField('enabled', $event.target.checked)"
              />
              <label for="user-enabled-toggle" class="text-sm text-gray-700">Kích hoạt người dùng</label>
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
                :disabled="isSaving"
                class="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed flex items-center"
              >
                <span
                  v-if="isSaving"
                  class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"
                ></span>
                Lưu thay đổi
              </button>
            </div>
          </form>
        </template>
      </div>
    </template>
  </ModalBase>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { X as XIcon } from 'lucide-vue-next'
import ModalBase from '@/components/common/ModalBase.vue'
import documentPermissionService from '@/services/documentPermissionService'
import { updateUser as updateUserService } from '@/services/userService'

const props = defineProps({
  visible: { type: Boolean, default: false },
  userId: { type: String, default: '' },
  // Optional controlled props
  form: { type: Object, default: null },
  availableRoles: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'save', 'update:field', 'toggle-role', 'updated'])

const localForm = ref({
  id: '',
  email: '',
  full_name: '',
  first_name: '',
  last_name: '',
  mobile_no: '',
  phone: '',
  language: 'vi',
  time_zone: 'Asia/Ho_Chi_Minh',
  enabled: true,
  roles: [],
})
const originalForm = ref(null)
const localRoles = ref([])
const localLoading = ref(false)
const localSaving = ref(false)
const localError = ref('')

const isControlled = computed(() => !!props.form)
const currentForm = computed(() => (isControlled.value ? props.form : localForm.value))
const isLoading = computed(() => props.loading || localLoading.value)
const isSaving = computed(() => props.saving || localSaving.value)
const displayError = computed(() => props.error || localError.value)
const rolesToUse = computed(() => {
  return props.availableRoles && props.availableRoles.length ? props.availableRoles : localRoles.value
})

const updateField = (field, value) => {
  if (isControlled.value) emit('update:field', field, value)
  else localForm.value = { ...localForm.value, [field]: value }
}

const toggleRole = (roleName, isChecked) => {
  if (isControlled.value) {
    emit('toggle-role', roleName, isChecked)
    return
  }
  const roles = Array.isArray(localForm.value.roles) ? [...localForm.value.roles] : []
  if (isChecked) {
    if (!roles.includes(roleName)) roles.push(roleName)
  } else {
    const i = roles.indexOf(roleName)
    if (i > -1) roles.splice(i, 1)
  }
  localForm.value = { ...localForm.value, roles }
}

const loadRoles = async () => {
  try {
    const resp = await documentPermissionService.getRoles()
    let roles = []
    if (resp?.data) roles = resp.data
    else if (Array.isArray(resp)) roles = resp
    else if (resp?.roles) roles = resp.roles
    localRoles.value = Array.isArray(roles) ? roles : []
  } catch (e) {
    localRoles.value = []
  }
}

const loadUser = async () => {
  if (!props.userId || isControlled.value) return
  try {
    localError.value = ''
    localLoading.value = true
    const response = await createResource({
      url: 'dbiz_ai_agent.api.users.get_user_detail',
      params: { user_id: props.userId },
      method: 'GET',
    }).fetch()
    const payload = response?.message || response
    const data = payload?.data || payload || {}
    if (!data || !data.email) throw new Error('Không tìm thấy thông tin người dùng')
    localForm.value = {
      id: data.name || props.userId,
      email: data.email || '',
      full_name: data.full_name || data.email || '',
      first_name: data.first_name || '',
      last_name: data.last_name || '',
      mobile_no: data.mobile_no || '',
      phone: data.phone || '',
      language: data.language || 'vi',
      time_zone: data.time_zone || 'Asia/Ho_Chi_Minh',
      enabled: data.enabled !== undefined ? !!data.enabled : true,
      roles: Array.isArray(data.roles) ? data.roles : [],
    }
    originalForm.value = JSON.parse(JSON.stringify(localForm.value))
  } catch (err) {
    localError.value = err?.message || 'Không thể tải thông tin người dùng'
  } finally {
    localLoading.value = false
  }
}

watch(
  () => props.visible,
  (v) => {
    if (v) {
      if (!props.availableRoles || !props.availableRoles.length) void loadRoles()
      void loadUser()
    }
  }
)

const handleSubmit = async () => {
  if (isControlled.value) {
    emit('save')
    return
  }
  if (!currentForm.value.id) {
    localError.value = 'Thiếu ID người dùng'
    return
  }
  try {
    localSaving.value = true
    localError.value = ''
    const payload = {}
    const fields = ['full_name', 'first_name', 'last_name', 'mobile_no', 'phone', 'language', 'time_zone', 'enabled']
    const original = originalForm.value || {}
    fields.forEach((f) => {
      if (currentForm.value[f] !== original[f]) payload[f] = currentForm.value[f]
    })
    const curRoles = Array.isArray(currentForm.value.roles) ? currentForm.value.roles.slice().sort() : []
    const origRoles = Array.isArray(original.roles) ? original.roles.slice().sort() : []
    if (JSON.stringify(curRoles) !== JSON.stringify(origRoles)) payload.roles = JSON.stringify(curRoles)

    console.log('[EditUserModal] Submitting update:', {
      userId: currentForm.value.id,
      payload: payload,
      currentRoles: curRoles,
      originalRoles: origRoles,
    })

    if (Object.keys(payload).length === 0) {
      localError.value = 'Không có thay đổi nào để lưu.'
      localSaving.value = false
      return
    }

    const result = await updateUserService(currentForm.value.id, payload)

    console.log('[EditUserModal] Update result:', result)

    if (!result || result.success === false) {
      throw new Error(result?.error || 'Không thể cập nhật người dùng')
    }

    emit('updated', { id: currentForm.value.id })
    emit('close')
  } catch (err) {
    console.error('[EditUserModal] Update error:', err)
    localError.value = err?.message || 'Không thể cập nhật người dùng'
  } finally {
    localSaving.value = false
  }
}
</script>
