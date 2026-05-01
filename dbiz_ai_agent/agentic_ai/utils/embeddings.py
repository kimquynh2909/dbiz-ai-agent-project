"""
Embeddings Module - OpenAI embedding generation utilities
"""
import frappe
import requests
from typing import List, Optional


def _get_setting(settings, name, default=None):
    """Helper to read a named setting with a default when settings may be None."""
    return getattr(settings, name, default) if settings else default


def get_embeddings(texts: List[str], settings=None) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI API.
    
    Args:
        texts: List of text strings to embed
        settings: AI Agent Settings object (optional)
    
    Returns:
        List of embedding vectors
    """
    try:
        headers = {
            "Authorization": f"Bearer {_get_setting(settings, 'openai_api_key', '')}",
            "Content-Type": "application/json"
        }
        embeddings = []
        batch_size = 10
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            data = {
                "model": _get_setting(settings, 'embedding_model', 'text-embedding-3-small'),
                "input": batch
            }
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                for item in result["data"]:
                    embeddings.append(item["embedding"])
            else:
                raise Exception(f"Embeddings API error: {response.status_code}")
        
        return embeddings
    except Exception as e:
        frappe.log_error(f"Embeddings generation failed: {str(e)}")
        raise


def get_query_embedding(openai_client, settings, query: str) -> Optional[List[float]]:
    """
    Generate embedding for a single query using OpenAI client.
    
    Args:
        openai_client: OpenAI client instance
        settings: AI Agent Settings object
        query: Query string to embed
    
    Returns:
        Embedding vector or None if failed
    """
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

