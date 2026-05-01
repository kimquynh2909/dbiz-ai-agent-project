<template>
  <div class="max-w-4xl mx-auto">
    <div class="bg-white rounded-2xl p-8 text-center max-w-2xl mx-auto mt-8 shadow-lg border border-gray-100">
      <div class="w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
        <img :src="avatarImage" alt="Ms.Sunny" class="w-12 h-12 object-contain" />
      </div>
      <h3 class="text-2xl font-bold text-gray-900 mb-3">{{ greetingMessage }}</h3>
      <p class="text-gray-600 mb-6 text-base">{{ description }}</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-6">
        <button v-for="question in quickQuestions" :key="question.question_text"
                @click="emit('selectQuestion', question.question_text)"
                class="group p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl hover:from-blue-50 hover:to-blue-100 hover:border-blue-300 border border-gray-200 transition-all duration-200 text-left transform hover:scale-105 shadow-sm hover:shadow-md">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
              <component :is="getIconComponent(question.icon)" class="w-4 h-4 text-blue-600" />
            </div>
            <p class="text-sm font-medium text-gray-800 group-hover:text-blue-700">{{ question.question_text }}</p>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// import các icon dùng cho câu hỏi nhanh
import { 
  Key as KeyIcon,
  Download as DownloadIcon,
  Server as ServerIcon,
  Mail as MailIcon,
  MessageSquare as MessageSquareIcon,
  HelpCircle as HelpCircleIcon
} from 'lucide-vue-next'

// props cho welcome message
const props = defineProps({
  greetingMessage: { type: String, required: true }, // lời chào
  description: { type: String, required: true }, // mô tả
  avatarImage: { type: String, required: true }, // ảnh đại diện
  quickQuestions: { type: Array, default: () => [] } // danh sách câu hỏi nhanh
})

// emit sự kiện chọn câu hỏi
const emit = defineEmits(['selectQuestion'])

// hàm lấy icon cho từng câu hỏi
const getIconComponent = (iconName) => {
  const iconMap = {
    'Key': KeyIcon,
    'Download': DownloadIcon,
    'Server': ServerIcon,
    'Mail': MailIcon,
    'MessageSquare': MessageSquareIcon,
    'HelpCircle': HelpCircleIcon
  }
  return iconMap[iconName] || MessageSquareIcon
}
</script>
