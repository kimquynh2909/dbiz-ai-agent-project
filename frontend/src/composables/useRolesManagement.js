import { ref, computed, watch } from 'vue'
import roleService from '@/services/roleService'
import documentPermissionService from '@/services/documentPermissionService'
import { unwrapResponse } from '@/services/userService'

const getColorClass = (color = '') => {
  const normalized = (color || '').toLowerCase()
  const colorMap = {
    '#ef4444': 'red-500',
    '#f97316': 'orange-500',
    '#f59e0b': 'yellow-500',
    '#10b981': 'green-500',
    '#3b82f6': 'blue-500',
    '#6366f1': 'indigo-500',
    '#8b5cf6': 'purple-500',
    '#ec4899': 'pink-500',
    '#6b7280': 'gray-500',
  }
  return colorMap[normalized] || 'gray-500'
}

const mapApiRole = (role) => {
  if (!role) return null

  const roleName = role.role_name || role.name || role.id || ''
  const colorHex = role.color || '#6b7280'
  const iconChar = (role.icon || roleName.charAt(0) || '?').toUpperCase()

  return {
    id: role.id,
    name: roleName,
    roleCode: role.role_code || '',
    description: role.description || '',
    colorClass: `bg-${getColorClass(colorHex)}`,
    colorHex,
    userCount: role.user_count || 0,
    isActive: role.is_active !== undefined ? !!role.is_active : true,
    initial: iconChar,
    priority: typeof role.priority === 'number' ? role.priority : parseInt(role.priority, 10) || 1,
    icon: role.icon || iconChar,
    user_management: !!role.user_management,
    permissions: [
      { id: 'all-docs', name: 'Tất cả tài liệu', checked: !!role.user_management },
      { id: 'database-full', name: 'Database (Full)', checked: !!role.user_management },
      { id: 'api-access', name: 'API Access', checked: !!role.user_management },
      { id: 'user-management', name: 'User Management', checked: !!role.user_management },
    ],
    __raw: role,
  }
}

export const useRolesManagement = () => {
  const roles = ref([])
  const loading = ref(false)
  const error = ref(null)
  const successMessage = ref('')
  const roleSearchQuery = ref('')
  const roleStatusFilter = ref('all')
  const rolesPerPage = ref(6)
  const rolesCurrentPage = ref(1)
  const availableRoles = ref([])

  const filteredRoles = computed(() => {
    const query = roleSearchQuery.value.trim().toLowerCase()
    const status = roleStatusFilter.value

    return roles.value.filter((role) => {
      const matchesQuery =
        !query ||
        (role.name && role.name.toLowerCase().includes(query)) ||
        (role.description && role.description.toLowerCase().includes(query)) ||
        (role.roleCode && role.roleCode.toLowerCase().includes(query))

      const matchesStatus =
        status === 'all' || (status === 'active' && role.isActive) || (status === 'inactive' && !role.isActive)

      return matchesQuery && matchesStatus
    })
  })

  const rolesTotalPages = computed(() => {
    if (!filteredRoles.value.length) return 1
    return Math.max(1, Math.ceil(filteredRoles.value.length / rolesPerPage.value))
  })

  const pagedRoles = computed(() => {
    if (!filteredRoles.value.length) return []
    const start = (rolesCurrentPage.value - 1) * rolesPerPage.value
    return filteredRoles.value.slice(start, start + rolesPerPage.value)
  })

  const rolesDisplayRange = computed(() => {
    if (!filteredRoles.value.length) {
      return { start: 0, end: 0, total: 0 }
    }
    const start = (rolesCurrentPage.value - 1) * rolesPerPage.value + 1
    const end = Math.min(start + pagedRoles.value.length - 1, filteredRoles.value.length)
    return { start, end, total: filteredRoles.value.length }
  })

  const activeRolesCount = computed(() => {
    return roles.value.filter((r) => r.isActive).length
  })

  watch([roleSearchQuery, roleStatusFilter], () => {
    rolesCurrentPage.value = 1
  })

  watch(rolesPerPage, () => {
    rolesCurrentPage.value = 1
  })

  watch(filteredRoles, () => {
    if (rolesCurrentPage.value > rolesTotalPages.value) {
      rolesCurrentPage.value = rolesTotalPages.value
    }
  })

  const applyRolesData = (rolesData) => {
    if (!Array.isArray(rolesData)) {
      availableRoles.value = []
      roles.value = []
      return
    }

    availableRoles.value = rolesData
    roles.value = rolesData.map(mapApiRole).filter(Boolean)

    const totalPages = Math.max(1, Math.ceil(Math.max(roles.value.length, 1) / rolesPerPage.value))
    rolesCurrentPage.value = Math.min(Math.max(rolesCurrentPage.value, 1), totalPages)
  }

  const gotoRolesPage = (page) => {
    if (!page) page = 1
    if (page < 1) page = 1
    if (page > rolesTotalPages.value) page = rolesTotalPages.value
    rolesCurrentPage.value = page
  }

  const refreshRoles = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await roleService.getRoles()
      let rolesData = []
      if (response && response.success && Array.isArray(response.data)) {
        rolesData = response.data
      } else if (Array.isArray(response)) {
        rolesData = response
      }

      applyRolesData(rolesData)
    } catch (err) {
      console.error('Error refreshing roles:', err)
      error.value = err.message || 'Network error occurred while loading roles'
    } finally {
      loading.value = false
    }
  }

  const loadAvailableRoles = async () => {
    const response = await documentPermissionService.getRoles()
    const payload = unwrapResponse(response)
    if (!payload || !payload.data) {
      throw new Error('Invalid roles response from server')
    }
    availableRoles.value = payload.data
  }

  return {
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
  }
}
