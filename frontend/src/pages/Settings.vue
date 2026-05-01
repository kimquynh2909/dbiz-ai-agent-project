<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-600 via-indigo-700 to-purple-800 rounded-2xl p-8 text-white relative overflow-hidden">
      <div class="absolute inset-0 bg-black/10"></div>
      <div class="relative z-10">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">{{ $t('settings.title') }}</h1>
            <p class="text-blue-200 text-lg mt-2">{{ $t('settings.subtitle') }}</p>
          </div>
          <div class="flex items-center space-x-4">
            <button
              @click="testConnection"
              :disabled="!settings.ai.openai_api_key || testing"
              class="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 backdrop-blur-sm border border-white/20"
            >
              <WifiIcon v-if="!testing" class="w-4 h-4" />
              <LoaderIcon v-else class="w-4 h-4 animate-spin" />
              <span>{{ testing ? $t('settings.testing') : $t('settings.testConnection') }}</span>
            </button>
            <button
              @click="resetToDefaults"
              class="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 flex items-center space-x-2 backdrop-blur-sm border border-white/20"
            >
              <RotateCcwIcon class="w-4 h-4" />
              <span>{{ $t('settings.resetDefaults') }}</span>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Decorative elements -->
      <div class="absolute top-10 right-10 w-32 h-32 bg-white/5 rounded-full blur-xl"></div>
      <div class="absolute bottom-10 left-10 w-24 h-24 bg-purple-300/10 rounded-full blur-lg"></div>
    </div>

    <!-- Settings Tabs -->
    <div class="bg-white rounded-2xl shadow-sm">
      <!-- Tab Navigation -->
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8 px-6">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <component :is="tab.icon" class="w-5 h-5 mr-2 inline" />
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="p-8">
        <!-- General Settings -->
        <div v-if="activeTab === 'general'" class="space-y-8">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <SettingsIcon class="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">{{ $t('settings.general.title') }}</h3>
              <p class="text-gray-600">{{ $t('settings.general.subtitle') }}</p>
            </div>
          </div>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-3">
                  {{ $t('settings.general.systemName') }}
                </label>
                <input
                  v-model="settings.general.system_name"
                  type="text"
                  placeholder="AI IT Assistant"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
                <p class="text-xs text-gray-500 mt-2">{{ $t('settings.general.systemNameDesc') }}</p>
              </div>
              
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-3">
                  {{ $t('settings.general.defaultLanguage') }}
                </label>
                <select
                  v-model="settings.general.language"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                >
                  <option value="vi">🇻🇳 {{ $t('settings.general.vietnamese') }}</option>
                  <option value="en">🇺🇸 English</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-3">
                  {{ $t('settings.general.interface') }}
                </label>
                <select
                  v-model="settings.general.theme"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                >
                  <option value="light">☀️ {{ $t('settings.general.themeLight') }}</option>
                  <option value="dark">🌙 {{ $t('settings.general.themeDark') }}</option>
                  <option value="auto">🔄 {{ $t('settings.general.themeAuto') }}</option>
                </select>
              </div>
            </div>
            
            <div class="space-y-6">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-3">
                  {{ $t('settings.general.timezone') }}
                </label>
                <input
                  v-model="settings.general.timezone"
                  type="text"
                  placeholder="Asia/Ho_Chi_Minh"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
              
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-3">
                  {{ $t('settings.general.dateFormat') }}
                </label>
                <select
                  v-model="settings.general.date_format"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                >
                  <option value="dd/mm/yyyy">DD/MM/YYYY</option>
                  <option value="mm/dd/yyyy">MM/DD/YYYY</option>
                  <option value="yyyy-mm-dd">YYYY-MM-DD</option>
                </select>
              </div>
              
              <!-- System Info Card -->
              <div class="bg-gray-50 rounded-xl p-4 border">
                <h4 class="font-semibold text-gray-900 mb-3">{{ $t('settings.general.systemInfo') }}</h4>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">{{ $t('settings.general.site') }}:</span>
                    <span class="font-medium">{{ systemInfo.site || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">{{ $t('settings.general.frappe') }}:</span>
                    <span class="font-medium">{{ systemInfo.frappe_version || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">{{ $t('settings.general.database') }}:</span>
                    <span class="font-medium">{{ systemInfo.database || 'MariaDB' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Configuration -->
        <div v-if="activeTab === 'ai'" class="space-y-8">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <BrainIcon class="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">{{ $t('settings.ai.title') }}</h3>
              <p class="text-gray-600">{{ $t('settings.ai.subtitle') }}</p>
            </div>
          </div>
          
          <!-- API Key Section -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
            <div class="flex items-center space-x-3 mb-4">
              <KeyIcon class="w-6 h-6 text-blue-600" />
              <h4 class="text-lg font-semibold text-gray-900">{{ $t('settings.ai.openaiApiKey') }}</h4>
            </div>
            <div class="relative">
              <input
                v-model="settings.ai.openai_api_key"
                :type="showApiKey ? 'text' : 'password'"
                placeholder="sk-..."
                class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <button
                @click="showApiKey = !showApiKey"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <EyeIcon v-if="!showApiKey" class="w-5 h-5" />
                <EyeOffIcon v-else class="w-5 h-5" />
              </button>
            </div>
            <p class="text-sm text-blue-700 mt-2">
              <InfoIcon class="w-4 h-4 inline mr-1" />
              {{ $t('settings.ai.apiKeyDesc') }} 
              <a href="https://platform.openai.com/api-keys" target="_blank" class="underline hover:text-blue-800">OpenAI Platform</a>
            </p>
          </div>
          
          <!-- Model Selection -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">
                Mô hình AI
              </label>
              <select
                v-model="settings.ai.model"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              >
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Nhanh, rẻ)</option>
                <option value="gpt-4">GPT-4 (Thông minh hơn)</option>
                <option value="gpt-4-turbo">GPT-4 Turbo (Cân bằng)</option>
                <option value="gpt-4o">GPT-4o (Mới nhất)</option>
                <option value="gpt-4o-mini">GPT-4o Mini (Tiết kiệm)</option>
              </select>
              <p class="text-xs text-gray-500 mt-2">Chọn mô hình phù hợp với nhu cầu và ngân sách</p>
            </div>
            
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">
                Mô hình Embedding
              </label>
              <select
                v-model="settings.ai.embedding_model"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              >
                <option value="text-embedding-ada-002">text-embedding-ada-002</option>
                <option value="text-embedding-3-small">text-embedding-3-small</option>
                <option value="text-embedding-3-large">text-embedding-3-large</option>
              </select>
              <p class="text-xs text-gray-500 mt-2">Dùng để tạo vector từ văn bản</p>
            </div>
          </div>
          
          <!-- AI Parameters -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">
                Temperature: {{ settings.ai.temperature }}
              </label>
              <input
                v-model.number="settings.ai.temperature"
                type="range"
                min="0"
                max="1"
                step="0.1"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <div class="flex justify-between text-xs text-gray-500 mt-2">
                <span>Chính xác (0)</span>
                <span>Sáng tạo (1)</span>
              </div>
              <p class="text-xs text-gray-500 mt-2">Điều chỉnh độ sáng tạo của AI (0 = chính xác, 1 = sáng tạo)</p>
            </div>
            
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">
                Max Tokens
              </label>
              <input
                v-model.number="settings.ai.max_tokens"
                type="number"
                min="100"
                max="4000"
                step="100"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <p class="text-xs text-gray-500 mt-2">Số lượng token tối đa cho mỗi phản hồi</p>
            </div>
            
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">
                Context Window
              </label>
              <input
                v-model.number="settings.ai.context_window"
                type="number"
                min="1"
                max="10"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <p class="text-xs text-gray-500 mt-2">Số lượng tin nhắn lịch sử để gửi cùng với câu hỏi</p>
            </div>
          </div>
        </div>

        <!-- RAG Configuration -->
        <div v-if="activeTab === 'rag'" class="space-y-8">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <DatabaseIcon class="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Cấu hình RAG</h3>
              <p class="text-gray-600">Thiết lập Retrieval-Augmented Generation</p>
            </div>
          </div>
          
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">
                Chunk Size
              </label>
              <input
                v-model.number="settings.rag.chunk_size"
                type="number"
                min="500"
                max="2000"
                step="100"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <p class="text-xs text-gray-500 mt-2">Kích thước mỗi đoạn văn bản (ký tự)</p>
            </div>
            
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">
                Chunk Overlap
              </label>
              <input
                v-model.number="settings.rag.chunk_overlap"
                type="number"
                min="50"
                max="500"
                step="50"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <p class="text-xs text-gray-500 mt-2">Số ký tự chồng lấp giữa các chunk</p>
            </div>
            
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">
                Retrieval Documents
              </label>
              <input
                v-model.number="settings.rag.retrieval_docs"
                type="number"
                min="1"
                max="10"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <p class="text-xs text-gray-500 mt-2">Số tài liệu tìm kiếm để trả lời câu hỏi</p>
            </div>
          </div>
          
          <!-- RAG Explanation -->
          <div class="bg-green-50 rounded-xl p-6 border border-green-200">
            <h4 class="font-semibold text-green-900 mb-3">
              <InfoIcon class="w-5 h-5 inline mr-2" />
              Giải thích về RAG
            </h4>
            <div class="text-sm text-green-800 space-y-2">
              <p><strong>Chunk Size:</strong> Kích thước mỗi đoạn văn bản khi chia nhỏ tài liệu. Lớn hơn = nhiều ngữ cảnh, nhỏ hơn = chính xác hơn.</p>
              <p><strong>Chunk Overlap:</strong> Số ký tự chồng lấp giữa các chunk để đảm bảo không mất thông tin quan trọng.</p>
              <p><strong>Retrieval Documents:</strong> Số lượng tài liệu liên quan nhất được tìm kiếm để trả lời câu hỏi.</p>
            </div>
          </div>
        </div>

        <!-- Permissions -->
        <div v-if="activeTab === 'permissions'" class="space-y-8">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <ShieldIcon class="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Phân quyền</h3>
              <p class="text-gray-600">Quản lý quyền truy cập của các vai trò</p>
            </div>
          </div>
          
          <div class="bg-orange-50 rounded-xl p-6 border border-orange-200">
            <div class="flex items-center space-x-3">
              <InfoIcon class="w-6 h-6 text-orange-600" />
              <div>
                <h4 class="font-semibold text-orange-900">Thông báo</h4>
                <p class="text-orange-800 text-sm mt-1">
                  Phân quyền được quản lý thông qua hệ thống Role của Frappe. 
                  Vui lòng truy cập <strong>Frappe Desk > Role Permission Manager</strong> để cấu hình chi tiết.
                </p>
              </div>
            </div>
          </div>
          
          <!-- Current User Permissions -->
          <div class="bg-white border border-gray-200 rounded-xl p-6">
            <h4 class="font-semibold text-gray-900 mb-4">Quyền của bạn</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="flex items-center space-x-2">
                <CheckCircleIcon class="w-5 h-5 text-green-500" />
                <span class="text-sm text-gray-700">Xem Dashboard</span>
              </div>
              <div class="flex items-center space-x-2">
                <CheckCircleIcon class="w-5 h-5 text-green-500" />
                <span class="text-sm text-gray-700">Sử dụng Chat</span>
              </div>
              <div class="flex items-center space-x-2">
                <CheckCircleIcon class="w-5 h-5 text-green-500" />
                <span class="text-sm text-gray-700">Upload tài liệu</span>
              </div>
              <div class="flex items-center space-x-2">
                <CheckCircleIcon class="w-5 h-5 text-green-500" />
                <span class="text-sm text-gray-700">Quản lý cài đặt</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="px-8 py-6 bg-gray-50 border-t rounded-b-2xl flex justify-between items-center">
        <div class="text-sm text-gray-600">
          <ClockIcon class="w-4 h-4 inline mr-1" />
          Lần cập nhật cuối: {{ lastUpdated || 'Chưa có' }}
        </div>
        <div class="flex items-center space-x-4">
          <button
            @click="loadSettings"
            class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
          >
            <RefreshCwIcon class="w-4 h-4" />
            <span>Tải lại</span>
          </button>
          <button
            @click="saveSettings"
            :disabled="saving"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
          >
            <LoaderIcon v-if="saving" class="w-4 h-4 animate-spin" />
            <SaveIcon v-else class="w-4 h-4" />
            <span>{{ saving ? 'Đang lưu...' : 'Lưu cài đặt' }}</span>
          </button>
        </div>
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
import { ref, computed, onMounted } from 'vue'
import { call, createResource } from 'frappe-ui'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import {
  Settings as SettingsIcon,
  Brain as BrainIcon,
  Database as DatabaseIcon,
  Shield as ShieldIcon,
  Key as KeyIcon,
  Eye as EyeIcon,
  EyeOff as EyeOffIcon,
  Info as InfoIcon,
  Wifi as WifiIcon,
  RotateCcw as RotateCcwIcon,
  Loader as LoaderIcon,
  Save as SaveIcon,
  RefreshCw as RefreshCwIcon,
  Clock as ClockIcon,
  CheckCircle as CheckCircleIcon
} from 'lucide-vue-next'

// Reactive data
const activeTab = ref('general')
const saving = ref(false)
const testing = ref(false)
const showApiKey = ref(false)
const message = ref(null)
const lastUpdated = ref('')
const systemInfo = ref({})

const tabs = computed(() => [
  { id: 'general', label: t('settings.tabs.general'), icon: SettingsIcon },
  { id: 'ai', label: t('settings.tabs.ai'), icon: BrainIcon },
  { id: 'rag', label: t('settings.tabs.rag'), icon: DatabaseIcon },
  { id: 'permissions', label: t('settings.tabs.permissions'), icon: ShieldIcon }
])

const settings = ref({
  general: {
    system_name: 'AI IT Assistant',
    language: 'vi',
    theme: 'light',
    timezone: 'Asia/Ho_Chi_Minh',
    date_format: 'dd/mm/yyyy'
  },
  ai: {
    openai_api_key: '',
    model: 'gpt-4o-mini',
    embedding_model: 'text-embedding-3-small',
    temperature: 0.7,
    max_tokens: 1000,
    context_window: 5
  },
  rag: {
    chunk_size: 1000,
    chunk_overlap: 200,
    retrieval_docs: 3
  }
})

// Methods
const showMessage = (text, type = 'success') => {
  message.value = { text, type }
  setTimeout(() => {
    message.value = null
  }, 5000)
}

const loadSettings = async () => {
  try {
  const response = await createResource({ url: 'dbiz_ai_agent.api.settings.get_settings', params: {}, method: 'GET' }).fetch()
    const payload = response?.message ?? response?.data
    if (payload) {
      // payload có thể là { success, data } hoặc data trực tiếp
      if (payload.success && payload.data) {
        settings.value = { ...settings.value, ...payload.data }
      } else {
        settings.value = { ...settings.value, ...payload }
      }
      lastUpdated.value = new Date().toLocaleString('vi-VN')
    }
  } catch (error) {
    showMessage('Không thể tải cài đặt', 'error')
    console.error('Load settings error:', error)
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
  const response = await createResource({ url: 'dbiz_ai_agent.api.settings.save_settings', params: { settings_data: settings.value }, method: 'POST' }).fetch()
    const payload = response?.message ?? response?.data
    if (payload) {
      showMessage(payload.message || payload || 'Cài đặt đã được lưu thành công!', 'success')
      lastUpdated.value = new Date().toLocaleString('vi-VN')
    }
  } catch (error) {
    showMessage('Lỗi khi lưu cài đặt', 'error')
    console.error('Save settings error:', error)
  } finally {
    saving.value = false
  }
}

const testConnection = async () => {
  if (!settings.value.ai.openai_api_key) {
    showMessage('Vui lòng nhập OpenAI API Key', 'error')
    return
  }
  testing.value = true
  try {
    const response = await createResource({ url: 'dbiz_ai_agent.api.settings.test_openai_connection', params: {
      api_key: settings.value.ai.openai_api_key,
      model: settings.value.ai.model
    }, method: 'POST' }).fetch()
    const payload = response?.message ?? response?.data
    if (payload?.success || payload) {
      showMessage('Kết nối OpenAI thành công!', 'success')
    } else {
      showMessage(payload?.message || 'Kết nối thất bại', 'error')
    }
  } catch (error) {
    showMessage('Lỗi khi kiểm tra kết nối', 'error')
    console.error('Test connection error:', error)
  } finally {
    testing.value = false
  }
}

const resetToDefaults = async () => {
  if (!confirm('Bạn có chắc muốn khôi phục cài đặt mặc định? (API Key sẽ được giữ nguyên)')) return
  try {
  const response = await createResource({ url: 'dbiz_ai_agent.api.settings.reset_to_defaults', params: {}, method: 'POST' }).fetch()
    const payload = response?.message ?? response?.data
    if (payload) {
      showMessage(payload?.message || 'Đã khôi phục cài đặt mặc định', 'success')
      await loadSettings()
    }
  } catch (error) {
    showMessage('Lỗi khi khôi phục cài đặt', 'error')
    console.error('Reset settings error:', error)
  }
}

const loadSystemInfo = async () => {
  try {
  const response = await createResource({ url: 'dbiz_ai_agent.api.settings.get_system_info', params: {}, method: 'GET' }).fetch()
    const payload = response?.message ?? response?.data
    if (payload) {
      if (payload.success && payload.data) systemInfo.value = payload.data
      else systemInfo.value = payload
    }
  } catch (error) {
    console.error('Load system info error:', error)
  }
}

onMounted(() => {
  loadSettings()
  loadSystemInfo()
})
</script>

<style scoped>
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
</style>