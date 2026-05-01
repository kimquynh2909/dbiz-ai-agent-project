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
