import { ref, computed } from 'vue'
import { call } from 'frappe-ui'

export const useAnalytics = () => {
  const isLoading = ref(false)
  const error = ref(null)
  const analyticsData = ref(null)
  const agentPerformance = ref([])
  const errorLogs = ref([])
  
  // Filter state
  const filterType = ref('7_days')
  const customStartDate = ref('')
  const customEndDate = ref('')
  
  // Date range display
  const dateRangeDisplay = computed(() => {
    if (filterType.value === '7_days') {
      return '7 ngày gần đây'
    } else if (filterType.value === 'month') {
      return '30 ngày gần đây'
    } else if (filterType.value === 'custom' && customStartDate.value && customEndDate.value) {
      return `${formatDate(customStartDate.value)} - ${formatDate(customEndDate.value)}`
    }
    return '7 ngày gần đây'
  })
  
  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('vi-VN', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric' 
    })
  }
  
  // Fetch analytics data
  const fetchAnalyticsData = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      const params = {
        filter_type: filterType.value
      }
      
      if (filterType.value === 'custom') {
        if (!customStartDate.value || !customEndDate.value) {
          throw new Error('Vui lòng chọn ngày bắt đầu và kết thúc')
        }
        params.start_date = customStartDate.value
        params.end_date = customEndDate.value
      }
      
      // Fetch main analytics data
      const data = await call('dbiz_ai_agent.api.analytics.Get_Analytics_Data', params)
      analyticsData.value = data
      
      return data
    } catch (err) {
      error.value = err.message || 'Không thể tải dữ liệu analytics'
      console.error('Analytics fetch error:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // Fetch agent performance
  const fetchAgentPerformance = async () => {
    try {
      const params = {
        filter_type: filterType.value
      }
      
      if (filterType.value === 'custom') {
        params.start_date = customStartDate.value
        params.end_date = customEndDate.value
      }
      
      const data = await call('dbiz_ai_agent.api.analytics.Get_Agent_Performance', params)
      agentPerformance.value = data || []
      
      return data
    } catch (err) {
      console.error('Agent performance fetch error:', err)
      return []
    }
  }
  
  // Fetch error logs
  const fetchErrorLogs = async (limit = 20) => {
    try {
      const params = {
        filter_type: filterType.value,
        limit
      }
      
      if (filterType.value === 'custom') {
        params.start_date = customStartDate.value
        params.end_date = customEndDate.value
      }
      
      const data = await call('dbiz_ai_agent.api.analytics.Get_Error_Logs', params)
      errorLogs.value = data || []
      
      return data
    } catch (err) {
      console.error('Error logs fetch error:', err)
      return []
    }
  }
  
  // Fetch all data
  const fetchAllData = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      await Promise.all([
        fetchAnalyticsData(),
        fetchAgentPerformance(),
        fetchErrorLogs()
      ])
    } catch (err) {
      error.value = err.message || 'Không thể tải dữ liệu'
    } finally {
      isLoading.value = false
    }
  }
  
  // Set filter type
  const setFilterType = async (type) => {
    filterType.value = type
    if (type !== 'custom') {
      await fetchAllData()
    }
  }
  
  // Apply custom date filter
  const applyCustomDateFilter = async () => {
    if (!customStartDate.value || !customEndDate.value) {
      error.value = 'Vui lòng chọn ngày bắt đầu và kết thúc'
      return
    }
    
    // Validate date range
    const start = new Date(customStartDate.value)
    const end = new Date(customEndDate.value)
    
    if (start > end) {
      error.value = 'Ngày bắt đầu phải nhỏ hơn ngày kết thúc'
      return
    }
    
    await fetchAllData()
  }
  
  return {
    // State
    isLoading,
    error,
    analyticsData,
    agentPerformance,
    errorLogs,
    filterType,
    customStartDate,
    customEndDate,
    dateRangeDisplay,
    
    // Methods
    fetchAnalyticsData,
    fetchAgentPerformance,
    fetchErrorLogs,
    fetchAllData,
    setFilterType,
    applyCustomDateFilter
  }
}

