<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-5xl"
    :panel-class="'bg-white rounded-[32px] w-full max-h-[92vh] overflow-hidden shadow-2xl flex flex-col'"
    @close="emit('close')"
  >
    <DocumentPreviewHeader
      :title="document?.title || document?.name || ''"
      :mime="document?.file_type || document?.mime || ''"
      :url="document?.file_url || document?.fileUrl || ''"
      :suggested-filename="document?.file_url || document?.fileUrl || ''"
      icon="file"
      @close="emit('close')"
    >
      <template #actions>
        <button
          @click="handleSubmit"
          :disabled="isSaving"
          class="inline-flex items-center gap-2 px-4 py-2 text-gray-900 font-semibold text-xl rounded-2xl disabled:opacity-60 disabled:cursor-not-allowed"
        >
          <SaveIcon class="w-6 h-6" />
          {{
            isSaving
              ? t('chatbotPermissions.documents.editModal.buttons.saving')
              : t('chatbotPermissions.documents.editModal.buttons.save')
          }}
        </button>
      </template>
    </DocumentPreviewHeader>

    <div class="p-6 lg:p-8 space-y-4 max-h-[80vh] overflow-y-auto">
      <div v-if="isLoading" class="flex flex-col items-center justify-center py-12">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
        <p class="text-sm text-gray-500 mt-3">{{ t('chatbotPermissions.documents.editModal.loading') }}</p>
      </div>

      <template v-else>
        <div v-if="displayError" class="bg-red-50 border border-red-200 text-sm text-red-700 rounded-2xl p-4">
          {{ displayError }}
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-gray-700">
                {{ t('chatbotPermissions.documents.editModal.fields.title') }}
              </label>
              <input
                :value="currentForm.title"
                type="text"
                required
                class="input-field"
                @input="updateField('title', $event.target.value)"
              />
            </div>
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-gray-700">
                {{ t('chatbotPermissions.documents.editModal.fields.category') }}
              </label>
              <input
                :value="currentForm.category"
                type="text"
                class="input-field"
                @input="updateField('category', $event.target.value)"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-gray-700">
                {{ t('chatbotPermissions.documents.editModal.fields.accessLevel') }}
              </label>
              <select
                :value="currentForm.access_level"
                required
                class="input-field"
                @change="updateField('access_level', $event.target.value)"
              >
                <option value="">
                  {{ t('chatbotPermissions.documents.editModal.fields.accessLevelPlaceholder') }}
                </option>
                <option v-for="level in accessLevelOptions" :key="level" :value="level">
                  {{ level }}
                </option>
              </select>
            </div>
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-gray-700">
                {{ t('chatbotPermissions.documents.editModal.fields.tags') }}
              </label>
              <input
                :value="currentForm.tags"
                type="text"
                class="input-field"
                @input="updateField('tags', $event.target.value)"
              />
            </div>
          </div>

          <div v-if="showDepartmentsField" class="flex flex-col gap-2">
            <label class="text-sm font-medium text-gray-700">
              {{ t('chatbotPermissions.documents.editModal.fields.departments') }}
            </label>
            <input
              :value="currentForm.departments_allowed"
              type="text"
              class="input-field"
              @input="updateField('departments_allowed', $event.target.value)"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-gray-700">
              {{ t('chatbotPermissions.documents.editModal.fields.description') }}
            </label>
            <textarea
              :value="currentForm.description"
              rows="3"
              class="input-field min-h-[120px]"
              @input="updateField('description', $event.target.value)"
            ></textarea>
          </div>

          <div v-if="showContentField" class="flex flex-col gap-2">
            <label class="text-sm font-medium text-gray-700">
              {{ t('chatbotPermissions.documents.editModal.fields.content') }}
            </label>
            <textarea
              :value="currentForm.content"
              rows="6"
              class="input-field min-h-[160px]"
              @input="updateField('content', $event.target.value)"
            ></textarea>
          </div>
        </form>
      </template>
    </div>
  </ModalBase>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Save as SaveIcon } from 'lucide-vue-next'
import ModalBase from '@/components/common/ModalBase.vue'
import DocumentPreviewHeader from '../common/DocumentPreviewHeader.vue'
import documentPermissionService from '@/services/documentPermissionService'

