import frappe
from frappe import _
import json
import re
from datetime import datetime
from dbiz_ai_agent.agentic_ai.agents.orchestration.smart_orchestrator import SmartOrchestrator
from dbiz_ai_agent.dbiz_ai_agent.doctype.ai_conversation.ai_conversation import (
    append_conversation_message,
    provide_feedback as conversation_provide_feedback,
    create_conversation,
    get_conversation as get_conversation_helper,
    delete_conversation as delete_conversation_helper,
    get_user_conversations as get_user_conversations_helper,
    delete_all_user_conversations as delete_all_user_conversations_helper,
)
from dbiz_ai_agent.dbiz_ai_agent.doctype.document_image.document_image import fetch_images_from_placeholders
from dbiz_ai_agent.helpers.chat_utility import (
    collect_stream_chunks,
    build_stream_summary,
    publish_stream_completion,
)

# Lazy module-level orchestrator instance to avoid repeated construction
_SMART_ORCHESTRATOR = None

def _get_smart_orchestrator():
    global _SMART_ORCHESTRATOR
    if _SMART_ORCHESTRATOR is None:
        try:
            _SMART_ORCHESTRATOR = SmartOrchestrator()
        except Exception:
            raise
    return _SMART_ORCHESTRATOR

@frappe.whitelist()
def Get_Conversations():
    return get_user_conversations_helper(user=frappe.session.user, status="Active")

@frappe.whitelist()
def Get_Conversation(conversation_name):
    try:
        # Sử dụng helper function
        conversation = get_conversation_helper(conversation_name, for_update=False)
        # Reload child table
        conversation.load_from_db()
    except frappe.DoesNotExistError:
        frappe.throw(_("Không tìm thấy cuộc hội thoại"))
    except Exception as err:
        frappe.log_error(f"Không thể tải cuộc hội thoại {conversation_name}: {str(err)}")
        frappe.throw(_("Không thể tải cuộc hội thoại."))
    if conversation.user != frappe.session.user:
        frappe.throw(_("Không có quyền truy cập"))
    
    print(f"📖 Get_Conversation: Loading {len(conversation.messages)} messages")
    
    messages = []
    for msg in conversation.messages:
        # We intentionally omit 'sources' from the conversation payload.
        images = []
        if msg.content:
            placeholder_ids = re.findall(r"\[\[IMAGE::([^\]]+)\]\]", msg.content)
            if placeholder_ids:
                images = fetch_images_from_placeholders(placeholder_ids, set()) or []
        
        is_streaming = getattr(msg, "is_streaming", 0) or 0
        stream_key = getattr(msg, "stream_key", None)
        
        # Debug: log tất cả fields của message
        if msg.role == "assistant":
            print(f"   Message {msg.name}: role={msg.role}, is_streaming={is_streaming}, stream_key={stream_key}, has_content={bool(msg.content)}")
        
        messages.append({
            "id": msg.name,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp,
            "feedback": msg.feedback,
            "images": images,
            "is_streaming": is_streaming,
            "stream_key": stream_key,
            "conversation_name": conversation.name,
        })
    return {
        "conversation": {
            "id": conversation.name,
            "name": conversation.name,
            "title": conversation.title,
            "created_date": conversation.created_date,
            "message_count": conversation.message_count,
        },
        "messages": messages,
    }

def Ensure_Conversation(conversation_name, user = "Guest"):
    if conversation_name:
        conversation = get_conversation_helper(conversation_name)
    else:
        result = create_conversation(title="New Conversation", user=user)
        conversation = get_conversation_helper(result["name"])
    
    return conversation

@frappe.whitelist(allow_guest=True)
def Send_Message_Streaming(conversation_name=None, message=None):
    user = frappe.session.user
    if not message:
        frappe.throw(_("Tin nhắn không được để trống"))
    if user:
        conversation = Ensure_Conversation(conversation_name, user=user)
    else: 
        conversation = Ensure_Conversation(conversation_name)
    orchestrator = _get_smart_orchestrator()
    conversation = append_conversation_message(
        conversation,
        role="user",
        content=message,
        title_generator=lambda _conv_name, text: orchestrator.generate_conversation_title(text),
    )
    # Lấy ID của tin nhắn user vừa lưu (tin nhắn cuối cùng)
    user_message_id = conversation.messages[-1].name if conversation.messages else None
    return {
        "conversation": {"name": conversation.name,
                         "title": conversation.title,
                         "created_date": conversation.created_date,
                         "last_message_date": conversation.last_message_date,
                         "message_count": conversation.message_count},
        "user_message_id": user_message_id,
        "streaming": True
    }

