<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-5xl"
    :panel-class="'bg-white rounded-[32px] w-full max-h-[92vh] overflow-hidden shadow-2xl flex flex-col'"
    @close="emit('close')"
  >
    <div class="bg-gradient-to-r from-gray-900 via-gray-900 to-black text-white flex-shrink-0">
      <div class="px-6 py-6 flex flex-col gap-4">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-2xl bg-white/15 backdrop-blur flex items-center justify-center shadow-lg">
              <UsersIcon class="w-6 h-6" />
            </div>
            <div>
              <p class="text-xs uppercase tracking-[0.3em] text-white/60">
                {{ t('chatbotPermissions.documents.bulkModal.label') }}
              </p>
              <h3 class="text-2xl font-semibold">
                {{ t('chatbotPermissions.documents.bulkModal.title') }}
              </h3>
              <p class="text-white/70 text-sm mt-1">
                {{ t('chatbotPermissions.documents.bulkModal.selectedDocs', { count: computedSelectedCount }) }}
              </p>
            </div>
          </div>
          <button @click="emit('close')" class="p-2 rounded-2xl bg-white/10 hover:bg-white/25 transition">
            <XIcon class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>

    <div class="p-6 lg:p-8 space-y-5 overflow-y-auto flex-1 bg-gray-50">
      <div v-if="displayError" class="bg-red-50 border border-red-200 text-sm text-red-700 rounded-2xl p-4">
        {{ displayError }}
      </div>

      <div class="space-y-3">
        <label class="block text-sm font-medium text-gray-700">
          {{ t('chatbotPermissions.documents.bulkModal.fields.role') }}
        </label>
        <select
          :value="selectedRoleValue"
          class="input-field"
          @change="setSelectedRole($event.target.value)"
        >
          <option value="" disabled>{{ t('chatbotPermissions.documents.bulkModal.fields.rolePlaceholder') }}</option>
          <option v-for="role in rolesDisplay" :key="role.name || role.role_name" :value="role.name">
            {{ role.role_name || role.name }}
          </option>
        </select>
      </div>

      <div class="space-y-3">
        <span class="block text-sm font-medium text-gray-700">
          {{ t('chatbotPermissions.documents.bulkModal.fields.action') }}
        </span>
        <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-4 text-sm text-gray-600 space-y-3 sm:space-y-0">
          <label class="inline-flex items-center">
            <input
              type="radio"
              value="grant"
              :checked="actionValue === 'grant'"
              class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              @change="setAction('grant')"
            />
            <span class="ml-2">{{ t('chatbotPermissions.documents.bulkModal.fields.actionGrant') }}</span>
          </label>
          <label class="inline-flex items-center">
            <input
              type="radio"
              value="revoke"
              :checked="actionValue === 'revoke'"
              class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              @change="setAction('revoke')"
            />
            <span class="ml-2">{{ t('chatbotPermissions.documents.bulkModal.fields.actionRevoke') }}</span>
          </label>
        </div>
      </div>

      <div>
        <span class="block text-sm font-medium text-gray-700 mb-2">
          {{ t('chatbotPermissions.documents.bulkModal.fields.documents') }}
        </span>
        <div class="max-h-52 overflow-y-auto border border-gray-200 rounded-2xl divide-y divide-gray-100 bg-white">
          <div v-for="doc in documentsDisplay" :key="doc.name || doc" class="px-3 py-2">
            <p class="text-sm font-medium text-gray-900 truncate" :title="doc.title || doc.name">
              {{ doc.title || doc.name || doc }}
            </p>
            <p class="text-xs text-gray-500">
              <span v-if="typeof doc === 'object'">
                {{ doc.category || t('chatbotPermissions.documents.bulkModal.fields.unknownCategory') }} • {{ doc.access_level || 'Internal' }}
              </span>
            </p>
          </div>
          <div v-if="!documentsDisplay.length" class="px-3 py-4 text-sm text-gray-500 text-center">
            {{ t('chatbotPermissions.documents.bulkModal.fields.noDocuments') }}
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          @click="emit('close')"
          class="px-5 py-2.5 text-sm text-gray-700 bg-white border border-gray-200 rounded-2xl hover:bg-gray-50"
        >
          {{ t('chatbotPermissions.documents.bulkModal.buttons.cancel') }}
        </button>
        <button
          type="button"
          :disabled="!canSubmit"
          class="px-5 py-2.5 text-sm text-white rounded-2xl flex items-center gap-2 disabled:cursor-not-allowed"
          :class="canSubmit ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-400 opacity-60'"
          @click="handleApply"
        >
          <span v-if="isSaving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          {{ t('chatbotPermissions.documents.bulkModal.buttons.apply') }}
        </button>
      </div>
    </div>
  </ModalBase>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { X as XIcon, Users as UsersIcon } from 'lucide-vue-next'
