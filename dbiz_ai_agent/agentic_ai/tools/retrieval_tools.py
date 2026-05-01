"""
Retrieval Tools
Contains retrieval tools for searching through multiple sources
"""
import frappe
import json
from typing import List, Dict, Any, Optional
from dbiz_ai_agent.agentic_ai.utils import retrieval_helpers as helpers
from dbiz_ai_agent.agentic_ai.agents.base_agent import current_request_user

class RetrievalTools:
    """Provides retrieval tools for searching multiple data sources"""
    
    def __init__(self):
        self.retrieval_docs = 3
        self.similarity_threshold = 0.0
        self._openai_client = None
        self._settings = None
        self._initialize()

    def _initialize(self):
        """Initialize settings and OpenAI client"""
        try:
            settings, retrieval_docs, openai_client = helpers.get_retrieval_config()
            self._settings = settings
            self.retrieval_docs = retrieval_docs
            self._openai_client = openai_client
            threshold = getattr(settings, "retrieval_similarity_threshold", None) if settings else None
            if threshold is None:
                # Mặc định: không áp dụng ngưỡng similarity (0.0)
                threshold = 0.0
            try:
                threshold = float(threshold)
            except (TypeError, ValueError):
                threshold = 0.0
            self.similarity_threshold = max(0.0, min(1.0, threshold))
        except Exception as e:
            frappe.log_error(f"RetrievalTools initialization failed: {str(e)}")
    
    def get_tools(self) -> List:
        """
        Get all retrieval tools that can be used by an agent
        
        Returns:
            List of function_tool decorated functions
        """
        from agents import function_tool
        
        # Reference to self for use in closures
        tools_instance = self
        
        @function_tool
        def search_documents(query: str) -> str:
            """🔍 TOOL BẮT BUỘC - Tìm kiếm thông tin từ tài liệu nội bộ.
            
            ⚠️ BẮT BUỘC gọi tool này TRƯỚC KHI trả lời các câu hỏi về:
            - Hướng dẫn sử dụng, quy trình, chính sách
            - Thông tin sản phẩm, dịch vụ, giá cả, thanh toán
            - Tài liệu kỹ thuật, tutorial, documentation
            - Bất kỳ thông tin cụ thể về công ty/tổ chức
            
            Args:
                query (str): Câu truy vấn tìm kiếm (tiếng Việt hoặc tiếng Anh)
                
            Returns:
                str: JSON array chứa kết quả tìm kiếm với content, source, similarity
                     Trả về "No documents found." nếu không tìm thấy
            
            ✅ Ví dụ query tốt: "hướng dẫn thanh toán phần mềm", "quy trình đăng ký dịch vụ"
            """
            # Lấy user từ context variable
            user = current_request_user.get()
            print(  f"🔍 search_documents called by user {user}")
            results = helpers.retrieve_documents(
                query,
                tools_instance._openai_client,
                tools_instance._settings,
                tools_instance.retrieval_docs,
                similarity_threshold=tools_instance.similarity_threshold,
                user=user,
            )
            if not results:
                return "No documents found."
            
            formatted_results = []
            for r in results[:3]:
                src = r.get("source") or r.get("metadata", {}).get("document")
                formatted_result = {
                    "content": r["content"],
                    "source": src,
                    "similarity": round(r["similarity"], 3)
                }

                if r.get("images"):
                    formatted_result["images"] = r["images"]

                formatted_results.append(formatted_result)
            
            frappe.logger().info(f"✅ Returning {len(formatted_results)} formatted results")
            return json.dumps(formatted_results, indent=2, ensure_ascii=False)
        
        @function_tool
        def search_database(query: str) -> str:
            """Sử dụng để tra cứu lịch sử hội thoại/ghi chú nội bộ liên quan tới truy vấn hiện tại."""
            results = helpers.retrieve_from_database(query, tools_instance.retrieval_docs)
            if not results:
                return "No database results found."
            
            formatted_results = []
            for r in results[:3]:
                formatted_results.append({
                    "content": r["content"][:300] + "..." if len(r["content"]) > 300 else r["content"],
                    "source": r["source"],
                    "similarity": round(r.get("similarity", 0), 3)
                })
            
            return json.dumps(formatted_results, indent=2, ensure_ascii=False)
        
        @function_tool
        def search_api(query: str) -> str:
            """Dùng cuối cùng để khảo sát API bên ngoài khi các nguồn nội bộ không có dữ liệu phù hợp."""
            results = helpers.retrieve_from_api(query)
            if not results:
                return "No API results found."
            
            formatted_results = []
            for r in results[:3]:
                formatted_results.append({
                    "content": r["content"][:300] + "..." if len(r["content"]) > 300 else r["content"],
                    "source": r["source"]
                })
            
            return json.dumps(formatted_results, indent=2, ensure_ascii=False)
        
        return [search_documents]
    
__all__ = ["RetrievalTools"]
