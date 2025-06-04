from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import os
from typing import List, Any, Optional, Union, Literal, Dict
import socketio
import uuid # Ensure uuid is imported
import yaml
import aiofiles
import asyncio
from contextlib import asynccontextmanager

from autogen_core import AgentId, SingleThreadedAgentRuntime, UserMessage, LLMMessage
from autogen_core.models import ChatCompletionClient
from .autogen_agent import MyDataDiscoveryAgent, STREAM_DONE

# Load environment variables from .env file, if present
load_dotenv()

# --- Global Variables (condensed) ---
runtime: SingleThreadedAgentRuntime | None = None
model_client_global: Optional[ChatCompletionClient] = None
data_discovery_agent_global: MyDataDiscoveryAgent | None = None

# --- Lifespan Management (condensed for plan, using verified logic) ---
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    global runtime, model_client_global, data_discovery_agent_global
    print("FastAPI app starting up...")
    model_config_path = "model_config.yaml"
    try:
        async with aiofiles.open(model_config_path, "r") as file: model_config_content = await file.read()
        if not model_config_content.strip(): print(f"Warning: {model_config_path} is empty.")
        else:
            model_config = yaml.safe_load(model_config_content)
            if model_config and model_config.get('provider'):
                if model_config.get('config', {}).get('api_key') == 'REPLACE_WITH_YOUR_API_KEY': print(f"Warning: API key placeholder in {model_config_path}.")
                else: model_client_global = ChatCompletionClient.load_component(model_config); print(f"Loaded model client from {model_config_path}")
            else: print(f"Warning: Could not load model client config from {model_config_path}.")
    except FileNotFoundError: print(f"Warning: {model_config_path} not found. LLM disabled.")
    except Exception as e: print(f"Error loading model config: {e}")
    runtime = SingleThreadedAgentRuntime()
    if model_client_global:
        data_discovery_agent_global = MyDataDiscoveryAgent(name="DataDiscoveryAssistant", model_client=model_client_global)
        await MyDataDiscoveryAgent.register(runtime, "data_agent", lambda: data_discovery_agent_global)
        print("MyDataDiscoveryAgent instance created and registered.")
    else: print("Skipping agent registration.")
    runtime.start(); print("AutoGen runtime started.")
    yield
    print("FastAPI app shutting down...")
    if runtime: await runtime.stop(); print("AutoGen runtime stopped.")

# Initialize FastAPI app with lifespan manager
app = FastAPI(title="Data Discovery Chat Backend (Python)", lifespan=lifespan)

# --- CORS & Socket.IO (condensed) ---
http_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080", "http://127.0.0.1:8080"]
app.add_middleware(CORSMiddleware, allow_origins=http_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=http_origins)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# --- Helper function for streaming agent responses (UPDATED) ---
async def stream_responses_to_client(sid: str, queue: asyncio.Queue):
    print(f"Starting to stream responses to client {sid}")
    accumulated_chat_response = ""
    current_chat_message_id: Optional[str] = None # Initialize to None
    first_chat_chunk = True

    while True:
        item = await queue.get()

        if item is STREAM_DONE:
            print(f"Stream finished for client {sid}. Full chat response: {accumulated_chat_response}")
            if current_chat_message_id is not None: # Only send end if a chat stream started
                sender_type = "ai_error" if accumulated_chat_response.startswith("ERROR:") else "ai"
                await sio.emit('ai_message_end', {
                    "id": current_chat_message_id,
                    "sender": sender_type,
                    "full_response": accumulated_chat_response
                }, room=sid)
            break

        if not isinstance(item, dict) or "stream_type" not in item:
            print(f"Warning: Received unexpected item from queue for {sid}: {item}")
            queue.task_done()
            continue

        stream_type = item.get("stream_type")
        event_data = item.get("data")
        artifact_id = item.get("artifact_id")

        if stream_type == "artifact_start":
            metadata = item.get("metadata", {})
            artifact_type_from_event = item.get("artifact_type", "unknown") # Renamed to avoid conflict
            await sio.emit('artifact_stream_start', {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type_from_event,
                "metadata": metadata
            }, room=sid)
            print(f"Sent 'artifact_stream_start' to {sid} for artifact {artifact_id}")
        elif stream_type == "artifact_chunk":
            await sio.emit('artifact_stream_chunk', {
                "artifact_id": artifact_id,
                "chunk_data": event_data
            }, room=sid)
        elif stream_type == "artifact_end":
            await sio.emit('artifact_stream_end', {"artifact_id": artifact_id}, room=sid)
            print(f"Sent 'artifact_stream_end' to {sid} for artifact {artifact_id}")
        elif stream_type == "chat_chunk":
            if first_chat_chunk:
                current_chat_message_id = str(uuid.uuid4())
            text_chunk = str(event_data)
            accumulated_chat_response += text_chunk
            await sio.emit('ai_message_chunk', {
                "id": current_chat_message_id,
                "text": text_chunk,
                "sender": "ai",
                "is_first_chunk": first_chat_chunk
            }, room=sid)
            first_chat_chunk = False
        elif stream_type == "error":
            if first_chat_chunk:
                current_chat_message_id = str(uuid.uuid4())
            error_text = str(event_data)
            accumulated_chat_response += error_text # Include error in final accumulated chat for logging
            await sio.emit('ai_message_chunk', {
                "id": current_chat_message_id,
                "text": error_text,
                "sender": "ai_error",
                "is_first_chunk": first_chat_chunk
            }, room=sid)
            first_chat_chunk = False
            print(f"Sent error chunk as 'ai_message_chunk' to {sid}: {error_text}")
        else:
            print(f"Warning: Unknown stream_type '{stream_type}' from queue for {sid}")

        queue.task_done()

