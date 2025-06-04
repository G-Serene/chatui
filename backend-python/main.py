from fastapi import FastAPI
# Removed duplicate FastAPI import
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import os
from typing import List, Any, Optional, Union, Literal
import socketio
import uuid # Added import for uuid

# Load environment variables from .env file, if present
load_dotenv()

app = FastAPI(title="Data Discovery Chat Backend (Python)")


# --- CORS Configuration for FastAPI HTTP requests ---
http_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",    # Dockerized frontend port used in docker-compose
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=http_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Socket.IO Server Setup ---
sio_cors_allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=sio_cors_allowed_origins)
# Wrap FastAPI app with Socket.IO's ASGI application
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


# --- Socket.IO Event Handlers ---
@sio.event
async def connect(sid, environ):
    print(f"Socket.IO Client connected: {sid}")
    # You can also access environ for request details, e.g., headers
    # print(f"Connection environment: {environ}")

@sio.event
async def disconnect(sid):
    print(f"Socket.IO Client disconnected: {sid}")

# Optional: A generic message handler for basic testing
# @sio.event
# async def message(sid, data):
#     print(f"Socket.IO message from {sid}: {data}")
#     await sio.emit('reply', f"Server received: {data}", room=sid)


# --- Pydantic Models for /api/chat ---
class ChatMessageRequest(BaseModel):
    message: str

class ChatApiResponse(BaseModel):
    success: bool
    message: str
    # Potentially add a session ID or user ID if needed for targeted WebSocket emits
    # sid: Optional[str] = None 

# --- Pydantic Models for /api/generate-artifact ---
class ArtifactRequest(BaseModel):
    query: str

# Specific content models
class DataArtifactContentData(BaseModel):
    columns: List[str]
    rows: List[List[Any]]

# Response models for each artifact type
class CodeArtifactResponse(BaseModel):
    type: Literal["code"]
    language: str
    content: str

class DataArtifactResponse(BaseModel):
    type: Literal["data"]
    format: str
    title: Optional[str] = None
    content: DataArtifactContentData

class MessageArtifactResponse(BaseModel):
    type: Literal["message"]
    content: str

# Union of possible artifact responses
ArtifactResponseUnion = Union[CodeArtifactResponse, DataArtifactResponse, MessageArtifactResponse]

