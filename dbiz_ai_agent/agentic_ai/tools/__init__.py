"""
Tools Module
trả về các tool của agent
"""
from .retrieval_tools import RetrievalTools
from .document_tools import DocumentProcessingTools
from .sales_order_tools import SalesOrderTools

_ALL_TOOLS_CACHE = None
_RetrievalTools = None
_DocumentProcessingTools = None
_SalesOrderTools = None

def get_all_tools():
    """Lấy tất cả các công cụ hiện có"""
    global _ALL_TOOLS_CACHE
    global _RetrievalTools
    global _DocumentProcessingTools
    global _SalesOrderTools
    if _ALL_TOOLS_CACHE is not None:
        return _ALL_TOOLS_CACHE
    _RetrievalTools = RetrievalTools()
    _DocumentProcessingTools = DocumentProcessingTools()
    _SalesOrderTools = SalesOrderTools()
    all_tools = []
    all_tools.extend(_RetrievalTools.get_tools())
    all_tools.extend(_SalesOrderTools.get_tools())
    # all_tools.extend(_DocumentProcessingTools.get_tools())
    _ALL_TOOLS_CACHE = all_tools
    return all_tools

__all__ = [
    'get_all_tools',
    'RetrievalTools',
    'DocumentProcessingTools',
    'SalesOrderTools'
]
