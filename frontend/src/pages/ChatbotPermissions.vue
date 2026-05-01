<template>
  <div
    class="flex flex-col h-full min-h-0"
    style="overflow-y: auto; overflow-x: hidden; -webkit-overflow-scrolling: touch"
  >
    <div
      class="flex-1 min-h-0 overflow-y-auto bg-gray-50"
      style="overflow-x: hidden; -webkit-overflow-scrolling: touch"
    >
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

      <!-- Stats Cards -->
      <div class="px-6 py-6" style="max-width: 100%; overflow-x: hidden">
        <div class="flex flex-nowrap gap-4 mb-6">
          <div v-for="card in statCards" :key="card.key" class="w-64">
            <StatsCard
              :title="card.title"
              :value="card.value"
              :description="card.description"
              :icon="card.icon"
              :icon-color="card.iconColor"
              :format="card.format || 'number'"
              :compact="card.compact ?? false"
            />
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="bg-white rounded-xl shadow-sm border mb-6" style="overflow: hidden">
          <div class="border-b border-gray-200">
            <NavigationTabs :tabs="tabs" :active-tab="activeTab" @change="activeTab = $event" />
          </div>

          <!-- Tab Content -->
          <div class="px-6 py-3 min-w-0" style="overflow-x: hidden">
            <!-- Roles & Permissions Tab -->
            <RolesTab v-if="activeTab === 'roles'" />

            <!-- Document Permissions Tab (simplified: tab manages its own document state) -->
            <DocumentsTab v-if="activeTab === 'documents'" />

            <!-- Database Permissions Tab -->
            <DatabaseTab
              v-if="activeTab === 'database'"
              :database-tables="databaseTables"
              @refresh="refreshDatabase"
              @open-create-permission="openCreateDatabasePermissionModal"
              @toggle-table-status="toggleTableStatus"
              @toggle-table-permission="
                ({ table, permission, action }) => toggleTablePermission(table, permission, action)
              "
              @edit-table="editTable"
              @view-table-data="viewTableData"
            />

            <!-- Manage Users Tab -->
            <UsersTab v-if="activeTab === 'users'" />

            <!-- Audit Logs Tab -->
            <AuditTab v-if="activeTab === 'audit'" :logs="auditLogs" @export="exportAuditLogs" />
          </div>
        </div>
      </div>
    </div>

    <!-- Role Users Modal -->
    <RoleUsersModal
      :visible="showRoleUsersModal"
      :role-info="selectedRoleInfo"
      :users="selectedRoleUsers"
      :loading="roleUsersLoading"
      :error="roleUsersError"
      @close="closeRoleUsersModal"
    />

    <!-- Document edit modal moved into DocumentsTab -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { createResource } from 'frappe-ui'
import {
  Shield as ShieldIcon,
  Users as UsersIcon,
  User as UserIcon,
  FileText as FileTextIcon,
  Database as DatabaseIcon,
} from 'lucide-vue-next'
import roleService from '../services/roleService.js'
// document logic moved into DocumentsTab
import RoleCrudModal from '@/components/permissions/modals/RoleCrudModal.vue'
import RoleUsersModal from '@/components/permissions/modals/RoleUsersModal.vue'
import RolesTab from '@/components/permissions/tabs/RolesTab.vue'
import DocumentsTab from '@/components/permissions/tabs/DocumentsTab.vue'
import DatabaseTab from '@/components/permissions/tabs/DatabaseTab.vue'
import UsersTab from '@/components/permissions/tabs/UsersTab.vue'
import AuditTab from '@/components/permissions/tabs/AuditTab.vue'
import NavigationTabs from '@/components/permissions/common/NavigationTabs.vue'
import {
  getUsers as fetchUsers,
  updateUser as updateUserService,
  deleteUser as deleteUserService,
  unwrapResponse,
} from '@/services/userService'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import { useRolesManagement } from '@/composables/useRolesManagement'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

// Reactive data
const activeTab = ref('roles')
const showRoleUsersModal = ref(false)
const showCreateDatabasePermissionModal = ref(false)
const showCreateUserModal = ref(false)
const roleUsersLoading = ref(false)
const roleUsersError = ref('')
const selectedRoleUsers = ref([])
const selectedRoleInfo = ref(null)

// Search and filter data
const userSearchQuery = ref('')
const userRoleFilter = ref('')

