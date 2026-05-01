export async function deleteAllConversations() {
    return await call('dbiz_ai_agent.api.chat.Delete_All_Conversations', {}, { freeze: true })
}
export async function deleteConversation(conversationName) {
    if (!conversationName) throw new Error('Thiếu tên hội thoại')
    return await call('dbiz_ai_agent.api.chat.Delete_Conversation', { conversation_name: conversationName }, { freeze: true })
}
// Service quản lý các hàm gọi API liên quan đến chat
import { call } from 'frappe-ui'

export async function loadConversations() {
    return await call('dbiz_ai_agent.api.chat.Get_Conversations', {}, { freeze: true, freeze_message: 'Đang tải cuộc hội thoại...' })
}

export async function loadConversation(conversationName) {
    if (!conversationName) return null
    return await call('dbiz_ai_agent.api.chat.Get_Conversation', { conversation_name: conversationName }, { freeze: true })
}

