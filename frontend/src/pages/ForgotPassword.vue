<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex">
    <!-- Left Side - Reset Password Form -->
    <div class="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full space-y-8">
        <!-- Logo and Header -->
        <div class="text-center">
          <!-- Logo DBIZ -->
          <div class="mx-auto mb-8">
            <img :src="dbizLogo" alt="DBIZ Autonomous Logo" class="w-32 h-32 mx-auto object-contain drop-shadow-2xl" />
          </div>
          
          <div class="space-y-4">
            <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              {{ $t('forgotPassword.title') }}
            </h1>
            <p class="text-lg text-gray-600 font-medium">{{ $t('forgotPassword.subtitle') }}</p>
            <p class="text-sm text-gray-500">{{ $t('forgotPassword.description') }}</p>
          </div>
        </div>
      
        <!-- Reset Password Form -->
        <div class="bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/30">
          <form @submit.prevent="handleResetPassword" class="space-y-6">
            <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center animate-pulse">
              <AlertCircleIcon class="w-5 h-5 mr-2 flex-shrink-0" />
              <span class="text-sm">{{ error }}</span>
            </div>

            <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center">
              <CheckCircleIcon class="w-5 h-5 mr-2 flex-shrink-0" />
              <span class="text-sm">{{ success }}</span>
            </div>
            
            <div class="space-y-4">
              <div>
                <label for="username" class="block text-sm font-semibold text-gray-700 mb-2">{{ $t('forgotPassword.form.username') }}</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <UserIcon class="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="username"
                    v-model="form.username"
                    type="text"
                    required
                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    :placeholder="$t('forgotPassword.form.usernamePlaceholder')"
                  />
                </div>
              </div>
              
              <div>
                <label for="new_password" class="block text-sm font-semibold text-gray-700 mb-2">Mật khẩu mới</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <LockIcon class="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="new_password"
                    v-model="form.newPassword"
                    :type="showNewPassword ? 'text' : 'password'"
                    required
                    class="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    @click="showNewPassword = !showNewPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    <EyeIcon v-if="!showNewPassword" class="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    <EyeOffIcon v-else class="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  </button>
                </div>
              </div>

              <div>
                <label for="confirm_password" class="block text-sm font-semibold text-gray-700 mb-2">Xác nhận mật khẩu</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <LockIcon class="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="confirm_password"
                    v-model="form.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    required
                    class="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    <EyeIcon v-if="!showConfirmPassword" class="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    <EyeOffIcon v-else class="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  </button>
                </div>
              </div>
            </div>
            
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02]"
            >
              <LoaderIcon v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
              <KeyIcon v-else class="w-5 h-5 mr-2" />
              {{ loading ? 'Đang xử lý...' : 'Đặt lại mật khẩu' }}
            </button>
          </form>
        </div>
        
        <div class="text-center space-y-4">
          <router-link 
            to="/login" 
            class="inline-flex items-center text-sm text-blue-600 hover:text-blue-500 transition-colors font-medium"
          >
            <ArrowLeftIcon class="w-4 h-4 mr-2" />
            Quay lại đăng nhập
          </router-link>
          
          <div class="text-sm text-gray-600">
            Cần hỗ trợ? 
            <router-link to="/contact-admin" class="font-medium text-blue-600 hover:text-blue-500 transition-colors">
              Liên hệ quản trị viên
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Side - Security Information -->
    <div class="hidden lg:flex lg:flex-1 bg-gradient-to-br from-green-600 via-teal-700 to-blue-800 relative overflow-hidden">
      <div class="absolute inset-0 bg-black/20"></div>
      <div class="relative z-10 flex flex-col justify-center px-12 py-16 text-white">
        <div class="max-w-lg">
          <div class="mb-8">
            <h2 class="text-4xl font-bold mb-4">Bảo mật tài khoản</h2>
            <div class="w-16 h-1 bg-gradient-to-r from-green-400 to-teal-500 rounded-full mb-4"></div>
            <p class="text-xl text-green-100 leading-relaxed">
              Đảm bảo tài khoản của bạn luôn được bảo vệ với mật khẩu mạnh và an toàn.
            </p>
          </div>
          
          <div class="space-y-6">
            <!-- Password Security -->
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div class="flex items-start space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-green-400 to-green-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  <ShieldCheckIcon class="w-7 h-7" />
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold mb-2">Mật khẩu mạnh</h3>
                  <p class="text-green-100 text-sm leading-relaxed">
                    Sử dụng ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Account Protection -->
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div class="flex items-start space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  <LockIcon class="w-7 h-7" />
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold mb-2">Bảo vệ tài khoản</h3>
                  <p class="text-green-100 text-sm leading-relaxed">
                    Không chia sẻ mật khẩu và thay đổi định kỳ để đảm bảo an toàn
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Support -->
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div class="flex items-start space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  <HeadphonesIcon class="w-7 h-7" />
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold mb-2">Hỗ trợ 24/7</h3>
                  <p class="text-green-100 text-sm leading-relaxed">
                    Đội ngũ kỹ thuật sẵn sàng hỗ trợ bạn mọi lúc, mọi nơi
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Decorative Elements -->
      <div class="absolute top-20 right-20 w-32 h-32 bg-white/10 rounded-full blur-xl"></div>
      <div class="absolute bottom-20 left-20 w-24 h-24 bg-green-300/20 rounded-full blur-lg"></div>
      <div class="absolute top-1/2 right-10 w-16 h-16 bg-teal-300/20 rounded-full blur-md"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { call, createResource } from 'frappe-ui'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import { useRouter } from 'vue-router'
