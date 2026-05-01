<template>
  <div class="relative overflow-hidden text-black flex-shrink-0 border-b border-gray-200 shadow-sm">
    <div class="px-6 py-6 flex flex-col gap-4">
      <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl text-black/80 flex items-center justify-center">
            <component :is="iconComponent" class="w-14 h-14" />
          </div>
          <div class="space-y-2">
            <p class="text-base font-bold uppercase tracking-[0.25em] text-black/80">
              {{ t('chatbotPermissions.documents.preview.label') }}
            </p>
            <h3 class="text-2xl font-bold leading-tight">
              {{ title }}
            </h3>
            <div class="flex flex-wrap gap-2 text-xs sm:text-sm text-black/85">
              <span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-black/10">
                <span class="w-2 h-2 rounded-full bg-emerald-300"></span>
                {{ mime }}
              </span>
              <span v-if="suggestedFilename" class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-black/10">
                <DownloadIcon class="w-3.5 h-3.5" />
                {{ suggestedFilename }}
              </span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <slot name="actions">
            <button @click="emit('openInNewTab')" class="inline-flex items-center gap-2 px-4 py-2 text-xl font-medium">
              <ExternalLinkIcon class="w-6 h-6" />
              {{ t('chatbotPermissions.documents.preview.buttons.openNewTab') }}
            </button>
            <a
              :href="url"
              :download="suggestedFilename"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-gray-900 font-semibold text-xl shadow-lg"
            >
              <DownloadIcon class="w-6 h-6" />
              {{ t('chatbotPermissions.documents.preview.buttons.download') }}
            </a>
          </slot>
          <button @click="emit('close')" class="p-2 rounded-2xl bg-white/10">
            <XIcon class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  ExternalLink as ExternalLinkIcon,
  Download as DownloadIcon,
  X as XIcon,
  FileText as FileTextIcon,
  ShieldCheck as ShieldCheckIcon,
} from 'lucide-vue-next'

const props = defineProps({
  title: { type: String, default: '' },
  mime: { type: String, default: '' },
  url: { type: String, default: '' },
  suggestedFilename: { type: String, default: '' },
  icon: { type: String, default: 'file' }, // 'file' or 'shield'
})

const emit = defineEmits(['close', 'openInNewTab'])
const { t } = useI18n()

const iconComponent = computed(() => {
  return props.icon === 'shield' ? ShieldCheckIcon : FileTextIcon
})
</script>
