// Production-ready Socket.IO server for realtime chat streaming
// Usage: node server.js (requires: npm i socket.io)

const { Server } = require("socket.io");
const http = require("http");

// ============= Configuration =============
const PORT = process.env.SIO_PORT || 5179;
const NODE_ENV = process.env.NODE_ENV || "development";
const IS_PRODUCTION = NODE_ENV === "production";

// CORS: In production, MUST be specific domain(s)
const CORS_ORIGIN = process.env.SIO_CORS || (IS_PRODUCTION ? false : "*");
if (IS_PRODUCTION && (!CORS_ORIGIN || CORS_ORIGIN === "*")) {
  console.error(
    "FATAL: SIO_CORS must be set to specific domain(s) in production!"
  );
  process.exit(1);
}

// Auth token validation
const AUTH_TOKEN = process.env.SIO_AUTH_TOKEN || null;
if (IS_PRODUCTION && !AUTH_TOKEN) {
  console.warn(
    "WARNING: SIO_AUTH_TOKEN not set in production - all connections accepted!"
  );
}

// Connection limits
const MAX_CONNECTIONS = parseInt(process.env.SIO_MAX_CONNECTIONS || "1000");
const RATE_LIMIT_WINDOW = parseInt(
  process.env.SIO_RATE_LIMIT_WINDOW || "60000"
); // 1 min
const RATE_LIMIT_MAX = parseInt(process.env.SIO_RATE_LIMIT_MAX || "100"); // events per window

// Timeouts
const PING_TIMEOUT = parseInt(process.env.SIO_PING_TIMEOUT || "20000");
const PING_INTERVAL = parseInt(process.env.SIO_PING_INTERVAL || "25000");

// ============= Metrics & Monitoring =============
const metrics = {
  totalConnections: 0,
  activeConnections: 0,
  totalMessages: 0,
  totalErrors: 0,
  startTime: Date.now(),
  rateLimitHits: 0,
  authFailures: 0,
};

// Rate limiting per socket
const rateLimiter = new Map();

function checkRateLimit(socketId) {
  const now = Date.now();
  const record = rateLimiter.get(socketId) || { count: 0, windowStart: now };

  if (now - record.windowStart > RATE_LIMIT_WINDOW) {
    record.count = 1;
    record.windowStart = now;
  } else {
    record.count++;
  }

  rateLimiter.set(socketId, record);

  if (record.count > RATE_LIMIT_MAX) {
    metrics.rateLimitHits++;
    return false;
  }
  return true;
}

// ============= HTTP Server for Health Check =============
const httpServer = http.createServer((req, res) => {
  if (req.url === "/health" || req.url === "/healthz") {
    const uptime = Math.floor((Date.now() - metrics.startTime) / 1000);
    const health = {
      status: "healthy",
      uptime,
      connections: metrics.activeConnections,
      maxConnections: MAX_CONNECTIONS,
      totalConnections: metrics.totalConnections,
      totalMessages: metrics.totalMessages,
      totalErrors: metrics.totalErrors,
      rateLimitHits: metrics.rateLimitHits,
      authFailures: metrics.authFailures,
      memoryUsage: process.memoryUsage(),
      timestamp: new Date().toISOString(),
    };
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(health, null, 2));
  } else if (req.url === "/metrics") {
    // Prometheus-compatible metrics
    const uptime = Math.floor((Date.now() - metrics.startTime) / 1000);
    const metricsText = `
# HELP socketio_active_connections Current number of active connections
# TYPE socketio_active_connections gauge
socketio_active_connections ${metrics.activeConnections}

# HELP socketio_total_connections Total connections since startup
# TYPE socketio_total_connections counter
socketio_total_connections ${metrics.totalConnections}

# HELP socketio_total_messages Total messages processed
# TYPE socketio_total_messages counter
socketio_total_messages ${metrics.totalMessages}

# HELP socketio_total_errors Total errors encountered
# TYPE socketio_total_errors counter
socketio_total_errors ${metrics.totalErrors}

# HELP socketio_rate_limit_hits Total rate limit violations
# TYPE socketio_rate_limit_hits counter
socketio_rate_limit_hits ${metrics.rateLimitHits}

# HELP socketio_auth_failures Total authentication failures
# TYPE socketio_auth_failures counter
socketio_auth_failures ${metrics.authFailures}

# HELP socketio_uptime_seconds Server uptime in seconds
# TYPE socketio_uptime_seconds gauge
socketio_uptime_seconds ${uptime}
`.trim();
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end(metricsText);
  } else {
    res.writeHead(404);
    res.end("Not Found");
  }
});

// ============= Socket.IO Server =============
// Path configuration for proxy compatibility
const SOCKET_PATH = process.env.SIO_PATH || '/socket.io/';

