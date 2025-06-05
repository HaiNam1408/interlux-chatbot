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
    last_activity: datetime = datetime.now()

    def add_message(self, role: Literal["user", "bot"], content: str):
        self.messages.append(ChatMessage(role=role, content=content))

    def get_messages(self):
        return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()}
                for msg in self.messages]

    def get_chat_history(self):
        return "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in self.messages])

class ProductModel(BaseModel):
    file: str
    format: str

class Product(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    price: float
    percentOff: Optional[int] = 0
    sold: Optional[int] = 0
    attributes: Dict[str, str] = {}
    category: str
    model: Optional[ProductModel] = None
    images: List[str] = []
    sort: Optional[int] = 0
    status: str = "PUBLISHED"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

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
