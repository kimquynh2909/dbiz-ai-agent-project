<template>
  <div class="space-y-4">
    <PermissionHeader
      title="Quản lý Users"
      :icon="UsersIcon"
      card-class="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-100"
      icon-wrapper-class="bg-gradient-to-br from-blue-500 to-cyan-500"
      color="blue"
    >
      <template #meta>
        <span class="font-medium text-blue-600">{{ usersTotal }} users</span>
        <span class="text-gray-400">•</span>
        <span>{{ filteredUsers.length }} đang hiển thị</span>
      </template>

      <template #actions>
        <button
          @click="refreshUsers"
          class="flex items-center px-4 py-2.5 text-sm font-medium text-blue-600 bg-white hover:bg-blue-50 border border-blue-200 rounded-lg transition-colors shadow-sm"
        >
          <RotateCcw class="w-4 h-4 mr-2" />
          Refresh
        </button>
        <button
          @click="openCreateUserModal"
          class="flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all shadow-sm text-white bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
        >
          <PlusIcon class="w-4 h-4 mr-2" />
          <span>Thêm user</span>
        </button>
      </template>
    </PermissionHeader>

    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
      <div class="relative w-full md:w-72">
        <SearchIcon class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
        <input
          v-model="userSearchQuery"
          type="text"
          placeholder="Tìm kiếm user..."
          class="pl-9 pr-3 py-2 w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          @input="onSearchInput"
        />
      </div>

      <div class="flex items-center justify-end w-full md:w-auto gap-2 sm:gap-3">
        <div class="flex w-full sm:w-48 justify-end">
          <FilterDropdown
            class="w-full sm:w-auto"
            :model-value="userRoleFilter"
            :options="availableRolesForSelect"
            all-option-text="Tất cả roles"
            @update:modelValue="onRoleChange"
          />
        </div>
      </div>
    </div>

    <div
      class="bg-white border border-gray-200 rounded-xl relative min-w-0"
      style="max-width: 100%; height: calc(100vh - 550px); min-height: 400px; overflow-y: auto; overflow-x: hidden"
    >
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Người dùng</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vai trò</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phòng ban</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Lần đăng nhập cuối
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hành động</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="usersLoading" class="text-center">
              <td colspan="6" class="px-6 py-12">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p class="text-gray-500 mt-2">Đang tải...</p>
              </td>
            </tr>
            <tr v-else-if="!filteredUsers || filteredUsers.length === 0" class="text-center">
              <td colspan="6" class="px-6 py-12">
                <p class="text-gray-500">Không có user nào</p>
              </td>
            </tr>
            <tr v-else v-for="user in filteredUsers" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-gray-700">{{ user.id.charAt(0) }}</span>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ user.id }}</div>
                    <div class="text-sm text-gray-500">{{ user.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center justify-center gap-1 flex-nowrap">
                  <template v-if="user.ai_roles && user.ai_roles.length">
                    <span
                      v-for="(role, index) in user.ai_roles.slice(0, VISIBLE_ROLES_LIMIT)"
                      :key="(role.role_name || role) + '-' + index"
                      :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full whitespace-nowrap',
                        getRoleColor(role),
                      ]"
                    >
                      {{ typeof role === 'string' ? role : role.role_name || role }}
                    </span>
                    <span
                      v-if="user.ai_roles.length > VISIBLE_ROLES_LIMIT"
                      class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-600"
                    >
                      +{{ user.ai_roles.length - VISIBLE_ROLES_LIMIT }}
                    </span>
                  </template>
                  <span v-else class="text-xs text-gray-400">Không có role</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.department }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.last_login }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    user.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                  ]"
                >
                  {{ user.enabled ? 'Hoạt động' : 'Đã khóa' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button
                    @click="editUser(user)"
                    class="text-gray-400 hover:text-gray-600"
                    title="Chỉnh sửa người dùng"
                  >
                    <EditIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteUser(user)"
                    :disabled="!!user.__deleting"
                    class="text-gray-400 hover:text-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Vô hiệu hóa người dùng"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="flex items-center justify-between mt-3">
      <div class="text-sm text-gray-600">
        Hiển thị {{ usersRangeStart }} - {{ usersRangeEnd }} trên {{ usersTotal }}
      </div>
      <div class="flex items-center space-x-4">
        <div class="mt-2">
          <FilterDropdown :model-value="pageSize" :options="perPageOptions" @update:modelValue="onPerPageChange" />
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="gotoPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Trước
          </button>
          <span class="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-lg">
            {{ currentPage }} / {{ totalPages }}
          </span>
          <button
            @click="gotoPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Sau
          </button>
        </div>
      </div>
    </div>
    <!-- Edit User Modal (self-managed) -->
    <EditUserModal
      :visible="showEditUserModal"
      :user-id="selectedUserId"
      @close="closeEditUserModal"
      @updated="onUserUpdated"
    />
    <!-- Create User Modal -->
    <CreateUserModal :visible="showCreateUserModal" @close="closeCreateUserModal" @created="onUserCreated" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Plus as PlusIcon,
  Edit as EditIcon,
  Trash2 as TrashIcon,
  Search as SearchIcon,
  RotateCcw,
  Users as UsersIcon,
} from 'lucide-vue-next'
import FilterDropdown from '@/components/permissions/common/FilterDropdown.vue'
import PermissionHeader from '@/components/permissions/common/PermissionHeader.vue'
import EditUserModal from '@/components/permissions/modals/EditUserModal.vue'
import CreateUserModal from '@/components/permissions/modals/CreateUserModal.vue'
import {
  getUsers as fetchUsers,
  updateUser as updateUserService,
  deleteUser as deleteUserService,
  createUser as createUserService,
} from '@/services/userService'
import roleService from '@/services/roleService'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

// Local state
const userSearchQuery = ref('')
const userRoleFilter = ref('')
const users = ref([])
const usersLoading = ref(false)
// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const usersTotal = ref(0)

const usersRangeStart = computed(() => {
  const total = Number(usersTotal.value) || (users.value || []).length
  if (total === 0) return 0
  return (currentPage.value - 1) * pageSize.value + 1
})

const usersRangeEnd = computed(() => {
  const total = Number(usersTotal.value) || (users.value || []).length
  return Math.min(total, currentPage.value * pageSize.value)
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil((Number(usersTotal.value) || (users.value || []).length) / pageSize.value))
)
const availableRoles = ref([])

// Modal state
const showEditUserModal = ref(false)
const showCreateUserModal = ref(false)
const selectedUserId = ref('')

const VISIBLE_ROLES_LIMIT = 2

// Per-page options
// (keep a single perPageOptions in this file to avoid duplicate identifier errors)
const perPageOptions = computed(() => [10, 20, 50, 100])

const onPerPageChange = (val) => {
  pageSize.value = Number(val) || 20
  currentPage.value = 1
  void loadUsers({ page: 1, pageSize: pageSize.value })
}

const availableRolesForSelect = computed(() =>
  (availableRoles.value || []).map((r) => r.role_name || r.name).filter(Boolean)
)

const filteredUsers = computed(() => {
  const q = (userSearchQuery.value || '').toLowerCase()
  const role = userRoleFilter.value || ''
  return (users.value || []).filter((u) => {
    const idMatch = !q || (u.id && u.id.toLowerCase().includes(q)) || (u.email && u.email.toLowerCase().includes(q))
    const roleMatch =
      !role || (u.ai_roles || []).some((r) => (typeof r === 'string' ? r === role : (r.role_name || r.name) === role))
    return idMatch && roleMatch
  })
})

const loadAvailableRoles = async () => {
  try {
    const resp = await roleService.getRoles()
    // roleService may return an array directly or an object with .data or .message.
    let roles = []
    if (Array.isArray(resp)) roles = resp
    else if (resp && Array.isArray(resp.data)) roles = resp.data
    else if (resp && Array.isArray(resp.message)) roles = resp.message
    else if (resp && Array.isArray(resp.roles)) roles = resp.roles

    // Filter out falsy entries
    availableRoles.value = roles.filter(Boolean)
  } catch (e) {
    availableRoles.value = []
  }
}

const loadUsers = async (opts = {}) => {
  usersLoading.value = true
  try {
    const page = opts.page ?? currentPage.value
    const pSize = opts.pageSize ?? pageSize.value
    console.log('[UsersTab] Fetching users with params:', {
      page,
      pageSize: pSize,
      search: userSearchQuery.value,
      role: userRoleFilter.value,
    })
    const response = await fetchUsers({
      page,
      pageSize: pSize,
      search: userSearchQuery.value,
      role: userRoleFilter.value,
    })
    console.log('[UsersTab] Fetch response:', response)
    const { users: apiUsers, pagination } = response
    users.value = Array.isArray(apiUsers) ? apiUsers : []
    console.log('[UsersTab] Loaded users:', users.value.length, users.value)
    if (pagination) {
      usersTotal.value = pagination.total_count ?? (Array.isArray(apiUsers) ? apiUsers.length : 0)
      currentPage.value = pagination.page ?? page
      pageSize.value = pagination.page_size ?? pSize
    } else {
      usersTotal.value = Array.isArray(apiUsers) ? apiUsers.length : 0
    }
    console.log('[UsersTab] Updated state - total:', usersTotal.value, 'page:', currentPage.value)
  } catch (e) {
    console.error('[UsersTab] Load users error:', e)
    users.value = []
    usersTotal.value = 0
  } finally {
    usersLoading.value = false
  }
}

const onSearchInput = () => {
  currentPage.value = 1
  void loadUsers({ page: 1 })
}
const onRoleChange = (val) => {
  userRoleFilter.value = val || ''
  currentPage.value = 1
  void loadUsers({ page: 1 })
}

const refreshUsers = () => {
  void loadUsers({ page: currentPage.value })
}

const gotoPage = (page) => {
  if (!page || page < 1) page = 1
  if (page > totalPages.value) page = totalPages.value
  currentPage.value = page
  void loadUsers({ page })
}

const editUser = (user) => {
  if (!user || !user.id) return
  selectedUserId.value = user.id
  showEditUserModal.value = true
}

const closeEditUserModal = () => {
  showEditUserModal.value = false
}
const onUserUpdated = async () => {
  await loadUsers()
  closeEditUserModal()
}
const onUserCreated = async () => {
  await loadUsers()
  closeCreateUserModal()
}

const deleteUser = async (user) => {
  if (!user || !user.id) return
  const confirmed = window.confirm(
    `Bạn chắc chắn muốn xóa người dùng "${user.name || user.id}"? Hành động này không thể hoàn tác.`
  )
  if (!confirmed) return
  user.__deleting = true
  try {
    const payload = await deleteUserService(user.id)
    if (!payload || payload.success === false) throw new Error(payload?.error || 'Không thể xóa người dùng')
    await loadUsers()
  } catch (err) {
    window.frappe?.msgprint?.({
      title: 'Lỗi',
      message: err?.message || 'Không thể xóa người dùng',
      indicator: 'red',
    }) ?? notificationStore.notify(err?.message || 'Không thể xóa người dùng', 'error')
  } finally {
    user.__deleting = false
  }
}

onMounted(async () => {
  await Promise.allSettled([loadAvailableRoles(), loadUsers()])
})

// Create user modal logic
const createUserForm = ref({
  email: '',
  password: '',
  full_name: '',
  first_name: '',
  last_name: '',
  mobile_no: '',
  language: 'vi',
  time_zone: 'Asia/Ho_Chi_Minh',
  enabled: true,
  roles: [],
})
const createUserError = ref('')
const createUserSaving = ref(false)

const resetCreateUserForm = () => {
  createUserForm.value = {
    email: '',
    password: '',
    full_name: '',
    first_name: '',
    last_name: '',
    mobile_no: '',
    language: 'vi',
    time_zone: 'Asia/Ho_Chi_Minh',
    enabled: true,
    roles: [],
  }
}
const openCreateUserModal = () => {
  createUserError.value = ''
  resetCreateUserForm()
  showCreateUserModal.value = true
}
const closeCreateUserModal = () => {
  showCreateUserModal.value = false
  createUserSaving.value = false
  createUserError.value = ''
}
const updateCreateUserField = (field, value) => {
  createUserForm.value[field] = value
}
const toggleCreateUserRole = (roleName, isChecked) => {
  if (!createUserForm.value.roles) createUserForm.value.roles = []
  if (isChecked) {
    if (!createUserForm.value.roles.includes(roleName)) createUserForm.value.roles.push(roleName)
  } else {
    const i = createUserForm.value.roles.indexOf(roleName)
    if (i > -1) createUserForm.value.roles.splice(i, 1)
  }
}
const saveNewUser = async () => {
  createUserError.value = ''
  createUserSaving.value = true
  try {
    const payload = {
      email: createUserForm.value.email,
      full_name: createUserForm.value.full_name,
      first_name: createUserForm.value.first_name,
      last_name: createUserForm.value.last_name,
      password: createUserForm.value.password || '',
      roles: JSON.stringify(createUserForm.value.roles || []),
      enabled: createUserForm.value.enabled ? 1 : 0,
      mobile_no: createUserForm.value.mobile_no,
      language: createUserForm.value.language,
      time_zone: createUserForm.value.time_zone,
    }
    if (!payload.email || !payload.full_name) throw new Error('Email và họ tên là bắt buộc')
    const result = await createUserService(payload)
    if (!result || result.success === false) throw new Error(result?.error || 'Không thể tạo người dùng')
    await loadUsers()
    closeCreateUserModal()
  } catch (err) {
    createUserError.value = err?.message || 'Không thể tạo người dùng'
  } finally {
    createUserSaving.value = false
  }
}

// legacy function removed; creation handled internally

const getRoleColor = (role) => {
  const roleObj = typeof role === 'object' ? role : null
  const roleName = typeof role === 'string' ? role : roleObj?.role_name || roleObj?.role || roleObj?.name || ''
  const isActive = roleObj
    ? roleObj.is_active !== false && roleObj.enabled !== false && roleObj.status !== 'inactive'
    : true

  const colors = {
    Administrator: 'bg-red-100 text-red-800',
    Manager: 'bg-blue-100 text-blue-800',
    Employee: 'bg-green-100 text-green-800',
    Guest: 'bg-gray-100 text-gray-800',
  }
  const baseClass = colors[roleName] || 'bg-purple-100 text-purple-800'
  if (!isActive) {
    return 'bg-gray-200 text-gray-500'
  }
  return baseClass
}
</script>
