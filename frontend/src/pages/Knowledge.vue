<template>
  <div :class="$attrs.class">
    <div class="h-full flex flex-col bg-gray-50">
      <!-- Header -->
      <div class="bg-white border-b px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <BookOpenIcon class="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ $t('knowledge.pageTitle') }}</h1>
              <p class="text-sm text-gray-500">{{ $t('knowledge.pageSubtitle') }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <!-- Source Selection Buttons -->
            <div class="flex items-center space-x-2">
              <!-- Paste Text -->
              <button
                @click="selectSource('paste')"
                class="flex items-center space-x-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-indigo-700 transition-all shadow-sm hover:shadow-md"
              >
                <FileTextIcon class="w-5 h-5" />
                <span>{{ $t('knowledge.sourceSelection.sources.paste.title') }}</span>
              </button>

              <!-- Upload File/URL -->
              <button
                @click="selectSource('file')"
                class="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-cyan-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-cyan-700 transition-all shadow-sm hover:shadow-md"
              >
                <UploadCloudIcon class="w-5 h-5" />
                <span>{{ $t('knowledge.sourceSelection.sources.file.title') }}</span>
              </button>

              <!-- Google Drive -->
              <button
                @click="selectSource('gdrive')"
                class="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-2 rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all shadow-sm hover:shadow-md"
              >
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M7.71 3.5L1.15 15l3.58 6.5L11.29 9.5 7.71 3.5M9.73 15L6.15 21.5h13.43l3.58-6.5H9.73M11.29 9.5L14.87 3.5h7.13l3.58 6.5h-14.3z"
                  />
                </svg>
                <span>Google Drive</span>
              </button>

              <!-- OneDrive -->
              <button
                @click="selectSource('onedrive')"
                class="flex items-center space-x-2 bg-gradient-to-r from-sky-500 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-sky-600 hover:to-blue-700 transition-all shadow-sm hover:shadow-md"
              >
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M13.8 11.3c0-.5-.1-1-.3-1.5-.3-.8-.8-1.4-1.5-1.8 0 0-.1 0-.1-.1-.8-.4-1.7-.5-2.6-.3-1.1.3-2 1-2.5 2-.1.3-.2.5-.3.8 0 .1 0 .2-.1.3 0 .2 0 .4-.1.6 0 .1 0 .2 0 .3v.6c0 .1 0 .2.1.3.1.6.3 1.1.7 1.6.5.7 1.3 1.2 2.1 1.4.1 0 .2 0 .3.1h.8c.1 0 .2 0 .3-.1.8-.2 1.6-.7 2.1-1.4.4-.5.6-1 .7-1.6 0-.1.1-.2.1-.3v-.6c0-.1 0-.2 0-.3-.1-.3-.1-.4-.1-.6.1-.1.1-.2.1-.3v-.2z"
                  />
                  <path
                    d="M16.4 11.3c-.1-.8-.4-1.5-.8-2.1-.7-.9-1.6-1.6-2.7-1.9-.1 0-.2-.1-.3-.1.1.3.2.5.3.8.1.3.1.5.2.8.8.2 1.4.7 1.9 1.4.3.5.5 1.1.6 1.7 0 .2 0 .4.1.6v.6c0 .1 0 .2-.1.3-.1.5-.3 1-.6 1.4-.5.7-1.3 1.2-2.1 1.4-.1 0-.2.1-.3.1h-.8l-.3-.1c-.2-.1-.4-.1-.6-.2-.1-.1-.2-.1-.3-.2v1.5c.1 0 .2.1.3.1.1 0 .2.1.3.1h1.6c.1 0 .2 0 .3-.1.9-.2 1.8-.7 2.4-1.5.5-.6.8-1.3.9-2.1 0-.1 0-.2.1-.3v-.9c0-.1 0-.2-.1-.3 0-.2 0-.4-.1-.6 0-.1 0-.2 0-.3v-.1z"
                  />
                </svg>
                <span>OneDrive</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 flex overflow-hidden h-full">
        <!-- Left Sidebar - Folder Tree -->
        <div class="w-64 bg-white border-r overflow-y-auto h-full">
          <div class="p-4">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-bold text-gray-900">{{ $t('knowledge.folders') }}</h2>
              <button
                @click="createFolderModalOpen = true"
                class="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors shadow-sm hover:shadow-md"
                :title="$t('knowledge.createFolder')"
              >
                <FolderPlusIcon class="w-5 h-5" />
              </button>
            </div>

            <!-- All Documents (Root) -->
            <div
              @click="goToFolder(null)"
              :class="[
                'flex items-center space-x-2 px-3 py-2 rounded-lg cursor-pointer transition-colors mb-2',
                currentFolderId === null ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100',
              ]"
            >
              <FolderIcon class="w-5 h-5" />
              <span class="font-medium">{{ $t('knowledge.allDocuments') }}</span>
            </div>

            <!-- Folder Tree -->
            <div class="space-y-1">
              <FolderTreeNode
                v-for="folder in rootFolders"
                :key="folder.id"
                :folder="folder"
                :current-folder-id="currentFolderId"
                :all-folders="folders"
                @select-folder="goToFolder"
                @edit-folder="editFolder"
                @delete-folder="deleteFolder"
                @rename-folder="renameFolder"
              />
            </div>
          </div>
        </div>

        <!-- Right Content Area -->
        <div class="flex-1 flex flex-col bg-gray-50 overflow-hidden">
          <!-- Search and Filters -->
          <div class="bg-white border-b px-6 py-4">
            <div class="flex items-center justify-between">
              <!-- Search Bar -->
              <div class="relative flex-1 max-w-md">
                <SearchIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  v-model="searchQuery"
                  :placeholder="$t('knowledge.searchPlaceholder')"
                  class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <!-- View Mode Toggle -->
              <div class="flex items-center space-x-2">
                <button
                  @click="viewMode = 'grid'"
                  :class="[
                    'p-2 rounded',
                    viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600',
                  ]"
                >
                  <GridIcon class="w-5 h-5" />
                </button>
                <button
                  @click="viewMode = 'list'"
                  :class="[
                    'p-2 rounded',
                    viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600',
                  ]"
                >
                  <ListIcon class="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          <!-- Document List/Grid -->
          <div class="flex-1 overflow-y-auto p-6">
            <div v-if="loading" class="flex items-center justify-center h-full">
              <div class="text-center">
                <LoaderIcon class="w-12 h-12 animate-spin mx-auto text-gray-400" />
                <p class="text-gray-500 mt-4">{{ $t('common.loading') }}</p>
              </div>
            </div>

            <div v-else-if="filteredDocuments.length === 0" class="flex items-center justify-center h-full">
              <div class="text-center">
                <FileTextIcon class="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <p class="text-xl font-semibold text-gray-700 mb-2">{{ $t('knowledge.noDocuments') }}</p>
                <p class="text-gray-500 mb-6">{{ $t('knowledge.uploadFirstDocument') }}</p>
                <button
                  @click="uploadModalOpen = true"
                  class="inline-flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <UploadIcon class="w-5 h-5" />
                  <span>{{ $t('knowledge.uploadDocument') }}</span>
                </button>
              </div>
            </div>

            <!-- Grid View -->
            <div
              v-else-if="viewMode === 'grid'"
              class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
            >
              <div
                v-for="doc in paginatedDocuments"
                :key="doc.id"
                class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div class="flex flex-col space-y-2">
                  <div class="flex items-center justify-between mb-3">
                    <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                      <component :is="getFileIcon(doc.fileType)" class="w-8 h-8 text-gray-600" />
                    </div>
                    <div class="flex items-center space-x-1">
                      <button @click="viewDocument(doc)" class="text-gray-400 hover:text-blue-600">
                        <EyeIcon class="w-4 h-4" />
                      </button>
                      <button @click="downloadDocument(doc)" class="text-gray-400 hover:text-green-600">
                        <DownloadIcon class="w-4 h-4" />
                      </button>
                      <button @click="deleteDocument(doc)" class="text-gray-400 hover:text-red-600">
                        <TrashIcon class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <h3 class="font-medium text-gray-900 truncate">{{ doc.title }}</h3>
                  <p class="text-sm text-gray-500 truncate">{{ doc.description }}</p>
                  <div class="flex items-center justify-between">
                    <span class="px-2 py-1 text-xs rounded-full" :class="getCategoryClass(doc.category)">
                      {{ $t(`knowledge.documentList.categories.${doc.category}`) || doc.category }}
                    </span>
                    <span class="text-xs text-gray-400">{{ doc.size }}</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-xs text-gray-400">{{ formatDate(doc.uploadDate) }}</span>
                    <span class="flex items-center">
                      <component
                        :is="getStatusIcon(doc.status)"
                        :class="getStatusClass(doc.status)"
                        class="w-3 h-3 mr-1"
                      />
                      <span class="text-xs" :class="getStatusTextClass(doc.status)">
                        {{ $t(`knowledge.documentList.status.${doc.status}`) || doc.status }}
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- List View -->
            <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tài liệu
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Danh mục
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Kích thước
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trạng thái
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ngày tải lên
                    </th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Thao tác
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="doc in paginatedDocuments" :key="doc.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mr-3">
                          <component :is="getFileIcon(doc.fileType)" class="w-6 h-6 text-gray-600" />
                        </div>
                        <div>
                          <div class="text-sm font-medium text-gray-900">{{ doc.title }}</div>
                          <div class="text-sm text-gray-500 truncate max-w-xs">{{ doc.description }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="px-2 py-1 text-xs rounded-full" :class="getCategoryClass(doc.category)">
                        {{ $t(`knowledge.documentList.categories.${doc.category}`) || doc.category }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ doc.size }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="flex items-center">
                        <component
                          :is="getStatusIcon(doc.status)"
                          :class="getStatusClass(doc.status)"
                          class="w-4 h-4 mr-2"
                        />
                        <span class="text-xs" :class="getStatusTextClass(doc.status)">
                          {{ $t(`knowledge.documentList.status.${doc.status}`) || doc.status }}
                        </span>
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(doc.uploadDate) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div class="flex items-center justify-end space-x-2">
                        <button @click="viewDocument(doc)" class="text-gray-400 hover:text-blue-600">
                          <EyeIcon class="w-4 h-4" />
                        </button>
                        <button @click="downloadDocument(doc)" class="text-gray-400 hover:text-green-600">
                          <DownloadIcon class="w-4 h-4" />
                        </button>
                        <button @click="deleteDocument(doc)" class="text-gray-400 hover:text-red-600">
                          <TrashIcon class="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="bg-white border-t px-6 py-4">
            <div class="flex items-center justify-between">
              <div class="text-sm text-gray-700">
                Hiển thị {{ paginationInfo.start }}-{{ paginationInfo.end }} trong {{ paginationInfo.total }} kết quả
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="prevPage"
                  :disabled="currentPage === 1"
                  class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Trước
                </button>

                <div class="flex space-x-1">
                  <button
                    v-for="page in visiblePages"
                    :key="page"
                    @click="goToPage(page)"
                    :class="[
                      'px-3 py-2 text-sm font-medium rounded-md',
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50',
                    ]"
                  >
                    {{ page }}
                  </button>
                </div>

                <button
                  @click="nextPage"
                  :disabled="currentPage === totalPages"
                  class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Sau
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Paste Text Modal -->
      <div v-if="pasteModalOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b">
            <div class="flex items-center justify-between">
              <h3 class="text-xl font-bold text-gray-900">{{ $t('knowledge.pasteModal.title') }}</h3>
              <button @click="closePasteModal" class="text-gray-400 hover:text-gray-600">
                <XIcon class="w-6 h-6" />
              </button>
            </div>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ $t('knowledge.pasteModal.titleLabel') }} *
              </label>
              <input
                v-model="pasteContent.title"
                :placeholder="$t('knowledge.pasteModal.titlePlaceholder')"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ $t('knowledge.pasteModal.contentLabel') }} *
              </label>
              <textarea
                v-model="pasteContent.content"
                :placeholder="$t('knowledge.pasteModal.contentPlaceholder')"
                rows="12"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">{{ $t('knowledge.pasteModal.contentHint') }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ $t('knowledge.uploadSection.fileInfo.folder') }}
              </label>
              <select
                v-model="pasteContent.folderId"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">{{ $t('knowledge.uploadSection.fileInfo.selectFolder') }}</option>
                <option v-for="folder in availableFolders" :key="folder.id" :value="folder.id">
                  {{ folder.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ $t('knowledge.uploadSection.fileInfo.category') }} *
              </label>
              <select
                v-model="pasteContent.category"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">{{ $t('knowledge.uploadSection.fileInfo.selectCategory') }}</option>
                <option value="faq">{{ $t('knowledge.documentList.categories.faq') }}</option>
                <option value="guide">{{ $t('knowledge.documentList.categories.guide') }}</option>
                <option value="policy">{{ $t('knowledge.documentList.categories.policy') }}</option>
                <option value="technical">{{ $t('knowledge.documentList.categories.technical') }}</option>
                <option value="software">{{ $t('knowledge.documentList.categories.software') }}</option>
                <option value="hardware">{{ $t('knowledge.documentList.categories.hardware') }}</option>
                <option value="other">{{ $t('knowledge.documentList.categories.other') }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ $t('knowledge.uploadSection.fileInfo.tags') }}
              </label>
              <input
                v-model="pasteContent.tags"
                :placeholder="$t('knowledge.uploadSection.fileInfo.tagsPlaceholder')"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-gray-500 mt-1">{{ $t('knowledge.uploadSection.fileInfo.tagsHint') }}</p>
            </div>
          </div>

          <div class="p-6 border-t flex justify-end space-x-3">
            <button
              @click="closePasteModal"
              :disabled="uploading"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              @click="savePastedContent"
              :disabled="!pasteContent.title || !pasteContent.content || !pasteContent.category || uploading"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <LoaderIcon v-if="uploading" class="w-4 h-4 animate-spin" />
              <span>{{ uploading ? $t('common.loading') : $t('common.save') }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Google Drive Modal -->
      <div
        v-if="gdriveModalOpen"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-green-600" viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M7.71 3.5L1.15 15l3.58 6.5L11.29 9.5 7.71 3.5M9.73 15L6.15 21.5h13.43l3.58-6.5H9.73M11.29 9.5L14.87 3.5h7.13l3.58 6.5h-14.3z"
                    />
                  </svg>
                </div>
                <h3 class="text-xl font-bold text-gray-900">{{ $t('knowledge.gdrive.title') }}</h3>
              </div>
              <button @click="gdriveModalOpen = false" class="text-gray-400 hover:text-gray-600">
                <XIcon class="w-6 h-6" />
              </button>
            </div>
          </div>

          <div class="p-6">
            <div class="text-center py-8">
              <svg class="w-20 h-20 mx-auto text-green-500 mb-4" viewBox="0 0 24 24" fill="currentColor">
                <path
                  d="M7.71 3.5L1.15 15l3.58 6.5L11.29 9.5 7.71 3.5M9.73 15L6.15 21.5h13.43l3.58-6.5H9.73M11.29 9.5L14.87 3.5h7.13l3.58 6.5h-14.3z"
                />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ $t('knowledge.gdrive.connectTitle') }}</h3>
              <p class="text-gray-600 mb-6">{{ $t('knowledge.gdrive.connectDesc') }}</p>
              <button
                class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2 mx-auto"
              >
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M7.71 3.5L1.15 15l3.58 6.5L11.29 9.5 7.71 3.5M9.73 15L6.15 21.5h13.43l3.58-6.5H9.73M11.29 9.5L14.87 3.5h7.13l3.58 6.5h-14.3z"
                  />
                </svg>
                <span>{{ $t('knowledge.gdrive.connectButton') }}</span>
              </button>
            </div>

            <div class="mt-6 border-t pt-6">
              <h4 class="font-semibold text-gray-900 mb-3">{{ $t('knowledge.gdrive.howItWorks') }}</h4>
              <ul class="space-y-2 text-sm text-gray-600">
                <li class="flex items-start">
                  <CheckCircleIcon class="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span>{{ $t('knowledge.gdrive.step1') }}</span>
                </li>
                <li class="flex items-start">
                  <CheckCircleIcon class="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span>{{ $t('knowledge.gdrive.step2') }}</span>
                </li>
                <li class="flex items-start">
                  <CheckCircleIcon class="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span>{{ $t('knowledge.gdrive.step3') }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- OneDrive Modal -->
      <div
        v-if="onedriveModalOpen"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-sky-100 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-sky-600" viewBox="0 0 24 24" fill="currentColor">
                    <path
                      d="M13.8 11.3c0-.5-.1-1-.3-1.5-.3-.8-.8-1.4-1.5-1.8 0 0-.1 0-.1-.1-.8-.4-1.7-.5-2.6-.3-1.1.3-2 1-2.5 2-.1.3-.2.5-.3.8 0 .1 0 .2-.1.3 0 .2 0 .4-.1.6 0 .1 0 .2 0 .3v.6c0 .1 0 .2.1.3.1.6.3 1.1.7 1.6.5.7 1.3 1.2 2.1 1.4.1 0 .2 0 .3.1h.8c.1 0 .2 0 .3-.1.8-.2 1.6-.7 2.1-1.4.4-.5.6-1 .7-1.6 0-.1.1-.2.1-.3v-.6c0-.1 0-.2 0-.3-.1-.3-.1-.4-.1-.6.1-.1.1-.2.1-.3v-.2z"
                    />
                    <path
                      d="M16.4 11.3c-.1-.8-.4-1.5-.8-2.1-.7-.9-1.6-1.6-2.7-1.9-.1 0-.2-.1-.3-.1.1.3.2.5.3.8.1.3.1.5.2.8.8.2 1.4.7 1.9 1.4.3.5.5 1.1.6 1.7 0 .2 0 .4.1.6v.6c0 .1 0 .2-.1.3-.1.5-.3 1-.6 1.4-.5.7-1.3 1.2-2.1 1.4-.1 0-.2.1-.3.1h-.8l-.3-.1c-.2-.1-.4-.1-.6-.2-.1-.1-.2-.1-.3-.2v1.5c.1 0 .2.1.3.1.1 0 .2.1.3.1h1.6c.1 0 .2 0 .3-.1.9-.2 1.8-.7 2.4-1.5.5-.6.8-1.3.9-2.1 0-.1 0-.2.1-.3v-.9c0-.1 0-.2-.1-.3 0-.2 0-.4-.1-.6 0-.1 0-.2 0-.3v-.1z"
                    />
                  </svg>
                </div>
                <h3 class="text-xl font-bold text-gray-900">{{ $t('knowledge.onedrive.title') }}</h3>
              </div>
              <button @click="onedriveModalOpen = false" class="text-gray-400 hover:text-gray-600">
                <XIcon class="w-6 h-6" />
              </button>
            </div>
          </div>

          <div class="p-6">
            <div class="text-center py-8">
              <svg class="w-20 h-20 mx-auto text-sky-500 mb-4" viewBox="0 0 24 24" fill="currentColor">
                <path
                  d="M13.8 11.3c0-.5-.1-1-.3-1.5-.3-.8-.8-1.4-1.5-1.8 0 0-.1 0-.1-.1-.8-.4-1.7-.5-2.6-.3-1.1.3-2 1-2.5 2-.1.3-.2.5-.3.8 0 .1 0 .2-.1.3 0 .2 0 .4-.1.6 0 .1 0 .2 0 .3v.6c0 .1 0 .2.1.3.1.6.3 1.1.7 1.6.5.7 1.3 1.2 2.1 1.4.1 0 .2 0 .3.1h.8c.1 0 .2 0 .3-.1.8-.2 1.6-.7 2.1-1.4.4-.5.6-1 .7-1.6 0-.1.1-.2.1-.3v-.6c0-.1 0-.2 0-.3-.1-.3-.1-.4-.1-.6.1-.1.1-.2.1-.3v-.2z"
                />
                <path
                  d="M16.4 11.3c-.1-.8-.4-1.5-.8-2.1-.7-.9-1.6-1.6-2.7-1.9-.1 0-.2-.1-.3-.1.1.3.2.5.3.8.1.3.1.5.2.8.8.2 1.4.7 1.9 1.4.3.5.5 1.1.6 1.7 0 .2 0 .4.1.6v.6c0 .1 0 .2-.1.3-.1.5-.3 1-.6 1.4-.5.7-1.3 1.2-2.1 1.4-.1 0-.2.1-.3.1h-.8l-.3-.1c-.2-.1-.4-.1-.6-.2-.1-.1-.2-.1-.3-.2v1.5c.1 0 .2.1.3.1.1 0 .2.1.3.1h1.6c.1 0 .2 0 .3-.1.9-.2 1.8-.7 2.4-1.5.5-.6.8-1.3.9-2.1 0-.1 0-.2.1-.3v-.9c0-.1 0-.2-.1-.3 0-.2 0-.4-.1-.6 0-.1 0-.2 0-.3v-.1z"
                />
              </svg>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ $t('knowledge.onedrive.connectTitle') }}</h3>
              <p class="text-gray-600 mb-6">{{ $t('knowledge.onedrive.connectDesc') }}</p>
              <button
                class="bg-sky-600 text-white px-6 py-3 rounded-lg hover:bg-sky-700 transition-colors flex items-center space-x-2 mx-auto"
              >
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M13.8 11.3c0-.5-.1-1-.3-1.5-.3-.8-.8-1.4-1.5-1.8 0 0-.1 0-.1-.1-.8-.4-1.7-.5-2.6-.3-1.1.3-2 1-2.5 2-.1.3-.2.5-.3.8 0 .1 0 .2-.1.3 0 .2 0 .4-.1.6 0 .1 0 .2 0 .3v.6c0 .1 0 .2.1.3.1.6.3 1.1.7 1.6.5.7 1.3 1.2 2.1 1.4.1 0 .2 0 .3.1h.8c.1 0 .2 0 .3-.1.8-.2 1.6-.7 2.1-1.4.4-.5.6-1 .7-1.6 0-.1.1-.2.1-.3v-.6c0-.1 0-.2 0-.3-.1-.3-.1-.4-.1-.6.1-.1.1-.2.1-.3v-.2z"
                  />
                  <path
                    d="M16.4 11.3c-.1-.8-.4-1.5-.8-2.1-.7-.9-1.6-1.6-2.7-1.9-.1 0-.2-.1-.3-.1.1.3.2.5.3.8.1.3.1.5.2.8.8.2 1.4.7 1.9 1.4.3.5.5 1.1.6 1.7 0 .2 0 .4.1.6v.6c0 .1 0 .2-.1.3-.1.5-.3 1-.6 1.4-.5.7-1.3 1.2-2.1 1.4-.1 0-.2.1-.3.1h-.8l-.3-.1c-.2-.1-.4-.1-.6-.2-.1-.1-.2-.1-.3-.2v1.5c.1 0 .2.1.3.1.1 0 .2.1.3.1h1.6c.1 0 .2 0 .3-.1.9-.2 1.8-.7 2.4-1.5.5-.6.8-1.3.9-2.1 0-.1 0-.2.1-.3v-.9c0-.1 0-.2-.1-.3 0-.2 0-.4-.1-.6 0-.1 0-.2 0-.3v-.1z"
                  />
                </svg>
                <span>{{ $t('knowledge.onedrive.connectButton') }}</span>
              </button>
            </div>

            <div class="mt-6 border-t pt-6">
              <h4 class="font-semibold text-gray-900 mb-3">{{ $t('knowledge.onedrive.howItWorks') }}</h4>
              <ul class="space-y-2 text-sm text-gray-600">
                <li class="flex items-start">
                  <CheckCircleIcon class="w-5 h-5 text-sky-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span>{{ $t('knowledge.onedrive.step1') }}</span>
                </li>
                <li class="flex items-start">
                  <CheckCircleIcon class="w-5 h-5 text-sky-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span>{{ $t('knowledge.onedrive.step2') }}</span>
                </li>
                <li class="flex items-start">
                  <CheckCircleIcon class="w-5 h-5 text-sky-500 mr-2 flex-shrink-0 mt-0.5" />
                  <span>{{ $t('knowledge.onedrive.step3') }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Upload File/URL Modal -->
      <div
        v-if="uploadModalOpen"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      >
        <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b">
            <div class="flex items-center justify-between">
              <h3 class="text-xl font-bold text-gray-900">{{ $t('knowledge.uploadSection.title') }}</h3>
              <button @click="closeUploadModal" class="text-gray-400 hover:text-gray-600">
                <XIcon class="w-6 h-6" />
              </button>
            </div>
          </div>

          <div class="p-6">
            <!-- Tab Selector -->
            <div class="flex space-x-2 mb-6 bg-gray-100 rounded-lg p-1">
              <button
                @click="uploadMode = 'file'"
                :class="[
                  'flex-1 px-4 py-2 rounded-md font-medium transition-colors',
                  uploadMode === 'file' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900',
                ]"
              >
                <UploadIcon class="w-4 h-4 inline-block mr-2" />
                {{ $t('knowledge.uploadSection.uploadFile') }}
              </button>
              <button
                @click="uploadMode = 'url'"
                :class="[
                  'flex-1 px-4 py-2 rounded-md font-medium transition-colors',
                  uploadMode === 'url' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900',
                ]"
              >
                <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                  />
                </svg>
                {{ $t('knowledge.uploadSection.importUrl') }}
              </button>
            </div>

            <!-- File Upload Mode -->
            <div v-if="uploadMode === 'file'">
              <!-- Drop Zone -->
              <div
                @drop="handleDrop"
                @dragover.prevent
                @dragenter.prevent
                :class="[
                  'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
                  dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300',
                ]"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.docm,.dot,.dotx,.dotm,.odt,.ott,.sxw,.rtf,.wps,.txt,.jpg,.jpeg,.png,.gif,.webp,.mp4,.avi,.mov,.wmv,.mp3,.wav,.ogg,.ppt,.pptx"
                  @change="handleFileSelect"
                  class="hidden"
                />

                <UploadCloudIcon class="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <p class="text-gray-600 mb-2">{{ $t('knowledge.uploadSection.dropzone') }}</p>
                <button @click="$refs.fileInput.click()" class="text-blue-600 hover:text-blue-700 font-medium">
                  {{ $t('common.upload') }}
                </button>
                <p class="text-xs text-gray-500 mt-4">{{ $t('knowledge.uploadSection.supportedFormats') }}</p>
              </div>
            </div>

            <!-- URL Import Mode -->
            <div v-else-if="uploadMode === 'url'">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    {{ $t('knowledge.uploadSection.urlLabel') }} *
                  </label>
                  <input
                    v-model="urlInfo.url"
                    type="url"
                    :placeholder="$t('knowledge.uploadSection.urlPlaceholder')"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p class="text-xs text-gray-500 mt-1">{{ $t('knowledge.uploadSection.urlHint') }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    {{ $t('knowledge.uploadSection.urlDescription') }}
                  </label>
                  <textarea
                    v-model="urlInfo.description"
                    :placeholder="$t('knowledge.uploadSection.urlDescriptionPlaceholder')"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  ></textarea>
                  <p class="text-xs text-gray-500 mt-1">{{ $t('knowledge.uploadSection.urlDescriptionHint') }}</p>
                </div>

                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div class="flex">
                    <AlertCircleIcon class="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
                    <div class="text-sm text-blue-800">
                      <p class="font-medium mb-1">{{ $t('knowledge.uploadSection.urlInfo.title') }}</p>
                      <ul class="list-disc list-inside space-y-1 text-xs">
                        <li>{{ $t('knowledge.uploadSection.urlInfo.point1') }}</li>
                        <li>{{ $t('knowledge.uploadSection.urlInfo.point2') }}</li>
                        <li>{{ $t('knowledge.uploadSection.urlInfo.point3') }}</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- File Info Form -->
            <div v-if="selectedFile || (uploadMode === 'url' && urlInfo.url)" class="mt-6 space-y-4">
              <!-- File Preview -->
              <div v-if="selectedFile" class="bg-gray-50 rounded-lg p-4 flex items-center justify-between">
                <div class="flex items-center">
                  <component :is="getFileIcon(selectedFile.type)" class="w-8 h-8 text-gray-600 mr-3" />
                  <div>
                    <p class="font-medium text-gray-900">{{ selectedFile.name }}</p>
                    <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
                  </div>
                </div>
                <button @click="clearSelection" class="text-red-600 hover:text-red-700">
                  <XIcon class="w-5 h-5" />
                </button>
              </div>

              <!-- URL Preview -->
              <div
                v-else-if="uploadMode === 'url' && urlInfo.url"
                class="bg-gray-50 rounded-lg p-4 flex items-center justify-between"
              >
                <div class="flex items-center flex-1 min-w-0">
                  <svg
                    class="w-8 h-8 text-gray-600 mr-3 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                    />
                  </svg>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-gray-900 truncate">{{ urlInfo.url }}</p>
                    <p class="text-sm text-gray-500">{{ $t('knowledge.uploadSection.webUrl') }}</p>
                  </div>
                </div>
                <button @click="clearSelection" class="text-red-600 hover:text-red-700 ml-3">
                  <XIcon class="w-5 h-5" />
                </button>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('knowledge.uploadSection.fileInfo.title') }} *
                </label>
                <input
                  v-model="fileInfo.title"
                  :placeholder="$t('knowledge.uploadSection.fileInfo.titlePlaceholder')"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('knowledge.uploadSection.fileInfo.folder') }}
                </label>
                <select
                  v-model="fileInfo.folderId"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">{{ $t('knowledge.uploadSection.fileInfo.selectFolder') }}</option>
                  <option v-for="folder in availableFolders" :key="folder.id" :value="folder.id">
                    {{ folder.name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('knowledge.uploadSection.fileInfo.category') }} *
                </label>
                <select
                  v-model="fileInfo.category"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">{{ $t('knowledge.uploadSection.fileInfo.selectCategory') }}</option>
                  <option value="faq">{{ $t('knowledge.documentList.categories.faq') }}</option>
                  <option value="guide">{{ $t('knowledge.documentList.categories.guide') }}</option>
                  <option value="policy">{{ $t('knowledge.documentList.categories.policy') }}</option>
                  <option value="technical">{{ $t('knowledge.documentList.categories.technical') }}</option>
                  <option value="software">{{ $t('knowledge.documentList.categories.software') }}</option>
                  <option value="hardware">{{ $t('knowledge.documentList.categories.hardware') }}</option>
                  <option value="other">{{ $t('knowledge.documentList.categories.other') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('knowledge.uploadSection.fileInfo.description') }}
                </label>
                <textarea
                  v-model="fileInfo.description"
                  :placeholder="$t('knowledge.uploadSection.fileInfo.descriptionPlaceholder')"
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('knowledge.uploadSection.fileInfo.tags') }}
                </label>
                <input
                  v-model="fileInfo.tags"
                  :placeholder="$t('knowledge.uploadSection.fileInfo.tagsPlaceholder')"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p class="text-xs text-gray-500 mt-1">{{ $t('knowledge.uploadSection.fileInfo.tagsHint') }}</p>
              </div>
            </div>
          </div>

          <!-- Upload Progress Bar -->
          <div v-if="uploading && uploadProgress > 0" class="p-4 border-t">
            <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                class="bg-blue-600 h-3 transition-all duration-300 flex items-center justify-center text-xs text-white font-medium"
                :style="{ width: uploadProgress + '%' }"
              >
                {{ uploadProgress }}%
              </div>
            </div>
            <p class="text-sm text-gray-600 mt-2 text-center">
              {{ $t('knowledge.uploadSection.uploading') || 'Uploading large file, please wait...' }}
            </p>
          </div>
          <div class="p-6 border-t flex justify-end space-x-3">
            <button
              @click="closeUploadModal"
              :disabled="uploading"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              @click="uploadDocument"
              :disabled="isUploadDisabled || uploading"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <LoaderIcon v-if="uploading" class="w-4 h-4 animate-spin" />
              <span>
                {{
                  uploading
                    ? uploadProgress > 0
                      ? `${uploadProgress}%`
                      : $t('common.loading')
                    : uploadMode === 'url'
                    ? $t('knowledge.uploadSection.import')
                    : $t('common.upload')
                }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Create Folder Modal -->
      <div
        v-if="createFolderModalOpen"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
          <div class="p-6 border-b">
            <div class="flex items-center justify-between">
              <h3 class="text-xl font-bold text-gray-900">{{ $t('knowledge.createFolder') }}</h3>
              <button @click="createFolderModalOpen = false" class="text-gray-400 hover:text-gray-600">
                <XIcon class="w-6 h-6" />
              </button>
            </div>
          </div>

          <div class="p-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ $t('knowledge.folderInfo.name') }} *
              </label>
              <input
                v-model="folderInfo.name"
                :placeholder="$t('knowledge.folderInfo.namePlaceholder')"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ $t('knowledge.folderInfo.description') }}
              </label>
              <textarea
                v-model="folderInfo.description"
                :placeholder="$t('knowledge.folderInfo.descriptionPlaceholder')"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              ></textarea>
            </div>
          </div>

          <div class="p-6 border-t flex justify-end space-x-3">
            <button
              @click="createFolderModalOpen = false"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {{ $t('common.cancel') }}
            </button>
            <button
              @click="createFolder"
              :disabled="!folderInfo.name || creatingFolder"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <LoaderIcon v-if="creatingFolder" class="w-4 h-4 animate-spin" />
              <span>{{ creatingFolder ? $t('common.loading') : $t('common.create') }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Document Preview Modal -->
    <DocumentPreviewModal
      :visible="showPreviewModal"
      :url="previewUrl"
      :mime="previewMime"
      :title="previewTitle"
      @close="closePreview"
    />
    <Notification />
    <ConfirmDialog
      ref="confirmDialog"
      :title="confirmDialogState.title"
      :message="confirmDialogState.message"
      :confirm-text="confirmDialogState.confirmText"
      :cancel-text="confirmDialogState.cancelText"
      :type="confirmDialogState.type"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import FolderTreeNode from '../components/knowledge/FolderTreeNode.vue'
import DocumentPreviewModal from '@/components/permissions/modals/DocumentPreviewModal.vue'
import Notification from '@/components/common/Notification.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { useNotificationStore } from '@/stores/notifications'
import {
  Upload as UploadIcon,
  Search as SearchIcon,
  FileText as FileTextIcon,
  Film as FilmIcon,
  File as FileIcon,
  Image as ImageIcon,
  Music as MusicIcon,
  Eye as EyeIcon,
  Download as DownloadIcon,
  Trash as TrashIcon,
  X as XIcon,
  UploadCloud as UploadCloudIcon,
  Loader as LoaderIcon,
  CheckCircle as CheckCircleIcon,
  Clock as ClockIcon,
  AlertCircle as AlertCircleIcon,
  Folder as FolderIcon,
  FolderPlus as FolderPlusIcon,
  BookOpen as BookOpenIcon,
  Grid3x3 as GridIcon,
  List as ListIcon,
} from 'lucide-vue-next'

const notificationStore = useNotificationStore()

// State management
const documents = ref([])
const folders = ref([])
const loading = ref(false)
const searchQuery = ref('')
const uploadModalOpen = ref(false)
const pasteModalOpen = ref(false)
const gdriveModalOpen = ref(false)
const onedriveModalOpen = ref(false)
const createFolderModalOpen = ref(false)
const selectedFile = ref(null)
const dragOver = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const creatingFolder = ref(false)
const currentFolderId = ref(null)
const viewMode = ref('grid') // 'grid' or 'list'
const uploadMode = ref('file') // 'file' or 'url'

// Preview modal state
const showPreviewModal = ref(false)
const previewUrl = ref('')
const previewMime = ref('')
const previewTitle = ref('')

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(12)

const fileInfo = ref({
  title: '',
  category: '',
  description: '',
  tags: '',
  folderId: '',
})

const urlInfo = ref({
  url: '',
  description: '',
})

const pasteContent = ref({
  title: '',
  content: '',
  category: '',
  tags: '',
  folderId: '',
})

const folderInfo = ref({
  name: '',
  description: '',
})

const confirmDialog = ref(null)
const confirmDialogState = ref({
  title: 'Confirm',
  message: 'Are you sure?',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  type: 'info',
})

// Computed properties
const rootFolders = computed(() => {
  return folders.value.filter((f) => !f.parent_folder_id || f.parent_folder_id === '')
})

const availableFolders = computed(() => {
  return folders.value
})

const filteredDocuments = computed(() => {
  let filtered = documents.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((doc) => {
      return (
        doc.title.toLowerCase().includes(query) ||
        doc.description?.toLowerCase().includes(query) ||
        doc.tags?.toLowerCase().includes(query)
      )
    })
  }

  return filtered
})