const stats = ref({
  totalUsers: 0,
  activeRoles: 0,
  protectedDocs: 0,
  databaseTables: 0,
})

const { t } = useI18n()
const tabs = computed(() => [
  { id: 'roles', name: t('chatbotPermissions.tabs.roles'), icon: UsersIcon },
  { id: 'documents', name: t('chatbotPermissions.tabs.documents'), icon: FileTextIcon },
  { id: 'database', name: t('chatbotPermissions.tabs.database'), icon: DatabaseIcon },
  { id: 'users', name: t('chatbotPermissions.tabs.users'), icon: UsersIcon },
  { id: 'audit', name: t('chatbotPermissions.tabs.audit'), icon: ShieldIcon },
])

const statCards = computed(() => {
  const totalUsers = stats.value?.totalUsers ?? 0
  const activeRoles = stats.value?.activeRoles ?? 0
  const protectedDocs = stats.value?.protectedDocs ?? 0
  const databaseTables = stats.value?.databaseTables ?? 0

  return [
    {
      key: 'totalUsers',
      title: t('chatbotPermissions.stats.users'),
      value: totalUsers,
      description: t('chatbotPermissions.stats.totalUsers'),
      icon: UsersIcon,
      iconColor: 'blue',
      format: 'number',
      compact: true,
    },
    {
      key: 'activeRoles',
      title: t('chatbotPermissions.stats.roles'),
      value: activeRoles,
      description: t('chatbotPermissions.stats.activeRoles'),
      icon: ShieldIcon,
      iconColor: 'green',
      format: 'number',
      compact: true,
    },
    {
      key: 'protectedDocs',
      title: t('chatbotPermissions.stats.documents'),
      value: protectedDocs,
      description: t('chatbotPermissions.stats.protectedDocs'),
      icon: FileTextIcon,
      iconColor: 'yellow',
      format: 'number',
      compact: true,
    },
    {
      key: 'databaseTables',
      title: t('chatbotPermissions.stats.database'),
      value: databaseTables,
      description: t('chatbotPermissions.stats.databaseTables'),
      icon: DatabaseIcon,
      iconColor: 'purple',
      format: 'number',
      compact: true,
    },
  ]
})

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
  gotoRolesPage,
  refreshRoles,
  loadAvailableRoles,
} = useRolesManagement()
const showRoleCrudModal = ref(false)
const roleCrudMode = ref('create') // 'create' | 'edit'
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

const setRoleSearchQuery = (value) => {
  roleSearchQuery.value = value ?? ''
}

const setRoleStatusFilter = (value) => {
  roleStatusFilter.value = value ?? 'all'
}

const setRolesPerPage = (value) => {
  const parsed = Number(value) || rolesPerPage.value
  rolesPerPage.value = parsed
  rolesCurrentPage.value = 1
}

const openCreateDatabasePermissionModal = () => {
  showCreateDatabasePermissionModal.value = true
}

const updateUserSearchQuery = (value) => {
  userSearchQuery.value = value ?? ''
}

const updateUserRoleFilter = (value) => {
  userRoleFilter.value = value ?? ''
}

const openCreateUserModal = () => {
  showCreateUserModal.value = true
}

const refreshStats = async () => {
  try {
    const response = await roleService.getRoleStatistics()
    if (response?.success && response?.data) {
      const data = response.data
      stats.value = {
        totalUsers: data.total_users ?? stats.value.totalUsers,
        activeRoles: data.active_roles ?? stats.value.activeRoles,
        protectedDocs: data.protected_docs ?? stats.value.protectedDocs,
        databaseTables: data.database_tables ?? stats.value.databaseTables,
      }
    }
  } catch (err) {
    console.error('Error loading stats:', err)
  }
}

// DocumentsTab now manages document state and modals internally
const showEditUserModal = ref(false)
const userEditLoading = ref(false)
const userEditSaving = ref(false)
const userEditError = ref('')
const userEditForm = ref({
  id: '',
  email: '',
  full_name: '',
  first_name: '',
  last_name: '',
  mobile_no: '',
  phone: '',
  language: 'vi',
  time_zone: 'Asia/Ho_Chi_Minh',
  enabled: true,
  roles: [],
})
const userEditOriginal = ref(null)

