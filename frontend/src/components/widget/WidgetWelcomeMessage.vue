<template>
  <div class="widget-welcome">
    <div class="bot-message" v-if="welcomeMessage">
      <img :src="props.avatarImage" alt="avatar" class="w-8 h-8 object-contain rounded-full" />
      <div class="bot-bubble" v-html="welcomeMessage"></div>
    </div>
    <div class="hint">
      <span class="icon">💡</span>
      <span class="label">Gợi ý câu hỏi:</span>
    </div>

    <div class="chips">
      <button
        v-for="(s, i) in activeSuggestions"
        :key="i"
        type="button"
        class="chip"
        @click="onSelect(s)">
        <span class="chip-icon">
          <component v-if="findLucideComponent(s.icon)" :is="findLucideComponent(s.icon)" class="lucide-icon" />
        </span>
        <span class="chip-tx">{{ s.question_text || s.text || s.title }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  // suggestions: array of objects { question_text, icon, is_active, sort_order, ... }
  suggestions: { type: Array, default: () => [] },
  // optional welcome text to show above suggestions
  welcomeText: { type: String, default: '' },
  // optional doctype/name/field to load welcome message from server
  welcomeDoctype: { type: String, default: '' },
  welcomeName: { type: String, default: '' },
  welcomeField: { type: String, default: 'message' }
  ,
  // optional avatar image to show next to the welcome bubble
  avatarImage: { type: String, default: '' }
})

const emit = defineEmits(['select-suggestion', 'submit-question'])
const value = ref('')

import * as LucideIcons from 'lucide-vue-next'

// Try to find a lucide icon component by name (case-insensitive). If not
// found, return null and UI will fallback to a simple emoji.
function findLucideComponent(name) {
  if (!name) return null
  // normalize to letters only and PascalCase likely matching lucide exports
  const normalized = String(name).replace(/[^a-zA-Z0-9]/g, ' ').split(/\s+/).filter(Boolean).map(s => s.charAt(0).toUpperCase() + s.slice(1).toLowerCase()).join('')
  if (!normalized) return null
  // try direct match
  if (LucideIcons[normalized]) return LucideIcons[normalized]
  // try some common alternate names
  const altMap = { pdf: 'Download', download: 'Download', key: 'Key', server: 'Server', mail: 'Mail', email: 'Mail', db: 'Database' }
  if (altMap[normalized.toLowerCase()] && LucideIcons[altMap[normalized.toLowerCase()]]) return LucideIcons[altMap[normalized.toLowerCase()]]
  return null
}

// local suggestions loaded from backend when component requests chatbot config
const welcomeSuggestions = ref([])

const activeSuggestions = computed(() => {
  try {
    const source = (props.suggestions && props.suggestions.length) ? props.suggestions : (welcomeSuggestions.value || [])
    return (source || [])
      .filter(s => s && (s.is_active === 1 || s.is_active === true || s.is_active === '1' || s.is_active === undefined))
      .slice()
      .sort((a, b) => {
        const sa = Number(a.sort_order || 0)
        const sb = Number(b.sort_order || 0)
        return sa - sb
      })
  } catch (e) { return [] }
})

// welcome message loaded from server (if any)
const welcomeFromDoctype = ref('')

// display welcome message (doctype result overrides prop if present)
const welcomeMessage = computed(() => {
  if (welcomeFromDoctype.value && String(welcomeFromDoctype.value).trim()) return String(welcomeFromDoctype.value)
  try {
    if (props.welcomeText && String(props.welcomeText).trim()) return String(props.welcomeText)
  } catch (e) { /* ignore */ }
  return 'Xin chào! Tôi có thể giúp gì cho bạn hôm nay?'
})