// Pagination computed properties
const totalPages = computed(() => {
  return Math.ceil(filteredDocuments.value.length / itemsPerPage.value)
})

const paginatedDocuments = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredDocuments.value.slice(start, end)
})

const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value + 1
  const end = Math.min(currentPage.value * itemsPerPage.value, filteredDocuments.value.length)
  return { start, end, total: filteredDocuments.value.length }
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let startPage = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let endPage = Math.min(totalPages.value, startPage + maxVisible - 1)

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1)
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return pages
})

const isUploadDisabled = computed(() => {
  if (!fileInfo.value.title || !fileInfo.value.category) {
    return true
  }

  if (uploadMode.value === 'file') {
    return !selectedFile.value
  } else if (uploadMode.value === 'url') {
    return !urlInfo.value.url
  }

  return false
})

const getFileIcon = (type) => {
  if (!type) return FileIcon

  if (type.includes('pdf') || type.includes('doc')) return FileTextIcon
  if (type.includes('image') || type.includes('jpg') || type.includes('png')) return ImageIcon
  if (type.includes('video') || type.includes('mp4')) return FilmIcon
  if (type.includes('audio') || type.includes('mp3')) return MusicIcon

  return FileIcon
}

const getCategoryClass = (category) => {
  const classes = {
    faq: 'bg-blue-100 text-blue-800',
    guide: 'bg-green-100 text-green-800',
    policy: 'bg-yellow-100 text-yellow-800',
    technical: 'bg-purple-100 text-purple-800',
    software: 'bg-indigo-100 text-indigo-800',
    hardware: 'bg-red-100 text-red-800',
  }
  return classes[category] || 'bg-gray-100 text-gray-800'
}

