<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex">
    <!-- Left Side - Contact Form -->
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
              Liên hệ quản trị viên
            </h1>
            <p class="text-lg text-gray-600 font-medium">Chúng tôi sẵn sàng hỗ trợ bạn</p>
            <p class="text-sm text-gray-500">Để lại thông tin, chúng tôi sẽ liên hệ sớm nhất</p>
          </div>
        </div>
      
        <!-- Contact Form -->
        <div class="bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/30">
          <form @submit.prevent="handleSubmitContact" class="space-y-6">
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
                <label for="fullName" class="block text-sm font-semibold text-gray-700 mb-2">Họ và tên *</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <UserIcon class="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="fullName"
                    v-model="form.fullName"
                    type="text"
                    required
                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Nguyễn Văn A"
                  />
                </div>
              </div>
              
              <div>
                <label for="email" class="block text-sm font-semibold text-gray-700 mb-2">Email *</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <MailIcon class="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    v-model="form.email"
                    type="email"
                    required
                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="example@company.com"
                  />
                </div>
              </div>

              <div>
                <label for="phone" class="block text-sm font-semibold text-gray-700 mb-2">Số điện thoại *</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <PhoneIcon class="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="phone"
                    v-model="form.phone"
                    type="tel"
                    required
                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="0123 456 789"
                  />
                </div>
              </div>

              <div>
                <label for="company" class="block text-sm font-semibold text-gray-700 mb-2">Công ty/Tổ chức</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <BuildingIcon class="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="company"
                    v-model="form.company"
                    type="text"
                    class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Tên công ty"
                  />
                </div>
              </div>

              <div>
                <label for="subject" class="block text-sm font-semibold text-gray-700 mb-2">Chủ đề *</label>
                <select
                  id="subject"
                  v-model="form.subject"
                  required
                  class="block w-full px-3 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                >
                  <option value="">Chọn chủ đề</option>
                  <option value="account_access">Truy cập tài khoản</option>
                  <option value="password_reset">Đặt lại mật khẩu</option>
                  <option value="technical_support">Hỗ trợ kỹ thuật</option>
                  <option value="product_demo">Demo sản phẩm</option>
                  <option value="business_inquiry">Tư vấn kinh doanh</option>
                  <option value="other">Khác</option>
                </select>
              </div>

              <div>
                <label for="message" class="block text-sm font-semibold text-gray-700 mb-2">Nội dung *</label>
                <textarea
                  id="message"
                  v-model="form.message"
                  required
                  rows="4"
                  class="block w-full px-3 py-3 border border-gray-300 rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
                  placeholder="Mô tả chi tiết vấn đề hoặc yêu cầu hỗ trợ của bạn..."
                ></textarea>
              </div>
            </div>
            
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02]"
            >
              <LoaderIcon v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
              <SendIcon v-else class="w-5 h-5 mr-2" />
              {{ loading ? 'Đang gửi...' : 'Gửi yêu cầu' }}
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
        </div>
      </div>
    </div>

    <!-- Right Side - Contact Information -->
    <div class="hidden lg:flex lg:flex-1 bg-gradient-to-br from-purple-600 via-pink-700 to-red-800 relative overflow-hidden">
      <div class="absolute inset-0 bg-black/20"></div>
      <div class="relative z-10 flex flex-col justify-center px-12 py-16 text-white">
        <div class="max-w-lg">
          <div class="mb-8">
            <h2 class="text-4xl font-bold mb-4">Hỗ trợ khách hàng</h2>
            <div class="w-16 h-1 bg-gradient-to-r from-pink-400 to-red-500 rounded-full mb-4"></div>
            <p class="text-xl text-pink-100 leading-relaxed">
              Đội ngũ chuyên gia của DBIZ Autonomous luôn sẵn sàng hỗ trợ bạn 24/7.
            </p>
          </div>
          
          <div class="space-y-6">
            <!-- Hotline -->
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div class="flex items-start space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-green-400 to-green-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  <PhoneIcon class="w-7 h-7" />
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold mb-2">Hotline 24/7</h3>
                  <p class="text-pink-100 text-lg font-semibold mb-1">1900 1234</p>
                  <p class="text-pink-100 text-sm leading-relaxed">
                    Gọi ngay để được hỗ trợ trực tiếp từ chuyên gia
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Email Support -->
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div class="flex items-start space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  <MailIcon class="w-7 h-7" />
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold mb-2">Email hỗ trợ</h3>
                  <p class="text-pink-100 text-lg font-semibold mb-1">support@dbiz.vn</p>
                  <p class="text-pink-100 text-sm leading-relaxed">
                    Phản hồi trong vòng 2 giờ làm việc
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Office Address -->
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div class="flex items-start space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-orange-400 to-red-500 rounded-xl flex items-center justify-center flex-shrink-0">
                  <MapPinIcon class="w-7 h-7" />
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold mb-2">Văn phòng</h3>
                  <p class="text-pink-100 text-sm leading-relaxed">
                    Tầng 10, Tòa nhà ABC<br>
                    123 Đường XYZ, Quận 1<br>
                    TP. Hồ Chí Minh, Việt Nam
                  </p>
                </div>
              </div>
            </div>

            <!-- Business Hours -->
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div class="flex items-start space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  <ClockIcon class="w-7 h-7" />
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold mb-2">Giờ làm việc</h3>
                  <p class="text-pink-100 text-sm leading-relaxed">
                    Thứ 2 - Thứ 6: 8:00 - 18:00<br>
                    Thứ 7: 8:00 - 12:00<br>
                    Chủ nhật: Nghỉ
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Decorative Elements -->
      <div class="absolute top-20 right-20 w-32 h-32 bg-white/10 rounded-full blur-xl"></div>
      <div class="absolute bottom-20 left-20 w-24 h-24 bg-pink-300/20 rounded-full blur-lg"></div>
      <div class="absolute top-1/2 right-10 w-16 h-16 bg-red-300/20 rounded-full blur-md"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import { useRouter } from 'vue-router'
