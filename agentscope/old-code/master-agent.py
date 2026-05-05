import asyncio
import csv
from flask import Flask, render_template, request, jsonify
from agentscope.model import OpenAIChatModel
from agentscope.formatter import DashScopeChatFormatter
from agentscope.agent import ReActAgent  
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit, ToolResponse
from agentscope.message import Msg

from ddgs import DDGS

app = Flask(__name__, template_folder='templates')

# --- 1. TOOL DEFINITIONS ---

def calculate_monthly_salary(annual_salary: int) -> ToolResponse:
    """
    Calculate the monthly take-home pay from an annual salary.
    Args:
        annual_salary (int): The yearly salary amount.
    """
    try:
        annual_val = float(annual_salary)
        monthly = annual_val / 12
        return ToolResponse(f"The monthly salary is ${monthly:.2f}")
    except ValueError:
        return ToolResponse("Error: Please provide a valid number for the annual salary.")

def multiply_numbers(a: float, b: float) -> ToolResponse:
    """
    Multiply two numbers together. Use this for any general multiplication tasks.
    Args:
        a (float): The first number to multiply.
        b (float): The second number to multiply.
    """
    try:
        result = float(a) * float(b)
        return ToolResponse(f"The result of {a} multiplied by {b} is {result}")
    except ValueError:
        return ToolResponse("Error: Please provide valid numbers for multiplication.")

def web_search(query: str) -> ToolResponse:
    """
    Search the web for up-to-date information, news, or current events. 
    Args:
        query (str): The specific search term or question to look up.
    """
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return ToolResponse("Error: Search returned no results. Try a different query.")
            
        formatted_results = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return ToolResponse(formatted_results)
    except Exception as e:
        return ToolResponse(f"Search failed: {str(e)}")

# --- 2. DATA LOADING ---
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

# --- 3. GLOBAL SETUP ---

# Register ALL tools to a single toolkit
agent_tools = Toolkit()
agent_tools.register_tool_function(calculate_monthly_salary)
agent_tools.register_tool_function(multiply_numbers)
agent_tools.register_tool_function(web_search)

full_context = f"Company Data:\n{COMPANY_DATA}\n\nCandidate Pool:\n{CANDIDATES_DATA}"

# Memory stays alive between clicks
chat_memory = InMemoryMemory()

# Create the Omni-Agent
agent = ReActAgent(
    name="OmniAssistant", 
    sys_prompt=(
        f"You are a highly capable AI assistant. You have access to internal company data:\n{full_context}\n\n"
        "CRITICAL TOOL INSTRUCTIONS:\n"
        "- IF the user asks about candidate pay: use the `calculate_monthly_salary` tool.\n"
        "- IF the user asks to multiply numbers: you MUST use the `multiply_numbers` tool. DO NOT calculate it internally.\n"
        "- IF the user asks about current events, outside knowledge, or facts not in your company data: you MUST use the `web_search` tool.\n"
        "- DO NOT use the salary tool for general math problems."
    ),
    model=OpenAIChatModel(
        model_name="/app/local_model/3.1-8b-instruct",
        api_key="key",
        client_kwargs={"base_url": "http://192.168.3.73:8080/v1"},
        stream=False,
    ),
    memory=chat_memory,
    formatter=DashScopeChatFormatter(), 
    toolkit=agent_tools,
)

# --- 4. CORE LOGIC ---
async def analyze(query):
    msg = Msg(name="user", role="user", content=query)
    response = await agent(msg)
    return response.get_text_content()

# --- 5. FLASK ROUTES ---
@app.route('/')
def index():
    # Pointing to the unified tools.html template you just created!
    return render_template('master-agent.html') 

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
    print("║  AgentScope Omni-Agent (3 Tools Loaded)   ║")
    print("║  Open: http://localhost:5000              ║")
    print("╚════════════════════════════════════════════╝\n")
    app.run(debug=False, port=5000)