const getStatusIcon = (status) => {
  const icons = {
    processed: CheckCircleIcon,
    processing: ClockIcon,
    error: AlertCircleIcon,
  }
  return icons[status] || ClockIcon
}

const getStatusClass = (status) => {
  const classes = {
    processed: 'text-green-500',
    processing: 'text-yellow-500',
    error: 'text-red-500',
    Processed: 'text-green-500',
    Processing: 'text-yellow-500',
    Error: 'text-red-500',
  }
  return classes[status] || 'text-gray-500'
}

const getStatusTextClass = (status) => {
  const classes = {
    processed: 'text-green-700 bg-green-100 px-2 py-1 rounded-full text-xs font-medium',
    processing: 'text-yellow-700 bg-yellow-100 px-2 py-1 rounded-full text-xs font-medium',
    error: 'text-red-700 bg-red-100 px-2 py-1 rounded-full text-xs font-medium',
    Processed: 'text-green-700 bg-green-100 px-2 py-1 rounded-full text-xs font-medium',
    Processing: 'text-yellow-700 bg-yellow-100 px-2 py-1 rounded-full text-xs font-medium',
    Error: 'text-red-700 bg-red-100 px-2 py-1 rounded-full text-xs font-medium',
  }
  return classes[status] || 'text-gray-700 bg-gray-100 px-2 py-1 rounded-full text-xs font-medium'
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('vi-VN')
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// Pagination methods
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

// Source selection methods
const selectSource = (source) => {
  if (source === 'paste') {
    pasteContent.value.folderId = currentFolderId.value || ''
    pasteModalOpen.value = true
  } else if (source === 'file') {
    fileInfo.value.folderId = currentFolderId.value || ''
    uploadModalOpen.value = true
    uploadMode.value = 'file'
  } else if (source === 'gdrive') {
    connectGoogleDrive()
  } else if (source === 'onedrive') {
    connectOneDrive()
  }
}

// Google Drive connection
const connectGoogleDrive = async () => {
  try {
    const response = await call('dbiz_ai_agent.api.cloud_storage.get_gdrive_auth_url')

    if (response.success && response.auth_url) {
      // Open OAuth window
      const width = 600
      const height = 700
      const left = (window.screen.width - width) / 2
      const top = (window.screen.height - height) / 2

      window.open(
        response.auth_url,
        'Google Drive Authorization',
        `width=${width},height=${height},left=${left},top=${top}`
      )

      // Listen for OAuth callback
      window.addEventListener('message', (event) => {
        if (event.data.type === 'gdrive_connected') {
          notificationStore.notify(t('knowledge.gdrive.connectSuccess'), 'success')
          // TODO: Load Google Drive files
        }
      })
    } else {
      notificationStore.notify(response.message || t('knowledge.gdrive.configError'), 'error')
    }
  } catch (error) {
    console.error('Google Drive connection error:', error)
    notificationStore.notify(t('knowledge.gdrive.connectError'), 'error')
  }
}

// OneDrive connection
const connectOneDrive = async () => {
  try {
    const response = await call('dbiz_ai_agent.api.cloud_storage.get_onedrive_auth_url')

    if (response.success && response.auth_url) {
      // Open OAuth window
      const width = 600
      const height = 700
      const left = (window.screen.width - width) / 2
      const top = (window.screen.height - height) / 2

      window.open(
        response.auth_url,
        'OneDrive Authorization',
        `width=${width},height=${height},left=${left},top=${top}`
      )

      // Listen for OAuth callback
      window.addEventListener('message', (event) => {
        if (event.data.type === 'onedrive_connected') {
          notificationStore.notify(t('knowledge.onedrive.connectSuccess'), 'success')
          // TODO: Load OneDrive files
        }
      })
    } else {
      notificationStore.notify(response.message || t('knowledge.onedrive.configError'), 'error')
    }
  } catch (error) {
    console.error('OneDrive connection error:', error)
    notificationStore.notify(t('knowledge.onedrive.connectError'), 'error')
  }
}

const closePasteModal = () => {
  pasteModalOpen.value = false
  pasteContent.value = {
    title: '',
    content: '',
    category: '',
    tags: '',
    folderId: '',
  }
}

const closeUploadModal = () => {
  uploadModalOpen.value = false
  selectedFile.value = null
  uploadMode.value = 'file'
  urlInfo.value = { url: '', description: '' }
  fileInfo.value = {
    title: '',
    category: '',
    description: '',
    tags: '',
    folderId: '',
  }
}

const clearSelection = () => {
  selectedFile.value = null
  urlInfo.value = { url: '' }
}

const savePastedContent = async () => {
  if (!pasteContent.value.title || !pasteContent.value.content || !pasteContent.value.category) {
    notificationStore.notify(t('knowledge.pasteModal.fillRequired'), 'warning')
    return
  }

  try {
    uploading.value = true

    // Create a text file from pasted content
    const blob = new Blob([pasteContent.value.content], { type: 'text/plain' })
    const file = new File([blob], `${pasteContent.value.title}.txt`, { type: 'text/plain' })

    // Create FormData
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', pasteContent.value.title)
    formData.append('category', pasteContent.value.category)
    formData.append('description', pasteContent.value.content.substring(0, 200))
    formData.append('tags', pasteContent.value.tags || '')
    formData.append('folder_id', pasteContent.value.folderId || '')

    // Upload using XMLHttpRequest for progress tracking
    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/method/dbiz_ai_agent.api.documents.upload_document', true)
    xhr.timeout = 600000 // 10 minutes timeout

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        uploadProgress.value = Math.round((e.loaded / e.total) * 100)
      }
    })

    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        try {
          const response = JSON.parse(xhr.responseText)
          if (response.message) {
            notificationStore.notify(t('knowledge.pasteModal.success'), 'success')
            closePasteModal()
            loadDocuments()
          }
        } catch (error) {
          console.error('Parse error:', error)
          notificationStore.notify(t('knowledge.pasteModal.error'), 'error')
        }
      } else {
        notificationStore.notify(t('knowledge.pasteModal.error') + ': ' + xhr.statusText, 'error')
      }
      uploading.value = false
      uploadProgress.value = 0
    })

    xhr.addEventListener('error', () => {
      notificationStore.notify(t('knowledge.pasteModal.error'), 'error')
      uploading.value = false
      uploadProgress.value = 0
    })

    xhr.addEventListener('timeout', () => {
      notificationStore.notify(t('knowledge.pasteModal.timeout'), 'error')
      uploading.value = false
      uploadProgress.value = 0
    })

    xhr.send(formData)
  } catch (error) {
    console.error('Paste error:', error)
    notificationStore.notify(t('knowledge.pasteModal.error') + ': ' + (error.message || 'Unknown error'), 'error')
    uploading.value = false
    uploadProgress.value = 0
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  dragOver.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

// Folder navigation methods
const goToFolder = (folderId) => {
  currentFolderId.value = folderId
  currentPage.value = 1
  loadDocuments()
}

// Folder management methods
const createFolder = async () => {
  const name = (folderInfo.value.name || '').trim()
  if (!name) return

  const duplicate = folders.value.find(
    (f) =>
      (f.name || '').trim().toLowerCase() === name.toLowerCase() &&
      (f.parent_folder_id || null) === (currentFolderId.value || null)
  )
  if (duplicate) {
    notificationStore.notify(`A folder named "${name}" already exists in this location.`, 'warning')
    return
  }

  creatingFolder.value = true
  try {
    const params = {
      name,
      description: (folderInfo.value.description || '').trim(),
    }
    if (currentFolderId.value) params.parent_folder_id = currentFolderId.value

    const response = await call('dbiz_ai_agent.api.documents.create_folder', params, { freeze: true })

    const payload = response?.message || response?.data || response
    if (payload) {
      folderInfo.value = { name: '', description: '' }
      createFolderModalOpen.value = false
      notificationStore.notify('Folder created successfully!', 'success')
      await loadFolders()
    }
  } catch (error) {
    console.error('Create folder error:', error)
    const serverMsg = error?.message || (error?.response && error.response.data) || String(error)
    notificationStore.notify('Error creating folder: ' + serverMsg, 'error')
  } finally {
    creatingFolder.value = false
  }
}

const editFolder = (folder) => {
  // Deprecated: Use inline editing via rename-folder event
}

const renameFolder = async ({ folder, newName }) => {
  if (!newName || !newName.trim()) {
    notificationStore.notify('Folder name cannot be empty', 'warning')
    return
  }
  console.log('Renaming folder:', folder, 'to new name:', newName)
  try {
    await call(
      'dbiz_ai_agent.api.documents.rename_folder',
      {
        folder_id: folder.id,
        new_name: newName.trim(),
      },
      { freeze: true }
    )

    await loadFolders()
  } catch (error) {
    console.error('Rename folder error:', error)
    notificationStore.notify('Error renaming folder: ' + (error.message || 'Unknown error'), 'error')
  }
}

const deleteFolder = async (folder) => {
  confirmDialogState.value = {
    title: t('knowledge.deleteFolder'),
    message: `Are you sure you want to delete folder "${folder.name}"?`,
    confirmText: t('common.delete'),
    cancelText: t('common.cancel'),
    type: 'danger',
  }

  const confirmed = await confirmDialog.value.show()
  if (!confirmed) return

  try {
    await call('dbiz_ai_agent.api.documents.delete_folder', { folder_id: folder.id }, { freeze: true })
    await loadFolders()
    if (currentFolderId.value === folder.id) {
      goToFolder(null)
    }
  } catch (error) {
    console.error('Delete folder error:', error)
    notificationStore.notify('Error deleting folder: ' + error.message, 'error')
  }
}

const uploadDocument = async () => {
  // Validation based on upload mode
  if (!fileInfo.value.title || !fileInfo.value.category) {
    notificationStore.notify(t('knowledge.uploadSection.fillRequired'), 'warning')
    return
  }

  if (uploadMode.value === 'file' && !selectedFile.value) {
    notificationStore.notify(t('knowledge.uploadSection.selectFile'), 'warning')
    return
  }

  if (uploadMode.value === 'url' && !urlInfo.value.url) {
    notificationStore.notify(t('knowledge.uploadSection.enterUrl'), 'warning')
    return
  }

  uploading.value = true
  uploadProgress.value = 0

  try {
    const formData = new FormData()

    // Add file or URL based on mode
    if (uploadMode.value === 'file') {
      formData.append('file', selectedFile.value)
      formData.append('file_name', selectedFile.value.name || 'document')
      formData.append('file_type', selectedFile.value.type || '')
    } else if (uploadMode.value === 'url') {
      formData.append('url', urlInfo.value.url)
      formData.append('file_name', fileInfo.value.title)
    }

    formData.append('title', fileInfo.value.title)
    formData.append('category', fileInfo.value.category)
    formData.append('description', fileInfo.value.description || '')
    formData.append('tags', fileInfo.value.tags || '')
    if (fileInfo.value.folderId || currentFolderId.value) {
      formData.append('folder_id', fileInfo.value.folderId || currentFolderId.value)
    }

    const csrfToken =
      document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || window.frappe?.csrf_token || ''

    // Use XMLHttpRequest for large files with progress tracking
    await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      // Progress event
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          uploadProgress.value = Math.round((e.loaded / e.total) * 100)
          console.log(`Upload progress: ${uploadProgress.value}%`)
        }
      })
      // Success event
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText)
            resolve(data)
          } catch (e) {
            reject(new Error('Failed to parse response'))
          }
        } else {
          reject(new Error(xhr.responseText || `Upload failed with status ${xhr.status}`))
        }
      })
      // Error events
      xhr.addEventListener('error', () => {
        reject(new Error('Network error occurred during upload'))
      })
      xhr.addEventListener('abort', () => {
        reject(new Error('Upload was aborted'))
      })

      xhr.addEventListener('timeout', () => {
        reject(new Error('Upload timeout - file too large or connection too slow'))
      })

      // Open connection with long timeout for large files (10 minutes)
      xhr.open('POST', '/api/method/dbiz_ai_agent.api.documents.upload_document')
      xhr.timeout = 600000 // 10 minutes timeout for large files
      // Set headers
      if (csrfToken) {
        xhr.setRequestHeader('X-Frappe-CSRF-Token', csrfToken)
      }
      xhr.withCredentials = true
      // Send
      xhr.send(formData)
    })
    selectedFile.value = null
    urlInfo.value = { url: '' }
    fileInfo.value = {
      title: '',
      category: '',
      description: '',
      tags: '',
      folderId: '',
    }
    uploadProgress.value = 0
    uploadModalOpen.value = false
    uploadMode.value = 'file'

    const successMsg =
      uploadMode.value === 'url'
        ? t('knowledge.uploadSection.urlImportSuccess')
        : t('knowledge.uploadSection.uploadSuccess')
    notificationStore.notify(successMsg, 'success')
    await loadDocuments()
  } catch (error) {
    console.error('Upload error:', error)
    uploadProgress.value = 0
    notificationStore.notify('Error uploading document: ' + (error.message || 'Unknown error'), 'error')
  } finally {
    uploading.value = false
  }
}

