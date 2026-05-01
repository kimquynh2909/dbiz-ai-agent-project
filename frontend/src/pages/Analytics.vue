<template>
  <div class="analytics-page">
    <!-- Header với Time Filters -->
    <div class="analytics-header">
      <div class="header-content">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">Phân tích & Thống kê</h1>
          <p class="text-gray-600 mt-1">Báo cáo và thống kê chi tiết về việc sử dụng AI Agent</p>
        </div>
        
        <!-- Time Filter Tabs -->
        <div class="time-filters">
          <button
            v-for="filter in timeFilters"
            :key="filter.value"
            @click="selectedTimeFilter = filter.value"
            :class="['filter-btn', { active: selectedTimeFilter === filter.value }]"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>

      <!-- View Mode Toggle & Agent Selector -->
      <div class="view-controls">
        <div class="view-mode-toggle">
          <button
            @click="viewMode = 'overview'"
            :class="['view-mode-btn', { active: viewMode === 'overview' }]"
          >
            Tổng quan
          </button>
          <button
            @click="viewMode = 'agent'"
            :class="['view-mode-btn', { active: viewMode === 'agent' }]"
          >
            Theo AI Agent
          </button>
        </div>

        <!-- Agent Selector (shown only when viewMode is 'agent') -->
        <div v-if="viewMode === 'agent'" class="agent-selector">
          <label class="text-sm font-medium text-gray-700">Chọn AI Agent:</label>
          <select v-model="selectedAgent" class="agent-select">
            <option value="">-- Tất cả AI Agents đã deployed --</option>
            <option
              v-for="agent in deployedAgents"
              :key="agent.docName"
              :value="agent.docName"
            >
              {{ agent.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Custom Date Range (if 'custom' is selected) -->
      <div v-if="selectedTimeFilter === 'custom'" class="date-range-picker">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <label class="text-sm font-medium text-gray-700">Từ ngày:</label>
            <input
              v-model="customDateRange.start"
              type="date"
              class="date-input"
            />
          </div>
          <div class="flex items-center gap-2">
            <label class="text-sm font-medium text-gray-700">Đến ngày:</label>
            <input
              v-model="customDateRange.end"
              type="date"
              class="date-input"
            />
          </div>
          <button @click="applyCustomDateRange" class="apply-btn">
            Áp dụng
          </button>
        </div>
      </div>
    </div>

    <!-- Analytics Content -->
    <div class="analytics-content">
      <!-- Summary Cards -->
      <div class="summary-grid">
        <div class="summary-card card-blue">
          <div class="card-icon">
            <MessageSquareIcon class="w-6 h-6" />
          </div>
          <div class="card-content">
            <p class="card-label">Tổng số Conversations</p>
            <p class="card-value">{{ formatNumber(analytics.totalConversations) }}</p>
            <p class="card-change positive">
              <TrendingUpIcon class="w-4 h-4" />
              +{{ analytics.conversationsGrowth }}% so với kỳ trước
            </p>
          </div>
        </div>

        <div class="summary-card card-purple">
          <div class="card-icon">
            <UsersIcon class="w-6 h-6" />
          </div>
          <div class="card-content">
            <p class="card-label">Người dùng hoạt động</p>
            <p class="card-value">{{ formatNumber(analytics.activeUsers) }}</p>
            <p class="card-change positive">
              <TrendingUpIcon class="w-4 h-4" />
              +{{ analytics.usersGrowth }}% so với kỳ trước
            </p>
          </div>
        </div>

        <div class="summary-card card-green">
          <div class="card-icon">
            <ZapIcon class="w-6 h-6" />
          </div>
          <div class="card-content">
            <p class="card-label">Tokens đã sử dụng</p>
            <p class="card-value">{{ formatNumber(analytics.totalTokens) }}</p>
            <p class="card-change negative">
              <TrendingDownIcon class="w-4 h-4" />
              {{ analytics.tokensGrowth }}% so với kỳ trước
            </p>
          </div>
        </div>

        <div class="summary-card card-orange">
          <div class="card-icon">
            <ClockIcon class="w-6 h-6" />
          </div>
          <div class="card-content">
            <p class="card-label">Thời gian phản hồi TB</p>
            <p class="card-value">{{ analytics.avgResponseTime }}s</p>
            <p class="card-change positive">
              <TrendingUpIcon class="w-4 h-4" />
              Cải thiện {{ analytics.responseTimeImprovement }}%
            </p>
          </div>
        </div>
      </div>

      <!-- Charts Row 1: Usage Trend & Service Distribution -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">Xu hướng sử dụng theo thời gian</h3>
            <select v-model="usageChartMetric" class="chart-select">
              <option value="conversations">Conversations</option>
              <option value="users">Users</option>
              <option value="tokens">Tokens</option>
            </select>
          </div>
          <div class="chart-body">
            <canvas ref="usageTrendChart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">Phân bố dịch vụ AI Agent</h3>
          </div>
          <div class="chart-body">
            <canvas ref="serviceDistributionChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Charts Row 2: Top Users & Peak Hours -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">Top người dùng hoạt động</h3>
          </div>
          <div class="chart-body">
            <div class="top-users-list">
              <div
                v-for="(user, index) in analytics.topUsers"
                :key="index"
                class="user-item"
              >
                <div class="user-rank" :class="`rank-${index + 1}`">
                  {{ index + 1 }}
                </div>
                <div class="user-info">
                  <p class="user-name">{{ user.name }}</p>
                  <p class="user-email">{{ user.email }}</p>
                </div>
                <div class="user-stats">
                  <div class="stat">
                    <span class="stat-value">{{ user.conversations }}</span>
                    <span class="stat-label">conversations</span>
                  </div>
                  <div class="stat">
                    <span class="stat-value">{{ formatNumber(user.tokens) }}</span>
                    <span class="stat-label">tokens</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">Giờ cao điểm sử dụng</h3>
          </div>
          <div class="chart-body">
            <canvas ref="peakHoursChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Service Usage Details Table -->
      <div class="chart-card full-width">
        <div class="chart-header">
          <h3 class="chart-title">Chi tiết sử dụng dịch vụ</h3>
          <button @click="exportData" class="export-btn">
            <DownloadIcon class="w-4 h-4" />
            Xuất báo cáo
          </button>
        </div>
        <div class="chart-body">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Dịch vụ</th>
                  <th>Số lượt sử dụng</th>
                  <th>Tokens tiêu thụ</th>
                  <th>Người dùng</th>
                  <th>Thời gian TB</th>
                  <th>Xu hướng</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="service in analytics.serviceDetails" :key="service.name">
                  <td>
                    <div class="service-name">
                      <div class="service-icon" :style="{ backgroundColor: service.color }">
                        <component :is="getServiceIcon(service.type)" class="w-4 h-4" />
                      </div>
                      {{ service.name }}
                    </div>
                  </td>
                  <td>{{ formatNumber(service.usage) }}</td>
                  <td>{{ formatNumber(service.tokens) }}</td>
                  <td>{{ service.users }}</td>
                  <td>{{ service.avgTime }}s</td>
                  <td>
                    <span :class="['trend-badge', service.trend > 0 ? 'positive' : 'negative']">
                      <component :is="service.trend > 0 ? TrendingUpIcon : TrendingDownIcon" class="w-3 h-3" />
                      {{ Math.abs(service.trend) }}%
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { 
  MessageSquare as MessageSquareIcon, 
  Users as UsersIcon, 
  Zap as ZapIcon, 
  Clock as ClockIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Download as DownloadIcon,
  Bot as BotIcon,
  FileText as FileTextIcon,
  Search as SearchIcon
} from 'lucide-vue-next'
import Chart from 'chart.js/auto'

const selectedTimeFilter = ref('today')
const customDateRange = ref({
  start: '',
  end: ''
})
const usageChartMetric = ref('conversations')
const viewMode = ref('overview') // 'overview' or 'agent'
const selectedAgent = ref('') // Selected AI Agent docName
const deployedAgents = ref([]) // List of deployed AI Agents

const timeFilters = [
  { label: 'Hôm nay', value: 'today' },
  { label: 'Tuần này', value: 'week' },
  { label: 'Tháng này', value: 'month' },
  { label: 'Tùy chỉnh', value: 'custom' }
]

// Mock Analytics Data
const analytics = ref({
  totalConversations: 15234,
  conversationsGrowth: 12.5,
  activeUsers: 892,
  usersGrowth: 8.3,
  totalTokens: 2456789,
  tokensGrowth: -5.2,
  avgResponseTime: 1.8,
  responseTimeImprovement: 15.3,
  topUsers: [
    { name: 'Nguyễn Văn A', email: 'nguyenvana@example.com', conversations: 234, tokens: 45678 },
    { name: 'Trần Thị B', email: 'tranthib@example.com', conversations: 198, tokens: 38942 },
    { name: 'Lê Văn C', email: 'levanc@example.com', conversations: 176, tokens: 32145 },
    { name: 'Phạm Thị D', email: 'phamthid@example.com', conversations: 145, tokens: 28563 },
    { name: 'Hoàng Văn E', email: 'hoangvane@example.com', conversations: 132, tokens: 24789 }
  ],
  serviceDetails: [
    { name: 'Chatbot AI', type: 'chat', usage: 8934, tokens: 1234567, users: 456, avgTime: 1.8, trend: 12.5, color: '#8b5cf6' },
    { name: 'OCR Hóa đơn', type: 'ocr', usage: 3421, tokens: 567890, users: 234, avgTime: 2.3, trend: 8.2, color: '#10b981' },
    { name: 'OCR Tài liệu', type: 'ocr', usage: 2879, tokens: 445678, users: 198, avgTime: 2.1, trend: -3.5, color: '#06b6d4' },
    { name: 'Knowledge Base Search', type: 'search', usage: 1567, tokens: 208654, users: 145, avgTime: 0.9, trend: 15.7, color: '#f59e0b' }
  ]
})

const usageTrendChart = ref(null)
const serviceDistributionChart = ref(null)
const peakHoursChart = ref(null)

let chartInstances = {}

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

const getServiceIcon = (type) => {
  switch (type) {
    case 'chat': return BotIcon
    case 'ocr': return FileTextIcon
    case 'search': return SearchIcon
    default: return BotIcon
  }
}

const applyCustomDateRange = () => {
  console.log('Apply custom date range:', customDateRange.value)
  // TODO: Fetch data for custom date range
}

const exportData = () => {
  console.log('Export analytics data')
  // TODO: Implement export functionality
}

const initUsageTrendChart = () => {
  if (!usageTrendChart.value) return
  
  if (chartInstances.usageTrend) {
    chartInstances.usageTrend.destroy()
  }

  const ctx = usageTrendChart.value.getContext('2d')
  chartInstances.usageTrend = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
      datasets: [{
        label: 'Conversations',
        data: [1200, 1900, 1500, 2100, 2400, 1800, 1600],
        borderColor: '#0ea5e9',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: '#f3f4f6'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  })
}

const initServiceDistributionChart = () => {
  if (!serviceDistributionChart.value) return
  
  if (chartInstances.serviceDistribution) {
    chartInstances.serviceDistribution.destroy()
  }

  const ctx = serviceDistributionChart.value.getContext('2d')
  chartInstances.serviceDistribution = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: analytics.value.serviceDetails.map(s => s.name),
      datasets: [{
        data: analytics.value.serviceDetails.map(s => s.usage),
        backgroundColor: analytics.value.serviceDetails.map(s => s.color),
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
}

const initPeakHoursChart = () => {
  if (!peakHoursChart.value) return
  
  if (chartInstances.peakHours) {
    chartInstances.peakHours.destroy()
  }

  const ctx = peakHoursChart.value.getContext('2d')
  chartInstances.peakHours = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['0h', '4h', '8h', '12h', '16h', '20h'],
      datasets: [{
        label: 'Số lượng requests',
        data: [120, 80, 450, 890, 1200, 650],
        backgroundColor: '#8b5cf6',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: '#f3f4f6'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  })
}

watch(selectedTimeFilter, () => {
  console.log('Time filter changed:', selectedTimeFilter.value)
  // TODO: Fetch data based on selected time filter
})

watch(usageChartMetric, () => {
  // TODO: Update chart based on selected metric
  initUsageTrendChart()
})

watch(viewMode, () => {
  console.log('View mode changed:', viewMode.value)
  if (viewMode.value === 'overview') {
    selectedAgent.value = ''
  }
  // Fetch analytics data based on view mode
  fetchAnalyticsData()
})

watch(selectedAgent, () => {
  console.log('Selected agent changed:', selectedAgent.value)
  // Fetch analytics data for selected agent
  fetchAnalyticsData()
})

// Fetch deployed AI Agents
const fetchDeployedAgents = async () => {
  try {
    const response = await fetch('/api/method/dbiz_ai_agent.dbiz_ai_agent.api.ai_catalog.get_agents')
    const result = await response.json()
    
    if (result.message && result.message.success) {
      // Filter only deployed agents
      deployedAgents.value = result.message.data.filter(agent => agent.status === 'deployed')
      console.log('Deployed agents:', deployedAgents.value)
    }
  } catch (error) {
    console.error('Error fetching deployed agents:', error)
  }
}

// Fetch analytics data based on filters
const fetchAnalyticsData = () => {
  console.log('Fetching analytics data...')
  console.log('View mode:', viewMode.value)
  console.log('Selected agent:', selectedAgent.value)
  console.log('Time filter:', selectedTimeFilter.value)
  
  // TODO: Implement actual API call to fetch analytics data
  // For now, we're using mock data
  // In production, this should filter data based on:
  // - viewMode: 'overview' or 'agent'
  // - selectedAgent: docName of selected agent (if viewMode is 'agent')
  // - selectedTimeFilter: time range
  
  // Refresh charts with new data
  setTimeout(() => {
    initUsageTrendChart()
    initServiceDistributionChart()
    initPeakHoursChart()
  }, 100)
}

onMounted(() => {
  // Fetch deployed agents
  fetchDeployedAgents()
  
  // Initialize charts
  setTimeout(() => {
    initUsageTrendChart()
    initServiceDistributionChart()
    initPeakHoursChart()
  }, 100)
})
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background: #f9fafb;
}

.analytics-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.time-filters {
  display: flex;
  gap: 0.5rem;
  background: #f3f4f6;
  padding: 4px;
  border-radius: 10px;
}

.filter-btn {
  padding: 0.5rem 1.25rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn.active {
  background: white;
  color: #0ea5e9;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.date-range-picker {
  max-width: 1400px;
  margin: 1.5rem auto 0;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.date-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.apply-btn {
  padding: 0.5rem 1.5rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.apply-btn:hover {
  background: #0284c7;
}

.view-controls {
  max-width: 1400px;
  margin: 1.5rem auto 0;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.view-mode-toggle {
  display: flex;
  gap: 0.5rem;
  background: #f3f4f6;
  padding: 4px;
  border-radius: 10px;
}

.view-mode-btn {
  padding: 0.5rem 1.5rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.view-mode-btn.active {
  background: white;
  color: #8b5cf6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.agent-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.agent-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  min-width: 250px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.agent-select:focus {
  outline: none;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.analytics-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-blue .card-icon { background: #0ea5e9; }
.card-purple .card-icon { background: #8b5cf6; }
.card-green .card-icon { background: #10b981; }
.card-orange .card-icon { background: #f59e0b; }

.card-content {
  flex: 1;
}

.card-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.card-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

.card-change {
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.card-change.positive { color: #10b981; }
.card-change.negative { color: #ef4444; }

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.chart-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover {
  background: #0284c7;
}

.chart-body {
  position: relative;
  height: 300px;
}

.top-users-list {
  max-height: 300px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.user-item:hover {
  background: #f9fafb;
}

.user-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  background: #f3f4f6;
  color: #6b7280;
}

.user-rank.rank-1 { background: #fef3c7; color: #f59e0b; }
.user-rank.rank-2 { background: #e5e7eb; color: #6b7280; }
.user-rank.rank-3 { background: #fed7aa; color: #ea580c; }

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #111827;
  font-size: 0.875rem;
}

.user-email {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.user-stats {
  display: flex;
  gap: 1.5rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-weight: 600;
  color: #111827;
  font-size: 0.875rem;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.125rem;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.875rem;
  color: #111827;
}

.service-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

.service-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.trend-badge.positive {
  background: #d1fae5;
  color: #065f46;
}

.trend-badge.negative {
  background: #fee2e2;
  color: #991b1b;
}
</style>

