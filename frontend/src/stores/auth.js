import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

// Store xác thực người dùng
export const useAuthStore = defineStore('auth', {
  // State: lưu thông tin user, quyền, trạng thái đăng nhập
  state: () => ({
    user: null, // thông tin user
    isAuthenticated: false, // đã đăng nhập chưa
    permissions: [], // danh sách quyền
    loading: false // trạng thái loading
  }),

  // Getters: các hàm lấy thông tin từ state
  getters: {
    currentUser: (state) => state.user, // lấy user hiện tại
    userPermissions: (state) => state.permissions, // lấy quyền hiện tại
    hasPermission: (state) => (permission) => state.permissions.includes(permission), // kiểm tra quyền
    isAdmin: (state) => state.user?.role === 'Administrator' // kiểm tra admin
  },

  // Actions: các hàm xử lý logic
  actions: {
    // Đăng nhập
    async login(username, password) {
      this.loading = true
      try {
        const data = await createResource({ url: 'dbiz_ai_agent.api.auth.login', params: { username, password }, method: 'POST' }).fetch()
        const result = data || {}
        if (result.success === true && result.user) {
          this.$patch({ user: result.user, isAuthenticated: true })
          await this.fetchPermissions()
          return { success: true }
        } else {
          let errorMessage = 'Đăng nhập thất bại'
          if (result.exc_type === 'AuthenticationError' || result.message?.exc_type === 'AuthenticationError') {
            errorMessage = 'Thông tin đăng nhập không hợp lệ'
          } else if (result.message) {
            errorMessage = result.message
          } else if (result.exc) {
            errorMessage = result.exc
          }
          return { success: false, error: errorMessage }
        }
      } catch (error) {
        console.error('Login error:', error)
        let errorMessage = 'Có lỗi xảy ra, vui lòng thử lại'
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          errorMessage = 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.'
        }
        return { success: false, error: errorMessage }
      } finally {
        this.loading = false
      }
    },

    // Lấy user hiện tại
    async fetchCurrentUser() {
      try {
        // Dùng API an toàn để không lỗi khi chưa đăng nhập
        const user = await createResource({ url: 'dbiz_ai_agent.api.auth.get_logged_user', params: {}, method: 'GET' }).fetch()
        if (user) {
          const udoc = await createResource({ url: 'frappe.client.get', params: { doctype: 'User', name: user }, method: 'GET' }).fetch()
          this.$patch({ user: udoc, isAuthenticated: true })
          await this.fetchPermissions()
        } else {
          this.$patch({ user: null, isAuthenticated: false, permissions: [] })
        }
        return { authenticated: !!user }
      } catch (error) {
        // PermissionError (unauthenticated) is an expected case: treat as logged out without noisy logs
        const isPermissionError = error?.exc_type === 'PermissionError' || String(error?.message || '').includes('PermissionError')
        this.$patch({ user: null, isAuthenticated: false, permissions: [] })
        if (!isPermissionError) {
          console.error('Fetch user error:', error)
        }
        return { authenticated: false, error: isPermissionError ? null : error }
      }
    },

    // Lấy quyền user
    async fetchPermissions() {
      try {
        const res = await createResource({ url: 'dbiz_ai_agent.api.permissions.get_user_permissions', params: {}, method: 'GET' }).fetch()
        this.permissions = res || []
      } catch (error) {
        console.error('Fetch permissions error:', error)
      }
    },

    // Đăng xuất
    async logout() {
      try {
        // Use whitelisted handler logout endpoint
        await createResource({ url: 'frappe.handler.logout', params: {}, method: 'GET' }).fetch()
        this.user = null
        this.isAuthenticated = false
        this.permissions = []
        return { success: true }
      } catch (error) {
        console.error('Logout error:', error)
        this.user = null
        this.isAuthenticated = false
        this.permissions = []
        return { success: false, error: error.message }
      }
    },

    // Xóa toàn bộ thông tin xác thực
    clearAuth() {
      this.user = null
      this.isAuthenticated = false
      this.permissions = []
    }
  }
})
