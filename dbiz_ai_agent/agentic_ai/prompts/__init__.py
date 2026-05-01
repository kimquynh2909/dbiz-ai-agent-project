"""
Prompts Module - Centralized prompt templates for AI agents

Provides prompt templates for:
- Intent analysis
- Query generation
- Synthesis and response generation
"""
from .intent_prompts import INTENT_ANALYZER_PROMPT
from .synthesis_prompts import RESPONSE_GENERATOR_PROMPT, CLARIFICATION_PROMPT
from .query_prompts import QUERY_GENERATOR_PROMPT

__all__ = [
    'INTENT_ANALYZER_PROMPT',
    'RESPONSE_GENERATOR_PROMPT',
    'CLARIFICATION_PROMPT',
    'QUERY_GENERATOR_PROMPT',
]