onMounted(async () => {
  try {
    if (props.welcomeDoctype) {
      // legacy: fetch a resource doctype/record
      let url = ''
      if (props.welcomeName) {
        url = '/api/resource/' + encodeURIComponent(props.welcomeDoctype) + '/' + encodeURIComponent(props.welcomeName)
      } else {
        // request first record and specific field
        const field = encodeURIComponent(props.welcomeField || 'message')
        url = '/api/resource/' + encodeURIComponent(props.welcomeDoctype) + '?limit_page_length=1&fields=["' + field + '"]'
      }
      const resp = await fetch(url, { credentials: 'include' })
      if (resp && resp.ok) {
        const j = await resp.json()
        let txt = ''
        if (j && j.data) {
          if (Array.isArray(j.data)) {
            const first = j.data[0] || {}
            txt = String(first[props.welcomeField] || first.message || first.content || '')
          } else if (typeof j.data === 'object') {
            txt = String(j.data[props.welcomeField] || j.data.message || j.data.content || '')
          }
        } else if (j && j.message) {
          txt = String(j.message)
        }
        if (txt) welcomeFromDoctype.value = txt
      }
      return
    }

    // Default: call whitelisted API that returns the active Chatbot Configuration
    // This endpoint is implemented server-side as dbiz_ai_agent.api.auth.get_chatbot_config
    // It returns an object containing greeting_message, quick_questions, assistant_name, avatar_image, etc.
    const resp2 = await fetch('/api/method/dbiz_ai_agent.api.auth.get_chatbot_config', { credentials: 'include' })
    if (resp2 && resp2.ok) {
      const j2 = await resp2.json()
      const msg = j2 && (j2.message || j2.data)
      if (msg) {
        // prefer greeting_message, fall back to title
        const gm = String(msg.greeting_message || msg.title || '').trim()
        if (gm) welcomeFromDoctype.value = gm
        // quick_questions is an array of {question_text, icon, is_active, sort_order}
        if (Array.isArray(msg.quick_questions) && msg.quick_questions.length) {
          welcomeSuggestions.value = msg.quick_questions.slice()
        }
      }
    }
  } catch (e) {
    /* ignore network errors */
  }
})

function onSelect(s) {
  if (!s) return
  const text = (s.question_text || s.text || s.title || '').trim()
  try { value.value = text } catch (e) { }
  // emit full object so consumer can use metadata
  emit('select-suggestion', s)
  // also emit submit-question with the object so parent can send immediately
//   emit('submit-question', s)
}

</script>

<style scoped>
.widget-welcome { padding: 12px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
.hint { display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#374151; font-weight:600 }
.hint .icon { font-size:16px }
.chips { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px }
.bot-message { display:flex; gap:8px; align-items:flex-start; margin:6px 0 10px }
.bot-avatar { width:36px; height:36px; border-radius:18px; display:inline-flex; align-items:center; justify-content:center; background:#eef2ff; color:#1e293b; font-size:18px }
.bot-bubble { background:#f8fafc; padding:10px 12px; border-radius:12px; color:#0f172a; box-shadow:0 6px 18px rgba(2,6,23,0.04); font-size:13px; line-height:1.35 }
.chip {
  /* Soft, less-saturated cyan pill for a calmer appearance */
  background: linear-gradient(180deg, #ffffff 0%, #CFF3FF 300%); /* very soft cyan top -> slightly deeper bottom */
  border: 1px solid rgba(3,105,161,0.08); /* muted blue border */
  color: #0f172a; /* keep dark text for contrast */
  padding: 8px 14px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  /* remove global opacity to keep color solid; use softer shadows */
  box-shadow: 0 8px 20px rgba(2,6,23,0.06), inset 0 1px 0 rgba(255,255,255,0.6);
  transition: transform 160ms cubic-bezier(.2,.9,.2,1), box-shadow 160ms cubic-bezier(.2,.9,.2,1);
  will-change: transform, box-shadow;
}
.chip-icon { display:inline-flex; width:18px; height:18px; align-items:center; justify-content:center }
.chip-icon svg { width:18px; height:18px; color: #0284C7 } /* calmer blue for icon */
.chip-tx { display:inline-block }
.chip:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(2,6,23,0.08), inset 0 1px 0 rgba(255,255,255,0.7) }
.chip:active { transform: translateY(-1px) scale(0.995); box-shadow: 0 8px 18px rgba(2,6,23,0.06) }

@media (max-width:420px) {
  .chip { padding:6px 10px; font-size:12px }
  .hint { font-size:14px }
}
</style>
