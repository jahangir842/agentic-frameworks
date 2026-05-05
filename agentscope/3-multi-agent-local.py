import asyncio
from transformers import pipeline, logging
from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.model import ChatResponse 
from agentscope.formatter import OllamaChatFormatter

######################### Part 1: Local Model Setup #########################
pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-1B-Instruct", device_map="auto")
logging.set_verbosity_error()

async def local_llama(messages, **kwargs):
    prompt = [
        {"role": m['role'] if isinstance(m, dict) else m.role, 
         "content": m['content'] if isinstance(m, dict) else m.content} 
        for m in messages
    ]
    out = pipe(prompt, max_new_tokens=500, pad_token_id=pipe.tokenizer.eos_token_id)[0]['generated_text'][-1]['content']
    return ChatResponse(content=[{"type": "text", "text": out}])

local_llama.stream = False                  
########################## Part 2: Multi-Agent Setup #########################
# Agent 1: The Brain
planner = ReActAgent(
    name="Planner", 
    sys_prompt="You are a senior architect. Briefly outline a 3-step plan to solve the user's request. Be very concise.", 
    model=local_llama, 
    formatter=OllamaChatFormatter()
)

# Agent 2: The Hands
executor = ReActAgent(
    name="Executor", 
    sys_prompt="You are a final-stage assistant. Read the User's original request and the Planner's outline. Provide the final, complete and detailed answer. If it requires code, write the code. If it is a general question, answer it in plain text.", 
    model=local_llama, 
    formatter=OllamaChatFormatter()
)

########################## Part 3: The Agent Communication Pipeline ##########################
print("\n Multi-Agent Environment Ready! \n" + "─"*30)

async def chat_flow(query):
    # Step 1: User sends message to Planner
    user_msg = Msg(name="user", role="user", content=query)
    planner_reply = await planner(user_msg)
    
    print("="*35)

    # Step 2: Planner's output becomes the input for the Executor
    handoff_msg = Msg(name="Planner", role="user", content=planner_reply.content[0]['text'])
    executor_reply = await executor(handoff_msg)

while True:
    q = input("\nYou: ")
    asyncio.run(chat_flow(q))