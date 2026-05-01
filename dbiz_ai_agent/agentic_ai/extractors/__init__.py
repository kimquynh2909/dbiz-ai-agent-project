"""
Extractors Module - Document content extraction

Provides extractors for different document types:
- PDF documents
- Word documents (doc, docx, etc.)
- Text files (txt, md, json, etc.)
"""
from .base_extractor import extract_document
from .pdf_extractor import extract_from_pdf
from .word_extractor import extract_from_word
from .text_extractor import extract_from_text

__all__ = [
    'extract_document',
    'extract_from_pdf',
    'extract_from_word',
    'extract_from_text',
]

