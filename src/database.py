import os
import json
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Try to import ChromaDB
try:
    import chromadb
    from chromadb.utils import embedding_functions

    CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT = os.getenv("CHROMA_PORT", "8001")

    if CHROMA_HOST != "localhost":
        print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        print("Connected to ChromaDB via HTTP!")
    else:
        CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        print(f"Connected to ChromaDB at local path: {CHROMA_DB_PATH}")

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Create collections if they don't exist
    try:
        product_collection = client.get_collection("products")
        print("Found existing products collection")
    except:
        print("Creating new products collection")
        product_collection = client.create_collection(
            name="products",
            embedding_function=embedding_function
        )

    try:
        policy_collection = client.get_collection("policies")
        print("Found existing policies collection")
    except:
        print("Creating new policies collection")
        policy_collection = client.create_collection(
            name="policies",
            embedding_function=embedding_function
        )

    try:
        faq_collection = client.get_collection("faqs")
        print("Found existing faqs collection")
    except:
        print("Creating new faqs collection")
        faq_collection = client.create_collection(
            name="faqs",
            embedding_function=embedding_function
        )

    print("ChromaDB initialized successfully!")
    VECTOR_DB_ENABLED = True

except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    print("Falling back to simple keyword search...")
    VECTOR_DB_ENABLED = False

# Sample data storage (in a real application, this would be a database)
DATA_DIR = "./data"
PRODUCTS_FILE = f"{DATA_DIR}/products.json"
USERS_FILE = f"{DATA_DIR}/users.json"
ORDERS_FILE = f"{DATA_DIR}/orders.json"
POLICIES_FILE = f"{DATA_DIR}/policies.json"
FAQS_FILE = f"{DATA_DIR}/faqs.json"

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Helper functions
def create_product_text_for_embedding(product):
    """Create text representation of product for embedding"""
    category_name = product["category"]["name"] if "category" in product and "name" in product["category"] else "Unknown"

    product_text = f"{product['title']}: {product.get('description', '')} Price: {product['price']}. Category: {category_name}."

    # Add variations info if available
    if "variations" in product and product["variations"]:
        variations_text = ", ".join([f"{var.get('sku', '')}: {var.get('price', 0)}" for var in product["variations"]])
        product_text += f" Variations: {variations_text}"

    return product_text

def save_json_file(file_path, data):
    """Save data to JSON file"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_json_file(file_path):
    """Load data from JSON file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Function to fetch products from API
def fetch_products_from_api():
    """Fetch products from the API"""
    api_url = "https://interlux-be-dwbhhhf7gkemhzbm.eastasia-01.azurewebsites.net/api/v1/client/product"
    params = {
        "page": 1,
        "limit": 1000,
        "sortBy": "createdAt",
        "sortDirection": "desc"
    }

    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["statusCode"] == 200 and "data" in data and "data" in data["data"]:
                print(f"{data["message"]}")
                return data["data"]["data"]
        print(f"Failed to fetch products from API: {response.status_code}")
        return []
    except Exception as e:
        print(f"Error fetching products from API: {e}")
        return []

# Initialize data files if they don't exist
def initialize_data_files():
    # Products - fetch from API
    api_products = fetch_products_from_api()

    if api_products:
        print(f"Fetched {len(api_products)} products from API")

        # Save to file
        save_json_file(PRODUCTS_FILE, api_products)

        # Add products to vector database if enabled
        if VECTOR_DB_ENABLED:
            try:
                # Clear existing products in vector database
                try:
                    product_collection.delete(where={})
                    print("Cleared existing products from vector database")
                except Exception as e:
                    print(f"Error clearing products from vector database: {e}")

                # Add new products
                for product in api_products:
                    product_text = create_product_text_for_embedding(product)
                    product_collection.add(
                        documents=[product_text],
                        metadatas=[product],
                        ids=[str(product["id"])]
                    )
                print(f"Added {len(api_products)} products to vector database")
            except Exception as e:
                print(f"Error adding products to vector database: {e}")
    else:
        # If API fetch fails, create empty products file
        if not os.path.exists(PRODUCTS_FILE):
            save_json_file(PRODUCTS_FILE, [])

    # Initialize other data files with empty arrays if they don't exist
    for file_path in [USERS_FILE, ORDERS_FILE, POLICIES_FILE, FAQS_FILE]:
        if not os.path.exists(file_path):
            save_json_file(file_path, [])

