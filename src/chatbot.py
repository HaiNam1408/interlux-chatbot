import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import json

from .database import (
    search_products, 
    search_policies, 
    search_faqs, 
    get_user_orders,
    get_product_by_id
)
from .models import UserSession

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=GOOGLE_API_KEY)

class Chatbot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.system_prompt = """
        Bạn là trợ lý ảo của Interlux - cửa hàng nội thất cao cấp. Nhiệm vụ của bạn là hỗ trợ khách hàng với các vấn đề sau:
        
        1. Tư vấn bán hàng: Giới thiệu sản phẩm, tính năng, giá cả, và giúp khách hàng tìm sản phẩm phù hợp.
        2. Tư vấn chính sách: Cung cấp thông tin về chính sách bảo hành, đổi trả, vận chuyển, và thanh toán.
        3. Quản lý đơn hàng: Giúp khách hàng kiểm tra trạng thái đơn hàng, lịch sử mua hàng.
        4. Trả lời câu hỏi: Giải đáp các thắc mắc của khách hàng về sản phẩm và dịch vụ.
        5. Gợi ý sản phẩm: Đề xuất sản phẩm phù hợp dựa trên nhu cầu của khách hàng.
        
        Hãy trả lời một cách lịch sự, chuyên nghiệp và hữu ích. Nếu không biết câu trả lời, hãy thành thật và đề nghị kết nối với nhân viên hỗ trợ.
        
        Khi trả lời, hãy sử dụng thông tin từ cơ sở dữ liệu được cung cấp. Không được tự ý tạo ra thông tin không có trong dữ liệu.
        """
    
    def classify_intent(self, message: str) -> str:
        """Phân loại ý định của người dùng"""
        prompt = f"""
        Phân loại ý định của tin nhắn sau vào một trong các danh mục:
        - product_inquiry: Hỏi về sản phẩm, tính năng, giá cả
        - policy_inquiry: Hỏi về chính sách bảo hành, đổi trả, vận chuyển, thanh toán
        - order_management: Kiểm tra đơn hàng, lịch sử mua hàng
        - general_question: Câu hỏi chung về cửa hàng, dịch vụ
        - product_recommendation: Yêu cầu gợi ý sản phẩm phù hợp
        
        Tin nhắn: {message}
        
        Trả về chỉ một danh mục duy nhất.
        """
        
        response = self.model.generate_content(prompt)
        intent = response.text.strip().lower()
        
        # Normalize intent
        if "product_inquiry" in intent:
            return "product_inquiry"
        elif "policy_inquiry" in intent:
            return "policy_inquiry"
        elif "order_management" in intent:
            return "order_management"
        elif "product_recommendation" in intent:
            return "product_recommendation"
        else:
            return "general_question"
    
    def retrieve_context(self, message: str, intent: str) -> Dict[str, Any]:
        """Truy xuất thông tin liên quan từ cơ sở dữ liệu"""
        context = {}
        
        if intent == "product_inquiry":
            products = search_products(message)
            context["products"] = products
        
        elif intent == "policy_inquiry":
            policies = search_policies(message)
            context["policies"] = policies
        
        elif intent == "general_question":
            faqs = search_faqs(message)
            context["faqs"] = faqs
        
        elif intent == "product_recommendation":
            # Tìm kiếm sản phẩm dựa trên mô tả nhu cầu
            products = search_products(message)
            context["recommended_products"] = products
        
        return context
    
    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Định dạng ngữ cảnh để đưa vào prompt"""
        formatted_context = "Thông tin từ cơ sở dữ liệu:\n"
        
        if "products" in context and context["products"]:
            formatted_context += "\nSản phẩm:\n"
            for product in context["products"]:
                formatted_context += f"- Tên: {product['name']}\n"
                formatted_context += f"  Mô tả: {product['description']}\n"
                formatted_context += f"  Giá: {product['price']} VND\n"
                formatted_context += f"  Danh mục: {product['category']}\n"
                formatted_context += f"  Tính năng: {', '.join(product['features'])}\n"
        
        if "policies" in context and context["policies"]:
            formatted_context += "\nChính sách:\n"
            for policy in context["policies"]:
                formatted_context += f"- {policy['title']}: {policy['content']}\n"
        
        if "faqs" in context and context["faqs"]:
            formatted_context += "\nCâu hỏi thường gặp:\n"
            for faq in context["faqs"]:
                formatted_context += f"- Câu hỏi: {faq['question']}\n"
                formatted_context += f"  Trả lời: {faq['answer']}\n"
        
        if "recommended_products" in context and context["recommended_products"]:
            formatted_context += "\nSản phẩm được đề xuất:\n"
            for product in context["recommended_products"]:
                formatted_context += f"- Tên: {product['name']}\n"
                formatted_context += f"  Mô tả: {product['description']}\n"
                formatted_context += f"  Giá: {product['price']} VND\n"
                formatted_context += f"  Danh mục: {product['category']}\n"
                formatted_context += f"  Tính năng: {', '.join(product['features'])}\n"
        
        if "orders" in context and context["orders"]:
            formatted_context += "\nĐơn hàng:\n"
            for order in context["orders"]:
                formatted_context += f"- Mã đơn hàng: {order['id']}\n"
                formatted_context += f"  Trạng thái: {order['status']}\n"
                formatted_context += f"  Tổng tiền: {order['total_amount']} VND\n"
                formatted_context += "  Sản phẩm:\n"
                for product in order["products"]:
                    formatted_context += f"    + {product.get('name', 'Sản phẩm')} - Số lượng: {product['quantity']}\n"
        
        return formatted_context
    
    def process_message(self, message: str, session: UserSession) -> str:
        """Xử lý tin nhắn từ người dùng và trả về phản hồi"""
        # Phân loại ý định
        intent = self.classify_intent(message)
        
        # Lấy ngữ cảnh từ session
        context = session.context
        
        # Xử lý đặc biệt cho quản lý đơn hàng
        if intent == "order_management" and "user_id" in context:
            user_id = context["user_id"]
            orders = get_user_orders(user_id)
            context["orders"] = orders
        
        # Truy xuất thông tin liên quan
        retrieved_context = self.retrieve_context(message, intent)
        
        # Cập nhật ngữ cảnh
        context.update(retrieved_context)
        session.context = context
        
        # Định dạng ngữ cảnh cho prompt
        formatted_context = self.format_context_for_prompt(context)
        
        # Lấy lịch sử trò chuyện
        chat_history = session.get_chat_history()
        
        # Tạo prompt
        prompt = f"""
        {self.system_prompt}
        
        {formatted_context}
        
        Lịch sử trò chuyện:
        {chat_history}
        
        Tin nhắn mới nhất của khách hàng: {message}
        
        Trả lời:
        """
        
        # Gọi Gemini API
        response = self.model.generate_content(prompt)
        
        return response.text.strip()
