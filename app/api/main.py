
from fastapi import FastAPI
from app.core.runtime.execution_engine import ExecutionEngine
from app.core.events.event_bus import EventBus
from app.core.state.state_manager import StateManager
from app.core.models.workflow import Workflow

app = FastAPI()

event_bus = EventBus()
state_manager = StateManager()
engine = ExecutionEngine(event_bus, state_manager)

@app.get("/")
def home():
    return {"status": "AgentForge OS Running"}

@app.post("/execute")
async def execute(workflow: Workflow):
    result = await engine.execute(workflow)
    return {"result": result}