// Document filters
const documentSearchQuery = ref('')
const documentFileTypeFilter = ref('')
const documentAccessLevelFilter = ref('')
const documentRoleFilter = ref('')

// Filter options provided by backend (from composable: fileTypes, accessLevels)

// documentsDisplayRange is provided by the useDocumentPermissions composable

watch(
  userEditForm,
  () => {
    if (userEditLoading.value) return
    if (userEditError.value) {
      userEditError.value = ''
    }
  },
  { deep: true }
)

watch(
  roleCrudForm,
  () => {
    if (roleCrudError.value) {
      roleCrudError.value = ''
    }
  },
  { deep: true }
)

// Documents-related UI and handlers moved into DocumentsTab
const databaseTables = ref([
  {
    id: 1,
    name: 'AI Document',
    records: 3542,
    isActive: true,
    permissions: [
      { id: 'admin', name: 'Administrator', read: true, write: true, delete: true },
      { id: 'manager', name: 'Manager', read: true, write: true, delete: false },
      { id: 'employee', name: 'Employee', read: true, write: false, delete: false },
      { id: 'guest', name: 'Guest', read: false, write: false, delete: false },
    ],
  },
  {
    id: 2,
    name: 'Chatbot Permission',
    records: 47,
    isActive: true,
    permissions: [
      { id: 'admin', name: 'Administrator', read: true, write: true, delete: true },
      { id: 'manager', name: 'Manager', read: true, write: false, delete: false },
      { id: 'employee', name: 'Employee', read: false, write: false, delete: false },
      { id: 'guest', name: 'Guest', read: false, write: false, delete: false },
    ],
  },
  {
    id: 3,
    name: 'User',
    records: 1248,
    isActive: true,
    permissions: [
      { id: 'admin', name: 'Administrator', read: true, write: true, delete: true },
      { id: 'manager', name: 'Manager', read: true, write: false, delete: false },
      { id: 'employee', name: 'Employee', read: false, write: false, delete: false },
      { id: 'guest', name: 'Guest', read: false, write: false, delete: false },
    ],
  },
  {
    id: 4,
    name: 'Chatbot Access Log',
    records: 12543,
    isActive: true,
    permissions: [
      { id: 'admin', name: 'Administrator', read: true, write: false, delete: true },
      { id: 'manager', name: 'Manager', read: true, write: false, delete: false },
      { id: 'employee', name: 'Employee', read: false, write: false, delete: false },
      { id: 'guest', name: 'Guest', read: false, write: false, delete: false },
    ],
  },
])

// Users data (loaded from API)
const users = ref([])
const usersLoading = ref(false)
const usersPagination = ref({
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 0,
  has_next: false,
  has_prev: false,
})
const VISIBLE_ROLES_LIMIT = 2

// Normalize API user into the shape used by this table

const loadUsers = async (opts = {}) => {
  usersLoading.value = true
  try {
    const page = opts.page ?? usersPagination.value.page ?? 1
    const pageSize = opts.page_size ?? usersPagination.value.page_size ?? 20

    const { users: apiUsers, pagination } = await fetchUsers({
      page,
      pageSize,
      search: userSearchQuery.value,
      role: userRoleFilter.value,
    })

    users.value = Array.isArray(apiUsers) ? apiUsers.filter(Boolean) : []

    const info = pagination || {}
    usersPagination.value = {
      page: info.page ?? page,
      page_size: info.page_size ?? pageSize,
      total_count: info.total_count ?? usersPagination.value.total_count ?? users.value.length,
      total_pages: info.total_pages ?? usersPagination.value.total_pages ?? 1,
      has_next: typeof info.has_next === 'boolean' ? info.has_next : (apiUsers || []).length === pageSize,
      has_prev: typeof info.has_prev === 'boolean' ? info.has_prev : page > 1,
    }
  } catch (err) {
    console.error('Load users error (User DocType):', err)
  } finally {
    usersLoading.value = false
  }
}

const availableRolesForSelect = computed(() => {
  if (!availableRoles.value) return []
  return availableRoles.value.map((r) => (typeof r === 'string' ? r : r.name || r.role_name || '')).filter(Boolean)
})

const onUserSearchInput = () => {
  usersPagination.value.page = 1
  void loadUsers()
}

const onUserRoleChange = () => {
  usersPagination.value.page = 1
  void loadUsers()
}

const auditLogs = ref([]) // Will be loaded by AuditTab component

