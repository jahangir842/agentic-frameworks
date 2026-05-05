import asyncio
from a2a.types import AgentCard, AgentCapabilities
from agentscope.agent import A2AAgent, UserAgent
from agentscope.message import Msg

# 1. Define the Card (The connection details)
agent_card = AgentCard(
    name="Friday",
    description="A fun chatting companion",
    url="http://127.0.0.1:8001", # Pointing to the server we created in Step 1
    version="1.0.0",
    capabilities=AgentCapabilities(
        push_notifications=False,
        state_transition_history=True,
        streaming=False, # Set to False for simpler initial testing
    ),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[],
)

async def test_a2a():
    # 2. Initialize the A2A Agent using the card
    remote_agent = A2AAgent(agent_card=agent_card)
    user = UserAgent("User")

    print("--- A2A Connection Established. Type 'exit' to quit. ---")
    
    msg = None
    while True:
        # Get input from you (the human)
        msg = await user(msg)
        
        if msg.content == "exit":
            break
            
        # Send the message to the "Remote" agent via A2A protocol
        print(f"\n[Client] Sending message to remote Friday...")
        response = await remote_agent(msg)
        
        print(f"\n[Friday]: {response.content}")

if __name__ == "__main__":
    asyncio.run(test_a2a())