const props = defineProps({
  visible: { type: Boolean, default: false },
  document: { type: Object, default: null },
  documentId: { type: String, default: '' },
  // Optional external control props (for backward compatibility)
  form: { type: Object, default: null },
  accessLevels: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'save', 'update:field', 'update:form', 'updated'])
const { t } = useI18n()

// local states for uncontrolled mode
const localForm = ref({
  title: '',
  category: '',
  access_level: '',
  description: '',
  tags: '',
  departments_allowed: '',
  content: '',
})
const lastFetched = ref({})
const internalLoading = ref(false)
const internalError = ref('')
const internalSaving = ref(false)

const DEFAULT_ACCESS_LEVELS = ['Public', 'Internal']
const accessLevelOptions = computed(() => {
  const set = new Set(DEFAULT_ACCESS_LEVELS)
  ;(props.accessLevels || []).forEach((lvl) => lvl && set.add(lvl))
  return Array.from(set)
})

const isControlled = computed(() => !!props.form)
const currentForm = computed(() => (isControlled.value ? props.form : localForm.value))
const isLoading = computed(() => props.loading || internalLoading.value)
const isSaving = computed(() => props.saving || internalSaving.value)
const displayError = computed(() => props.error || internalError.value)
const showContentField = computed(() => true)
const showDepartmentsField = computed(() => {
  // Sau khi chỉ còn hai access level (Public, Internal), không cần trường departments
  return false
})

const updateField = (field, value) => {
  if (isControlled.value) {
    emit('update:field', field, value)
  } else {
    localForm.value = { ...localForm.value, [field]: value }
  }
}

const loadDocumentDetails = async () => {
  if (!props.documentId || isControlled.value === true) return
  try {
    internalError.value = ''
    internalLoading.value = true
    // Request content explicitly; backend returns `content` only when include_content=1
    const response = await documentPermissionService.getDocumentPermissions(props.documentId, { includeContent: true })
    // Normalize response
    const payload = response?.data || response || {}
    const doc = payload.document || payload || {}

    const nextForm = {
      title: doc.title || '',
      category: doc.category || '',
      access_level: doc.access_level || '',
      description: doc.description || '',
      tags: doc.tags || '',
      departments_allowed: doc.departments_allowed || '',
      content: doc.content || '',
    }
    localForm.value = nextForm
    lastFetched.value = { ...nextForm }
  } catch (err) {
    console.error('Failed to load document details:', err)
    internalError.value = err?.message || t('chatbotPermissions.documents.editModal.errors.loadFailed')
  } finally {
    internalLoading.value = false
  }
}

watch(
  () => props.visible,
  (v) => {
    if (v && props.documentId && !isControlled.value) {
      void loadDocumentDetails()
    }
  }
)

watch(
  () => props.documentId,
  (id) => {
    if (props.visible && id && !isControlled.value) {
      void loadDocumentDetails()
    }
  }
)

const handleSubmit = async () => {
  if (isControlled.value) {
    emit('save')
    return
  }
  // Uncontrolled: perform API call directly
  try {
    internalError.value = ''
    internalSaving.value = true
    const allowedFields = ['title', 'category', 'access_level', 'description', 'tags', 'departments_allowed', 'content']
    const payload = {}
    for (const key of allowedFields) {
      if (currentForm.value[key] !== lastFetched.value[key]) {
        payload[key] = currentForm.value[key]
      }
    }
    if (Object.keys(payload).length === 0) {
      internalSaving.value = false
      internalError.value = t('chatbotPermissions.documents.editModal.errors.noChanges')
      return
    }
    const response = await documentPermissionService.updateDocumentMetadata(props.documentId, payload)
    if (!response || response.success === false) {
      throw new Error(response?.error || t('chatbotPermissions.documents.editModal.errors.saveFailed'))
    }
    const updatedDoc = response?.data?.document || {}
    emit('updated', updatedDoc)
    emit('close')
  } catch (err) {
    console.error('Failed to save document:', err)
    internalError.value = err?.message || t('chatbotPermissions.documents.editModal.errors.saveFailed')
  } finally {
    internalSaving.value = false
  }
}
</script>

<style scoped>
.input-field {
  @apply w-full px-4 py-2.5 rounded-2xl border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition;
}
</style>
