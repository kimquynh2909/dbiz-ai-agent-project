"""
Retrieval Helpers Module - Utility functions for document retrieval

Contains functions for embeddings, similarity and image id parsing/fetching.
Uses Permission Denormalization for efficient Qdrant-level filtering.
"""
import re
from functools import lru_cache
from typing import List, Dict, Any, Optional
import frappe
from frappe.utils import get_url
import numpy as np
from dbiz_ai_agent.integrations import qdrant_store


# =============================================================================
# User AI Roles - Cached for performance
# =============================================================================

def get_user_ai_roles(user: str) -> List[str]:
    """
    Get AI Roles for a user from their Contact record.
    Uses request-level caching for performance.
    
    Args:
        user: User email
    
    Returns:
        List of AI Role names the user has
    """
    if not user or user in ["Administrator", "Guest"]:
        return []
    
    cache_key = f"user_ai_roles:{user}"
    if hasattr(frappe.local, "cache") and cache_key in (frappe.local.cache or {}):
        return frappe.local.cache.get(cache_key, [])
    
    user_ai_roles = []
    try:
        # Get Contact for user
        contact_name = frappe.db.get_value("Contact", {"user": user}, "name")
        if contact_name:
            # Get AI Roles from Contact's ai_roles child table
            contact_doc = frappe.get_doc("Contact", contact_name)
            ai_roles_list = getattr(contact_doc, "ai_roles", [])
            if ai_roles_list:
                user_ai_roles = [child.role for child in ai_roles_list if child.role]
    except Exception as e:
        frappe.log_error(f"Failed to get AI Roles for user {user}: {str(e)}")
    
    # Cache at request level
    if not hasattr(frappe.local, "cache"):
        frappe.local.cache = {}
    frappe.local.cache[cache_key] = user_ai_roles
    
    return user_ai_roles

def parse_image_ids_from_chunk(chunk_text: str) -> List[str]:
    """Extract ordered image ids from a chunk text using the same regex as earlier."""
    if not chunk_text:
        return []

    ordered_ids: List[str] = []
    seen: set = set()
    pattern = re.compile(r"\[\[IMAGE::([^\]]+)\]\]|ID:\s*([A-Z0-9\-]+)", re.IGNORECASE)
    for match in pattern.finditer(chunk_text):
        placeholder_id = match.group(1)
        legacy_id = match.group(2)
        image_id = (placeholder_id or legacy_id or "").strip()
        if not image_id:
            continue
        if image_id.upper().startswith("HTTP"):
            continue
        if image_id not in seen:
            ordered_ids.append(image_id)
            seen.add(image_id)
    return ordered_ids


