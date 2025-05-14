# Interlux Chatbot

A chatbot for sales consulting and answering questions for the Interlux luxury furniture sales system.

## Features

- Sales consulting: Introduce products, features, prices
- Policy advising: Provide information about warranty, return, shipping, and payment policies
- Order management: Help customers check order status and purchase history
- Customer Q&A: Answer customer inquiries about products and services
- Product recommendations: Suggest suitable products based on customer needs

## Technologies Used

- FastAPI: Web API framework
- Gemini API: Natural language processing
- ChromaDB: Vector database for RAG (Retrieval-Augmented Generation)
- Sentence Transformers: Text embedding model
- Docker: Containerization

## Installation

### Method 1: Using Docker (Recommended)

1. Clone repository:
```
git clone https://github.com/your-username/interlux-chatbot.git
cd interlux-chatbot
```

2. Create `.env` file and add your Gemini API key:
```
GOOGLE_API_KEY=your_gemini_api_key_here
CHROMA_HOST=chroma
CHROMA_PORT=8000
```

3. Run the application with Docker Compose:
```
docker-compose up -d
```

4. Access the application at: http://localhost:8502
   - ChromaDB UI can be accessed at: http://localhost:8501

### Method 2: Direct Installation

1. Clone repository:
```
git clone https://github.com/your-username/interlux-chatbot.git
cd interlux-chatbot
```

2. Install required libraries:
```
pip install -r requirements.txt
```

3. Create `.env` file and add your Gemini API key:
```
GOOGLE_API_KEY=your_gemini_api_key_here
CHROMA_DB_PATH=./data/chroma_db
```

4. Run the application:
```
python main.py
```

5. Access the application at: http://localhost:8502

## Project Structure

```
interlux-chatbot/
├── data/                  # Data directory
│   ├── chroma_db/         # Vector database (when running locally)
│   ├── products.json      # Product data
│   ├── policies.json      # Policy data
│   ├── faqs.json          # FAQ data
│   ├── users.json         # User data
│   └── orders.json        # Order data
├── src/                   # Source code
│   ├── chatbot.py         # Chatbot logic
│   ├── database.py        # Data handling
│   └── models.py          # Model definitions
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
│   └── index.html         # User interface
├── .dockerignore          # Docker ignore configuration
├── .env                   # Environment variables
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker configuration
├── main.py                # Main file
└── requirements.txt       # Required libraries
```

## Usage Guide

1. Access the application at http://localhost:8502
2. Enter your question or request in the chat box
3. The chatbot will analyze your intent and respond based on available data
4. For order management, the chatbot will display the user's order information

## Docker Management

### Start services
```
docker-compose up -d
```

### View logs
```
docker-compose logs -f
```

### Stop services
```
docker-compose down
```

### Delete data and restart
```
docker-compose down -v
docker-compose up -d
```

## Future Development

- Add user authentication
- Integrate with payment systems
- Add direct ordering through the chatbot
- Improve user interface
- Add user sentiment analysis
- Expand vector database to handle larger datasets