const viewDocument = (doc) => {
  const url = doc.fileUrl || doc.file_url || doc.file_attachment || doc.file || doc.download_url || doc.downloadUrl
  if (url) {
    previewUrl.value = url
    previewMime.value = doc.fileType || doc.file_type || doc.mime || ''
    previewTitle.value = doc.title || doc.name || ''
    showPreviewModal.value = true
  } else {
    console.warn('No file URL available for preview:', doc)
    notificationStore.notify(
      t('chatbotPermissions.documents.messages.previewMissing') || 'Không có URL để xem trước',
      'warning'
    )
  }
}

const closePreview = () => {
  showPreviewModal.value = false
  previewUrl.value = ''
  previewMime.value = ''
  previewTitle.value = ''
}

const downloadDocument = (doc) => {
  const url = doc.fileUrl || doc.file_url || doc.file_attachment || doc.file || doc.download_url || doc.downloadUrl
  if (url) {
    const link = window.document.createElement('a')
    link.href = url
    link.download = doc.title || doc.name || 'document'
    window.document.body.appendChild(link)
    link.click()
    window.document.body.removeChild(link)
  } else {
    console.warn('No file URL available for download:', doc)
    notificationStore.notify(
      t('chatbotPermissions.documents.messages.downloadMissing') || 'Không có URL để tải xuống',
      'warning'
    )
  }
}

