import asyncio
import csv
from flask import Flask, render_template, request, jsonify
from agentscope.model import OpenAIChatModel
from agentscope.formatter import OllamaChatFormatter
from agentscope.agent import ReActAgent  
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg

app = Flask(__name__, template_folder='templates')

# --- 1. DATA LOADING ---
def load_candidates():
    candidates = []
    try:
        with open('candidates.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                candidates.append(row)
    except FileNotFoundError:
        print("Warning: candidates.csv not found.")
    return candidates

COMPANY_DATA = """
HIRING: 7 open positions, 45 candidates, 12 interviews scheduled
PROJECTS: Mobile Redesign, API Migration, Security Audit
METRICS: 156 employees, $2.5M revenue, 94.2% retention
"""

candidates_list = load_candidates()
CANDIDATES_DATA = "\n".join([
    f"- {c['name']}: {c['position']}, {c['experience']} exp, Skills: {c['skills']}, Status: {c['status']}, Salary: {c['salary_expectation']}" 
    for c in candidates_list
])

# --- 2. GLOBAL SETUP (Fixes Amnesia Bug) ---
full_context = f"Company Data:\n{COMPANY_DATA}\n\nCandidate Pool:\n{CANDIDATES_DATA}"

# Memory stays alive between clicks
chat_memory = InMemoryMemory()

# Agent created globally
agent = ReActAgent(
    name="HiringAgent",
    sys_prompt=f"You are a hiring expert. Use this data to answer questions:\n{full_context}\nAnswer concisely with specific names and details.",
    model=OpenAIChatModel(
        model_name="/app/local_model/3.1-8b-instruct",
        api_key="key",
        client_kwargs={"base_url": "http://192.168.3.73:8080/v1"},
        stream=False,
    ),
    memory=chat_memory,
    formatter=OllamaChatFormatter(), # Note: Kept your Ollama formatter here as requested in your snippet
)

# --- 3. CORE LOGIC ---
async def analyze(query):
    # Only send the message, the agent is already set up
    msg = Msg(name="user", role="user", content=query)
    return (await agent(msg)).get_text_content()

# --- 4. FLASK ROUTES ---
@app.route('/')
def index():
    return render_template('chat-agent.html')

# Made this route async to fix the "Event loop is closed" crash
@app.route('/api/analyze', methods=['POST'])
async def api_analyze():
    try:
        query = request.json.get('query', '')
        result = await analyze(query)
        return jsonify({'response': result})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("\n╔════════════════════════════════════════════╗")
    print("║  AgentScope Company Agent                 ║")
    print("║                                            ║")
    print("║  Open: http://localhost:5000              ║")
    print("╚════════════════════════════════════════════╝\n")
    app.run(debug=False, port=5000)