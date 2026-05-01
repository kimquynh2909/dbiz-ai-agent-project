<template>
  <div>
    <div
      v-for="message in messages"
      :key="message.id"
      :class="['flex', message.role === 'user' ? 'justify-end' : 'justify-start', 'mb-3']"
    >
      <div
        v-if="message.role === 'user'"
        :class="[compact ? 'max-w-full' : 'max-w-2xl', 'bg-gray-100 text-gray-800 rounded-2xl px-6 py-4 shadow-sm']"
      >
        <div class="flex items-center space-x-2 mb-2">
          <span class="text-sm font-medium text-gray-600">Bạn</span>
          <span class="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded-full">
            {{ formatTime(message.timestamp) }}
          </span>
        </div>
        <p class="text-base leading-relaxed">{{ message.content }}</p>
      </div>

      <div v-else-if="message.role === 'assistant'" :class="[compact ? 'max-w-full' : 'max-w-4xl']">
        <div class="flex items-start" :class="avatarImage ? 'space-x-4' : ''">
          <div
            v-if="avatarImage"
            class="w-12 h-12 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg"
          >
            <img :src="avatarImage" alt="Ms.Sunny" class="w-8 h-8 object-contain" />
          </div>
          <div
            :class="[
              'bg-white border border-gray-200 rounded-2xl px-6 py-4 shadow-sm flex-1',
              message.is_streaming ? 'streaming-message' : '',
            ]"
          >
            <div class="flex items-center space-x-3 mb-3">
              <span class="text-lg font-semibold text-gray-800">AI Agent</span>
              <span class="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                {{ formatTime(message.timestamp) }}
              </span>
              <span
                v-if="message.streaming || message.is_streaming"
                class="text-xs text-blue-500 bg-blue-100 px-3 py-1 rounded-full animate-pulse"
              >
                {{ $t('chat.responding') }}
              </span>
            </div>
            <div class="text-base text-gray-800 prose prose-base max-w-none leading-relaxed">
              <div v-if="message.streaming && !message.content" class="flex items-center space-x-2 text-gray-500">
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                <span class="text-sm">{{ $t('chat.generatingResponse') }}</span>
              </div>
              <!-- Chart rendering -->
              <div v-else-if="hasChartData(message)" class="chart-message-container">
                <div v-if="getChartTextMessage(message)" v-html="getChartTextMessage(message)" class="chart-text-message mb-4"></div>
                <ChatChart
                  v-if="getChartData(message)"
                  :chart-type="getChartData(message).chartData.chartType"
                  :title="getChartData(message).chartData.title"
                  :data="getChartData(message).chartData.data"
                  :options="getChartData(message).chartData.options"
                  :summary="getChartData(message).chartData.summary"
                />
              </div>
              <!-- Regular message rendering -->
              <div v-else-if="message.content">
                <div v-html="formattedContent(message)"></div>
                <span v-if="message.streaming" class="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1"></span>
              </div>
              <div v-else class="flex items-center space-x-2 text-gray-500">
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                <span class="text-sm">{{ $t('chat.generatingResponse') }}</span>
              </div>
            </div>

            <div v-if="!message.feedback" class="mt-4 pt-4 border-t border-gray-100 flex items-center space-x-4">
              <span class="text-sm text-gray-500">{{ $t('chat.feedback.helpful') }}</span>
              <div class="flex items-center space-x-2">
                <button
                  @click="emit('feedback', message.id, true)"
                  class="p-2 hover:bg-green-50 rounded-lg transition-colors"
                >
                  <ThumbsUpIcon class="w-5 h-5 text-gray-400 hover:text-green-600" />
                </button>
                <button
                  @click="emit('feedback', message.id, false)"
                  class="p-2 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <ThumbsDownIcon class="w-5 h-5 text-gray-400 hover:text-red-600" />
                </button>
                <button class="p-2 hover:bg-gray-50 rounded-lg transition-colors">
                  <svg
                    class="w-5 h-5 text-gray-400 hover:text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </button>
                <button class="p-2 hover:bg-gray-50 rounded-lg transition-colors">
                  <svg
                    class="w-5 h-5 text-gray-400 hover:text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  </svg>
                </button>
                <button class="p-2 hover:bg-gray-50 rounded-lg transition-colors">
                  <svg
                    class="w-5 h-5 text-gray-400 hover:text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                </button>
                <button class="p-2 hover:bg-gray-50 rounded-lg transition-colors">
                  <svg
                    class="w-5 h-5 text-gray-400 hover:text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </div>
            <div v-else class="mt-4 pt-4 border-t border-gray-100">
              <span class="text-sm text-green-600">{{ $t('chat.feedback.thanks') }}</span>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else-if="message.role === 'error'"
        :class="[
          compact ? 'max-w-full' : 'max-w-2xl',
          'bg-red-50 border border-red-200 text-red-700 rounded-2xl px-6 py-4',
        ]"
      >
        <p class="text-base">{{ message.content }}</p>
      </div>
    </div>

    <div v-if="isThinking" class="flex justify-start">
      <div class="flex items-start space-x-3">
        <div
          v-if="avatarImage"
          class="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center shadow-md"
        >
          <img :src="avatarImage" alt="AI" class="w-8 h-8 object-contain animate-pulse" />
        </div>
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-2xl px-4 py-3 shadow-sm">
          <div class="flex items-center space-x-2 mb-2">
            <span class="text-sm font-semibold text-blue-700">AI Agent</span>
            <span class="text-xs text-gray-500 bg-white px-2 py-1 rounded-full">{{ $t('chat.thinking') }}</span>
          </div>
          <div class="flex space-x-2">
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ThumbsUp as ThumbsUpIcon, ThumbsDown as ThumbsDownIcon } from 'lucide-vue-next'
import ChatChart from './ChatChart.vue'
import { parseChartData, formatChartMessage } from '@/utils/chartParser'

