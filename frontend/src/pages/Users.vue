<template>
  <div class="space-y-6">
    <!-- Header with Stats -->
    <div class="bg-white rounded-xl shadow-sm p-6">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ $t('users.title') }}</h1>
          <p class="text-gray-600 mt-1">{{ $t('users.subtitle') }}</p>
        </div>
        <button
          @click="showAddUserModal = true"
          class="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <UserPlusIcon class="w-5 h-5" />
          <span>{{ $t('users.addUser') }}</span>
        </button>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          :title="$t('users.stats.total')"
          :value="stats.total_users || 0"
          subtitle=""
          :icon="UsersIcon"
          icon-color="blue"
          format="number"
        />
        <StatsCard
          :title="$t('users.stats.active')"
          :value="stats.active_users || 0"
          subtitle=""
          :icon="CheckCircleIcon"
          icon-color="green"
          format="number"
        />
        <StatsCard
          :title="$t('users.stats.inactive')"
          :value="stats.inactive_users || 0"
          subtitle=""
          :icon="MinusCircleIcon"
          icon-color="red"
          format="number"
        />
        <StatsCard
          :title="$t('users.stats.newToday')"
          :value="stats.users_created_today || 0"
          subtitle=""
          :icon="PlusCircleIcon"
          icon-color="purple"
          format="number"
        />
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-xl shadow-sm">
      <!-- Search and Filters -->
      <div class="p-6 border-b">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div class="flex items-center space-x-4">
            <div class="relative">
              <SearchIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                v-model="searchQuery"
                @input="debouncedSearch"
                :placeholder="$t('users.searchPlaceholder')"
                class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
              />
            </div>

            <select
              v-model="statusFilter"
              @change="loadUsers"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{{ $t('users.allStatus') }}</option>
              <option value="active">{{ $t('users.status.active') }}</option>
              <option value="inactive">{{ $t('users.status.inactive') }}</option>
            </select>

            <select
              v-model="roleFilter"
              @change="loadUsers"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{{ $t('users.allRoles') }}</option>
              <option v-for="role in availableRoles" :key="role.name" :value="role.name">
                {{ role.name }}
              </option>
            </select>
          </div>

          <div class="flex items-center space-x-2">
            <select
              v-model="pageSize"
              @change="changePageSize"
              class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="10">10 {{ $t('users.perPage') }}</option>
              <option value="20">20 {{ $t('users.perPage') }}</option>
              <option value="50">50 {{ $t('users.perPage') }}</option>
              <option value="100">100 / trang</option>
            </select>
            <button
              @click="loadUsers"
              class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <RefreshCwIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {{ $t('users.columns.user') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vai trò</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Lần cuối đăng nhập
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hành động</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading" class="text-center">
              <td colspan="6" class="px-6 py-12">
                <LoaderIcon class="w-8 h-8 animate-spin mx-auto text-gray-400" />
                <p class="text-gray-500 mt-2">Đang tải...</p>
              </td>
            </tr>
            <tr v-else-if="users.length === 0" class="text-center">
              <td colspan="6" class="px-6 py-12">
                <UsersIcon class="w-12 h-12 mx-auto text-gray-300" />
                <p class="text-gray-500 mt-2">Không có dữ liệu</p>
              </td>
            </tr>
            <tr v-else v-for="user in users" :key="user.name" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <div class="w-10 h-10 rounded-full flex items-center justify-center mr-3 overflow-hidden">
                    <img
                      v-if="user.user_image"
                      :src="user.user_image"
                      :alt="user.full_name"
                      class="w-full h-full object-cover"
                    />
                    <div
                      v-else
                      class="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold"
                    >
                      {{ getInitials(user.full_name || user.email) }}
                    </div>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ user.full_name || user.email }}</p>
                    <p class="text-xs text-gray-500">{{ user.first_name }} {{ user.last_name }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ user.email }}</td>
              <td class="px-6 py-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="role in user.roles.slice(0, 2)"
                    :key="role.role_name || role"
                    class="px-2 py-1 text-xs rounded-full"
                    :class="getRoleClass(role)"
                  >
                    {{ role.role_name || role }}
                  </span>
                  <span v-if="user.roles.length > 2" class="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
                    +{{ user.roles.length - 2 }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="flex items-center">
                  <component
                    :is="getStatusIcon(user.status)"
                    :class="getStatusClass(user.status)"
                    class="w-4 h-4 mr-1"
                  />
                  <span :class="getStatusTextClass(user.status)" class="text-sm">
                    {{ user.status === 'active' ? 'Hoạt động' : 'Không hoạt động' }}
                  </span>
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">
                {{ user.last_login ? formatDate(user.last_login) : 'Chưa đăng nhập' }}
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center space-x-2">
                  <button
                    @click="viewUserDetail(user)"
                    class="text-blue-600 hover:text-blue-700 p-1 rounded hover:bg-blue-50"
                    title="Xem chi tiết"
                  >
                    <EyeIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="editUser(user)"
                    class="text-green-600 hover:text-green-700 p-1 rounded hover:bg-green-50"
                    title="Chỉnh sửa"
                  >
                    <EditIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="resetPassword(user)"
                    class="text-orange-600 hover:text-orange-700 p-1 rounded hover:bg-orange-50"
                    title="Reset mật khẩu"
                  >
                    <KeyIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteUser(user)"
                    class="text-red-600 hover:text-red-700 p-1 rounded hover:bg-red-50"
                    title="Vô hiệu hóa"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.total_pages > 1" class="px-6 py-4 border-t bg-gray-50">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            Hiển thị {{ (pagination.page - 1) * pagination.page_size + 1 }} -
            {{ Math.min(pagination.page * pagination.page_size, pagination.total_count) }}
            trong tổng số {{ pagination.total_count }} người dùng
          </div>

          <div class="flex items-center space-x-2">
            <button
              @click="goToPage(1)"
              :disabled="!pagination.has_prev"
              class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronsLeftIcon class="w-4 h-4" />
            </button>

            <button
              @click="goToPage(pagination.page - 1)"
              :disabled="!pagination.has_prev"
              class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeftIcon class="w-4 h-4" />
            </button>

            <div class="flex items-center space-x-1">
              <button
                v-for="page in getVisiblePages()"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  'px-3 py-1 text-sm border rounded',
                  page === pagination.page
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'border-gray-300 hover:bg-gray-100',
                ]"
              >
                {{ page }}
              </button>
            </div>

            <button
              @click="goToPage(pagination.page + 1)"
              :disabled="!pagination.has_next"
              class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRightIcon class="w-4 h-4" />
            </button>

            <button
              @click="goToPage(pagination.total_pages)"
              :disabled="!pagination.has_next"
              class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronsRightIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit User Modal -->
    <div
      v-if="showAddUserModal || editingUser"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold text-gray-900">
              {{ editingUser ? 'Chỉnh sửa người dùng' : 'Thêm người dùng mới' }}
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
              <XIcon class="w-6 h-6" />
            </button>
          </div>
        </div>

        <form @submit.prevent="saveUser" class="p-6 space-y-6">
          <!-- Basic Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                v-model="userForm.email"
                type="email"
                required
                :disabled="!!editingUser"
                placeholder="user@example.com"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Họ và tên *</label>
              <input
                v-model="userForm.full_name"
                type="text"
                required
                placeholder="Nguyễn Văn A"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Họ</label>
              <input
                v-model="userForm.first_name"
                type="text"
                placeholder="Nguyễn"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tên</label>
              <input
                v-model="userForm.last_name"
                type="text"
                placeholder="Văn A"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div v-if="!editingUser">
            <label class="block text-sm font-medium text-gray-700 mb-1">Mật khẩu *</label>
            <input
              v-model="userForm.password"
              type="password"
              required
              placeholder="Tối thiểu 8 ký tự"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <!-- Contact Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Số điện thoại</label>
              <input
                v-model="userForm.mobile_no"
                type="tel"
                placeholder="0123456789"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Giới tính</label>
              <select
                v-model="userForm.gender"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Chọn giới tính</option>
                <option value="Male">Nam</option>
                <option value="Female">Nữ</option>
                <option value="Other">Khác</option>
              </select>
            </div>
          </div>

          <!-- Roles and Status -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Vai trò *</label>
              <div class="space-y-2 max-h-32 overflow-y-auto border border-gray-300 rounded-lg p-2">
                <label v-for="role in availableRoles" :key="role.name" class="flex items-center">
                  <input
                    type="checkbox"
                    :value="role.name"
                    v-model="userForm.roles"
                    class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span class="text-sm">{{ role.name }}</span>
                </label>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
              <select
                v-model="userForm.enabled"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option :value="1">Hoạt động</option>
                <option :value="0">Không hoạt động</option>
              </select>
            </div>
          </div>

          <div class="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Hủy
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <LoaderIcon v-if="saving" class="w-4 h-4 animate-spin" />
              <span>{{ saving ? 'Đang lưu...' : 'Lưu' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- User Detail Modal -->
    <div v-if="showUserDetail" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold text-gray-900">Chi tiết người dùng</h3>
            <button @click="showUserDetail = false" class="text-gray-400 hover:text-gray-600">
              <XIcon class="w-6 h-6" />
            </button>
          </div>
        </div>

        <div v-if="selectedUser" class="p-6 space-y-6">
          <!-- User Avatar and Basic Info -->
          <div class="flex items-center space-x-4">
            <div class="w-20 h-20 rounded-full overflow-hidden">
              <img
                v-if="selectedUser.user_image"
                :src="selectedUser.user_image"
                :alt="selectedUser.full_name"
                class="w-full h-full object-cover"
              />
              <div
                v-else
                class="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold"
              >
                {{ getInitials(selectedUser.full_name || selectedUser.email) }}
              </div>
            </div>
            <div>
              <h4 class="text-xl font-bold text-gray-900">{{ selectedUser.full_name || selectedUser.email }}</h4>
              <p class="text-gray-600">{{ selectedUser.email }}</p>
              <div class="flex items-center mt-2">
                <component
                  :is="getStatusIcon(selectedUser.status)"
                  :class="getStatusClass(selectedUser.status)"
                  class="w-4 h-4 mr-1"
                />
                <span :class="getStatusTextClass(selectedUser.status)" class="text-sm">
                  {{ selectedUser.status === 'active' ? 'Hoạt động' : 'Không hoạt động' }}
                </span>
              </div>
            </div>
          </div>

          <!-- User Information Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h5 class="font-semibold text-gray-900 mb-3">Thông tin cá nhân</h5>
              <div class="space-y-2 text-sm">
                <div>
                  <span class="font-medium">Họ:</span>
                  {{ selectedUser.first_name || 'Chưa có' }}
                </div>
                <div>
                  <span class="font-medium">Tên:</span>
                  {{ selectedUser.last_name || 'Chưa có' }}
                </div>
                <div>
                  <span class="font-medium">Số điện thoại:</span>
                  {{ selectedUser.mobile_no || 'Chưa có' }}
                </div>
                <div>
                  <span class="font-medium">Giới tính:</span>
                  {{ selectedUser.gender || 'Chưa có' }}
                </div>
                <div>
                  <span class="font-medium">Ngày sinh:</span>
                  {{ selectedUser.birth_date || 'Chưa có' }}
                </div>
                <div>
                  <span class="font-medium">Địa chỉ:</span>
                  {{ selectedUser.location || 'Chưa có' }}
                </div>
              </div>
            </div>

            <div>
              <h5 class="font-semibold text-gray-900 mb-3">Thông tin hệ thống</h5>
              <div class="space-y-2 text-sm">
                <div>
                  <span class="font-medium">Ngày tạo:</span>
                  {{ formatDate(selectedUser.creation) }}
                </div>
                <div>
                  <span class="font-medium">Cập nhật cuối:</span>
                  {{ formatDate(selectedUser.modified) }}
                </div>
                <div>
                  <span class="font-medium">Lần cuối đăng nhập:</span>
                  {{ selectedUser.last_login ? formatDate(selectedUser.last_login) : 'Chưa đăng nhập' }}
                </div>
                <div>
                  <span class="font-medium">Hoạt động cuối:</span>
                  {{ selectedUser.last_active ? formatDate(selectedUser.last_active) : 'Chưa có' }}
                </div>
                <div>
                  <span class="font-medium">Ngôn ngữ:</span>
                  {{ selectedUser.language || 'vi' }}
                </div>
                <div>
                  <span class="font-medium">Múi giờ:</span>
                  {{ selectedUser.time_zone || 'Asia/Ho_Chi_Minh' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Roles -->
          <div>
            <h5 class="font-semibold text-gray-900 mb-3">Vai trò</h5>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="role in selectedUser.roles"
                :key="role"
                class="px-3 py-1 text-sm rounded-full"
                :class="getRoleClass(role)"
              >
                {{ role }}
              </span>
            </div>
          </div>

          <!-- Activity Stats -->
          <div v-if="selectedUser.activity_stats">
            <h5 class="font-semibold text-gray-900 mb-3">Thống kê hoạt động</h5>
            <div class="grid grid-cols-3 gap-4">
              <div class="text-center p-3 bg-blue-50 rounded-lg">
                <div class="text-2xl font-bold text-blue-600">{{ selectedUser.activity_stats.login_count || 0 }}</div>
                <div class="text-sm text-gray-600">Lần đăng nhập</div>
              </div>
              <div class="text-center p-3 bg-green-50 rounded-lg">
                <div class="text-2xl font-bold text-green-600">
                  {{ selectedUser.activity_stats.documents_created || 0 }}
                </div>
                <div class="text-sm text-gray-600">Tài liệu tạo</div>
              </div>
              <div class="text-center p-3 bg-purple-50 rounded-lg">
                <div class="text-2xl font-bold text-purple-600">
                  {{ selectedUser.activity_stats.total_sessions || 0 }}
                </div>
                <div class="text-sm text-gray-600">Phiên làm việc</div>
              </div>
            </div>
          </div>

          <!-- Bio -->
          <div v-if="selectedUser.bio">
            <h5 class="font-semibold text-gray-900 mb-3">Giới thiệu</h5>
            <p class="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{{ selectedUser.bio }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" class="fixed top-4 right-4 z-50">
      <div
        :class="[
          'px-6 py-4 rounded-lg shadow-lg',
          message.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white',
        ]"
      >
        {{ message.text }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call, createResource } from 'frappe-ui'
import { useI18n } from 'vue-i18n'
import {
  UserPlus as UserPlusIcon,
  Search as SearchIcon,
  Users as UsersIcon,
  Edit as EditIcon,
  Trash as TrashIcon,
  X as XIcon,
  Loader as LoaderIcon,
  CheckCircle as CheckCircleIcon,
  XCircle as XCircleIcon,
  MinusCircle as MinusCircleIcon,
  PlusCircle as PlusCircleIcon,
  Eye as EyeIcon,
  Key as KeyIcon,
  RefreshCw as RefreshCwIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ChevronsLeft as ChevronsLeftIcon,
  ChevronsRight as ChevronsRightIcon,
} from 'lucide-vue-next'
import {
  getUsers as fetchUsers,
  getAvailableRoles as fetchAvailableRoles,
  getUserStats as fetchUserStats,
  createUser as createUserService,
  updateUser as updateUserService,
  deleteUser as deleteUserService,
} from '@/services/userService'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import { useNotificationStore } from '@/stores/notifications'

const notificationStore = useNotificationStore()

const { t } = useI18n()

// Reactive data
const users = ref([])
const stats = ref({})
const availableRoles = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const roleFilter = ref('')
const pageSize = ref(20)
const showAddUserModal = ref(false)
const showUserDetail = ref(false)
const editingUser = ref(null)
const selectedUser = ref(null)
const message = ref(null)

// Pagination
const pagination = ref({
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 0,
  has_next: false,
  has_prev: false,
})

const userForm = ref({
  email: '',
  full_name: '',
  first_name: '',
  last_name: '',
  password: '',
  mobile_no: '',
  gender: '',
  roles: [],
  enabled: 1,
})

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.value.page = 1
    loadUsers()
  }, 500)
}

