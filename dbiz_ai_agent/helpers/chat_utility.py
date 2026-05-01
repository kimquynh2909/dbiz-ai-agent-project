"""Utility helpers used by chat API for streaming and image handling.

Realtime transport via Socket.IO (Firebase removed).
"""

import asyncio
from dbiz_ai_agent.agentic_ai.agents.orchestration.smart_orchestrator import SmartOrchestrator
import frappe
from typing import Optional

from dbiz_ai_agent.dbiz_ai_agent.doctype.ai_conversation.ai_conversation import get_conversation as get_conversation_helper
from dbiz_ai_agent.integrations.socketio_client import (
    publish_stream_chunk as sio_publish_chunk,
    publish_stream_images as sio_publish_images,
    publish_stream_done as sio_publish_done,
)

def _publish_chunk(conversation_name: str, message_key: str, chunk: str, user=None, id_token=None):
    try:
        return sio_publish_chunk(conversation_name, message_key, chunk, user=user, id_token=id_token)
    except Exception as e:
        try:
            frappe.log_error(f"Realtime chunk publish skipped for {conversation_name}:{message_key}: {str(e)}")
        except Exception:
            pass
        return False

def _publish_images(conversation_name: str, message_key: str, images, user=None, id_token=None):
    try:
        return sio_publish_images(conversation_name, message_key, images, user=user, id_token=id_token)
    except Exception as e:
        try:
            frappe.log_error(f"Realtime images publish skipped for {conversation_name}:{message_key}: {str(e)}")
        except Exception:
            pass
        return False

def _publish_done(conversation_name: str, message_key: str, final_text=None, images=None, tool_results=None, user=None, id_token=None) -> bool:
    """
    Publish stream completion event via Socket.IO.
    
    Returns:
        True if event was sent successfully, False otherwise.
        Note: Even if this returns False, the DB should be updated as fallback.
    """
    try:
        result = sio_publish_done(
            conversation_name, 
            message_key, 
            final_text=final_text, 
            images=images, 
            tool_results=tool_results, 
            user=user, 
            id_token=id_token
        )
        if result:
            frappe.logger().info(f"[STREAM] Done event published for {conversation_name}:{message_key}")
        return result
    except Exception as e:
        frappe.log_error(
            f"Realtime completion publish failed for {conversation_name}:{message_key}: {str(e)}",
            "Stream Completion Error"
        )
        return False

from dbiz_ai_agent.dbiz_ai_agent.doctype.document_image.document_image import (
    fetch_images_from_placeholders,
)


def collect_stream_chunks(
    orchestrator,
    conversation_name,
    conversation_id,
    message_text,
    message_key,
    user,
    id_token: Optional[str] = None,
    placeholder_pattern=None,
    assistant_message=None,
):
    """Stream agent output chunk-by-chunk, tracking text and placeholder images."""
    seen_placeholders = set()
    collected_chunks = []
    streamed_images = []
    
    # Buffer để gộp chunks nhỏ - giảm số lần gửi qua Socket.IO
    chunk_buffer = []
    buffer_size_threshold = 15
    
    # Counter để định kỳ update message vào DB (mỗi 50 chunks)
    update_counter = 0
    update_threshold = 50
    
    def _flush_buffer():
        """Gửi buffer hiện tại qua Socket.IO và update DB"""
        nonlocal update_counter
        
        if not chunk_buffer:
            return
        buffered_text = "".join(chunk_buffer)
        chunk_buffer.clear()
        
        combined_text = "".join(collected_chunks)
        ids = placeholder_pattern.findall(combined_text) if placeholder_pattern else []
        new_images = fetch_images_from_placeholders(
            ids,
            seen_placeholders,
            parent_document=None,
            skip_numeric=True,
        )
        if new_images:
            streamed_images.extend(new_images)
            publish_image_update(conversation_name, message_key, new_images, user, id_token=id_token)
        
        # Đẩy buffer qua Socket.IO
        _publish_chunk(conversation_name, message_key, buffered_text, user=user, id_token=id_token)
        
        # Định kỳ update message vào DB để khi refresh vẫn thấy
        update_counter += 1
        if assistant_message and update_counter >= update_threshold:
            try:
                # Reload conversation để lấy reference mới
                conv = get_conversation_helper(conversation_name)
                # Tìm message theo tên
                msg_to_update = None
                for msg in conv.messages:
                    if msg.name == assistant_message.name:
                        msg_to_update = msg
                        break
                
                if msg_to_update:
                    msg_to_update.content = combined_text
                    msg_to_update.is_streaming = 1  # Vẫn đang stream
                    conv.save()
                    frappe.db.commit()
                    print(f"🔄 Updated message during stream: {len(combined_text)} chars, is_streaming=1")
                
                update_counter = 0
            except Exception as e:
                frappe.log_error(f"Không thể update message trong stream: {str(e)}")
    
    def _handle_chunk(chunk):
        try:
            if isinstance(chunk, str):
                text = chunk
            elif chunk is not None:
                text = str(chunk)
            else:
                text = ""

            if text:
                collected_chunks.append(text)
                chunk_buffer.append(text)
                
                # Chỉ flush khi đạt ngưỡng size (bỏ time-based để tích lũy nhiều hơn)
                buffer_size = sum(len(c) for c in chunk_buffer)
                
                if buffer_size >= buffer_size_threshold:
                    _flush_buffer()
        except Exception as err:
            frappe.log_error(f"Không thể phát chunk realtime cho {conversation_name}:{message_key}: {str(err)}")
            raise

    run_agent_stream(
        orchestrator,
        conversation_id,
        message_text,
        _handle_chunk,
        user
    )
    
    # Flush buffer cuối cùng
    _flush_buffer()

    return collected_chunks, streamed_images, seen_placeholders


