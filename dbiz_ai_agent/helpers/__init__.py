"""
Helpers Module - General utility functions for the app

Contains:
- chat_utility: Chat streaming and realtime utilities
- contact_sync: Contact synchronization utilities
- cors: CORS handling
- create_sample_data: Sample data creation scripts
- sync_doctypes: DocType synchronization utilities

Note: This module is for general app utilities, NOT AI-specific utilities.
For AI-specific utilities, use agentic_ai.utils instead.
"""
from .chat_utility import (
    collect_stream_chunks,
    run_agent_stream,
    build_stream_summary,
    publish_stream_completion,
    publish_image_update,
    merge_images,
)
from .contact_sync import sync_ai_role_contacts
from .cors import handle_cors
from .create_sample_data import create_sample_data
from .sync_doctypes import sync_new_doctypes

__all__ = [
    # Chat utilities
    'collect_stream_chunks',
    'run_agent_stream',
    'build_stream_summary',
    'publish_stream_completion',
    'publish_image_update',
    'merge_images',
    
    # Contact sync
    'sync_ai_role_contacts',
    
    # CORS
    'handle_cors',
    
    # Sample data
    'create_sample_data',
    
    # DocType sync
    'sync_new_doctypes',
]

