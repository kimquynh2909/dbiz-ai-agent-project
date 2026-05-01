import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { loadConversation as loadConversationService } from '@/services/chatService'
import { call } from 'frappe-ui'
import { subscribeToSocketChatStream } from '@/utils/socket'

export const useChatStore = defineStore('chat', {
  state: () => ({
    conversations: [],
    currentConversation: null,
    messages: [],
    messageCache: {},
    loading: false,
    thinking: false,
    error: null,
    user: null, // Lưu thông tin user đã xác thực
  }),

  getters: {
    currentMessages: (state) => state.messages,
    conversationList: (state) => state.conversations,
    isLoading: (state) => state.loading,
    isThinking: (state) => state.thinking,
    currentUser: (state) => state.user,
  },

  actions: {
    async setUser(username) {
      if (username) {
        this.user = username
      } else {
        this.user = await createResource({ url: 'dbiz_ai_agent.api.auth.Get_Current_User', method: 'Get' }).fetch()
      }
    },

    clearUser() {
      this.user = null
    },

    // Load hội thoại và tin nhắn từ service, lưu vào state
    async loadConversation(conversationName) {
      this.loading = true
      this.error = null
      try {
        const data = await loadConversationService(conversationName)
        this.currentConversation = data.conversation
        this.messages = Array.isArray(data.messages) ? data.messages : []
        // Lưu cache cho hội thoại này
        if (this.currentConversation?.name) {
          this._setCachedMessages(this.currentConversation.name, this.messages)
        }
      } catch (error) {
        this.error = error.message || 'Không thể tải hội thoại.'
        this.currentConversation = null
        this.messages = []
      } finally {
        this.loading = false
      }
    },
    async sendMessage(message) {
      // Bỏ qua nếu tin nhắn rỗng
      if (!message.trim()) return
      this.error = null

      // Xác định user gửi
      // Tạo id tạm cho tin nhắn
      const localId = crypto.randomUUID()
      const messageKey = `${localId}__key`

      // Đưa tin nhắn user vào danh sách
      this.messages.push({
        id: localId,
        content: message,
        role: 'user',
        timestamp: new Date().toISOString(),
      })

      // Lưu cache nếu đang trong 1 hội thoại - dùng name thay vì id
      const conversationKey = this.currentConversation?.name
      if (conversationKey) this._setCachedMessages(conversationKey, this.messages)

      try {
        // Gọi API gửi tin nhắn trực tiếp
        const response = await call('dbiz_ai_agent.api.chat.Send_Message_Streaming', {
          conversation_name: conversationKey ?? null,
          message,
        })
        if (!response) throw new Error('Không nhận được phản hồi từ server')

        // Cập nhật hội thoại hiện tại
        this.currentConversation = response.conversation
        const cacheKey = this.currentConversation.name

        // Cập nhật ID của tin nhắn user từ localId sang ID thật từ database
        if (response.user_message_id) {
          const userMsgIndex = this.messages.findIndex((m) => m.id === localId)
          if (userMsgIndex !== -1) {
            this.messages[userMsgIndex].id = response.user_message_id
          }
        }

        if (cacheKey) this._setCachedMessages(cacheKey, this.messages)

        // Bắt đầu lắng nghe luồng phản hồi qua Socket.IO TRƯỚC
        // để không bỏ lỡ các chunk đầu tiên
        const streamResponsePromise = this.streamResponse(this.currentConversation.name, messageKey, localId, null)

        // Sau đó mới gọi API bắt đầu stream AI
        const streamStartResponse = await call('dbiz_ai_agent.api.chat.Stream_AI_Response', {
          conversation_name: this.currentConversation.name,
          message,
          message_key: messageKey,
        })

        // Cập nhật assistant_message_id thật từ backend
        const assistantMessageId = streamStartResponse?.assistant_message_id
        if (assistantMessageId) {
          // Cập nhật ID thật cho message AI trong cache
          this._updateConversationMessages(this.currentConversation.name, (list) => {
            const next = this._cloneMessages(list)
            const tempId = `${localId}__assistant`
            const idx = next.findIndex((m) => m.id === tempId)
            if (idx !== -1) {
              next[idx].id = assistantMessageId
            }
            return next
          })

          if (this.currentConversation?.name === this.currentConversation.name) {
            this.messages = this._getCachedMessages(this.currentConversation.name)
          }
        }

        await streamResponsePromise
      } catch (error) {
        // Nếu lỗi: xóa tin nhắn user vừa push, thêm thông báo lỗi
        this.error = error.message
        console.error('Send message error:', error)
        this.messages.pop()
        this.messages.push({
          id: Date.now(),
          content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.',
          role: 'error',
          timestamp: new Date().toISOString(),
        })
        if (conversationKey) this._setCachedMessages(conversationKey, this.messages)
      }
    },

    // Lắng nghe realtime và cập nhật tin nhắn AI cho hội thoại
    async streamResponse(conversationName, messageKey, localId, assistantMessageId = null) {
      // Tạo id cho tin nhắn AI - ưu tiên dùng ID thật từ database
      const aiId = assistantMessageId || `${localId}__assistant`
      // Tạo tin nhắn AI rỗng, trạng thái đang stream
      let aiMessage = {
        id: aiId,
        content: '',
        role: 'assistant',
        timestamp: new Date().toISOString(),
        sources: [],
        streaming: true,
      }
      // Thêm hoặc cập nhật tin nhắn AI vào cache hội thoại
      if (conversationName) {
        this._updateConversationMessages(conversationName, (list) => {
          const next = this._cloneMessages(list)
          const idx = next.findIndex((m) => m.id === aiId)
          if (idx !== -1) next.splice(idx, 1)
          next.push(aiMessage)
          return next
        })
      }

      // Cập nhật messages nếu đang xem đúng hội thoại
      if (this.currentConversation?.name === conversationName) {
        this.messages = this._getCachedMessages(conversationName)
      }

      // Đăng ký lắng nghe realtime qua Firebase RTDB
      let lastActivity = Date.now()
      const STALLED_TIMEOUT_MS = 30000 // 30s không có dữ liệu thì ngắt

      // Xử lý dữ liệu nhận được từ server
      const handler = (data) => {
        try {
          if (!data) return
          lastActivity = Date.now()
          // Nhận từng đoạn text AI (event type="chunk")
          if (data.chunk || data.type === 'chunk') {
            this._updateConversationMessages(conversationName, (list) => {
              const next = this._cloneMessages(list)
              const idx = next.findIndex((m) => m.id === aiId)
              if (idx === -1) return next
              const chunk = data.chunk || ''
              next[idx].content = (next[idx].content || '') + chunk
              return next
            })

            // Sync lại messages nếu đang xem conversation này
            if (this.currentConversation?.name === conversationName) {
              this.messages = this._getCachedMessages(conversationName)
            }
          }
          // Nhận hình ảnh AI trả về (event type="images")
          if (data.images || data.type === 'images') {
            const imgs = data.images || []
            this._updateConversationMessages(conversationName, (list) => {
              const next = this._cloneMessages(list)
              const idx = next.findIndex((m) => m.id === aiId)
              if (idx === -1) return next
              const merged = [...(next[idx].images || []), ...imgs]
              next[idx].images = merged.filter((item, index) => merged.findIndex((img) => img.id === item.id) === index)
              return next
            })
          }
          // Kết thúc stream
          if (data.done || data.type === 'done') {
            this._updateConversationMessages(conversationName, (list) => {
              const next = this._cloneMessages(list)
              const idx = next.findIndex((m) => m.id === aiId)
              if (idx === -1) return next
              if (data.final_text && !next[idx].content) next[idx].content = data.final_text
              if (data.images) next[idx].images = data.images
              if (data.tool_results) next[idx].toolResults = data.tool_results
              next[idx].streaming = false
              next[idx].timestamp = new Date().toISOString()
              return next
            })

            // Sync lại messages nếu đang xem conversation này
            if (this.currentConversation?.name === conversationName) {
              this.messages = this._getCachedMessages(conversationName)
            }

            // Cập nhật database
            call('dbiz_ai_agent.api.chat.Update_Message_Streaming_Status', {
              conversation_name: conversationName,
              message_id: aiId,
              is_streaming: 0,
              content: data.final_text,
            }).catch((err) => console.error('Failed to update streaming status:', err))

            try {
              unsub?.()
            } catch (e) {}
          }
          // Nếu có lỗi từ server
          if (data.error) {
            this._updateConversationMessages(conversationName, (list) => {
              const next = this._cloneMessages(list)
              const idx = next.findIndex((m) => m.id === aiId)
              if (idx === -1) return next
              next[idx].content = `Lỗi: ${data.error}`
              next[idx].streaming = false
              next[idx].error = true
              return next
            })

            // Sync lại messages nếu đang xem conversation này
            if (this.currentConversation?.name === conversationName) {
              this.messages = this._getCachedMessages(conversationName)
            }

            // Cập nhật database
            const cachedMessages = this._getCachedMessages(conversationName)
            const errorMsg = cachedMessages.find((m) => m.id === aiId)
            call('dbiz_ai_agent.api.chat.Update_Message_Streaming_Status', {
              conversation_name: conversationName,
              message_id: aiId,
              is_streaming: 0,
              content: errorMsg?.content,
            }).catch((err) => console.error('Failed to update streaming status:', err))

            try {
              unsub?.()
            } catch (e) {}
          }
        } catch (e) {
          console.error('Realtime handler error:', e)
        }
      }

      // Đăng ký lắng nghe qua Socket.IO
      let unsub = null
      try {
        unsub = await subscribeToSocketChatStream(conversationName, messageKey, handler)
      } catch (e) {
        console.error('Socket.IO realtime not available:', e)
      }

      // Tự động ngắt nếu không có dữ liệu trong 30s
      const stallChecker = setInterval(() => {
        const now = Date.now()
        if (now - lastActivity > STALLED_TIMEOUT_MS) {
          this._updateConversationMessages(conversationName, (list) => {
            const next = this._cloneMessages(list)
            const idx = next.findIndex((m) => m.id === aiId)
            if (idx === -1) return next
            if (!next[idx].content) next[idx].content = '(Phản hồi bị gián đoạn hoặc quá chậm.)'
            next[idx].streaming = false
            next[idx].timestamp = new Date().toISOString()
            return next
          })

          // Sync lại messages nếu đang xem conversation này
          if (this.currentConversation?.name === conversationName) {
            this.messages = this._getCachedMessages(conversationName)
          }

          // Cập nhật database
          const cachedMessages = this._getCachedMessages(conversationName)
          const timeoutMsg = cachedMessages.find((m) => m.id === aiId)
          call('dbiz_ai_agent.api.chat.Update_Message_Streaming_Status', {
            conversation_name: conversationName,
            message_id: aiId,
            is_streaming: 0,
            content: timeoutMsg?.content,
          }).catch((err) => console.error('Failed to update streaming status:', err))

          try {
            unsub?.()
          } catch (e) {}
          clearInterval(stallChecker)
        }
      }, 1000)

      // Trả về promise khi stream kết thúc
      return new Promise((resolve) => {
        const checkInterval = setInterval(() => {
          const cachedMessages = this._getCachedMessages(conversationName)
          const msg = cachedMessages.find((m) => m.id === aiId)
          if (!msg) return
          if (!msg.streaming) {
            clearInterval(checkInterval)
            clearInterval(stallChecker)
            try {
              unsub?.()
            } catch (e) {}
            resolve()
          }
        }, 200)
      })
    },

    async provideFeedback(messageId, helpful) {
      try {
        await call('dbiz_ai_agent.api.chat.Provide_Feedback', {
          message_id: messageId,
          helpful: helpful,
        })

        const message = this.messages.find((m) => m.id === messageId)
        if (message) {
          message.feedback = helpful
          const conversationKey = this.currentConversation?.name
          if (conversationKey) {
            this._setCachedMessages(conversationKey, this.messages)
          }
        }
      } catch (error) {
        console.error('Provide feedback error:', error)
      }
    },

    _cloneMessages(list = []) {
      return JSON.parse(JSON.stringify(list))
    },

    _getCachedMessages(conversationName) {
      if (!conversationName) return []
      const cached = this.messageCache[conversationName]
      return this._cloneMessages(cached)
    },

    _setCachedMessages(conversationName, messages) {
      if (!conversationName) return
      const copy = this._cloneMessages(messages || [])
      this.messageCache[conversationName] = copy

      // Cập nhật this.messages nếu đang xem conversation này
      // conversationName là CONV-xxxxx, check với currentConversation.name
      if (this.currentConversation?.name === conversationName) {
        this.messages = this._cloneMessages(messages || [])
      }
    },

    _mergeWithCached(conversationName, serverMessages = []) {
      const cached = this._getCachedMessages(conversationName)
      if (!cached.length) return serverMessages
      const hasStreaming = cached.some((msg) => msg.streaming)
      if (!hasStreaming) return serverMessages
      const serverMap = new Map(serverMessages.map((item) => [item.id, { ...item }]))
      const merged = cached.map((item) => {
        const serverItem = serverMap.get(item.id)
        if (!serverItem) return item
        serverMap.delete(item.id)
        if (item.streaming) return { ...serverItem, ...item }
        return serverItem
      })
      serverMap.forEach((value) => {
        merged.push(value)
      })
      merged.sort((a, b) => {
        const aTime = a.timestamp ? new Date(a.timestamp).getTime() : 0
        const bTime = b.timestamp ? new Date(b.timestamp).getTime() : 0
        return aTime - bTime
      })
      return merged
    },

    _updateConversationMessages(conversationName, updater) {
      if (!conversationName || typeof updater !== 'function') return
      let base = this._getCachedMessages(conversationName)
      if (!base.length && this.currentConversation?.name === conversationName) {
        base = this._cloneMessages(this.messages)
      }
      const working = this._cloneMessages(base)
      const result = updater(working)
      const updated = Array.isArray(result) ? result : working
      this._setCachedMessages(conversationName, updated)
    },

    clearCurrentConversation() {
      const conversationKey = this.currentConversation?.name
      if (conversationKey) {
        this._setCachedMessages(conversationKey, this.messages)
      }
      this.currentConversation = null
      this.messages = []
      this.error = null
    },

    async loadConversations() {
      try {
        const response = await call('dbiz_ai_agent.api.chat.Get_Conversations')
        if (response && Array.isArray(response)) {
          this.conversations = response
        }
      } catch (error) {
        console.error('Failed to load conversations:', error)
        this.conversations = []
      }
    },

    async deleteConversation(conversationName) {
      try {
        await call('dbiz_ai_agent.api.chat.Delete_Conversation', {
          conversation_name: conversationName,
        })
        // Remove from conversations list
        this.conversations = this.conversations.filter((c) => c.name !== conversationName)
        // Clear cache
        if (this.messageCache[conversationName]) {
          delete this.messageCache[conversationName]
        }
      } catch (error) {
        console.error('Failed to delete conversation:', error)
        throw error
      }
    },
  },
})
