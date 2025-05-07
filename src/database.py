import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Create data directory if it doesn't exist
os.makedirs("./data", exist_ok=True)

# Try to import ChromaDB
try:
    import chromadb
    from chromadb.utils import embedding_functions

    # Kiểm tra xem có đang chạy trong Docker không
    CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT = os.getenv("CHROMA_PORT", "8001")

    # Nếu chạy trong Docker, sử dụng HTTP client để kết nối với ChromaDB container
    # Nếu không, sử dụng PersistentClient với đường dẫn local
    if CHROMA_HOST != "localhost":
        print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        print("Connected to ChromaDB via HTTP!")
    else:
        # Initialize ChromaDB with local path
        CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        print(f"Connected to ChromaDB at local path: {CHROMA_DB_PATH}")

    # Set up embedding function
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
PRODUCTS_FILE = "./data/products.json"
USERS_FILE = "./data/users.json"
ORDERS_FILE = "./data/orders.json"
POLICIES_FILE = "./data/policies.json"
FAQS_FILE = "./data/faqs.json"

# Create data directory if it doesn't exist
os.makedirs("./data", exist_ok=True)

# Initialize data files if they don't exist
def initialize_data_files():
    # Sample products
    if not os.path.exists(PRODUCTS_FILE):
        sample_products = [
            {
                "id": "p1",
                "name": "Sofa Elegance",
                "description": "Sofa cao cấp với chất liệu da thật, thiết kế hiện đại và sang trọng.",
                "price": 25000000,
                "category": "sofa",
                "features": ["Da thật", "Khung gỗ sồi", "Bảo hành 5 năm"]
            },
            {
                "id": "p2",
                "name": "Bàn ăn Harmony",
                "description": "Bàn ăn gỗ sồi tự nhiên, thiết kế tinh tế, phù hợp cho gia đình 6 người.",
                "price": 15000000,
                "category": "bàn ăn",
                "features": ["Gỗ sồi tự nhiên", "Kích thước 180x90cm", "Bảo hành 3 năm"]
            },
            {
                "id": "p3",
                "name": "Giường ngủ Luxury",
                "description": "Giường ngủ king size với đầu giường bọc da, thiết kế sang trọng.",
                "price": 35000000,
                "category": "giường ngủ",
                "features": ["Kích thước 200x200cm", "Đầu giường bọc da", "Khung gỗ tự nhiên", "Bảo hành 5 năm"]
            }
        ]
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(sample_products, f, ensure_ascii=False, indent=4)

        # Add products to vector database if enabled
        if VECTOR_DB_ENABLED:
            try:
                for product in sample_products:
                    product_text = f"{product['name']}: {product['description']} Giá: {product['price']} VND. Danh mục: {product['category']}. Tính năng: {', '.join(product['features'])}"
                    product_collection.add(
                        documents=[product_text],
                        metadatas=[product],
                        ids=[product["id"]]
                    )
                print(f"Added {len(sample_products)} products to vector database")
            except Exception as e:
                print(f"Error adding products to vector database: {e}")

    # Sample users
    if not os.path.exists(USERS_FILE):
        sample_users = [
            {
                "id": "u1",
                "name": "Nguyễn Văn A",
                "email": "nguyenvana@example.com",
                "phone": "0901234567"
            },
            {
                "id": "u2",
                "name": "Trần Thị B",
                "email": "tranthib@example.com",
                "phone": "0909876543"
            }
        ]
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(sample_users, f, ensure_ascii=False, indent=4)

    # Sample orders
    if not os.path.exists(ORDERS_FILE):
        sample_orders = [
            {
                "id": "o1",
                "user_id": "u1",
                "products": [
                    {"product_id": "p1", "quantity": 1, "price": 25000000}
                ],
                "total_amount": 25000000,
                "status": "Đã giao hàng",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "o2",
                "user_id": "u2",
                "products": [
                    {"product_id": "p2", "quantity": 1, "price": 15000000},
                    {"product_id": "p3", "quantity": 1, "price": 35000000}
                ],
                "total_amount": 50000000,
                "status": "Đang xử lý",
                "created_at": datetime.now().isoformat()
            }
        ]
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(sample_orders, f, ensure_ascii=False, indent=4)

    # Sample policies
    if not os.path.exists(POLICIES_FILE):
        sample_policies = [
            {
                "id": "pol1",
                "title": "Chính sách bảo hành",
                "content": "Tất cả sản phẩm nội thất của Interlux đều được bảo hành từ 1-5 năm tùy theo loại sản phẩm. Khách hàng cần giữ hóa đơn và phiếu bảo hành để được hỗ trợ khi cần thiết."
            },
            {
                "id": "pol2",
                "title": "Chính sách đổi trả",
                "content": "Khách hàng có thể đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng nếu sản phẩm có lỗi từ nhà sản xuất. Sản phẩm đổi trả phải còn nguyên vẹn, không có dấu hiệu đã qua sử dụng."
            },
            {
                "id": "pol3",
                "title": "Chính sách vận chuyển",
                "content": "Interlux cung cấp dịch vụ vận chuyển miễn phí trong nội thành Hà Nội và TP.HCM cho đơn hàng từ 10 triệu đồng. Đối với các tỉnh thành khác, phí vận chuyển sẽ được tính dựa trên khoảng cách và khối lượng sản phẩm."
            },
            {
                "id": "pol4",
                "title": "Chính sách thanh toán",
                "content": "Khách hàng có thể thanh toán bằng tiền mặt, chuyển khoản ngân hàng, hoặc thẻ tín dụng. Đối với đơn hàng trên 50 triệu đồng, khách hàng có thể thanh toán trả góp với lãi suất 0% trong 6 tháng đầu."
            }
        ]
        with open(POLICIES_FILE, "w", encoding="utf-8") as f:
            json.dump(sample_policies, f, ensure_ascii=False, indent=4)

        # Add policies to vector database if enabled
        if VECTOR_DB_ENABLED:
            try:
                for policy in sample_policies:
                    policy_collection.add(
                        documents=[f"{policy['title']}: {policy['content']}"],
                        metadatas=[policy],
                        ids=[policy["id"]]
                    )
                print(f"Added {len(sample_policies)} policies to vector database")
            except Exception as e:
                print(f"Error adding policies to vector database: {e}")

    # Sample FAQs
    if not os.path.exists(FAQS_FILE):
        sample_faqs = [
            {
                "id": "faq1",
                "question": "Làm thế nào để đặt hàng?",
                "answer": "Khách hàng có thể đặt hàng trực tiếp trên website, qua hotline 1900xxxx, hoặc đến trực tiếp showroom của Interlux."
            },
            {
                "id": "faq2",
                "question": "Thời gian giao hàng là bao lâu?",
                "answer": "Thời gian giao hàng thông thường là 3-5 ngày đối với sản phẩm có sẵn, và 15-30 ngày đối với sản phẩm đặt hàng riêng."
            },
            {
                "id": "faq3",
                "question": "Có dịch vụ lắp đặt không?",
                "answer": "Có, Interlux cung cấp dịch vụ lắp đặt miễn phí cho tất cả các sản phẩm nội thất."
            },
            {
                "id": "faq4",
                "question": "Làm thế nào để chăm sóc và bảo quản sản phẩm nội thất?",
                "answer": "Mỗi sản phẩm sẽ có hướng dẫn chăm sóc và bảo quản riêng. Nhìn chung, nên tránh ánh nắng trực tiếp, độ ẩm cao, và vệ sinh thường xuyên bằng các sản phẩm chuyên dụng."
            }
        ]
        with open(FAQS_FILE, "w", encoding="utf-8") as f:
            json.dump(sample_faqs, f, ensure_ascii=False, indent=4)

        # Add FAQs to vector database if enabled
        if VECTOR_DB_ENABLED:
            try:
                for faq in sample_faqs:
                    faq_collection.add(
                        documents=[f"Câu hỏi: {faq['question']} Trả lời: {faq['answer']}"],
                        metadatas=[faq],
                        ids=[faq["id"]]
                    )
                print(f"Added {len(sample_faqs)} FAQs to vector database")
            except Exception as e:
                print(f"Error adding FAQs to vector database: {e}")