# Hàm tiện ích để quản lý dữ liệu trong vector database
def add_product_to_vector_db(product):
    """Add a new product to the vector database"""
    if not VECTOR_DB_ENABLED:
        return False

    try:
        product_text = create_product_text_for_embedding(product)
        product_collection.add(
            documents=[product_text],
            metadatas=[product],
            ids=[str(product["id"])]
        )
        return True
    except Exception as e:
        print(f"Error adding product to vector database: {e}")
        return False

def add_policy_to_vector_db(policy):
    """Thêm chính sách mới vào vector database"""
    if not VECTOR_DB_ENABLED:
        return False

    try:
        policy_collection.add(
            documents=[f"{policy['title']}: {policy['content']}"],
            metadatas=[policy],
            ids=[policy["id"]]
        )
        return True
    except Exception as e:
        print(f"Error adding policy to vector database: {e}")
        return False

def add_faq_to_vector_db(faq):
    """Thêm câu hỏi thường gặp mới vào vector database"""
    if not VECTOR_DB_ENABLED:
        return False

    try:
        faq_collection.add(
            documents=[f"Câu hỏi: {faq['question']} Trả lời: {faq['answer']}"],
            metadatas=[faq],
            ids=[faq["id"]]
        )
        return True
    except Exception as e:
        print(f"Error adding FAQ to vector database: {e}")
        return False

def update_product_in_vector_db(product):
    """Update a product in the vector database"""
    if not VECTOR_DB_ENABLED:
        return False

    try:
        # Delete old product
        product_collection.delete(ids=[str(product["id"])])

        # Add new product (reuse the add_product_to_vector_db function)
        return add_product_to_vector_db(product)
    except Exception as e:
        print(f"Error updating product in vector database: {e}")
        return False

def delete_from_vector_db(collection_name, doc_id):
    """Xóa một document từ vector database"""
    if not VECTOR_DB_ENABLED:
        return False

    try:
        if collection_name == "products":
            product_collection.delete(ids=[doc_id])
        elif collection_name == "policies":
            policy_collection.delete(ids=[doc_id])
        elif collection_name == "faqs":
            faq_collection.delete(ids=[doc_id])
        else:
            return False
        return True
    except Exception as e:
        print(f"Error deleting from vector database: {e}")
        return False

# Database functions
def get_products():
    return load_json_file(PRODUCTS_FILE)

def get_product_by_id(product_id):
    """Get a product by ID (accepts both string and integer IDs)"""
    # Convert product_id to int if it's a string containing a number
    if isinstance(product_id, str) and product_id.isdigit():
        product_id = int(product_id)

    products = get_products()
    for product in products:
        if product["id"] == product_id:
            return product
    return None

def add_product(product):
    """Thêm sản phẩm mới vào cơ sở dữ liệu"""
    products = get_products()

    # Kiểm tra xem sản phẩm đã tồn tại chưa
    for existing_product in products:
        if existing_product["id"] == product["id"]:
            return False

    # Thêm sản phẩm mới
    products.append(product)

    # Lưu vào file
    save_json_file(PRODUCTS_FILE, products)

    # Thêm vào vector database
    add_product_to_vector_db(product)

    return True

def update_product(product_id: str, updated_product):
    """Cập nhật sản phẩm trong cơ sở dữ liệu"""
    products = get_products()

    # Tìm và cập nhật sản phẩm
    for i, product in enumerate(products):
        if product["id"] == product_id:
            # Giữ nguyên ID
            updated_product["id"] = product_id
            products[i] = updated_product

            # Lưu vào file
            with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=4)

            # Cập nhật trong vector database
            update_product_in_vector_db(updated_product)

            return True

    return False

def delete_product(product_id: str):
    """Xóa sản phẩm khỏi cơ sở dữ liệu"""
    products = get_products()

    # Tìm và xóa sản phẩm
    for i, product in enumerate(products):
        if product["id"] == product_id:
            del products[i]

            # Lưu vào file
            with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=4)

            # Xóa khỏi vector database
            delete_from_vector_db("products", product_id)

            return True

    return False

