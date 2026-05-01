<template>
  <div class="space-y-4">
    <PermissionHeader
      :title="rolesHeaderConfig.title"
      :icon="UsersIcon"
      :card-class="rolesHeaderConfig.cardClass"
      :icon-wrapper-class="rolesHeaderConfig.iconWrapperClass"
      :color="rolesHeaderConfig.color"
    >
      <template #meta>
        <span class="font-medium text-indigo-600">
          {{
            t('chatbotPermissions.documents.roles.header.total', {
              count: rolesDisplayRange.total || filteredRoles.length,
            })
          }}
        </span>
        <span class="text-gray-400">•</span>
        <span>{{ t('chatbotPermissions.documents.roles.header.active', { count: activeRolesCount }) }}</span>
      </template>

      <template #actions>
        <button
          @click="doRefresh"
          class="flex items-center px-4 py-2.5 text-sm font-medium text-indigo-600 bg-white hover:bg-indigo-50 border border-indigo-200 rounded-lg transition-colors shadow-sm"
        >
          <RotateCcw class="w-4 h-4 mr-2" />
          {{ t('chatbotPermissions.documents.roles.actions.refresh') }}
        </button>
        <button
          @click="openCreateRoleModal"
          class="flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all shadow-sm text-white"
          :class="rolesHeaderConfig.buttonClass"
        >
          <PlusIcon class="w-4 h-4 mr-2" />
          <span>{{ t('chatbotPermissions.documents.roles.actions.add') }}</span>
        </button>
      </template>
    </PermissionHeader>

    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
      <div class="relative w-full md:w-72">
        <SearchIcon class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
        <input
          :value="roleSearchQuery"
          type="text"
          :placeholder="t('chatbotPermissions.documents.roles.filters.searchPlaceholder')"
          class="pl-9 pr-3 py-2 w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          @input="doUpdateSearch($event.target.value)"
        />
      </div>

      <div class="flex items-center w-full md:w-auto gap-2 sm:gap-3">
        <div class="flex w-full sm:w-48 justify-end">
          <FilterDropdown
            class="w-full sm:w-auto"
            :model-value="roleStatusFilter"
            :options="statusOptions"
            value-key="value"
            label-key="label"
            @update:modelValue="doUpdateStatus"
          />
        </div>
      </div>
    </div>

    <div v-if="successMessage" class="bg-green-50 border border-green-200 text-green-700 p-3 rounded-lg text-sm">
      {{ successMessage }}
    </div>
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
      {{ error }}
    </div>

    <div
      v-if="loading"
      class="bg-white rounded-xl border border-gray-200 p-12 flex flex-col items-center justify-center space-y-4"
    >
      <div class="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      <p class="text-sm text-gray-500">
        {{ t('chatbotPermissions.documents.roles.loading') }}
      </p>
    </div>

    <div v-else>
      <div
        class="bg-white border border-gray-200 rounded-xl relative min-w-0"
        style="min-height: 60vh; overflow-y: auto; overflow-x: hidden"
      >
        <div :class="['p-4', gridColsClass, 'gap-4']">
          <div
            v-for="role in pagedRoles"
            :key="role.id"
            class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow w-full h-full flex flex-col"
          >
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 flex-1 min-w-0">
              <div class="flex items-center space-x-3 flex-1 min-w-0">
                <div
                  :class="[
                    'w-10 h-10 md:w-12 md:h-12 rounded-full hidden md:flex items-center justify-center text-white text-lg font-semibold shadow-lg',
                    role.colorHex ? '' : 'bg-gradient-to-br from-blue-500 to-indigo-500',
                  ]"
                  :style="role.colorHex ? { backgroundColor: role.colorHex } : {}"
                >
                  {{ role.icon || role.initial || role.role_name?.charAt(0) || '?' }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2">
                    <h4 class="text-base md:text-lg font-semibold text-gray-900 break-words">{{ role.name }}</h4>
                    <span
                      :class="[
                        'inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full',
                        role.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600',
                      ]"
                    >
                      {{
                        role.isActive
                          ? t('chatbotPermissions.documents.roles.status.active')
                          : t('chatbotPermissions.documents.roles.status.inactive')
                      }}
                    </span>
                  </div>
                </div>

                <div class="flex items-center space-x-3 self-center ml-auto whitespace-nowrap">
                  <button
                    class="relative inline-flex items-center h-6 w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    :class="role.isActive ? 'bg-green-500' : 'bg-gray-200'"
                    :disabled="role._toggling"
                    @click="doToggleActive(role)"
                  >
                    <span v-if="role._toggling" class="absolute inset-0 flex items-center justify-center">
                      <svg
                        class="animate-spin h-4 w-4 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          class="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          stroke-width="4"
                        ></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                      </svg>
                    </span>
                    <span
                      v-else
                      :class="[
                        'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                        role.isActive ? 'translate-x-6' : 'translate-x-1',
                      ]"
                    ></span>
                  </button>
                </div>
              </div>
            </div>

            <div
              class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mt-4 pt-4 border-t border-gray-100"
            >
              <div class="flex flex-col sm:flex-row gap-2">
                <button
                  @click="startEditRole(role)"
                  class="w-full sm:w-auto flex items-center justify-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg"
                >
                  <EditIcon class="w-4 h-4 mr-1" />
                  {{ t('chatbotPermissions.documents.roles.actions.edit') }}
                </button>
                <button
                  @click="viewRoleUsers(role)"
                  class="w-full sm:w-auto flex items-center justify-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg"
                >
                  <UsersIcon class="w-4 h-4 mr-1" />
                  {{ t('chatbotPermissions.documents.roles.actions.viewUsers') }}
                </button>
                <button
                  @click="deleteRole(role)"
                  class="w-full sm:w-auto flex items-center justify-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg"
                  :disabled="role.userCount > 0"
                  :title="
                    role.userCount > 0
                      ? t('chatbotPermissions.documents.roles.actions.deleteTooltip')
                      : t('chatbotPermissions.documents.roles.actions.deleteRole')
                  "
                >
                  <TrashIcon class="w-4 h-4 mr-1" />
                  {{ t('chatbotPermissions.documents.roles.actions.delete') }}
                </button>
              </div>

              <div class="mt-3 sm:mt-0 flex flex-wrap gap-2">
                <span
                  class="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-50 text-blue-700 rounded-full"
                >
                  {{
                    t('chatbotPermissions.documents.roles.tags.users', {
                      count: role.userCount || 0,
                    })
                  }}
                </span>
              </div>
            </div>
          </div>
          <div v-if="!error && !filteredRoles.length" class="p-8 text-center text-gray-500">
            {{ t('chatbotPermissions.documents.roles.empty') }}
          </div>
        </div>
      </div>
      <div
        v-if="!error && filteredRoles.length"
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-4"
      >
        <div class="text-sm text-gray-600">
          {{
            t('chatbotPermissions.documents.roles.pagination.range', {
              start: rolesDisplayRange.start,
              end: rolesDisplayRange.end,
              total: filteredRoles.length,
            })
          }}
        </div>
        <div class="flex items-center justify-between sm:justify-end gap-2">
          <button
            @click="gotoRolesPage(rolesCurrentPage - 1)"
            :disabled="rolesCurrentPage === 1"
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ t('chatbotPermissions.documents.roles.pagination.prev') }}
          </button>
          <span class="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-lg">
            {{ rolesCurrentPage }} / {{ rolesTotalPages }}
          </span>
          <button
            @click="gotoRolesPage(rolesCurrentPage + 1)"
            :disabled="rolesCurrentPage === rolesTotalPages"
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ t('chatbotPermissions.documents.roles.pagination.next') }}
          </button>
          <select
            :value="rolesPerPage"
            @change="doUpdatePerPage(Number($event.target.value))"
            class="px-3 pr-10 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option v-for="size in perPageOptions" :key="size" :value="size">
              {{ t('chatbotPermissions.documents.pagination.perPageOption', { count: size }) }}
            </option>
          </select>
        </div>
      </div>
      <!-- Modals -->
      <RoleCrudModal
        :visible="showRoleCrudModal"
        :mode="roleCrudMode"
        :loading="roleCrudLoading"
        :saving="roleCrudSaving"
        :error="roleCrudError"
        :form="roleCrudForm"
        @update:form="updateRoleCrudForm"
        @close="closeRoleCrudModal"
        @submit="saveRole"
      />

      <RoleUsersModal
        :visible="showRoleUsersModal"
        :role-info="selectedRoleInfo"
        :users="selectedRoleUsers"
        :loading="roleUsersLoading"
        :error="roleUsersError"
        @close="closeRoleUsersModal"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  RotateCcw,
  Search as SearchIcon,
  Plus as PlusIcon,
  Edit as EditIcon,
  Users as UsersIcon,
  Trash2 as TrashIcon,
} from 'lucide-vue-next'
import FilterDropdown from '@/components/permissions/common/FilterDropdown.vue'
import PermissionHeader from '@/components/permissions/common/PermissionHeader.vue'
import RoleCrudModal from '@/components/permissions/modals/RoleCrudModal.vue'
import RoleUsersModal from '@/components/permissions/modals/RoleUsersModal.vue'
import roleService from '@/services/roleService'
import { useRolesManagement } from '@/composables/useRolesManagement'
import { unwrapResponse } from '@/services/userService'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

