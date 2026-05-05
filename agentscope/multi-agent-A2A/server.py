import uvicorn
import asyncio
import uuid
from typing import AsyncGenerator, Any
from transformers import pipeline, logging

# A2A SDK imports
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import Event
from a2a.types import (
    AgentCard, 
    AgentCapabilities,
    TaskStatus,
    TaskState,
    MessageSendParams,
    TaskStatusUpdateEvent,
)

# AgentScope imports
from agentscope.agent import ReActAgent
from agentscope.model import ChatResponse 
from agentscope.formatter import OllamaChatFormatter, A2AChatFormatter

######################### Part 1: Local Model Setup #########################
# Load the model once at the start
pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-1B-Instruct", device_map="auto")
logging.set_verbosity_error()

async def local_llama(messages, **kwargs):
    prompt = [
        {"role": m['role'] if isinstance(m, dict) else m.role, 
         "content": m['content'] if isinstance(m, dict) else m.content} 
        for m in messages
    ]
    # Simple generation call
    output = pipe(prompt, max_new_tokens=256)[0]['generated_text'][-1]['content']
    return ChatResponse(content=[{"type": "text", "text": output}])

local_llama.stream = False  

######################### Part 2: Define Agent Card #########################
agent_card = AgentCard(
    name="Friday",
    description="A local A2A Llama Agent",
    url="http://127.0.0.1:8001",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[],  # <--- Added this line to satisfy the validation error
)

######################### Part 3: Define the Missing Handler #########################
class SimpleStreamHandler:
    """The bridge between the A2A protocol and your local Llama agent"""

    # This handles the non-streaming request your client is sending
    async def on_message_send(
        self,
        params: MessageSendParams,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        # We just redirect this to our existing logic and collect the generator results
        responses = []
        async for event in self.on_message_send_stream(params, *args, **kwargs):
            if isinstance(event, TaskStatusUpdateEvent) and event.status.message:
                responses.append(event.status.message)
        
        # Return the last message found in the stream
        return responses[-1] if responses else "No response generated."

    async def on_message_send_stream(
        self,
        params: MessageSendParams,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncGenerator[Event, None]:
        task_id = params.message.task_id or uuid.uuid4().hex
        context_id = params.message.context_id or "default-context"

        agent = ReActAgent(
            name="Friday",
            sys_prompt="You are a helpful assistant powered by Llama-3.2-1B.",
            model=local_llama,
            formatter=OllamaChatFormatter(),
        )

        a2a_formatter = A2AChatFormatter()
        as_msg = await a2a_formatter.format_a2a_message(
            name="User",
            message=params.message,
        )

        yield TaskStatusUpdateEvent(
            task_id=task_id,
            context_id=context_id,
            status=TaskStatus(state=TaskState.working),
            final=False,
        )

        # Generate response
        response_msg = await agent(as_msg)
        
        # Format for A2A
        a2a_response_content = await a2a_formatter.format([response_msg])

        yield TaskStatusUpdateEvent(
            task_id=task_id,
            context_id=context_id,
            status=TaskStatus(
                state=TaskState.working,
                message=a2a_response_content,
            ),
            final=False,
        )

        yield TaskStatusUpdateEvent(
            task_id=task_id,
            context_id=context_id,
            status=TaskStatus(state=TaskState.completed),
            final=True,
        )
######################### Part 4: The Main Loop #########################
if __name__ == "__main__":
    # Now SimpleStreamHandler is defined above, so this won't crash!
    handler = SimpleStreamHandler()
    
    app_instance = A2AStarletteApplication(agent_card, handler)
    app = app_instance.build()
    
    print("🚀 Friday A2A Server starting on http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)