const normalizeRoles = (rawRoles) => {
  if (Array.isArray(rawRoles)) {
    return rawRoles
      .map((role) => {
        if (!role && role !== 0) return null
        if (typeof role === 'string') return role
        return role.role_name || role.name || role
      })
      .filter(Boolean)
  }
  if (typeof rawRoles === 'string' && rawRoles.trim()) {
    return rawRoles
      .split(',')
      .map((r) => r.trim())
      .filter(Boolean)
  }
  return []
}

const normalizeUserRecord = (user) => {
  if (!user) return user
  const roles = normalizeRoles(user.roles ?? user.ai_roles ?? [])
  const enabledFlag = typeof user.enabled === 'number' ? user.enabled === 1 : user.enabled !== false
  const status = user.status || (enabledFlag ? 'active' : 'inactive')

  return {
    ...user,
    id: user.id || user.name || user.email,
    name: user.name || user.id || user.email,
    email: user.email || user.name || '',
    full_name: user.full_name || user.name || '',
    roles,
    ai_roles: Array.isArray(user.ai_roles) ? user.ai_roles : roles,
    enabled: enabledFlag,
    status,
  }
}

// Methods
const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getRoleClass = (role) => {
  const roleName = typeof role === 'string' ? role : role?.role_name || ''
  const roleActive = typeof role === 'object' ? role?.is_active : true

  const classes = {
    'System Manager': 'bg-red-100 text-red-800',
    Administrator: 'bg-red-100 text-red-800',
    'AI Agent Admin': 'bg-blue-100 text-blue-800',
    'AI Agent User': 'bg-green-100 text-green-800',
    User: 'bg-gray-100 text-gray-800',
    Guest: 'bg-gray-100 text-gray-800',
  }
  const baseClass = classes[roleName] || 'bg-purple-100 text-purple-800'

  if (!roleActive) {
    return 'bg-gray-200 text-gray-500'
  }

  return baseClass
}