# Hàm tiện ích để quản lý dữ liệu trong vector database
def add_product_to_vector_db(product):
    """Thêm sản phẩm mới vào vector database"""
    if not VECTOR_DB_ENABLED:
        return False

    try:
        product_text = f"{product['name']}: {product['description']} Giá: {product['price']} VND. Danh mục: {product['category']}. Tính năng: {', '.join(product['features'])}"
        product_collection.add(
            documents=[product_text],
            metadatas=[product],
            ids=[product["id"]]
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
    """Cập nhật sản phẩm trong vector database"""
    if not VECTOR_DB_ENABLED:
        return False

    try:
        # Xóa sản phẩm cũ
        product_collection.delete(ids=[product["id"]])

        # Thêm sản phẩm mới
        product_text = f"{product['name']}: {product['description']} Giá: {product['price']} VND. Danh mục: {product['category']}. Tính năng: {', '.join(product['features'])}"
        product_collection.add(
            documents=[product_text],
            metadatas=[product],
            ids=[product["id"]]
        )
        return True
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

# Initialize data files
initialize_data_files()

# Database functions
def get_products():
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_product_by_id(product_id: str):
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
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

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
    Tìm kiếm sản phẩm dựa trên từ khóa trong query
    Sử dụng vector database nếu có, nếu không sẽ sử dụng tìm kiếm từ khóa đơn giản
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

    # Tìm kiếm sản phẩm có chứa từ khóa trong tên hoặc mô tả
    matched_products = []
    for product in products:
        if (query in product["name"].lower() or
            query in product["description"].lower() or
            query in product["category"].lower()):
            matched_products.append(product)

    # Giới hạn số lượng kết quả
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
                product["name"] = product_details["name"]

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
