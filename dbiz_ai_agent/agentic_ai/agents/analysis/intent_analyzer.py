"""
Intent Analyzer Agent - Phân tích ý định người dùng và quyết định có cần retrieval
"""
import json
import frappe
from typing import Dict, Any
from ..base_agent import BaseAgent
from ..state import AgentState
from dbiz_ai_agent.api.auth import Get_Chatbot_Config


class IntentAnalyzer(BaseAgent):
    """
    Agent phân tích ý định người dùng.
    
    Nhiệm vụ:
    - Phân tích câu hỏi/yêu cầu của người dùng
    - Quyết định có cần tìm kiếm tài liệu hay không
    - Phân loại loại query (specific_info, general_knowledge, procedural, data_lookup)
    - Đánh giá độ tin cậy của phân tích
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
Bạn là chuyên gia phân tích ý định và đánh giá chất lượng thông tin.

NHIỆM VỤ KÉP:

A. PHÂN TÍCH Ý ĐỊNH (khi chưa có retrieval results):
Quyết định có cần tìm kiếm tài liệu hay không.

CẦN TÌM KIẾM TÀI LIỆU KHI:
- Người dùng hỏi về thông tin cụ thể (sản phẩm, dịch vụ, quy trình, chính sách)
- Cần tra cứu dữ liệu, số liệu, báo cáo
- Hỏi về hướng dẫn, tài liệu kỹ thuật
- Yêu cầu thông tin từ nguồn dữ liệu nội bộ

KHÔNG CẦN TÌM KIẾM TÀI LIỆU KHI:
- Chào hỏi, trò chuyện thông thường
- Hỏi về khả năng của chatbot
- Câu hỏi chung chung không yêu cầu dữ liệu cụ thể
- Toán học đơn giản, logic, suy luận

ĐÁNH GIÁ ĐỘ RÕ RÀNG CỦA CÂU HỎI (query_clarity_score):
- 1.0: Câu hỏi rất cụ thể, rõ ràng (ví dụ: "Giá của gói DBIZ ERP Standard là bao nhiêu?")
- 0.8: Câu hỏi khá rõ nhưng thiếu vài chi tiết nhỏ
- 0.6: Câu hỏi tương đối rõ nhưng có thể hiểu theo nhiều cách
- 0.4: Câu hỏi mơ hồ, thiếu ngữ cảnh quan trọng (ví dụ: "Cái đó giá bao nhiêu?")
- 0.2: Câu hỏi rất mơ hồ, không thể hiểu được ý định (ví dụ: "Cho tôi thông tin")
- 0.0: Câu hỏi hoàn toàn không rõ ràng

LƯU Ý: Nếu query_clarity_score < 0.6, nên yêu cầu làm rõ TRƯỚC KHI tìm kiếm

B. ĐÁNH GIÁ KẾT QUẢ (khi đã có retrieval results):
Đánh giá xem kết quả tìm kiếm có đủ chất lượng để trả lời câu hỏi không.

TIÊU CHÍ ĐÁNH GIÁ:
1. Relevance: Kết quả có liên quan đến câu hỏi không?
2. Completeness: Kết quả có đủ thông tin để trả lời không?
3. Quality: Chất lượng nội dung (độ chi tiết, rõ ràng)

QUY TẮC QUYẾT ĐỊNH:
- PASS: Kết quả đủ tốt, có thể tạo câu trả lời ngay
- FALLBACK: Không đủ kết quả, trả lời dựa trên kiến thức chung

OUTPUT FORMAT (JSON):

Nếu chưa có retrieval results (intent analysis):
{
    "mode": "intent",
    "need_retrieval": true/false,
    "confidence": 0.0-1.0,
    "reason": "Lý do quyết định",
    "query_type": "specific_info|general_knowledge|procedural|data_lookup|none",
    "query_clarity_score": 0.0-1.0,
    "clarity_reason": "Câu hỏi rõ ràng / mơ hồ vì sao"
}

Nếu đã có retrieval results (evaluation):
{
    "mode": "evaluation",
    "decision": "pass|fallback",
    "confidence": 0.0-1.0,
    "reason": "Lý do quyết định",
    "relevance_score": 0.0-1.0,
    "completeness_score": 0.0-1.0
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
            frappe.log_error(f"Failed to initialize IntentAnalyzer: {str(e)}")
            return None
    
    async def analyze(self, state: AgentState) -> AgentState:
        """
        Phân tích ý định từ state và cập nhật kết quả vào state
        
        Args:
            state: AgentState chứa user_question và conversation_history
        
        Returns:
            AgentState đã được cập nhật với kết quả phân tích:
            - intent_analysis_success: bool
            - intent_data: dict với need_retrieval, confidence, reason, query_type
            - need_retrieval: bool
            - query_type: str
            - intent_confidence: float
        """
        start_time = self.create_agent_timer()
        try:
            if not self._AGENT:
                raise RuntimeError("IntentAnalyzer agent not initialized")
            
            user_query = state.user_question
            if not user_query:
                raise ValueError("user_question not found in state")
            
            # Chuẩn bị context từ state
            conversation_history = state.get("conversation_history", [])
            context = f"User query: {user_query}"
            
            if conversation_history:
                recent_context = "\n".join([
                    f"User: {msg.get('content', '')}" if msg.get('role') == 'user' 
                    else f"Assistant: {msg.get('content', '')}"
                    for msg in conversation_history[-3:]  # Lấy 3 tin nhắn gần nhất
                ])
                context = f"Recent conversation:\n{recent_context}\n\nCurrent query: {user_query}"
            
            # Phân tích ý định
            result = await self.Run_Agent(self._AGENT, context)
            
            if not result or not result.final_output:
                raise RuntimeError("Intent analysis failed - no output")
            
            # Parse JSON response
            intent_data = json.loads(result.final_output)
            
            # Validate intent_data structure
            if "need_retrieval" not in intent_data:
                raise ValueError("Invalid intent_data: missing 'need_retrieval' field")
            
            # Lưu kết quả vào state
            state.update_context(
                intent_analysis_success=True,
                intent_data=intent_data,
                need_retrieval=intent_data.get("need_retrieval", False),
                query_type=intent_data.get("query_type"),
                intent_confidence=intent_data.get("confidence", 0.0)
            )
            
            # Log kết quả agent
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="IntentAnalyzer",
                user_query=user_query,
                result_data={
                    "intent_data": intent_data,
                    "need_retrieval": intent_data.get("need_retrieval"),
                    "query_type": intent_data.get("query_type"),
                    "confidence": intent_data.get("confidence")
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=True,
                message_id=state.get("message_id")
            )
            
            return state
            
        except json.JSONDecodeError as e:
            frappe.log_error(f"Failed to parse intent analysis result: {str(e)}")
            # Fallback: assume need retrieval for safety
            fallback_data = {
                "need_retrieval": True,
                "confidence": 0.5,
                "reason": "Failed to analyze, assuming need retrieval",
                "query_type": "general_knowledge"
            }
            state.update_context(
                intent_analysis_success=False,
                intent_error=str(e),
                intent_data=fallback_data,
                need_retrieval=True,
                query_type="general_knowledge",
                intent_confidence=0.5
            )
            
            # Log lỗi
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="IntentAnalyzer",
                user_query=state.user_question or "Unknown",
                result_data=fallback_data,
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=f"JSON Parse Error: {str(e)}",
                message_id=state.get("message_id")
            )
            return state
            
        except Exception as e:
            frappe.log_error(f"Intent analysis error: {str(e)}")
            fallback_data = {
                "need_retrieval": False,
                "confidence": 0.0,
                "reason": f"Analysis failed: {str(e)}",
                "query_type": "none"
            }
            state.update_context(
                intent_analysis_success=False,
                intent_error=str(e),
                intent_data=fallback_data,
                need_retrieval=False,
                query_type="none",
                intent_confidence=0.0
            )
            
            # Log lỗi
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="IntentAnalyzer",
                user_query=state.user_question or "Unknown",
                result_data=fallback_data,
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=str(e),
                message_id=state.get("message_id")
            )
            return state
    
    async def evaluate_results(self, state: AgentState) -> AgentState:
        """
        Đánh giá chất lượng retrieved documents (Critic role)
        
        Args:
            state: AgentState chứa retrieved_documents, user_question
        
        Returns:
            AgentState đã được cập nhật với:
            - evaluation_success: bool
            - evaluation_decision: "pass|clarify|fallback"
            - should_clarify: bool
            - can_generate_response: bool
        """
        start_time = self.create_agent_timer()
        try:
            if not self._AGENT:
                raise RuntimeError("IntentAnalyzer agent not initialized")
            
            user_query = state.user_question
            retrieved_docs = state.get("retrieved_documents", [])
            num_retrieved = state.get("num_retrieved", 0)
            
            # Chuẩn bị context cho evaluation
            context = f"""