const props = defineProps({
  messages: {
    type: Array,
    required: true,
  },
  compact: {
    type: Boolean,
    default: false,
  },
  isThinking: {
    type: Boolean,
    default: false,
  },
  avatarImage: {
    type: String,
    required: true,
  },
  formatMessage: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits(['feedback', 'imageClick'])

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Check if message contains chart data and extract it
 */
const getChartData = (message) => {
  if (!message?.content) return null
  return parseChartData(message.content)
}

/**
 * Get formatted text message for chart responses
 */
const getChartTextMessage = (message) => {
  const chartResult = getChartData(message)
  if (chartResult?.textMessage) {
    return formatChartMessage(chartResult.textMessage)
  }
  return ''
}

/**
 * Check if message has chart data
 */
const hasChartData = (message) => {
  return getChartData(message) !== null
}

const formattedContent = (message) => {
  // If message contains chart data, don't format as regular markdown
  if (hasChartData(message)) {
    return ''
  }
  return props.formatMessage(message)
}
</script>

<style scoped>
.prose {
  max-width: none;
}
.prose p {
  margin: 0.5em 0;
}
.prose ul {
  margin: 0.5em 0;
  padding-left: 1.5em;
}
.prose li {
  margin: 0.25em 0;
}
.prose code {
  background: #f3f4f6;
  padding: 0.125em 0.25em;
  border-radius: 0.25em;
  font-size: 0.875em;
}
.prose pre {
  background: #1f2937;
  color: #f3f4f6;
  padding: 1em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin: 0.5em 0;
}
:deep(.chat-inline-image) {
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
:deep(.chat-inline-image__img) {
  max-width: 100%;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
  cursor: zoom-in;
  transition: transform 0.2s ease;
}
:deep(.chat-inline-image__img:hover) {
  transform: scale(1.01);
}

/* Streaming animation */
.streaming-message {
  position: relative;
}

.streaming-message::after {
  content: '';
  position: absolute;
  top: 12px;
  right: 12px;
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  animation: pulse-dot 1.5s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* Chart message styles */
.chart-message-container {
  width: 100%;
}

.chart-text-message {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #374151;
}

.chart-text-message :deep(strong) {
  color: #1f2937;
  font-weight: 600;
}
</style>