# --- Mock Artifact Data ---
mock_artifacts_data = [
    {
        "id": "sales-data-table",
        "description": "A mock JSON data table for sales figures.",
        "keywords": ["sales", "revenue", "table", "data", "report"],
        "artifact": {
            "type": "data",
            "format": "json",
            "title": "Quarterly Sales Report",
            "content": {
                "columns": ["Quarter", "Product Category", "Total Sales", "Units Sold"],
                "rows": [
                    ["Q1 2024", "Electronics", 150000, 350],
                    ["Q1 2024", "Appliances", 120000, 200],
                    ["Q2 2024", "Electronics", 175000, 400],
                    ["Q2 2024", "Appliances", 110000, 180],
                ]
            }
        }
    },
    {
        "id": "product-inventory-table",
        "description": "A mock JSON data table for product inventory.",
        "keywords": ["product", "inventory", "stock", "table", "data"],
        "artifact": {
            "type": "data",
            "format": "json",
            "title": "Product Inventory Levels",
            "content": {
                "columns": ["Product ID", "Name", "Category", "Stock Level", "Reorder Point"],
                "rows": [
                    ["PID001", "Laptop Pro X", "Electronics", 75, 50],
                    ["PID002", "Smart Thermostat", "Home Automation", 120, 100],
                    ["PID003", "Wireless Mouse", "Accessories", 300, 150],
                    ["PID004", "Coffee Maker Deluxe", "Appliances", 45, 50],
                ]
            }
        }
    },
    {
        "id": "python-user-processing-script",
        "description": "A mock Python code snippet for user processing.",
        "keywords": ["python", "user", "script", "code", "processing", "analysis"],
        "artifact": {
            "type": "code",
            "language": "python",
            "content": "# Mock Python script for user data processing\n\ndef process_users(user_list):\n  active_users = []\n  for user in user_list:\n    if user.get('is_active'):\n      print(f\"Processing active user: {user.get('name')}\")\n      active_users.append(user)\n  return active_users\n\n# Example usage:\n# users = [{'name': 'Alice', 'is_active': True}, {'name': 'Bob', 'is_active': False}]\n# process_users(users)"
        }
    },
    {
        "id": "sql-active-customers-query",
        "description": "A mock SQL query for fetching active customers.",
        "keywords": ["sql", "active", "customer", "query", "database"],
        "artifact": {
            "type": "code",
            "language": "sql",
            "content": "SELECT\n  customer_id,\n  first_name,\n  last_name,\n  email,\n  last_login_date\nFROM\n  customers\nWHERE\n  is_active = TRUE\n  AND last_login_date >= CURRENT_DATE - INTERVAL '30 days'\nORDER BY\n  last_login_date DESC;"
        }
    },
    {
        "id": "javascript-ui-validation-script",
        "description": "A mock JavaScript code snippet for UI form validation.",
        "keywords": ["javascript", "js", "ui", "form", "validation", "script", "code"],
        "artifact": {
            "type": "code",
            "language": "javascript",
            "content": "// Mock JavaScript for UI form validation\n\nfunction validateEmail(email) {\n  if (!email) return false;\n  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\n  return emailRegex.test(email);\n}\n\nfunction validatePassword(password) {\n  if (!password || password.length < 8) return false;\n  // Add more complex rules if needed\n  return true;\n}\n\n// Example usage:\n// const emailInput = document.getElementById('email');\n// const isValid = validateEmail(emailInput.value);\n// console.log('Email is valid:', isValid);"
        }
    }
]

# --- API Endpoints ---
@app.get("/")
async def read_root():
    return {"message": "Python backend is running!"}

@app.post("/api/chat", response_model=ChatApiResponse)
async def handle_chat_message(chat_request: ChatMessageRequest):
    print(f"Received chat message: {chat_request.message}")
    
    user_message_lower = chat_request.message.lower()
    artifact_keywords = ["find", "search", "generate", "show me", "what is", "create", "display"]
    
    ai_reply_text: str
    if any(keyword in user_message_lower for keyword in artifact_keywords):
        ai_reply_text = "I've processed your request. If it's something I can generate an artifact for, you might see it in the artifact window, or you can try a more specific command like 'generate sales data table'."
    else:
        ai_reply_text = f"AI says: You sent '{chat_request.message}'. This is a mock Python AI response."
        
    ai_message_id = str(uuid.uuid4())
    ai_response_data = {
        "id": ai_message_id,
        "text": ai_reply_text,
        "sender": "ai"
    }
    
    # Simulate some processing time before emitting, if desired
    # import asyncio
    # await asyncio.sleep(0.5) 
    
    await sio.emit('ai_message', ai_response_data)
    print(f"Emitted AI message: {ai_response_data}")
    
    return ChatApiResponse(success=True, message="Message received and is being processed")

@app.post("/api/generate-artifact", response_model=ArtifactResponseUnion)
async def generate_artifact(request_data: ArtifactRequest):
    query = request_data.query.lower()
    print(f"Received artifact generation query: \"{request_data.query}\"")

    for item in mock_artifacts_data:
        if any(keyword.lower() in query for keyword in item["keywords"]):
            print(f"Matched artifact: \"{item['description']}\" based on query keywords.")
            return item["artifact"]

    print("No specific artifact matched. Returning default message.")
    return MessageArtifactResponse(
        type="message",
        content="No specific artifact could be generated for your query. Please try phrases like 'generate sales table' or 'show python script for users'."
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    # Use "main:socket_app" to run the combined FastAPI and Socket.IO app
    uvicorn.run("main:socket_app", host="0.0.0.0", port=port, reload=True)
