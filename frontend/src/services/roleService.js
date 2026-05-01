const API_BASE_METHOD = 'dbiz_ai_agent.api.roles'


import { call, createResource } from 'frappe-ui'

export const roleService = {
  // Get all roles
  async getRoles() {
    try {
      const response = await createResource({ url: `${API_BASE_METHOD}.get_roles`, params: {}, method: 'GET' }).fetch()
      return response
    } catch (error) {
      console.error('Error fetching roles:', error)
      throw error
    }
  },

  // Create a new role
  async createRole(roleData) {
    try {
      const response = await createResource({
        url: `${API_BASE_METHOD}.create_role`, params: {
          role_data: JSON.stringify(roleData)
        }, method: 'POST'
      }).fetch()
      return response
    } catch (error) {
      console.error('Error creating role:', error)
      throw error
    }
  },

  // Update an existing role
  async updateRole(roleId, roleData) {
    try {
      const response = await createResource({
        url: `${API_BASE_METHOD}.update_role`, params: {
          role_id: roleId,
          role_data: JSON.stringify(roleData)
        }, method: 'POST'
      }).fetch()
      return response
    } catch (error) {
      console.error('Error updating role:', error)
      throw error
    }
  },

  // Delete a role
  async deleteRole(roleId) {
    try {
      const response = await createResource({
        url: `${API_BASE_METHOD}.delete_role`, params: {
          role_id: roleId
        }, method: 'POST'
      }).fetch()
      return response
    } catch (error) {
      console.error('Error deleting role:', error)
      throw error
    }
  },

  // Get role details
  async getRoleDetails(roleId) {
    try {
      const response = await createResource({
        url: `${API_BASE_METHOD}.get_role_details`, params: {
          role_id: roleId
        }, method: 'GET'
      }).fetch()
      return response
    } catch (error) {
      console.error('Error fetching role details:', error)
      throw error
    }
  },

  // Toggle role status
  async toggleRoleStatus(roleId, isActive) {
    try {
      const response = await createResource({
        url: `${API_BASE_METHOD}.toggle_role_status`, params: {
          role_id: roleId,
          is_active: isActive ? 1 : 0
        }, method: 'POST'
      }).fetch()
      return response
    } catch (error) {
      console.error('Error toggling role status:', error)
      throw error
    }
  },

  // Get role statistics
  async getRoleStatistics() {
    try {
      const response = await createResource({ url: `${API_BASE_METHOD}.get_role_statistics`, params: {}, method: 'GET' }).fetch()
      return response
    } catch (error) {
      console.error('Error fetching role statistics:', error)
      throw error
    }
  }
}

export default roleService
