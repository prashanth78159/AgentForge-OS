
from fastapi import FastAPI
from app.core.runtime.execution_engine import ExecutionEngine
from app.core.events.event_bus import EventBus
from app.core.state.state_manager import StateManager
from app.core.models.workflow import Workflow
from app.services.llm_service import LLMService # Import to get default model
import os # Import os
from dotenv import load_dotenv # Import load_dotenv

load_dotenv() # Load environment variables from .env

app = FastAPI()

event_bus = EventBus()
state_manager = StateManager()

# --- LLM CONFIGURATION (moved here from `ExecutionEngine` init) ---
# For a simple FastAPI setup, we'll hardcode or get from env/secrets
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "Groq") # Use os.getenv
default_model_name = LLMService.get_default_model(DEFAULT_LLM_PROVIDER)
GROQ_API_KEY = os.getenv('GROQ_API_KEY') # Use os.getenv
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') # Add other API keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
# --- END LLM CONFIGURATION ---

# Dynamically select API key based on provider
api_key_map = {
    "Groq": GROQ_API_KEY,
    "OpenAI": OPENAI_API_KEY,
    "Anthropic": ANTHROPIC_API_KEY,
    "Gemini": GEMINI_API_KEY,
    "Deepseek": DEEPSEEK_API_KEY,
    "OpenRouter": OPENROUTER_API_KEY
}
selected_api_key = api_key_map.get(DEFAULT_LLM_PROVIDER)

engine = ExecutionEngine(event_bus, state_manager, DEFAULT_LLM_PROVIDER, selected_api_key, default_model_name)

@app.get("/")
def home():
    return {"status": "AgentForge OS Running"}

@app.post("/execute")
async def execute(workflow: Workflow):
    result = await engine.execute(workflow)
    return {"result": result}