def search_products(query: str, limit: int = 5):
    """
    Search for products based on keywords in query
    Uses vector database if available, otherwise falls back to simple keyword search
    """
    if VECTOR_DB_ENABLED:
        try:
            results = product_collection.query(
                query_texts=[query],
                n_results=limit
            )

            if results and results["metadatas"] and len(results["metadatas"][0]) > 0:
                return results["metadatas"][0]
        except Exception as e:
            print(f"Error searching products in vector database: {e}")
            print("Falling back to keyword search...")

    # Fallback to keyword search
    products = get_products()
    query = query.lower()

    # Search for products containing keywords in title, description or category
    matched_products = []
    for product in products:
        # Check in title and description
        if (query in product["title"].lower() or
            query in product.get("description", "").lower() or
            query in product["slug"].lower()):
            matched_products.append(product)
            continue

        # Check in category
        if "category" in product and "name" in product["category"]:
            if query in product["category"]["name"].lower():
                matched_products.append(product)
                continue

        # Check in variations
        if "variations" in product:
            for variation in product["variations"]:
                if "sku" in variation and query in variation["sku"].lower():
                    matched_products.append(product)
                    break

    # Limit the number of results
    return matched_products[:limit]

def get_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_user_by_id(user_id: str):
    users = get_users()
    for user in users:
        if user["id"] == user_id:
            return user
    return None

def get_orders():
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_user_orders(user_id: str):
    orders = get_orders()
    user_orders = [order for order in orders if order["user_id"] == user_id]

    # Enrich orders with product details
    for order in user_orders:
        for product in order["products"]:
            product_details = get_product_by_id(product["product_id"])
            if product_details:
                product["title"] = product_details["title"]
                # Add more product details
                if "images" in product_details and product_details["images"]:
                    product["image"] = product_details["images"][0]["filePath"] if "filePath" in product_details["images"][0] else None
                # Add variation details if available
                if "variations" in product_details:
                    default_variation = next((var for var in product_details["variations"] if var.get("isDefault", False)), None)
                    if default_variation:
                        product["variation"] = default_variation["sku"]
                        product["finalPrice"] = default_variation["finalPrice"]

    return user_orders