const filteredUsers = computed(() => {
  const raw = Array.isArray(users.value) ? users.value : []
  let filtered = raw.slice()

  if (userSearchQuery.value) {
    const query = userSearchQuery.value.toLowerCase()
    filtered = filtered.filter((user) => {
      if (!user) return false
      const name = (user.name || '').toLowerCase()
      const email = (user.email || '').toLowerCase()
      return name.includes(query) || email.includes(query)
    })
  }

  if (userRoleFilter.value) {
    filtered = filtered.filter((user) => {
      if (!user) return false
      const rolesList = user.roles || []
      return rolesList.some((r) => {
        if (!r && r !== 0) return false
        if (typeof r === 'string') {
          return r === userRoleFilter.value
        }
        const roleName = r.role_name || r.role || r.name || ''
        return roleName === userRoleFilter.value
      })
    })
  }

  return filtered
})

// Methods
const getAccessLevelClass = (level) => {
  const classes = {
    Public: 'bg-green-100 text-green-800',
    Internal: 'bg-blue-100 text-blue-800',
  }
  return classes[level] || 'bg-gray-100 text-gray-800'
}

const toggleRoleStatus = async (role) => {
  if (!role || role._toggling) return

  role._toggling = true
  const previous = !!role.isActive
  const desired = !previous
  role.isActive = desired

  try {
    const response = await roleService.toggleRoleStatus(role.id, desired)
    const success = response?.success === true

    if (success) {
      role.isActive = !!(response?.data?.is_active ?? desired)
      await refreshStats()
    } else {
      role.isActive = previous
      error.value = response?.error || response?.message || 'Failed to toggle role status'
      console.error('Toggle role failed:', response)
    }
  } catch (err) {
    role.isActive = previous
    error.value = err.message || 'Network error'
    console.error('Error toggling role status:', err)
  } finally {
    role._toggling = false
  }
}

const updateRolePermission = (role, permission) => {
  // Optimistic UI: toggle immediately
  const previous = !!permission.checked
  permission.checked = !previous(
    // Fire-and-forget background update
    async () => {
      try {
        // Assume document context - try to find current document from surrounding loop
        // In UI this handler is called inside a per-document render so `role` and `permission` are sufficient
        const updates = { [role.name || role.role_name || role.id]: !!permission.checked }
        const response = await documentPermissionService.updateDocumentPermission(
          /* documentName */ permission.__documentName || permission.documentName || null,
          updates
        )

        // If API reports failure, rollback and surface error
        if (!response || !response.success) {
          permission.checked = previous
          error.value = response?.error || response?.message || 'Failed to update permission'
          console.error('Background permission update failed:', response)
        }
      } catch (err) {
        permission.checked = previous
        error.value = err.message || 'Network error'
        console.error('Background permission update error:', err)
      }
    }
  )()
}

const toggleDocumentSelection = (document, isSelected) => {
  return docPerm.toggleDocumentSelection(document, isSelected)
}

const toggleSelectAllDocuments = (selectAll) => {
  return docPerm.toggleSelectAllDocuments(selectAll)
}

const allDocumentsSelected = computed(() => {
  return documents.value.length > 0 && documents.value.every((doc) => bulkSelection.value.has(doc.name))
})

// Bulk permissions handled inside DocumentsTab

// Old function removed - replaced with async version below

const resetRoleUsersState = () => {
  roleUsersError.value = ''
  selectedRoleUsers.value = []
}

const closeRoleUsersModal = () => {
  showRoleUsersModal.value = false
  selectedRoleInfo.value = null
  roleUsersLoading.value = false
  resetRoleUsersState()
}

const resetRoleCrudForm = () => {
  updateRoleCrudForm({})
}

const openCreateRoleModal = () => {
  roleCrudMode.value = 'create'
  roleCrudError.value = ''
  resetRoleCrudForm()
  showRoleCrudModal.value = true
}

const closeRoleCrudModal = () => {
  showRoleCrudModal.value = false
  roleCrudLoading.value = false
  roleCrudSaving.value = false
  roleCrudError.value = ''
  roleCrudMode.value = 'create'
  resetRoleCrudForm()
}