const io = new Server(httpServer, {
  cors: {
    origin: CORS_ORIGIN,
    credentials: true,
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type", "Authorization", "X-Frappe-Site-Name"],
  },
  pingTimeout: PING_TIMEOUT,
  pingInterval: PING_INTERVAL,
  maxHttpBufferSize: 1e6, // 1MB max message size
  transports: ["websocket", "polling"],
  allowEIO3: false, // Disable older Engine.IO v3
  path: SOCKET_PATH,
  // Allow requests from proxy
  allowRequest: (req, callback) => {
    // When behind proxy, trust proxy headers
    // This allows connections from HAProxy/Nginx
    callback(null, true);
  },
  // Connection state recovery for better proxy handling
  connectionStateRecovery: {
    // The backup duration of the sessions and the packets.
    maxDisconnectionDuration: 2 * 60 * 1000, // 2 minutes
    // Whether to skip middlewares upon successful recovery.
    skipMiddlewares: true,
  },
});

// ============= Middleware =============
io.use((socket, next) => {
  // Connection limit
  if (metrics.activeConnections >= MAX_CONNECTIONS) {
    console.warn(
      `Connection rejected: max connections (${MAX_CONNECTIONS}) reached`
    );
    return next(new Error("Server at capacity"));
  }

  // Authentication
  if (AUTH_TOKEN) {
    const token = socket.handshake.auth?.token || socket.handshake.query?.token;
    if (token !== AUTH_TOKEN) {
      metrics.authFailures++;
      console.warn(`Auth failed for socket ${socket.id}:`, {
        ip: socket.handshake.address,
        headers: socket.handshake.headers["user-agent"],
      });
      return next(new Error("Authentication failed"));
    }
  }

  next();
});

// ============= Connection Handling =============
io.on("connection", (socket) => {
  metrics.totalConnections++;
  metrics.activeConnections++;

  const clientInfo = {
    id: socket.id,
    ip: socket.handshake.address,
    userAgent: socket.handshake.headers["user-agent"],
    connectedAt: new Date().toISOString(),
  };

  console.log(`[CONNECT] Socket ${socket.id}:`, {
    active: metrics.activeConnections,
    total: metrics.totalConnections,
    ip: clientInfo.ip,
  });

  // Validate and sanitize payload helper
  function validatePayload(payload, requiredFields = []) {
    if (!payload || typeof payload !== "object") {
      return { valid: false, error: "Invalid payload" };
    }

    for (const field of requiredFields) {
      if (!payload[field]) {
        return { valid: false, error: `Missing field: ${field}` };
      }
      // Sanitize strings
      if (typeof payload[field] === "string") {
        payload[field] = payload[field].substring(0, 500); // Max 500 chars
      }
    }

    return { valid: true, payload };
  }

  // ============= Event Handlers with Rate Limiting =============

  // Helper to create room name consistently (matches Python backend)
  function createRoomName(conversation, message_key) {
    // Sanitize to match Python backend logic
    const safe = (s) => String(s || '_').replace(/[^a-zA-Z0-9\-_:]/g, '-');
    return `room:${safe(conversation)}:${safe(message_key)}`;
  }

  socket.on("join_stream", (data) => {
    if (!checkRateLimit(socket.id)) {
      socket.emit("error", { message: "Rate limit exceeded" });
      return;
    }

    const validation = validatePayload(data, ["conversation", "message_key"]);
    if (!validation.valid) {
      console.warn(
        `[join_stream] Invalid payload from ${socket.id}:`,
        validation.error
      );
      socket.emit("error", { message: validation.error });
      return;
    }

    const { conversation, message_key } = validation.payload;
    const room = createRoomName(conversation, message_key);

    socket.join(room);
    metrics.totalMessages++;

    console.log(`[JOIN_STREAM] ${socket.id} -> ${room}`, {
      conversation,
      message_key,
      sanitized_room: room,
    });
  });

  socket.on("join_room", (data) => {
    if (!checkRateLimit(socket.id)) {
      socket.emit("error", { message: "Rate limit exceeded" });
      return;
    }

    const validation = validatePayload(data, ["room"]);
    if (!validation.valid) {
      console.warn(
        `[join_room] Invalid payload from ${socket.id}:`,
        validation.error
      );
      socket.emit("error", { message: validation.error });
      return;
    }

    const { room } = validation.payload;
    socket.join(room);
    metrics.totalMessages++;

    console.log(`[JOIN_ROOM] ${socket.id} -> ${room}`);
  });

  socket.on("leave_stream", (data) => {
    if (!checkRateLimit(socket.id)) return;

    const validation = validatePayload(data, ["conversation", "message_key"]);
    if (!validation.valid) return;

    const { conversation, message_key } = validation.payload;
    const room = createRoomName(conversation, message_key);

    socket.leave(room);
    console.log(`[LEAVE_STREAM] ${socket.id} <- ${room}`);
  });

  socket.on("chat_stream_event", (payload) => {
    if (!checkRateLimit(socket.id)) {
      socket.emit("error", { message: "Rate limit exceeded" });
      return;
    }

    try {
      const validation = validatePayload(payload);
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      const data = validation.payload;
      // Use room from payload if available (from Python backend),
      // otherwise construct it (from client)
      const room = data.room || 
        (data.conversation && data.message_key 
          ? createRoomName(data.conversation, data.message_key)
          : null);

      if (!room) {
        throw new Error("Missing room identifier");
      }

      // Debug logging in production for troubleshooting
      if (IS_PRODUCTION && metrics.totalMessages % 100 === 0) {
        console.log(`[STREAM] ${socket.id} -> ${room}:`, {
          type: data.type,
          conv: data.conversation,
          key: data.message_key,
        });
      }

      io.to(room).emit("chat_stream_event", data);
      metrics.totalMessages++;

      if (!IS_PRODUCTION) {
        console.log(`[STREAM] ${socket.id} -> ${room}:`, {
          type: data.type,
          conv: data.conversation,
          key: data.message_key,
        });
      }
    } catch (e) {
      metrics.totalErrors++;
      console.error(`[ERROR] chat_stream_event from ${socket.id}:`, e.message);
      socket.emit("error", { message: "Failed to process event" });
    }
  });

  socket.on("generic_event", (payload) => {
    if (!checkRateLimit(socket.id)) {
      socket.emit("error", { message: "Rate limit exceeded" });
      return;
    }

    try {
      const validation = validatePayload(payload);
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      io.emit("generic_event", validation.payload);
      metrics.totalMessages++;

      console.log(`[GENERIC] ${socket.id} broadcast`);
    } catch (e) {
      metrics.totalErrors++;
      console.error(`[ERROR] generic_event from ${socket.id}:`, e.message);
    }
  });

  // ============= Disconnection =============
  socket.on("disconnect", (reason) => {
    metrics.activeConnections--;
    rateLimiter.delete(socket.id);

    console.log(`[DISCONNECT] ${socket.id}:`, {
      reason,
      active: metrics.activeConnections,
      duration: Date.now() - new Date(clientInfo.connectedAt).getTime(),
    });
  });

  socket.on("error", (error) => {
    metrics.totalErrors++;
    console.error(`[SOCKET_ERROR] ${socket.id}:`, error);
  });
});