MODE: evaluation

User query: {user_query}

Retrieved documents: {num_retrieved} documents found

Documents summary:
"""
            
            for i, doc in enumerate(retrieved_docs[:5], 1):  # Limit to top 5 for context
                doc_content = doc.get("content", doc.get("text", "N/A"))
                doc_score = doc.get("score", "N/A")
                context += f"\n{i}. Score: {doc_score}\n   Content: {doc_content[:200]}...\n"
            
            if num_retrieved == 0:
                context += "\n(No documents retrieved)"
            
            context += "\nTask: Evaluate if these results are sufficient to answer the user's question. If the question is too vague, suggest CLARIFY."
            
            # Đánh giá
            result = await self.Run_Agent(self._AGENT, context)
            
            if not result or not result.final_output:
                raise RuntimeError("Evaluation failed - no output")
            
            # Parse JSON response
            evaluation_result = json.loads(result.final_output)
            
            decision = evaluation_result.get("decision", "fallback")

            # Nếu đã có tài liệu (num_retrieved > 0) thì không nên
            # cho phép decision = "fallback". Trong trường hợp model
            # vẫn trả "fallback", ưu tiên xử lý như "pass" để synthesis
            # sử dụng các nguồn đã tìm được thay vì bỏ qua.
            if num_retrieved > 0 and decision == "fallback":
                frappe.logger().info(
                    "[IntentAnalyzer-Critic] Overriding decision 'fallback' "
                    "to 'pass' because documents were retrieved"
                )
                decision = "pass"
                evaluation_result["decision"] = "pass"
            can_generate = (decision in ["pass", "fallback"])
            
            # Lưu kết quả vào state
            state.update_context(
                evaluation_success=True,
                evaluation_result=evaluation_result,
                evaluation_decision=decision,
                can_generate_response=can_generate,
                evaluation_confidence=evaluation_result.get("confidence", 0.0)
            )
            
            # Log kết quả
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="IntentAnalyzer-Critic",
                user_query=user_query,
                result_data={
                    "decision": decision,
                    "relevance_score": evaluation_result.get("relevance_score"),
                    "completeness_score": evaluation_result.get("completeness_score"),
                    "confidence": evaluation_result.get("confidence")
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=True,
                message_id=state.get("message_id")
            )
            
            return state
            
        except json.JSONDecodeError as e:
            frappe.log_error(f"Failed to parse evaluation result: {str(e)}")
            state.update_context(
                evaluation_success=False,
                evaluation_error=str(e),
                evaluation_decision="fallback",
                can_generate_response=True
            )
            return state
            
        except Exception as e:
            frappe.log_error(f"Evaluation error: {str(e)}")
            state.update_context(
                evaluation_success=False,
                evaluation_error=str(e),
                evaluation_decision="fallback",
                can_generate_response=True
            )
            return state