const deleteDocument = async (doc) => {
  confirmDialogState.value = {
    title: t('knowledge.deleteDocument'),
    message: `Are you sure you want to delete "${doc.title}"?`,
    confirmText: t('common.delete'),
    cancelText: t('common.cancel'),
    type: 'danger',
  }

  const confirmed = await confirmDialog.value.show()
  if (!confirmed) return

  try {
    const response = await call(
      'dbiz_ai_agent.api.documents.delete_document',
      { document_id: doc.id },
      { freeze: true }
    )
    if (response && response.success === false) {
      notificationStore.notify('Error deleting document: ' + (response.error || 'Unknown error'), 'error')
      return
    }
    await loadDocuments()
  } catch (error) {
    console.error('Delete error:', error)
    notificationStore.notify('Error deleting document: ' + error.message, 'error')
  }
}

const loadDocuments = async () => {
  loading.value = true

  try {
    const response = await call(
      'dbiz_ai_agent.api.documents.get_documents',
      { folder_id: currentFolderId.value },
      { freeze: true }
    )
    const processedDocuments = (response?.message || response?.data || response || []).map((doc) => ({
      ...doc,
      category: (doc.category || '').toString().toLowerCase(),
      tags: typeof doc.tags === 'string' ? doc.tags : (doc.tags || '').toString(),
    }))
    documents.value = processedDocuments
  } catch (error) {
    console.error('Load documents error:', error)
  } finally {
    loading.value = false
  }
}

const loadFolders = async () => {
  try {
    const response = await call('dbiz_ai_agent.api.documents.get_all_folders', {}, { freeze: true })
    const allFolders = response?.message || response?.data || response || []
    folders.value = (Array.isArray(allFolders) ? allFolders : []).map((folder) => ({
      ...folder,
      type: 'folder',
    }))
  } catch (error) {
    console.error('Load folders error:', error)
  }
}

onMounted(() => {
  loadDocuments()
  loadFolders()
})
</script>
