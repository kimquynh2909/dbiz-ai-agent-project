import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

export const useChatConfig = () => {
  const chatConfig = ref(null)
  const suggestions = ref([])
  const isLoadingConfig = ref(false)

  const quickQuestions = computed(() => {
    if (!chatConfig.value || !Array.isArray(chatConfig.value.quick_questions)) return []
    return chatConfig.value.quick_questions
  })

  const loadChatbotConfig = async (retryCount = 0) => {
    if (isLoadingConfig.value) return
    isLoadingConfig.value = true

    try {
      const res = await createResource({ url: 'dbiz_ai_agent.api.auth.get_assistant_config', method: 'GET' }).fetch()
      if (res) {
        chatConfig.value = {
          title: res.title || null,
          description: res.description || null,
          assistant_name: res.assistant_name || null,
          greeting_message: res.greeting_message || null,
          support_info: res.support_info || null,
          avatar_image: res.avatar_image || null,
          quick_questions: Array.isArray(res.quick_questions) ? res.quick_questions : []
        }
        suggestions.value = (chatConfig.value.quick_questions || []).map((q) => q.question_text)
      } else {
        chatConfig.value = null
        suggestions.value = []
      }
    } catch (error) {
      console.error('Error loading chatbot config:', error)
      if (retryCount < 2) {
        setTimeout(() => loadChatbotConfig(retryCount + 1), 1000 * (retryCount + 1))
        return
      }

      chatConfig.value = null
      suggestions.value = []
    } finally {
      isLoadingConfig.value = false
    }
  }

  return {
    chatConfig,
    suggestions,
    quickQuestions,
    isLoadingConfig,
    loadChatbotConfig
  }
}