// ============= Global Error Handling =============
process.on("uncaughtException", (error) => {
  console.error("[UNCAUGHT_EXCEPTION]", error);
  metrics.totalErrors++;
  // Don't exit immediately, log and continue
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("[UNHANDLED_REJECTION]", reason);
  metrics.totalErrors++;
});

// ============= Graceful Shutdown =============
let isShuttingDown = false;

async function gracefulShutdown(signal) {
  if (isShuttingDown) return;
  isShuttingDown = true;

  console.log(`\n[SHUTDOWN] Received ${signal}, starting graceful shutdown...`);

  // Stop accepting new connections
  io.close(() => {
    console.log("[SHUTDOWN] Socket.IO server closed");
  });

  // Close HTTP server
  httpServer.close(() => {
    console.log("[SHUTDOWN] HTTP server closed");
  });

  // Give existing connections time to close
  setTimeout(() => {
    console.log("[SHUTDOWN] Force exit after timeout");
    process.exit(0);
  }, 10000);
}

process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
process.on("SIGINT", () => gracefulShutdown("SIGINT"));

// ============= Cleanup old rate limit records =============
setInterval(() => {
  const now = Date.now();
  for (const [socketId, record] of rateLimiter.entries()) {
    if (now - record.windowStart > RATE_LIMIT_WINDOW * 2) {
      rateLimiter.delete(socketId);
    }
  }
}, RATE_LIMIT_WINDOW);

// ============= Start Server =============
httpServer.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  Socket.IO Server - Production Ready                      ║
╠════════════════════════════════════════════════════════════╣
║  Environment: ${NODE_ENV.padEnd(44)} ║
║  Port: ${String(PORT).padEnd(51)} ║
║  CORS: ${String(CORS_ORIGIN).substring(0, 51).padEnd(51)} ║
║  Auth: ${(AUTH_TOKEN ? "Enabled" : "Disabled").padEnd(51)} ║
║  Max Connections: ${String(MAX_CONNECTIONS).padEnd(40)} ║
║  Rate Limit: ${String(RATE_LIMIT_MAX).padEnd(45)} ║
╠════════════════════════════════════════════════════════════╣
║  Health Check: http://localhost:${PORT}/health${" ".repeat(22)} ║
║  Metrics: http://localhost:${PORT}/metrics${" ".repeat(26)} ║
╚════════════════════════════════════════════════════════════╝
  `);
});
