"""
Base Agent Class for Agentic RAG System
"""
import os
import frappe
from frappe import _
from abc import ABC
from typing import Dict, List, Any, Optional
from contextvars import ContextVar
import time
from openai import OpenAI
from agents import Agent, Runner, OpenAIConversationsSession
from agents.result import RunResultStreaming

# Context variable để truyền user giữa các async calls
current_request_user: ContextVar[Optional[str]] = ContextVar('current_request_user', default=None)


class BaseAgent(ABC):
    """Base class for AI agents"""    
    _OPENAI_CLIENT: Optional[OpenAI] = None
    _SETTINGS: Optional[Any] = None
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._initialize()
        self._last_stream_result: Optional[RunResultStreaming] = None
    
    def _initialize(self):
        # Load required settings even for Guest (widget) using DB-level getters
        if not self._SETTINGS:
            self._SETTINGS = frappe.get_single("AI Agent Settings") or frappe.throw(_("Chưa tìm thấy cấu hình AI Agent."))
            os.environ['OPENAI_API_KEY'] = self._SETTINGS.openai_api_key
        if not getattr(self._SETTINGS, "openai_api_key", None):
            frappe.throw(_("OpenAI API key chưa có trong AI Agent Settings."))
            return 

        if self._OPENAI_CLIENT is None:
            self._OPENAI_CLIENT = OpenAI(api_key=self._SETTINGS.openai_api_key)
    
    @staticmethod
    def Get_Chatbot_Config(title: Optional[str] = None):
        """Load chatbot configuration by title or current active one."""
        try:
            if title:
                return frappe.get_doc("Chatbot Configuration", {"title": title})

            active_name = frappe.db.get_value(
                "Chatbot Configuration",
                {"is_active": 1},
                "name",
            )
            if active_name:
                return frappe.get_doc("Chatbot Configuration", active_name)
        except frappe.DoesNotExistError:
            pass

        frappe.throw(_("Vui lòng thiết lập một cấu hình Chatbot đang hoạt động trước khi sử dụng trợ lý."))
    
    def Get_Openai_Client(self) -> Optional[OpenAI]:
        return self._OPENAI_CLIENT
    
    def Get_Openai_Settings(self):
        return self._SETTINGS
    
    def Create_Agent(self, instructions: str = None, tools: List = None, response_format: Dict = None) -> Optional[Any]:
        try:
            # Lấy config nếu chưa có
            if not hasattr(self, 'Config'):
                self.Config = self.Get_Chatbot_Config()
            
            agent_params = {
                "name": self.Config.assistant_name if hasattr(self, 'Config') else self.name,
                "model": self.Get_Openai_Settings().model,
                "instructions": instructions,
                "tools": tools or []
            }
            
            agent = Agent(**agent_params)
            
            # Lưu response_format để sử dụng khi Run_Agent
            if response_format:
                agent._response_format = response_format
            
            return agent
        except Exception as e:
            frappe.log_error(f"Không thể tạo agent: {str(e)}")
            raise RuntimeError(f"Không thể tạo agent: {str(e)}")
    
    async def Run_Agent(self, agent: Agent, input_text: str, conversation_id: str = None):
        try:
            session = self.Build_Session(conversation_id)
            
            # Kiểm tra có response_format không (cho JSON mode)
            if hasattr(agent, '_response_format'):
                # Sử dụng OpenAI client trực tiếp cho JSON mode
                response = await self._run_agent_with_json_mode(
                    agent=agent,
                    input_text=input_text,
                    session=session
                )
            else:
                # Chạy agent bình thường
                response = await Runner.run(
                    starting_agent=agent,
                    input=input_text,
                    session=session,
                )
            
            return response
        except Exception as e:
            frappe.log_error(f"Không thể chạy agent: {str(e)}")
            raise RuntimeError(f"Không thể chạy agent: {str(e)}")
    
    async def _run_agent_with_json_mode(self, agent: Agent, input_text: str, session):
        """
        Chạy agent với JSON mode bằng OpenAI client trực tiếp
        """
        try:
            client = self.Get_Openai_Client()
            
            # Tạo messages
            messages = [
                {"role": "system", "content": agent.instructions},
                {"role": "user", "content": input_text}
            ]
            
            # Gọi OpenAI API với response_format
            response = client.chat.completions.create(
                model=agent.model,
                messages=messages,
                response_format=agent._response_format
            )
            
            # Tạo object giống với Runner.run response
            class JSONResponse:
                def __init__(self, content):
                    self.final_output = content
            
            return JSONResponse(response.choices[0].message.content)
            
        except Exception as e:
            frappe.log_error(f"JSON mode agent error: {str(e)}")
            raise RuntimeError(f"JSON mode agent error: {str(e)}")

    async def Run_Agent_Stream(self, agent: Agent, input_text: str, conversation_id: str = None, user: Optional[str] = None):
        try:
            if user:
                current_request_user.set(user)
            
            # Check if agent has tools
            has_tools = hasattr(agent, 'tools') and agent.tools and len(agent.tools) > 0
            
            if has_tools:
                # Use Runner with tools support - DON'T use session to avoid OpenAI conversation_id issue
                frappe.logger().info(f"🔧 Running agent with {len(agent.tools)} tools")
                
                # Run with tools - non-streaming, NO session (avoids conversation_id format issue)
                result = await Runner.run(
                    starting_agent=agent,
                    input=input_text,
                    # Don't pass session - OpenAI expects conv-xxx format but we use CONV-xxxx
                )
                
                # Log result for debugging
                frappe.logger().info(f"🔧 Runner result type: {type(result)}")
                if result:
                    frappe.logger().info(f"🔧 Final output (first 200 chars): {str(result.final_output)[:200] if result.final_output else 'None'}")
                
                # Check if any tool returned chart data - if so, yield that instead of agent's formatted text
                chart_data = None
                if result and hasattr(result, 'new_items'):
                    from agents.items import ToolCallOutputItem
                    for item in result.new_items:
                        item_type = type(item).__name__
                        frappe.logger().info(f"🔧 Result item type: {item_type}")
                        # Check for ToolCallOutputItem which contains tool output
                        if isinstance(item, ToolCallOutputItem) or (hasattr(item, 'output') and hasattr(item, 'type') and item.type == 'tool_call_output_item'):
                            try:
                                import json
                                output_str = item.output if isinstance(item.output, str) else str(item.output)
                                frappe.logger().info(f"🔧 Tool output (first 200): {output_str[:200]}")
                                output_data = json.loads(output_str) if isinstance(item.output, str) else item.output
                                if isinstance(output_data, dict) and output_data.get('type') == 'chart':
                                    frappe.logger().info(f"📊 Found chart data from tool!")
                                    chart_data = output_str
                                    break
                            except Exception as parse_err:
                                frappe.logger().warning(f"🔧 Failed to parse tool output: {parse_err}")
                                pass
                
                # If we found chart data, yield it directly (JSON for frontend to parse)
                if chart_data:
                    frappe.logger().info(f"📊 Yielding chart data directly (bypassing agent format)")
                    yield chart_data
                elif result and result.final_output:
                    yield result.final_output
                else:
                    yield "Không có kết quả từ agent."
            else:
                # No tools - use direct OpenAI streaming for better UX
                client = self.Get_Openai_Client()
                if not client:
                    raise RuntimeError("OpenAI client not available")
                
                stream = client.chat.completions.create(
                    model=agent.model or "gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": agent.instructions or ""},
                        {"role": "user", "content": input_text}
                    ],
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
        except Exception as e:
            error_msg = str(e)[:100]  # Truncate to avoid log error
            frappe.logger().error(f"Run_Agent_Stream error: {error_msg}")
            yield f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại."
        finally:
            # Clear context sau khi xong
            current_request_user.set(None)

    def Build_Session(self, conversation_id: Optional[str]) -> Optional[OpenAIConversationsSession]:
        if conversation_id:
            return OpenAIConversationsSession(
                conversation_id=conversation_id,
            )
        return OpenAIConversationsSession()

    def Ensure_Conversation(self, conversation_name: str = None) -> Optional[str]:
        from dbiz_ai_agent.dbiz_ai_agent.doctype.ai_conversation.ai_conversation import get_conversation as get_conversation_helper
        
        client = self.Get_Openai_Client()
        if conversation_name:
            ai_conv = get_conversation_helper(conversation_name)
            if ai_conv.openai_conversation_id:
                conversation = client.conversations.retrieve(ai_conv.openai_conversation_id)
                return conversation.id
            conversation = client.conversations.create()
            ai_conv.openai_conversation_id = conversation.id
            ai_conv.save(ignore_permissions=True)
            return conversation.id

    def Run_Response(self, prompt: str) -> str:
        client = self.Get_Openai_Client()
        if client is None:
            frappe.throw(_("Chưa khởi tạo OpenAI client."))
        try:
            resp = client.responses.create(
                model=self.Get_Openai_Settings().model,
                input=prompt, 
            )
            return getattr(resp, "output_text", "") or ""
        except Exception as e:
            frappe.log_error(f"Không thể gọi OpenAI: {e}")
            frappe.throw(_("Không thể gọi OpenAI."))
    
    @staticmethod
    def log_agent_result(
        agent_name: str,
        user_query: str,
        result_data: Dict[str, Any],
        response_time_ms: Optional[int] = None,
        conversation_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Lưu kết quả agent vào Chatbot Access Log
        
        Args:
            agent_name: Tên agent (IntentAnalyzer, QueryGenerator, etc.)
            user_query: Câu hỏi người dùng
            result_data: Dict chứa kết quả của agent
            response_time_ms: Thời gian xử lý (ms)
            conversation_id: ID cuộc hội thoại
            success: Agent có chạy thành công không
            error_message: Thông báo lỗi nếu có
            message_id: ID của message (dùng để group các agents cùng xử lý 1 message)
        
        Returns:
            Log name nếu thành công, None nếu thất bại
        """
        try:
            # Import here để tránh circular import
            from dbiz_ai_agent.dbiz_ai_agent.doctype.chatbot_access_log.chatbot_access_log import log_chatbot_access
            
            # Map agent name sang query_type hợp lệ
            # Valid options: "Document Search", "Data Query", "General Chat", "System Command", "Chat with Images"
            agent_to_query_type = {
                "IntentAnalyzer": "System Command",
                "QueryGenerator": "System Command", 
                "RetrievalAgent": "Document Search",
                "SynthesisAgent-Critic": "System Command",
                "SynthesisAgent-Response": "General Chat",
                "SmartOrchestrator": "General Chat"
            }
            
            query_type = agent_to_query_type.get(agent_name, "General Chat")
            
            # Trích xuất thông tin từ result_data
            accessed_documents = []
            if "retrieved_documents" in result_data:
                docs = result_data.get("retrieved_documents", [])
                accessed_documents = [
                    {
                        "source": doc.get("source", doc.get("title", "Unknown")),
                        "score": doc.get("score", 0),
                        "preview": doc.get("content", doc.get("text", ""))[:150]
                    }
                    for doc in docs[:10]  # Limit to 10 documents
                ]
            
            # Metadata về agent execution (lưu agent_name vào đây)
            agent_metadata = {
                "agent_name": agent_name,  # Lưu tên agent thực sự ở đây
                "agent_type": query_type,  # Loại query được map
                "conversation_id": conversation_id,
                "success": success,
                "error_message": error_message,
                "result_summary": {
                    k: v for k, v in result_data.items() 
                    if k not in ["retrieved_documents", "conversation_history"]  # Exclude large fields
                }
            }
            
            # Security flags nếu có lỗi
            security_flags = None
            if not success:
                security_flags = f"Agent Error: {agent_name}"
            
            # Results count
            results_count = 0
            if "num_retrieved" in result_data:
                results_count = result_data.get("num_retrieved", 0)
            elif "retrieved_documents" in result_data:
                results_count = len(result_data.get("retrieved_documents", []))
            
            # Gọi hàm log
            log_name = log_chatbot_access(
                query_text=user_query,
                query_type=query_type,
                accessed_documents=accessed_documents if accessed_documents else None,
                vector_collections_used=agent_metadata.get("vector_collections"),
                permissions_applied=agent_metadata,
                response_time_ms=response_time_ms,
                results_count=results_count,
                security_flags=security_flags,
                blocked_reason=error_message if not success else None,
                message_id=message_id,
                agent_name=agent_name
            )
            
            return log_name
            
        except Exception as e:
            frappe.log_error(f"Failed to log agent result for {agent_name}: {str(e)}")
            return None
    
    @staticmethod
    def create_agent_timer():
        """Tạo timer để đo thời gian xử lý agent"""
        return time.time()
    
    @staticmethod
    def calculate_elapsed_ms(start_time: float) -> int:
        """Tính thời gian đã trôi qua từ start_time (ms)"""
        return int((time.time() - start_time) * 1000)
