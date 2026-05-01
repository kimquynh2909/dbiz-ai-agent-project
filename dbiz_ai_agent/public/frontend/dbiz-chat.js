(function () {
  var DEFAULTS = {
    baseUrl: null,
    path: '/ai-agent/widget',
    position: 'right',
    bottom: 24,
    side: 24,
    zIndex: 2147483647,
    open: false,
    width: 380,
    height: 640,
    autologinRepeat: true,
    widgetSecret: null,
  }

  var state = {
    inited: false,
    open: false,
    opts: null,
    container: null,
    iframe: null,
    externalButtons: [],
  }

  function emitWidgetEvent(name) {
    if (typeof window === 'undefined' || typeof window.dispatchEvent !== 'function' || typeof window.CustomEvent !== 'function') {
      return
    }
    try {
      var detail = { open: state.open }
      window.dispatchEvent(new CustomEvent('dbizchatwidget:' + name, { detail: detail }))
    } catch (e) {
      /* ignore */
    }
  }

  function onDomReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn)
    } else {
      fn()
    }
  }

  function getScriptTag() {
    try {
      var s = document.currentScript
      if (s && s.src && s.src.indexOf('dbiz-chat.js') !== -1) return s
      var scripts = document.getElementsByTagName('script')
      for (var i = scripts.length - 1; i >= 0; i--) {
        if (scripts[i].src && scripts[i].src.indexOf('dbiz-chat.js') !== -1) return scripts[i]
      }
    } catch (e) {}
    return null
  }

  function getScriptOrigin() {
    try {
      var s = getScriptTag()
      if (!s || !s.src) return window.location.origin
      var u = new URL(s.src)
      return u.origin
    } catch (e) {
      try {
        return window.location.origin
      } catch (_) {
        return ''
      }
    }
  }

  function coerce(key, val) {
    if (val == null) return val
    if (key === 'open') return val === true || val === 'true' || val === '1'
    if (key === 'bottom' || key === 'side' || key === 'width' || key === 'height' || key === 'zIndex') {
      var n = parseInt(val, 10)
      return isNaN(n) ? undefined : n
    }
    return val
  }

  function parseOptionsFromScript() {
    var out = {}
    var s = getScriptTag()
    try {
      if (s) {
        var ds = s.dataset || {}
        if (ds.zIndex) out.zIndex = coerce('zIndex', ds.zIndex)
        if (ds.username) out.username = ds.username
        if (ds.password) out.password = ds.password
        if (ds.secret) out.widgetSecret = ds.secret
        if (ds.secretKey) out.widgetSecret = ds.secretKey
        if (ds.widgetSecret) out.widgetSecret = ds.widgetSecret

        if (s.src && s.src.indexOf('?') !== -1) {
          var u = new URL(s.src)
          u.searchParams.forEach(function (v, k) {
            if (k === 'zIndex') out.zIndex = coerce('zIndex', v)
            if (k === 'username') out.username = v
            if (k === 'password') out.password = v
            if (k === 'secret' || k === 'secretKey' || k === 'widgetSecret') out.widgetSecret = v
          })
        }
      }
    } catch (e) {
      /* ignore */
    }
    try {
      if (window.DbizChatBaseUrl) out.baseUrl = window.DbizChatBaseUrl
      if (window.DbizChatWidgetConfig && typeof window.DbizChatWidgetConfig === 'object') {
        out = Object.assign({}, out, window.DbizChatWidgetConfig)
      }
    } catch (e) {
      /* ignore */
    }
    return out
  }

  function createStyles() {
    var css =
      '' +
      '.dbizcw-container{position:fixed;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;box-shadow:0 16px 48px rgba(0,0,0,.2);min-width:400px !important;min-height:480px !important;}' +
      '.dbizcw-hidden{display:none !important;}' +
      '.dbizcw-iframe{border:0;width:100%;height:100%;min-height:480px !important;}'
    var el = document.createElement('style')
    el.type = 'text/css'
    el.setAttribute('data-dbizz', 'true')
    el.appendChild(document.createTextNode(css))
    document.head.appendChild(el)
  }

  function createContainer(opts) {
    var existing = document.getElementById('dbizcw-container')
    if (existing) {
      var ifr = existing.querySelector('iframe.dbizcw-iframe')
      return { container: existing, iframe: ifr }
    }
    var c = document.createElement('div')
    c.className = 'dbizcw-container dbizcw-hidden'
    c.id = 'dbizcw-container'
    c.style.width = DEFAULTS.width + 'px'
    c.style.height = DEFAULTS.height + 'px'
    c.style.zIndex = String(opts.zIndex)
    c.style.bottom = DEFAULTS.bottom + 'px'
    if (DEFAULTS.position === 'left') {
      c.style.left = DEFAULTS.side + 'px'
      c.style.right = 'auto'
    } else {
      c.style.right = DEFAULTS.side + 'px'
      c.style.left = 'auto'
    }

    var iframe = document.createElement('iframe')
    iframe.className = 'dbizcw-iframe'
    iframe.setAttribute('allow', 'microphone; camera; autoplay; clipboard-write; encrypted-media;')
    c.appendChild(iframe)

    try {
      var handles = []
      function makeHandle(position) {
        var h = document.createElement('div')
        h.setAttribute('data-dbizz-resizer', position)
        h.style.position = 'absolute'
        h.style.zIndex = String((opts.zIndex || DEFAULTS.zIndex) + 10000)
        if (position === 'br') {
          h.style.width = '20px'
          h.style.height = '20px'
          h.style.right = '-6px'
          h.style.bottom = '-6px'
          h.style.cursor = 'se-resize'
          h.style.background = 'rgba(0,0,0,0.08)'
          h.style.border = '1px solid rgba(0,0,0,0.12)'
          h.style.borderRadius = '4px'
        } else if (position === 'left') {
          h.style.width = '18px'
          h.style.height = '100%'
          h.style.left = '-6px'
          h.style.top = '0px'
          h.style.cursor = 'ew-resize'
          h.style.background = 'transparent'
        } else if (position === 'top') {
          h.style.height = '18px'
          h.style.width = '100%'
          h.style.top = '-6px'
          h.style.left = '0px'
          h.style.cursor = 'ns-resize'
          h.style.background = 'transparent'
        }
        h.style.touchAction = 'none'
        h.style.pointerEvents = 'auto'
        c.appendChild(h)
        handles.push(h)
        return h
      }

      var br = makeHandle('br')
      var leftHandle = makeHandle('left')
      var topHandle = makeHandle('top')

      var headerOverlay = document.createElement('div')
      headerOverlay.setAttribute('data-dbizz-header-drag', 'true')
      headerOverlay.style.position = 'absolute'
      headerOverlay.style.top = '18px'
      headerOverlay.style.left = '0'
      headerOverlay.style.right = '100px'
      headerOverlay.style.height = '38px'
      headerOverlay.style.cursor = 'move'
      headerOverlay.style.zIndex = String((opts.zIndex || DEFAULTS.zIndex) + 10000)
      headerOverlay.style.touchAction = 'none'
      headerOverlay.style.pointerEvents = 'auto'
      headerOverlay.style.background = 'transparent'
      c.appendChild(headerOverlay)
      handles.push(headerOverlay)

      function onHeaderDblClick(e) {
        try {
          if (c._dbiz_is_maximized) {
            var prev = c._dbiz_prev_bounds || {}
            if (prev.left != null) c.style.left = prev.left
            if (prev.top != null) c.style.top = prev.top
            if (prev.right != null) c.style.right = prev.right
            if (prev.bottom != null) c.style.bottom = prev.bottom
            if (prev.width != null) c.style.width = prev.width
            if (prev.height != null) c.style.height = prev.height
            c._dbiz_is_maximized = false
          } else {
            c._dbiz_prev_bounds = {
              left: c.style.left || null,
              top: c.style.top || null,
              right: c.style.right || null,
              bottom: c.style.bottom || null,
              width: c.style.width || null,
              height: c.style.height || null,
            }
            var margin = 20
            var w = Math.max(360, Math.min(window.innerWidth - margin * 2, Math.floor(window.innerWidth * 0.9)))
            var h = Math.max(480, Math.min(window.innerHeight - margin * 2, Math.floor(window.innerHeight * 0.9)))
            c.style.left = margin + 'px'
            c.style.top = margin + 'px'
            c.style.right = 'auto'
            c.style.bottom = 'auto'
            c.style.width = w + 'px'
            c.style.height = h + 'px'
            c._dbiz_is_maximized = true
          }
        } catch (err) {}
        if (e && e.preventDefault) e.preventDefault()
        return false
      }
      headerOverlay.addEventListener('dblclick', onHeaderDblClick)

      var cleanups = []
      var minW = 360,
        minH = 480

      function addMove(handle) {
        var isDragging = false
        var startX = 0,
          startY = 0,
          rect = null
        var rafId = null
        var pending = null
        var lastRect = null
        var overlay = null
        var lastTarget = null

        function applyPending() {
          rafId = null
          if (!pending) return
          try {
            if (overlay) {
              var tx = pending.left - rect.left
              var ty = pending.top - rect.top
              overlay.style.transform = 'translate(' + (tx | 0) + 'px,' + (ty | 0) + 'px)'
              lastTarget = pending
            } else {
              c.style.left = pending.left + 'px'
              c.style.top = pending.top + 'px'
              c.style.right = 'auto'
              c.style.bottom = 'auto'
            }
          } catch (e) {}
          try {
            lastRect = c.getBoundingClientRect()
          } catch (e) {
            lastRect = null
          }
          pending = null
        }

        var origBoxShadow = null,
          origTransition = null,
          origWillChange = null

        function scheduleUpdate(values) {
          if (!pending) pending = {}
          for (var k in values) pending[k] = values[k]
          if (rafId == null) rafId = window.requestAnimationFrame(applyPending)
        }

        function onMove(e) {
          if (!isDragging) return
          var clientX = e.touches ? e.touches[0].clientX : e.clientX
          var clientY = e.touches ? e.touches[0].clientY : e.clientY
          try {
            var r = lastRect || rect
            var dx = clientX - startX
            var dy = clientY - startY
            var newLeft = Math.max(0, Math.min(r.left + dx, window.innerWidth - r.width))
            var newTop = Math.max(0, Math.min(r.top + dy, window.innerHeight - r.height))
            scheduleUpdate({ left: newLeft, top: newTop })
          } catch (err) {}
          if (e.preventDefault) e.preventDefault()
        }

        function onUp() {
          if (!isDragging) return
          isDragging = false
          try {
            window.removeEventListener('mousemove', onMove)
          } catch (e) {}
          try {
            window.removeEventListener('mouseup', onUp)
          } catch (e) {}
          try {
            window.removeEventListener('touchmove', onMove)
          } catch (e) {}
          try {
            window.removeEventListener('touchend', onUp)
          } catch (e) {}
          if (rafId != null) {
            try {
              window.cancelAnimationFrame(rafId)
            } catch (e) {}
            rafId = null
          }
          if (pending) applyPending()
          try {
            if (origBoxShadow !== null) c.style.boxShadow = origBoxShadow
            if (origTransition !== null) c.style.transition = origTransition
            if (origWillChange !== null) c.style.willChange = origWillChange
          } catch (e) {}
          origBoxShadow = origTransition = origWillChange = null
          try {
            if (overlay) {
              try {
                if (lastTarget) {
                  c.style.left = lastTarget.left + 'px'
                  c.style.top = lastTarget.top + 'px'
                  c.style.right = 'auto'
                  c.style.bottom = 'auto'
                }
              } catch (e) {}
              try {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay)
              } catch (e) {}
              overlay = null
              lastTarget = null
            }
            try {
              if (iframe && iframe.style) iframe.style.pointerEvents = ''
            } catch (e) {}
          } catch (e) {}
        }

        function onDown(e) {
          isDragging = true
          startX = e.touches ? e.touches[0].clientX : e.clientX
          startY = e.touches ? e.touches[0].clientY : e.clientY
          rect = c.getBoundingClientRect()
          lastRect = rect
          try {
            overlay = document.createElement('div')
            overlay.style.position = 'fixed'
            overlay.style.left = rect.left + 'px'
            overlay.style.top = rect.top + 'px'
            overlay.style.width = rect.width + 'px'
            overlay.style.height = rect.height + 'px'
            overlay.style.border = '1px dashed rgba(0,0,0,0.12)'
            overlay.style.background = 'rgba(0,0,0,0.02)'
            overlay.style.borderRadius = '12px'
            overlay.style.zIndex = String((opts.zIndex || DEFAULTS.zIndex) + 10001)
            overlay.style.pointerEvents = 'none'
            overlay.style.willChange = 'transform'
            overlay.style.transformOrigin = '0 0'
            document.body.appendChild(overlay)
            try {
              if (iframe && iframe.style) iframe.style.pointerEvents = 'none'
            } catch (e) {}
          } catch (e) {
            overlay = null
          }
          try {
            origBoxShadow = c.style.boxShadow == null ? '' : c.style.boxShadow
            origTransition = c.style.transition == null ? '' : c.style.transition
            origWillChange = c.style.willChange == null ? '' : c.style.willChange
            c.style.boxShadow = 'none'
            c.style.transition = 'none'
            c.style.willChange = 'transform, left, top'
          } catch (e) {}
          window.addEventListener('mousemove', onMove)
          window.addEventListener('mouseup', onUp)
          window.addEventListener('pointerup', onUp)
          window.addEventListener('pointercancel', onUp)
          window.addEventListener('touchmove', onMove, { passive: false })
          window.addEventListener('touchend', onUp)
          if (e.preventDefault) e.preventDefault()
        }

        handle.addEventListener('mousedown', onDown)
        handle.addEventListener('touchstart', onDown)

        cleanups.push(function () {
          try {
            handle.removeEventListener('mousedown', onDown)
            handle.removeEventListener('touchstart', onDown)
            window.removeEventListener('mousemove', onMove)
            window.removeEventListener('mouseup', onUp)
            window.removeEventListener('pointerup', onUp)
            window.removeEventListener('pointercancel', onUp)
            window.removeEventListener('touchmove', onMove)
            window.removeEventListener('touchend', onUp)
          } catch (e) {}
          if (rafId != null) {
            try {
              window.cancelAnimationFrame(rafId)
            } catch (e) {}
            rafId = null
          }
          try {
            if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay)
          } catch (e) {}
          overlay = null
        })
      }

      function addDrag(handle, mode) {
        var isResizing = false
        var startX = 0,
          startY = 0,
          rect = null
        var rafId = null
        var pending = null
        var lastRect = null
        var overlay = null
        var lastTarget = null

        function applyPending() {
          rafId = null
          if (!pending) return
          try {
            if (overlay) {
              var t = pending.transform || { tx: 0, ty: 0, sx: 1, sy: 1 }
              overlay.style.transform =
                'translate(' + (t.tx | 0) + 'px,' + (t.ty | 0) + 'px) scale(' + t.sx + ',' + t.sy + ')'
              lastTarget = pending.target || null
            } else {
              if (pending.setPosition === 'br') {
                if (pending.width != null) c.style.width = pending.width + 'px'
                if (pending.height != null) c.style.height = pending.height + 'px'
              } else if (pending.setPosition === 'left') {
                if (pending.left != null) {
                  c.style.right = 'auto'
                  c.style.left = pending.left + 'px'
                }
                if (pending.width != null) c.style.width = pending.width + 'px'
              } else if (pending.setPosition === 'top') {
                if (pending.top != null) {
                  c.style.bottom = 'auto'
                  c.style.top = pending.top + 'px'
                }
                if (pending.height != null) c.style.height = pending.height + 'px'
              }
            }
          } catch (e) {}
          try {
            lastRect = c.getBoundingClientRect()
          } catch (e) {
            lastRect = null
          }
          pending = null
        }
        var origBoxShadow = null,
          origTransition = null,
          origWillChange = null

        function scheduleUpdate(values) {
          if (!pending) pending = {}
          for (var k in values) pending[k] = values[k]
          if (rafId == null) rafId = window.requestAnimationFrame(applyPending)
        }

        function onMove(e) {
          if (!isResizing) return
          var clientX = e.touches ? e.touches[0].clientX : e.clientX
          var clientY = e.touches ? e.touches[0].clientY : e.clientY
          try {
            var r = lastRect || rect
            if (mode === 'br') {
              var dx = clientX - startX
              var dy = clientY - startY
              var newW = Math.max(minW, Math.min(r.width + dx, window.innerWidth - 40))
              var newH = Math.max(minH, Math.min(r.height + dy, window.innerHeight - 40))
              var tx = 0,
                ty = 0,
                sx = newW / rect.width,
                sy = newH / rect.height
              scheduleUpdate({
                transform: { tx: tx, ty: ty, sx: sx, sy: sy },
                target: { left: rect.left, top: rect.top, width: newW, height: newH },
              })
            } else if (mode === 'left') {
              var newLeft = Math.max(0, Math.min(clientX, r.right - minW))
              var newW = Math.max(minW, r.right - newLeft)
              var tx = newLeft - rect.left,
                ty = 0,
                sx = newW / rect.width,
                sy = 1
              scheduleUpdate({
                transform: { tx: tx, ty: ty, sx: sx, sy: sy },
                target: { left: newLeft, top: rect.top, width: newW, height: rect.height },
              })
            } else if (mode === 'top') {
              var newTop = Math.max(0, Math.min(clientY, r.bottom - minH))
              var newH = Math.max(minH, r.bottom - newTop)
              var tx = 0,
                ty = newTop - rect.top,
                sx = 1,
                sy = newH / rect.height
              scheduleUpdate({
                transform: { tx: tx, ty: ty, sx: sx, sy: sy },
                target: { left: rect.left, top: newTop, width: rect.width, height: newH },
              })
            }
          } catch (err) {}
          if (e.preventDefault) e.preventDefault()
        }

        function onUp() {
          if (!isResizing) return
          isResizing = false
          try {
            window.removeEventListener('mousemove', onMove)
          } catch (e) {}
          try {
            window.removeEventListener('mouseup', onUp)
          } catch (e) {}
          try {
            window.removeEventListener('touchmove', onMove)
          } catch (e) {}
          try {
            window.removeEventListener('touchend', onUp)
          } catch (e) {}
          if (rafId != null) {
            try {
              window.cancelAnimationFrame(rafId)
            } catch (e) {}
            rafId = null
          }
          if (pending) applyPending()
          try {
            if (origBoxShadow !== null) c.style.boxShadow = origBoxShadow
            if (origTransition !== null) c.style.transition = origTransition
            if (origWillChange !== null) c.style.willChange = origWillChange
          } catch (e) {}
          origBoxShadow = origTransition = origWillChange = null
          try {
            if (overlay) {
              try {
                if (lastTarget) {
                  c.style.right = 'auto'
                  c.style.left = lastTarget.left != null ? lastTarget.left + 'px' : c.style.left
                  c.style.top = lastTarget.top != null ? lastTarget.top + 'px' : c.style.top
                  c.style.bottom = 'auto'
                  if (lastTarget.width != null) c.style.width = lastTarget.width + 'px'
                  if (lastTarget.height != null) c.style.height = lastTarget.height + 'px'
                }
              } catch (e) {}
              try {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay)
              } catch (e) {}
              overlay = null
              lastTarget = null
            }
            try {
              if (iframe && iframe.style) iframe.style.pointerEvents = ''
            } catch (e) {}
          } catch (e) {}
        }

        function onDown(e) {
          isResizing = true
          startX = e.touches ? e.touches[0].clientX : e.clientX
          startY = e.touches ? e.touches[0].clientY : e.clientY
          rect = c.getBoundingClientRect()
          lastRect = rect
          try {
            overlay = document.createElement('div')
            overlay.style.position = 'fixed'
            overlay.style.left = rect.left + 'px'
            overlay.style.top = rect.top + 'px'
            overlay.style.width = rect.width + 'px'
            overlay.style.height = rect.height + 'px'
            overlay.style.border = '1px dashed rgba(0,0,0,0.12)'
            overlay.style.background = 'rgba(0,0,0,0.02)'
            overlay.style.borderRadius = '12px'
            overlay.style.zIndex = String((opts.zIndex || DEFAULTS.zIndex) + 10001)
            overlay.style.pointerEvents = 'none'
            overlay.style.willChange = 'transform'
            overlay.style.transformOrigin = '0 0'
            document.body.appendChild(overlay)
            try {
              if (iframe && iframe.style) iframe.style.pointerEvents = 'none'
            } catch (e) {}
          } catch (e) {
            overlay = null
          }
          try {
            origBoxShadow = c.style.boxShadow == null ? '' : c.style.boxShadow
            origTransition = c.style.transition == null ? '' : c.style.transition
            origWillChange = c.style.willChange == null ? '' : c.style.willChange
            c.style.boxShadow = 'none'
            c.style.transition = 'none'
            c.style.willChange = 'width, height, left, top'
          } catch (e) {}
          window.addEventListener('mousemove', onMove)
          window.addEventListener('mouseup', onUp)
          window.addEventListener('pointerup', onUp)
          window.addEventListener('pointercancel', onUp)
          window.addEventListener('touchmove', onMove, { passive: false })
          window.addEventListener('touchend', onUp)
          if (e.preventDefault) e.preventDefault()
        }

        handle.addEventListener('mousedown', onDown)
        handle.addEventListener('touchstart', onDown)

        cleanups.push(function () {
          try {
            handle.removeEventListener('mousedown', onDown)
            handle.removeEventListener('touchstart', onDown)
            window.removeEventListener('mousemove', onMove)
            window.removeEventListener('mouseup', onUp)
            window.removeEventListener('pointerup', onUp)
            window.removeEventListener('pointercancel', onUp)
            window.removeEventListener('touchmove', onMove)
            window.removeEventListener('touchend', onUp)
          } catch (e) {}
          if (rafId != null) {
            try {
              window.cancelAnimationFrame(rafId)
            } catch (e) {}
            rafId = null
          }
          try {
            if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay)
          } catch (e) {}
          overlay = null
        })
      }

      addDrag(br, 'br')
      addDrag(leftHandle, 'left')
      addDrag(topHandle, 'top')
      addMove(headerOverlay)

      c._dbiz_resize_cleanup = function () {
        try {
          cleanups.forEach(function (fn) {
            try {
              fn()
            } catch (e) {}
          })
          try {
            headerOverlay.removeEventListener('dblclick', onHeaderDblClick)
          } catch (e) {}
          handles.forEach(function (h) {
            try {
              if (h.parentNode) h.parentNode.removeChild(h)
            } catch (e) {}
          })
        } catch (e) {}
      }
    } catch (e) {}
    document.body.appendChild(c)

    try {
      if (opts.username && opts.password) {
        var origin = getScriptOrigin() || window.location.origin
        var guardKey = 'dbiz_login_done:' + origin
        var allowRepeat = opts.autologinRepeat !== false
        var already = false
        if (!allowRepeat) {
          try {
            already = sessionStorage.getItem(guardKey) === '1'
          } catch (e) {}
        } else {
          try {
            sessionStorage.removeItem(guardKey)
          } catch (e) {}
        }
        if (already) {
          iframe.src = buildIframeUrl(opts)
        } else {
          performAutologin(origin, opts).then(function (res) {
            if (res && res.ok) {
              if (!allowRepeat) {
                try {
                  sessionStorage.setItem(guardKey, '1')
                } catch (e) {}
              }
            } else {
              console.warn('[DbizChatWidget] Đăng nhập thất bại qua autologin:', (res && (res.reason || res.error)) || res)
              if (!allowRepeat) {
                try {
                  sessionStorage.removeItem(guardKey)
                } catch (e) {}
              }
            }
            try {
              iframe.src = buildIframeUrl(opts)
            } catch (e) {
              console.warn('[DbizChatWidget] Lỗi set iframe.src', e)
            }
          })
        }
      } else {
        iframe.src = buildIframeUrl(opts)
      }
    } catch (e) {
      try {
        iframe.src = buildIframeUrl(opts)
      } catch (er) {
        opts.debug && console && console.warn && console.warn('[DbizChatWidget] createContainer error', er)
      }
    }

    return { container: c, iframe: iframe }
  }

  function buildIframeUrl(opts) {
    var origin = (opts.baseUrl || getScriptOrigin()).replace(/\/$/, '')
    var path = opts.path || DEFAULTS.path
    var url = origin + path
    var params = []
    try {
      params.push('parent_origin=' + encodeURIComponent(window.location.origin))
    } catch (e) {}
    if (params.length) url += '?' + params.join('&')
    return url
  }

  function performAutologin(origin, opts) {
    return new Promise(function (resolve) {
      try {
        if (!opts || !opts.username || !opts.password) return resolve({ ok: false, reason: 'no-creds' })

        var baseOrigin = (origin || '').replace(/\/$/, '')
        var apiPaths = ['/api/method/dbiz_ai_agent.api.auth.login', '/api/method/login', '/api/auth/login']

        var pi = 0
        function tryNext() {
          if (pi >= apiPaths.length) return resolve({ ok: false, reason: 'all-failed' })
          var path = apiPaths[pi]
          var loginUrl = baseOrigin + path

          fetch(loginUrl, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: opts.username, password: opts.password }),
          })
            .then(function (resp) {
              if (resp.ok) {
                console.log('[DbizChatWidget] login thành công', loginUrl, resp.status)
                return resolve({ ok: true, url: loginUrl })
              }
              resp
                .text()
                .then(function (t) {
                  console.warn('[DbizChatWidget] login thất bại', loginUrl, resp.status, t)
                  pi++
                  tryNext()
                })
                .catch(function () {
                  pi++
                  tryNext()
                })
            })
            .catch(function (err) {
              console.error(
                '[DbizChatWidget] Lỗi login (network/CORS)',
                loginUrl,
                err && err.message ? err.message : err
              )
              pi++
              tryNext()
            })
        }

        tryNext()
      } catch (e) {
        console.error('[DbizChatWidget] login exception', e)
        resolve({ ok: false, error: e })
      }
    })
  }

  function verifyWidgetSecret(origin, opts) {
    return new Promise(function (resolve) {
      try {
        var secret = opts.widgetSecret
        if (!secret) {
          console.warn('[DbizChatWidget] Missing widget secret; widget will not initialize')
          return resolve({ ok: false, reason: 'missing-secret' })
        }

        var baseOrigin = (origin || '').replace(/\/$/, '')
        var verifyUrl = baseOrigin + '/api/method/dbiz_ai_agent.api.auth.verify_widget_secret'

        fetch(verifyUrl, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ secret: secret }),
        })
          .then(function (resp) {
            if (!resp.ok) {
              return resolve({ ok: false, reason: 'verify-failed' })
            }
            resp
              .json()
              .then(function (payload) {
                var msg = payload && payload.message
                if (msg && (msg.success === true || msg.verified === true)) {
                  resolve({ ok: true, origin: baseOrigin })
                } else {
                  resolve({ ok: false, reason: 'invalid-secret' })
                }
              })
              .catch(function () {
                resolve({ ok: false, reason: 'parse-error' })
              })
          })
          .catch(function () {
            resolve({ ok: false, reason: 'network-error' })
          })
      } catch (err) {
        console.error('[DbizChatWidget] Error verifying widget secret', err)
        resolve({ ok: false, error: err })
      }
    })
  }

  function open() {
    if (!state.inited) return
    state.container.classList.remove('dbizcw-hidden')
    state.open = true
    syncExternalButtons(true)
    emitWidgetEvent('open')
    emitWidgetEvent('state')
  }

  function close() {
    if (!state.inited) return
    state.container.classList.add('dbizcw-hidden')
    state.open = false
    syncExternalButtons(false)
    emitWidgetEvent('close')
    emitWidgetEvent('state')
  }

  function toggle() {
    state.open ? close() : open()
  }

  function syncExternalButtons(isOpen) {
    if (!state.externalButtons || !state.externalButtons.length) return
    state.externalButtons.forEach(function (btn) {
      try {
        btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false')
        if (isOpen) {
          btn.classList.add('is-open')
        } else {
          btn.classList.remove('is-open')
        }
      } catch (e) {}
    })
  }

  function detachExternalButtons() {
    if (!state.externalButtons || !state.externalButtons.length) return
    state.externalButtons.forEach(function (btn) {
      try {
        btn.removeEventListener('click', onExternalButtonClick)
      } catch (e) {}
    })
    state.externalButtons = []
  }

  function attachExternalButtons() {
    onDomReady(function () {
      try {
        var buttons = document.querySelectorAll('.dbiz-chatbot__button')
        if (!buttons || !buttons.length) {
          console.warn('[DbizChatWidget] No .dbiz-chatbot__button found to control the widget')
          return
        }
        detachExternalButtons()
        var filtered = Array.prototype.slice
          .call(buttons)
          .filter(function (btn) {
            return !btn.hasAttribute('data-dbizz-manual-control')
          })

        if (!filtered.length) {
          return
        }

        state.externalButtons = filtered
        state.externalButtons.forEach(function (btn) {
          btn.addEventListener('click', onExternalButtonClick)
          btn.setAttribute('aria-expanded', state.open ? 'true' : 'false')
        })
      } catch (e) {}
    })
  }

  function onExternalButtonClick(e) {
    if (e && typeof e.preventDefault === 'function') e.preventDefault()
    toggle()
  }

  function destroy() {
    try {
      window.removeEventListener('message', onMessage)
    } catch (e) {}
    detachExternalButtons()
    if (state.container) {
      try {
        if (typeof state.container._dbiz_resize_cleanup === 'function') state.container._dbiz_resize_cleanup()
      } catch (e) {}
      if (state.container.parentNode) state.container.parentNode.removeChild(state.container)
    }
    state.inited = false
    state.open = false
    state.container = null
    state.iframe = null
  }

  function onMessage(ev) {
    try {
      if (!ev || !ev.data) return
      var data = ev.data
      if (typeof data === 'string') {
        try {
          data = JSON.parse(data)
        } catch (_) {}
      }
      if (!data || !data.type) return
      if (data.type === 'DBIZ_CHAT:CLOSE') close()
      if (data.type === 'DBIZ_CHAT:OPEN') open()
      if (data.type === 'DBIZ_CHAT:TOGGLE') toggle()
      if (data.type === 'DBIZ_CHAT:FOCUS') {
        try {
          if (state.iframe && state.iframe.contentWindow) state.iframe.contentWindow.focus()
        } catch (e) {}
      }
      if (
        data.type === 'DBIZ_WIDGET:START_DRAG' ||
        data.type === 'DBIZ_WIDGET:DRAG_MOVE' ||
        data.type === 'DBIZ_WIDGET:END_DRAG'
      ) {
        return
      }
    } catch (e) {}
  }

  async function init(options) {
    if (state.inited) {
      console.log('[DbizChatWidget] init called but already initialized')
      return
    }
    var pre = document.getElementById('dbizcw-container')
    if (pre) {
      console.log('[DbizChatWidget] adopting existing container during init (likely previous inject)')
      state.container = pre
      state.iframe = pre.querySelector('iframe.dbizcw-iframe')
      state.inited = true
      state.open = !pre.classList.contains('dbizcw-hidden')
      window.addEventListener('message', onMessage)
      attachExternalButtons()
      if (state.open) {
        open()
      } else {
        close()
      }
      return
    }
    var fromScript = parseOptionsFromScript()
    var opts = Object.assign({}, DEFAULTS, fromScript, options || {})
    var logSafeOpts = Object.assign({}, opts)
    if (logSafeOpts.widgetSecret) logSafeOpts.widgetSecret = '[redacted]'
    console.log('[DbizChatWidget] init options', logSafeOpts)
    if (!opts.baseUrl) opts.baseUrl = getScriptOrigin()

    var verificationOrigin = opts.baseUrl || getScriptOrigin() || window.location.origin
    var verification = await verifyWidgetSecret(verificationOrigin, opts)
    if (!verification.ok) {
      console.error('[DbizChatWidget] Widget secret verification failed', verification)
      return
    }
    if (verification.origin) opts.baseUrl = verification.origin
    opts.widgetSecret = undefined

    try {
      if (opts.debug) {
        window._dbiz_unload_guard = function (e) {
          var msg = 'Page is about to be reloaded. Press Cancel to inspect console/logs.'
          e = e || window.event
          if (e) e.returnValue = msg
          return msg
        }
        window.addEventListener('beforeunload', window._dbiz_unload_guard)

        try {
          var dbgBtn = document.createElement('button')
          dbgBtn.textContent = 'Allow reload'
          dbgBtn.title = 'Disable automatic reload guard'
          dbgBtn.style.position = 'fixed'
          dbgBtn.style.right = '12px'
          dbgBtn.style.top = '12px'
          dbgBtn.style.zIndex = String((opts.zIndex || DEFAULTS.zIndex) + 2000)
          dbgBtn.style.padding = '6px 10px'
          dbgBtn.style.borderRadius = '6px'
          dbgBtn.style.border = 'none'
          dbgBtn.style.background = '#fff'
          dbgBtn.style.color = '#111'
          dbgBtn.style.cursor = 'pointer'
          dbgBtn.addEventListener('click', function () {
            try {
              window.removeEventListener('beforeunload', window._dbiz_unload_guard)
            } catch (e) {}
            dbgBtn.parentNode && dbgBtn.parentNode.removeChild(dbgBtn)
          })
          document.addEventListener('DOMContentLoaded', function () {
            document.body && document.body.appendChild(dbgBtn)
          })
          if (document.readyState !== 'loading') document.body && document.body.appendChild(dbgBtn)
        } catch (e) {}
      }
    } catch (e) {}

    createStyles()
    var built = createContainer(opts)
    state.container = built.container
    state.iframe = built.iframe
    state.opts = opts
    state.inited = true
    window.addEventListener('message', onMessage)
    attachExternalButtons()
    if (opts.open) {
      open()
    } else {
      emitWidgetEvent('state')
    }
  }

  window.DbizChatWidget = {
    init: init,
    open: open,
    close: close,
    toggle: toggle,
    destroy: destroy,
    isOpen: function () {
      return !!state.open
    },
  }

  try {
    var s = getScriptTag()
    var shouldAutoInit = false
    if (s) {
      var ds = s.dataset || {}
      if (ds.autoInit != null) {
        shouldAutoInit = ds.autoInit === '' || ds.autoInit === 'true' || ds.autoInit === '1'
      }
      if (!shouldAutoInit && s.src && s.src.indexOf('?') !== -1) {
        var u = new URL(s.src)
        var ai = u.searchParams.get('autoInit')
        if (ai != null) shouldAutoInit = ai === '1' || ai === 'true'
      }
    }
    if (shouldAutoInit)
      init().catch(function (err) {
        console.error('[DbizChatWidget] Auto init failed', err)
      })
  } catch (e) {}
})()