// Internal roles management (self-contained)
const { t } = useI18n()

const {
  roles,
  loading,
  error,
  successMessage,
  roleSearchQuery,
  roleStatusFilter,
  rolesPerPage,
  rolesCurrentPage,
  availableRoles,
  filteredRoles,
  rolesTotalPages,
  pagedRoles,
  rolesDisplayRange,
  activeRolesCount,
  gotoRolesPage,
  refreshRoles,
  loadAvailableRoles,
} = useRolesManagement()

// Responsive grid handled by CSS classes; no JS sizing required

const perPageOptions = computed(() => [3, 6, 9, 12])
const statusOptions = computed(() => [
  { value: 'all', label: t('chatbotPermissions.documents.roles.filters.allStatus') },
  { value: 'active', label: t('chatbotPermissions.documents.roles.filters.active') },
  { value: 'inactive', label: t('chatbotPermissions.documents.roles.filters.inactive') },
])

// Decide grid columns based on roles per page (responsive mapping)
const gridColsClass = computed(() => {
  const per = Number(rolesPerPage.value) || 6
  // mapping strategy:
  // - <= 3 per page: 1 column on sm/lg
  // - <= 6 per page: 2 columns on sm/lg
  // - > 6: 2 cols on sm, 3 cols on lg
  if (per <= 3) return 'grid grid-cols-1 sm:grid-cols-1 lg:grid-cols-1'
  if (per <= 6) return 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2'
  return 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'
})

