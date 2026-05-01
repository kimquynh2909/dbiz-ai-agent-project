<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-900">Chatbot Audit Logs</h3>
      <div class="flex items-center space-x-3">
        <FilterDropdown
          :model-value="dateFilter"
          :options="dateFilterOptions"
          value-key="value"
          label-key="label"
          @update:modelValue="handleDateChange"
        />
        <FilterDropdown
          :model-value="actionFilter"
          :options="actionOptions"
          all-option-text="Tất cả hành động"
          value-key="value"
          label-key="label"
          @update:modelValue="handleActionChange"
        />
        <button
          @click="emit('export')"
          class="flex items-center px-3 py-2 text-sm text-white bg-green-600 hover:bg-green-700 rounded-lg"
        >
          <DownloadIcon class="w-4 h-4 mr-1" />
          Export
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div v-for="card in statsCards" :key="card.label" class="bg-white border border-gray-200 rounded-xl p-4">
        <div class="flex items-center">
          <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', card.iconBg]">
            <component :is="card.icon" :class="['w-5 h-5', card.iconColor]" />
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">{{ card.label }}</p>
            <p class="text-2xl font-bold text-gray-900">{{ card.value }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="bg-white border border-gray-200 rounded-xl p-8 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Đang tải audit logs...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-white border border-gray-200 rounded-xl p-8 text-center">
      <p class="text-red-600">{{ error }}</p>
      <button @click="loadLogs" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
        Thử lại
      </button>
    </div>

    <!-- Data table -->
    <div
      v-else
      class="bg-white border border-gray-200 rounded-xl relative min-w-0"
      style="max-width: 100%; height: calc(100vh - 550px); min-height: 400px; overflow-y: auto; overflow-x: hidden"
    >
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">TIMESTAMP</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">USER</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">AGENTS</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">QUERY</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                RESPONSE TIME
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">STATUS</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <template v-for="log in paginatedLogs" :key="log.id">
              <!-- Main row (Message summary) -->
              <tr
                @click="log.agents && log.agents.length > 0 ? toggleRow(log.messageId) : null"
                :class="['hover:bg-gray-50', log.agents && log.agents.length > 0 ? 'cursor-pointer' : '']"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div class="flex items-center">
                    <span v-if="log.agents && log.agents.length > 0" class="mr-2">
                      <svg
                        v-if="!isExpanded(log.messageId)"
                        class="w-4 h-4 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                      <svg v-else class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                    {{ log.timestamp }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                      <span class="text-xs font-medium text-gray-700">{{ log.user.charAt(0) }}</span>
                    </div>
                    <div class="ml-3">
                      <div class="text-sm font-medium text-gray-900">{{ log.user }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                    {{ log.agentCount || (log.agents ? log.agents.length : 1) }} agents
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-900 max-w-xs truncate" :title="log.query">
                    {{ log.query }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ log.responseTime }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                      log.status === 'Success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                    ]"
                  >
                    {{ log.status }}
                  </span>
                </td>
              </tr>

              <!-- Expanded agent details (Chi tiết hóa đơn) -->
              <tr
                v-if="isExpanded(log.messageId) && log.agents"
                v-for="agent in log.agents"
                :key="agent.id"
                class="bg-gray-50 hover:bg-gray-100 cursor-pointer"
                @click="openAgentDetail(agent)"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400 pl-12">
                  {{ agent.timestamp }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <!-- Để trống cột USER cho agent rows, chỉ hiển thị indent -->
                  <div class="pl-4 text-sm text-gray-400">↳</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'inline-flex px-2 py-1 text-xs font-semibold rounded-full cursor-pointer hover:opacity-80',
                      getAgentColor(agent.agentName),
                    ]"
                  >
                    {{ agent.agentName || 'Agent' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-600 max-w-md" :title="formatResultSummary(agent.resultSummary)">
                    <template v-if="agent.resultSummary">
                      <div class="truncate">{{ formatResultSummary(agent.resultSummary) }}</div>
                    </template>
                    <template v-else>
                      <span class="italic">{{ agent.action }} processing...</span>
                    </template>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ agent.responseTime }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                      agent.status === 'Success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                    ]"
                  >
                    {{ agent.status }}
                  </span>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <div class="flex items-center justify-between bg-white px-4 py-3 border border-gray-200 rounded-xl">
      <div class="flex items-center text-sm text-gray-700">
        <span>
          Hiển thị {{ paginationRange.start }} đến {{ paginationRange.end }} trong {{ filteredLogs.length }} kết quả
        </span>
      </div>
      <div class="flex items-center space-x-2">
        <FilterDropdown
          :model-value="itemsPerPage"
          :options="perPageOptions"
          @update:modelValue="handleItemsPerPageChange"
        />
        <div class="flex space-x-1">
          <button
            @click="goToPage(1)"
            :disabled="currentPage === 1"
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Đầu
          </button>
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Trước
          </button>
          <span class="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-lg">
            {{ currentPage }} / {{ totalPages }}
          </span>
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Sau
          </button>
          <button
            @click="goToPage(totalPages)"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cuối
          </button>
        </div>
      </div>
    </div>

    <!-- Agent Detail Modal -->
    <div
      v-if="selectedAgent"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeAgentDetail"
    >
      <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
        <!-- Modal Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <span
            :class="[
              'inline-flex px-3 py-1 text-sm font-semibold rounded-full',
              getAgentColor(selectedAgent.agentName),
            ]"
          >
            {{ selectedAgent.agentName || 'Agent' }}
          </span>
          <button @click="closeAgentDetail" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <div class="px-6 py-4 overflow-y-auto max-h-[60vh]">
          <!-- Basic Info -->
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label class="text-xs font-medium text-gray-500 uppercase">Timestamp</label>
              <p class="text-sm text-gray-900">{{ selectedAgent.timestamp }}</p>
            </div>
            <div>
              <label class="text-xs font-medium text-gray-500 uppercase">Response Time</label>
              <p class="text-sm text-gray-900">{{ selectedAgent.responseTime }}</p>
            </div>
            <div>
              <label class="text-xs font-medium text-gray-500 uppercase">Message ID</label>
              <p class="text-sm text-gray-900 font-mono">{{ selectedAgent.messageId || 'N/A' }}</p>
            </div>
            <div>
              <label class="text-xs font-medium text-gray-500 uppercase">Log ID</label>
              <p class="text-sm text-gray-900 font-mono">{{ selectedAgent.id }}</p>
            </div>
          </div>

          <!-- Query -->
          <div class="mb-6">
            <label class="text-xs font-medium text-gray-500 uppercase">Query</label>
            <p class="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg mt-1">{{ selectedAgent.query || 'N/A' }}</p>
          </div>

          <!-- Result Summary -->
          <div v-if="selectedAgent.resultSummary" class="mb-6">
            <label class="text-xs font-medium text-gray-500 uppercase">Result Summary</label>
            <div class="bg-gray-50 p-3 rounded-lg mt-1 overflow-x-auto">
              <pre class="text-xs text-gray-800 whitespace-pre-wrap">{{ formatJSON(selectedAgent.resultSummary) }}</pre>
            </div>
          </div>

          <!-- Action Type -->
          <div class="mb-6">
            <label class="text-xs font-medium text-gray-500 uppercase">Action Type</label>
            <p class="text-sm text-gray-900">{{ selectedAgent.action || 'N/A' }}</p>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <!-- Status ở bên trái -->
          <span
            :class="[
              'inline-flex px-3 py-1 text-sm font-semibold rounded-full',
              selectedAgent.status === 'Success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
            ]"
          >
            {{ selectedAgent.status }}
          </span>
          <!-- Nút Đóng ở bên phải -->
          <button
            @click="closeAgentDetail"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  Download as DownloadIcon,
  Database as DatabaseIcon,
  Shield as ShieldIcon,
  RotateCcw,
  FileText as FileTextIcon,
} from 'lucide-vue-next'
import FilterDropdown from '@/components/permissions/common/FilterDropdown.vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
  logs: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['export'])

