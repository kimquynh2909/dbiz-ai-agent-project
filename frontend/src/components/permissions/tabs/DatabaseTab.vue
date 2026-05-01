<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-900">Phân quyền Database</h3>
      <div class="flex items-center space-x-3">
        <button @click="emit('refresh')" class="flex items-center px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg">
          <RotateCcw class="w-4 h-4 mr-1" />
          Refresh
        </button>
        <button @click="emit('open-create-permission')" class="flex items-center px-3 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg">
          <PlusIcon class="w-4 h-4 mr-1" />
          Thêm quyền DB
        </button>
      </div>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl relative min-w-0"
         style="max-width: 100%; height: calc(100vh - 550px); min-height: 400px; overflow-y: auto; overflow-x: hidden;">
      <div class="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="table in databaseTables"
        :key="table.id"
        class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center">
            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <DatabaseIcon class="w-5 h-5 text-blue-600" />
            </div>
            <div class="ml-3">
              <h4 class="font-semibold text-gray-900">{{ table.name }}</h4>
              <p class="text-sm text-gray-500">{{ table.records }} records</p>
            </div>
          </div>
          <div class="flex items-center">
            <button
              @click="emit('toggle-table-status', table)"
              :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors', table.isActive ? 'bg-green-600' : 'bg-gray-200']"
            >
              <span
                :class="[
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  table.isActive ? 'translate-x-6' : 'translate-x-1'
                ]"
              ></span>
            </button>
          </div>
        </div>

        <div class="space-y-3">
          <h5 class="text-xs font-medium text-gray-500 uppercase tracking-wide">QUYỀN TRUY CẬP</h5>
          <div class="space-y-2">
            <div
              v-for="permission in table.permissions"
              :key="permission.id"
              class="flex items-center justify-between"
            >
              <span class="text-sm text-gray-700">{{ permission.name }}</span>
              <div class="flex space-x-2">
                <button
                  @click="emit('toggle-table-permission', { table, permission, action: 'read' })"
                  :class="['px-2 py-1 text-xs rounded-full', permission.read ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600']"
                >
                  Read
                </button>
                <button
                  @click="emit('toggle-table-permission', { table, permission, action: 'write' })"
                  :class="['px-2 py-1 text-xs rounded-full', permission.write ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600']"
                >
                  Write
                </button>
                <button
                  @click="emit('toggle-table-permission', { table, permission, action: 'delete' })"
                  :class="['px-2 py-1 text-xs rounded-full', permission.delete ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600']"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex space-x-2 mt-4 pt-4 border-t border-gray-100">
          <button @click="emit('edit-table', table)" class="flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg">
            <EditIcon class="w-4 h-4 mr-1" />
            Chỉnh sửa
          </button>
          <button @click="emit('view-table-data', table)" class="flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg">
            <DatabaseIcon class="w-4 h-4 mr-1" />
            Xem dữ liệu
          </button>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RotateCcw, Plus as PlusIcon, Database as DatabaseIcon, Edit as EditIcon } from 'lucide-vue-next'

defineProps({
  databaseTables: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'refresh',
  'open-create-permission',
  'toggle-table-status',
  'toggle-table-permission',
  'edit-table',
  'view-table-data'
])
</script>