const doRefresh = () => refreshRoles()
const doUpdateSearch = (val) => {
  roleSearchQuery.value = val || ''
}
const doUpdateStatus = (val) => {
  roleStatusFilter.value = val || 'all'
}
const doUpdatePerPage = (val) => {
  rolesPerPage.value = Number(val) || 6
}

const doToggleActive = async (role) => {
  if (!role || role._toggling) return
  role._toggling = true
  const previous = !!role.isActive
  role.isActive = !previous
  try {
    const response = await roleService.toggleRoleStatus(role.id, role.isActive)
    if (!response || response.success === false) {
      role.isActive = previous
      throw new Error(response?.error || 'Toggle failed')
    }
  } catch (err) {
    role.isActive = previous
    console.error('Toggle role status error:', err)
  } finally {
    role._toggling = false
  }
}

const doTogglePermission = (role, permission) => {
  permission.checked = !permission.checked
  // Placeholder for future API if needed
}

const rolesHeaderConfig = computed(() => ({
  title: t('chatbotPermissions.documents.roles.header.title'),
  cardClass: 'bg-gradient-to-r from-blue-50 to-indigo-50 border border-indigo-100',
  iconWrapperClass: 'bg-gradient-to-br from-blue-500 to-indigo-500',
  color: 'indigo',
  buttonClass: 'bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 shadow-lg',
}))

// Role CRUD modal state
const showRoleCrudModal = ref(false)
const roleCrudMode = ref('create')
const roleCrudLoading = ref(false)
const roleCrudSaving = ref(false)
const roleCrudError = ref('')
const roleCrudForm = ref({
  id: '',
  role_name: '',
  description: '',
  is_active: true,
  priority: 1,
  color: '#6b7280',
  icon: '',
  user_management: false,
})
const updateRoleCrudForm = (form) => {
  roleCrudForm.value = {
    id: '',
    role_name: '',
    description: '',
    is_active: true,
    priority: 1,
    color: '#6b7280',
    icon: '',
    user_management: false,
    ...(form || {}),
  }
}
const openCreateRoleModal = () => {
  roleCrudMode.value = 'create'
  roleCrudError.value = ''
  updateRoleCrudForm({})
  showRoleCrudModal.value = true
}
const closeRoleCrudModal = () => {
  showRoleCrudModal.value = false
  roleCrudLoading.value = false
  roleCrudSaving.value = false
  roleCrudError.value = ''
  roleCrudMode.value = 'create'
  updateRoleCrudForm({})
}
const startEditRole = (role) => {
  if (!role) return
  roleCrudMode.value = 'edit'
  roleCrudError.value = ''
  updateRoleCrudForm({
    id: role.id,
    role_name: role.name,
    description: role.description || '',
    is_active: !!role.isActive,
    priority: role.priority ?? 1,
    color: role.colorHex || '#6b7280',
    icon: role.icon || role.initial,
    user_management: !!role.user_management,
  })
  showRoleCrudModal.value = true
}
const saveRole = async () => {
  const roleName = (roleCrudForm.value.role_name || '').trim()
  if (!roleName) {
    roleCrudError.value = 'Tên vai trò là bắt buộc.'
    return
  }
  roleCrudSaving.value = true
  roleCrudError.value = ''
  const payload = {
    role_name: roleName,
    description: roleCrudForm.value.description || '',
    is_active: !!roleCrudForm.value.is_active,
    priority: Number(roleCrudForm.value.priority) || 1,
    color: roleCrudForm.value.color || '#6b7280',
    icon: (roleCrudForm.value.icon || roleName.charAt(0) || '?').toUpperCase(),
    user_management: !!roleCrudForm.value.user_management,
  }
  try {
    let response
    if (roleCrudMode.value === 'create') response = await roleService.createRole(payload)
    else {
      if (!roleCrudForm.value.id) throw new Error(t('chatbotPermissions.documents.roles.errors.unknownRole'))
      response = await roleService.updateRole(roleCrudForm.value.id, payload)
    }
    const result = unwrapResponse(response) || response
    if (!result || result.success === false)
      throw new Error(result?.error || result?.message || t('chatbotPermissions.documents.roles.errors.saveFailed'))
    await refreshRoles()
    await loadAvailableRoles()
    // simple success message
    closeRoleCrudModal()
  } catch (err) {
    console.error('Save role failed:', err)
    roleCrudError.value = err?.message || t('chatbotPermissions.documents.roles.errors.saveFailed')
  } finally {
    roleCrudSaving.value = false
  }
}

