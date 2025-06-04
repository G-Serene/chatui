from typing import List, Dict, Any, Optional, AsyncGenerator # Added AsyncGenerator
import asyncio
import uuid # Added uuid
from autogen_core import RoutedAgent, MessageContext, SystemMessage, UserMessage, AssistantMessage, LLMMessage
from autogen_core.models import ChatCompletionClient

# Sentinel object to signal the end of the stream
STREAM_DONE = object()

# --- Placeholder Tool Functions for Artifact Generation (Async Generators) ---
async def _generate_mock_code_artifact(query: str) -> AsyncGenerator[Dict[str, Any], None]:
    query_lower = query.lower()
    artifact_generated = False
    if "python" in query_lower and ("user" in query_lower or "processing" in query_lower or "script" in query_lower):
        artifact_id = str(uuid.uuid4())
        yield {"stream_type": "artifact_start", "artifact_id": artifact_id, "artifact_type": "code", "metadata": {"language": "python", "title": "Python User Processing Script"}}
        code_lines = ["# Python script for user data processing", "def process_users(users):", "    active_users = []", "    for user in users:", "        if user.get('is_active'):", "            print(f\"Processing: {user['name']}\")", "            active_users.append(user)", "    return active_users", "", "# Example:", "# my_users = [{'name': 'Alice', 'is_active': True}]", "# process_users(my_users)"]
        for line in code_lines:
            await asyncio.sleep(0.05) # Simulate work
            yield {"stream_type": "artifact_chunk", "artifact_id": artifact_id, "data": line + '\n'}
        artifact_generated = True
    elif "javascript" in query_lower and ("validation" in query_lower or "script" in query_lower):
        artifact_id = str(uuid.uuid4())
        yield {"stream_type": "artifact_start", "artifact_id": artifact_id, "artifact_type": "code", "metadata": {"language": "javascript", "title": "JS Form Validation"}}
        code_lines = ["// JavaScript for form validation", "function validateForm() {", "    const email = document.getElementById('email').value;", "    if (!email.includes('@')) {", "        alert('Invalid email!');", "        return false;", "    }", "    return true;", "}"]
        for line in code_lines:
            await asyncio.sleep(0.05)
            yield {"stream_type": "artifact_chunk", "artifact_id": artifact_id, "data": line + '\n'}
        artifact_generated = True
    elif "sql" in query_lower and ("customer" in query_lower or "query" in query_lower):
        artifact_id = str(uuid.uuid4())
        yield {"stream_type": "artifact_start", "artifact_id": artifact_id, "artifact_type": "code", "metadata": {"language": "sql", "title": "Active Customers Query"}}
        code_lines = ["SELECT customer_id, first_name, email", "FROM customers", "WHERE is_active = TRUE", "  AND last_seen_days < 30;"]
        for line in code_lines:
            await asyncio.sleep(0.05)
            yield {"stream_type": "artifact_chunk", "artifact_id": artifact_id, "data": line + '\n'}
        artifact_generated = True

    if artifact_generated:
        yield {"stream_type": "artifact_end", "artifact_id": artifact_id}
    # If nothing matched, the generator simply stops without yielding artifact_end

async def _generate_mock_data_artifact(query: str) -> AsyncGenerator[Dict[str, Any], None]:
    query_lower = query.lower()
    artifact_generated = False
    if "sales" in query_lower or ("report" in query_lower and "table" in query_lower):
        artifact_id = str(uuid.uuid4())
        columns = ["Month", "Revenue", "Units Sold"]
        yield {"stream_type": "artifact_start", "artifact_id": artifact_id, "artifact_type": "data", "metadata": {"title": "Quarterly Sales Report", "format": "json_table_rows", "columns": columns}}
        rows = [["January", 10500, 520], ["February", 12300, 610], ["March", 15600, 770]]
        for row in rows:
            await asyncio.sleep(0.1)
            yield {"stream_type": "artifact_chunk", "artifact_id": artifact_id, "data": row}
        artifact_generated = True
    elif ("product" in query_lower or "inventory" in query_lower) and "table" in query_lower:
        artifact_id = str(uuid.uuid4())
        columns = ["Product_ID", "Name", "Stock_Level", "Category"]
        yield {"stream_type": "artifact_start", "artifact_id": artifact_id, "artifact_type": "data", "metadata": {"title": "Product Inventory Status", "format": "json_table_rows", "columns": columns}}
        rows = [["PID001", "Laptop X", 42, "Electronics"], ["PID002", "Wireless Mouse", 189, "Accessories"], ["PID003", "Coffee Maker Pro", 75, "Appliances"]]
        for row in rows:
            await asyncio.sleep(0.1)
            yield {"stream_type": "artifact_chunk", "artifact_id": artifact_id, "data": row}
        artifact_generated = True

    if artifact_generated:
        yield {"stream_type": "artifact_end", "artifact_id": artifact_id}

class MyDataDiscoveryAgent(RoutedAgent):
    def __init__(self, name: str, model_client: ChatCompletionClient, system_message: str = "You are a helpful AI assistant for data discovery."):
        super().__init__(name)
        self._model_client = model_client
        self._system_messages: List[LLMMessage] = [SystemMessage(content=system_message)]

    async def handle_chat_message(
        self,
        user_input_message: LLMMessage,
        response_queue: asyncio.Queue,
    ) -> str:
        accumulated_content = ""
        user_text_content = user_input_message.content if hasattr(user_input_message, 'content') else str(user_input_message)
        print(f"Agent '{self.name}' received message: {user_text_content}")

        artifact_stream_started = False
        async for artifact_event in _generate_mock_code_artifact(user_text_content):
            await response_queue.put(artifact_event)
            if artifact_event.get("stream_type") == "artifact_start": artifact_stream_started = True

        if artifact_stream_started:
            await response_queue.put(STREAM_DONE) # Signal end of this interaction
            return "Streamed code artifact based on keywords."

        async for artifact_event in _generate_mock_data_artifact(user_text_content):
            await response_queue.put(artifact_event)
            if artifact_event.get("stream_type") == "artifact_start": artifact_stream_started = True

        if artifact_stream_started:
            await response_queue.put(STREAM_DONE) # Signal end of this interaction
            return "Streamed data artifact based on keywords."

        # If no artifact generated by keywords, proceed with LLM call
        print(f"No keyword-based artifact generated for: '{user_text_content}'. Proceeding with LLM chat.")
        try:
            if not self._model_client:
                await response_queue.put({"stream_type": "error", "data": "ERROR: Model client not available in agent."})
                await response_queue.put(STREAM_DONE)
                return "Error: Model client not available."

            messages_to_llm: List[LLMMessage] = self._system_messages + [user_input_message]
            async for chunk_str in self._model_client.create_stream(messages_to_llm):
                if isinstance(chunk_str, str):
                    accumulated_content += chunk_str
                    await response_queue.put({"stream_type": "chat_chunk", "data": chunk_str})
                else: pass

            await response_queue.put(STREAM_DONE)
            print(f"Agent '{self.name}' finished LLM streaming. Full response: {accumulated_content}")
            return accumulated_content
        except Exception as e:
            print(f"Error in agent's LLM call: {e}")
            error_msg_dict = {"stream_type": "error", "data": f"ERROR: An error occurred during LLM call: {str(e)}"}
            try:
                await response_queue.put(error_msg_dict)
                await response_queue.put(STREAM_DONE)
            except Exception as q_e: print(f"Error putting error to queue: {q_e}")
            return accumulated_content