const getStatusIcon = (status) => {
  const icons = {
    active: CheckCircleIcon,
    inactive: MinusCircleIcon,
    suspended: XCircleIcon,
  }
  return icons[status] || CheckCircleIcon
}

const getStatusClass = (status) => {
  const classes = {
    active: 'text-green-500',
    inactive: 'text-gray-500',
    suspended: 'text-red-500',
  }
  return classes[status] || 'text-gray-500'
}

const getStatusTextClass = (status) => {
  const classes = {
    active: 'text-green-700',
    inactive: 'text-gray-700',
    suspended: 'text-red-700',
  }
  return classes[status] || 'text-gray-700'
}

const getVisiblePages = () => {
  const current = pagination.value.page
  const total = pagination.value.total_pages
  const delta = 2

  let start = Math.max(1, current - delta)
  let end = Math.min(total, current + delta)

  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4)
    } else if (end === total) {
      start = Math.max(1, end - 4)
    }
  }

  const pages = []
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    pagination.value.page = page
    loadUsers()
  }
}

const changePageSize = () => {
  pagination.value.page = 1
  pagination.value.page_size = parseInt(pageSize.value)
  loadUsers()
}

const viewUserDetail = async (user) => {
  try {
    const response = await createResource({
      url: 'dbiz_ai_agent.api.users.get_user_detail',
      params: { user_id: user.name },
      method: 'GET',
    }).fetch()
    const payload = response?.message ?? response?.data
    if (payload) {
      selectedUser.value = payload.data ?? payload
      showUserDetail.value = true
    }
  } catch (error) {
    showMessage('Không thể tải chi tiết người dùng', 'error')
    console.error('Get user detail error:', error)
  }
}

