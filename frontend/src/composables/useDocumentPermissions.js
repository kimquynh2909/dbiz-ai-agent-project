import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { unwrapResponse } from '@/services/userService'
import documentPermissionService from '@/services/documentPermissionService.js'

export function useDocumentPermissions() {
  const documents = ref([])
  const documentsLoading = ref(false)
  const documentsError = ref(null)
  const documentPermissions = ref({})
  const bulkSelection = ref(new Set())
  const documentDetails = ref({})
  const fileTypeOptions = ref([])
  const accessLevelOptions = ref([])
  const documentSearchDebounce = ref(null)
  const documentsRequestToken = ref(0)

  const DOCUMENTS_PAGE_LIMIT = 100
  const documentsPagination = ref({
    limit: DOCUMENTS_PAGE_LIMIT,
    offset: 0,
    total: 0,
    nextOffset: null,
  })

  const documentsPerPage = ref(DOCUMENTS_PAGE_LIMIT)
  const documentsCurrentPage = ref(1)

  const totalDocuments = computed(() => documentsPagination.value.total || 0)

  const selectedDocuments = computed(() => documents.value.filter((doc) => bulkSelection.value.has(doc.name)))

  const fileTypes = computed(() => fileTypeOptions.value || [])

  const accessLevels = computed(() => {
    const DEFAULT_ACCESS_LEVELS = ['Public', 'Internal']
    const options = new Set(DEFAULT_ACCESS_LEVELS)
    ;(accessLevelOptions.value || []).forEach((level) => {
      if (level) options.add(level)
    })
    return Array.from(options)
  })

  const documentsDisplayRange = computed(() => {
    const total = totalDocuments.value
    const limit = documentsPagination.value.limit || documentsPerPage.value || DOCUMENTS_PAGE_LIMIT

    if (!total) return { start: 0, end: 0 }

    const start = (documentsPagination.value.offset || 0) + 1
    const end = Math.min(start + (documents.value.length || 0) - 1, total)

    return {
      start: documents.value.length ? start : 0,
      end: documents.value.length ? end : 0,
    }
  })

  const documentsTotalPages = computed(() => {
    const perPage = documentsPagination.value.limit || documentsPerPage.value || DOCUMENTS_PAGE_LIMIT
    const total = totalDocuments.value || 0
    return Math.max(1, Math.ceil(total / perPage))
  })

  const loadDocumentPermissions = async (documentName, force = false) => {
    const hasPermissions = !!documentPermissions.value[documentName]
    const hasDetails = !!documentDetails.value[documentName]
    if (!force && hasPermissions && hasDetails) return

    try {
      const response = await documentPermissionService.getDocumentPermissions(documentName, { includeContent: force })
      const payload = unwrapResponse(response)
      if (payload && payload.data) {
        if (payload.data.permissions) documentPermissions.value[documentName] = payload.data.permissions
        if (payload.data.document) documentDetails.value[documentName] = payload.data.document
      }
    } catch (err) {
      console.error(`Error loading permissions for ${documentName}:`, err)
      if (force) throw err
    }
  }

  const loadPermissionsForCurrentDocuments = async () => {
    const docs = documents.value
    if (!docs || !docs.length) return
    const promises = docs.map((doc) => loadDocumentPermissions(doc.name))
    await Promise.all(promises)
  }

  const fetchDocuments = async ({ offset = 0, resetPermissions = true, params = {} } = {}) => {
    const token = ++documentsRequestToken.value
    documentsLoading.value = true
    documentsError.value = null

    try {
      const response = await documentPermissionService.getDocuments({
        limit: documentsPerPage.value,
        offset,
        ...params,
      })
      const payload = unwrapResponse(response)
      if (!payload || !Array.isArray(payload.data)) throw new Error('Invalid documents response from server')
      if (token !== documentsRequestToken.value) return

      documents.value = payload.data
      if (resetPermissions) {
        documentPermissions.value = {}
        documentDetails.value = {}
      }

      if (payload.filters) {
        fileTypeOptions.value = payload.filters.file_types || []
        accessLevelOptions.value = payload.filters.access_levels || []
      }

      const pagination = payload.pagination || {}
      const resolvedLimit = pagination.limit || documentsPerPage.value || DOCUMENTS_PAGE_LIMIT
      const resolvedOffset = pagination.offset != null ? pagination.offset : offset
      const resolvedTotal = typeof pagination.total === 'number' ? pagination.total : totalDocuments.value

      if (token !== documentsRequestToken.value) return

      documentsPagination.value = {
        limit: resolvedLimit,
        offset: resolvedOffset,
        total: resolvedTotal,
        nextOffset:
          typeof pagination.next_offset === 'number' ? pagination.next_offset : pagination.next_offset ?? null,
      }

      documentsPerPage.value = resolvedLimit
      documentsCurrentPage.value = Math.max(1, Math.floor(resolvedOffset / resolvedLimit) + 1)

      // prune bulkSelection to current page
      const currentPageNames = new Set(documents.value.map((doc) => doc.name))
      const newSelection = new Set()
      bulkSelection.value.forEach((name) => {
        if (currentPageNames.has(name)) newSelection.add(name)
      })
      bulkSelection.value = newSelection

      await loadPermissionsForCurrentDocuments()
    } catch (err) {
      console.error('Error fetching documents:', err)
      if (token === documentsRequestToken.value) {
        documentsError.value = err.message || 'Failed to fetch documents'
        documents.value = []
        documentsPagination.value = {
          limit: documentsPerPage.value || DOCUMENTS_PAGE_LIMIT,
          offset: 0,
          total: 0,
          nextOffset: null,
        }
        fileTypeOptions.value = []
        accessLevelOptions.value = []
        documentsCurrentPage.value = 1
        documentPermissions.value = {}
        documentDetails.value = {}
      }
    } finally {
      if (token === documentsRequestToken.value) documentsLoading.value = false
    }
  }

  const toggleDocumentSelection = (document, isSelected) => {
    const newSet = new Set(bulkSelection.value)
    if (isSelected) newSet.add(document.name)
    else newSet.delete(document.name)
    bulkSelection.value = newSet
  }

  const toggleSelectAllDocuments = (selectAll) => {
    if (!documents.value.length) {
      bulkSelection.value = new Set()
      return
    }
    bulkSelection.value = selectAll ? new Set(documents.value.map((doc) => doc.name)) : new Set()
  }

  const updateDocumentPermission = async (document, updates) => {
    try {
      const response = await documentPermissionService.updateDocumentPermission(document.name, updates)
      if (response && response.success) {
        if (!documentPermissions.value[document.name]) documentPermissions.value[document.name] = {}
        for (const [roleName, payload] of Object.entries(updates)) {
          let canRead = false
          if (typeof payload === 'boolean') canRead = payload
          else if (payload && typeof payload === 'object')
            canRead = !!(payload.can_read ?? payload.can_access ?? payload.access)
          else continue

          if (!documentPermissions.value[document.name][roleName])
            documentPermissions.value[document.name][roleName] = {}
          documentPermissions.value[document.name][roleName]['can_read'] = canRead
          documentPermissions.value[document.name][roleName]['can_write'] = canRead
          documentPermissions.value[document.name][roleName]['can_delete'] = canRead
        }
      } else {
        throw new Error(response?.error || 'Failed to update permission')
      }
    } catch (err) {
      console.error('Error updating document permission:', err)
      throw err
    }
  }

  const editDocumentPermissions = async (document) => {
    if (!document || !document.name) return
    try {
      await loadDocumentPermissions(document.name, true)
      const details = documentDetails.value[document.name] || document
      return {
        title: details.title || document.title || '',
        category: details.category || document.category || '',
        access_level: details.access_level || document.access_level || accessLevels.value[0] || 'Public',
        description: details.description || '',
        tags: details.tags || '',
        departments_allowed: details.departments_allowed || '',
        content: details.content || '',
      }
    } catch (err) {
      console.error('Failed to load document details:', err)
      throw err
    }
  }

  const saveDocumentMetadata = async (editingDocumentName, form) => {
    if (!editingDocumentName) throw new Error('No document specified')
    const payload = {}
    const fields = ['title', 'category', 'access_level', 'description', 'tags', 'departments_allowed', 'content']
    const existingDetails = documentDetails.value[editingDocumentName] || {}
    const currentListDoc = documents.value.find((doc) => doc.name === editingDocumentName) || {}

    const normalize = (value) => {
      if (value === null || value === undefined) return ''
      if (typeof value === 'string') return value
      return String(value)
    }

    fields.forEach((field) => {
      if (!Object.prototype.hasOwnProperty.call(form, field)) return
      const newValue = form[field] ?? ''
      const existingValue = existingDetails[field] ?? currentListDoc[field] ?? ''
      if (normalize(newValue) !== normalize(existingValue)) payload[field] = newValue
    })

    if (Object.keys(payload).length === 0) throw new Error('No changes to save')

    const response = await documentPermissionService.updateDocumentMetadata(editingDocumentName, payload)
    if (!response || response.success === false) throw new Error(response?.error || 'Cập nhật tài liệu thất bại')

    const updatedDoc = response?.data?.document || {}
    const previousDetails = documentDetails.value[editingDocumentName] || {}
    documentDetails.value[editingDocumentName] = {
      ...previousDetails,
      ...updatedDoc,
      content: updatedDoc.content ?? payload.content ?? previousDetails.content ?? '',
    }

    const index = documents.value.findIndex((doc) => doc.name === editingDocumentName)
    if (index !== -1) {
      const merged = {
        ...documents.value[index],
        title: updatedDoc.title ?? payload.title ?? documents.value[index].title,
        category: updatedDoc.category ?? payload.category ?? documents.value[index].category,
        access_level: updatedDoc.access_level ?? payload.access_level ?? documents.value[index].access_level,
        status: updatedDoc.status ?? documents.value[index].status,
        file_type: updatedDoc.file_type ?? documents.value[index].file_type,
      }
      documents.value.splice(index, 1, merged)
      return merged
    }

    return null
  }

  // cleanup
  onBeforeUnmount(() => {
    if (documentSearchDebounce.value) clearTimeout(documentSearchDebounce.value)
    documentSearchDebounce.value = null
  })

  return {
    // state
    documents,
    documentsLoading,
    documentsError,
    documentPermissions,
    bulkSelection,
    selectedDocuments,
    documentDetails,
    fileTypeOptions,
    accessLevelOptions,
    documentsPagination,
    documentsPerPage,
    documentsCurrentPage,
    documentsDisplayRange,
    documentsTotalPages,
    totalDocuments,
    fileTypes,
    accessLevels,

    // actions
    fetchDocuments,
    loadDocumentPermissions,
    loadPermissionsForCurrentDocuments,
    loadPermissionsForCurrentDocuments,
    toggleDocumentSelection,
    toggleSelectAllDocuments,
    updateDocumentPermission,
    editDocumentPermissions,
    saveDocumentMetadata,
  }
}
