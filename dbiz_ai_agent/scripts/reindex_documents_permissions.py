"""
Script to re-index existing documents with permission fields in Qdrant.

Run this script after updating to the Permission Denormalization approach.
This will update all existing documents in Qdrant to include the new permission
fields (is_public, has_role_restriction, owner, uploaded_by).

Usage:
    bench execute dbiz_ai_agent.scripts.reindex_documents_permissions.run
    
    Or with options:
    bench execute dbiz_ai_agent.scripts.reindex_documents_permissions.run --args "['--dry-run']"
"""
import frappe
from typing import List, Dict, Any, Optional


def get_all_ai_documents() -> List[Dict[str, Any]]:
    """Get all AI Documents with their metadata."""
    docs = frappe.get_all(
        "AI Document",
        fields=[
            "name", "title", "category", "access_level", 
            "uploaded_by", "owner", "tags", "departments_allowed",
            "file_attachment", "vector_collection"
        ]
    )
    return docs


def get_document_roles(document_name: str) -> List[str]:
    """Get roles_allowed for a document from child table."""
    roles = []
    try:
        doc = frappe.get_doc("AI Document", document_name)
        if getattr(doc, "roles_allowed", None):
            roles = [getattr(role, "role_name", "") for role in doc.roles_allowed]
            roles = [role for role in roles if role]
    except Exception:
        pass
    return roles


def build_permission_payload(doc: Dict[str, Any], roles: List[str]) -> Dict[str, Any]:
    """Build permission-related payload fields for Qdrant."""
    access_level = doc.get("access_level") or "Internal"
    is_public = access_level == "Public"
    has_role_restriction = len(roles) > 0
    
    return {
        "is_public": is_public,
        "has_role_restriction": has_role_restriction,
        "owner": doc.get("owner") or "",
        "uploaded_by": doc.get("uploaded_by") or "",
        "access_level": access_level,
        "roles_allowed": roles,
    }


def update_qdrant_payloads(document_id: str, permission_payload: Dict[str, Any], dry_run: bool = False):
    """Update existing Qdrant points for a document with permission fields."""
    from dbiz_ai_agent.integrations import qdrant_store
    from qdrant_client.http.models import FieldCondition, Filter, MatchValue
    
    if dry_run:
        print(f"  [DRY RUN] Would update document: {document_id}")
        print(f"    Permission payload: {permission_payload}")
        return 0
    
    try:
        client = qdrant_store.get_client()
        collection_name = qdrant_store.get_collection_name()
        
        # Find all points for this document
        condition = FieldCondition(key="document_id", match=MatchValue(value=document_id))
        
        # Scroll through all points for this document
        scroll_result = client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(must=[condition]),
            limit=1000,  # Should be enough for most documents
            with_payload=True,
            with_vectors=False,
        )
        
        points, _ = scroll_result
        
        if not points:
            print(f"  [SKIP] No vectors found for document: {document_id}")
            return 0
        
        # Update each point's payload
        point_ids = [point.id for point in points]
        
        # Use set_payload to add/update specific fields
        client.set_payload(
            collection_name=collection_name,
            payload=permission_payload,
            points=point_ids,
        )
        
        print(f"  [OK] Updated {len(point_ids)} vectors for: {document_id}")
        return len(point_ids)
        
    except Exception as e:
        print(f"  [ERROR] Failed to update {document_id}: {str(e)}")
        frappe.log_error(f"Failed to update Qdrant payloads for {document_id}: {str(e)}")
        return 0


def run(*args):
    """Main entry point for the re-indexing script."""
    dry_run = "--dry-run" in args if args else False
    
    print("\n" + "=" * 60)
    print("Re-indexing Documents with Permission Fields")
    print("=" * 60)
    
    if dry_run:
        print("\n[MODE] DRY RUN - No changes will be made\n")
    else:
        print("\n[MODE] LIVE - Changes will be applied to Qdrant\n")
    
    # Get all AI Documents
    documents = get_all_ai_documents()
    print(f"Found {len(documents)} AI Documents to process\n")
    
    total_vectors = 0
    processed_docs = 0
    failed_docs = 0
    
    for doc in documents:
        document_id = doc.get("name")
        print(f"Processing: {document_id}")
        
        # Get roles for this document
        roles = get_document_roles(document_id)
        
        # Build permission payload
        permission_payload = build_permission_payload(doc, roles)
        
        # Update Qdrant
        vectors_updated = update_qdrant_payloads(document_id, permission_payload, dry_run)
        
        if vectors_updated > 0:
            total_vectors += vectors_updated
            processed_docs += 1
        else:
            failed_docs += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total documents:  {len(documents)}")
    print(f"Processed:        {processed_docs}")
    print(f"Skipped/Failed:   {failed_docs}")
    print(f"Total vectors:    {total_vectors}")
    print("=" * 60 + "\n")
    
    if dry_run:
        print("This was a dry run. Run without --dry-run to apply changes.")
    
    return {
        "total_documents": len(documents),
        "processed": processed_docs,
        "failed": failed_docs,
        "total_vectors": total_vectors,
    }


def reindex_single_document(document_name: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Re-index a single document with permission fields.
    
    Usage:
        from dbiz_ai_agent.scripts.reindex_documents_permissions import reindex_single_document
        reindex_single_document("AI-DOC-00001")
    """
    print(f"\nRe-indexing single document: {document_name}")
    
    try:
        doc = frappe.get_doc("AI Document", document_name)
        doc_dict = {
            "name": doc.name,
            "access_level": doc.access_level,
            "owner": doc.owner,
            "uploaded_by": doc.uploaded_by,
        }
        roles = get_document_roles(document_name)
        permission_payload = build_permission_payload(doc_dict, roles)
        
        vectors_updated = update_qdrant_payloads(document_name, permission_payload, dry_run)
        
        return {
            "document": document_name,
            "vectors_updated": vectors_updated,
            "permission_payload": permission_payload,
        }
    except Exception as e:
        frappe.log_error(f"Failed to re-index document {document_name}: {str(e)}")
        return {
            "document": document_name,
            "error": str(e),
        }


# =============================================================================
# Document Event Hooks
# =============================================================================

def on_document_update(doc, method):
    """
    Hook triggered when AI Document is updated.
    Syncs permission fields to Qdrant automatically.
    
    This is called via doc_events in hooks.py:
        "AI Document": {
            "on_update": "dbiz_ai_agent.scripts.reindex_documents_permissions.on_document_update"
        }
    """
    try:
        # Only sync if document has vectors in Qdrant
        from dbiz_ai_agent.integrations import qdrant_store
        print(f"[PERMISSION SYNC] Checking document: {doc.name}")
        if not qdrant_store.document_has_vectors(doc.name):

            return
        # Build permission payload from current document state
        roles = get_document_roles(doc.name)
        doc_dict = {
            "name": doc.name,
            "access_level": getattr(doc, "access_level", "Internal"),
            "owner": doc.owner,
            "uploaded_by": getattr(doc, "uploaded_by", ""),
        }
        permission_payload = build_permission_payload(doc_dict, roles)
        
        # Update Qdrant payloads
        update_qdrant_payloads(doc.name, permission_payload, dry_run=False)
        
        frappe.logger().info(f"[PERMISSION SYNC] Updated Qdrant permissions for: {doc.name}")
        
    except Exception as e:
        # Log error but don't block document save
        frappe.log_error(
            f"Failed to sync permissions to Qdrant for {doc.name}: {str(e)}",
            "Permission Sync Error"
        )