from typing import Optional


@frappe.whitelist(allow_guest=True)
def Stream_AI_Response(conversation_name, message, message_key=None, id_token: Optional[str] = None):
    conversation = get_conversation_helper(conversation_name)
    
    # Tạo assistant message placeholder trước khi bắt đầu stream
    assistant_message = conversation.append("messages", {
        "role": "assistant",
        "content": "",
        "timestamp": datetime.now(),
        "is_streaming": 1,
        "stream_key": message_key
    })
    conversation.save()
    frappe.db.commit()
    
    assistant_message_id = assistant_message.name
    
    _Run_Streaming_Job(
        conversation_name,
        message_text=message,
        message_key=message_key,
        user=conversation.user,
        id_token=id_token,
        assistant_message_name=assistant_message_id,
    )
    return {
        "started": True,
        "message_key": message_key,
        "assistant_message_id": assistant_message_id
    }

def _Run_Streaming_Job(conversation_name, message_text, message_key, user=None, id_token: Optional[str] = None, assistant_message_name=None):
    message_key = str(message_key)
    assistant_message = None
    try:
        orchestrator = _get_smart_orchestrator()
        # SmartOrchestrator không có Ensure_Conversation, chỉ cần conversation_name
        conversation_id = conversation_name
        
        # Lấy assistant message đã tạo từ Stream_AI_Response
        try:
            # Reload để lấy message mới nhất
            conversation = get_conversation_helper(conversation_name)
            if assistant_message_name:
                for msg in conversation.messages:
                    if msg.name == assistant_message_name:
                        assistant_message = msg
                        break
            
            if not assistant_message:
                # Fallback: tạo mới nếu không tìm thấy
                assistant_message = conversation.append("messages", {
                    "role": "assistant",
                    "content": "",
                    "timestamp": datetime.now(),
                    "is_streaming": 1,
                    "stream_key": message_key
                })
                conversation.save()
                frappe.db.commit()
            
            print(f"✅ Using assistant message: is_streaming={assistant_message.is_streaming}, stream_key={message_key}, name={assistant_message.name}")
        except Exception as create_err:
            frappe.log_error(f"Không thể lấy/tạo assistant message: {str(create_err)}")
            print(f"❌ Error with message: {str(create_err)}")
        
        placeholder_pattern = re.compile(r"\[\[IMAGE::([^\]]+)\]\]")
        print(f"🚀 Starting stream collection, assistant_message={assistant_message.name if assistant_message else None}")
        collected_chunks, streamed_images, seen_placeholders = collect_stream_chunks(
            orchestrator,
            conversation_name,
            conversation_id,
            message_text,
            message_key,
            user,
            id_token,
            placeholder_pattern,
            assistant_message,
        )
        print(f"📦 Stream collection completed, chunks={len(collected_chunks)}")

        # Build summary but be defensive: if extraction fails, still attempt to
        # publish a completion event so clients can stop streaming.
        final_text = ""
        sources = []
        images = []
        tool_results = []
        try:
            final_text, sources, images, tool_results = build_stream_summary(
                orchestrator,
                collected_chunks,
                streamed_images,
                seen_placeholders,
                conversation_name,
                message_key,
                user,
                id_token,
            )
        except Exception as summary_err:
            # Log and continue — we'll still publish completion below.
            try:
                frappe.log_error(f"Không thể tóm tắt luồng: {str(summary_err)}")
            except Exception:
                pass

        # Only keep sources that have a resolved file_url. If no source has
        # a file_url, we won't include the sources field at all (so UI won't show it).
        filtered_sources = []
        for s in (sources or []):
            if isinstance(s, dict) and s.get('file_url'):
                filtered_sources.append(s)

        # ================================================================
        # CRITICAL: Update DB FIRST, then send Socket.IO event
        # This ensures FE can fallback to polling if Socket.IO fails
        # ================================================================
        
        # Filter images to only keep id and image_url
        filtered_images = [
            {"id": img.get("id"), "image_url": img.get("image_url")}
            for img in (images or [])
            if isinstance(img, dict) and img.get("id") and img.get("image_url")
        ]
        
        db_updated = False
        
        # Step 1: Update DB to mark streaming as complete
        # Use DIRECT SQL UPDATE for reliability - child table ORM updates can be unreliable
        try:
            print(f"💾 Persisting message, assistant_message={assistant_message.name if assistant_message else None}")
            
            if assistant_message:
                message_name = assistant_message.name
                
                # DIRECT SQL UPDATE - more reliable than ORM for child tables
                frappe.db.sql("""
                    UPDATE `tabAI Message` 
                    SET 
                        content = %s,
                        is_streaming = 0,
                        stream_key = NULL,
                        modified = NOW()
                    WHERE name = %s
                """, (final_text or "", message_name))
                
                frappe.db.commit()
                db_updated = True
                
                # Verify the update
                verify = frappe.db.get_value(
                    "AI Message", 
                    message_name, 
                    ["is_streaming", "content"], 
                    as_dict=True
                )
                
                if verify:
                    print(f"🏁 Stream completed in DB: is_streaming={verify.is_streaming}, content_length={len(verify.content or '')}")
                    if verify.is_streaming != 0:
                        # Update failed somehow, try again with set_value
                        frappe.db.set_value("AI Message", message_name, {
                            "is_streaming": 0,
                            "stream_key": None,
                            "content": final_text or ""
                        })
                        frappe.db.commit()
                        print(f"🔄 Retry update with set_value")
                else:
                    print(f"⚠️ Could not verify message {message_name}")
                    
            else:
                # Fallback: tạo message mới nếu chưa có
                append_conversation_message(
                    conversation_name,
                    role="assistant",
                    content=final_text or "",
                    conversation_id=conversation_id,
                    title_generator=lambda _conv_name, text: orchestrator.generate_conversation_title(text),
                    images=filtered_images,
                )
                db_updated = True
                
        except Exception as persist_err:
            frappe.log_error(
                f"Không thể cập nhật message assistant: {str(persist_err)}",
                "Stream DB Update Error"
            )
            # Last resort: try direct set_value
            try:
                if assistant_message:
                    frappe.db.set_value("AI Message", assistant_message.name, {
                        "is_streaming": 0,
                        "stream_key": None,
                        "content": final_text or ""
                    })
                    frappe.db.commit()
                    db_updated = True
                    print(f"🔄 Fallback update succeeded")
            except Exception as fallback_err:
                frappe.log_error(f"Fallback update also failed: {str(fallback_err)}")

        # Step 2: Send Socket.IO completion event (with retry)
        # Even if this fails, DB is already updated so FE can poll
        socketio_success = False
        try:
            socketio_success = publish_stream_completion(
                conversation_name,
                message_key,
                user,
                final_text,
                None,  # sources intentionally None for realtime
                images,
                tool_results,
                id_token,
            )
            
            if socketio_success:
                print(f"✅ Socket.IO done event sent successfully")
            else:
                print(f"⚠️ Socket.IO done event failed, FE should use DB polling fallback")
                
        except Exception as pub_err:
            frappe.log_error(
                f"Socket.IO completion event error: {str(pub_err)}",
                "Stream Socket.IO Error"
            )
        
        # Log summary
        print(f"📊 Stream completion summary: DB={db_updated}, Socket.IO={socketio_success}")

    except Exception as e:
        try:
            frappe.log_error(f"Streaming error (background): {str(e)}\n{frappe.get_traceback()}")
        except Exception:
            pass
        raise


