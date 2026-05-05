## 🔧 Tool Calling in vLLM

Used to enable automatic tool usage in agents.

```bash
--enable-auto-tool-choice
# Lets the model decide when to use tools

--tool-call-parser llama3_json
# Parses tool calls using llama3_json format
```

* Auto tool selection enabled
* Proper tool call parsing
* Makes vLLM agent-ready for frameworks like AgentScope


## Default DashScope API (Alibaba Cloud)

DashScope API (via `DASHSCOPE_API_KEY`) from `Alibaba Cloud`.

### Original (AgentScope example)

```python
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeChatFormatter
```

### 🔄 Our Implementation

```python
from agentscope.model import OpenAIChatModel
from agentscope.formatter import OllamaChatFormatter
```

---

## ⚖️ Agents Comparison

| Agent Type            | Reasoning | Tools      | Planning | Speed        | Use Case          |
| --------------------- | --------- | ---------- | -------- | ------------ | ----------------- |
| `AssistantAgent`      | ❌         | ❌          | ❌        | ⚡ Fast       | Simple chat       |
| `ReflexAgent`         | ❌         | ⚠️ Limited | ❌        | ⚡⚡ Very fast | Event triggers    |
| `ReActAgent`          | ✅         | ✅          | ❌        | ⚖️ Medium    | Autonomous agents |
| `PlanAndExecuteAgent` | ✅         | ✅          | ✅        | 🐢 Slower    | Complex workflows |

---

## AgentScope Memory Implementations

| Memory Class | Type | Best For |
| :--- | :--- | :--- |
| **`InMemoryMemory`** | Short-Term | Quick testing and local scripts (wipes when script ends). |
| **`AsyncSQLAlchemyMemory`**| Short-Term | Production apps using SQL databases (SQLite, PostgreSQL). |
| **`RedisMemory`** | Short-Term | Distributed systems with multiple workers sharing state. |
| **`Mem0LongTermMemory`** | Long-Term | Mem0 is a popular, `open-source` memory layer `built for` Large Language Models |
| **`ReMePersonalLongTermMemory`**| Long-Term | ReMe is a dedicated memory management toolkit created specifically for the `AgentScope ecosystem` |

---

## Built-in Tool Categories

| Category | Available Tools | Purpose |
| :--- | :--- | :--- |
| **Information Retrieval** | `GoogleSearch`, `BingSearch`, `Wikipedia` | Allows agents to browse the live web for up-to-date facts. |
| **File Operations** | `ReadFileTool`, `WriteFileTool`, `ListFiles` | Reading and writing local files (with security sandboxing). |
| **Code & System** | `PythonExecution`, `ShellCommandTool` | Running Python scripts or terminal commands (e.g., for DevOps). |
| **Multimodal** | `ImageGeneration`, `VisionAnalysis` | Processing images or generating visual content. |
| **Service Integration** | `WeatherService`, `DatabaseQuery` | Connecting to external APIs or structured data. |


### Comparison: Built-in vs. Custom Tools

| Feature | Built-in Tools (Skills) | Custom Tools (User-Defined) |
| :--- | :--- | :--- |
| **Ease of Use** | Just import and add to `Toolkit`. | Requires writing a Python function. |
| **Best For** | Common tasks (Search, Files). | Internal business logic (HR, Payroll, IT). |



---
### Out-of-box Agents
- https://docs.agentscope.io/out-of-box-agents/alias

