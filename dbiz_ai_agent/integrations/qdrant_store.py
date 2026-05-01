"""Wrapper utilities for interacting with Qdrant vector database."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import frappe


from qdrant_client import QdrantClient  # type: ignore[import]
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse  # type: ignore[import]
from qdrant_client.http.models import (  # type: ignore[import]
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    OptimizersConfigDiff,
    PointStruct,
    VectorParams,
)

def _get_base_url() -> str:
    url = frappe.conf.get("qdrant_url") if hasattr(frappe, "conf") else None
    if not url:
        url = os.getenv("QDRANT_URL")
    if not url:
        # fallback to localhost for developer environments
        url = "http://localhost:6333"
    return url


def _get_collection_name() -> str:
    collection = frappe.conf.get("qdrant_collection") if hasattr(frappe, "conf") else None
    if not collection:
        collection = os.getenv("QDRANT_COLLECTION")
    return collection or "ai_documents"


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    if QdrantClient is None:
        raise ImportError("qdrant-client is not installed")

    url = _get_base_url()
    client = QdrantClient(url=url, timeout=30.0)
    return client


def ensure_collection(vector_size: int, distance: str = "cosine") -> str:
    """Ensure the default collection exists and matches vector size."""
    collection_name = _get_collection_name()
    client = get_client()

    distance_enum = Distance.COSINE
    if distance.lower() == "dot":
        distance_enum = Distance.DOT
    elif distance.lower() in {"euclid", "l2", "euclidean"}:
        distance_enum = Distance.EUCLID

    def _extract_size(info: Any) -> Optional[int]:
        if not info:
            return None

        try:
            return info.config.params.vectors.size  # type: ignore[attr-defined]
        except AttributeError:
            pass

        try:
            return (
                info.get("config", {})
                .get("params", {})
                .get("vectors", {})
                .get("size")
            )
        except AttributeError:
            return None

    try:
        try:
            info = client.get_collection(collection_name)
            current_vector_size = _extract_size(info)
            if current_vector_size is None or current_vector_size != vector_size:
                client.recreate_collection(
                    collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=distance_enum),
                )
        except UnexpectedResponse:
            client.recreate_collection(
                collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance_enum),
            )
    except ResponseHandlingException as err:
        raise RuntimeError(
            f"Failed to connect to Qdrant at {_get_base_url()}. "
            "Please ensure the Qdrant service is running and the URL configuration is correct."
        ) from err

    return collection_name


def upsert_embeddings(
    embeddings: List[List[float]],
    payloads: List[Dict[str, Any]],
    ids: List[str],
    *,
    distance: str = "cosine",
) -> None:
    if not embeddings:
        return
    if len(embeddings) != len(payloads) or len(ids) != len(embeddings):
        raise ValueError("Embeddings, payloads and ids must have the same length")

    vector_size = len(embeddings[0])
    collection_name = ensure_collection(vector_size, distance=distance)
    client = get_client()

    points = [
        PointStruct(id=idx, vector=vec, payload=payload)
        for idx, vec, payload in zip(ids, embeddings, payloads)
    ]
    client.upsert(collection_name=collection_name, points=points)


def build_filter(conditions: Dict[str, Any]) -> Optional[Filter]:
    """Build a simple AND filter from conditions dict."""
    if not conditions:
        return None
    if Filter is None:
        return None

    must_conditions: List[Any] = []
    for key, value in conditions.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            must_conditions.append(FieldCondition(key=key, match=MatchAny(any=list(value))))
        else:
            must_conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

    if not must_conditions:
        return None
    return Filter(must=must_conditions)


def build_permission_filter(
    user: str,
    user_roles: Optional[List[str]] = None,
) -> Optional[Filter]:
    """
    Build a Qdrant filter for permission-based document access.
    
    Permission Logic (OR):
    1. Document is Public (is_public = True)
    2. Document is Internal with no role restriction (has_role_restriction = False)
    3. User is the document owner
    4. User is the document uploader
    5. User has a role that matches roles_allowed
    
    Args:
        user: Current user email
        user_roles: List of AI Role names the user has
    
    Returns:
        Qdrant Filter object or None for unrestricted access
    """
    if not user:
        return None
    
    # Administrator: no filter needed
    if user == "Administrator":
        return None
    
    # Guest: only public documents
    if user == "Guest":
        return Filter(
            must=[FieldCondition(key="is_public", match=MatchValue(value=True))]
        )
    
    # Logged-in user: complex OR filter
    should_conditions: List[Any] = []
    
    # Condition 1: Document is Public
    should_conditions.append(
        FieldCondition(key="is_public", match=MatchValue(value=True))
    )
    
    # Condition 2: Internal document with no role restriction
    # (All logged-in users can access)
    should_conditions.append(
        FieldCondition(key="has_role_restriction", match=MatchValue(value=False))
    )
    
    # Condition 3: User is the document owner
    should_conditions.append(
        FieldCondition(key="owner", match=MatchValue(value=user))
    )
    
    # Condition 4: User is the document uploader
    should_conditions.append(
        FieldCondition(key="uploaded_by", match=MatchValue(value=user))
    )
    
    # Condition 5: User has a matching role in roles_allowed
    if user_roles:
        # MatchAny checks if roles_allowed array contains ANY of user_roles
        should_conditions.append(
            FieldCondition(key="roles_allowed", match=MatchAny(any=user_roles))
        )
    
    # Return OR filter (should = OR logic)
    return Filter(should=should_conditions)


def search(
    query_vector: List[float],
    *,
    top_k: int = 10,
    conditions: Optional[Dict[str, Any]] = None,
    qdrant_filter: Optional[Filter] = None,
):
    """
    Search for similar vectors in Qdrant.
    
    Args:
        query_vector: The query embedding vector
        top_k: Maximum number of results to return
        conditions: Simple conditions dict (will be converted to AND filter)
        qdrant_filter: Pre-built Qdrant Filter object (takes precedence over conditions)
    
    Returns:
        List of search results with payload
    """
    collection_name = _get_collection_name()
    client = get_client()
    
    # Use provided filter or build from conditions
    if qdrant_filter is None:
        qdrant_filter = build_filter(conditions or {})
    
    search_fn = getattr(client, "search", None)
    if callable(search_fn):
        return search_fn(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )

    # Fallback for client versions without .search (e.g., 1.16.0)
    result = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        query_filter=qdrant_filter,
        with_payload=True,
    )

    # query_points returns a QueryResponse; expose the points list for compatibility
    try:
        points = getattr(result, "points", None)
        if points is not None:
            return points
    except Exception:
        pass
    return result


def delete_document(document_id: str) -> None:
    if not document_id:
        return
    client = get_client()
    collection_name = _get_collection_name()
    condition = FieldCondition(key="document_id", match=MatchValue(value=document_id))
    client.delete(
        collection_name=collection_name,
        points_selector=Filter(must=[condition]),
    )


def document_has_vectors(document_id: str) -> bool:
    if not document_id:
        return False
    client = get_client()
    collection_name = _get_collection_name()
    condition = FieldCondition(key="document_id", match=MatchValue(value=document_id))
    response = client.count(
        collection_name=collection_name,
        count_filter=Filter(must=[condition]),
        exact=True,
    )
    print(f"[QDRANT CHECK] Count response: {response}")
    return bool(getattr(response, "count", 0))


def get_collection_name() -> str:
    """Return the configured Qdrant collection name."""
    return _get_collection_name()
