<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-3xl"
    :panel-class="'bg-white rounded-xl w-full max-h-[90vh] overflow-y-auto'"
    @close="emit('close')"
  >
    <div class="flex items-center justify-between p-6 border-b">
      <div>
        <h3 class="text-lg font-bold text-gray-900">Tạo người dùng mới</h3>
        <p v-if="currentForm && currentForm.email" class="text-sm text-gray-500 mt-1">{{ currentForm.email }}</p>
      </div>
      <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">
        <XIcon class="w-6 h-6" />
      </button>
    </div>

    <div class="p-6 space-y-4">
      <div v-if="isLoading" class="flex flex-col items-center justify-center py-10">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="text-sm text-gray-500 mt-3">Đang chuẩn bị...</p>
      </div>

      <template v-else>
        <div v-if="displayError" class="bg-red-50 border border-red-200 text-sm text-red-700 rounded-lg p-3">
          {{ displayError }}
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                :value="currentForm.email"
                type="email"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                @input="updateField('email', $event.target.value)"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mật khẩu (tùy chọn)</label>
              <input
                :value="currentForm.password"
                type="password"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                @input="updateField('password', $event.target.value)"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Họ và tên *</label>
              <input
                :value="currentForm.full_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                @input="updateField('full_name', $event.target.value)"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
              <input
                :value="currentForm.mobile_no"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                @input="updateField('mobile_no', $event.target.value)"
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
              <span class="text-xs font-normal text-gray-500 ml-2">({{ currentForm.roles?.length || 0 }} đã chọn)</span>
            </label>
            <div class="border border-gray-300 rounded-lg p-3 max-h-64 overflow-y-auto space-y-2">
              <div v-for="role in rolesToUse" :key="role.id || role.name" class="flex items-center justify-between">
                <label :for="`create-role-checkbox-${role.id || role.name}`" class="flex items-center">
                  <input
                    :id="`create-role-checkbox-${role.id || role.name}`"
                    type="checkbox"
                    :value="role.id || role.name"
                    :checked="currentForm.roles?.includes(role.id || role.name)"
                    class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    @change="toggleRole(role.id || role.name, $event.target.checked)"
                  />
                  <span class="ml-2 text-sm text-gray-700">{{ role.role_name || role.title || role.name }}</span>
                </label>
                <span v-if="role.description" class="text-xs text-gray-400">{{ role.description }}</span>
              </div>
              <p v-if="!rolesToUse.length" class="text-sm text-gray-400">Không có vai trò nào</p>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <input
              id="create-user-enabled-toggle"
              type="checkbox"
              :checked="currentForm.enabled"
              class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              @change="updateField('enabled', $event.target.checked)"
            />
            <label for="create-user-enabled-toggle" class="text-sm text-gray-700">Kích hoạt người dùng</label>
          </div>

          <div class="flex items-center justify-end space-x-3 pt-4 border-t">
            <button type="button" @click="emit('close')"
                    class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200">
              Hủy
            </button>
            <button type="submit"
                    :disabled="isSaving"
                    class="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed flex items-center">
              <span v-if="isSaving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
              Tạo người dùng
            </button>
          </div>
        </form>
      </template>
    </div>
  </ModalBase>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { X as XIcon } from 'lucide-vue-next'
import ModalBase from '@/components/common/ModalBase.vue'
import documentPermissionService from '@/services/documentPermissionService'
import { createUser as createUserService, updateUser as updateUserService } from '@/services/userService'

const props = defineProps({
  visible: { type: Boolean, default: false },
  // Keep props for backward compat but not required
  form: { type: Object, default: null },
  availableRoles: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' }
})

const emit = defineEmits(['close', 'created'])

// Internal form state
const localForm = ref({
  email: '',
  password: '',
  full_name: '',
  first_name: '',
  last_name: '',
  mobile_no: '',
  language: 'vi',
  time_zone: 'Asia/Ho_Chi_Minh',
  enabled: true,
  roles: []
})
const internalLoading = ref(false)
const internalSaving = ref(false)
const internalError = ref('')

const isControlled = computed(() => !!props.form)
const currentForm = computed(() => (isControlled.value ? props.form : localForm.value))
const isLoading = computed(() => props.loading || internalLoading.value)
const isSaving = computed(() => props.saving || internalSaving.value)
const displayError = computed(() => props.error || internalError.value)

const updateField = (field, value) => {
  if (isControlled.value) {
    // Fallback for older usage
    props.form[field] = value
  } else {
    localForm.value = { ...localForm.value, [field]: value }
  }
}

