from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from datetime import datetime

class ChatMessage(BaseModel):
    role: Literal["user", "bot"]
    content: str
    timestamp: datetime = datetime.now()

class UserSession(BaseModel):
    user_id: str
    messages: List[ChatMessage] = []
    context: Dict = {}

    def add_message(self, role: Literal["user", "bot"], content: str):
        self.messages.append(ChatMessage(role=role, content=content))

    def get_messages(self):
        return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()}
                for msg in self.messages]

    def get_chat_history(self):
        return "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in self.messages])

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    features: List[str] = []

class Order(BaseModel):
    id: str
    user_id: str
    products: List[Dict]
    total_amount: float
    status: str
    created_at: datetime

class User(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None

class Policy(BaseModel):
    id: str
    title: str
    content: str

class FAQ(BaseModel):
    id: str
    question: str
    answer: str