def get_policies():
    with open(POLICIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def add_policy(policy):
    """Thêm chính sách mới vào cơ sở dữ liệu"""
    policies = get_policies()

    # Kiểm tra xem chính sách đã tồn tại chưa
    for existing_policy in policies:
        if existing_policy["id"] == policy["id"]:
            return False

    # Thêm chính sách mới
    policies.append(policy)

    # Lưu vào file
    with open(POLICIES_FILE, "w", encoding="utf-8") as f:
        json.dump(policies, f, ensure_ascii=False, indent=4)

    # Thêm vào vector database
    add_policy_to_vector_db(policy)

    return True

def update_policy(policy_id: str, updated_policy):
    """Cập nhật chính sách trong cơ sở dữ liệu"""
    policies = get_policies()

    # Tìm và cập nhật chính sách
    for i, policy in enumerate(policies):
        if policy["id"] == policy_id:
            # Giữ nguyên ID
            updated_policy["id"] = policy_id
            policies[i] = updated_policy

            # Lưu vào file
            with open(POLICIES_FILE, "w", encoding="utf-8") as f:
                json.dump(policies, f, ensure_ascii=False, indent=4)

            # Cập nhật trong vector database
            if VECTOR_DB_ENABLED:
                try:
                    # Xóa chính sách cũ
                    policy_collection.delete(ids=[policy_id])

                    # Thêm chính sách mới
                    policy_collection.add(
                        documents=[f"{updated_policy['title']}: {updated_policy['content']}"],
                        metadatas=[updated_policy],
                        ids=[policy_id]
                    )
                except Exception as e:
                    print(f"Error updating policy in vector database: {e}")

            return True

    return False

def delete_policy(policy_id: str):
    """Xóa chính sách khỏi cơ sở dữ liệu"""
    policies = get_policies()

    # Tìm và xóa chính sách
    for i, policy in enumerate(policies):
        if policy["id"] == policy_id:
            del policies[i]

            # Lưu vào file
            with open(POLICIES_FILE, "w", encoding="utf-8") as f:
                json.dump(policies, f, ensure_ascii=False, indent=4)

            # Xóa khỏi vector database
            delete_from_vector_db("policies", policy_id)

            return True

    return False

def search_policies(query: str, limit: int = 3):
    """
    Tìm kiếm chính sách dựa trên từ khóa trong query
    Sử dụng vector database nếu có, nếu không sẽ sử dụng tìm kiếm từ khóa đơn giản
    """
    if VECTOR_DB_ENABLED:
        try:
            results = policy_collection.query(
                query_texts=[query],
                n_results=limit
            )

            if results and results["metadatas"] and len(results["metadatas"][0]) > 0:
                return results["metadatas"][0]
        except Exception as e:
            print(f"Error searching policies in vector database: {e}")
            print("Falling back to keyword search...")

    # Fallback to keyword search
    policies = get_policies()
    query = query.lower()

    # Tìm kiếm chính sách có chứa từ khóa trong tiêu đề hoặc nội dung
    matched_policies = []
    for policy in policies:
        if (query in policy["title"].lower() or
            query in policy["content"].lower()):
            matched_policies.append(policy)

    # Giới hạn số lượng kết quả
    return matched_policies[:limit]

def get_faqs():
    with open(FAQS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def add_faq(faq):
    """Thêm câu hỏi thường gặp mới vào cơ sở dữ liệu"""
    faqs = get_faqs()

    # Kiểm tra xem câu hỏi đã tồn tại chưa
    for existing_faq in faqs:
        if existing_faq["id"] == faq["id"]:
            return False

    # Thêm câu hỏi mới
    faqs.append(faq)

    # Lưu vào file
    with open(FAQS_FILE, "w", encoding="utf-8") as f:
        json.dump(faqs, f, ensure_ascii=False, indent=4)

    # Thêm vào vector database
    add_faq_to_vector_db(faq)

    return True

def update_faq(faq_id: str, updated_faq):
    """Cập nhật câu hỏi thường gặp trong cơ sở dữ liệu"""
    faqs = get_faqs()

    # Tìm và cập nhật câu hỏi
    for i, faq in enumerate(faqs):
        if faq["id"] == faq_id:
            # Giữ nguyên ID
            updated_faq["id"] = faq_id
            faqs[i] = updated_faq

            # Lưu vào file
            with open(FAQS_FILE, "w", encoding="utf-8") as f:
                json.dump(faqs, f, ensure_ascii=False, indent=4)

            # Cập nhật trong vector database
            if VECTOR_DB_ENABLED:
                try:
                    # Xóa câu hỏi cũ
                    faq_collection.delete(ids=[faq_id])

                    # Thêm câu hỏi mới
                    faq_collection.add(
                        documents=[f"Câu hỏi: {updated_faq['question']} Trả lời: {updated_faq['answer']}"],
                        metadatas=[updated_faq],
                        ids=[faq_id]
                    )
                except Exception as e:
                    print(f"Error updating FAQ in vector database: {e}")

            return True

    return False

def delete_faq(faq_id: str):
    """Xóa câu hỏi thường gặp khỏi cơ sở dữ liệu"""
    faqs = get_faqs()

    # Tìm và xóa câu hỏi
    for i, faq in enumerate(faqs):
        if faq["id"] == faq_id:
            del faqs[i]

            # Lưu vào file
            with open(FAQS_FILE, "w", encoding="utf-8") as f:
                json.dump(faqs, f, ensure_ascii=False, indent=4)

            # Xóa khỏi vector database
            delete_from_vector_db("faqs", faq_id)

            return True

    return False

def search_faqs(query: str, limit: int = 3):
    """
    Tìm kiếm câu hỏi thường gặp dựa trên từ khóa trong query
    Sử dụng vector database nếu có, nếu không sẽ sử dụng tìm kiếm từ khóa đơn giản
    """
    if VECTOR_DB_ENABLED:
        try:
            results = faq_collection.query(
                query_texts=[query],
                n_results=limit
            )

            if results and results["metadatas"] and len(results["metadatas"][0]) > 0:
                return results["metadatas"][0]
        except Exception as e:
            print(f"Error searching FAQs in vector database: {e}")
            print("Falling back to keyword search...")

    # Fallback to keyword search
    faqs = get_faqs()
    query = query.lower()

    # Tìm kiếm FAQ có chứa từ khóa trong câu hỏi hoặc câu trả lời
    matched_faqs = []
    for faq in faqs:
        if (query in faq["question"].lower() or
            query in faq["answer"].lower()):
            matched_faqs.append(faq)

    # Giới hạn số lượng kết quả
    return matched_faqs[:limit]
