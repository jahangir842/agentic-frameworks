import torch
from transformers import pipeline
from agentscope.agent import AgentBase
from agentscope.message import Msg
from agentscope.model import ModelResponse

print("Loading Llama-3.2-1B into memory... (This takes a moment)")

# 2. LOAD LOCAL MODEL: Programmatically bypasses vLLM/Ollama
pipe = pipeline(
    "text-generation", 
    model="unsloth/Llama-3.2-1B-Instruct", 
    torch_dtype=torch.bfloat16, 
    device_map="auto"
)

# 3. FUNCTION WRAPPER: Connects HuggingFace directly to AgentScope
def local_llama(messages, **kwargs):
    # Convert AgentScope Msgs into standard HuggingFace dicts
    prompt = [{"role": m.role, "content": m.content} for m in messages]
    # Generate text and extract just the AI's reply
    output = pipe(prompt, max_new_tokens=256)[0]['generated_text'][-1]['content']
    return ModelResponse(text=output)

# Hack to satisfy AgentScope's internal checks
local_llama.format = lambda msgs: msgs

# 4. CUSTOM MINIMAL AGENT: Bypasses missing "DialogAgent" classes
class MinimalChatAgent(AgentBase):
    def __init__(self, name, sys_prompt, model):
        super().__init__(name=name)
        self.model = model
        # Create a simple memory array starting with the instructions
        self.messages = [Msg(name="system", role="system", content=sys_prompt)]
        
    def reply(self, x=None):
        if x is not None:
            self.messages.append(x)
            
        # Run the programmatic model
        response = self.model(self.messages)
        
        # Save and print the reply
        reply_msg = Msg(name=self.name, role="assistant", content=response.text)
        self.messages.append(reply_msg)
        print(f"\n{self.name}: {response.text}")
        
        return reply_msg

# --- 5. BARE MINIMUM EXECUTION ---
agent = MinimalChatAgent(
    name="Assistant", 
    sys_prompt="You are a helpful, concise AI.", 
    model=local_llama
)

print("\n🤖 Assistant ready! (Type 'quit' to exit)\n" + "─"*40)
while True:
    query = input("\nYou: ")
    if query.lower() in ['quit', 'exit']: 
        break
        
    agent(Msg(name="user", role="user", content=query))