const editUser = (user) => {
  editingUser.value = user
  userForm.value = {
    email: user.email,
    full_name: user.full_name || '',
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    password: '',
    mobile_no: user.mobile_no || '',
    gender: user.gender || '',
    roles: [...user.roles],
    enabled: user.enabled ? 1 : 0,
  }
}

const deleteUser = async (user) => {
  if (!confirm(`Bạn có chắc muốn vô hiệu hóa người dùng "${user.full_name || user.email}"?`)) return
  try {
    const payload = await deleteUserService(user.name || user.id)
    if (payload?.success === false) throw new Error(payload.error || 'Không thể vô hiệu hóa người dùng')
    showMessage(payload?.message || 'Người dùng đã được vô hiệu hóa', 'success')
    loadUsers()
  } catch (error) {
    showMessage('Lỗi khi vô hiệu hóa người dùng', 'error')
    console.error('Delete user error:', error)
  }
}

const resetPassword = async (user) => {
  const newPassword = prompt(`Nhập mật khẩu mới cho ${user.full_name || user.email}:`)
  if (!newPassword) return
  if (newPassword.length < 8) {
    notificationStore.notify('Mật khẩu phải có ít nhất 8 ký tự', 'warning')
    return
  }
  try {
    const response = await createResource({
      url: 'dbiz_ai_agent.api.users.reset_user_password',
      params: { user_id: user.name, new_password: newPassword },
      method: 'POST',
    }).fetch()
    const payload = response?.message ?? response?.data
    if (payload) showMessage(payload.message || 'Mật khẩu đã được reset thành công', 'success')
  } catch (error) {
    showMessage('Lỗi khi reset mật khẩu', 'error')
    console.error('Reset password error:', error)
  }
}

