<template>
  <div class="space-y-3">
    <!-- Header Section -->
    <PermissionHeader
      :title="documentsHeaderConfig.title"
      :icon="FileTextIcon"
      :card-class="documentsHeaderConfig.cardClass"
      :icon-wrapper-class="documentsHeaderConfig.iconWrapperClass"
      :color="documentsHeaderConfig.color"
    >
      <template #meta>
        <span class="font-medium text-indigo-600">
          {{
            t('chatbotPermissions.documents.header.range', {
              start: displayRange.start,
              end: displayRange.end,
              total: totalDocuments,
            })
          }}
        </span>
        <span class="text-gray-400">•</span>
        <span>{{ t('chatbotPermissions.documents.header.roles', { count: availableRoles.length }) }}</span>
      </template>

      <template #actions>
        <button
          @click="refreshDocuments"
          class="flex items-center px-4 py-2.5 text-sm font-medium text-indigo-600 bg-white hover:bg-indigo-50 border border-indigo-200 rounded-lg transition-colors shadow-sm"
        >
          <RotateCcw class="w-4 h-4 mr-2" />
          {{ t('chatbotPermissions.documents.buttons.refresh') }}
        </button>
        <button
          @click="openBulkPermissionModal"
          :disabled="bulkSelectionSize === 0"
          class="flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all shadow-sm"
          :class="
            bulkSelectionSize === 0
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg'
          "
        >
          <PlusIcon class="w-4 h-4 mr-2" />
          <span>{{ t('chatbotPermissions.documents.buttons.bulkAssign', { count: bulkSelectionSize }) }}</span>
        </button>
      </template>
    </PermissionHeader>

    <!-- Filters Section -->
    <div class="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center gap-3">
        <div class="relative flex-1">
          <SearchIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            v-model="searchQuery"
            :placeholder="t('chatbotPermissions.documents.filters.searchPlaceholder')"
            class="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
        <div class="flex items-center space-x-2">
          <FilterDropdown
            v-model="fileTypeFilter"
            :options="fileTypes"
            :all-option-text="t('chatbotPermissions.documents.filters.fileTypeAll')"
          />
          <FilterDropdown
            v-model="accessLevelFilter"
            :options="accessLevelFilterOptions"
            :all-option-text="t('chatbotPermissions.documents.filters.accessLevelAll')"
          />
          <FilterDropdown
            v-model="roleFilter"
            :options="availableRoles"
            value-key="name"
            label-key="role_name"
            :all-option-text="t('chatbotPermissions.documents.filters.roleAll')"
          />
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex">
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">{{ t('errors.general') }}</h3>
          <div class="mt-2 text-sm text-red-700">{{ error }}</div>
        </div>
      </div>
    </div>

    <div
      v-if="!loading && !error"
      class="bg-white border border-gray-200 rounded-xl relative min-w-0"
      style="max-width: 100%; height: calc(100vh - 550px); min-height: 400px; overflow-y: auto; overflow-x: hidden"
    >
      <div class="block overflow-x-auto sm:overflow-visible">
        <table class="divide-y divide-gray-200 w-full min-w-[36rem]" style="border-collapse: collapse">
          <thead>
            <tr>
              <th
                class="sticky top-0 z-20 px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"
                style="width: 2.5rem"
              >
                <input
                  type="checkbox"
                  :checked="allDocumentsSelected"
                  @change="toggleSelectAll($event.target.checked)"
                  class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </th>
              <th
                class="sticky top-0 z-20 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50 whitespace-nowrap min-w-[12rem]"
              >
                {{ t('chatbotPermissions.documents.table.columns.document') }}
              </th>
              <th
                class="sticky top-0 z-20 px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50 hidden xl:table-cell"
                style="width: 5.5rem"
              >
                {{ t('chatbotPermissions.documents.table.columns.type') }}
              </th>
              <th
                class="sticky top-0 z-20 px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50 hidden xl:table-cell"
                style="width: 6.5rem"
              >
                {{ t('chatbotPermissions.documents.table.columns.accessLevel') }}
              </th>
              <th
                class="sticky top-0 z-20 px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"
                style="width: 6rem; min-width: 6rem; max-width: 6rem"
              >
                {{ t('chatbotPermissions.documents.table.columns.roles') }}
              </th>
              <th
                class="sticky top-0 z-20 px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"
                style="width: 7rem"
              >
                {{ t('chatbotPermissions.documents.table.columns.actions') }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="document in documents" :key="document.name" class="hover:bg-gray-50">
              <td class="px-2 py-3 text-center" style="width: 2.5rem">
                <input
                  type="checkbox"
                  :checked="bulkSelection.has(document.name)"
                  @change="toggleDocument(document, $event.target.checked)"
                  class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </td>
              <td class="px-4 py-3 min-w-[12rem]">
                <div class="flex items-center">
                  <div
                    class="w-10 h-10 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center mr-3 flex-shrink-0 shadow-sm"
                  >
                    <FileTextIcon class="w-5 h-5 text-indigo-600" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-sm font-semibold text-gray-900 truncate" :title="document.title || document.name">
                      {{ document.title || document.name }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-2 py-3 text-center hidden xl:table-cell" style="width: 5.5rem">
                <span
                  class="inline-flex px-3 py-1.5 text-xs font-semibold bg-gray-100 text-gray-700 rounded-lg whitespace-nowrap"
                >
                  {{ document.file_type || t('chatbotPermissions.documents.table.unknownType') }}
                </span>
              </td>
              <td class="px-2 py-3 text-center hidden xl:table-cell" style="width: 6.5rem">
                <span
                  :class="[
                    'inline-flex px-3 py-1.5 text-xs font-bold rounded-lg whitespace-nowrap shadow-sm',
                    getAccessLevelClass(document.access_level),
                  ]"
                >
                  {{ getAccessLevelLabel(document.access_level) }}
                </span>
              </td>
              <td class="px-2 py-3 text-center" style="width: 6rem; min-width: 6rem; max-width: 6rem">
                <span
                  :class="[
                    'inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-lg',
                    isPublicOrInternal(document.access_level)
                      ? 'bg-gray-50 text-gray-400 border border-gray-200'
                      : 'bg-purple-50 text-purple-700 border border-purple-200',
                  ]"
                >
                  {{ countRolesWithAccess(document) }} / {{ availableRoles.length }}
                </span>
              </td>
              <td class="px-2 py-3 text-center" style="width: 7rem">
                <div class="flex space-x-1 justify-center">
                  <button
                    @click.stop="previewFile(document)"
                    class="p-2 rounded-lg text-blue-500 hover:bg-blue-50 hover:text-blue-700 transition-all"
                    :title="t('chatbotPermissions.documents.table.actions.preview')"
                  >
                    <EyeIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click.stop="downloadFile(document)"
                    class="p-2 rounded-lg text-green-500 hover:bg-green-50 hover:text-green-700 transition-all"
                    :title="t('chatbotPermissions.documents.table.actions.download')"
                  >
                    <DownloadIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="openRolesModal(document)"
                    :disabled="isPublicOrInternal(document.access_level)"
                    :class="[
                      'p-2 rounded-lg transition-all',
                      isPublicOrInternal(document.access_level)
                        ? 'text-gray-300 cursor-not-allowed'
                        : 'text-purple-500 hover:bg-purple-50 hover:text-purple-700',
                    ]"
                    :title="t('chatbotPermissions.documents.table.actions.permissions')"
                  >
                    <UsersIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="editDocument(document)"
                    class="p-2 rounded-lg text-amber-500 hover:bg-amber-50 hover:text-amber-700 transition-all"
                    :title="t('chatbotPermissions.documents.table.actions.edit')"
                  >
                    <EditIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div v-if="!loading && !error" class="flex items-center mt-4">
    <div class="flex items-center space-x-2 ml-auto">
      <button
        @click="gotoPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ t('chatbotPermissions.documents.pagination.prev') }}
      </button>
      <span class="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-lg">{{ currentPage }} / {{ totalPages }}</span>
      <button
        @click="gotoPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ t('chatbotPermissions.documents.pagination.next') }}
      </button>
      <select
        :value="perPage"
        @change="changePerPage(Number($event.target.value))"
        class="px-3 pr-10 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option v-for="size in perPageOptions" :key="size" :value="size">
          {{ t('chatbotPermissions.documents.pagination.perPageOption', { count: size }) }}
        </option>
      </select>
    </div>
  </div>
  <div>
    <!-- Modals -->
    <BulkPermissionModal
      :visible="showBulkPermissionModal"
      :document-ids="Array.from(bulkSelection)"
      :documents="documents.filter((doc) => bulkSelection.has(doc.name))"
      @close="closeBulkPermissionModal"
      @updated="onBulkPermissionsUpdated"
    />

    <EditDocumentModal
      :visible="showEditDocumentModal"
      :document="selectedDocument"
      :document-id="selectedDocument ? selectedDocument.name : ''"
      @close="closeEditDocumentModal"
      @updated="onDocumentUpdated"
    />

    <DocumentPermissionModal
      :visible="showDocumentPermissionModal"
      :document="selectedDocument"
      :mime="previewMime"
      :url="previewUrl"
      :document-id="selectedDocument ? selectedDocument.name : ''"
      @close="closeDocumentPermissionModal"
      @updated="onDocumentPermissionsUpdated"
    />

    <DocumentPreviewModal
      :visible="showPreviewModal"
      :url="previewUrl"
      :mime="previewMime"
      :title="previewTitle"
      @close="closePreview"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  RotateCcw,
  Plus as PlusIcon,
  FileText as FileTextIcon,
  Users as UsersIcon,
  Edit as EditIcon,
  Eye as EyeIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
} from 'lucide-vue-next'
import FilterDropdown from '@/components/permissions/common/FilterDropdown.vue'
import PermissionHeader from '@/components/permissions/common/PermissionHeader.vue'
import BulkPermissionModal from '@/components/permissions/modals/BulkPermissionModal.vue'
import EditDocumentModal from '@/components/permissions/modals/EditDocumentModal.vue'
import DocumentPermissionModal from '@/components/permissions/modals/DocumentPermissionModal.vue'
import DocumentPreviewModal from '@/components/permissions/modals/DocumentPreviewModal.vue'
import documentPermissionService from '@/services/documentPermissionService'
import roleService from '@/services/roleService'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const { t, tm } = useI18n()

