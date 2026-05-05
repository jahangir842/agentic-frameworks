import asyncio
from transformers import pipeline, logging
from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.model import ChatResponse 
from agentscope.formatter import OllamaChatFormatter

######################### Part 1: Local LLaMA-3.2-1B-Instruct Model Setup #########################
pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-1B-Instruct")
logging.set_verbosity_error()

async def local_llama(messages, **kwargs):
    prompt = [
        {"role": m['role'] if isinstance(m, dict) else m.role, 
         "content": m['content'] if isinstance(m, dict) else m.content} 
        for m in messages
    ]
    output = pipe(prompt)[0]['generated_text'][-1]['content']
    return ChatResponse(content=[{"type": "text", "text": output}])

local_llama.stream = False          
########################## Part 2: ReAct Agent Setup #########################
agent = ReActAgent(name="Assistant", sys_prompt="You are a helpful, concise AI.", model=local_llama, formatter=OllamaChatFormatter())

########################## Part 3: Interactive loop for user queries ##########################
print("\n🤖 Assistant ready! \n" + "─"*20)

while True:
    query = input("\nYou: ")
    response = asyncio.run(agent(Msg(name="user", role="user", content=query)))
