<template>
  <div class="px-6 py-6">
    <div class="max-w-7xl mx-auto">
      <div class="space-y-8 mb-8">
        <!-- Tiêu đề -->
        <div class="text-center">
          <h3 class="text-3xl font-bold text-gray-800 mb-2">Dashboard Analytics</h3>
          <p class="text-gray-600">Tổng quan về hiệu suất và sử dụng dịch vụ</p>
        </div>

        <!-- Token Usage Overview -->
        <div class="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 rounded-3xl p-8 shadow-2xl text-white">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h4 class="text-2xl font-bold mb-2">Token Usage</h4>
              <p class="text-blue-100">Tổng token đã sử dụng trong tháng này</p>
            </div>
            <div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
              <svg class="w-9 h-9" fill="currentColor" viewBox="0 0 24 24">
                <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/20">
              <div class="text-4xl font-bold mb-2">{{ formatNumber(analyticsData.tokens.total) }}</div>
              <div class="text-blue-100 text-sm mb-3">Tổng token</div>
              <div class="flex items-center text-xs text-green-300">
                <span>+12.5% so với tháng trước</span>
              </div>
            </div>
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/20">
              <div class="text-4xl font-bold mb-2">{{ formatNumber(analyticsData.tokens.input) }}</div>
              <div class="text-blue-100 text-sm mb-3">Input tokens</div>
              <div class="w-full bg-white/20 rounded-full h-2">
                <div class="bg-green-400 h-2 rounded-full" :style="`width: ${(analyticsData.tokens.input / analyticsData.tokens.total * 100)}%`"></div>
              </div>
            </div>
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/20">
              <div class="text-4xl font-bold mb-2">{{ formatNumber(analyticsData.tokens.output) }}</div>
              <div class="text-blue-100 text-sm mb-3">Output tokens</div>
              <div class="w-full bg-white/20 rounded-full h-2">
                <div class="bg-yellow-400 h-2 rounded-full" :style="`width: ${(analyticsData.tokens.output / analyticsData.tokens.total * 100)}%`"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Service Usage Stats -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- OCR Service -->
          <div class="bg-white rounded-3xl p-8 shadow-xl border border-gray-200 hover:shadow-2xl transition-shadow">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                  </svg>
                </div>
                <div>
                  <h4 class="text-xl font-bold text-gray-800">OCR Service</h4>
                  <p class="text-gray-500 text-sm">Dịch vụ nhận dạng ký tự</p>
                </div>
              </div>
            </div>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                <div>
                  <div class="text-sm text-gray-600 mb-1">Tổng tài liệu đã xử lý</div>
                  <div class="text-3xl font-bold text-gray-800">{{ analyticsData.ocr.totalDocuments }}</div>
                </div>
                <div class="text-right">
                  <div class="text-sm text-green-600 font-semibold">+8.2%</div>
                  <div class="text-xs text-gray-500">Tuần này</div>
                </div>
              </div>
              <div class="grid grid-cols-3 gap-3">
                <div class="text-center p-3 bg-blue-50 rounded-xl">
                  <div class="text-2xl font-bold text-blue-600">{{ analyticsData.ocr.invoices }}</div>
                  <div class="text-xs text-gray-600 mt-1">Hóa đơn</div>
                </div>
                <div class="text-center p-3 bg-purple-50 rounded-xl">
                  <div class="text-2xl font-bold text-purple-600">{{ analyticsData.ocr.receipts }}</div>
                  <div class="text-xs text-gray-600 mt-1">Biên lai</div>
                </div>
                <div class="text-center p-3 bg-green-50 rounded-xl">
                  <div class="text-2xl font-bold text-green-600">{{ analyticsData.ocr.others }}</div>
                  <div class="text-xs text-gray-600 mt-1">Khác</div>
                </div>
              </div>
              <div class="pt-4 border-t border-gray-200">
                <div class="flex justify-between text-sm mb-2">
                  <span class="text-gray-600">Độ chính xác trung bình</span>
                  <span class="font-semibold text-gray-800">{{ analyticsData.ocr.accuracy }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div class="bg-gradient-to-r from-emerald-500 to-teal-600 h-3 rounded-full transition-all duration-500" :style="`width: ${analyticsData.ocr.accuracy}%`"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Chatbot AI Service -->
          <div class="bg-white rounded-3xl p-8 shadow-xl border border-gray-200 hover:shadow-2xl transition-shadow">
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center space-x-4">
                <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                  </svg>
                </div>
                <div>
                  <h4 class="text-xl font-bold text-gray-800">Chatbot AI</h4>
                  <p class="text-gray-500 text-sm">Trợ lý AI thông minh</p>
                </div>
              </div>
            </div>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                <div>
                  <div class="text-sm text-gray-600 mb-1">Tổng cuộc hội thoại</div>
                  <div class="text-3xl font-bold text-gray-800">{{ analyticsData.chatbot.totalConversations }}</div>
                </div>
                <div class="text-right">
                  <div class="text-sm text-green-600 font-semibold">+15.3%</div>
                  <div class="text-xs text-gray-500">Tuần này</div>
                </div>
              </div>
              <div class="grid grid-cols-3 gap-3">
                <div class="text-center p-3 bg-indigo-50 rounded-xl">
                  <div class="text-2xl font-bold text-indigo-600">{{ analyticsData.chatbot.messages }}</div>
                  <div class="text-xs text-gray-600 mt-1">Tin nhắn</div>
                </div>
                <div class="text-center p-3 bg-pink-50 rounded-xl">
                  <div class="text-2xl font-bold text-pink-600">{{ analyticsData.chatbot.avgResponseTime }}s</div>
                  <div class="text-xs text-gray-600 mt-1">Thời gian</div>
                </div>
                <div class="text-center p-3 bg-amber-50 rounded-xl">
                  <div class="text-2xl font-bold text-amber-600">{{ analyticsData.chatbot.satisfaction }}%</div>
                  <div class="text-xs text-gray-600 mt-1">Hài lòng</div>
                </div>
              </div>
              <div class="pt-4 border-t border-gray-200">
                <div class="flex justify-between text-sm mb-2">
                  <span class="text-gray-600">Tỷ lệ giải quyết thành công</span>
                  <span class="font-semibold text-gray-800">{{ analyticsData.chatbot.successRate }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div class="bg-gradient-to-r from-purple-500 to-pink-600 h-3 rounded-full transition-all duration-500" :style="`width: ${analyticsData.chatbot.successRate}%`"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- User Activity Stats -->
        <div class="bg-white rounded-3xl p-8 shadow-xl border border-gray-200">
          <div class="flex items-center justify-between mb-8">
            <div>
              <h4 class="text-2xl font-bold text-gray-800 mb-2">Hoạt động người dùng</h4>
              <p class="text-gray-600">Thống kê hoạt động của người dùng hệ thống</p>
            </div>
            <div class="flex space-x-3">
              <button class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors">
                Hôm nay
              </button>
              <button class="px-4 py-2 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">
                Tuần này
              </button>
              <button class="px-4 py-2 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">
                Tháng này
              </button>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl border border-blue-200">
              <div class="w-12 h-12 bg-blue-500 rounded-xl mx-auto mb-3 flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </div>
              <div class="text-3xl font-bold text-gray-800 mb-1">{{ analyticsData.users.total }}</div>
              <div class="text-sm text-gray-600">Tổng người dùng</div>
            </div>
            
            <div class="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-2xl border border-green-200">
              <div class="w-12 h-12 bg-green-500 rounded-xl mx-auto mb-3 flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="text-3xl font-bold text-gray-800 mb-1">{{ analyticsData.users.active }}</div>
              <div class="text-sm text-gray-600">Đang hoạt động</div>
            </div>
            
            <div class="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl border border-purple-200">
              <div class="w-12 h-12 bg-purple-500 rounded-xl mx-auto mb-3 flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M7 11.5a.5.5 0 01.5-.5h9a.5.5 0 010 1h-9a.5.5 0 01-.5-.5zM7 8a.5.5 0 01.5-.5h9a.5.5 0 010 1h-9A.5.5 0 017 8zm-.5 7a.5.5 0 000 1h9a.5.5 0 000-1h-9z"/>
                </svg>
              </div>
              <div class="text-3xl font-bold text-gray-800 mb-1">{{ formatNumber(analyticsData.users.avgUsagePerUser) }}</div>
              <div class="text-sm text-gray-600">Sử dụng/người dùng</div>
            </div>
            
            <div class="text-center p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl border border-orange-200">
              <div class="w-12 h-12 bg-orange-500 rounded-xl mx-auto mb-3 flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="text-3xl font-bold text-gray-800 mb-1">{{ analyticsData.users.avgSessionTime }}m</div>
              <div class="text-sm text-gray-600">Thời gian trung bình</div>
            </div>
          </div>

          <!-- Top Users Table -->
          <div class="bg-gray-50 rounded-2xl p-6">
            <h5 class="text-lg font-semibold text-gray-800 mb-4">Top người dùng hoạt động</h5>
            <div class="space-y-3">
              <div v-for="(user, index) in analyticsData.topUsers" :key="index"
                   class="flex items-center justify-between p-4 bg-white rounded-xl hover:shadow-md transition-shadow">
                <div class="flex items-center space-x-4">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-bold"
                       :class="[
                         index === 0 ? 'from-yellow-400 to-yellow-600' : '',
                         index === 1 ? 'from-gray-400 to-gray-600' : '',
                         index === 2 ? 'from-orange-400 to-orange-600' : '',
                         index > 2 ? 'from-blue-400 to-blue-600' : ''
                       ]">
                    {{ index + 1 }}
                  </div>
                  <div>
                    <div class="font-semibold text-gray-800">{{ user.name }}</div>
                    <div class="text-sm text-gray-500">{{ user.email }}</div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="font-semibold text-gray-800">{{ user.usage }} lần</div>
                  <div class="text-sm text-gray-500">{{ user.tokens }} tokens</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Analytics Data
const analyticsData = ref({
  tokens: {
    total: 1245678,
    input: 823451,
    output: 422227
  },
  ocr: {
    totalDocuments: 1456,
    invoices: 586,
    receipts: 432,
    others: 438,
    accuracy: 96.8
  },
  chatbot: {
    totalConversations: 892,
    messages: 5634,
    avgResponseTime: 1.8,
    satisfaction: 94,
    successRate: 91.5
  },
  users: {
    total: 234,
    active: 89,
    avgUsagePerUser: 42,
    avgSessionTime: 18
  },
  topUsers: [
    {
      name: 'Nguyễn Văn A',
      email: 'nguyenvana@example.com',
      usage: 156,
      tokens: '45.2K'
    },
    {
      name: 'Trần Thị B',
      email: 'tranthib@example.com',
      usage: 142,
      tokens: '38.9K'
    },
    {
      name: 'Lê Văn C',
      email: 'levanc@example.com',
      usage: 128,
      tokens: '32.1K'
    },
    {
      name: 'Phạm Thị D',
      email: 'phamthid@example.com',
      usage: 115,
      tokens: '28.5K'
    },
    {
      name: 'Hoàng Văn E',
      email: 'hoangvane@example.com',
      usage: 98,
      tokens: '24.3K'
    }
  ]
})

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
</script>