// Loading and error states
const loading = ref(false)
const error = ref('')
const allLogs = ref([])
const expandedRows = ref(new Set()) // Track expanded message IDs
const selectedAgent = ref(null) // Agent được chọn để xem chi tiết

const dateFilter = ref('week') // Default to week instead of today
const actionFilter = ref('')
const itemsPerPage = ref(5)
const currentPage = ref(1)

const dateFilterOptions = [
  { value: 'today', label: 'Hôm nay' },
  { value: 'week', label: 'Tuần này' },
  { value: 'month', label: 'Tháng này' },
  { value: 'all', label: 'Tất cả' },
]

const actionOptions = [
  { value: 'chatbot query', label: 'Chatbot Query' },
  { value: 'document access', label: 'Document Access' },
  { value: 'vector search', label: 'Vector Search' },
  { value: 'document upload', label: 'Document Upload' },
  { value: 'permission check', label: 'Permission Check' },
  { value: 'login', label: 'Login' },
  { value: 'logout', label: 'Logout' },
  { value: 'create', label: 'Create' },
  { value: 'update', label: 'Update' },
  { value: 'delete', label: 'Delete' },
  { value: 'access', label: 'Access' },
]

const perPageOptions = [5, 10, 20, 50]

// Helper functions
const parseResponseTime = (timeString = '') => {
  const match = String(timeString).match(/([0-9]+\.?[0-9]*)/)
  return match ? Number(match[1]) : 0
}