const saveUser = async () => {
  if (!userForm.value.email || !userForm.value.full_name || userForm.value.roles.length === 0) {
    showMessage('Vui lòng điền đầy đủ thông tin bắt buộc', 'error')
    return
  }

  if (!editingUser.value && !userForm.value.password) {
    showMessage('Vui lòng nhập mật khẩu cho người dùng mới', 'error')
    return
  }

  saving.value = true

  try {
    const params = { ...userForm.value }
    let response
    if (editingUser.value) {
      response = await updateUserService(editingUser.value.name || editingUser.value.id, params)
    } else {
      response = await createUserService(params)
    }

    if (response?.success === false) {
      throw new Error(response.error || 'Không thể lưu người dùng')
    }

    showMessage(response?.message || 'Lưu thành công!', 'success')
    closeModal()
    loadUsers()
    loadStats()
  } catch (error) {
    showMessage('Lỗi khi lưu người dùng', 'error')
    console.error('Save user error:', error)
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showAddUserModal.value = false
  editingUser.value = null
  userForm.value = {
    email: '',
    full_name: '',
    first_name: '',
    last_name: '',
    password: '',
    mobile_no: '',
    gender: '',
    roles: [],
    enabled: 1,
  }
}

const loadUsers = async () => {
  loading.value = true

  try {
    const { users: apiUsers, pagination: paginationInfo } = await fetchUsers({
      page: pagination.value.page,
      pageSize: pagination.value.page_size,
      search: searchQuery.value,
      status: statusFilter.value,
      role: roleFilter.value,
    })

    users.value = (apiUsers || []).map(normalizeUserRecord)
    const info = paginationInfo || {}
    pagination.value = {
      page: info.page ?? pagination.value.page,
      page_size: info.page_size ?? pagination.value.page_size,
      total_count: info.total_count ?? pagination.value.total_count,
      total_pages: info.total_pages ?? pagination.value.total_pages,
      has_next: info.has_next ?? pagination.value.has_next ?? false,
      has_prev: info.has_prev ?? pagination.value.has_prev ?? false,
    }
  } catch (error) {
    showMessage('Lỗi khi tải danh sách người dùng', 'error')
    console.error('Load users error:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const data = await fetchUserStats()
    stats.value = data.data ?? data
  } catch (error) {
    console.error('Load stats error:', error)
  }
}

const loadRoles = async () => {
  try {
    const roles = await fetchAvailableRoles()
    availableRoles.value = Array.isArray(roles) ? roles : []
  } catch (error) {
    console.error('Load roles error:', error)
  }
}

const showMessage = (text, type = 'success') => {
  message.value = { text, type }
  setTimeout(() => {
    message.value = null
  }, 5000)
}

onMounted(() => {
  loadUsers()
  loadStats()
  loadRoles()
})
</script>
