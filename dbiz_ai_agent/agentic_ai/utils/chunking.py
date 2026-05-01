"""
Chunking Module - Text chunking utilities
"""
import hashlib
from typing import List, Dict, Any


def create_chunks(text: str, chunk_size: int, chunk_overlap: int) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
    
    Returns:
        List of chunk dictionaries containing:
        - text: The chunk text
        - size: Character count
        - hash: MD5 hash of the chunk
    """
    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1
        
        if current_size >= chunk_size:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "size": len(chunk_text),
                "hash": hashlib.md5(chunk_text.encode()).hexdigest()
            })
            # Keep overlap words for next chunk
            overlap_words = current_chunk[-chunk_overlap//10:]
            current_chunk = overlap_words
            current_size = sum(len(word) + 1 for word in overlap_words)
    
    # Add remaining chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append({
            "text": chunk_text,
            "size": len(chunk_text),
            "hash": hashlib.md5(chunk_text.encode()).hexdigest()
        })
    
    return chunks