const getActionColor = (action) => {
  const colors = {
    'Chatbot Query': 'bg-blue-100 text-blue-800',
    'Document Access': 'bg-green-100 text-green-800',
    'Vector Search': 'bg-blue-100 text-blue-800',
    'Document Upload': 'bg-orange-100 text-orange-800',
    'Permission Check': 'bg-yellow-100 text-yellow-800',
    Login: 'bg-blue-100 text-blue-800',
    Logout: 'bg-gray-100 text-gray-800',
    Create: 'bg-green-100 text-green-800',
    Update: 'bg-yellow-100 text-yellow-800',
    Delete: 'bg-red-100 text-red-800',
    Access: 'bg-blue-100 text-blue-800',
  }
  return colors[action] || 'bg-gray-100 text-gray-800'
}

// Màu riêng cho từng agent (không trùng với màu tím của tổng số agents)
const getAgentColor = (agentName) => {
  const colors = {
    IntentAnalyzer: 'bg-blue-100 text-blue-800',
    QueryGenerator: 'bg-indigo-100 text-indigo-800',
    RetrievalAgent: 'bg-cyan-100 text-cyan-800',
    'IntentAnalyzer-Critic': 'bg-orange-100 text-orange-800',
    'SynthesisAgent-Critic': 'bg-orange-100 text-orange-800',
    'SynthesisAgent-Response': 'bg-green-100 text-green-800',
    'SynthesisAgent-Clarification': 'bg-yellow-100 text-yellow-800',
    SmartOrchestrator: 'bg-pink-100 text-pink-800',
  }
  return colors[agentName] || 'bg-slate-100 text-slate-800'
}

// Format result summary for display
const formatResultSummary = (resultSummary) => {
  if (!resultSummary || typeof resultSummary !== 'object') {
    return ''
  }

  // Lấy các field quan trọng để hiển thị
  const parts = []

  // Hiển thị final_response nếu có
  if (resultSummary.final_response) {
    const truncated = resultSummary.final_response.substring(0, 100)
    return truncated + (resultSummary.final_response.length > 100 ? '...' : '')
  }

  // Hiển thị intent nếu có
  if (resultSummary.intent) {
    parts.push(`Intent: ${resultSummary.intent}`)
  }

  // Hiển thị confidence nếu có
  if (resultSummary.confidence !== undefined) {
    parts.push(`Confidence: ${(resultSummary.confidence * 100).toFixed(0)}%`)
  }

  // Hiển thị num_retrieved nếu có
  if (resultSummary.num_retrieved !== undefined) {
    parts.push(`Retrieved: ${resultSummary.num_retrieved} docs`)
  }

  // Hiển thị decision nếu có
  if (resultSummary.decision) {
    parts.push(`Decision: ${resultSummary.decision}`)
  }

  // Hiển thị reason nếu có
  if (resultSummary.reason) {
    const truncated = resultSummary.reason.substring(0, 80)
    parts.push(truncated + (resultSummary.reason.length > 80 ? '...' : ''))
  }

  // Nếu không có gì, hiển thị JSON ngắn gọn
  if (parts.length === 0) {
    const jsonStr = JSON.stringify(resultSummary)
    return jsonStr.length > 100 ? jsonStr.substring(0, 100) + '...' : jsonStr
  }

  return parts.join(' | ')
}

