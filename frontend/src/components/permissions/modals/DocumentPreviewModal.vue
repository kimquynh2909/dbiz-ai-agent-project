<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-5xl"
    :panel-class="'bg-white rounded-[32px] w-[90%] max-w-7xl max-h-[92vh] overflow-hidden shadow-2xl flex flex-col'"
    @close="close"
  >
    <!-- Hero header -->
    <DocumentPreviewHeader
      :title="title"
      :mime="mime"
      :url="url"
      :suggested-filename="suggestedFilename"
      @close="close"
      @open-in-new-tab="openInNewTab"
    />
    <!-- Preview body -->
    <div class="flex-1 min-h-0 px-12 py-3 overflow-auto">
      <div class="relative min-h-0 rounded-2xl border border-gray-100 shadow-inner">
        <div v-if="loading" class="flex items-center justify-center h-full">
          <div class="animate-spin rounded-2xl h-10 w-10 border-b-2 border-indigo-600"></div>
        </div>

        <template v-else-if="error">
          <div class="text-center text-red-600 text-sm sm:text-base">
            {{ error }}
          </div>
        </template>

        <template v-else-if="isPdf">
          <iframe
            :src="displayUrl"
            class="w-full rounded-xl border border-gray-200"
            style="height: 60vh; max-height: calc(92vh - 10rem)"
            frameborder="0"
          ></iframe>
        </template>

        <template v-else-if="isImage">
          <img
            :src="displayUrl"
            class="mx-auto max-h-[60vh] rounded-xl shadow-lg"
            :alt="t('chatbotPermissions.documents.preview.imageAlt')"
          />
        </template>

        <template v-else-if="isText">
          <pre class="whitespace-pre-wrap text-sm text-gray-800 font-mono leading-relaxed">{{ textContent }}</pre>
        </template>

        <template v-else-if="isDocx">
          <div v-if="docHtml" class="docx-preview rounded-2xl" v-html="docHtml"></div>
          <div v-else class="text-center text-gray-600 space-y-2">
            <p>{{ t('chatbotPermissions.documents.preview.docx.notConvertible') }}</p>
            <p>{{ t('chatbotPermissions.documents.preview.docx.openOrDownload') }}</p>
          </div>
        </template>

        <template v-else>
          <div class="text-center text-gray-600 space-y-2">
            <p>{{ t('chatbotPermissions.documents.preview.unsupported.title') }}</p>
            <p>{{ t('chatbotPermissions.documents.preview.unsupported.hint') }}</p>
          </div>
        </template>
      </div>
    </div>
    <!-- Footer Actions -->
    <div class="px-8 py-4"></div>
  </ModalBase>
</template>

