"""
Vector Store Module - Qdrant vector database operations
"""
import frappe
import hashlib
from typing import List, Dict, Any, Optional
from dbiz_ai_agent.integrations import qdrant_store


def _split_csv(value: Optional[str]) -> List[str]:
    """Split comma-separated string into list."""
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item and item.strip()]


def fetch_document_metadata(document_name: Optional[str]) -> Dict[str, Any]:
    """
    Fetch metadata for a document from AI Document doctype.
    
    Args:
        document_name: Name of the AI Document
    
    Returns:
        Dictionary containing document metadata including permission fields
        for Qdrant-level filtering (Permission Denormalization)
    """
    if not document_name:
        return {}
    try:
        doc = frappe.get_doc("AI Document", document_name)
    except Exception:
        return {}
    
    roles = []
    try:
        if getattr(doc, "roles_allowed", None):
            roles = [getattr(role, "role_name", "") for role in doc.roles_allowed]
            roles = [role for role in roles if role]
    except Exception:
        roles = []
    
    departments = _split_csv(getattr(doc, "departments_allowed", ""))
    tags = _split_csv(getattr(doc, "tags", ""))
    
    # Permission fields for Qdrant-level filtering
    access_level = getattr(doc, "access_level", "") or "Internal"
    is_public = access_level == "Public"
    has_role_restriction = len(roles) > 0
    owner = getattr(doc, "owner", "") or ""
    uploaded_by = getattr(doc, "uploaded_by", "") or ""
    
    return {
        "document_id": doc.name,
        "title": getattr(doc, "title", ""),
        "category": getattr(doc, "category", ""),
        "access_level": access_level,
        "tags": tags,
        "roles_allowed": roles,
        "departments_allowed": departments,
        "vector_collection": getattr(doc, "vector_collection", ""),
        "uploaded_by": uploaded_by,
        "upload_date": getattr(doc, "upload_date", None),
        # Permission Denormalization fields
        "is_public": is_public,
        "has_role_restriction": has_role_restriction,
        "owner": owner,
    }


def _store_in_qdrant(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    document_path: str,
    document_name: Optional[str],
):
    """
    Internal function to store embeddings in Qdrant.
    
    Args:
        chunks: List of chunk dictionaries with text and metadata
        embeddings: List of embedding vectors
        document_path: Path to the source document
        document_name: Name of the AI Document
    """
    if not embeddings or not chunks:
        return
    
    metadata = fetch_document_metadata(document_name)
    document_id = metadata.get("document_id") or document_name or document_path
    
    chunk_payloads: List[Dict[str, Any]] = []
    chunk_ids: List[str] = []
    
    for idx, chunk in enumerate(chunks):
        chunk_hash = chunk.get("hash") or hashlib.md5((chunk.get("text") or "").encode()).hexdigest()
        payload = {
            "content": chunk.get("text", ""),
            "chunk_size": chunk.get("size"),
            "chunk_hash": chunk_hash,
            "chunk_index": idx,
            "document_path": document_path,
            "document_id": document_id,
            "document_title": metadata.get("title"),
            "category": metadata.get("category"),
            "access_level": metadata.get("access_level"),
            "tags": metadata.get("tags"),
            "roles_allowed": metadata.get("roles_allowed"),
            "departments_allowed": metadata.get("departments_allowed"),
            "vector_collection": metadata.get("vector_collection"),
            # Permission Denormalization fields for Qdrant-level filtering
            "is_public": metadata.get("is_public", False),
            "has_role_restriction": metadata.get("has_role_restriction", False),
            "owner": metadata.get("owner", ""),
            "uploaded_by": metadata.get("uploaded_by", ""),
        }
        chunk_payloads.append(payload)
        chunk_ids.append(f"{chunk_hash}")
    
    try:
        qdrant_store.delete_document(document_id)
    except Exception as err:
        frappe.log_error(
            "Failed to delete old Qdrant points",
            message=f"Document: {document_id}\nError: {err}",
        )
    
    qdrant_store.upsert_embeddings(embeddings, chunk_payloads, chunk_ids)


def store_in_vector_db(
    chunks: List[Dict],
    embeddings: List[List[float]],
    document_path: str,
    *,
    settings=None,
    document_name: Optional[str] = None,
):
    """
    Store document chunks and embeddings in vector database.
    
    Args:
        chunks: List of chunk dictionaries
        embeddings: List of embedding vectors
        document_path: Path to the source document
        settings: AI Agent Settings (optional, not used currently)
        document_name: Name of the AI Document
    """
    try:
        _store_in_qdrant(chunks, embeddings, document_path, document_name)
    except Exception as err:
        frappe.log_error(
            "Không thể lưu dữ liệu vào Qdrant",
            message=f"Document: {document_name or document_path}\nError: {err}",
        )
        raise