// Load logs from API
const loadLogs = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await createResource({
      url: 'dbiz_ai_agent.dbiz_ai_agent.doctype.chatbot_access_log.chatbot_access_log.get_audit_logs',
      params: {
        page: 1,
        page_size: 1000, // Load all for client-side filtering
        date_filter: dateFilter.value,
        action_filter: actionFilter.value,
      },
      method: 'GET',
    }).fetch()

    console.log('[AuditTab] API response:', response)

    if (response?.success && response?.logs) {
      allLogs.value = response.logs
      console.log(`[AuditTab] Loaded ${response.logs.length} logs from API`)
    } else {
      error.value = response?.error || 'Không thể tải audit logs'
      allLogs.value = []
      console.error('[AuditTab] Failed to load logs:', response)
    }
  } catch (err) {
    console.error('Error loading audit logs:', err)
    error.value = err?.message || 'Không thể tải audit logs'
    allLogs.value = []
  } finally {
    loading.value = false
  }
}

// Computed properties - backend handles all filtering
const filteredLogs = computed(() => {
  console.log(`[AuditTab] Displaying ${allLogs.value.length} logs (backend filtered)`)
  return allLogs.value
})

const totalPages = computed(() => {
  const total = Math.ceil(filteredLogs.value.length / itemsPerPage.value)
  return total > 0 ? total : 1
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredLogs.value.slice(start, start + itemsPerPage.value)
})

const paginationRange = computed(() => {
  if (!filteredLogs.value.length) return { start: 0, end: 0 }
  const start = (currentPage.value - 1) * itemsPerPage.value + 1
  const end = Math.min(start + itemsPerPage.value - 1, filteredLogs.value.length)
  return { start, end }
})

const successfulLogs = computed(() => filteredLogs.value.filter((log) => log.status === 'Success'))

const averageResponseTime = computed(() => {
  if (successfulLogs.value.length === 0) return '0s'
  const totalTime = successfulLogs.value.reduce((sum, log) => sum + parseResponseTime(log.responseTime), 0)
  const avg = totalTime / successfulLogs.value.length
  return `${avg.toFixed(1)}s`
})

const statsCards = computed(() => [
  {
    label: 'Tổng queries',
    value: filteredLogs.value.length,
    icon: DatabaseIcon,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
  },
  {
    label: 'Thành công',
    value: successfulLogs.value.length,
    icon: ShieldIcon,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
  },
  {
    label: 'Thời gian TB',
    value: averageResponseTime.value,
    icon: RotateCcw,
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600',
  },
])

watch([filteredLogs, itemsPerPage], () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = totalPages.value
  }
})

const handleDateChange = (value) => {
  dateFilter.value = value || 'today'
  currentPage.value = 1
}

const handleActionChange = (value) => {
  actionFilter.value = value || ''
  currentPage.value = 1
}

const handleItemsPerPageChange = (value) => {
  const parsed = Number(value)
  if (!Number.isFinite(parsed) || parsed <= 0) return
  itemsPerPage.value = parsed
  currentPage.value = 1
}

const goToPage = (page) => {
  const total = totalPages.value
  const target = Math.min(Math.max(page, 1), total)
  currentPage.value = target
}

const toggleRow = (messageId) => {
  if (expandedRows.value.has(messageId)) {
    expandedRows.value.delete(messageId)
  } else {
    expandedRows.value.add(messageId)
  }
}

const isExpanded = (messageId) => {
  return expandedRows.value.has(messageId)
}

// Mở modal xem chi tiết agent
const openAgentDetail = (agent) => {
  selectedAgent.value = agent
}

// Đóng modal
const closeAgentDetail = () => {
  selectedAgent.value = null
}

// Format JSON để hiển thị đẹp
const formatJSON = (obj) => {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

// Load data on mount
onMounted(() => {
  loadLogs()
})

// Reload when filters change
watch([dateFilter, actionFilter], () => {
  currentPage.value = 1
  loadLogs()
})
</script>