import {
  User as UserIcon,
  Lock as LockIcon,
  Eye as EyeIcon,
  EyeOff as EyeOffIcon,
  Key as KeyIcon,
  Loader as LoaderIcon,
  AlertCircle as AlertCircleIcon,
  CheckCircle as CheckCircleIcon,
  ArrowLeft as ArrowLeftIcon,
  ShieldCheck as ShieldCheckIcon,
  Headphones as HeadphonesIcon
} from 'lucide-vue-next'
import dbizLogo from '@/assets/dbizlogodark.png'

const router = useRouter()

const form = ref({
  username: '',
  newPassword: '',
  confirmPassword: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const handleResetPassword = async () => {
  if (!form.value.username || !form.value.newPassword || !form.value.confirmPassword) {
    error.value = 'Vui lòng nhập đầy đủ thông tin'
    return
  }
  
  if (form.value.newPassword !== form.value.confirmPassword) {
    error.value = 'Mật khẩu xác nhận không khớp'
    return
  }
  
  if (form.value.newPassword.length < 8) {
    error.value = 'Mật khẩu phải có ít nhất 8 ký tự'
    return
  }
  
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    // Gọi API bằng frappe-ui
    const response = await createResource({ url: 'dbiz_ai_agent.api.auth.reset_password', params: {
      user: form.value.username.trim(),
      new_password: form.value.newPassword
    }, method: 'POST' }).fetch()

    if (!response?.exc) {
      success.value = 'Mật khẩu đã được đặt lại thành công! Đang chuyển hướng...'
      // Redirect to login sau 2 giây
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      // Xử lý các loại lỗi khác nhau
      let errorMessage = 'Đặt lại mật khẩu thất bại'
      if (response.exc_type === 'ValidationError') {
        errorMessage = 'Thông tin không hợp lệ'
      } else if (response.message) {
        errorMessage = response.message
      } else if (response.exc) {
        errorMessage = response.exc
      }
      error.value = errorMessage
    }
    
  } catch (err) {
    console.error('Reset password error:', err)
    let errorMessage = 'Có lỗi xảy ra, vui lòng thử lại'
    
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      errorMessage = 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.'
    }
    
    error.value = errorMessage
  } finally {
    loading.value = false
  }
}
</script>
