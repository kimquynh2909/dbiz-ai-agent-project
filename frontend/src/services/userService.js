export const unwrapResponse = (payload) => {
  if (!payload) return null
  if (Object.prototype.hasOwnProperty.call(payload, 'success')) {
    return payload
  }
  if (Object.prototype.hasOwnProperty.call(payload, 'message')) {
    return unwrapResponse(payload.message)
  }
  if (Object.prototype.hasOwnProperty.call(payload, 'data')) {
    return { success: true, data: payload.data }
  }
  return null
}


import { createResource } from 'frappe-ui'

const callFrappe = async (method, args = {}) => {
  const response = await createResource({ url: method, params: args, method: (Object.keys(args || {}).length ? 'POST' : 'GET') }).fetch()
  return unwrapResponse(response) || response
}

export const getUsers = async ({ page = 1, pageSize = 20, search = '', role = '', status = '' } = {}) => {
  const result = await callFrappe('dbiz_ai_agent.api.users.get_users', {
    page,
    page_size: pageSize,
    search: search || undefined,
    role: role || undefined,
    status: status || undefined
  })

  const data = result?.data ?? result ?? {}
  const users = data.users ?? []
  const pagination = data.pagination ?? {
    page,
    page_size: pageSize,
    total_count: users.length,
    total_pages: 1,
    has_next: false,
    has_prev: false
  }

  return { users, pagination, raw: data }
}

export const getAvailableRoles = async () => {
  const result = await callFrappe('dbiz_ai_agent.api.users.get_available_roles')
  const data = result?.data ?? result ?? []
  return Array.isArray(data) ? data : data.roles ?? []
}

export const getUserStats = async () => {
  const result = await callFrappe('dbiz_ai_agent.api.users.get_user_stats')
  return result?.data ?? result ?? {}
}

export const createUser = async (payload) => {
  return callFrappe('dbiz_ai_agent.api.users.create_user', payload)
}

export const updateUser = async (userId, payload) => {
  return callFrappe('dbiz_ai_agent.api.users.update_user', {
    user_id: userId,
    ...payload
  })
}

export const deleteUser = async (userId) => {
  return callFrappe('dbiz_ai_agent.api.users.delete_user', { user_id: userId })
}
