# Petshop API

This is a FastAPI application and Python scripts for POC and tests fo ChromaDB, Milvus, LangChain, LangGraph, Helm, Azure OoenAI, Azure AI Foundry, AKS, ect

## Project Structure

```
petshopapiPython
├── petshopapi
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── logger_config.py
│   ├── requirements.txt
│   └── routes
│       └── item_routes.py
│       └── sale_routes.py
│   └── loaders
│       └── sale_loader.py
├── Dockerfile
└── README.md
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd petshopapi
   ```

2. **Install dependencies**:
   You can install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   You can run the application using Uvicorn:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Docker Instructions

To build and run the application using Docker, follow these steps:

1. **Build the Docker image**:
   ```
   docker build -t petshopapi .
   ```

2. **Run the Docker container**:
   ```
   docker run -d -p 8000:8000 petshopapi
   ```

## API Endpoints

- `GET /{item_id}`: Retrieve an item by its ID. Optionally, you can include a query parameter `q` for additional filtering.

## License

This project is licensed under the MIT License.
