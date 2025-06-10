import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any, List

from .database import (
    search_products,
    search_policies,
    search_faqs,
    get_user_orders
)
from .models import UserSession

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

        QUAN TRỌNG:
        - Trả lời một cách lịch sự, chuyên nghiệp và hữu ích.
        - TUYỆT ĐỐI CHỈ sử dụng thông tin từ cơ sở dữ liệu được cung cấp.
        - KHÔNG ĐƯỢC TẠO RA hoặc BỊA RA bất kỳ thông tin nào không có trong dữ liệu.
        - Nếu không có thông tin hoặc không biết câu trả lời, hãy thành thật nói rằng bạn không có thông tin đó.
        - Nếu thông tin không chính xác hoặc không đầy đủ, hãy nói rõ rằng bạn chỉ có thông tin giới hạn.
        - Khi khách hàng yêu cầu tư vấn sản phẩm, hãy hỏi từ yêu cầu một, không hỏi nhiều thông tin cùng lúc, hỏi thông tin tối đa 3 lần.

        ĐỊNH DẠNG PHẢN HỒI:
        - Sử dụng định dạng Markdown để trình bày thông tin rõ ràng, có cấu trúc.
        - Sử dụng tiêu đề, danh sách, và đoạn văn để phân chia thông tin.
        - KHÔNG bao giờ cung cấp thông tin mơ hồ hoặc không có giá trị thực tế.

        ĐỊNH DẠNG PHẢN HỒI STRUCTURED:
        - Chỉ trả lời bằng văn bản thông thường, KHÔNG sử dụng format đặc biệt nào.
        - KHÔNG đề cập đến hình ảnh hoặc URL trong phản hồi văn bản.
        - Tập trung vào việc cung cấp thông tin hữu ích và tư vấn cho khách hàng.
        - Hệ thống sẽ tự động xử lý việc hiển thị sản phẩm dựa trên ngữ cảnh.
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
            products = search_products(message)
            context["recommended_products"] = products

        return context

    def format_product_info(self, product):
        """Helper function to format product information"""
        info = f"- Tên: {product['title']}\n"
        info += f"  Mô tả: {product.get('description', 'Không có mô tả')}\n"
        info += f"  Giá: {product['price']} USD"
        if product.get('percentOff', 0) > 0:
            info += f" (Giảm giá: {product['percentOff']}%)\n"
        else:
            info += "\n"

        if "category" in product and "name" in product["category"]:
            info += f"  Danh mục: {product['category']['name']}\n"

        if "variations" in product and product["variations"]:
            info += "  Biến thể:\n"
            for variation in product["variations"][:3]:
                info += f"    * {variation.get('sku', 'Không xác định')}: {variation.get('price', 0)} USD"
                if variation.get('percentOff', 0) > 0:
                    info += f" (Giảm giá: {variation['percentOff']}%)"
                info += "\n"


        return info

    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Định dạng ngữ cảnh để đưa vào prompt"""
        formatted_context = "Thông tin từ cơ sở dữ liệu:\n"

        if "products" in context and context["products"]:
            formatted_context += "\nSản phẩm:\n"
            for product in context["products"]:
                formatted_context += self.format_product_info(product)

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
                formatted_context += self.format_product_info(product)

        if "orders" in context and context["orders"]:
            formatted_context += "\nĐơn hàng:\n"
            for order in context["orders"]:
                formatted_context += f"- Mã đơn hàng: {order['id']}\n"
                formatted_context += f"  Trạng thái: {order['status']}\n"
                formatted_context += f"  Tổng tiền: {order['total_amount']} USD\n"
                formatted_context += "  Sản phẩm:\n"
                for product in order["products"]:
                    formatted_context += f"    + {product.get('title', 'Sản phẩm')} - Số lượng: {product['quantity']}"
                    if "variation" in product:
                        formatted_context += f" - Biến thể: {product['variation']}"
                    if "finalPrice" in product:
                        formatted_context += f" - Giá: {product['finalPrice']} USD"
                    formatted_context += "\n"

        return formatted_context

    def process_message(self, message: str, session: UserSession) -> Dict[str, Any]:
        """Xử lý tin nhắn từ người dùng và trả về phản hồi có cấu trúc"""
        intent = self.classify_intent(message)

        context = session.context
        if intent == "order_management" and "user_id" in context:
            print("Order management")
            user_id = context["user_id"]
            orders = get_user_orders(user_id)
            context["orders"] = orders

        retrieved_context = self.retrieve_context(message, intent)
        context.update(retrieved_context)
        session.context = context
        formatted_context = self.format_context_for_prompt(context)
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

        response = self.model.generate_content(prompt)
        message_text = response.text.strip()

        structured_response = {
            "message": message_text,
            "data": []
        }

        if intent in ["product_inquiry", "product_recommendation"] and "products" in context:
            structured_response["data"] = self.format_products_data(context["products"])
        elif intent == "product_recommendation" and "recommended_products" in context:
            structured_response["data"] = self.format_products_data(context["recommended_products"])
        elif intent == "order_management" and "orders" in context:
            structured_response["data"] = self.format_orders_data(context["orders"])

        return structured_response

    def format_products_data(self, products: List[Dict]) -> List[Dict]:
        """Format products data for structured response"""
        formatted_products = []
        for product in products:
            # Lấy hình ảnh đầu tiên
            image_url = None
            if "images" in product and product["images"]:
                image_url = product["images"][0].get("filePath") if "filePath" in product["images"][0] else None

            # Lấy giá từ variation mặc định hoặc giá gốc
            price = product.get("price", 0)
            if "variations" in product and product["variations"]:
                default_variation = next((var for var in product["variations"] if var.get("isDefault", False)), None)
                if default_variation:
                    price = default_variation.get("finalPrice", default_variation.get("price", price))

            formatted_product = {
                "id": product["id"],
                "title": product["title"],
                "description": product.get("description", ""),
                "price": price,
                "originalPrice": product.get("price", 0),
                "percentOff": product.get("percentOff", 0),
                "image": image_url,
                "category": product["category"]["name"] if "category" in product and "name" in product["category"] else "Unknown",
                "slug": product.get("slug", ""),
                "sold": product.get("sold", 0)
            }
            formatted_products.append(formatted_product)

        return formatted_products

    def format_orders_data(self, orders: List[Dict]) -> List[Dict]:
        """Format orders data for structured response"""
        formatted_orders = []
        for order in orders:
            formatted_order = {
                "id": order["id"],
                "status": order["status"],
                "total_amount": order["total_amount"],
                "created_at": order.get("created_at", ""),
                "products": []
            }

            for product in order.get("products", []):
                formatted_product = {
                    "id": product.get("product_id", ""),
                    "title": product.get("title", ""),
                    "quantity": product.get("quantity", 0),
                    "price": product.get("finalPrice", product.get("price", 0)),
                    "image": product.get("image", None),
                    "variation": product.get("variation", "")
                }
                formatted_order["products"].append(formatted_product)

            formatted_orders.append(formatted_order)

        return formatted_orders
