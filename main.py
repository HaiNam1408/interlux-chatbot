import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import uuid

from src.chatbot import Chatbot
from src.database import (
    get_user_orders, get_user_by_id, get_products, get_product_by_id,
    get_policies, get_faqs, search_products, search_policies, search_faqs,
    add_product, update_product, delete_product,
    add_policy, update_policy, delete_policy,
    add_faq, update_faq, delete_faq
)
from src.models import ChatMessage, UserSession, Product, Policy, FAQ

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Interlux Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Initialize chatbot
chatbot = Chatbot()

# Store user sessions
user_sessions = {}

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(
    message: str = Form(...),
    user_id: Optional[str] = Form(None)
):
    if not user_id:
        # Generate a random user ID if not provided
        import uuid
        user_id = str(uuid.uuid4())
        user_sessions[user_id] = UserSession(user_id=user_id)

    # Get user session or create new one
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id=user_id)

    session = user_sessions[user_id]

    # Add user message to history
    session.add_message("user", message)

    # Get response from chatbot
    response = chatbot.process_message(message, session)

    # Add bot response to history
    session.add_message("bot", response)

    return {
        "response": response,
        "user_id": user_id,
        "history": session.get_messages()
    }

@app.get("/orders/{user_id}")
async def get_orders(user_id: str):
    # Get user orders from database
    orders = get_user_orders(user_id)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")
    return {"orders": orders}

# API endpoints for products
@app.get("/api/products")
async def api_get_products():
    """Get all products"""
    return {"products": get_products()}

@app.get("/api/products/{product_id}")
async def api_get_product(product_id: str):
    """Get a specific product by ID"""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}

@app.post("/api/products")
async def api_create_product(product: Product):
    """Create a new product"""
    success = add_product(product.model_dump())
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create product")
    return {"message": "Product created successfully", "product": product}

@app.put("/api/products/{product_id}")
async def api_update_product(product_id: str, product: Product):
    """Update an existing product"""
    success = update_product(product_id, product.model_dump())
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully", "product": product}

@app.delete("/api/products/{product_id}")
async def api_delete_product(product_id: str):
    """Delete a product"""
    success = delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@app.get("/api/search/products")
async def api_search_products(q: str, limit: int = 5):
    """Search for products"""
    products = search_products(q, limit)
    return {"products": products}

# API endpoints for policies
@app.get("/api/policies")
async def api_get_policies():
    """Get all policies"""
    return {"policies": get_policies()}

@app.post("/api/policies")
async def api_create_policy(policy: Policy):
    """Create a new policy"""
    success = add_policy(policy.model_dump())
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create policy")
    return {"message": "Policy created successfully", "policy": policy}

@app.put("/api/policies/{policy_id}")
async def api_update_policy(policy_id: str, policy: Policy):
    """Update an existing policy"""
    success = update_policy(policy_id, policy.model_dump())
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy updated successfully", "policy": policy}

@app.delete("/api/policies/{policy_id}")
async def api_delete_policy(policy_id: str):
    """Delete a policy"""
    success = delete_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted successfully"}

@app.get("/api/search/policies")
async def api_search_policies(q: str, limit: int = 3):
    """Search for policies"""
    policies = search_policies(q, limit)
    return {"policies": policies}

# API endpoints for FAQs
@app.get("/api/faqs")
async def api_get_faqs():
    """Get all FAQs"""
    return {"faqs": get_faqs()}

@app.post("/api/faqs")
async def api_create_faq(faq: FAQ):
    """Create a new FAQ"""
    success = add_faq(faq.model_dump())
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create FAQ")
    return {"message": "FAQ created successfully", "faq": faq}

@app.put("/api/faqs/{faq_id}")
async def api_update_faq(faq_id: str, faq: FAQ):
    """Update an existing FAQ"""
    success = update_faq(faq_id, faq.model_dump())
    if not success:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"message": "FAQ updated successfully", "faq": faq}

@app.delete("/api/faqs/{faq_id}")
async def api_delete_faq(faq_id: str):
    """Delete a FAQ"""
    success = delete_faq(faq_id)
    if not success:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"message": "FAQ deleted successfully"}

@app.get("/api/search/faqs")
async def api_search_faqs(q: str, limit: int = 3):
    """Search for FAQs"""
    faqs = search_faqs(q, limit)
    return {"faqs": faqs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
