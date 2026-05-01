<template>
  <div
    :class="[
      'rounded-2xl px-6 py-4 shadow-sm',
      resolvedCardClass
    ]"
  >
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="flex items-center space-x-4">
        <div
          :class="[
            'w-12 h-12 rounded-xl flex items-center justify-center text-white shadow-lg',
            resolvedIconWrapperClass
          ]"
        >
          <slot name="icon">
            <component v-if="icon" :is="icon" class="w-6 h-6" />
          </slot>
        </div>
        <div>
          <h3 class="text-xl font-bold text-gray-900">{{ title }}</h3>
          <div class="text-sm text-gray-600 mt-0.5 flex items-center space-x-2">
            <slot name="meta">
              <span v-if="subtitle" class="font-medium text-indigo-600">
                {{ subtitle }}
              </span>
            </slot>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-start sm:justify-end gap-2 sm:gap-3">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const colorThemes = {
  indigo: {
    cardClass: 'bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100',
    iconWrapperClass: 'bg-gradient-to-br from-indigo-500 to-purple-600'
  },
  blue: {
    cardClass: 'bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-100',
    iconWrapperClass: 'bg-gradient-to-br from-blue-500 to-cyan-500'
  },
  emerald: {
    cardClass: 'bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-100',
    iconWrapperClass: 'bg-gradient-to-br from-emerald-500 to-teal-500'
  },
  amber: {
    cardClass: 'bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-100',
    iconWrapperClass: 'bg-gradient-to-br from-amber-500 to-orange-500'
  },
  purple: {
    cardClass: 'bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-100',
    iconWrapperClass: 'bg-gradient-to-br from-purple-500 to-pink-500'
  }
}

const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: [Object, Function], default: null },
  cardClass: { type: String, default: '' },
  iconWrapperClass: { type: String, default: '' },
  color: {
    type: String,
    default: 'indigo'
  }
})

const fallbackTheme = colorThemes.indigo
const theme = computed(() => colorThemes[props.color] || fallbackTheme)

const resolvedCardClass = computed(() => props.cardClass || theme.value.cardClass)
const resolvedIconWrapperClass = computed(() => props.iconWrapperClass || theme.value.iconWrapperClass)
</script>
