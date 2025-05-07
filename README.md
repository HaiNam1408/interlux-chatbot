# Interlux Chatbot

Chatbot hỗ trợ tư vấn bán hàng và trả lời câu hỏi cho hệ thống bán hàng nội thất cao cấp Interlux.

## Tính năng

- Tư vấn bán hàng: Giới thiệu sản phẩm, tính năng, giá cả
- Tư vấn chính sách: Cung cấp thông tin về chính sách bảo hành, đổi trả, vận chuyển, thanh toán
- Quản lý đơn hàng: Giúp khách hàng kiểm tra trạng thái đơn hàng, lịch sử mua hàng
- Trả lời câu hỏi: Giải đáp các thắc mắc của khách hàng về sản phẩm và dịch vụ
- Gợi ý sản phẩm: Đề xuất sản phẩm phù hợp dựa trên nhu cầu của khách hàng

## Công nghệ sử dụng

- FastAPI: Framework web API
- Gemini API: Xử lý ngôn ngữ tự nhiên
- ChromaDB: Vector database cho RAG (Retrieval-Augmented Generation)
- Sentence Transformers: Mô hình nhúng văn bản
- Docker: Containerization

## Cài đặt

### Phương pháp 1: Sử dụng Docker (Khuyến nghị)

1. Clone repository:
```
git clone https://github.com/your-username/interlux-chatbot.git
cd interlux-chatbot
```

2. Tạo file `.env` và thêm API key của Gemini:
```
GOOGLE_API_KEY=your_gemini_api_key_here
CHROMA_HOST=chroma
CHROMA_PORT=8000
```

3. Chạy ứng dụng với Docker Compose:
```
docker-compose up -d
```

4. Truy cập ứng dụng tại: http://localhost:8502
   - ChromaDB UI có thể truy cập tại: http://localhost:8501

### Phương pháp 2: Cài đặt trực tiếp

1. Clone repository:
```
git clone https://github.com/your-username/interlux-chatbot.git
cd interlux-chatbot
```

2. Cài đặt các thư viện cần thiết:
```
pip install -r requirements.txt
```

3. Tạo file `.env` và thêm API key của Gemini:
```
GOOGLE_API_KEY=your_gemini_api_key_here
CHROMA_DB_PATH=./data/chroma_db
```

4. Chạy ứng dụng:
```
python main.py
```

5. Truy cập ứng dụng tại: http://localhost:8502

## Cấu trúc dự án

```
interlux-chatbot/
├── data/                  # Thư mục chứa dữ liệu
│   ├── chroma_db/         # Vector database (khi chạy local)
│   ├── products.json      # Dữ liệu sản phẩm
│   ├── policies.json      # Dữ liệu chính sách
│   ├── faqs.json          # Dữ liệu câu hỏi thường gặp
│   ├── users.json         # Dữ liệu người dùng
│   └── orders.json        # Dữ liệu đơn hàng
├── src/                   # Mã nguồn
│   ├── chatbot.py         # Logic chatbot
│   ├── database.py        # Xử lý dữ liệu
│   └── models.py          # Định nghĩa model
├── static/                # File tĩnh (CSS, JS, hình ảnh)
├── templates/             # Template HTML
│   └── index.html         # Giao diện người dùng
├── .dockerignore          # Cấu hình Docker ignore
├── .env                   # Biến môi trường
├── docker-compose.yml     # Cấu hình Docker Compose
├── Dockerfile             # Cấu hình Docker
├── main.py                # File chính
└── requirements.txt       # Thư viện cần thiết
```

## Hướng dẫn sử dụng

1. Truy cập ứng dụng tại http://localhost:8502
2. Nhập câu hỏi hoặc yêu cầu vào ô chat
3. Chatbot sẽ phân tích ý định và trả lời dựa trên dữ liệu có sẵn
4. Đối với quản lý đơn hàng, chatbot sẽ hiển thị thông tin đơn hàng của người dùng

## Quản lý Docker

### Khởi động dịch vụ
```
docker-compose up -d
```

### Xem logs
```
docker-compose logs -f
```

### Dừng dịch vụ
```
docker-compose down
```

### Xóa dữ liệu và khởi động lại
```
docker-compose down -v
docker-compose up -d
```

## Phát triển thêm

- Thêm xác thực người dùng
- Tích hợp với hệ thống thanh toán
- Thêm tính năng đặt hàng trực tiếp qua chatbot
- Cải thiện giao diện người dùng
- Thêm tính năng phân tích cảm xúc người dùng
- Mở rộng vector database để xử lý dữ liệu lớn hơn