const startEditRole = (role) => {
  if (!role) return
  roleCrudMode.value = 'edit'
  roleCrudError.value = ''
  resetRoleCrudForm()
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

  if (roleCrudMode.value === 'edit' && !roleCrudForm.value.id) {
    roleCrudError.value = 'Không xác định được vai trò cần cập nhật.'
    roleCrudSaving.value = false
    return
  }

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
    if (roleCrudMode.value === 'create') {
      response = await roleService.createRole(payload)
    } else {
      response = await roleService.updateRole(roleCrudForm.value.id, payload)
    }

    const result = unwrapResponse(response) || response
    if (!result || result.success === false) {
      throw new Error(result?.error || result?.message || 'Không thể lưu vai trò')
    }

    await refreshRoles()
    await refreshStats()
    await loadAvailableRoles()
    successMessage.value =
      roleCrudMode.value === 'create'
        ? `Đã tạo vai trò \"${payload.role_name}\"`
        : `Đã cập nhật vai trò \"${payload.role_name}\"`

    closeRoleCrudModal()

    setTimeout(() => {
      if (successMessage.value && successMessage.value.includes(payload.role_name)) {
        successMessage.value = ''
      }
    }, 3000)
  } catch (err) {
    console.error('Save role failed:', err)
    roleCrudError.value = err?.message || 'Không thể lưu vai trò'
  } finally {
    roleCrudSaving.value = false
  }
}

const resetUserEditForm = () => {
  userEditForm.value = {
    id: '',
    email: '',
    full_name: '',
    first_name: '',
    last_name: '',
    mobile_no: '',
    phone: '',
    language: 'vi',
    time_zone: 'Asia/Ho_Chi_Minh',
    enabled: true,
    roles: [],
  }
  userEditOriginal.value = null
}

const editUser = async (user) => {
  if (!user || !user.id) return

  resetUserEditForm()
  userEditError.value = ''
  showEditUserModal.value = true
  userEditLoading.value = true
  userEditSaving.value = false

  try {
    if (!availableRoles.value.length) {
      await loadAvailableRoles()
    }

    const response = await createResource({
      url: 'dbiz_ai_agent.api.users.get_user_detail',
      params: { user_id: user.id },
      method: 'GET',
    }).fetch()

    const payload = unwrapResponse(response) || response
    const data = payload?.data || payload || {}

    if (!data || !data.email) {
      throw new Error('Không tìm thấy thông tin người dùng')
    }

    // Backend giờ trả về AI roles từ Contact (mảng các role IDs như "AI-ROLE-0001")
    let normalizedRoles = []
    if (Array.isArray(data.roles)) {
      normalizedRoles = data.roles.filter((roleId) => {
        if (!roleId) return false
        return availableRoles.value.some((r) => (r.id || r.name) === roleId)
      })
    }

    userEditForm.value = {
      id: data.name || user.id,
      email: data.email || user.email,
      full_name: data.full_name || data.email || '',
      first_name: data.first_name || '',
      last_name: data.last_name || '',
      mobile_no: data.mobile_no || '',
      phone: data.phone || '',
      language: data.language || 'vi',
      time_zone: data.time_zone || 'Asia/Ho_Chi_Minh',
      enabled: data.enabled !== undefined ? !!data.enabled : user.isActive,
      roles: normalizedRoles,
    }

    userEditOriginal.value = JSON.parse(JSON.stringify(userEditForm.value))
  } catch (err) {
    console.error('Failed to load user detail:', err)
    userEditError.value = err?.message || 'Không thể tải thông tin người dùng'
  } finally {
    userEditLoading.value = false
  }
}

const closeEditUserModal = () => {
  showEditUserModal.value = false
  userEditLoading.value = false
  userEditSaving.value = false
  userEditError.value = ''
  resetUserEditForm()
}

const toggleUserRole = (roleName, isChecked) => {
  if (!userEditForm.value.roles) {
    userEditForm.value.roles = []
  }

  if (isChecked) {
    // Thêm role nếu chưa có
    if (!userEditForm.value.roles.includes(roleName)) {
      userEditForm.value.roles.push(roleName)
    }
  } else {
    // Xóa role nếu có
    const index = userEditForm.value.roles.indexOf(roleName)
    if (index > -1) {
      userEditForm.value.roles.splice(index, 1)
    }
  }
}

