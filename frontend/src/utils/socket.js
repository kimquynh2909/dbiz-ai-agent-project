// Socket.IO helpers for chat streaming (optional transport)
import { io } from 'socket.io-client'
import { call } from 'frappe-ui'

let socket = null
let connectPromise = null

async function fetchSocketConfig() {
  const res = await call('dbiz_ai_agent.api.auth.get_socketio_client_config', {})
  return res || { enabled: false }
}

export async function ensureSocket() {
  if (socket && socket.connected) return socket
  if (connectPromise) return connectPromise
  connectPromise = (async () => {
    const cfg = await fetchSocketConfig()
    if (!cfg?.enabled) {
      throw new Error('Socket.IO not configured')
    }
    // Detect if running behind proxy (production)
    const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'

    // For production/proxy: try polling first, then upgrade to websocket
    // For local: prefer websocket
    const transports = isProduction
      ? ['polling', 'websocket'] // Fallback to polling if websocket fails via proxy
      : ['websocket', 'polling']

    socket = io(cfg.serverUrl, {
      transports: transports,
      withCredentials: true,
      // Path should be explicit when behind proxy
      path: cfg.path || '/socket.io/',
      auth: cfg.authToken ? { token: cfg.authToken } : undefined,
      // Connection options for proxy environments
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 10,
      timeout: 20000, // Increased timeout for proxy environments (20s)
      // Force upgrade after initial polling connection
      upgrade: true,
      rememberUpgrade: true,
      // Additional options for proxy compatibility
      forceNew: false,
      autoConnect: true,
    })

    // Add error logging for debugging
    socket.on('connect_error', (err) => {
      console.error('[Socket.IO] Connection error:', err.message, {
        type: err.type,
        description: err.description,
        context: err.context,
      })
    })

    socket.on('disconnect', (reason) => {
      console.warn('[Socket.IO] Disconnected:', reason)
      // If disconnect is not intentional, trigger reconnection
      if (reason === 'io server disconnect') {
        // Server disconnected the socket, don't reconnect automatically
        socket.disconnect()
      }
    })

    socket.on('reconnect_attempt', (attemptNumber) => {
      console.info(`[Socket.IO] Reconnection attempt ${attemptNumber}`)
    })

    socket.on('reconnect', (attemptNumber) => {
      console.info(`[Socket.IO] Reconnected after ${attemptNumber} attempts`)
    })

    return new Promise((resolve, reject) => {
      const onConnect = () => {
        console.info('[Socket.IO] Connected:', {
          id: socket.id,
          transport: socket.io.engine.transport.name,
        })
        socket.off('connect_error', onError)
        resolve(socket)
      }
      const onError = (err) => {
        console.error('[Socket.IO] Connection failed:', err.message)
        socket.off('connect', onConnect)
        reject(err)
      }
      socket.once('connect', onConnect)
      socket.once('connect_error', onError)
      // Increased timeout to 20s for proxy environments
      setTimeout(() => {
        socket.off('connect', onConnect)
        socket.off('connect_error', onError)
        if (!socket.connected) {
          const timeoutErr = new Error('Socket.IO connect timeout after 20s')
          console.error('[Socket.IO]', timeoutErr.message)
          reject(timeoutErr)
        }
      }, 20000) // 20 seconds timeout
    })
  })()
  try {
    const s = await connectPromise
    return s
  } finally {
    connectPromise = null
  }
}

// Helper to sanitize room names (matches Python backend logic)
function sanitizeRoomComponent(s) {
  return String(s || '_').replace(/[^a-zA-Z0-9\-_:]/g, '-')
}

export async function subscribeToSocketChatStream(conversationName, messageKey, onEvent) {
  if (!conversationName || !messageKey) throw new Error('Missing conversationName/messageKey')
  const s = await ensureSocket()

  // Sanitize to match backend room format
  const sanitizedConversation = sanitizeRoomComponent(conversationName)
  const sanitizedMessageKey = sanitizeRoomComponent(messageKey)
  const room = `room:${sanitizedConversation}:${sanitizedMessageKey}`

  console.info('[Socket.IO] Subscribing to stream:', {
    conversation: conversationName,
    messageKey: messageKey,
    room: room,
  })

  const handler = (evt) => {
    try {
      // Log events for debugging in development
      if (process.env.NODE_ENV !== 'production') {
        console.debug('[Socket.IO] Stream event received:', {
          type: evt?.type,
          room: evt?.room,
          conversation: evt?.conversation,
          message_key: evt?.message_key,
        })
      }
      onEvent?.(evt)
    } catch (e) {
      console.error('[Socket.IO] Handler error:', e, evt)
    }
  }

  // Ensure connected before emitting
  if (!s.connected) {
    console.warn('[Socket.IO] Socket not connected, waiting...')
    await new Promise((resolve) => {
      if (s.connected) {
        resolve()
      } else {
        s.once('connect', resolve)
        // Timeout after 10s
        setTimeout(() => {
          s.off('connect', resolve)
          resolve()
        }, 10000)
      }
    })
  }

  s.emit('join_stream', {
    conversation: conversationName,
    message_key: messageKey,
  })
  s.on('chat_stream_event', handler)

  return () => {
    try {
      s.emit('leave_stream', {
        conversation: conversationName,
        message_key: messageKey,
      })
      console.info('[Socket.IO] Left stream:', room)
    } catch (e) {
      console.error('[Socket.IO] Error leaving stream:', e)
    }
    try {
      s.off('chat_stream_event', handler)
    } catch (e) {
      console.error('[Socket.IO] Error removing handler:', e)
    }
  }
}

// Subscribe to generic events (for conversation title updates, etc.)
export async function subscribeToGenericEvent(eventName, handler) {
  const s = await ensureSocket()
  const wrappedHandler = (data) => {
    try {
      handler(data)
    } catch (e) {
      console.error(`[Socket.IO] ${eventName} handler error:`, e, data)
    }
  }
  s.on('generic_event', wrappedHandler)

  return () => {
    try {
      s.off('generic_event', wrappedHandler)
    } catch (e) {
      console.error('[Socket.IO] Error removing generic_event handler:', e)
    }
  }
}
