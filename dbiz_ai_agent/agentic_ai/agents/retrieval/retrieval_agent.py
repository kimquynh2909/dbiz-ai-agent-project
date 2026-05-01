"""
Retrieval Agent - Thực thi retrieval với các query và phương thức đã được plan
"""
import frappe
from typing import Dict, Any, List
from ..base_agent import BaseAgent
from ..state import AgentState
from dbiz_ai_agent.api.auth import Get_Chatbot_Config
from dbiz_ai_agent.agentic_ai.tools.retrieval_tools import RetrievalTools
import json


class RetrievalAgent(BaseAgent):
    """
    Agent thực thi retrieval dựa trên plan từ QueryGenerator.
    
    Nhiệm vụ:
    - Nhận retrieval plan từ state (queries, strategy, max_results)
    - Thực thi tìm kiếm theo từng query với phương thức phù hợp
    - Điều phối execution (sequential hoặc parallel)
    - Tổng hợp và rank kết quả
    - Lưu retrieved documents vào state
    """
    
    def __init__(self):
        config = Get_Chatbot_Config()
        super().__init__(config.assistant_name, config.description)
        
        # Initialize retrieval tools
        self.retrieval_tools = RetrievalTools()
    
    async def retrieve(self, state: AgentState) -> AgentState:
        """
        Thực thi retrieval từ plan trong state và cập nhật kết quả vào state
        
        Args:
            state: AgentState chứa retrieval_plan với:
                - queries: list of query objects
                - retrieval_strategy: "sequential" hoặc "parallel"
                - max_results: số lượng kết quả tối đa
        
        Returns:
            AgentState đã được cập nhật với:
            - retrieval_success: bool
            - retrieved_documents: list of documents
            - retrieval_metadata: dict với thông tin về quá trình retrieval
        """
        start_time = self.create_agent_timer()
        try:
            retrieval_plan = state.get("retrieval_plan")
            if not retrieval_plan:
                raise ValueError("retrieval_plan not found in state")
            
            queries = retrieval_plan.get("queries", [])
            if not queries:
                raise ValueError("No queries found in retrieval plan")
            
            strategy = retrieval_plan.get("strategy", "sequential")
            max_results = retrieval_plan.get("max_results", 5)
            
            # TODO: Implement actual retrieval logic
            # For now, return placeholder structure
            
            all_results = []
            retrieval_metadata = {
                "total_queries": len(queries),
                "strategy_used": strategy,
                "queries_executed": [],
                "execution_times": {}
            }
            
            # Execute queries based on strategy
            if strategy == "parallel":
                # TODO: Implement parallel execution
                # For now, fall back to sequential
                all_results = await self._execute_sequential(queries, max_results, retrieval_metadata)
            else:
                all_results = await self._execute_sequential(queries, max_results, retrieval_metadata)
            
            # Rank and deduplicate results
            ranked_results = self._rank_results(all_results, max_results)
            
            # Extract image metadata from retrieved documents
            image_metadata = self._extract_image_metadata(ranked_results)
            
            # Update state
            state.update_context(
                retrieval_success=True,
                retrieved_documents=ranked_results,
                retrieval_metadata=retrieval_metadata,
                num_retrieved=len(ranked_results),
                image_metadata=image_metadata
            )
            
            # Log kết quả agent
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="RetrievalAgent",
                user_query=state.user_question or "Unknown",
                result_data={
                    "retrieved_documents": ranked_results,
                    "num_retrieved": len(ranked_results),
                    "retrieval_metadata": retrieval_metadata
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=True,
                message_id=state.get("message_id")
            )
            
            return state
            
        except Exception as e:
            frappe.log_error(f"Retrieval error: {str(e)}")
            state.update_context(
                retrieval_success=False,
                retrieval_error=str(e),
                retrieved_documents=[],
                num_retrieved=0
            )
            
            # Log lỗi
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="RetrievalAgent",
                user_query=state.user_question or "Unknown",
                result_data={
                    "retrieval_error": str(e),
                    "num_retrieved": 0
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=str(e),
                message_id=state.get("message_id")
            )
            return state
    
    async def _execute_sequential(
        self, 
        queries: List[Dict], 
        max_results: int,
        metadata: Dict
    ) -> List[Dict]:
        """
        Thực thi các query tuần tự
        
        Args:
            queries: List of query objects từ retrieval plan
            max_results: Số lượng kết quả tối đa cho mỗi query
            metadata: Dict để lưu thông tin execution
        
        Returns:
            List of retrieved documents
        """
        all_results = []
        
        for query_obj in queries:
            # Khởi tạo giá trị mặc định
            query_text = ""
            method = "embedding"
            target = "documents"
            filters = {}
            
            try:
                # Xử lý cả trường hợp query_obj là string hoặc dict
                if isinstance(query_obj, str):
                    query_text = query_obj
                elif isinstance(query_obj, dict):
                    query_text = query_obj.get("query_text", "")
                    method = query_obj.get("method", "embedding")
                    target = query_obj.get("target", "documents")
                    filters = query_obj.get("filters", {})
                else:
                    query_text = str(query_obj)
                
                if not query_text:
                    continue
                
                # TODO: Implement actual retrieval based on method
                # For now, log the query and return placeholder
                frappe.logger().info(f"Executing query: {query_text} with method: {method}")
                
                results = await self._execute_single_query(
                    query_text=query_text,
                    method=method,
                    target=target,
                    filters=filters,
                    max_results=max_results
                )
                
                all_results.extend(results)
                
                metadata["queries_executed"].append({
                    "query": query_text,
                    "method": method,
                    "results_count": len(results)
                })
                
            except Exception as e:
                frappe.log_error(f"Error executing query {query_text}: {str(e)}")
                metadata["queries_executed"].append({
                    "query": query_text,
                    "method": method,
                    "error": str(e)
                })
                continue
        
        return all_results
    
    async def _execute_single_query(
        self,
        query_text: str,
        method: str,
        target: str,
        filters: Dict,
        max_results: int
    ) -> List[Dict]:
        """
        Thực thi một query đơn lẻ
        
        Args:
            query_text: Câu query
            method: Phương thức retrieval (embedding/api/hybrid)
            target: Loại dữ liệu cần tìm
            filters: Các bộ lọc
            max_results: Số lượng kết quả tối đa
        
        Returns:
            List of documents
        """
        if method == "embedding":
            return await self._embedding_search(query_text, target, filters, max_results)
        elif method == "api":
            return await self._api_search(query_text, target, filters, max_results)
        elif method == "hybrid":
            embedding_results = await self._embedding_search(query_text, target, filters, max_results)
            api_results = await self._api_search(query_text, target, filters, max_results)
            return self._merge_results(embedding_results, api_results)
        else:
            frappe.logger().warning(f"Unknown retrieval method: {method}, falling back to embedding")
            return await self._embedding_search(query_text, target, filters, max_results)
    
    async def _embedding_search(
        self, 
        query: str, 
        target: str, 
        filters: Dict, 
        max_results: int
    ) -> List[Dict]:
        """
        Thực hiện embedding-based semantic search sử dụng RetrievalTools
        """
        try:
            frappe.logger().info(f"Embedding search: {query} (target: {target})")
            
            # Sử dụng search_documents từ RetrievalTools
            # Note: RetrievalTools.get_tools() trả về function_tool decorators
            # Ta cần gọi trực tiếp helper function
            from dbiz_ai_agent.agentic_ai.utils import retrieval_helpers as helpers
            from dbiz_ai_agent.agentic_ai.agents.base_agent import current_request_user
            
            # Lấy user từ context
            user = current_request_user.get()
            
            # Gọi retrieve_documents
            results = helpers.retrieve_documents(
                query,
                self.retrieval_tools._openai_client,
                self.retrieval_tools._settings,
                max_results,
                similarity_threshold=self.retrieval_tools.similarity_threshold,
                user=user
            )
            
            if not results:
                frappe.logger().info(f"No embedding results found for: {query}")
                return []
            
            # Chuyển đổi format về chuẩn
            formatted_results = []
            for r in results:
                src = r.get("source") or r.get("metadata", {}).get("document", "Unknown")
                doc = {
                    "content": r.get("content", ""),
                    "text": r.get("content", ""),
                    "source": src,
                    "title": src,
                    "score": r.get("similarity", 0.0),
                    "method": "embedding"
                }
                
                # Thêm images nếu có
                if r.get("images"):
                    doc["images"] = r["images"]
                
                formatted_results.append(doc)
            
            frappe.logger().info(f"Found {len(formatted_results)} embedding results")
            return formatted_results
            
        except Exception as e:
            frappe.log_error(f"Embedding search error: {str(e)}")
            return []
    
    async def _api_search(
        self, 
        query: str, 
        target: str, 
        filters: Dict, 
        max_results: int
    ) -> List[Dict]:
        """
        Thực hiện API search cho dữ liệu có cấu trúc
        """
        try:
            frappe.logger().info(f"API search: {query} (target: {target})")
            results: List[Dict] = []

            # TODO: Implement structured API search based on target
            # Ví dụ: Nếu target = "products", query Frappe DocType "Item"
            # Nếu target = "orders", query "Sales Order", etc.
            #
            # Sau khi implement, gán kết quả vào `results`.

            # Placeholder implementation cho target "documents":
            # vẫn dùng embedding search như một dạng semantic search chính.
            if target == "documents":
                results = await self._embedding_search(query, target, filters, max_results)
            else:
                frappe.logger().info(f"API search not implemented for target: {target}")

            # Nếu API search (hoặc logic trên) không trả về kết quả,
            # luôn fallback sang embedding search để ưu tiên tìm trong tài liệu.
            if not results:
                frappe.logger().info(
                    f"API search returned no results for target={target}, "
                    "falling back to embedding search"
                )
                results = await self._embedding_search(query, target, filters, max_results)

            return results
            
        except Exception as e:
            frappe.log_error(f"API search error: {str(e)}")
            return []
    
    def _merge_results(self, results1: List[Dict], results2: List[Dict]) -> List[Dict]:
        """
        Merge và deduplicate kết quả từ nhiều nguồn
        """
        # TODO: Implement intelligent merging with deduplication
        # For now, simple concatenation
        return results1 + results2
    
    def _rank_results(self, results: List[Dict], max_results: int) -> List[Dict]:
        """
        Rank, deduplicate và giới hạn số lượng kết quả
        
        Args:
            results: List of all retrieved documents
            max_results: Maximum number of results to return
        
        Returns:
            Top-ranked deduplicated results
        """
        if not results:
            return []
        
        # Add default scores if not present
        for i, doc in enumerate(results):
            if "score" not in doc:
                doc["score"] = 1.0 / (i + 1)
        
        # Deduplicate based on source + content
        seen = {}
        deduplicated = []
        
        for doc in results:
            # Tạo key duy nhất từ source và một phần content
            source = doc.get("source") or doc.get("title", "")
            content_preview = doc.get("content", "")[:100] if doc.get("content") else ""
            
            # Nếu có document_id, ưu tiên dùng nó
            if isinstance(source, dict) and source.get("document_id"):
                key = source["document_id"]
            elif isinstance(source, str):
                key = f"{source}_{content_preview}"
            else:
                key = f"{str(source)}_{content_preview}"
            
            # Chỉ giữ lại document có score cao nhất cho mỗi key
            if key not in seen or doc.get("score", 0) > seen[key].get("score", 0):
                seen[key] = doc
        
        # Lấy các documents đã deduplicate
        deduplicated = list(seen.values())
        
        # Sort by score (descending)
        sorted_results = sorted(deduplicated, key=lambda x: x.get("score", 0), reverse=True)
        
        # Return top max_results
        return sorted_results[:max_results]
    
    def _extract_image_metadata(self, documents: List[Dict]) -> Dict[str, Dict]:
        """
        Extract image metadata từ retrieved documents để synthesis agent có thể
        thay thế [[IMAGE::ID]] placeholders thành Markdown images
        
        Args:
            documents: List of retrieved documents
        
        Returns:
            Dict mapping image ID -> {"description": str, "file": str}
        """
        image_metadata = {}
        
        for doc in documents:
            # Nếu document có images field
            if "images" in doc and isinstance(doc["images"], list):
                for img in doc["images"]:
                    if isinstance(img, dict):
                        img_id = img.get("id") or img.get("name")
                        if img_id:
                            image_metadata[img_id] = {
                                "description": img.get("description") or img.get("title") or f"Image {img_id}",
                                "file": img.get("image_url") or img.get("file") or ""
                            }
        
        frappe.logger().info(f"[RetrievalAgent] Extracted {len(image_metadata)} image metadata entries")
        return image_metadata