// Role Users modal state
const showRoleUsersModal = ref(false)
const roleUsersLoading = ref(false)
const roleUsersError = ref('')
const selectedRoleUsers = ref([])
const selectedRoleInfo = ref(null)
const closeRoleUsersModal = () => {
  showRoleUsersModal.value = false
  roleUsersLoading.value = false
  roleUsersError.value = ''
  selectedRoleUsers.value = []
  selectedRoleInfo.value = null
}

const viewRoleUsers = async (role) => {
  if (!role || !role.id) return
  selectedRoleInfo.value = {
    id: role.id,
    roleName: role.name,
    roleCode: role.roleCode || '',
    description: role.description || '',
    userCount: role.userCount ?? 0,
    isActive: role.isActive ?? true,
  }
  showRoleUsersModal.value = true
  roleUsersLoading.value = true
  try {
    const response = await roleService.getRoleDetails(role.id)
    const payload = response?.data ?? response
    const data = payload?.data ?? payload
    const users = Array.isArray(data?.users) ? data.users : []
    selectedRoleUsers.value = users
    const rawIsActive = data?.is_active
    const computedIsActive =
      typeof rawIsActive === 'boolean'
        ? rawIsActive
        : rawIsActive == null
        ? !!selectedRoleInfo.value.isActive
        : !!rawIsActive
    selectedRoleInfo.value = {
      id: data?.id || selectedRoleInfo.value.id,
      roleName: data?.role_name || data?.name || selectedRoleInfo.value.roleName,
      roleCode: data?.role_code || selectedRoleInfo.value.roleCode,
      description: data?.description ?? selectedRoleInfo.value.description,
      userCount: data?.user_count ?? users.length ?? selectedRoleInfo.value.userCount,
      isActive: computedIsActive,
      lastModified: data?.modified || null,
      createdAt: data?.creation || null,
    }
  } catch (err) {
    console.error('Load role users failed:', err)
    roleUsersError.value = err?.message || t('chatbotPermissions.documents.roles.errors.loadUsersFailed')
  } finally {
    roleUsersLoading.value = false
  }
}

// Delete role
const deleteRole = async (role) => {
  if (!role || !role.id) return

  // Check if role has users
  if (role.userCount > 0) {
    notificationStore.notify(`Không thể xóa role "${role.name}" vì đang có ${role.userCount} user được gán.`, 'warning')
    return
  }

  // Confirm deletion
  const confirmMessage = `Bạn có chắc chắn muốn xóa role "${role.name}"?\n\nHành động này không thể hoàn tác.`
  if (!confirm(confirmMessage)) return

  try {
    const response = await roleService.deleteRole(role.id)
    const result = unwrapResponse(response) || response

    if (!result || result.success === false) {
      throw new Error(result?.error || result?.message || 'Không thể xóa role')
    }

    // Refresh roles list
    await refreshRoles()
    await loadAvailableRoles()

    notificationStore.notify(`Role "${role.name}" đã được xóa thành công.`, 'success')
  } catch (err) {
    console.error('Delete role failed:', err)
    notificationStore.notify(err?.message || 'Không thể xóa role', 'error')
  }
}

// Initial load
doRefresh()
</script>
