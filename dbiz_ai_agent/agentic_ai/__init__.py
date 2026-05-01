# AI Agents Module
# Re-export key classes for convenience/backward-compat

# Core agents
from .agents.base_agent import BaseAgent  # noqa: F401
from .agents.state import AgentState, current_agent_state, get_state, set_state, clear_state  # noqa: F401
from .agents.orchestration import SmartOrchestrator  # noqa: F401

# Utility modules - New modular structure
from .utils import (  # noqa: F401
    get_embeddings,
    get_query_embedding,
    store_in_vector_db,
    fetch_document_metadata,
    create_chunks,
    save_image,
    generate_ai_metadata,
    retrieve_documents,
    retrieve_from_database,
    retrieve_from_api,
)

# Document extractors - New modular structure
from .extractors import (  # noqa: F401
    extract_document,
    extract_from_pdf,
    extract_from_word,
    extract_from_text,
)

# Prompts - Centralized prompt templates
from .prompts import (  # noqa: F401
    INTENT_ANALYZER_PROMPT,
    RESPONSE_GENERATOR_PROMPT,
    CLARIFICATION_PROMPT,
    QUERY_GENERATOR_PROMPT,
)