def run_agent_stream(orchestrator: SmartOrchestrator, conversation_id, message_text, on_chunk, user):
    """Execute SmartOrchestrator stream, forwarding each emitted chunk to callback."""
    async def _stream_agent():
        async for chunk in await orchestrator.orchestrate(
            user_query=message_text,
            conversation_id=conversation_id,
            stream=True
        ):
            on_chunk(chunk)
    
    # Tự quản lý event loop để cleanup đúng cách
    loop = None
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(_stream_agent())
    finally:
        # Cleanup tất cả pending tasks trước khi đóng loop
        try:
            pending = asyncio.all_tasks(loop)
            if pending:
                for task in pending:
                    task.cancel()
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass


def build_stream_summary(
    orchestrator,
    collected_chunks,
    streamed_images,
    seen_placeholders,
    conversation_name,
    message_key,
    user,
    id_token: Optional[str] = None,
):
    """Extract final text, sources, images, and tool results from SmartOrchestrator stream."""
    final_text = "".join(collected_chunks).strip() if collected_chunks else ""
    sources = []
    images = list(streamed_images)
    tool_results = []

    # Try to get state from orchestrator to extract response_images
    try:
        from dbiz_ai_agent.agentic_ai.agents.state import get_state
        state = get_state(create=False)
        if state:
            # Get images from state (synthesis agent extracted them)
            response_images = state.get("response_images", [])
            if response_images:
                images = merge_images(images, response_images)
            
            # Get sources from state if available
            response_sources = state.get("response_sources", [])
            if response_sources:
                sources = response_sources
    except Exception as e:
        frappe.log_error(f"Could not extract state data: {str(e)}")
    
    return final_text, sources, images, tool_results


def publish_stream_completion(
    conversation_name,
    message_key,
    user,
    final_text,
    sources,
    images,
    tool_results,
    id_token: Optional[str] = None,
) -> bool:
    """
    Phát sự kiện hoàn tất stream qua Socket.IO cùng metadata.
    
    Returns:
        True if Socket.IO event was sent successfully, False otherwise.
        
    Note: 
        Even if this returns False, the caller should ensure DB state is updated
        so FE can fallback to polling.
    """
    try:
        success = _publish_done(
            conversation_name,
            message_key,
            final_text=final_text,
            images=images,
            tool_results=tool_results,
            user=user,
            id_token=id_token,
        )
        
        if not success:
            frappe.logger().warning(
                f"[STREAM] Socket.IO done event failed for {conversation_name}:{message_key}, "
                "FE should fallback to DB polling"
            )
        
        return success
        
    except Exception as err:
        frappe.log_error(
            f"Không thể phát sự kiện hoàn tất cho {conversation_name}:{message_key}: {str(err)}",
            "Stream Completion Error"
        )
        return False


def publish_image_update(conversation_name, message_key, images, user=None, id_token: Optional[str] = None):
    """Phát cập nhật ảnh mới qua Socket.IO trong lúc stream."""
    if not images:
        return
    try:
        _publish_images(conversation_name, message_key, images, user=user, id_token=id_token)
    except Exception as err:
        frappe.log_error(f"Không thể phát sự kiện ảnh realtime cho {conversation_name}:{message_key}: {str(err)}")


def merge_images(existing, candidates):
    """Combine two image lists without duplicates (id or image_url)."""
    merged = list(existing or [])
    seen_ids = {img.get("id") for img in merged if img.get("id")}
    seen_urls = {img.get("image_url") for img in merged if img.get("image_url")}

    for img in candidates or []:
        if not isinstance(img, dict):
            continue
        img_id = img.get("id")
        img_url = img.get("image_url")
        if img_id and img_id in seen_ids:
            continue
        if img_url and img_url in seen_urls:
            continue
        merged.append(img)
        if img_id:
            seen_ids.add(img_id)
        if img_url:
            seen_urls.add(img_url)

    return merged