# --- Socket.IO Event Handlers (condensed) ---
@sio.event
async def connect(sid, environ): print(f"Socket.IO Client connected: {sid}")
@sio.event
async def disconnect(sid): print(f"Socket.IO Client disconnected: {sid}")
@sio.on('send_chat_message')
async def handle_socket_chat_message(sid, data):
    user_message_text = data.get("message")
    global data_discovery_agent_global, runtime, model_client_global
    if not user_message_text: await sio.emit('ai_message_end', {"id": str(uuid.uuid4()), "sender": "ai_error", "full_response": "Error: No message text provided."}, room=sid); return
    if not runtime or not model_client_global or not data_discovery_agent_global: await sio.emit('ai_message_end', {"id": str(uuid.uuid4()), "sender": "ai_error", "full_response": "AI service not configured."}, room=sid); return
    response_queue = asyncio.Queue()
    user_llm_message = UserMessage(content=user_message_text)
    try:
        asyncio.create_task(data_discovery_agent_global.handle_chat_message(user_llm_message, response_queue))
        asyncio.create_task(stream_responses_to_client(sid, response_queue))
    except Exception as e: await sio.emit('ai_message_end', {"id": str(uuid.uuid4()), "sender": "ai_error", "full_response": str(e)}, room=sid)

# --- Pydantic Models & Other Endpoints (condensed) ---
class ChatMessageRequest(BaseModel): message: str
class ChatApiResponse(BaseModel): success: bool; message: str
class ArtifactRequest(BaseModel): query: str
class DataArtifactContentData(BaseModel): columns: List[str]; rows: List[List[Any]]
class CodeArtifactResponse(BaseModel): type: Literal["code"]; language: str; content: str
class DataArtifactResponse(BaseModel): type: Literal["data"]; format: str; title: Optional[str] = None; content: DataArtifactContentData
class MessageArtifactResponse(BaseModel): type: Literal["message"]; content: str
ArtifactResponseUnion = Union[CodeArtifactResponse, DataArtifactResponse, MessageArtifactResponse]
@app.get("/")
async def read_root(): return {"message": "Python backend is running!"}
@app.post("/api/chat", response_model=ChatApiResponse, deprecated=True)
async def http_handle_chat_message(chat_request: ChatMessageRequest): return ChatApiResponse(success=False, message="This HTTP chat endpoint is deprecated. Please use WebSocket.")
@app.post("/api/generate-artifact", response_model=MessageArtifactResponse)
async def handle_generate_artifact(request_data: ArtifactRequest): return MessageArtifactResponse(type="message", content="Artifact generation via this direct endpoint is under review for AutoGen integration...")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:socket_app", host="0.0.0.0", port=port, reload=True)
