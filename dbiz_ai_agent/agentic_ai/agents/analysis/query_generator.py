"""
Query Generator Agent - Tạo query tối ưu và điều hướng retrieval
"""
import json
import frappe
from typing import Dict, Any, List
from ..base_agent import BaseAgent
from ..state import AgentState
from dbiz_ai_agent.api.auth import Get_Chatbot_Config


class QueryGenerator(BaseAgent):
    """
    Agent tạo query tìm kiếm và điều hướng retrieval.
    
    Nhiệm vụ:
    - Phân tích câu hỏi người dùng và intent analysis
    - Tạo các câu query tối ưu cho retrieval
    - Quyết định phương thức retrieval cho mỗi query (embedding/api/hybrid)
    - Xác định chiến lược thực thi (sequential/parallel)
    """
    
    _AGENT = None
    
    def __init__(self):
        config = Get_Chatbot_Config()
        super().__init__(config.assistant_name, config.description)
        
        if not self._AGENT:
            self._AGENT = self._init_agent()
    
    def _init_agent(self):
        """Khởi tạo agent với instructions và JSON response format"""
        instructions = """
Bạn là chuyên gia tạo query tìm kiếm và điều hướng retrieval.

NHIỆM VỤ:
1. Phân tích câu hỏi người dùng
2. Tạo các câu query tìm kiếm tối ưu
3. Quyết định phương thức retrieval cho mỗi query

PHƯƠNG THỨC RETRIEVAL:
- "embedding": Tìm kiếm semantic trong vector database (cho câu hỏi mở, khái niệm, tài liệu)
- "api": Gọi API lấy dữ liệu cụ thể (cho tra cứu chính xác: ID, mã, tên cụ thể)
- "hybrid": Kết hợp cả hai (cho query phức tạp CẦN CẢ tài liệu VÀ dữ liệu có cấu trúc)

QUY TẮC TẠO QUERY:
1. **ƯU TIÊN 1 QUERY DUY NHẤT** - Chỉ tạo nhiều queries khi thực sự cần thiết (các khía cạnh HOÀN TOÀN khác nhau)
2. **KHÔNG TẠO queries song ngữ** - Chỉ dùng ngôn ngữ của câu hỏi gốc
3. **KHÔNG TẠO queries trùng ý nghĩa** - Mỗi query phải có mục đích riêng biệt
4. Với API: chỉ dùng khi CẦN tra cứu theo ID/mã cụ thể
5. Với embedding: dùng cho tìm kiếm tài liệu, hướng dẫn, thông tin chung

VÍ DỤ TỐT:
- Câu hỏi: "Hướng dẫn thanh toán DBIZ"
  → 1 query: "Hướng dẫn thanh toán DBIZ" (embedding)
  
- Câu hỏi: "Giá iPhone 15 và so sánh với Samsung S24"
  → 2 queries: "Giá iPhone 15" (embedding), "Giá Samsung S24" (embedding)

VÍ DỤ TỒI (TRÁNH):
- ❌ Tạo query tiếng Việt + tiếng Anh cho cùng 1 ý
- ❌ Tạo query embedding + api cho cùng 1 câu hỏi đơn giản
- ❌ Tạo nhiều queries với từ ngữ khác nhau nhưng cùng ý nghĩa

OUTPUT FORMAT (JSON):
{
    "queries": [
        {
            "query_text": "Câu query cụ thể",
            "method": "embedding|api",
            "priority": 1-10,
            "target": "documents|products|orders|customers|general",
            "filters": {}
        }
    ],
    "strategy": "sequential",
    "max_results": 3,
    "reasoning": "Giải thích chiến lược retrieval"
}
"""
        try:
            agent = self.Create_Agent(
                instructions=instructions,
                tools=[],
                response_format={"type": "json_object"}
            )
            return agent
        except Exception as e:
            frappe.log_error(f"Failed to initialize QueryGenerator: {str(e)}")
            return None
    
    async def generate_queries(self, state: AgentState) -> AgentState:
        """
        Tạo retrieval plan từ state và cập nhật kết quả vào state
        
        Args:
            state: AgentState chứa user_question, intent_data, conversation_history
        
        Returns:
            AgentState đã được cập nhật với retrieval plan:
            - retrieval_plan_success: bool
            - retrieval_plan: dict với queries, strategy, max_results, reasoning
            - queries: list of query objects
            - retrieval_strategy: str (sequential/parallel)
            - max_results: int
        """
        start_time = self.create_agent_timer()
        try:
            if not self._AGENT:
                raise RuntimeError("QueryGenerator agent not initialized")
            
            user_query = state.user_question
            if not user_query:
                raise ValueError("user_question not found in state")
            
            intent_data = state.get("intent_data", {})
            conversation_history = state.get("conversation_history", [])
            
            # Chuẩn bị context cho query generator
            context = f"""
User query: {user_query}

Intent analysis:
- Query type: {intent_data.get('query_type', 'unknown')}
- Confidence: {intent_data.get('confidence', 0.0)}
- Reason: {intent_data.get('reason', 'N/A')}

Task: Generate optimized retrieval queries and routing strategy.
"""
            
            if conversation_history:
                recent_context = "\n".join([
                    f"- {msg.get('role')}: {msg.get('content', '')[:100]}..."
                    for msg in conversation_history[-3:]
                ])
                context += f"\n\nRecent context:\n{recent_context}"
            
            # Generate retrieval plan
            result = await self.Run_Agent(self._AGENT, context)
            
            if not result or not result.final_output:
                raise RuntimeError("Query generation failed - no output")
            
            # Parse JSON response
            plan_data = json.loads(result.final_output)
            
            # Validate plan_data structure
            if "queries" not in plan_data:
                raise ValueError("Invalid plan_data: missing 'queries' field")
            
            # Lưu kết quả vào state
            state.update_context(
                retrieval_plan_success=True,
                retrieval_plan=plan_data,
                queries=plan_data.get("queries", []),
                retrieval_strategy=plan_data.get("strategy", "sequential"),
                max_results=plan_data.get("max_results", 5)
            )
            
            # Log kết quả agent
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="QueryGenerator",
                user_query=user_query,
                result_data={
                    "retrieval_plan": plan_data,
                    "num_queries": len(plan_data.get("queries", [])),
                    "strategy": plan_data.get("strategy"),
                    "max_results": plan_data.get("max_results"),
                    "reasoning": plan_data.get("reasoning")
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=True,
                message_id=state.get("message_id")
            )
            
            return state
            
        except json.JSONDecodeError as e:
            frappe.log_error(f"Failed to parse retrieval plan: {str(e)}")
            # Fallback: create simple embedding search
            user_query = state.user_question
            fallback_plan = {
                "queries": [
                    {
                        "query_text": user_query,
                        "method": "embedding",
                        "priority": 5,
                        "target": "documents",
                        "filters": {}
                    }
                ],
                "strategy": "sequential",
                "max_results": 5,
                "reasoning": "Fallback to simple embedding search due to parse error"
            }
            state.update_context(
                retrieval_plan_success=False,
                retrieval_plan_error=str(e),
                retrieval_plan=fallback_plan,
                queries=fallback_plan["queries"],
                retrieval_strategy="sequential",
                max_results=5
            )
            
            # Log lỗi
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="QueryGenerator",
                user_query=user_query or "Unknown",
                result_data=fallback_plan,
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=f"JSON Parse Error: {str(e)}",
                message_id=state.get("message_id")
            )
            return state
            
        except Exception as e:
            frappe.log_error(f"Query generation error: {str(e)}")
            # Fallback with minimal plan
            user_query = state.user_question
            fallback_plan = {
                "queries": [
                    {
                        "query_text": user_query,
                        "method": "embedding",
                        "priority": 5,
                        "target": "documents",
                        "filters": {}
                    }
                ],
                "strategy": "sequential",
                "max_results": 5,
                "reasoning": f"Fallback due to error: {str(e)}"
            }
            state.update_context(
                retrieval_plan_success=False,
                retrieval_plan_error=str(e),
                retrieval_plan=fallback_plan,
                queries=fallback_plan["queries"],
                retrieval_strategy="sequential",
                max_results=5
            )
            
            # Log lỗi
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="QueryGenerator",
                user_query=user_query or "Unknown",
                result_data=fallback_plan,
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=str(e),
                message_id=state.get("message_id")
            )
            return state
