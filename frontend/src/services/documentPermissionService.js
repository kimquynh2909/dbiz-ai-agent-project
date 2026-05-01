import { createResource } from 'frappe-ui'

export default {
  async getDocuments({
    limit = 100,
    offset = 0,
    q = undefined,
    file_type = undefined,
    access_level = undefined,
    role = undefined,
    fetch_all = undefined,
  } = {}) {
    try {
      const args = { limit, offset }
      if (q !== undefined) args.q = q
      if (file_type !== undefined) args.file_type = file_type
      if (access_level !== undefined) args.access_level = access_level
      if (role !== undefined) args.role = role
      if (fetch_all !== undefined) args.fetch_all = fetch_all

      const response = await createResource({
        url: 'dbiz_ai_agent.api.document_permissions.get_documents',
        params: args,
        method: 'GET',
      }).fetch()
      // frappe returns { message: ... }
      return response?.message ?? response
    } catch (error) {
      console.error('Error fetching documents via call:', error)
      throw error
    }
  },

  async getRoles() {
    try {
      const response = await createResource({
        url: 'dbiz_ai_agent.api.roles.get_roles',
        params: {},
        method: 'GET',
      }).fetch()
      return response?.message ?? response
    } catch (error) {
      console.error('Error fetching roles via call:', error)
      throw error
    }
  },

  async getDocumentPermissions(documentName, options = {}) {
    try {
      const args = {
        document_name: documentName,
        _t: Date.now(), // Cache buster
      }
      if (options.includeContent) {
        args.include_content = 1
      }
      const response = await createResource({
        url: 'dbiz_ai_agent.api.document_permissions.get_document_permissions',
        params: args,
        method: 'GET',
      }).fetch()
      return response?.message ?? response
    } catch (error) {
      console.error('Error fetching document permissions via call:', error)
      throw error
    }
  },

  async updateDocumentPermission(documentName, updates) {
    try {
      const response = await createResource({
        url: 'dbiz_ai_agent.api.document_permissions.update_document_permission',
        params: {
          document_name: documentName,
          updates: JSON.stringify(updates),
        },
        method: 'POST',
      }).fetch()
      return response?.message ?? response
    } catch (error) {
      console.error('Error updating document permission via call:', error)
      throw error
    }
  },

  async bulkUpdateDocumentPermissions(documentName, permissionsData) {
    try {
      const response = await createResource({
        url: 'dbiz_ai_agent.api.document_permissions.bulk_update_document_permissions',
        params: {
          document_name: documentName,
          permissions_data: JSON.stringify(permissionsData),
        },
        method: 'POST',
      }).fetch()
      return response?.message ?? response
    } catch (error) {
      console.error('Error bulk updating document permissions via call:', error)
      throw error
    }
  },

  async bulkUpdateDocumentsPermissions(documentNames, roleId, grant) {
    try {
      const response = await createResource({
        url: 'dbiz_ai_agent.api.document_permissions.bulk_update_documents_permissions',
        params: {
          document_names: JSON.stringify(documentNames),
          role_id: roleId,
          grant: grant ? 1 : 0,
        },
        method: 'POST',
      }).fetch()
      return response?.message ?? response
    } catch (error) {
      console.error('Error bulk updating permissions via call:', error)
      throw error
    }
  },

  async updateDocumentMetadata(documentName, updates) {
    try {
      const response = await createResource({
        url: 'dbiz_ai_agent.api.document_permissions.update_document_metadata',
        params: {
          document_name: documentName,
          updates: JSON.stringify(updates),
        },
        method: 'POST',
      }).fetch()
      return response?.message ?? response
    } catch (error) {
      console.error('Error updating document metadata via call:', error)
      throw error
    }
  },
}