const saveUserEdits = async () => {
  if (!userEditForm.value.id || !userEditOriginal.value) return

  userEditError.value = ''
  userEditSaving.value = true

  try {
    const payload = {}
    const fields = ['full_name', 'first_name', 'last_name', 'mobile_no', 'phone', 'language', 'time_zone', 'enabled']
    fields.forEach((field) => {
      if (userEditForm.value[field] !== userEditOriginal.value[field]) {
        payload[field] = userEditForm.value[field]
      }
    })

    const currentRoles = Array.isArray(userEditForm.value.roles) ? userEditForm.value.roles.slice().sort() : []
    const originalRoles = Array.isArray(userEditOriginal.value.roles) ? userEditOriginal.value.roles.slice().sort() : []
    if (JSON.stringify(currentRoles) !== JSON.stringify(originalRoles)) {
      payload.roles = JSON.stringify(currentRoles)
    }

    if (Object.keys(payload).length === 0) {
      userEditError.value = 'Không có thay đổi nào để lưu.'
      userEditSaving.value = false
      return
    }

    const result = await updateUserService(userEditForm.value.id, payload)
    if (!result || result.success === false) {
      throw new Error(result?.error || 'Không thể cập nhật người dùng')
    }

    const idx = users.value.findIndex(
      (u) => u && (u.id === userEditForm.value.id || u.email === userEditForm.value.email)
    )
    const normalizedRoles = currentRoles.map((role) => ({ role_name: role, is_active: true }))

    if (idx !== -1) {
      const existing = users.value[idx]
      users.value.splice(idx, 1, {
        ...existing,
        name: userEditForm.value.full_name || userEditForm.value.email,
        full_name: userEditForm.value.full_name || userEditForm.value.email,
        roles: normalizedRoles,
        isActive: !!userEditForm.value.enabled,
        __raw: {
          ...(existing.__raw || {}),
          full_name: userEditForm.value.full_name,
          first_name: userEditForm.value.first_name,
          last_name: userEditForm.value.last_name,
          mobile_no: userEditForm.value.mobile_no,
          phone: userEditForm.value.phone,
          language: userEditForm.value.language,
          time_zone: userEditForm.value.time_zone,
          enabled: userEditForm.value.enabled,
          roles: currentRoles,
        },
      })
    }

    userEditOriginal.value = JSON.parse(JSON.stringify(userEditForm.value))
    successMessage.value = 'Cập nhật người dùng thành công'
    closeEditUserModal()
    setTimeout(() => {
      if (successMessage.value === 'Cập nhật người dùng thành công') {
        successMessage.value = ''
      }
    }, 3000)
    await loadUsers()
  } catch (err) {
    console.error('Save user edits failed:', err)
    userEditError.value = err?.message || 'Không thể cập nhật người dùng'
  } finally {
    userEditSaving.value = false
  }
}

