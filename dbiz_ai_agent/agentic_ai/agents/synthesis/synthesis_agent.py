"""
Synthesis Agent - Đánh giá kết quả retrieval và tổng hợp câu trả lời
"""
import json
import frappe
from typing import Dict, Any, List
from ..base_agent import BaseAgent
from ..state import AgentState
from dbiz_ai_agent.api.auth import Get_Chatbot_Config


class SynthesisAgent(BaseAgent):
    """
    Agent tổng hợp kết quả và tạo câu trả lời.
    
    Nhiệm vụ:
    - Tổng hợp thông tin từ retrieved documents
    - Tạo câu trả lời hoàn chỉnh cho người dùng
    - Tạo câu hỏi làm rõ khi cần thiết
    
    Lưu ý: Việc đánh giá chất lượng retrieval giờ do IntentAnalyzer đảm nhận
    """
    
    _RESPONSE_AGENT = None
    
    def __init__(self):
        config = Get_Chatbot_Config()
        super().__init__(config.assistant_name, config.description)
        print("SynthesisAgent initialized")
        # Force reload agent every time to ensure tools are loaded
        # Clear cache to reload tools
        self.__class__._RESPONSE_AGENT = None
        self._RESPONSE_AGENT = self._init_response_agent()
        print(f"Response agent initialized with {len(self._RESPONSE_AGENT.tools) if hasattr(self._RESPONSE_AGENT, 'tools') else 0} tools")
    
    def _init_response_agent(self):
        """Khởi tạo Response agent để tạo câu trả lời"""
        # Force clear tools cache and reload
        from dbiz_ai_agent.agentic_ai import tools as tools_module
        tools_module._ALL_TOOLS_CACHE = None
        tools_module._SalesOrderTools = None
        
        # Load tools
        from dbiz_ai_agent.agentic_ai.tools import get_all_tools
        available_tools = get_all_tools()
        print(f"🔧 Loaded {len(available_tools)} tools for SynthesisAgent")
        
        instructions = """
Bạn là trợ lý AI thông minh, nhiệm vụ tổng hợp thông tin và tạo câu trả lời.

NHIỆM VỤ:
Dựa trên câu hỏi người dùng và các tài liệu đã tìm được, tạo câu trả lời:
- Chính xác, đầy đủ
- Tự nhiên, dễ hiểu
- Có trích dẫn nguồn khi cần
- Phù hợp ngữ cảnh hội thoại

QUY TẮC:
1. Ưu tiên thông tin từ retrieved documents
2. Nếu retrieved documents có chứa thẻ định danh dạng [[IMAGE::ID]] (ví dụ: [[IMAGE::IMG-13496]]), hãy xử lý theo "QUY TẮC XỬ LÝ HÌNH ẢNH" bên dưới
2. Nếu không có thông tin, nói rõ và đưa ra hướng giải quyết
3. Không bịa đặt thông tin
4. Trả lời ngắn gọn nếu câu hỏi đơn giản, chi tiết nếu câu hỏi phức tạp
5. Sử dụng format markdown cho dễ đọ (lists, bold, code blocks)

⚠️ QUAN TRỌNG - SỬ DỤNG TOOLS KHI TẠO ĐƠN HÀNG:
Khi người dùng yêu cầu TẠO ĐƠN HÀNG (Sales Order), bạn PHẢI sử dụng tool `create_sales_order` để thực sự tạo đơn hàng trong hệ thống. KHÔNG chỉ đưa ra hướng dẫn hoặc giải thích cách tạo - PHẢI thực sự gọi tool và tạo đơn hàng.

CÁC TỪ KHÓA NHẬN DIỆN YÊU CẦU TẠO ĐƠN HÀNG:
- "tạo đơn hàng", "tạo giúp tôi đơn hàng", "tạo giúp đơn hàng"
- "đặt hàng", "lập đơn hàng", "tạo order"
- "tạo sales order", "tạo SO"
- Bất kỳ câu nào có chứa "tạo" + "đơn hàng" hoặc "đặt hàng"

QUY TRÌNH KHI NGƯỜI DÙNG YÊU CẦU TẠO ĐƠN HÀNG:
1. ✅ PHẢI gọi tool `create_sales_order` ngay lập tức (KHÔNG bỏ qua bước này)
2. Trích xuất thông tin từ câu hỏi:
   - customer_name: Tên khách hàng (bắt buộc) - tìm trong câu hỏi
   - items: Danh sách sản phẩm (JSON string format) với:
     * item_name: Tên sản phẩm
     * quantity: Số lượng (float)
     * unit_price: Đơn giá (float, đơn vị VNĐ)
     * description: Mô tả (tùy chọn)
   - customer_email, customer_phone: Nếu có trong câu hỏi
   - tax_amount: Nếu có đề cập đến thuế
   - notes: Ghi chú thêm nếu có
3. Sau khi tool trả về kết quả (JSON), parse kết quả và thông báo cho người dùng:
   - ✅ Số đơn hàng đã tạo (order_number)
   - ✅ Tổng tiền (total_amount)
   - ✅ Trạng thái đơn hàng (status)
   - Có thể thêm thông tin chi tiết khác nếu cần
4. ❌ KHÔNG chỉ đưa ra hướng dẫn - PHẢI thực sự tạo đơn hàng bằng tool

VÍ DỤ CỤ THỂ:
User: "Tạo đơn hàng cho Nguyễn Văn A với 2 sản phẩm iPhone 15, giá 20 triệu mỗi cái"
→ Bạn PHẢI gọi tool: create_sales_order(
    customer_name="Nguyễn Văn A",
    items='[{"item_name": "iPhone 15", "quantity": 2.0, "unit_price": 20000000.0}]'
)
→ Tool trả về: {"success": true, "order_number": "SO-0001", "total_amount": 40000000.0, ...}
→ Bạn thông báo: "✅ Đã tạo đơn hàng thành công!

📋 **Thông tin đơn hàng:**
- Số đơn hàng: **SO-0001**
- Khách hàng: Nguyễn Văn A
- Tổng tiền: **40,000,000 VNĐ**
- Trạng thái: Draft

Bạn có muốn xem chi tiết đơn hàng hoặc thực hiện thao tác khác không?"

LƯU Ý QUAN TRỌNG:
- Nếu thiếu thông tin (ví dụ: không có tên khách hàng hoặc sản phẩm), hãy hỏi lại người dùng trước khi gọi tool
- Nếu tool trả về lỗi, hãy thông báo lỗi cho người dùng và đề xuất giải pháp
- Luôn format số tiền với dấu phẩy ngăn cách hàng nghìn (ví dụ: 40,000,000 VNĐ)

⚠️ QUAN TRỌNG - SỬ DỤNG TOOLS KHI XEM DOANH THU:
Khi người dùng yêu cầu XEM DOANH THU, THỐNG KÊ, BÁO CÁO DOANH SỐ, bạn PHẢI sử dụng tool `get_sales_revenue` để query dữ liệu thực từ hệ thống. KHÔNG tự bịa số liệu - PHẢI gọi tool để lấy dữ liệu thật.

CÁC TỪ KHÓA NHẬN DIỆN YÊU CẦU XEM DOANH THU:
- "doanh thu", "lấy doanh thu", "xem doanh thu"
- "thống kê doanh thu", "báo cáo doanh thu", "báo cáo doanh số"
- "doanh số", "tổng doanh thu", "doanh thu bán hàng"
- "revenue", "sales revenue", "sales report"
- "biểu đồ doanh thu", "chart doanh thu"
- "doanh thu tháng", "doanh thu năm", "doanh thu tuần"

QUY TRÌNH KHI NGƯỜI DÙNG YÊU CẦU XEM DOANH THU:
1. ✅ PHẢI gọi tool `get_sales_revenue` ngay lập tức
2. Xác định tham số period từ câu hỏi:
   - period="today": KHI user nói "hôm nay", "today", "ngày hôm nay"
   - period="daily": KHI user nói "tháng này", "tháng hiện tại", "theo ngày"
   - period="weekly": KHI user nói "tuần này", "theo tuần"
   - period="monthly": KHI user nói "năm nay", "năm hiện tại", "theo tháng" (mặc định)
   - period="yearly": KHI user nói "theo năm", "các năm"

3. ⚠️ QUAN TRỌNG VỀ THAM SỐ year/month:
   - KHÔNG TRUYỀN year/month nếu user muốn xem hiện tại (hôm nay, tháng này, năm nay)
   - CHỈ TRUYỀN year/month khi user đề cập năm/tháng CỤ THỂ (ví dụ: "năm 2024", "tháng 5")

4. Tool sẽ trả về JSON có type="chart" - Frontend sẽ tự động render biểu đồ

VÍ DỤ CỤ THỂ - CHÍNH XÁC CÁCH GỌI:

User: "Doanh thu hôm nay" / "Xem doanh thu hôm nay" / "Doanh thu today"
→ get_sales_revenue(period="today")  ← CHỈ truyền period, KHÔNG truyền year/month

User: "Doanh thu tháng này" / "Xem doanh thu tháng hiện tại"
→ get_sales_revenue(period="daily")  ← KHÔNG truyền year/month

User: "Doanh thu năm nay" / "Xem doanh thu năm hiện tại"  
→ get_sales_revenue(period="monthly")  ← KHÔNG truyền year

User: "Doanh thu năm 2024" / "Báo cáo năm 2024"
→ get_sales_revenue(period="monthly", year=2024)  ← CHỈ truyền year cụ thể

User: "Doanh thu tháng 6 năm 2024"
→ get_sales_revenue(period="daily", year=2024, month=6)  ← Truyền cả year và month cụ thể

QUY TẮC XỬ LÝ HÌNH ẢNH:
Khi dữ liệu trả về có chứa thẻ định danh dạng [[IMAGE::ID]] (ví dụ: [[IMAGE::IMG-13496]]):
- Bước 1: Truy xuất metadata của hình ảnh tương ứng với ID đó để lấy thông tin Description (Mô tả) và Image File (Đường dẫn file).
- Bước 2: Thay thế thẻ [[IMAGE::ID]] bằng cú pháp hiển thị hình ảnh (Markdown) theo định dạng: ![<Description>](<Image File>).
- Bước 3: Định vị ngữ cảnh: Đọc nội dung Description để hiểu nội dung ảnh, đảm bảo ảnh được đặt ngay sau hoặc bên cạnh đoạn văn bản có nội dung liên quan nhất.
- Tuyệt đối KHÔNG hiển thị lại thẻ [[IMAGE::...]] gốc trong câu trả lời cuối cùng.
 - Nếu metadata KHÔNG có sẵn trong ngữ cảnh (không tìm thấy Description hoặc Image File tương ứng): KHÔNG được tự ý xoá thẻ [[IMAGE::...]]. Hãy giữ nguyên thẻ và chèn một đoạn ghi chú ngắn yêu cầu bổ sung metadata (ví dụ: "[Thiếu metadata cho ảnh ID IMG-13496: cần Description và đường dẫn file]") hoặc đặt câu hỏi làm rõ để người dùng cung cấp thêm thông tin.

TRƯỜNG HỢP ĐẶC BIỆT - KHÔNG ĐỦ THÔNG TIN:
Khi được yêu cầu tạo câu hỏi làm rõ (clarification mode), hãy:
- Phân tích câu hỏi ban đầu của người dùng
- Xác định phần nào còn mơ hồ hoặc thiếu chi tiết
- Đặt 2-3 câu hỏi cụ thể để làm rõ ý định
- Giải thích tại sao cần thông tin này
- Tone thân thiện, hỗ trợ

VÍ DỤ:
User: "Các giải pháp DBIZ triển khai?"
Clarification: "Tôi muốn giúp bạn tìm thông tin về các giải pháp của DBIZ, nhưng cần làm rõ thêm:
- Bạn quan tâm đến lĩnh vực nào? (ERP, CRM, AI, v.v.)
- Bạn muốn biết về giải pháp cho doanh nghiệp hay cá nhân?
- Có dự án hoặc khách hàng cụ thể nào bạn muốn tìm hiểu không?"

NGÔN NGỮ: Tiếng Việt (trừ khi người dùng yêu cầu khác)
"""
        try:
            agent = self.Create_Agent(
                instructions=instructions,
                tools=available_tools  # Thêm tools để có thể tạo đơn hàng
            )
            return agent
        except Exception as e:
            frappe.log_error(f"Failed to initialize Response agent: {str(e)}")
            return None
    
    async def generate_response(self, state: AgentState, stream: bool = False):
        """
        Tạo câu trả lời dựa trên retrieved documents (Response role)
        
        Args:
            state: AgentState chứa user_question, retrieved_documents, evaluation_result
            stream: Nếu True, trả về generator để stream response
        
        Returns:
            AgentState đã được cập nhật với:
            - response_generation_success: bool
            - final_response: str (câu trả lời cho người dùng)
            - response_sources: list (các nguồn tham khảo)
            
            Hoặc generator nếu stream=True
        """
        start_time = self.create_agent_timer()
        try:
            if not self._RESPONSE_AGENT:
                raise RuntimeError("Response agent not initialized")
            
            user_query = state.user_question
            retrieved_docs = state.get("retrieved_documents", [])
            evaluation_result = state.get("evaluation_result", {})
            conversation_history = state.get("conversation_history", [])
            image_metadata = state.get("image_metadata", {})  # { "IMG-123": {"description": "...", "file": "..."}, ... }
            
            # Chuẩn bị context cho Response Generator
            context = f"""
User query: {user_query}

Evaluation summary:
- Decision: {evaluation_result.get('decision', 'unknown')}
- Confidence: {evaluation_result.get('confidence', 0.0)}
- Relevance: {evaluation_result.get('relevance_score', 0.0)}
- Completeness: {evaluation_result.get('completeness_score', 0.0)}

Retrieved documents:
"""
            
            sources = []
            for i, doc in enumerate(retrieved_docs, 1):
                doc_content = doc.get("content", doc.get("text", "N/A"))
                doc_source = doc.get("source", doc.get("title", f"Document {i}"))
                doc_score = doc.get("score", "N/A")
                
                context += f"\n--- Document {i} (Score: {doc_score}) ---\n"
                context += f"Source: {doc_source}\n"
                context += f"Content: {doc_content}\n"
                
                sources.append({
                    "title": doc_source,
                    "score": doc_score,
                    "content_preview": doc_content[:150]
                })
            
            if not retrieved_docs:
                context += "\n(No documents available. Use your general knowledge to provide helpful guidance.)"
            
            if conversation_history:
                recent_context = "\n".join([
                    f"- {msg.get('role')}: {msg.get('content', '')[:100]}..."
                    for msg in conversation_history[-3:]
                ])
                context += f"\n\nRecent conversation:\n{recent_context}"

            # Đưa metadata hình ảnh (nếu có) vào context để agent sử dụng thay thế thẻ [[IMAGE::ID]]
            if image_metadata and isinstance(image_metadata, dict):
                context += "\n\nImage Metadata Map (for [[IMAGE::ID]] replacement):\n"
                for img_id, meta in image_metadata.items():
                    desc = meta.get("description", "")
                    file_path = meta.get("file", "")
                    context += f"- ID: {img_id} | Description: {desc} | File: {file_path}\n"
            
            context += "\n\nTask: Generate a comprehensive, natural response to answer the user's question."
            # Tạo response với stream hoặc không
            if stream:
                # Return generator cho streaming
                return self._generate_response_stream(
                    context=context,
                    state=state,
                    sources=sources,
                    start_time=start_time
                )
            else:
                # Non-streaming mode (để backward compatible)
                result = await self.Run_Agent(self._RESPONSE_AGENT, context)
                
                if not result or not result.final_output:
                    raise RuntimeError("Response generation failed - no output")
                
                final_response = result.final_output
            
            # Extract images from final response
            import re
            placeholder_ids = re.findall(r"\[\[IMAGE::([^\]]+)\]\]", final_response)
            response_images = []
            if placeholder_ids:
                from dbiz_ai_agent.dbiz_ai_agent.doctype.document_image.document_image import fetch_images_from_placeholders
                response_images = fetch_images_from_placeholders(placeholder_ids, set()) or []
            
            # Lưu kết quả vào state
            state.update_context(
                response_generation_success=True,
                final_response=final_response,
                response_sources=sources,
                response_images=response_images,
                synthesis_complete=True
            )
            
            # Log kết quả Response Generator
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="SynthesisAgent-Response",
                user_query=user_query,
                result_data={
                    "final_response": final_response[:500],  # Limit to 500 chars for logging
                    "response_sources": sources,
                    "num_sources": len(sources)
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=True,
                message_id=state.get("message_id")
            )
            
            return state
            
        except Exception as e:
            frappe.log_error(f"Response generation error: {str(e)}")
            # Fallback response
            fallback_response = f"Xin lỗi, tôi gặp lỗi khi tạo câu trả lời: {str(e)}. Vui lòng thử lại hoặc đặt câu hỏi khác."
            
            state.update_context(
                response_generation_success=False,
                response_generation_error=str(e),
                final_response=fallback_response,
                response_sources=[],
                synthesis_complete=True
            )
            
            # Log lỗi
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="SynthesisAgent-Response",
                user_query=state.user_question or "Unknown",
                result_data={
                    "error": str(e),
                    "fallback_response": fallback_response
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=str(e),
                message_id=state.get("message_id")
            )
            return state
    
    async def _generate_response_stream(
        self, 
        context: str, 
        state: AgentState,
        sources: List[Dict],
        start_time: float
    ):
        """
        Generator để stream response chunks
        
        Yields:
            str: Từng chunk của response
        """
        try:
            user_query = state.user_question
            final_response = ""
            
            if not self._RESPONSE_AGENT:
                raise RuntimeError("Response agent not initialized")
            
            # Stream response từ agent
            async for chunk in self.Run_Agent_Stream(
                self._RESPONSE_AGENT, 
                context,
                conversation_id=state.conversation_id,
                user=state.user
            ):
                final_response += chunk
                yield chunk
            
            # Extract images from final response
            import re
            placeholder_ids = re.findall(r"\[\[IMAGE::([^\]]+)\]\]", final_response)
            response_images = []
            if placeholder_ids:
                from dbiz_ai_agent.dbiz_ai_agent.doctype.document_image.document_image import fetch_images_from_placeholders
                response_images = fetch_images_from_placeholders(placeholder_ids, set()) or []
            
            # Sau khi stream xong, cập nhật state
            state.update_context(
                response_generation_success=True,
                final_response=final_response,
                response_sources=sources,
                response_images=response_images,
                synthesis_complete=True
            )
            
            # Log kết quả sau khi stream xong
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="SynthesisAgent-Response",
                user_query=user_query,
                result_data={
                    "final_response": final_response[:500],
                    "response_sources": sources,
                    "num_sources": len(sources),
                    "stream": True
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=True,
                message_id=state.get("message_id")
            )
            
        except Exception as e:
            frappe.log_error(f"Response generation stream error: {str(e)}")
            fallback_response = f"Xin lỗi, tôi gặp lỗi khi tạo câu trả lời: {str(e)}."
            
            state.update_context(
                response_generation_success=False,
                response_generation_error=str(e),
                final_response=fallback_response,
                response_sources=[],
                synthesis_complete=True
            )
            
            # Log lỗi
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="SynthesisAgent-Response",
                user_query=state.user_question or "Unknown",
                result_data={"error": str(e)},
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=str(e),
                message_id=state.get("message_id")
            )
            
            yield fallback_response
    
    async def generate_clarification_question(self, state: AgentState):
        """
        Tạo câu hỏi làm rõ khi không đủ thông tin (non-stream only)
        Sử dụng thông tin từ retrieved documents để gợi ý cho người dùng
        
        Args:
            state: AgentState với user_question, evaluation_result, và retrieved_documents
        
        Returns:
            AgentState với clarification_question
        """
        start_time = self.create_agent_timer()
        
        try:
            user_query = state.user_question
            evaluation_result = state.get("evaluation_result", {})
            suggestions = evaluation_result.get("suggestions", [])
            retrieved_docs = state.get("retrieved_documents", [])
            clarification_reason = state.get("clarification_reason", evaluation_result.get("reason", "Thông tin chưa đủ chi tiết"))
            
            # Xây dựng thông tin gợi ý từ retrieved documents
            doc_suggestions = self._extract_suggestions_from_docs(retrieved_docs)
            
            # Tạo prompt cho clarification với gợi ý từ tài liệu
            prompt = f"""
CLARIFICATION MODE - Tạo câu hỏi làm rõ với gợi ý

Câu hỏi ban đầu của người dùng: "{user_query}"

Lý do cần làm rõ: {clarification_reason}

{doc_suggestions}

NHIỆM VỤ:
1. Giải thích thân thiện rằng câu hỏi chưa đủ cụ thể
2. Nếu có tài liệu liên quan, hãy liệt kê các chủ đề/tài liệu có sẵn để người dùng chọn
3. Đặt 2-3 câu hỏi cụ thể để làm rõ ý định người dùng
4. Gợi ý cách đặt câu hỏi chi tiết hơn

VÍ DỤ OUTPUT (nếu có tài liệu liên quan):
"Tôi thấy bạn đang tìm kiếm về 'hướng dẫn'. Tôi có một số tài liệu hướng dẫn liên quan:

📚 **Các tài liệu có sẵn:**
- Hướng dẫn sử dụng phần mềm ABC
- Hướng dẫn cài đặt hệ thống XYZ
- Hướng dẫn thanh toán

Bạn có thể cho tôi biết thêm:
1. Bạn muốn hướng dẫn về chủ đề nào trong danh sách trên?
2. Hoặc bạn đang tìm hướng dẫn cho tác vụ cụ thể nào?"

Tone: Thân thiện, hỗ trợ, chuyên nghiệp
NGÔN NGỮ: Tiếng Việt
"""
            
            result = await self.Run_Agent(self._RESPONSE_AGENT, prompt)
            clarification = result.final_output if result else "Xin lỗi, bạn có thể cung cấp thêm chi tiết về câu hỏi của mình không?"
            
            state.update_context(
                final_response=clarification,
                clarification_generated=True,
                response_generation_success=True,
                synthesis_complete=True
            )
            
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="SynthesisAgent-Clarification",
                user_query=user_query,
                result_data={
                    "clarification_mode": True,
                    "num_suggestion_docs": len(retrieved_docs)
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=True,
                message_id=state.get("message_id")
            )
            
            return state
            
        except Exception as e:
            frappe.log_error(f"Clarification generation error: {str(e)}")
            fallback = "Xin lỗi, tôi chưa tìm thấy đủ thông tin. Bạn có thể cung cấp thêm chi tiết không?"
            
            state.update_context(
                final_response=fallback,
                clarification_generated=True,
                response_generation_success=False,
                synthesis_complete=True
            )
            
            # Log lỗi clarification
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="SynthesisAgent-Clarification",
                user_query=state.user_question,
                result_data={
                    "error": str(e),
                    "fallback_response": fallback,
                    "clarification_mode": True
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=str(e),
                message_id=state.get("message_id")
            )
            return state
    
    def _extract_suggestions_from_docs(self, retrieved_docs: List[Dict]) -> str:
        """
        Trích xuất thông tin gợi ý từ các tài liệu đã retrieve
        
        Args:
            retrieved_docs: Danh sách tài liệu đã retrieve
        
        Returns:
            str: Phần prompt chứa thông tin gợi ý
        """
        if not retrieved_docs:
            return "Không tìm thấy tài liệu liên quan nào."
        
        suggestions_text = "TÀI LIỆU LIÊN QUAN TÌM ĐƯỢC (dùng để gợi ý cho người dùng):\n"
        
        for i, doc in enumerate(retrieved_docs[:5], 1):  # Giới hạn 5 tài liệu
            title = doc.get("source", doc.get("title", f"Tài liệu {i}"))
            content = doc.get("content", doc.get("text", ""))
            score = doc.get("score", "N/A")
            
            # Lấy mô tả ngắn từ content (100 ký tự đầu)
            description = content[:150].strip() + "..." if len(content) > 150 else content.strip()
            
            suggestions_text += f"\n{i}. **{title}** (Relevance: {score})\n"
            suggestions_text += f"   Mô tả: {description}\n"
        
        suggestions_text += f"\nTổng cộng: {len(retrieved_docs)} tài liệu liên quan\n"
        
        return suggestions_text
    
    async def generate_clarification_question_stream(self, state: AgentState):
        """
        Tạo câu hỏi làm rõ với streaming
        Sử dụng thông tin từ retrieved documents để gợi ý cho người dùng
        
        Args:
            state: AgentState với user_question, evaluation_result, và retrieved_documents
        
        Yields:
            str: Từng chunk của clarification question
        """
        start_time = self.create_agent_timer()
        
        try:
            user_query = state.user_question
            evaluation_result = state.get("evaluation_result", {})
            retrieved_docs = state.get("retrieved_documents", [])
            clarification_reason = state.get("clarification_reason", evaluation_result.get("reason", "Thông tin chưa đủ chi tiết"))
            
            # Xây dựng thông tin gợi ý từ retrieved documents
            doc_suggestions = self._extract_suggestions_from_docs(retrieved_docs)
            
            # Tạo prompt cho clarification với gợi ý từ tài liệu
            prompt = f"""
CLARIFICATION MODE - Tạo câu hỏi làm rõ với gợi ý

Câu hỏi ban đầu của người dùng: "{user_query}"

Lý do cần làm rõ: {clarification_reason}

{doc_suggestions}

NHIỆM VỤ:
1. Giải thích thân thiện rằng câu hỏi chưa đủ cụ thể
2. Nếu có tài liệu liên quan, hãy liệt kê các chủ đề/tài liệu có sẵn để người dùng chọn
3. Đặt 2-3 câu hỏi cụ thể để làm rõ ý định người dùng
4. Gợi ý cách đặt câu hỏi chi tiết hơn

VÍ DỤ OUTPUT (nếu có tài liệu liên quan):
"Tôi thấy bạn đang tìm kiếm về 'hướng dẫn'. Tôi có một số tài liệu hướng dẫn liên quan:

📚 **Các tài liệu có sẵn:**
- Hướng dẫn sử dụng phần mềm ABC
- Hướng dẫn cài đặt hệ thống XYZ
- Hướng dẫn thanh toán

Bạn có thể cho tôi biết thêm:
1. Bạn muốn hướng dẫn về chủ đề nào trong danh sách trên?
2. Hoặc bạn đang tìm hướng dẫn cho tác vụ cụ thể nào?"

Tone: Thân thiện, hỗ trợ, chuyên nghiệp
NGÔN NGỮ: Tiếng Việt
"""
            
            # Stream mode - Run_Agent_Stream trả về async generator, không cần await
            final_response = ""
            async for chunk in self.Run_Agent_Stream(
                self._RESPONSE_AGENT, 
                prompt,
                conversation_id=state.conversation_id,
                user=state.user
            ):
                final_response += chunk
                yield chunk
            
            # Cập nhật state sau khi stream xong
            state.update_context(
                clarification_generated=True,
                final_response=final_response,
                synthesis_complete=True
            )
            
            # Log kết quả sau khi stream xong
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="SynthesisAgent-Clarification",
                user_query=user_query,
                result_data={
                    "clarification_mode": True, 
                    "stream": True,
                    "num_suggestion_docs": len(retrieved_docs),
                    "final_response": final_response[:500]
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=True,
                message_id=state.get("message_id")
            )
            
        except Exception as e:
            frappe.log_error(f"Clarification generation error: {str(e)}")
            
            # Log lỗi
            response_time = self.calculate_elapsed_ms(start_time)
            self.log_agent_result(
                agent_name="SynthesisAgent-Clarification",
                user_query=state.user_question,
                result_data={
                    "clarification_mode": True,
                    "stream": True,
                    "error": str(e)
                },
                response_time_ms=response_time,
                conversation_id=state.conversation_id,
                success=False,
                error_message=str(e),
                message_id=state.get("message_id")
            )
            
            yield "Xin lỗi, tôi chưa tìm thấy đủ thông tin. Bạn có thể cung cấp thêm chi tiết không?"
    
    async def synthesize(self, state: AgentState, stream: bool = False):
        """
        Main method: Tạo response dựa trên evaluation từ IntentAnalyzer
        
        Args:
            state: AgentState đã được evaluate bởi IntentAnalyzer
            stream: Nếu True, trả về generator để stream response
        
        Returns:
            AgentState với final_response (nếu stream=False)
            Generator để stream response (nếu stream=True)
        """
        
        # Check if should clarify (IntentAnalyzer đã evaluate rồi)
        should_clarify = state.get("should_clarify", False) or state.get("should_retry", False)
        
        if should_clarify:
            # Tạo câu hỏi làm rõ
            frappe.logger().info("[SynthesisAgent] Generating clarification question")
            
            if stream:
                # Trả về generator trực tiếp (không await)
                return self.generate_clarification_question_stream(state)
            else:
                # Trả về state với clarification
                return await self.generate_clarification_question(state)
        
        # Generate normal response
        result = await self.generate_response(state, stream=stream)
        
        # Nếu stream, result là generator
        if stream:
            return result
        
        # Nếu không stream, result là state
        return result