import {
  User as UserIcon,
  Mail as MailIcon,
  Phone as PhoneIcon,
  Building as BuildingIcon,
  Send as SendIcon,
  Loader as LoaderIcon,
  AlertCircle as AlertCircleIcon,
  CheckCircle as CheckCircleIcon,
  ArrowLeft as ArrowLeftIcon,
  MapPin as MapPinIcon,
  Clock as ClockIcon
} from 'lucide-vue-next'
import dbizLogo from '@/assets/dbizlogodark.png'

const router = useRouter()

const form = ref({
  fullName: '',
  email: '',
  phone: '',
  company: '',
  subject: '',
  message: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')

import { call, createResource } from 'frappe-ui'

const handleSubmitContact = async () => {
  if (!form.value.fullName || !form.value.email || !form.value.phone || !form.value.subject || !form.value.message) {
    error.value = 'Vui lòng nhập đầy đủ thông tin bắt buộc (*)'
    return
  }
  
  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.value.email)) {
    error.value = 'Email không hợp lệ'
    return
  }
  
  // Basic phone validation
  const phoneRegex = /^[0-9\s\-\+\(\)]{10,15}$/
  if (!phoneRegex.test(form.value.phone.replace(/\s/g, ''))) {
    error.value = 'Số điện thoại không hợp lệ'
    return
  }
  
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    // Gọi API bằng frappe-ui
    const response = await createResource({ url: 'dbiz_ai_agent.api.auth.send_contact_request', params: {
      full_name: form.value.fullName,
      email: form.value.email,
      phone: form.value.phone,
      company: form.value.company,
      subject: form.value.subject,
      message: form.value.message
    }, method: 'POST' }).fetch()

    if (!response?.exc) {
      success.value = 'Yêu cầu của bạn đã được gửi thành công! Chúng tôi sẽ liên hệ trong vòng 24h.'
      // Reset form
      form.value = {
        fullName: '',
        email: '',
        phone: '',
        company: '',
        subject: '',
        message: ''
      }
    } else {
      // Xử lý lỗi trả về
      let errorMessage = 'Gửi yêu cầu thất bại'
      if (response.message) {
        errorMessage = response.message
      } else if (response.exc) {
        errorMessage = response.exc
      }
      error.value = errorMessage
    }
    
  } catch (err) {
    console.error('Contact form error:', err)
    let errorMessage = 'Có lỗi xảy ra, vui lòng thử lại hoặc liên hệ hotline'
    
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      errorMessage = 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.'
    }
    
    error.value = errorMessage
  } finally {
    loading.value = false
  }
}
</script>
