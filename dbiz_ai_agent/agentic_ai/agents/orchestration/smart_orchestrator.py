"""
Smart Orchestrator - Điều phối luồng xử lý giữa các agents
"""
import frappe
import time
import random
from typing import Dict, Any, List, Optional
from ..base_agent import BaseAgent
from ..state import AgentState, get_state, set_state
from ..analysis import IntentAnalyzer, QueryGenerator
from ..retrieval import RetrievalAgent
from ..synthesis import SynthesisAgent
from dbiz_ai_agent.api.auth import Get_Chatbot_Config


class SmartOrchestrator(BaseAgent):
    """
    Orchestrator điều phối các agents theo flow:
    1. IntentAnalyzer - Phân tích ý định và quyết định cần retrieval không
    2. QueryGenerator - Tạo queries và routing strategy (nếu cần retrieval)
    3. RetrievalAgent - Thực thi retrieval (nếu cần)
    4. SynthesisAgent - Đánh giá kết quả và tạo response
    
    Orchestrator chỉ điều phối, không chứa business logic.
    """
    
    def __init__(self):
        config = Get_Chatbot_Config()
        super().__init__(config.assistant_name, config.description)
        
        # Initialize specialized agents
        self.intent_analyzer = IntentAnalyzer()
        self.query_generator = QueryGenerator()
        self.retrieval_agent = RetrievalAgent()
        self.synthesis_agent = SynthesisAgent()
    
    async def _prepare_state(
        self,
        user_query: str,
        conversation_id: str = None,
        conversation_history: List[Dict] = None
    ) -> AgentState:
        """
        Chuẩn bị state và thực hiện intent, query generation, retrieval
        Trả về state đã sẵn sàng cho synthesis
        """
        # Generate unique message_id for this user query
        timestamp = int(time.time() * 1000)  # milliseconds
        random_suffix = random.randint(1000, 9999)
        message_id = f"MSG-{timestamp}-{random_suffix}"
        
        # Initialize state
        state = AgentState(
            conversation_id=conversation_id,
            user_question=user_query
        )
        state.update_context(
            conversation_history=conversation_history or [],
            orchestration_started=True,
            message_id=message_id  # Lưu message_id để tất cả agents dùng chung
        )
        
        # Set state to context
        set_state(state)
        
        # STEP 1: Intent Analysis
        frappe.logger().info(f"[Orchestrator] Step 1: Analyzing intent for query: {user_query}")
        try:
            state = await self.intent_analyzer.analyze(state)
        except Exception as e:
            frappe.log_error(f"[Orchestrator] Intent analysis exception: {str(e)}")
            state.update_context(
                intent_analysis_success=False,
                orchestration_error=f"Intent analysis exception: {str(e)}"
            )
            return state
        
        if not state.get("intent_analysis_success"):
            frappe.log_error("[Orchestrator] Intent analysis failed")
            state.update_context(
                orchestration_success=False,
                orchestration_error="Intent analysis failed"
            )
            return state
        
        # STEP 1.5: Check query clarity ngay sau intent analysis
        intent_data = state.get("intent_data", {})
        query_clarity_score = intent_data.get("query_clarity_score", 1.0)
        
        # Nếu câu hỏi không rõ ràng (clarity < 0.6), vẫn retrieval để lấy gợi ý
        if query_clarity_score < 0.6:
            frappe.logger().info(f"[Orchestrator] Query unclear (clarity={query_clarity_score}), will retrieve for suggestions")
            
            # Vẫn thực hiện retrieval với query gốc để lấy tài liệu liên quan
            # Dùng thông tin này để gợi ý cho người dùng
            state.update_context(
                need_clarification_with_suggestions=True,  # Flag để biết cần gợi ý
                clarification_reason=intent_data.get("reason", "Câu hỏi chưa đủ rõ ràng")
            )
            
            # Thực hiện retrieval đơn giản với query gốc
            frappe.logger().info("[Orchestrator] Retrieving documents for clarification suggestions")
            try:
                # Tạo retrieval plan đơn giản với đúng cấu trúc mà retrieval_agent mong đợi
                state.update_context(
                    retrieval_plan={
                        "queries": [user_query],  # Dùng query gốc
                        "strategy": "sequential",
                        "max_results": 5
                    },
                    retrieval_plan_success=True
                )
                
                # Execute retrieval
                state = await self.retrieval_agent.retrieve(state)
                
            except Exception as e:
                frappe.log_error(f"[Orchestrator] Retrieval for suggestions failed: {str(e)}")
                state.update_context(
                    retrieved_documents=[],
                    num_retrieved=0
                )
            
            # Set flags để synthesis biết cần tạo clarification với suggestions
            state.update_context(
                should_clarify=True,
                evaluation_decision="clarify",
                can_generate_response=False
            )
            return state
        
        # STEP 2: Check if retrieval is needed
        need_retrieval = state.get("need_retrieval", False)
        frappe.logger().info(f"[Orchestrator] Need retrieval: {need_retrieval}")
        
        if not need_retrieval:
            # Skip retrieval, go straight to response generation
            frappe.logger().info("[Orchestrator] Skipping retrieval, will generate direct response")
            state.update_context(
                skip_retrieval=True,
                retrieved_documents=[],
                num_retrieved=0,
                evaluation_decision="pass",  # Skip evaluation, go straight to synthesis
                can_generate_response=True
            )
            # KHÔNG return ở đây - phải tiếp tục để synthesis agent tạo response
            return state
        
        # STEP 3: Generate Retrieval Plan
        frappe.logger().info("[Orchestrator] Step 2: Generating retrieval plan")
        try:
            state = await self.query_generator.generate_queries(state)
        except Exception as e:
            frappe.log_error(f"[Orchestrator] Query generation exception: {str(e)}")
            state.update_context(
                retrieval_plan_success=False,
                orchestration_error=f"Query generation exception: {str(e)}"
            )
            return state
        
        if not state.get("retrieval_plan_success"):
            frappe.log_error("[Orchestrator] Retrieval planning failed")
            state.update_context(
                orchestration_success=False,
                orchestration_error="Retrieval planning failed",
                retrieved_documents=[],
                num_retrieved=0
            )
            return state
        
        # STEP 4: Execute Retrieval
        frappe.logger().info("[Orchestrator] Step 3: Executing retrieval")
        state = await self.retrieval_agent.retrieve(state)
        
        if not state.get("retrieval_success"):
            frappe.log_error("[Orchestrator] Retrieval execution failed")
            # Continue with empty results
            state.update_context(
                retrieved_documents=[],
                num_retrieved=0
            )
        
        # STEP 5: Evaluate results (IntentAnalyzer as Critic)
        frappe.logger().info("[Orchestrator] Step 4: Evaluating retrieval results")
        state = await self.intent_analyzer.evaluate_results(state)
        
        return state
    
    async def orchestrate(
        self, 
        user_query: str, 
        conversation_id: str = None,
        conversation_history: List[Dict] = None,
        stream: bool = False
    ):
        """
        Điều phối toàn bộ luồng xử lý với State management
        
        Flow:
        1. Initialize State
        2. Intent Analysis -> check need_retrieval
        3. Query Generation (if needed) -> create retrieval plan
        4. Retrieval (if needed) -> get documents
        5. Synthesis -> evaluate + generate response
        
        Args:
            user_query: Câu hỏi người dùng
            conversation_id: ID cuộc hội thoại
            conversation_history: Lịch sử hội thoại
            stream: Nếu True, trả về generator để stream response
        
        Returns:
            AgentState chứa final_response (nếu stream=False)
            Generator để stream response (nếu stream=True)
        """
        try:
            # Chuẩn bị state (intent, query, retrieval, evaluation)
            state = await self._prepare_state(user_query, conversation_id, conversation_history)
            
            # STEP 6: Synthesis (Generate Response hoặc Clarification)
            frappe.logger().info("[Orchestrator] Step 5: Synthesizing response")
            
            if stream:
                # Stream mode: return async generator
                return self._orchestrate_stream(state)
            else:
                # Non-stream mode: wait for complete response
                state = await self.synthesis_agent.synthesize(state, stream=False)
                
                # Mark orchestration complete
                state.update_context(
                    orchestration_success=True,
                    orchestration_complete=True
                )
                
                frappe.logger().info("[Orchestrator] Orchestration complete")
                
                return state
            
        except Exception as e:
            frappe.log_error(f"[Orchestrator] Orchestration error: {str(e)}")
            state = AgentState(
                conversation_id=conversation_id,
                user_question=user_query
            )
            state.update_context(
                orchestration_success=False,
                orchestration_error=str(e),
                orchestration_complete=True,
                final_response=f"Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi của bạn: {str(e)}. Vui lòng thử lại."
            )
            
            return state
        finally:
            # Keep state in context for logging/debugging
            try:
                set_state(state)
            except:
                pass
    
    async def _orchestrate_stream(self, state: AgentState):
        """
        Generator cho streaming mode
        
        Yields:
            str: Từng chunk của response
        """
        try:
            # Synthesize với stream=True - trả về generator
            generator = await self.synthesis_agent.synthesize(state, stream=True)
            
            # Stream từng chunk (có thể là response bình thường hoặc clarification question)
            async for chunk in generator:
                yield chunk
            
            # Sau khi stream xong, mark complete và log
            state.update_context(
                orchestration_success=True,
                orchestration_complete=True
            )
            
            frappe.logger().info("[Orchestrator] Orchestration complete (streamed)")
            
        except Exception as e:
            frappe.log_error(f"[Orchestrator] Stream error: {str(e)}")
            yield f"Xin lỗi, có lỗi xảy ra: {str(e)}"
    
    def get_orchestration_result(self, state: AgentState) -> Dict[str, Any]:
        """
        Chuyển đổi State thành dict để trả về hoặc log
        
        Args:
            state: AgentState sau khi orchestrate
        
        Returns:
            Dict chứa tóm tắt kết quả orchestration
        """
        return {
            "success": state.get("orchestration_success", False),
            "conversation_id": state.conversation_id,
            "query": state.user_question,
            "final_response": state.get("final_response"),
            "flow": {
                "need_retrieval": state.get("need_retrieval", False),
                "skip_retrieval": state.get("skip_retrieval", False),
                "retrieval_executed": state.get("retrieval_success", False),
                "synthesis_complete": state.get("synthesis_complete", False)
            },
            "intent": {
                "success": state.get("intent_analysis_success", False),
                "data": state.get("intent_data"),
                "confidence": state.get("intent_confidence"),
                "query_type": state.get("query_type")
            },
            "retrieval": {
                "plan_success": state.get("retrieval_plan_success", False),
                "execution_success": state.get("retrieval_success", False),
                "num_documents": state.get("num_retrieved", 0),
                "strategy": state.get("retrieval_strategy"),
                "num_queries": len(state.get("queries", []))
            },
            "synthesis": {
                "evaluation_success": state.get("evaluation_success", False),
                "evaluation_decision": state.get("evaluation_decision"),
                "should_retry": state.get("should_retry", False),
                "response_success": state.get("response_generation_success", False),
                "num_sources": len(state.get("response_sources", []))
            },
            "errors": {
                "intent_error": state.get("intent_error"),
                "retrieval_plan_error": state.get("retrieval_plan_error"),
                "retrieval_error": state.get("retrieval_error"),
                "evaluation_error": state.get("evaluation_error"),
                "response_error": state.get("response_generation_error"),
                "orchestration_error": state.get("orchestration_error")
            }
        }
    
    def generate_conversation_title(self, message: str) -> str:
        """
        Tạo tiêu đề ngắn gọn cho cuộc hội thoại từ câu hỏi đầu tiên
        
        Args:
            message: Câu hỏi người dùng
        
        Returns:
            str: Tiêu đề cuộc hội thoại (tối đa 50 ký tự)
        """
        try:
            if not message:
                return "New Conversation"
            
            # Lấy API key từ AI Agent Settings
            from openai import OpenAI
            settings = frappe.get_single("AI Agent Settings")
            if not settings or not settings.openai_api_key:
                frappe.throw("OpenAI API key chưa có trong AI Agent Settings")
            
            client = OpenAI(api_key=settings.openai_api_key)
            
            prompt = (
                "Tạo một tiêu đề ngắn (tối đa 50 ký tự) cho cuộc hội thoại dựa trên câu hỏi của user. "
                "Chỉ trả về tiêu đề, không kèm giải thích.\n\nMessage: " + message
            )
            
            response = client.chat.completions.create(
                model=settings.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.5
            )
            
            title = response.choices[0].message.content.strip()
            # Đảm bảo không quá 50 ký tự
            if len(title) > 50:
                title = title[:47] + "..."
            
            return title
        except Exception as e:
            frappe.log_error(f"Không thể tạo title: {str(e)}")
            # Fallback: lấy 50 ký tự đầu của message
            return message[:47] + "..." if len(message) > 50 else message
