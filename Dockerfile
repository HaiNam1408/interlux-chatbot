FROM python:3.12-slim

WORKDIR /app

# Cài đặt các gói phụ thuộc
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Sao chép requirements.txt trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code vào container
COPY . .

# Mở cổng cho ứng dụng
EXPOSE 8000

# Khởi chạy ứng dụng
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
