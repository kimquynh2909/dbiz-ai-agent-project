"""
Base Extractor - Main document extraction dispatcher
"""
import os
from typing import Dict, Any, Optional

from .pdf_extractor import extract_from_pdf
from .word_extractor import extract_from_word
from .text_extractor import extract_from_text


def extract_document(document_path: str, document_name: Optional[str] = None, settings=None) -> Dict[str, Any]:
    """
    Dispatch document extraction by type (PDF, Word, Image, Text).
    
    Args:
        document_path: Path to the document file
        document_name: AI Document name for tracking
        settings: AI Agent Settings (optional)
    
    Returns:
        Dictionary containing:
        - text: Extracted text content
        - images: List of extracted images with metadata
        - document_id: Document identifier
    """
    ext = os.path.splitext(document_path)[1].lower()
    
    # PDF documents
    if ext == ".pdf":
        return extract_from_pdf(document_path, document_name=document_name)
    
    # Text-based files
    if ext in [".txt", ".md", ".log", ".csv", ".json", ".yaml", ".yml"]:
        return extract_from_text(document_path, document_name=document_name)
    
    # Word documents and similar formats
    if ext in [".doc", ".docx", ".docm", ".dot", ".dotx", ".dotm", ".odt", ".ott", ".sxw", ".rtf", ".wps"]:
        return extract_from_word(document_path, document_name=document_name)
    
    # Unsupported format
    text_content = "Định dạng chưa được hỗ trợ bởi bộ đọc văn bản hiện tại"
    return {
        "text": text_content,
        "images": [],
        "document_id": document_name,
    }

