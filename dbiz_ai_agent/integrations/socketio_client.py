"""
Socket.IO client publisher for realtime streaming.

This module is optional. It activates when `socketio_server_url` is set in
Frappe site_config (or env var SOCKETIO_SERVER_URL). It mirrors the Firebase
publisher API so the rest of the code can switch transparently.

Features:
- Connection health check with auto-reconnect
- Retry mechanism for critical events (done)
- Better error handling and logging
"""
from __future__ import annotations

from typing import Optional, Any, Dict
import threading

import os
import time

import frappe
import socketio

_client_lock = threading.RLock()
_client = None
_client_url = None
_last_successful_emit = 0  # Timestamp of last successful emit


def _get_conf_value(key: str, default: Optional[str] = None) -> Optional[str]:
    try:
        val = (getattr(frappe, 'conf', {}) or {}).get(key)
        if val:
            return str(val)
    except Exception:
        pass
    return os.environ.get(key.upper(), default)


def _is_connected() -> bool:
    """Check if Socket.IO client is connected."""
    global _client
    if _client is None:
        return False
    try:
        return _client.connected
    except Exception:
        return False


def _force_reconnect() -> bool:
    """Force reconnect the Socket.IO client."""
    global _client, _client_url
    with _client_lock:
        # Disconnect existing client
        if _client:
            try:
                _client.disconnect()
            except Exception:
                pass
            _client = None
        
        # Create new connection
        try:
            _ensure_client()
            return True
        except Exception as e:
            frappe.log_error(f"Socket.IO force reconnect failed: {str(e)}")
            return False


def _ensure_client():
    global _client, _client_url
    with _client_lock:
        url = _get_conf_value('socketio_server_url')
        if not url:
            raise RuntimeError('socketio_server_url is not configured')

        # Check if existing client is still connected
        if _client and _client_url == url:
            if _is_connected():
                return _client
            else:
                # Client exists but disconnected - try to reconnect
                try:
                    _client.disconnect()
                except Exception:
                    pass
                _client = None
        
        # Tear down previous client if URL changed
        if _client and _client_url != url:
            try:
                _client.disconnect()
            except Exception:
                pass
            _client = None

        sio = socketio.Client(
            request_timeout=300,  # 5 phút cho streaming dài
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5
        )
        
        # Optional static auth token (dev/testing)
        auth_token = _get_conf_value('socketio_auth_token')
        
        # Connect with error handling
        try:
            sio.connect(
                url,
                transports=['websocket'],
                auth={'token': auth_token} if auth_token else None,
            )
        except Exception as e:
            frappe.log_error(f"Socket.IO connection failed to {url}: {str(e)}")
            raise

        _client = sio
        _client_url = url
        return _client


def _room_name(uid: str, conversation_name: str, message_key: str) -> str:
    # Room naming aligned with frontend join semantics (no uid)
    safe = lambda s: ''.join(c if c.isalnum() or c in '-_:' else '-' for c in str(s or '_'))
    return f"room:{safe(conversation_name)}:{safe(message_key)}"


def _resolve_uid(user: Optional[str] = None, id_token: Optional[str] = None) -> str:
    # For dev/demo we prefer explicit user; fall back to session user
    # (verification, if any, should be handled by the socket server if needed)
    try:
        return user or frappe.session.user or 'Guest'
    except Exception:
        return user or 'Guest'


def _emit(event: str, payload: Dict[str, Any], retry_count: int = 0, max_retries: int = 1):
    """
    Emit event to Socket.IO server with optional retry.
    
    Args:
        event: Event name
        payload: Event payload
        retry_count: Current retry attempt (internal use)
        max_retries: Maximum retry attempts (default 1 for regular events)
    
    Returns:
        True if emit succeeded, False otherwise
    """
    global _last_successful_emit
    
    try:
        cli = _ensure_client()
        namespace = _get_conf_value('socketio_namespace', '/') or '/'
        
        # Check connection before emit
        if not _is_connected():
            if retry_count < max_retries:
                # Try to reconnect
                if _force_reconnect():
                    return _emit(event, payload, retry_count + 1, max_retries)
            raise ConnectionError("Socket.IO client not connected")
        
        cli.emit(event, payload, namespace=namespace)
        _last_successful_emit = time.time()
        return True
        
    except Exception as e:
        if retry_count < max_retries:
            # Wait a bit before retry
            time.sleep(0.5 * (retry_count + 1))
            # Try to reconnect and retry
            _force_reconnect()
            return _emit(event, payload, retry_count + 1, max_retries)
        
        # Log error on final failure
        frappe.log_error(
            f"Socket.IO emit failed after {retry_count + 1} attempts: {str(e)}",
            "Socket.IO Emit Error"
        )
        raise