const deleteUser = async (user) => {
  if (!user || !user.id) return

  const confirmed = window.confirm(`Bạn chắc chắn muốn vô hiệu hóa người dùng "${user.name}"?`)
  if (!confirmed) return

  user.__deleting = true
  try {
    const payload = await deleteUserService(user.id)
    if (!payload || payload.success === false) {
      throw new Error(payload?.error || 'Không thể vô hiệu hóa người dùng')
    }

    user.isActive = false
    successMessage.value = `Đã vô hiệu hóa người dùng "${user.name}"`
    setTimeout(() => {
      if (successMessage.value && successMessage.value.includes(user.name)) {
        successMessage.value = ''
      }
    }, 3000)
    await loadUsers()
  } catch (err) {
    console.error('Delete user failed:', err)
    window.frappe?.msgprint?.({
      title: 'Lỗi',
      message: err?.message || 'Không thể vô hiệu hóa người dùng',
      indicator: 'red',
    }) ?? notificationStore.notify(err?.message || 'Không thể vô hiệu hóa người dùng', 'error')
  } finally {
    user.__deleting = false
  }
}
const viewRoleUsers = async (role) => {
  resetRoleUsersState()

  const fallbackInfo = {
    id: role.id,
    roleName: role.name,
    roleCode: role.roleCode || '',
    description: role.description || '',
    userCount: role.userCount ?? 0,
    isActive: role.isActive ?? true,
  }

  selectedRoleInfo.value = fallbackInfo
  showRoleUsersModal.value = true
  roleUsersLoading.value = true

  try {
    const response = await roleService.getRoleDetails(role.id)
    if (!response) {
      throw new Error('Không nhận được phản hồi từ máy chủ')
    }

    if (response?.success === false) {
      throw new Error(response?.error || 'Không thể tải dữ liệu vai trò')
    }

    const payload = response?.data ?? response
    if (!payload) {
      throw new Error('Không thể phân tích dữ liệu vai trò')
    }

    if (payload?.success === false) {
      throw new Error(payload?.error || 'Không thể tải dữ liệu vai trò')
    }

    const roleData = payload?.data ?? payload
    if (!roleData) {
      throw new Error('Dữ liệu vai trò không hợp lệ')
    }

    const usersList = Array.isArray(roleData.users) ? roleData.users : []
    selectedRoleUsers.value = usersList

    const previousInfo = selectedRoleInfo.value ?? fallbackInfo
    const rawIsActive = roleData.is_active
    const computedIsActive =
      typeof rawIsActive === 'boolean'
        ? rawIsActive
        : rawIsActive == null
        ? !!(previousInfo?.isActive ?? fallbackInfo.isActive)
        : !!rawIsActive

    selectedRoleInfo.value = {
      id: roleData.id || fallbackInfo.id,
      roleName: roleData.role_name || roleData.name || fallbackInfo.roleName,
      roleCode: roleData.role_code || fallbackInfo.roleCode,
      description: roleData.description ?? fallbackInfo.description,
      userCount: roleData.user_count ?? usersList.length ?? fallbackInfo.userCount,
      isActive: computedIsActive,
      lastModified: roleData.modified || null,
      createdAt: roleData.creation || null,
    }
  } catch (err) {
    roleUsersError.value = err?.message || 'Không thể tải danh sách người dùng'
  } finally {
    roleUsersLoading.value = false
  }
}

const getDocumentPermission = (document, roleName, permissionType) => {
  const docPermissions = documentPermissions.value[document.name]
  if (!docPermissions || !docPermissions[roleName]) {
    return false
  }
  // For simplified UI, we only show one checkbox per role
  // This represents general access permission
  return docPermissions[roleName][`can_${permissionType}`] || false
}

// Audit logs methods
const exportAuditLogs = () => {}

// Watch for tab changes to load data
// DocumentsTab manages its own loading when it mounts/activates

onMounted(async () => {
  await Promise.allSettled([refreshRoles(), refreshStats()])
  await Promise.allSettled([loadAvailableRoles(), loadUsers()])
})

// Database Tab Methods
const refreshDatabase = () => {
  // In a real app, this would fetch the latest database tables from the API
  notificationStore.notify('Đã làm mới dữ liệu database', 'success')
}

const toggleTableStatus = (table) => {
  if (!table) return
  table.isActive = !table.isActive
  notificationStore.notify(`Đã ${table.isActive ? 'kích hoạt' : 'vô hiệu hóa'} bảng ${table.name}`, 'success')
}

const toggleTablePermission = (table, permission, action) => {
  if (!table || !permission || !action) return

  // Toggle the specific action (read, write, delete)
  if (action === 'read') permission.read = !permission.read
  if (action === 'write') permission.write = !permission.write
  if (action === 'delete') permission.delete = !permission.delete

  notificationStore.notify(`Đã cập nhật quyền ${action} cho ${permission.name} trên bảng ${table.name}`, 'success')
}

const editTable = (table) => {
  notificationStore.notify(`Chức năng chỉnh sửa bảng ${table.name} đang được phát triển`, 'info')
}

const viewTableData = (table) => {
  notificationStore.notify(`Chức năng xem dữ liệu bảng ${table.name} đang được phát triển`, 'info')
}
</script>

<style scoped>
.permission-table-container {
  position: relative;
  overflow: auto;
}

.permission-header-cap {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  height: 48px;
  margin-bottom: -48px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  z-index: 25;
  pointer-events: none;
}

.permission-table {
  width: max-content;
  min-width: 100%;
  border-collapse: collapse;
}

.permission-table thead th {
  position: sticky;
  top: 0;
  z-index: 30;
  background-color: transparent;
  font-weight: 600;
  text-transform: uppercase;
}

.permission-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
}

.permission-table tbody tr:last-child {
  border-bottom: none;
}

.sticky-cell {
  position: sticky;
  left: 0;
  z-index: 20;
  background-color: inherit;
}
</style>
