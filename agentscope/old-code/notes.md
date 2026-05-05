## **LLM & AgentScope Technical Reference**

### **1. Hardware Requirements**
* **Model:** Llama 3.2 1B
* **Precision:** BF16 (BFloat16) — 2 bytes per parameter.
* **VRAM/RAM:** Exactly **2 GB** just for model weights.
    * *Note:* Total system RAM/VRAM should be **~4 GB** to account for the context window and system overhead.

### **2. The Async Requirement**
AgentScope is designed as an **"Async-First"** architecture. You cannot run it without `asyncio` because:
* **Event Loop:** It requires a running event loop to manage background tasks like reasoning and tool-handling.
* **Concurrency:** It is built for multi-agent coordination; async prevents the entire system from freezing while one agent is "thinking."
* **Internal Logic:** Core functions (like `agent.reply`) are defined as coroutines that must be **awaited** to execute.

### **3. Messaging & Formatting (The Bridge)**
To ensure compatibility between the User, the Agent, and the Model, AgentScope uses two primary tools:

* **Msg (The Packet):** A standardized data container (similar to a structured API packet). It holds the sender's **Name**, **Role**, and **Content** so the framework knows exactly who is speaking at all times.
* **Formatter (The Translator):** A universal translator that takes `Msg` objects and converts them into the specific JSON or text "dialect" (e.g., Llama-3-Instruct or Ollama tags) that a specific model was trained to understand.

### **Why use them?**
In a complex multi-agent system, **Msg** provides the reliable data structure needed for agents to communicate, while the **Formatter** ensures those instructions are structured correctly so the model doesn't hallucinate or fail to recognize user input.

---