def _emit_with_retry(event: str, payload: Dict[str, Any], max_retries: int = 3):
    """
    Emit event with multiple retries - use for critical events like 'done'.
    
    Args:
        event: Event name
        payload: Event payload
        max_retries: Maximum retry attempts (default 3 for critical events)
    """
    return _emit(event, payload, retry_count=0, max_retries=max_retries)


def publish_stream_chunk(conversation_name: str, message_key: str, chunk: str, user: Optional[str] = None, id_token: Optional[str] = None):
    """
    Publish a stream chunk to Socket.IO.
    Uses single retry for chunks (not critical if one chunk is lost).
    """
    uid = _resolve_uid(user, id_token)
    payload = {
        'type': 'chunk',
        'uid': uid,
        'conversation': conversation_name,
        'message_key': str(message_key),
        'chunk': chunk or '',
        'ts': int(time.time() * 1000),
        'room': _room_name(uid, conversation_name, message_key),
    }
    try:
        _emit('chat_stream_event', payload, max_retries=1)
        return True
    except Exception:
        # Chunk loss is acceptable, don't raise
        return False


def publish_stream_images(conversation_name: str, message_key: str, images: Any, user: Optional[str] = None, id_token: Optional[str] = None):
    """
    Publish images update to Socket.IO.
    Uses retry since images are important.
    """
    uid = _resolve_uid(user, id_token)
    payload = {
        'type': 'images',
        'uid': uid,
        'conversation': conversation_name,
        'message_key': str(message_key),
        'images': images or [],
        'ts': int(time.time() * 1000),
        'room': _room_name(uid, conversation_name, message_key),
    }
    try:
        _emit('chat_stream_event', payload, max_retries=2)
        return True
    except Exception:
        return False


def publish_stream_done(
    conversation_name: str,
    message_key: str,
    final_text: Optional[str] = None,
    images: Optional[Any] = None,
    tool_results: Optional[Any] = None,
    user: Optional[str] = None,
    id_token: Optional[str] = None,
) -> bool:
    """
    Publish stream completion event to Socket.IO.
    
    CRITICAL: Uses maximum retries (3) since missing 'done' event
    causes FE to hang in streaming state.
    
    Returns:
        True if event was sent successfully, False otherwise
    """
    uid = _resolve_uid(user, id_token)
    payload = {
        'type': 'done',
        'uid': uid,
        'conversation': conversation_name,
        'message_key': str(message_key),
        'final_text': final_text or '',
        'images': images or [],
        'tool_results': tool_results or [],
        'done': True,
        'ts': int(time.time() * 1000),
        'room': _room_name(uid, conversation_name, message_key),
    }
    
    try:
        # Critical event - use max retries
        _emit_with_retry('chat_stream_event', payload, max_retries=3)
        frappe.logger().info(
            f"[SOCKET.IO] Done event sent for {conversation_name}:{message_key}"
        )
        return True
    except Exception as e:
        # Log failure but don't raise - DB is the fallback
        frappe.log_error(
            f"[SOCKET.IO] Failed to send done event for {conversation_name}:{message_key}: {str(e)}",
            "Stream Done Event Failed"
        )
        return False


def publish_realtime(event_name: str, data: Dict[str, Any], user: Optional[str] = None, id_token: Optional[str] = None):
    uid = _resolve_uid(user, id_token)
    payload = {
        'type': 'generic',
        'event': event_name,
        'uid': uid,
        'data': data or {},
        'ts': int(time.time() * 1000),
    }
    _emit('generic_event', payload)
    return True


__all__ = [
    'publish_stream_chunk',
    'publish_stream_images',
    'publish_stream_done',
    'publish_realtime',
]