import ModalBase from '@/components/base/ModalBase.vue'
import documentPermissionService from '@/services/documentPermissionService'

const props = defineProps({
  visible: { type: Boolean, default: false },
  // Uncontrolled inputs
  documentIds: { type: Array, default: () => [] },
  documents: { type: Array, default: () => [] },
  // Optional controlled props (backward compatible)
  roles: { type: Array, default: () => [] },
  selectedRole: { type: String, default: '' },
  action: { type: String, default: 'grant' },
  selectedCount: { type: Number, default: 0 },
  error: { type: String, default: '' },
  saving: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'updated'])
const { t } = useI18n()

// Internal state for uncontrolled mode
const localRoles = ref([])
const localSelectedRole = ref('')
const localAction = ref('grant')
const localSaving = ref(false)
const localError = ref('')

const isControlled = computed(() => Array.isArray(props.roles) && props.roles.length > 0)
const rolesDisplay = computed(() => (isControlled.value ? props.roles : localRoles.value))
const selectedRoleValue = computed(() => (isControlled.value ? props.selectedRole : localSelectedRole.value))
const actionValue = computed(() => (isControlled.value ? props.action : localAction.value))
const isSaving = computed(() => props.saving || localSaving.value)
const displayError = computed(() => props.error || localError.value)
const computedSelectedCount = computed(() => props.selectedCount || props.documentIds.length || props.documents.length)
const documentsDisplay = computed(() => (props.documents && props.documents.length ? props.documents : (props.documentIds || [])))

const canSubmit = computed(() => !isSaving.value && computedSelectedCount.value > 0 && !!selectedRoleValue.value)

const setSelectedRole = (val) => {
  if (isControlled.value) return
  localSelectedRole.value = val
}
const setAction = (val) => {
  if (isControlled.value) return
  localAction.value = val
}

const loadRoles = async () => {
  try {
    localError.value = ''
    const rolesResp = await documentPermissionService.getRoles()
    let roles = []
    if (rolesResp?.data) roles = rolesResp.data
    else if (Array.isArray(rolesResp)) roles = rolesResp
    else if (rolesResp?.roles) roles = rolesResp.roles
    localRoles.value = roles
    if (!localSelectedRole.value && roles.length) {
      localSelectedRole.value = roles[0].name
    }
  } catch (err) {
    console.error('Failed to load roles:', err)
    localError.value = err?.message || t('chatbotPermissions.documents.bulkModal.errors.rolesLoadFailed')
  }
}

watch(
  () => props.visible,
  (v) => {
    if (v && !isControlled.value) {
      void loadRoles()
    }
  }
)

const handleApply = async () => {
  if (isControlled.value) {
    // In controlled mode, consumer should handle submit. But to avoid passing handlers, we still attempt apply when documentIds are present
  }
  try {
    localError.value = ''
    localSaving.value = true
    const names = (props.documentIds && props.documentIds.length)
      ? props.documentIds
      : (props.documents || []).map(d => (typeof d === 'object' ? d.name : d)).filter(Boolean)
    const grant = actionValue.value === 'grant'
    const result = await documentPermissionService.bulkUpdateDocumentsPermissions(names, selectedRoleValue.value, grant)
    if (!result || result.success === false) {
      throw new Error(result?.error || t('chatbotPermissions.documents.bulkModal.errors.applyFailed'))
    }
    emit('updated', { count: names.length, role: selectedRoleValue.value, action: actionValue.value })
    emit('close')
  } catch (err) {
    console.error('Bulk apply error:', err)
    localError.value = err?.message || t('chatbotPermissions.documents.bulkModal.errors.applyFailed')
  } finally {
    localSaving.value = false
  }
}
</script>

<style scoped>
.input-field {
  @apply w-full px-4 py-2.5 rounded-2xl border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition;
}
</style>