// Load AI Roles (AI Role DocType). These are assigned to Contact via update_user
const localRoles = ref([])
const rolesToUse = computed(() => {
  return (props.availableRoles && props.availableRoles.length) ? props.availableRoles : (localRoles.value || [])
})

const loadAiRoles = async () => {
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

watch(
  () => props.visible,
  (v) => {
    if (!v) return
    if (!props.availableRoles || !props.availableRoles.length) void loadAiRoles()
  },
  { immediate: false }
)

const toggleRole = (roleName, checked) => {
  const roles = Array.isArray(currentForm.value.roles) ? [...currentForm.value.roles] : []
  if (checked) {
    if (!roles.includes(roleName)) roles.push(roleName)
  } else {
    const i = roles.indexOf(roleName)
    if (i > -1) roles.splice(i, 1)
  }
  updateField('roles', roles)
}

// Helpers: extract and translate frappe error messages to Vietnamese
const extractFrappeMessage = (val) => {
  if (!val) return ''
  if (typeof val === 'string') return val
  if (val?.error) {
    if (typeof val.error === 'string') return val.error
    if (typeof val.error?.message === 'string') return val.error.message
  }
  if (typeof val?.message === 'string') return val.message
  if (typeof val?.message?.message === 'string') return val.message.message
  if (typeof val?.exception === 'string') return val.exception
  if (typeof val?.exc === 'string') return val.exc
  try { return JSON.stringify(val) } catch { return '' }
}

const translateUserCreateErrorMessage = (rawMsg) => {
  const msg = String(rawMsg || '').trim()
  if (!msg) return 'Không thể tạo người dùng'

  const usernameExists = msg.match(/Username\s+([\w.@+-]+)\s+already exists/i)
  if (usernameExists) {
    const uname = usernameExists[1]
    const suggested = (msg.match(/Suggested Username:\s*([\w.@+-]+)/i) || [])[1]
    return `Tên đăng nhập "${uname}" đã tồn tại.${suggested ? ` Gợi ý: "${suggested}".` : ''} Vui lòng chọn tên khác.`
  }

  const emailExists = msg.match(/User with email\s+([^\s]+)\s+already exists/i)
  if (emailExists) {
    return `Người dùng với email "${emailExists[1]}" đã tồn tại.`
  }

  if (/Duplicate entry/i.test(msg)) {
    return 'Bản ghi đã tồn tại. Vui lòng chọn giá trị khác.'
  }

  if (/Failed to create user/i.test(msg)) {
    return msg.replace(/Failed to create user/i, 'Không thể tạo người dùng')
  }

  return `Không thể tạo người dùng: ${msg}`
}

const formatFrappeErrorMessage = (payload) => translateUserCreateErrorMessage(extractFrappeMessage(payload))
const translateUserCreateError = (err) => {
  if (!err) return 'Không thể tạo người dùng'
  return translateUserCreateErrorMessage(err?.message || extractFrappeMessage(err))
}

const handleSubmit = async () => {
  try {
    internalError.value = ''
    internalSaving.value = true
    const f = currentForm.value
    if (!f.email || !f.full_name) {
      throw new Error('Email và họ tên là bắt buộc')
    }
    const payload = {
      email: f.email,
      full_name: f.full_name,
      first_name: f.first_name || '',
      last_name: f.last_name || '',
      password: f.password || '',
      enabled: f.enabled ? 1 : 0,
      mobile_no: f.mobile_no || '',
      language: f.language || 'vi',
      time_zone: f.time_zone || 'Asia/Ho_Chi_Minh'
    }
    const result = await createUserService(payload)
    if (!result || result.success === false) {
      const msg = formatFrappeErrorMessage(result)
      throw new Error(msg || 'Không thể tạo người dùng')
    }
    // After creating the user, assign AI Roles to Contact via update_user
    const newUserId = result?.data?.name || f.email
    const aiRoles = Array.isArray(f.roles) ? f.roles : []
    if (newUserId && aiRoles.length) {
      try {
        await updateUserService(newUserId, { roles: JSON.stringify(aiRoles) })
      } catch (e) {
        // Non-fatal: creation succeeded but AI role assignment failed
        window.frappe?.msgprint?.({
          title: 'Lưu ý',
          message: 'Tạo người dùng thành công nhưng gán AI Role thất bại. Bạn có thể chỉnh sửa sau trong màn hình Edit User.',
          indicator: 'orange'
        })
      }
    }
    emit('created', { email: f.email })
    emit('close')
  } catch (err) {
    internalError.value = translateUserCreateError(err)
  } finally {
    internalSaving.value = false
  }
}
</script>
