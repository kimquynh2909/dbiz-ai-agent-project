<template>
  <ModalBase
    :visible="visible"
    max-width="max-w-5xl"
    :panel-class="'bg-white rounded-[32px] w-[90%] max-w-7xl max-h-[92vh] overflow-hidden shadow-2xl flex flex-col'"
    @close="emit('close')"
  >
    <!-- Header with gradient background -->
    <DocumentPreviewHeader
      :title="document?.title"
      :mime="mime"
      :url="url"
      :suggested-filename="suggestedFilename"
      icon="shield"
      @close="emit('close')"
    >
      <template #actions>
        <button
          @click="handleSave"
          class="inline-flex items-center gap-2 px-4 py-2 text-gray-900 font-semibold text-xl rounded-2xl"
        >
          <SaveIcon class="w-6 h-6" />
          {{
            isSaving
              ? t('chatbotPermissions.documents.permissionModal.buttons.saving')
              : t('chatbotPermissions.documents.permissionModal.buttons.save')
          }}
        </button>
      </template>
    </DocumentPreviewHeader>

    <!-- Content Area -->
    <div class="flex flex-col h-full flex-1 overflow-hidden border-t border-gray-200">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
        <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        <p class="text-gray-600 mt-4 font-medium">
          {{ t('chatbotPermissions.documents.permissionModal.loading') }}
        </p>
      </div>

      <!-- Error State -->
      <div v-else-if="displayError" class="mx-8 mt-6">
        <div class="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
          <div class="flex items-center">
            <AlertCircleIcon class="w-5 h-5 text-red-400 mr-3" />
            <p class="text-red-700 font-medium">{{ displayError }}</p>
          </div>
        </div>
      </div>

      <!-- Roles List: action bar fixed, roles grid scrolls below -->
      <div v-else class="flex-1 min-h-0 flex flex-col">
        <div class="px-8 py-4 flex-shrink-0">
          <!-- Action Bar -->
          <div class="px-4">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div class="flex flex-wrap items-center gap-3">
                <button
                  @click="selectAll"
                  :disabled="isLoading"
                  class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-white bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 shadow disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <CheckSquareIcon class="w-4 h-4" />
                  <span>{{ t('chatbotPermissions.documents.permissionModal.actions.selectAll') }}</span>
                </button>
                <button
                  @click="deselectAll"
                  :disabled="isLoading"
                  class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-gray-800 bg-gray-100 hover:bg-gray-200 border border-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <SquareIcon class="w-4 h-4" />
                  <span>{{ t('chatbotPermissions.documents.permissionModal.actions.deselectAll') }}</span>
                </button>
              </div>
              <div class="text-2xl text-gray-600">
                <a
                  :href="url"
                  :download="suggestedFilename"
                  class="inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-gray-900 font-semibold text-lg shadow-lg hover:shadow-xl transition"
                >
                  <span class="text-gray-400 text-3xl">{{ selectedCount }}/{{ rolesDisplay.length }}</span>
                  <span class="text-gray-500">
                    {{ ' ' + t('chatbotPermissions.documents.permissionModal.actions.rolesSelected') }}
                  </span>
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Scrollable roles grid -->
        <div class="px-8 pb-6 overflow-auto flex-1 min-h-0">
          <div
            v-for="role in rolesDisplay"
            :key="role.name"
            class="bg-gray-100 border border-gray-200 rounded-2xl p-5 hover:shadow-md transition-all duration-200 mb-4"
            :class="{
              'opacity-60 bg-gray-50': role.is_active === false,
              'border-blue-500 shadow-lg ring-1 ring-blue-200 bg-blue-50/60': getPermission(role.name, 'can_read'),
            }"
          >
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div class="flex items-center gap-4">
                <div
                  class="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-semibold text-lg shadow-lg"
                  :style="{ backgroundColor: role.color || '#6b7280' }"
                >
                  {{ role.icon || role.role_name?.charAt(0) || '?' }}
                </div>

                <div class="space-y-1">
                  <div class="flex items-center flex-wrap gap-3">
                    <h4 class="text-lg font-semibold text-gray-900">
                      {{ role.role_name }}
                    </h4>
                    <span
                      v-if="role.is_active !== false"
                      class="px-3 py-1 text-xs font-semibold text-emerald-700 bg-emerald-100 rounded-full"
                    >
                      {{ t('chatbotPermissions.documents.permissionModal.role.active') }}
                    </span>
                    <span v-else class="px-3 py-1 text-xs font-semibold text-gray-600 bg-gray-100 rounded-full">
                      {{ t('chatbotPermissions.documents.permissionModal.role.inactive') }}
                    </span>
                  </div>
                  <p v-if="role.description" class="text-sm text-gray-600">
                    {{ role.description }}
                  </p>
                </div>
              </div>

              <div class="flex items-center justify-end w-full lg:w-auto">
                <label class="flex items-center gap-3 cursor-pointer">
                  <span class="text-sm font-medium text-gray-700">
                    {{ t('chatbotPermissions.documents.permissionModal.role.accessLabel') }}
                  </span>
                  <div class="relative">
                    <input
                      type="checkbox"
                      :checked="getPermission(role.name, 'can_read')"
                      @change="togglePermission(role.name, 'can_read', $event.target.checked)"
                      class="w-6 h-6 text-blue-600 border-2 border-gray-300 rounded-lg focus:ring-blue-500 focus:ring-2 cursor-pointer appearance-none bg-white"
                    />
                    <div
                      v-if="getPermission(role.name, 'can_read')"
                      class="absolute inset-0 flex items-center justify-center pointer-events-none bg-gradient-to-r from-blue-600 to-purple-500 rounded-lg"
                    >
                      <CheckIcon class="w-4 h-4 text-white" />
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Footer Actions -->
    <div class="px-8 py-4"></div>
  </ModalBase>
