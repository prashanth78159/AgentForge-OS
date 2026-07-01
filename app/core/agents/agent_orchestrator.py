
from app.services.llm_service import LLMService

from app.core.agents.planner_agent import PlannerAgent
from app.core.agents.research_agent import ResearchAgent
from app.core.agents.writer_agent import WriterAgent
from app.core.agents.critic_agent import CriticAgent

from app.core.memory.memory_manager import MemoryManager
from app.core.memory.vector_memory import VectorMemory

from app.core.observability.tracer import ExecutionTracer
from app.core.replay.execution_store import ExecutionStore
from app.core.runtime.execution_engine import ExecutionEngine
from app.core.events.event_bus import EventBus
from app.core.state.state_manager import StateManager
from app.core.models.workflow import Workflow
from app.core.metrics.metrics_manager import MetricsManager # Import MetricsManager


class AgentOrchestrator:
    """
    Central orchestration engine for multi-agent execution.
    Responsible for:
    - Managing agent pipeline
    - Handling memory
    - Tracing execution
    - Persisting runs for replay
    - Collecting performance metrics
    """

    def __init__(self, llm_provider: str, api_key: str, model_name: str):

        # ✅ Shared LLM service
        self.llm_service = LLMService(llm_provider, api_key, model_name)

        # ✅ Metrics Manager
        self.metrics_manager = MetricsManager()

        # ✅ Agents, now passing the metrics_manager
        self.planner = PlannerAgent("Planner", self.llm_service, self.metrics_manager)
        self.researcher = ResearchAgent("Researcher", self.llm_service, self.metrics_manager)
        self.writer = WriterAgent("Writer", self.llm_service, self.metrics_manager)
        self.critic = CriticAgent("Critic", self.llm_service, self.metrics_manager)

        # ✅ Memory systems
        self.memory = MemoryManager()
        self.long_term_memory = VectorMemory()

        # ✅ Observability
        self.tracer = ExecutionTracer()

        # ✅ Replay storage
        self.store = ExecutionStore()

        # ✅ Execution Engine for workflows
        self.event_bus = EventBus()
        self.state_manager = StateManager()
        self.execution_engine = ExecutionEngine(self.event_bus, self.state_manager, llm_provider, api_key, model_name)

    def classify_input(self, task):
        short_inputs = ["hi", "hello", "hey"]

        if task.lower().strip() in short_inputs:
            return "simple"

        return "complex"

    def run(self, task: str):
        """
        Executes full multi-agent pipeline
        """
        mode = self.classify_input(task)

        if mode == "simple":
            return {
                "execution_id": "simple",
                "final": f"Hello 👋 How can I help you?",
                "logs": []
            }

        # ✅ Reset tracer every run (IMPORTANT)
        self.tracer = ExecutionTracer()

        # ✅ Execution ID
        execution_id = "exec_" + str(len(self.store.executions))
        self.metrics_manager.start_execution(execution_id) # Start tracking metrics for this execution

        # ✅ Context
        context = {}
        session_id = "default"

        # ✅ Retrieve memory
        short_term_memory = self.memory.get(session_id)
        long_term_memory = self.long_term_memory.search(task)

        # ✅ Combine memory context
        memory_context = f"""
        Short-term memory:
        {short_term_memory}

        Long-term memory:
        {long_term_memory}
        """

        # --------------------------------------------------
        # ✅ STEP 1 — PLANNER
        # --------------------------------------------------
        planner_input = task + memory_context
        plan = self.planner.run(planner_input, context)

        self.tracer.log("planner", planner_input, plan)
        self.memory.add(session_id, plan)

        # --------------------------------------------------
        # ✅ STEP 2 — RESEARCH
        # --------------------------------------------------
        research = self.researcher.run(plan, context)

        self.tracer.log("research", plan, research)
        self.memory.add(session_id, research)

        # --------------------------------------------------
        # ✅ STEP 3 — WRITER
        # --------------------------------------------------
        draft = self.writer.run(research, context)

        self.tracer.log("writer", research, draft)

        # --------------------------------------------------
        # ✅ STEP 4 — CRITIC
        # --------------------------------------------------
        final = self.critic.run(draft, context)

        self.tracer.log("critic", draft, final)

        # --------------------------------------------------
        # ✅ STORE LONG-TERM MEMORY
        # --------------------------------------------------
        self.long_term_memory.add(task)
        self.long_term_memory.add(plan)
        self.long_term_memory.add(final)

        # --------------------------------------------------
        # ✅ SAVE EXECUTION (for replay)
        # --------------------------------------------------
        logs = self.tracer.get_logs()
        self.store.save(execution_id, logs)

        # --------------------------------------------------
        # ✅ FINAL OUTPUT
        # --------------------------------------------------
        return {
            "execution_id": execution_id,
            "plan": plan,
            "research": research,
            "draft": draft,
            "final": final,
            "logs": logs
        }

    async def execute_workflow(self, workflow: Workflow):
        """
        Executes a pre-defined workflow using the execution engine.
        """
        # Tracer for workflow execution (optional, can be integrated if needed)
        # self.tracer = ExecutionTracer()
        # Logs from execution engine are sufficient for now

        # Start tracking metrics for this workflow execution
        workflow_execution_id = str(uuid.uuid4()) # Generate a new ID for workflow execution metrics
        self.metrics_manager.start_execution(workflow_execution_id)

        results = await self.execution_engine.execute(workflow)

        # For consistency, return a dictionary similar to the 'run' method
        # You might want to process 'results' into a 'final' output here
        execution_id = results.get("execution_id", workflow_execution_id) # Use the ID from engine if available, else workflow_execution_id
        final_output = "Workflow execution completed. See debugger for details." # Placeholder
        logs = self.state_manager.get(execution_id) # Get logs from state manager after execution

        # Store this execution for replay
        self.store.save(execution_id, logs)

        return {
            "execution_id": execution_id,
            "final": final_output,
            "logs": logs
        }
