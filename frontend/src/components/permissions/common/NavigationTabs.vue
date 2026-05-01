<template>
  <nav class="flex space-x-8 px-6">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      @click="emit('change', tab.id)"
      :class="[
        'flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors',
        activeTab === tab.id
          ? 'border-blue-500 text-blue-600'
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      ]"
    >
      <component :is="tab.icon" class="w-5 h-5 mr-2" />
      {{ tab.name }}
    </button>
  </nav>
</template>

<script setup>
const props = defineProps({
  tabs: {
    type: Array,
    default: () => []
  },
  activeTab: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['change'])
</script>