</template>

<script setup>
import {
  Save as SaveIcon,
  Check as CheckIcon,
  AlertCircle as AlertCircleIcon,
  CheckSquare as CheckSquareIcon,
  Square as SquareIcon,
} from 'lucide-vue-next'
import ModalBase from '@/components/base/ModalBase.vue'
import DocumentPreviewHeader from '../common/DocumentPreviewHeader.vue'
import { watch, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import documentPermissionService from '@/services/documentPermissionService'

const props = defineProps({
  visible: { type: Boolean, default: false },
  document: { type: Object, default: null },
  mime: { type: String, default: '' },
  url: { type: String, default: '' },
  suggestedFilename: { type: String, default: '' },
  documentId: { type: String, default: '' },
  roles: { type: Array, default: () => [] },
  permissions: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'save', 'update:permission', 'updated'])
const { t } = useI18n()

// Internal state (uncontrolled mode)
const localRoles = ref([])
const localPermissions = ref({})
const localLoading = ref(false)
const localSaving = ref(false)
const localError = ref('')

const isControlled = computed(() => Array.isArray(props.roles) && props.roles.length > 0)

// Normalize is_active to boolean helper
const normalizeRole = (r) => ({
  ...r,
  is_active: r?.is_active === true || r?.is_active === 1 || r?.is_active === '1',
})

const rolesDisplay = computed(() => {
  if (isControlled.value) {
    return (props.roles || []).map(normalizeRole)
  }
  return localRoles.value.map(normalizeRole)
})
const currentPermissions = computed(() => (isControlled.value ? props.permissions : localPermissions.value))
const isLoading = computed(() => props.loading || localLoading.value)
const isSaving = computed(() => props.saving || localSaving.value)
const displayError = computed(() => props.error || localError.value)

// Computed for selected count
const selectedCount = computed(() => {
  return rolesDisplay.value.filter((role) => getPermission(role.name, 'can_read')).length
})

// suggestedFilename: prefer parent prop, then derive from `url`/`downloadUrl`, then fall back to document name/title
const suggestedFilename = computed(() => {
  try {
    if (!props.url) return ''
    const parts = props.url.split('/')
    return parts[parts.length - 1].split('?')[0]
  } catch (e) {
    return ''
  }
})

const getPermission = (roleName, permissionType) => {
  const perm = currentPermissions.value[roleName]
  return perm ? !!perm[permissionType] : false
}

// Select all / Deselect all functions
const selectAll = () => {
  rolesDisplay.value.forEach((role) => {
    if (role.is_active !== false) {
      togglePermission(role.name, 'can_read', true)
    }
  })
}

const deselectAll = () => {
  rolesDisplay.value.forEach((role) => {
    togglePermission(role.name, 'can_read', false)
  })
}

const togglePermission = (roleName, permissionType, value) => {
  if (isControlled.value) {
    emit('update:permission', roleName, permissionType, value)
    return
  }
  const next = {
    ...(currentPermissions.value[roleName] || {
      can_read: false,
      can_write: false,
      can_delete: false,
    }),
  }
  next[permissionType] = value
  localPermissions.value = { ...currentPermissions.value, [roleName]: next }
}

const loadRolesAndPermissions = async () => {
  if (!props.documentId) return
  try {
    localError.value = ''
    localLoading.value = true
    // Fetch roles
    const rolesResp = await documentPermissionService.getRoles()
    let roles = []
    if (rolesResp?.data) roles = rolesResp.data
    else if (Array.isArray(rolesResp)) roles = rolesResp
    else if (rolesResp?.roles) roles = rolesResp.roles
    // Normalize is_active to boolean for consistent UI
    localRoles.value = roles.map(normalizeRole)
    // Fetch document permissions
    const permResp = await documentPermissionService.getDocumentPermissions(props.documentId)
    const payload = permResp?.data || permResp || {}
    const perms = payload.permissions || {}
    localPermissions.value = perms
  } catch (err) {
    console.error('Failed to load roles/permissions:', err)
    localError.value = err?.message || t('chatbotPermissions.documents.permissionModal.errors.loadFailed')
  } finally {
    localLoading.value = false
  }
}

watch(
  () => props.visible,
  (v) => {
    if (v && props.documentId && !isControlled.value) {
      void loadRolesAndPermissions()
    }
  }
)

watch(
  () => props.documentId,
  (id) => {
    if (props.visible && id && !isControlled.value) {
      void loadRolesAndPermissions()
    }
  }
)

const handleSave = async () => {
  if (isControlled.value) {
    emit('save')
    return
  }
  try {
    localError.value = ''
    localSaving.value = true
    const resp = await documentPermissionService.bulkUpdateDocumentPermissions(
      props.documentId,
      currentPermissions.value
    )
    if (!resp || resp.success === false) {
      throw new Error(resp?.error || t('chatbotPermissions.documents.permissionModal.errors.updateFailed'))
    }
    emit('updated', { documentId: props.documentId })
    emit('close')
  } catch (err) {
    console.error('Failed to save permissions:', err)
    localError.value = err?.message || t('chatbotPermissions.documents.permissionModal.errors.saveFailed')
  } finally {
    localSaving.value = false
  }
}
</script>
