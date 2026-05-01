<template>
  <div class="h-screen relative flex overflow-hidden">
    <!-- Background Image with Overlay -->
    <div class="absolute inset-0 z-0">
      <img :src="loginBackground" alt="Background" class="w-full h-full object-cover" />
      <div class="absolute inset-0 bg-gradient-to-br from-slate-900/70 via-blue-900/60 to-indigo-900/70"></div>
      <!-- Overlay to hide binary code and small logo at top-left -->
      <div class="absolute top-0 left-0 w-96 h-32 bg-gradient-to-br from-slate-900 via-slate-900/95 to-transparent"></div>
    </div>

    <!-- Left Side - Login Form -->
    <div class="relative z-10 flex-1 flex items-center justify-center py-8 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full">
        <!-- Login Form with Logo inside - Transparent Background -->
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-6 border border-white/20 ring-1 ring-white/10">
          <!-- Logo DBIZ inside the form - Larger and centered -->
          <div class="text-center mb-4">
            <img :src="dbizLogo" alt="DBIZ Autonomous Logo" class="w-40 h-40 mx-auto object-contain drop-shadow-2xl filter brightness-0 invert" />
          </div>
          
          <form @submit.prevent="handleLogin" class="space-y-4">
            <div v-if="error" class="bg-red-500/20 backdrop-blur-sm border border-red-400/50 text-red-200 px-4 py-3 rounded-lg flex items-center animate-pulse shadow-sm">
              <AlertCircleIcon class="w-5 h-5 mr-2 flex-shrink-0" />
              <span class="text-sm">{{ error }}</span>
            </div>
            
            <div class="space-y-3">
              <div>
                <label for="username" class="block text-sm font-semibold text-blue-100 mb-1.5 drop-shadow">{{ $t('login.form.username') }}</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <MailIcon class="h-5 w-5 text-blue-300" />
                  </div>
                  <input
                    id="username"
                    v-model="form.email"
                    type="text"
                    required
                    class="block w-full pl-10 pr-3 py-2.5 border border-white/30 rounded-xl shadow-sm placeholder-blue-200 bg-white/20 backdrop-blur-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 transition-all"
                    :placeholder="$t('login.form.usernamePlaceholder')"
                  />
                </div>
              </div>
              
              <div>
                <label for="password" class="block text-sm font-semibold text-blue-100 mb-1.5 drop-shadow">{{ $t('login.form.password') }}</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <LockIcon class="h-5 w-5 text-blue-300" />
                  </div>
                  <input
                    id="password"
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    class="block w-full pl-10 pr-12 py-2.5 border border-white/30 rounded-xl shadow-sm placeholder-blue-200 bg-white/20 backdrop-blur-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 transition-all"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    <EyeIcon v-if="!showPassword" class="h-5 w-5 text-blue-300 hover:text-blue-200 transition-colors" />
                    <EyeOffIcon v-else class="h-5 w-5 text-blue-300 hover:text-blue-200 transition-colors" />
                  </button>
                </div>
              </div>
            </div>
            
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <input
                  id="remember"
                  v-model="form.remember"
                  type="checkbox"
                  class="h-4 w-4 text-cyan-400 focus:ring-cyan-400 border-white/30 rounded bg-white/20"
                />
                <label for="remember" class="ml-2 block text-sm text-blue-100 drop-shadow">{{ $t('login.form.rememberLogin') }}</label>
              </div>
              
              <div class="text-sm">
                <router-link to="/forgot-password" class="font-medium text-cyan-300 hover:text-cyan-200 transition-colors drop-shadow">{{ $t('login.form.forgotPassword') }}</router-link>
              </div>
            </div>
            
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-xl shadow-lg text-sm font-semibold text-white bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-700 hover:via-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] hover:shadow-xl"
            >
              <LoaderIcon v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
              <LogInIcon v-else class="w-5 h-5 mr-2" />
              {{ loading ? $t('login.form.loggingIn') : $t('login.form.login') }}
            </button>
          </form>
          
          <div class="text-center mt-4">
            <p class="text-sm text-blue-100 drop-shadow">
              Chưa có tài khoản? 
              <router-link to="/contact-admin" class="font-medium text-cyan-300 hover:text-cyan-200 transition-colors">Liên hệ quản trị viên</router-link>
            </p>
          </div>
          
          <!-- Version Info inside form -->
          <div class="flex items-center justify-center mt-3 gap-2 border-t border-white/10 pt-3">
            <p class="text-xs text-blue-200/70 drop-shadow">
              Phiên bản 1.0.0 | Powered by
            </p>
            <img :src="dbizSmallLogo" alt="DBIZ" class="h-6 object-contain drop-shadow-2xl filter brightness-0 invert" />
          </div>
        </div>
      </div>
    </div>

    <!-- Right Side - DBIZ Autonomous Features Showcase -->
    <div class="hidden lg:flex lg:flex-1 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-slate-900/20 via-blue-900/15 to-indigo-900/20"></div>
      <div class="relative z-10 flex flex-col justify-center px-12 py-12 text-white">
        <div class="max-w-lg">
          <div class="mb-6">
            <h2 class="text-3xl font-bold mb-3 bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">DBIZ Autonomous</h2>
            <div class="w-16 h-1 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full mb-3"></div>
            <p class="text-lg text-blue-100 leading-relaxed">
              Nền tảng AI tự động hóa toàn diện với khả năng xử lý ngôn ngữ tự nhiên, 
              nhận dạng văn bản và tự động hóa quy trình kinh doanh.
            </p>
          </div>
          
          <div class="space-y-4">
            <!-- Chatbot AI -->
            <div class="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10 shadow-lg hover:bg-white/10 transition-all duration-300">
              <div class="flex items-start space-x-3">
                <div class="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg">
                  <MessageSquareIcon class="w-6 h-6" />
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-bold mb-1 text-cyan-100">Chatbot AI Thông minh</h3>
                  <p class="text-blue-100 text-xs leading-relaxed">
                    AI Assistant với khả năng hiểu ngữ cảnh, trả lời tự nhiên và học hỏi từ dữ liệu doanh nghiệp
                  </p>
                </div>
              </div>
            </div>
            
            <!-- OCR & Document Processing -->
            <div class="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10 shadow-lg hover:bg-white/10 transition-all duration-300">
              <div class="flex items-start space-x-3">
                <div class="w-12 h-12 bg-gradient-to-br from-emerald-400 to-green-600 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg">
                  <ScanTextIcon class="w-6 h-6" />
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-bold mb-1 text-emerald-100">OCR - Nhập liệu tự động</h3>
                  <p class="text-blue-100 text-xs leading-relaxed">
                    Nhận dạng và trích xuất văn bản từ hình ảnh, PDF với độ chính xác cao, tự động hóa quy trình nhập liệu
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Knowledge Management -->
            <div class="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10 shadow-lg hover:bg-white/10 transition-all duration-300">
              <div class="flex items-start space-x-3">
                <div class="w-12 h-12 bg-gradient-to-br from-purple-400 to-violet-600 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg">
                  <BookOpenIcon class="w-6 h-6" />
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-bold mb-1 text-purple-100">Quản lý Tri thức</h3>
                  <p class="text-blue-100 text-xs leading-relaxed">
                    Tích hợp, phân loại và tìm kiếm thông minh trong kho tài liệu doanh nghiệp
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Security & Enterprise -->
            <div class="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10 shadow-lg hover:bg-white/10 transition-all duration-300">
              <div class="flex items-start space-x-3">
                <div class="w-12 h-12 bg-gradient-to-br from-orange-400 to-red-500 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg">
                  <ShieldIcon class="w-6 h-6" />
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-bold mb-1 text-orange-100">Bảo mật Enterprise</h3>
                  <p class="text-blue-100 text-xs leading-relaxed">
                    Hệ thống bảo mật đa lớp, tuân thủ tiêu chuẩn quốc tế, đảm bảo an toàn dữ liệu
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Decorative Elements -->
      <div class="absolute top-20 right-20 w-32 h-32 bg-cyan-400/20 rounded-full blur-xl animate-pulse"></div>
      <div class="absolute bottom-20 left-20 w-24 h-24 bg-blue-400/20 rounded-full blur-lg animate-pulse" style="animation-delay: 1s;"></div>
      <div class="absolute top-1/2 right-10 w-16 h-16 bg-indigo-400/20 rounded-full blur-md animate-pulse" style="animation-delay: 2s;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Mail as MailIcon,
  Lock as LockIcon,
  Eye as EyeIcon,
  EyeOff as EyeOffIcon,
  LogIn as LogInIcon,
  Loader as LoaderIcon,
  AlertCircle as AlertCircleIcon,
  MessageSquare as MessageSquareIcon,
  BookOpen as BookOpenIcon,
  Shield as ShieldIcon,
  ScanText as ScanTextIcon
} from 'lucide-vue-next'
import dbizLogo from '@/assets/dbizlogodark.png'
import dbizSmallLogo from '@/assets/dbiz.png'
import loginBackground from '@/assets/loginbackground.png'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  remember: false
})

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const handleLogin = async () => {
  if (!form.value.email || !form.value.password) {
    error.value = 'Vui lòng nhập đầy đủ thông tin đăng nhập'
    return
  }
  
  // Trim whitespace from username/email
  form.value.email = form.value.email.trim()
  
  loading.value = true
  error.value = ''
  
  try {
    const result = await authStore.login(form.value.email, form.value.password)
    
    if (result.success) {
      router.push('/')
    } else {
      error.value = result.error || 'Đăng nhập thất bại'
    }
  } catch (err) {
    error.value = 'Có lỗi xảy ra, vui lòng thử lại'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}
</script>