@frappe.whitelist()
def Resume_Streaming(conversation_name, stream_key):
    """
    API để reconnect vào stream đang chạy.
    Frontend gọi khi phát hiện message có is_streaming = 1
    """
    try:
        # Kiểm tra quyền truy cập - helper sẽ tự động kiểm tra
        conversation = get_conversation_helper(conversation_name)
        
        # Tìm message đang stream
        streaming_message = None
        for msg in conversation.messages:
            if msg.get("stream_key") == stream_key and msg.get("is_streaming") == 1:
                streaming_message = msg
                break
        
        if not streaming_message:
            return {"success": False, "message": "Stream không còn active"}
        
        # Trả về thông tin để frontend reconnect
        return {
            "success": True,
            "stream_key": stream_key,
            "current_content": streaming_message.get("content", ""),
            "message": "Reconnecting to stream..."
        }
    except Exception as e:
        frappe.log_error(f"Không thể resume stream: {str(e)}")
        return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=True)
def Update_Message_Streaming_Status(conversation_name, message_id, is_streaming=0, content=None):
    """
    API để cập nhật trạng thái streaming của message trong database.
    Được gọi từ frontend khi:
    - Stream kết thúc (done)
    - Stream bị lỗi (error)
    - Stream bị timeout (stalled)
    """
    try:
        is_streaming_int = int(is_streaming) if is_streaming is not None else 0
        
        # Use DIRECT SQL UPDATE for reliability
        update_values = {
            "is_streaming": is_streaming_int,
            "modified": frappe.utils.now()
        }
        
        if content is not None:
            update_values["content"] = content
        
        if is_streaming_int == 0:
            update_values["stream_key"] = None
        
        frappe.db.set_value("AI Message", message_id, update_values)
        frappe.db.commit()
        
        # Verify update
        verify = frappe.db.get_value("AI Message", message_id, "is_streaming")
        
        return {
            "success": True,
            "message": "Đã cập nhật trạng thái streaming",
            "is_streaming": verify
        }
    except Exception as e:
        frappe.log_error(f"Không thể cập nhật streaming status: {str(e)}")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def Force_Complete_Stream(conversation_name, message_id=None, stream_key=None):
    """
    Force complete a streaming message - use when stream appears stuck.
    
    FE should call this if:
    - No chunks received for 30+ seconds
    - Done event not received after stream appears complete
    - User clicks "Stop generating" button
    
    Args:
        conversation_name: Conversation ID
        message_id: Message ID to complete (preferred)
        stream_key: Stream key to find message (alternative)
    
    Returns:
        Success status and final message content
    """
    try:
        # Find message by ID or stream_key
        target_name = message_id
        
        if not target_name and stream_key:
            # Find by stream_key
            result = frappe.db.get_value(
                "AI Message",
                {"stream_key": stream_key, "is_streaming": 1},
                "name"
            )
            target_name = result
        
        if not target_name:
            return {"success": False, "error": "Message not found"}
        
        # Get current content
        current = frappe.db.get_value(
            "AI Message",
            target_name,
            ["content", "is_streaming"],
            as_dict=True
        )
        
        if not current:
            return {"success": False, "error": "Message not found"}
        
        if current.is_streaming == 0:
            # Already completed
            return {
                "success": True,
                "message": "Stream already completed",
                "content": current.content or "",
                "was_streaming": False
            }
        
        # Force complete
        frappe.db.sql("""
            UPDATE `tabAI Message` 
            SET 
                is_streaming = 0,
                stream_key = NULL,
                modified = NOW()
            WHERE name = %s
        """, (target_name,))
        frappe.db.commit()
        
        print(f"🛑 Force completed stream for message {target_name}")
        
        return {
            "success": True,
            "message": "Stream force completed",
            "message_id": target_name,
            "content": current.content or "",
            "was_streaming": True
        }
        
    except Exception as e:
        frappe.log_error(f"Force_Complete_Stream error: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist(allow_guest=True)
def Check_Stream_Status(conversation_name, message_id=None, stream_key=None):
    """
    Polling endpoint for FE to check streaming status.
    
    Use this as fallback when Socket.IO done event is not received.
    FE should poll every 2-3 seconds if stream appears stalled.
    
    Args:
        conversation_name: Conversation ID
        message_id: Optional message ID to check
        stream_key: Optional stream key to find message
    
    Returns:
        {
            "is_streaming": bool,
            "content": str,
            "message_id": str,
            "completed": bool
        }
    """
    try:
        conversation = get_conversation_helper(conversation_name, for_update=False)
        
        # Find the message
        target_message = None
        
        if message_id:
            for msg in conversation.messages:
                if msg.name == message_id:
                    target_message = msg
                    break
        elif stream_key:
            for msg in conversation.messages:
                if getattr(msg, "stream_key", None) == stream_key:
                    target_message = msg
                    break
        else:
            # Find latest assistant message
            for msg in reversed(conversation.messages):
                if msg.role == "assistant":
                    target_message = msg
                    break
        
        if not target_message:
            return {
                "success": False,
                "error": "Message not found"
            }
        
        is_streaming = bool(getattr(target_message, "is_streaming", 0))
        
        return {
            "success": True,
            "message_id": target_message.name,
            "is_streaming": is_streaming,
            "completed": not is_streaming,
            "content": target_message.content or "",
            "stream_key": getattr(target_message, "stream_key", None),
        }
        
    except Exception as e:
        frappe.log_error(f"Check_Stream_Status error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def Provide_Feedback(message_id, helpful):
    return conversation_provide_feedback(message_id, helpful)

@frappe.whitelist()
def Delete_Conversation(conversation_name):
    return delete_conversation_helper(conversation_name)

@frappe.whitelist()
def Delete_All_Conversations():
    return delete_all_user_conversations_helper(user=frappe.session.user)
