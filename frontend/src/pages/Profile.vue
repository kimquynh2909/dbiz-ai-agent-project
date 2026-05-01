<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="bg-white rounded-2xl shadow-sm p-6 mb-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="relative">
              <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                <img v-if="profile.user_image" :src="profile.user_image" :alt="profile.full_name" class="w-full h-full object-cover rounded-2xl">
                <span v-else>{{ getInitials(profile.full_name || profile.email) }}</span>
              </div>
              <button @click="showImageUpload = true" class="absolute -bottom-2 -right-2 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors shadow-lg">
                <CameraIcon class="w-4 h-4" />
              </button>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ profile.full_name || profile.email }}</h1>
              <p class="text-gray-500">{{ profile.email }}</p>
              <div class="flex items-center space-x-2 mt-1">
                <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                <span class="text-sm text-gray-600">Hoạt động</span>
              </div>
            </div>
          </div>
          <div class="text-right">
            <div class="text-sm text-gray-500">Tham gia từ</div>
            <div class="font-medium text-gray-900">{{ formatDate(profile.creation) }}</div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Profile Form -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-bold text-gray-900">Thông tin cá nhân</h2>
              <button 
                v-if="!isEditing" 
                @click="startEditing"
                class="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <EditIcon class="w-4 h-4" />
                <span>Chỉnh sửa</span>
              </button>
            </div>

            <form @submit.prevent="saveProfile" class="space-y-6">
              <!-- Basic Information -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Họ</label>
                  <input 
                    v-model="editForm.first_name"
                    :disabled="!isEditing"
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="Nhập họ"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Tên</label>
                  <input 
                    v-model="editForm.last_name"
                    :disabled="!isEditing"
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="Nhập tên"
                  >
                </div>
              </div>

              <!-- Contact Information -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Số điện thoại</label>
                  <input 
                    v-model="editForm.mobile_no"
                    :disabled="!isEditing"
                    type="tel" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="Nhập số điện thoại"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Điện thoại cố định</label>
                  <input 
                    v-model="editForm.phone"
                    :disabled="!isEditing"
                    type="tel" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                    placeholder="Nhập điện thoại cố định"
                  >
                </div>
              </div>

              <!-- Personal Information -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Giới tính</label>
                  <select 
                    v-model="editForm.gender"
                    :disabled="!isEditing"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                  >
                    <option value="">Chọn giới tính</option>
                    <option value="Male">Nam</option>
                    <option value="Female">Nữ</option>
                    <option value="Other">Khác</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Ngày sinh</label>
                  <input 
                    v-model="editForm.birth_date"
                    :disabled="!isEditing"
                    type="date" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                  >
                </div>
              </div>

              <!-- Location -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Địa chỉ</label>
                <input 
                  v-model="editForm.location"
                  :disabled="!isEditing"
                  type="text" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                  placeholder="Nhập địa chỉ"
                >
              </div>

              <!-- Bio -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Giới thiệu bản thân</label>
                <textarea 
                  v-model="editForm.bio"
                  :disabled="!isEditing"
                  rows="4" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                  placeholder="Viết vài dòng giới thiệu về bản thân..."
                ></textarea>
              </div>

              <!-- Preferences -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Ngôn ngữ</label>
                  <select 
                    v-model="editForm.language"
                    :disabled="!isEditing"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                  >
                    <option value="vi">Tiếng Việt</option>
                    <option value="en">English</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Múi giờ</label>
                  <select 
                    v-model="editForm.time_zone"
                    :disabled="!isEditing"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                  >
                    <option value="Asia/Ho_Chi_Minh">Việt Nam (GMT+7)</option>
                    <option value="Asia/Bangkok">Bangkok (GMT+7)</option>
                    <option value="Asia/Singapore">Singapore (GMT+8)</option>
                  </select>
                </div>
              </div>

              <!-- Action Buttons -->
              <div v-if="isEditing" class="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
                <button 
                  type="button"
                  @click="cancelEditing"
                  class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Hủy
                </button>
                <button 
                  type="submit"
                  :disabled="loading"
                  class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <LoaderIcon v-if="loading" class="w-4 h-4 animate-spin" />
                  <SaveIcon v-else class="w-4 h-4" />
                  <span>{{ loading ? 'Đang lưu...' : 'Lưu thay đổi' }}</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Account Stats -->
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Thống kê tài khoản</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <LoginIcon class="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Lần đăng nhập</p>
                    <p class="text-sm text-gray-500">Tổng số lần</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-xl font-bold text-blue-600">{{ activity.login_count || 0 }}</div>
                </div>
              </div>

              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <ClockIcon class="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Lần cuối hoạt động</p>
                    <p class="text-sm text-gray-500">{{ formatDate(activity.last_active) || 'Chưa có' }}</p>
                  </div>
                </div>
              </div>

              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <FileTextIcon class="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">Tài liệu tạo</p>
                    <p class="text-sm text-gray-500">Tổng số</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-xl font-bold text-purple-600">{{ activity.documents_created || 0 }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Security Settings -->
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Bảo mật</h3>
            <div class="space-y-4">
              <button 
                @click="showPasswordChange = true"
                class="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                    <KeyIcon class="w-5 h-5 text-red-600" />
                  </div>
                  <div class="text-left">
                    <p class="font-medium text-gray-900">Đổi mật khẩu</p>
                    <p class="text-sm text-gray-500">Cập nhật mật khẩu bảo mật</p>
                  </div>
                </div>
                <ChevronRightIcon class="w-5 h-5 text-gray-400" />
              </button>
            </div>
          </div>

          <!-- User Roles -->
          <div class="bg-white rounded-2xl shadow-sm p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Vai trò & Quyền hạn</h3>
            <div class="space-y-2">
              <div v-for="role in profile.roles" :key="role" class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span class="text-sm text-gray-700">{{ role }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Upload Modal -->
    <div v-if="showImageUpload" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Cập nhật ảnh đại diện</h3>
        <div class="space-y-4">
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input 
              ref="fileInput"
              type="file" 
              accept="image/*" 
              @change="handleImageUpload"
              class="hidden"
            >
            <button @click="$refs.fileInput.click()" class="text-blue-600 hover:text-blue-700">
              <UploadIcon class="w-12 h-12 mx-auto mb-2" />
              <p>Chọn ảnh từ máy tính</p>
              <p class="text-sm text-gray-500 mt-1">JPG, PNG, GIF (tối đa 5MB)</p>
            </button>
          </div>
          <div class="flex items-center justify-end space-x-4">
            <button 
              @click="showImageUpload = false"
              class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Hủy
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Password Change Modal -->
    <div v-if="showPasswordChange" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Đổi mật khẩu</h3>
        <form @submit.prevent="changePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Mật khẩu hiện tại</label>
            <input 
              v-model="passwordForm.current_password"
              type="password" 
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Nhập mật khẩu hiện tại"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Mật khẩu mới</label>
            <input 
              v-model="passwordForm.new_password"
              type="password" 
              required
              minlength="8"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Nhập mật khẩu mới (tối thiểu 8 ký tự)"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Xác nhận mật khẩu mới</label>
            <input 
              v-model="passwordForm.confirm_password"
              type="password" 
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Nhập lại mật khẩu mới"
            >
          </div>
          <div class="flex items-center justify-end space-x-4 pt-4">
            <button 
              type="button"
              @click="showPasswordChange = false"
              class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Hủy
            </button>
            <button 
              type="submit"
              :disabled="passwordLoading"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <LoaderIcon v-if="passwordLoading" class="w-4 h-4 animate-spin" />
              <span>{{ passwordLoading ? 'Đang cập nhật...' : 'Đổi mật khẩu' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" class="fixed top-4 right-4 z-50">
      <div :class="[
        'px-6 py-4 rounded-lg shadow-lg',
        message.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]">
        {{ message.text }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { createResource } from 'frappe-ui'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Camera as CameraIcon,
  Upload as UploadIcon,
  Key as KeyIcon,
  Clock as ClockIcon,
  FileText as FileTextIcon,
  LogIn as LoginIcon,
  ChevronRight as ChevronRightIcon,
  Loader as LoaderIcon
} from 'lucide-vue-next'

// Reactive data
const profile = ref({})
const activity = ref({})
const isEditing = ref(false)
const loading = ref(false)
const passwordLoading = ref(false)
const showImageUpload = ref(false)
const showPasswordChange = ref(false)
const message = ref(null)

const editForm = reactive({
  first_name: '',
  last_name: '',
  mobile_no: '',
  phone: '',
  gender: '',
  birth_date: '',
  location: '',
  bio: '',
  language: 'vi',
  time_zone: 'Asia/Ho_Chi_Minh'
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const getUserProfile = async () => {
  try {
    const res = await createResource({ url: 'dbiz_ai_agent.api.user_profile.get_user_profile', params: {}, method: 'GET' }).fetch()
    const payload = res?.message ?? res?.data
    if (payload) {
      profile.value = payload.data ?? payload
      Object.keys(editForm).forEach(key => {
        editForm[key] = profile.value[key] || ''
      })
    }
  } catch (error) {
    showMessage('Không thể tải thông tin profile', 'error')
    console.error('Get profile error:', error)
  }
}

const updateProfile = async (profile_data) => {
  try {
  const res = await createResource({ url: 'dbiz_ai_agent.api.user_profile.update_user_profile', params: { profile_data }, method: 'POST' }).fetch()
    const payload = res?.message ?? res?.data
    if (payload) {
      showMessage(payload.message || 'Cập nhật thành công!', 'success')
      isEditing.value = false
      await getUserProfile()
    }
  } catch (error) {
    showMessage('Không thể cập nhật profile', 'error')
    console.error('Update profile error:', error)
  }
}

const getUserActivity = async () => {
  try {
  const res = await createResource({ url: 'dbiz_ai_agent.api.user_profile.get_user_activity', params: {}, method: 'GET' }).fetch()
    const payload = res?.message ?? res?.data
    if (payload) activity.value = payload.data ?? payload
  } catch (error) {
    console.error('Get activity error:', error)
  }
}

const changePasswordResource = async (current_password, new_password) => {
  try {
  const res = await createResource({ url: 'dbiz_ai_agent.api.user_profile.change_password', params: { current_password, new_password }, method: 'POST' }).fetch()
    const payload = res?.message ?? res?.data
    if (payload) {
      showMessage(payload.message || 'Đổi mật khẩu thành công!', 'success')
      showPasswordChange.value = false
      Object.keys(passwordForm).forEach(key => { passwordForm[key] = '' })
    }
  } catch (error) {
    showMessage('Không thể đổi mật khẩu', 'error')
    console.error('Change password error:', error)
  }
}

// Methods
const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('vi-VN')
}

const startEditing = () => {
  isEditing.value = true
}

const cancelEditing = () => {
  isEditing.value = false
  // Reset form to original values
  Object.keys(editForm).forEach(key => {
    editForm[key] = profile.value[key] || ''
  })
}

const saveProfile = async () => {
  loading.value = true
  try {
    await updateProfile(editForm)
  } finally {
    loading.value = false
  }
}

const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validate file size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    showMessage('File quá lớn. Vui lòng chọn file nhỏ hơn 5MB', 'error')
    return
  }

  // Create FormData
  const formData = new FormData()
  formData.append('file', file)

  try {
    // Try using frappe.upload if available
    if (window.frappe && typeof window.frappe.upload === 'function') {
      const res = await new Promise((resolve, reject) => {
        window.frappe.upload({
          args: { file_url: null },
          file: file,
          method: 'dbiz_ai_agent.api.user_profile.upload_profile_image',
          callback: (r) => {
            if (r && r.message) resolve(r)
            else reject(new Error('Upload failed'))
          }
        })
      })

      if (res.message && res.message.success) {
        showMessage('Cập nhật ảnh đại diện thành công!', 'success')
        showImageUpload.value = false
        getUserProfile.reload()
      } else {
        throw new Error(res.message || 'Upload failed')
      }
    } else {
      // Fallback to fetch with CSRF token
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || window.frappe?.csrf_token || ''
      const response = await fetch('/api/method/dbiz_ai_agent.api.user_profile.upload_profile_image', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Frappe-CSRF-Token': csrfToken
        }
      })

      const data = await response.json()
      if (data.message && data.message.success) {
        showMessage('Cập nhật ảnh đại diện thành công!', 'success')
        showImageUpload.value = false
        getUserProfile.reload()
      } else {
        throw new Error(data.message || 'Upload failed')
      }
    }
  } catch (error) {
    showMessage('Không thể upload ảnh', 'error')
    console.error('Upload error:', error)
  }
}

const changePassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    showMessage('Mật khẩu xác nhận không khớp', 'error')
    return
  }

  passwordLoading.value = true
  try {
    await changePasswordResource(passwordForm.current_password, passwordForm.new_password)
  } finally {
    passwordLoading.value = false
  }
}

const showMessage = (text, type = 'success') => {
  message.value = { text, type }
  setTimeout(() => {
    message.value = null
  }, 5000)
}

onMounted(() => {
  // Load profile and activity explicitly
  getUserProfile()
  getUserActivity()
})
</script>