// State
const documents = ref([])
const availableRoles = ref([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const fileTypeFilter = ref('')
const accessLevelFilter = ref('')
const roleFilter = ref('')
const currentPage = ref(1)
const perPage = ref(10)
const totalDocuments = ref(0)
const bulkSelection = ref(new Set())

// Modal states
const showBulkPermissionModal = ref(false)
const showEditDocumentModal = ref(false)
const showDocumentPermissionModal = ref(false)
const selectedDocument = ref(null)
const showPreviewModal = ref(false)
const previewUrl = ref('')
const previewMime = ref('')
const previewTitle = ref('')
const previewFilename = ref('')

// Bulk permission modal state (managed inside modal)

// Edit document modal state

// Document permission modal state is managed inside the modal now

// Constants
const perPageOptions = [10, 25, 50, 100]
const fileTypes = ref(['PDF', 'DOCX', 'DOC', 'TXT', 'XLSX', 'XLS'])
const accessLevels = ref(['Public', 'Internal'])

const documentsTexts = computed(() => (tm ? tm('chatbotPermissions.documents') : null) || {})
const headerDefaults = {
  title: t('chatbotPermissions.documents.header.title'),
  cardClass: 'bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100',
  iconWrapperClass: 'bg-gradient-to-br from-indigo-500 to-purple-600',
  color: 'indigo',
}

const documentsHeaderConfig = computed(() => {
  const header = documentsTexts.value.header || {}
  return {
    title: header.title || headerDefaults.title,
    cardClass: header.cardClass || headerDefaults.cardClass,
    iconWrapperClass: header.iconWrapperClass || headerDefaults.iconWrapperClass,
    color: header.color || headerDefaults.color,
  }
})

const accessLevelDisplayMap = computed(() => documentsTexts.value.accessLevels || {})
const accessLevelClassMap = computed(() => documentsTexts.value.accessLevelClasses || {})
const defaultAccessLevelLabel = computed(() => documentsTexts.value.table?.defaultAccessLevel || 'Public')
const defaultAccessLevelClass = computed(
  () => accessLevelClassMap.value.default || 'bg-gray-100 text-gray-700 border border-gray-200'
)
const accessLevelFilterOptions = computed(() =>
  accessLevels.value.map((level) => ({
    value: level,
    label: accessLevelDisplayMap.value[level] || level,
  }))
)

// Computed
const totalPages = computed(() => Math.ceil(totalDocuments.value / perPage.value))

const displayRange = computed(() => {
  const start = (currentPage.value - 1) * perPage.value + 1
  const end = Math.min(currentPage.value * perPage.value, totalDocuments.value)
  return { start, end }
})

const bulkSelectionSize = computed(() => bulkSelection.value.size)

const allDocumentsSelected = computed(() => {
  return documents.value.length > 0 && documents.value.every((doc) => bulkSelection.value.has(doc.name))
})

// Methods
const loadDocuments = async () => {
  try {
    loading.value = true
    error.value = ''

    const params = {
      limit: perPage.value,
      offset: (currentPage.value - 1) * perPage.value,
    }

    if (searchQuery.value) params.q = searchQuery.value
    if (fileTypeFilter.value) params.file_type = fileTypeFilter.value
    if (accessLevelFilter.value) params.access_level = accessLevelFilter.value
    if (roleFilter.value) params.role = roleFilter.value

    const response = await documentPermissionService.getDocuments(params)

    console.log('Raw response:', response)
    console.log('Response type:', typeof response)
    console.log('Response keys:', response ? Object.keys(response) : 'null')

    // Xử lý nhiều cấu trúc response khác nhau
    let data = null

    if (response) {
      // Trường hợp 1: response.success = true và có data
      if (response.success && response.data) {
        data = response.data
      }
      // Trường hợp 2: response trực tiếp là data (không có wrapper success)
      else if (response.documents || response.total !== undefined) {
        data = response
      }
      // Trường hợp 3: response.data trực tiếp chứa documents
      else if (response.data && (response.data.documents || response.data.total !== undefined)) {
        data = response.data
      }
    }

    console.log('Parsed data:', data)

    if (data) {
      // Nếu data là array trực tiếp, gán vào documents
      if (Array.isArray(data)) {
        documents.value = data
        totalDocuments.value = response.pagination?.total || data.length
      }
      // Nếu data là object có thuộc tính documents
      else if (data.documents) {
        documents.value = data.documents
        totalDocuments.value = data.total || 0
      }
      // Trường hợp khác
      else {
        documents.value = []
        totalDocuments.value = 0
      }

      console.log('Documents loaded:', documents.value.length)
      console.log('Total documents:', totalDocuments.value)
      console.log('First document structure:', documents.value[0])

      // Load permissions cho từng document
      await loadPermissionsForDocuments()

      // Không ghi đè fileTypes và accessLevels vì đã khởi tạo cứng
    } else {
      throw new Error(response?.message || t('chatbotPermissions.documents.messages.loadFailed'))
    }
  } catch (err) {
    console.error('Error loading documents:', err)
    error.value = err.message || t('chatbotPermissions.documents.messages.genericError')
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    const response = await roleService.getRoles()

    console.log('Roles response:', response)

    // Xử lý nhiều cấu trúc response khác nhau
    if (response) {
      if (response.success && response.data) {
        availableRoles.value = response.data || []
      } else if (Array.isArray(response)) {
        availableRoles.value = response
      } else if (response.data && Array.isArray(response.data)) {
        availableRoles.value = response.data
      }
    }

    console.log('Roles loaded:', availableRoles.value.length)
    if (availableRoles.value.length > 0) {
      console.log('First role structure:', availableRoles.value[0])
      console.log('First role keys:', Object.keys(availableRoles.value[0]))
    }
  } catch (err) {
    console.error('Error loading roles:', err)
  }
}

const loadPermissionsForDocuments = async () => {
  try {
    console.log('Loading permissions for documents...')

    // Load permissions cho từng document song song
    const permissionPromises = documents.value.map(async (doc) => {
      try {
        const response = await documentPermissionService.getDocumentPermissions(doc.name)
        console.log(`Permissions for ${doc.name}:`, response)

        // Parse response để lấy permissions
        let permissions = {}
        if (response && response.success && response.data && response.data.permissions) {
          permissions = response.data.permissions
        } else if (response && response.permissions) {
          permissions = response.permissions
        } else if (response && typeof response === 'object' && !Array.isArray(response)) {
          permissions = response
        }

        // Gán permissions vào document (permissions là object, không phải array)
        doc.permissions = permissions
        console.log(`Assigned permissions to ${doc.name}:`, permissions)

        return { name: doc.name, permissions }
      } catch (err) {
        console.error(`Error loading permissions for ${doc.name}:`, err)
        doc.permissions = {}
        return { name: doc.name, permissions: {} }
      }
    })

    await Promise.all(permissionPromises)

    // Trigger reactivity update
    documents.value = [...documents.value]

    console.log('All permissions loaded')
  } catch (err) {
    console.error('Error loading permissions:', err)
  }
}

const refreshDocuments = () => {
  loadDocuments()
}

const toggleSelectAll = (checked) => {
  if (checked) {
    documents.value.forEach((doc) => bulkSelection.value.add(doc.name))
  } else {
    documents.value.forEach((doc) => bulkSelection.value.delete(doc.name))
  }
}

const toggleDocument = (document, checked) => {
  if (checked) {
    bulkSelection.value.add(document.name)
  } else {
    bulkSelection.value.delete(document.name)
  }
}

const gotoPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const changePerPage = (size) => {
  perPage.value = size
  currentPage.value = 1
  loadDocuments()
}

const countRolesWithAccess = (document) => {
  if (!document.permissions || typeof document.permissions !== 'object') {
    return 0
  }

  // permissions là object với key là role name
  // Đếm số role có ít nhất 1 quyền (can_read, can_write, hoặc can_delete)
  const count = Object.values(document.permissions).filter((p) => p.can_read || p.can_write || p.can_delete).length

  return count
}

const getAccessLevelLabel = (accessLevel) => {
  if (!accessLevel) return defaultAccessLevelLabel.value
  return accessLevelDisplayMap.value[accessLevel] || accessLevel
}

const getAccessLevelClass = (accessLevel) => {
  if (!accessLevel) return defaultAccessLevelClass.value
  return accessLevelClassMap.value[accessLevel] || defaultAccessLevelClass.value
}

const isPublicOrInternal = (accessLevel) => {
  // Chỉ Public không cần quản lý roles (hiển thị xám)
  return accessLevel === 'Public'
}

const openRolesModal = async (document) => {
  selectedDocument.value = { name: document.name, title: document.title || document.name }
  // Try to set preview data so the permission modal can show filename/mime and provide download/open behavior
  previewUrl.value =
    document.file_url ||
    document.fileUrl ||
    document.file_attachment ||
    document.file ||
    document.download_url ||
    document.downloadUrl ||
    ''
  previewMime.value = document.file_type || document.mime || ''
  previewFilename.value = document.title || document.name || ''
  showDocumentPermissionModal.value = true
}

// Permission changes are handled inside the modal

const onDocumentPermissionsUpdated = async () => {
  await loadDocuments()
}

const closeDocumentPermissionModal = () => {
  showDocumentPermissionModal.value = false
  previewMime.value = ''
  previewUrl.value = ''
  previewFilename.value = ''
}

const editDocument = (document) => {
  // Pass full document to modal to show file info in header
  selectedDocument.value = {
    name: document.name,
    title: document.title || document.name,
    file_type: document.file_type || document.mime || '',
    file_url: document.file_url || document.fileUrl || '',
    mime: document.file_type || document.mime || '',
  }
  showEditDocumentModal.value = true
  console.log('Edit document (open modal & fetch inside):', selectedDocument.value)
}

const previewFile = (document) => {
  // Try common fields that might contain a URL
  const url =
    document.file_url ||
    document.fileUrl ||
    document.file_attachment ||
    document.file ||
    document.download_url ||
    document.downloadUrl
  if (url) {
    previewUrl.value = url
    previewMime.value = document.file_type || document.mime || ''
    previewTitle.value = document.title || document.name || ''
    showPreviewModal.value = true
  } else {
    console.warn('No file URL available for preview:', document)
    notificationStore.notify(t('chatbotPermissions.documents.messages.previewMissing'), 'warning')
  }
}

const closePreview = () => {
  showPreviewModal.value = false
  previewUrl.value = ''
  previewMime.value = ''
  previewTitle.value = ''
}

const downloadFile = (document) => {
  const url =
    document.file_url ||
    document.fileUrl ||
    document.file_attachment ||
    document.file ||
    document.download_url ||
    document.downloadUrl
  if (url) {
    // Use window.document explicitly because the local parameter is named `document`
    const link = window.document.createElement('a')
    link.href = url
    // Try to provide a filename
    link.download = document.title || document.name || t('chatbotPermissions.documents.messages.downloadFilename')
    window.document.body.appendChild(link)
    link.click()
    link.remove()
  } else {
    console.warn('No file URL available for download:', document)
    notificationStore.notify(t('chatbotPermissions.documents.messages.downloadMissing'), 'warning')
  }
}

const openBulkPermissionModal = () => {
  if (bulkSelection.value.size === 0) return
  showBulkPermissionModal.value = true
  console.log('Open bulk permission modal for:', Array.from(bulkSelection.value))
}

// Modal handlers
const onBulkPermissionsUpdated = async () => {
  await loadDocuments()
  bulkSelection.value.clear()
  showBulkPermissionModal.value = false
}

const onDocumentUpdated = async (updatedDoc) => {
  // If needed, patch the current list without full reload
  try {
    if (updatedDoc && updatedDoc.name) {
      const idx = documents.value.findIndex((d) => d.name === updatedDoc.name)
      if (idx !== -1) {
        documents.value[idx] = {
          ...documents.value[idx],
          title: updatedDoc.title ?? documents.value[idx].title,
          category: updatedDoc.category ?? documents.value[idx].category,
          access_level: updatedDoc.access_level ?? documents.value[idx].access_level,
        }
      }
    }
  } catch (e) {
    // no-op
  }
  // Also refresh to ensure consistency
  await loadDocuments()
}

const closeBulkPermissionModal = () => {
  showBulkPermissionModal.value = false
}

const closeEditDocumentModal = () => {
  showEditDocumentModal.value = false
}

// Watchers
watch([searchQuery, fileTypeFilter, accessLevelFilter, roleFilter, currentPage], () => {
  console.log('Filters changed, reloading documents...')
  loadDocuments()
})

// Lifecycle
onMounted(() => {
  console.log('DocumentsTab mounted, loading data...')
  loadRoles()
  loadDocuments()
})
</script>
