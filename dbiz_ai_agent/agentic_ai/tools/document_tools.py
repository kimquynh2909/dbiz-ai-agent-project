import frappe
from typing import Dict, Any
from dbiz_ai_agent.api.settings import get_ai_agent_settings
from dbiz_ai_agent.agentic_ai.extractors import extract_document
from dbiz_ai_agent.agentic_ai.utils import (
    get_embeddings,
    store_in_vector_db,
    create_chunks,
    generate_ai_metadata,
)
class DocumentProcessingTools:
    """Tools for processing documents: extraction, chunking, embedding, and storage."""

    def __init__(self):
        """Initialize with default chunk configuration."""
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self._settings = None
        self._initialize()

    def _initialize(self):
        """Load agent settings and default chunk sizes."""
        settings, chunk_size, chunk_overlap = get_ai_agent_settings()
        self._settings = settings
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _console_log(self, message: str, log_type: str = "Info") -> None:
        """Store a small message to the `Console Log` doctype for developer debugging.

        NOTE: This creates a `Console Log` document and should be used sparingly to avoid log spam.
        """
        try:
            log_doc = frappe.get_doc({
                "doctype": "Console Log",
                "script": str(message),
                "type": log_type,
            })
            log_doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to write Console Log entry: {str(e)}")

    def process_document(self, document_path: str, document_name: str = None) -> Dict[str, Any]:
        """Full pipeline: extract, enhance with images, chunk, embed, and store vectors."""
        extracted = extract_document(
            document_path,
            document_name,
            settings=self._settings,
        )
        text_content = extracted.get("text", "")
        extracted_images = extracted.get("images", []) or []
        
        metadata = generate_ai_metadata(text_content, settings=self._settings)
        chunks = create_chunks(text_content, self.chunk_size, self.chunk_overlap)
        embeddings = get_embeddings([chunk["text"] for chunk in chunks], settings=self._settings)

        store_in_vector_db(
            chunks,
            embeddings,
            document_path,
            settings=self._settings,
            document_name=document_name,
        )

        chunk_ids = [chunk["hash"] for chunk in chunks]

        return {
            "chunks_count": len(chunks),
            "chunks": chunks,
            "embeddings": embeddings,
            "chunk_ids": chunk_ids,
            "full_text": text_content,
            "document_path": document_path,
            "images_extracted": len(extracted_images),
            "image_ids": extracted_images,
            "ai_description": metadata.get("description", ""),
            "ai_keywords": metadata.get("keywords", ""),
        }
