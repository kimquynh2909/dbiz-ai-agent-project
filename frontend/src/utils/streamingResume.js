/**
 * Utility để xử lý resume streaming khi user refresh hoặc chuyển conversation
 *
 * Cách hoạt động:
 * 1. Khi load conversation, kiểm tra xem có message nào đang is_streaming = 1 không
 * 2. Nếu có, reconnect vào stream_key đó qua Socket.IO
 * 3. Tiếp tục hiển thị streaming effect với nội dung mới
 */

import { ensureSocket } from './socket'

/**
 * Kiểm tra và resume streaming messages trong conversation
 * @param {Array} messages - Danh sách messages từ conversation
 * @param {Function} onStreamChunk - Callback khi nhận được chunk mới
 * @param {Function} onStreamComplete - Callback khi stream hoàn tất
 * @returns {Promise<Array>} Danh sách stream_keys đang active
 */
export async function checkAndResumeStreaming(messages, onStreamChunk, onStreamComplete) {
  const activeStreams = []

  if (!messages || !Array.isArray(messages)) {
    console.warn('checkAndResumeStreaming: messages is not an array')
    return activeStreams
  }

  // Lấy socket client của app
  let socketClient
  try {
    socketClient = await ensureSocket()
  } catch (error) {
    console.warn('Socket.IO client not available for streaming resume:', error.message)
    return activeStreams
  }

  messages.forEach((message, index) => {
    if (message.is_streaming === 1 && message.stream_key) {
      activeStreams.push(message.stream_key)

      const streamKey = message.stream_key
      console.log(`🔄 Resuming stream for message ${index} with key: ${streamKey}`)

      // Listen cho streaming events qua chat_stream_event
      const handler = (evt) => {
        // Check nếu event thuộc về stream_key này
        if (evt?.message_key !== streamKey) return

        if (evt?.type === 'chunk' && onStreamChunk) {
          onStreamChunk(index, evt)
        } else if (evt?.type === 'complete' && onStreamComplete) {
          console.log(`✅ Stream completed for key: ${streamKey}`)
          onStreamComplete(index, evt)
          // Cleanup listener
          socketClient.off('chat_stream_event', handler)
        }
      }

      socketClient.on('chat_stream_event', handler)

      // Emit join_stream để backend biết client đang listen
      socketClient.emit('join_stream', {
        conversation: message.conversation_name,
        message_key: streamKey,
      })
    }
  })

  if (activeStreams.length > 0) {
    console.log(`Found ${activeStreams.length} active streams to resume`)
  }

  return activeStreams
}

/**
 * Cleanup stream listeners khi unmount component
 * @param {Array} streamKeys - Danh sách stream_keys cần cleanup
 * @param {Object} conversationData - Data về conversation để emit leave_stream
 */
export async function cleanupStreamListeners(streamKeys, conversationData = {}) {
  if (!streamKeys || streamKeys.length === 0) return

  try {
    const socketClient = await ensureSocket()

    streamKeys.forEach((streamKey) => {
      // Emit leave_stream để backend dừng gửi events
      socketClient.emit('leave_stream', {
        conversation: conversationData.conversation_name,
        message_key: streamKey,
      })
    })

    console.log(`Cleaned up ${streamKeys.length} stream listeners`)
  } catch (error) {
    console.warn('Error cleaning up stream listeners:', error.message)
  }
}

/**
 * Call API để kiểm tra stream còn active không
 * @param {String} conversationName
 * @param {String} streamKey
 * @returns {Promise} Response từ Resume_Streaming API
 */
export async function resumeStreamingAPI(conversationName, streamKey) {
  try {
    // Sử dụng frappe.call từ window nếu có
    const frappeCall = window.frappe?.call
    if (!frappeCall) {
      throw new Error('Frappe call method not available')
    }

    const response = await frappeCall({
      method: 'dbiz_ai_agent.api.chat.Resume_Streaming',
      args: {
        conversation_name: conversationName,
        stream_key: streamKey,
      },
    })
    return response
  } catch (error) {
    console.error('Error resuming stream:', error)
    return { success: false, message: error.message }
  }
}
