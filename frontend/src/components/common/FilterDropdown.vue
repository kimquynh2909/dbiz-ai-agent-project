<template>
  <select
    :value="modelValue"
    :disabled="disabled"
    class="px-3 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
    @change="handleChange"
  >
    <option v-if="allOptionText" :value="allOptionValue">
      {{ allOptionText }}
    </option>
    <option
      v-for="option in normalizedOptions"
      :key="option.value ?? option.label"
      :value="option.value"
    >
      {{ option.label }}
    </option>
  </select>
</template>

<script setup>
// import computed
import { computed } from 'vue'

// props cho dropdown lọc
const props = defineProps({
  modelValue: { type: [String, Number, Boolean], default: '' }, // giá trị chọn
  options: { type: Array, default: () => [] }, // danh sách option
  valueKey: { type: String, default: 'value' }, // key lấy value
  labelKey: { type: String, default: 'label' }, // key lấy label
  allOptionText: { type: String, default: '' }, // text cho option "tất cả"
  allOptionValue: { type: [String, Number, Boolean], default: '' }, // value cho option "tất cả"
  disabled: { type: Boolean, default: false } // trạng thái disabled
})

// emit sự kiện thay đổi
const emit = defineEmits(['update:modelValue', 'change'])

// chuẩn hóa danh sách option
const normalizedOptions = computed(() => {
  return props.options.map((option) => {
    if (option && typeof option === 'object') {
      const value = option[props.valueKey]
      const label = option[props.labelKey] ?? value
      return { value, label: formatLabel(label) }
    }
    return { value: option, label: formatLabel(option) }
  })
})

// format lại label nếu là số
const formatLabel = (input) => {
  if (input == null) return ''
  const label = String(input)
  if (label && /^\d+$/.test(label)) return `${label} / trang`
  return label
}

const handleChange = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

