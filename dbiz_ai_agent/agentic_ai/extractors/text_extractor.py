"""
Text Extractor - Extract content from text-based files
"""
from typing import Dict, Any, Optional


def extract_from_text(text_path: str, document_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract text from text-based files (txt, md, json, yaml, etc.).
    
    Args:
        text_path: Path to the text file
        document_name: AI Document name for tracking
    
    Returns:
        Dictionary containing:
        - text: File content
        - images: Empty list (text files don't contain images)
        - document_id: Document identifier
    """
    with open(text_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    return {
        "text": content,
        "images": [],
        "document_id": document_name
    }

