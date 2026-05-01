# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import now_datetime

class AIConversation(Document):
    def before_insert(self):
        """Set default values before inserting"""
        if not self.created_date:
            self.created_date = datetime.now()
        if not self.user:
            self.user = frappe.session.user
        if not self.status:
            self.status = "Active"
    
    def before_save(self):
        """Update message count and last message date"""
        if self.messages:
            self.message_count = len(self.messages)
            # Get the latest message timestamp
            latest_message = max(self.messages, key=lambda x: x.timestamp if x.timestamp else datetime.min)
            if latest_message.timestamp:
                self.last_message_date = latest_message.timestamp
    
    @frappe.whitelist()
    def add_message(self, role, content):
        """Add a new message to the conversation"""
        # Sources are no longer stored on messages
        self.append("messages", {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
        })
        self.save()
        return self.messages[-1]
    
    @frappe.whitelist()
    def archive(self):
        """Archive the conversation"""
        self.status = "Archived"
        self.save()
        return {"success": True}
    
    @frappe.whitelist()
    def delete_conversation(self):
        """Mark conversation as deleted"""
        self.status = "Deleted"
        self.save()
        return {"success": True}


@frappe.whitelist()
def create_conversation(title: str = "New Conversation", user: str = None, status: str = "Active", initial_message: str = None):
    """Create a new AI Conversation record.

    Args:
        title: conversation title (default: "New Conversation")
        user: owner user (defaults to current session user)
        status: initial status (default: "Active")
        initial_message: optional first message content (role will be 'user')

    Returns:
        dict with success and created conversation name/title
    """
    owner = user or frappe.session.user

    conv = frappe.get_doc({
        "doctype": "AI Conversation",
        "title": title or "New Conversation",
        "user": owner,
        "status": status,
        "messages": []
    }).insert(ignore_permissions=True)

    # Optionally append an initial message
    if initial_message:
        ts = now_datetime()
        conv.append("messages", {"role": "user", "content": initial_message, "timestamp": ts})
        conv.message_count = len(conv.messages)
        conv.last_message_date = ts
        conv.save(ignore_permissions=True)
        frappe.db.commit()

    return {"success": True, "name": conv.name, "title": conv.title}


@frappe.whitelist()
def get_conversation(conversation_name: str, for_update: bool = False):
    """Get an AI Conversation document.
    
    Args:
        conversation_name: name/id of the conversation
        for_update: whether to lock the record for update
        
    Returns:
        AI Conversation document
    """
    if not conversation_name:
        frappe.throw("Conversation name is required")
    
    doc = frappe.get_doc("AI Conversation", conversation_name, for_update=for_update)
    
    # Check permissions - user can only access their own conversations
    if doc.user != frappe.session.user and frappe.session.user != "Administrator":
        frappe.throw("You don't have permission to access this conversation")
    
    return doc


@frappe.whitelist()
def delete_conversation(conversation_name: str):
    """Delete/mark a conversation as deleted.
    
    Args:
        conversation_name: name/id of the conversation
        
    Returns:
        dict with success status
    """
    doc = get_conversation(conversation_name)
    doc.status = "Deleted"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def archive_conversation(conversation_name: str):
    """Archive a conversation.
    
    Args:
        conversation_name: name/id of the conversation
        
    Returns:
        dict with success status
    """
    doc = get_conversation(conversation_name)
    doc.status = "Archived"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def get_user_conversations(user: str = None, status: str = "Active"):
    """Get all conversations for a user.
    
    Args:
        user: user email (defaults to current session user)
        status: conversation status filter (default: "Active")
        
    Returns:
        list of conversation records
    """
    user = user or frappe.session.user
    return frappe.get_all(
        "AI Conversation",
        filters={"user": user, "status": status},
        fields=["name", "title", "created_date", "last_message_date", "message_count", "openai_conversation_id"],
        order_by="last_message_date desc"
    )


@frappe.whitelist()
def delete_all_user_conversations(user: str = None):
    """Delete all conversations for a user.
    
    Args:
        user: user email (defaults to current session user)
        
    Returns:
        dict with success status and count
    """
    user = user or frappe.session.user
    conversations = frappe.get_all(
        "AI Conversation",
        filters={"user": user, "status": "Active"},
        pluck="name"
    )
    for conv_name in conversations:
        delete_conversation(conv_name)
    return {"success": True, "deleted_count": len(conversations)}


def append_conversation_message(
    conversation,
    *,
    role: str,
    content: str,
    tokens=None,
    conversation_id=None,
    title_generator=None,
    images=None,
):
    """Append a chat message to an AI Conversation record."""
    if isinstance(conversation, str):
        conversation = frappe.get_doc("AI Conversation", conversation)

    timestamp = now_datetime()
    conversation.append(
        "messages",
        {
            "role": role,
            "content": content or "",
            "timestamp": timestamp,
            "tokens_used": tokens or 0,
            # sources removed
            "openai_conversation_id": conversation_id,
            "images": json.dumps(images or []),
        },
    )

    conversation.message_count = (conversation.message_count or 0) + 1
    if not conversation.created_date:
        conversation.created_date = timestamp
    conversation.last_message_date = timestamp

    title_updated = False
    if conversation.title == "New Conversation" and title_generator:
        try:
            title_candidate = title_generator(conversation.name, content)
            if title_candidate:
                conversation.title = title_candidate
                title_updated = True
        except Exception as err:
            frappe.log_error(
                f"Không thể tạo tiêu đề cuộc hội thoại bằng agent cho {conversation.name}: {str(err)}"
            )
            raise

    conversation.save(ignore_permissions=True)
    frappe.db.commit()

    # Nếu title được cập nhật, gửi realtime event để reload sidebar
    if title_updated:
        try:
            from dbiz_ai_agent.integrations.socketio_client import publish_realtime
            publish_realtime(
                'conversation_title_updated',
                {
                    'conversation_name': conversation.name,
                    'title': conversation.title,
                },
                user=conversation.user
            )
        except Exception as e:
            frappe.log_error(f"Không thể phát sự kiện cập nhật title: {str(e)}")

    return conversation


@frappe.whitelist()
def provide_feedback(message_id: str, helpful: bool):
    """Cập nhật feedback cho một tin nhắn trong cuộc hội thoại."""
    if not message_id:
        frappe.throw(frappe._("Message not found"))

    parent_conv = frappe.db.get_value("AI Message", message_id, "parent")
    if not parent_conv:
        frappe.throw(frappe._("Message not found"))

    conversation = frappe.get_doc("AI Conversation", parent_conv)
    if conversation.user != frappe.session.user:
        frappe.throw(frappe._("Message not found"))

    feedback_value = "Helpful" if helpful else "Not Helpful"
    for msg in conversation.messages:
        if msg.name == message_id:
            msg.feedback = feedback_value
            conversation.save(ignore_permissions=True)
            frappe.db.commit()
            return {"success": True}

    frappe.throw(frappe._("Message not found"))