def fetch_images_by_ids(ordered_ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch Document Image records for a list of ids (in order), returning metadata list."""
    if not ordered_ids:
        return []

    images = []
    fields = [
        "name",
        "title",
        "image_file",
        "parent_document",
        "page_number",
        "description",
        "alt_text",
    ]

    for raw_id in ordered_ids:
        image_id = (raw_id or "").strip()
        if not image_id:
            continue
        try:
            image_doc = frappe.db.get_value(
                "Document Image",
                image_id,
                fields,
                as_dict=True,
            )

            if not image_doc:
                placeholder_key = f"[[IMAGE::{image_id}]]"
                image_doc = frappe.db.get_value(
                    "Document Image",
                    {"alt_text": placeholder_key},
                    fields,
                    as_dict=True,
                )

            if not image_doc and image_id.isdigit():
                placeholder_key = f"[[IMAGE::{int(image_id)}]]"
                image_doc = frappe.db.get_value(
                    "Document Image",
                    {"alt_text": placeholder_key},
                    fields,
                    as_dict=True,
                )

            if image_doc:
                file_url = image_doc.get("image_file")
                absolute_url = None
                if file_url:
                    if file_url.lower().startswith(("http://", "https://")):
                        absolute_url = file_url
                    else:
                        absolute_url = get_url(file_url)
                images.append({
                    "id": image_doc["name"],
                    "title": image_doc.get("title"),
                    "image_url": absolute_url or file_url,
                    "file_url": file_url,
                    "parent_document": image_doc.get("parent_document"),
                    "page_number": image_doc.get("page_number"),
                    "description": image_doc.get("description"),
                    "alt_text": image_doc.get("alt_text"),
                })
        except Exception:
            # swallow to keep retrieval resilient; caller logs if desired
            continue

    return images


def get_query_embedding(openai_client, settings, query: str) -> Optional[List[float]]:
    """Generate embedding for a query using OpenAI client."""
    try:
        if not openai_client:
            frappe.log_error("OpenAI client not available for embedding")
            return None

        embedding_model = getattr(settings, 'embedding_model', 'text-embedding-3-small') if settings else 'text-embedding-3-small'
        response = openai_client.embeddings.create(
            model=embedding_model,
            input=query,
            encoding_format="float"
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        frappe.log_error(f"Query embedding failed: {str(e)}")
        return None


def get_retrieval_config():
    """Return (settings, retrieval_docs, openai_client) for retrieval tools."""
    try:
        settings = frappe.get_single("AI Agent Settings")
        retrieval_docs = getattr(settings, 'retrieval_docs', 3)
        api_key = getattr(settings, 'openai_api_key', '')
        openai_client = None
        try:
            from openai import OpenAI
            if api_key:
                openai_client = OpenAI(api_key=api_key)
        except Exception:
            openai_client = None

        return settings, retrieval_docs, openai_client
    except Exception as e:
        frappe.log_error(f"get_retrieval_config failed: {str(e)}")
        return None, 3, None


def _retrieve_from_qdrant(
    query_embedding: List[float],
    retrieval_docs: int,
    similarity_threshold: float = 0.0,
    user: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve documents from Qdrant with permission filtering at Qdrant level.
    
    Uses Permission Denormalization: permissions are stored in Qdrant payload
    and filtered at query time, eliminating the need for post-filtering.
    
    Args:
        query_embedding: Query vector
        retrieval_docs: Number of documents to retrieve
        similarity_threshold: Minimum similarity score (0.0-1.0)
        user: User email for permission filtering
    
    Returns:
        List of filtered and ranked documents
    """
    try:
        current_user = user if user else frappe.session.user
        user_ai_roles = get_user_ai_roles(current_user)
        
        permission_filter = qdrant_store.build_permission_filter(current_user, user_ai_roles)
        
        # Since filtering happens at Qdrant level, we don't need 10x multiplier
        # Just fetch a bit more to account for similarity threshold filtering
        top_k = max(retrieval_docs * 2, 10)
        # Search with permission filter - Qdrant returns ONLY documents user can access
        search_results = qdrant_store.search(
            query_embedding, 
            top_k=top_k,
            qdrant_filter=permission_filter
        )
        
        frappe.logger().info(f"[QDRANT] Found {len(search_results)} permission-filtered results")
        
    except Exception as err:
        frappe.log_error(f"Qdrant search failed: {str(err)}")
        return []

    results: List[Dict[str, Any]] = []
    for hit in search_results:
        payload = getattr(hit, 'payload', {}) or {}
        content_text = payload.get('content')
        if not content_text:
            continue

        associated_images: List[Dict[str, Any]] = []
        ordered_ids = parse_image_ids_from_chunk(content_text)
        if ordered_ids:
            associated_images = fetch_images_by_ids(ordered_ids)

        if associated_images:
            for img in associated_images:
                placeholder = img.get('alt_text')
                if placeholder and placeholder not in content_text:
                    content_text = content_text.rstrip() + "\n" + placeholder

        metadata = {
            'chunk_size': payload.get('chunk_size'),
            'chunk_hash': payload.get('chunk_hash'),
            'document': payload.get('document_path'),
            'document_id': payload.get('document_id'),
            'document_title': payload.get('document_title'),
            'access_level': payload.get('access_level'),
            'roles_allowed': payload.get('roles_allowed'),
            'departments_allowed': payload.get('departments_allowed'),
        }

        # Resolve a file URL when possible
        file_url = None
        doc_path = payload.get('document_path')
        try:
            if doc_path:
                if isinstance(doc_path, str) and doc_path.lower().startswith(("http://", "https://")):
                    file_url = doc_path
                else:
                    file_url = get_url(doc_path)
        except Exception:
            file_url = None

        source_obj = {
            'title': payload.get('document_title') or (doc_path if doc_path else ""),
            'file_url': file_url,
            'document_id': payload.get('document_id'),
            'document_path': doc_path,
        }

        results.append({
            'content': content_text,
            'source': source_obj,
            'similarity': getattr(hit, 'score', 0.0),
            'metadata': metadata,
            'images': associated_images,
        })

    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Apply similarity threshold
    if similarity_threshold:
        results = [r for r in results if r.get('similarity', 0.0) >= similarity_threshold]
        frappe.logger().info(f"[QDRANT] After similarity filter: {len(results)} results")
    
    # Return top retrieval_docs (no post-filter needed - permissions handled at Qdrant level)
    final_results = results[:retrieval_docs]
    frappe.logger().info(f"[QDRANT] Returning {len(final_results)} final results")
    
    return final_results


def retrieve_documents(
    query: str,
    openai_client,
    settings,
    retrieval_docs: int,
    similarity_threshold: float = 0.0,
    user: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve relevant documents from Qdrant for a query."""
    try:
        query_embedding = get_query_embedding(openai_client, settings, query)
        if not query_embedding:
            return []

        return _retrieve_from_qdrant(
            query_embedding,
            retrieval_docs,
            similarity_threshold=similarity_threshold,
            user=user,
        )

    except Exception as e:
        frappe.log_error(f"retrieve_documents failed: {str(e)}")
        return []


def retrieve_from_database(query: str, retrieval_docs: int, user: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search trong conversations history - CHỈ trả về conversations mà user có quyền xem"""
    try:
        current_user = user if user else frappe.session.user
        
        # Administrator và system users có thể xem tất cả conversations
        if current_user in ["Administrator", "Guest"]:
            # Guest không nên xem conversations nào cả
            if current_user == "Guest":
                frappe.logger().info("Guest user - không trả về conversations")
                return []
            
            # Administrator xem tất cả
            like_pattern = f"%{query}%"
            similar_conversations = frappe.db.sql("""
                SELECT 
                    c.name,
                    c.title,
                    m.content,
                    m.role,
                    m.creation
                FROM `tabAI Conversation` c
                JOIN `tabAI Message` m ON m.parent = c.name
                WHERE m.parenttype = 'AI Conversation'
                AND m.role = 'assistant'
                AND (
                    c.title LIKE %s
                    OR m.content LIKE %s
                )
                ORDER BY m.creation DESC
                LIMIT %s
            """, (like_pattern, like_pattern, retrieval_docs), as_dict=True)
        else:
            # User thường CHỈ xem conversations của chính họ
            like_pattern = f"%{query}%"
            similar_conversations = frappe.db.sql("""
                SELECT 
                    c.name,
                    c.title,
                    m.content,
                    m.role,
                    m.creation
                FROM `tabAI Conversation` c
                JOIN `tabAI Message` m ON m.parent = c.name
                WHERE m.parenttype = 'AI Conversation'
                AND m.role = 'assistant'
                AND c.owner = %s
                AND (
                    c.title LIKE %s
                    OR m.content LIKE %s
                )
                ORDER BY m.creation DESC
                LIMIT %s
            """, (current_user, like_pattern, like_pattern, retrieval_docs), as_dict=True)

        results = []
        for conv in similar_conversations:
            results.append({
                'content': conv.content,
                'source': 'previous_conversations',
                'similarity': 0.8,
                'metadata': {
                    'conversation_id': conv.name,
                    'conversation_title': conv.title,
                    'timestamp': conv.creation
                }
            })

        frappe.logger().info(f"retrieve_from_database: {len(results)} conversations for user {current_user}")
        return results

    except Exception as e:
        frappe.log_error(f"retrieve_from_database failed: {str(e)}")
        return []


def retrieve_from_api(query: str, user: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search trong API documentation - Public, tất cả users đều có thể xem"""
    try:
        current_user = user if user else frappe.session.user
        
        # API docs là public, nhưng Guest có thể bị giới hạn
        if current_user == "Guest":
            frappe.logger().info("Guest user accessing API docs - limited access")
            return []
        
        api_results = [
            {
                'content': f"API documentation related to: {query}",
                'source': 'frappe_docs_api',
                'similarity': 0.7,
                'metadata': {
                    'api_endpoint': 'https://frappeframework.com/docs',
                    'query': query
                }
            }
        ]
        return api_results
    except Exception as e:
        frappe.log_error(f"retrieve_from_api failed: {str(e)}")
        return []