<script setup>
import { ref, watch, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import ModalBase from '@/components/base/ModalBase.vue'
import DocumentPreviewHeader from '../common/DocumentPreviewHeader.vue'
const props = defineProps({
  visible: { type: Boolean, default: false },
  url: { type: String, default: '' },
  mime: { type: String, default: '' },
  title: { type: String, default: '' },
})
const emit = defineEmits(['close'])
const { t } = useI18n()

const textContent = ref('')
const displayUrl = ref('')
const loading = ref(false)
const error = ref('')
let generatedBlobUrl = ''
let tempHtmlBlobUrl = ''
let currentAbortController = null
let currentTimeoutId = null

const suggestedFilename = computed(() => {
  try {
    if (!props.url) return ''
    const parts = props.url.split('/')
    return parts[parts.length - 1].split('?')[0]
  } catch (e) {
    return ''
  }
})

const lowerMime = computed(() => (props.mime || '').toLowerCase())
const isPdf = computed(() => lowerMime.value.includes('pdf') || props.url?.toLowerCase().endsWith('.pdf'))
const isImage = computed(
  () => /(\.png|\.jpe?g|\.gif|\.webp|\.bmp|\.svg)$/i.test(props.url || '') || lowerMime.value.startsWith('image/')
)
const isText = computed(
  () => lowerMime.value.startsWith('text/') || /(\.txt|\.md|\.csv|\.json)$/i.test(props.url || '')
)
const isDocx = computed(
  () =>
    lowerMime.value === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
    props.url?.toLowerCase().endsWith('.docx')
)
const docHtml = ref('')

watch(
  () => props.visible,
  async (v) => {
    // Reset state when closed
    if (!v) {
      textContent.value = ''
      displayUrl.value = ''
      error.value = ''
      loading.value = false
      if (generatedBlobUrl) {
        URL.revokeObjectURL(generatedBlobUrl)
        generatedBlobUrl = ''
      }
      return
    }

    // When opened, try to fetch/prepare preview depending on type
    if (!props.url) {
      error.value = t('chatbotPermissions.documents.preview.errors.noUrl')
      return
    }

    loading.value = true
    error.value = ''
    displayUrl.value = ''

    try {
      // For text, fetch as text
      if (isText.value) {
        // abortable fetch with timeout
        if (currentAbortController) currentAbortController.abort()
        currentAbortController = new AbortController()
        const signal = currentAbortController.signal
        // 15s timeout
        if (currentTimeoutId) clearTimeout(currentTimeoutId)
        currentTimeoutId = setTimeout(() => currentAbortController && currentAbortController.abort(), 15000)

        const res = await fetch(props.url, { credentials: 'include', signal })
        console.debug('Text fetch status:', res.status, 'content-type:', res.headers.get('content-type'))
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        textContent.value = await res.text()
        // clear timeout on success
        if (currentTimeoutId) {
          clearTimeout(currentTimeoutId)
          currentTimeoutId = null
        }
        currentAbortController = null
      } else if (isDocx.value) {
        // Try to convert DOCX to HTML. Avoid a literal import('mammoth') so the
        // bundler doesn't fail when the package isn't installed. Prefer a local
        // install if available at runtime, otherwise fall back to loading the
        // browser build from CDN and using the global `window.mammoth`.
        try {
          if (currentAbortController) currentAbortController.abort()
          currentAbortController = new AbortController()
          const signal = currentAbortController.signal
          if (currentTimeoutId) clearTimeout(currentTimeoutId)
          currentTimeoutId = setTimeout(() => currentAbortController && currentAbortController.abort(), 15000)

          const res = await fetch(props.url, { credentials: 'include', signal })
          if (!res.ok) throw new Error(`HTTP ${res.status}`)
          const arrayBuffer = await res.arrayBuffer()

          const loadMammoth = async () => {
            // Direct dynamic import of the installed mammoth package.
            // No CDN fallback — ensure `mammoth` is installed in frontend/package.json.
            const mod = await import('mammoth')
            return mod?.default ?? mod
          }

          const mammoth = await loadMammoth()
          if (!mammoth || typeof mammoth.convertToHtml !== 'function') {
            throw new Error('mammoth unavailable or invalid')
          }

          const result = await mammoth.convertToHtml({ arrayBuffer })
          docHtml.value = result.value || ''
          // clear timeout/abort state
          if (currentTimeoutId) {
            clearTimeout(currentTimeoutId)
            currentTimeoutId = null
          }
          currentAbortController = null
        } catch (e) {
          console.error('DOCX preview failed:', e)
          // Surface a friendly message in the UI (watch() will set `error`)
          // Normalize AbortError
          if (e && e.name === 'AbortError') {
            throw new Error(t('chatbotPermissions.documents.preview.errors.abort'))
          }
          throw e
        }
      }
      // For PDFs and images, fetch as blob and create object URL to avoid some embedding/CORS issues
      else if (isPdf.value || isImage.value) {
        if (currentAbortController) currentAbortController.abort()
        currentAbortController = new AbortController()
        const signal = currentAbortController.signal
        if (currentTimeoutId) clearTimeout(currentTimeoutId)
        currentTimeoutId = setTimeout(() => currentAbortController && currentAbortController.abort(), 15000)

        const res = await fetch(props.url, { credentials: 'include', signal })
        console.debug('Blob fetch status:', res.status, 'content-type:', res.headers.get('content-type'))
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const blob = await res.blob()
        // createObjectURL is usually safe for same-origin or binary preview; browser will handle mime
        generatedBlobUrl = URL.createObjectURL(blob)
        displayUrl.value = generatedBlobUrl
        if (currentTimeoutId) {
          clearTimeout(currentTimeoutId)
          currentTimeoutId = null
        }
        currentAbortController = null
      }
      // Others: leave displayUrl empty to show fallback
    } catch (e) {
      console.error('Error preparing preview for', props.url, e)
      // If fetch fails due to CORS or auth, provide a helpful message
      error.value = t('chatbotPermissions.documents.preview.errors.loadFailed', { error: e.message || e })
    } finally {
      loading.value = false
    }
  }
)

const close = () => emit('close')

const openInNewTab = () => {
  if (!props.url) return
  const downloadLabel = t('chatbotPermissions.documents.preview.buttons.download')
  const fallbackName = t('chatbotPermissions.documents.preview.documentFallbackName')
  try {
    // If we already created a blob/object URL for preview, open a small wrapper
    // page that embeds the blob and includes a Download button (proxy -> download=1).
    if (displayUrl.value) {
      try {
        const downloadProxy =
          window.location.origin +
          `/api/method/dbiz_ai_agent.document_permissions.serve_file?file_url=${encodeURIComponent(
            props.url
          )}&download=1`
        const title = (props.title || suggestedFilename.value || fallbackName).replace(/[<>]/g, '')
        let embedHtml = ''
        if (isPdf.value) {
          embedHtml = `<iframe src="${displayUrl.value}" style="width:100%;height:calc(100vh - 48px);border:0"></iframe>`
        } else if (isImage.value) {
          embedHtml = `<div style="text-align:center;padding:12px"><img src="${displayUrl.value}" style="max-width:100%;height:auto"/></div>`
        } else {
          embedHtml = `<iframe src="${displayUrl.value}" style="width:100%;height:calc(100vh - 48px);border:0"></iframe>`
        }

        const wrapper =
          `<!doctype html><html><head><meta charset="utf-8"><title>${title}</title>` +
          `<style>body{margin:0;font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial;} .toolbar{height:48px;display:flex;align-items:center;justify-content:flex-end;padding:8px;background:#f7f7f7;border-bottom:1px solid #e5e7eb;} .toolbar a{margin-right:12px;text-decoration:none;padding:6px 10px;background:#2563eb;color:#fff;border-radius:6px;font-size:14px;}</style>` +
          `</head><body><div class="toolbar"><a href="${downloadProxy}" download>${downloadLabel}</a></div>${embedHtml}</body></html>`

        if (tempHtmlBlobUrl) {
          URL.revokeObjectURL(tempHtmlBlobUrl)
          tempHtmlBlobUrl = ''
        }
        const blob = new Blob([wrapper], { type: 'text/html' })
        tempHtmlBlobUrl = URL.createObjectURL(blob)

        const a = window.document.createElement('a')
        a.href = tempHtmlBlobUrl
        a.target = '_blank'
        window.document.body.appendChild(a)
        a.click()
        a.remove()
        return
      } catch (e) {
        console.debug('openInNewTab: failed to open wrapper for displayUrl', e)
      }
    }

    // If a DOCX was converted client-side, open a new tab and write the HTML into it
    if (isDocx.value && docHtml.value) {
      // Attempt to open a blank window and write the converted HTML into it.
      const safeTitle = (props.title || suggestedFilename.value || fallbackName).replace(/[<>]/g, '')
      const fullHtml =
        `<!doctype html><html><head><meta charset="utf-8"><title>${safeTitle}</title>` +
        `<style>body{font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding:20px;} img{max-width:100%;height:auto;} .prose{max-width:800px;margin:0 auto;}</style>` +
        `</head><body><div class="prose">` +
        docHtml.value +
        `</div></body></html>`

      // Create a temporary blob URL for the HTML and try to open it via anchor click
      try {
        if (tempHtmlBlobUrl) {
          URL.revokeObjectURL(tempHtmlBlobUrl)
          tempHtmlBlobUrl = ''
        }
        const blob = new Blob([fullHtml], { type: 'text/html' })
        tempHtmlBlobUrl = URL.createObjectURL(blob)
        // Prefer anchor click navigation
        try {
          console.debug('openInNewTab: attempting anchor click for HTML blob')
          const a2 = window.document.createElement('a')
          a2.href = tempHtmlBlobUrl
          a2.target = '_blank'
          window.document.body.appendChild(a2)
          a2.click()
          a2.remove()
          return
        } catch (e) {
          console.debug('openInNewTab: anchor click for HTML blob failed', e)
          // Fallback to window.open if anchor click doesn't work
          try {
            const opened2 = window.open(tempHtmlBlobUrl, '_blank')
            console.debug('openInNewTab: window.open for HTML blob returned', opened2)
            if (opened2) {
              try {
                if (opened2.location && opened2.location.href === 'about:blank') opened2.location.href = tempHtmlBlobUrl
              } catch (navErr) {
                console.debug('openInNewTab: navigation to tempHtmlBlobUrl failed', navErr)
              }
              return
            }
          } catch (e2) {
            console.debug('openInNewTab: window.open for HTML blob threw', e2)
          }
        }
      } catch (e) {
        // continue to fallback
      }
    }

    // Fallback: open the same-origin proxy endpoint with download=0 to force inline display
    // Ensure we encode the URL parameter
    const encoded = encodeURIComponent(props.url)
    const proxy =
      window.location.origin +
      `/api/method/dbiz_ai_agent.document_permissions.serve_file?file_url=${encoded}&download=0`
    const a = window.document.createElement('a')
    a.href = proxy
    a.target = '_blank'
    window.document.body.appendChild(a)
    a.click()
    a.remove()
  } catch (e) {
    window.open(props.url, '_blank')
  }
}

// Ensure blob URL revoked when component unmounts (safety)
try {
  onUnmounted(() => {
    if (generatedBlobUrl) URL.revokeObjectURL(generatedBlobUrl)
    if (tempHtmlBlobUrl) {
      try {
        URL.revokeObjectURL(tempHtmlBlobUrl)
      } catch (e) {
        /* noop */
      }
      tempHtmlBlobUrl = ''
    }
    if (currentAbortController) currentAbortController.abort()
    if (currentTimeoutId) {
      clearTimeout(currentTimeoutId)
      currentTimeoutId = null
    }
  })
} catch (e) {
  // In case onUnmounted isn't available in this runtime, ignore
}
</script>

<style scoped>
.docx-preview {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #111827;
  line-height: 1.65;
  background-color: white;
  font-size: 0.95rem;
  padding: 1.5rem 2rem;
  box-shadow: inset 0 0 0 1px #e5e7eb;
  max-height: calc(72vh - 2.2rem);
  overflow: auto;
}

.docx-preview :deep(*) {
  max-width: 100%;
}

.docx-preview :deep(h1),
.docx-preview :deep(h2),
.docx-preview :deep(h3),
.docx-preview :deep(h4),
.docx-preview :deep(h5),
.docx-preview :deep(h6) {
  color: #111827;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.docx-preview :deep(p) {
  margin-bottom: 0.75rem;
}

.docx-preview :deep(ul),
.docx-preview :deep(ol) {
  margin: 0.75rem 0 0.75rem 1.25rem;
  padding-left: 1rem;
}

.docx-preview :deep(li) {
  margin-bottom: 0.4rem;
}

.docx-preview :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
  font-size: 0.95rem;
  padding: 1.5rem 2rem;
  max-height: calc(72vh - 6rem);
  overflow: auto;
}

.docx-preview :deep(th),
.docx-preview :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.5rem 0.75rem;
}

.docx-preview :deep(th) {
  background: #f5f5f5;
  font-weight: 600;
}

.docx-preview :deep(blockquote) {
  border-left: 4px solid #c7d2fe;
  background: #f5f3ff;
  padding: 0.75rem 1rem;
  color: #4338ca;
  margin: 1rem 0;
}

.docx-preview :deep(code),
.docx-preview :deep(pre) {
  background: #1f2937;
  color: #f9fafb;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.9rem;
  overflow-y: auto;
}

.docx-preview :deep(pre) {
  margin: 1rem 0;
}
</style>
