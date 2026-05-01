<template>
  <div>
    <div
      @click="toggleExpand"
      :class="[
        'flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors group',
        isSelected ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100',
      ]"
    >
      <div class="flex items-center space-x-2 flex-1 min-w-0" @click.stop="selectFolder">
        <button v-if="hasChildren" @click.stop="toggleExpand" class="p-0.5 hover:bg-gray-200 rounded transition-colors">
          <ChevronRightIcon :class="['w-4 h-4 transition-transform', isExpanded ? 'transform rotate-90' : '']" />
        </button>
        <div v-else class="w-5"></div>
        <FolderIcon class="w-5 h-5" />

        <!-- Editing mode -->
        <div v-if="isEditing" class="flex-1">
          <input
            ref="editInput"
            v-model="editingName"
            @click.stop
            @blur="saveEdit"
            @keyup.enter="saveEdit"
            @keyup.esc="cancelEdit"
            :class="[
              'w-full px-2 py-1 rounded border-2 focus:outline-none',
              isSelected ? 'bg-white text-gray-900 border-blue-400' : 'bg-white text-gray-900 border-blue-500',
            ]"
          />
        </div>
        <!-- Display mode -->
        <span v-else class="font-medium truncate">{{ folder.name }}</span>
      </div>

      <div
        v-if="isSelected && !isEditing"
        class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <button @click.stop="startEdit" class="p-1 hover:bg-blue-700 rounded">
          <EditIcon class="w-3 h-3" />
        </button>
        <button @click.stop="$emit('delete-folder', folder)" class="p-1 hover:bg-blue-700 rounded">
          <TrashIcon class="w-3 h-3" />
        </button>
      </div>
    </div>

    <div v-if="isExpanded && hasChildren" class="ml-4 mt-1 space-y-1">
      <FolderTreeNode
        v-for="child in childFolders"
        :key="child.id"
        :folder="child"
        :current-folder-id="currentFolderId"
        :all-folders="allFolders"
        @select-folder="$emit('select-folder', $event)"
        @edit-folder="$emit('edit-folder', $event)"
        @delete-folder="$emit('delete-folder', $event)"
        @rename-folder="$emit('rename-folder', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import {
  Folder as FolderIcon,
  ChevronRight as ChevronRightIcon,
  Edit as EditIcon,
  Trash as TrashIcon,
} from 'lucide-vue-next'

const props = defineProps({
  folder: {
    type: Object,
    required: true,
  },
  currentFolderId: {
    type: String,
    default: null,
  },
  allFolders: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['select-folder', 'edit-folder', 'delete-folder', 'rename-folder'])

const isExpanded = ref(false)
const isEditing = ref(false)
const editingName = ref('')
const editInput = ref(null)

const isSelected = computed(() => {
  return props.currentFolderId === props.folder.id
})

const childFolders = computed(() => {
  return props.allFolders.filter((f) => f.parent_folder_id === props.folder.id)
})

const hasChildren = computed(() => {
  return childFolders.value.length > 0
})

const toggleExpand = () => {
  if (hasChildren.value) {
    isExpanded.value = !isExpanded.value
  }
}

const selectFolder = () => {
  emit('select-folder', props.folder.id)
}

const startEdit = async () => {
  isEditing.value = true
  editingName.value = props.folder.name
  await nextTick()
  if (editInput.value) {
    editInput.value.focus()
    editInput.value.select()
  }
}

const saveEdit = () => {
  if (!isEditing.value) return // Prevent duplicate calls

  const newName = editingName.value.trim()
  if (newName && newName !== props.folder.name) {
    emit('rename-folder', { folder: props.folder, newName })
  }
  isEditing.value = false
}

const cancelEdit = () => {
  isEditing.value = false
  editingName.value = ''
}
</script>
