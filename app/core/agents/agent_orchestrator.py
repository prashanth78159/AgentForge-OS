
from app.services.llm_service import LLMService

from app.core.agents.planner_agent import PlannerAgent
from app.core.agents.research_agent import ResearchAgent
from app.core.agents.writer_agent import WriterAgent
from app.core.agents.critic_agent import CriticAgent

from app.core.memory.memory_manager import MemoryManager
from app.core.memory.vector_memory import VectorMemory

from app.core.observability.tracer import ExecutionTracer
from app.core.replay.execution_store import ExecutionStore


class AgentOrchestrator:
    """
    Central orchestration engine for multi-agent execution.
    Responsible for:
    - Managing agent pipeline
    - Handling memory
    - Tracing execution
    - Persisting runs for replay
    """

    def __init__(self, api_key: str):

        # ✅ Shared LLM service
        llm = LLMService(api_key)

        # ✅ Agents
        self.planner = PlannerAgent("Planner", llm)
        self.researcher = ResearchAgent("Researcher", llm)
        self.writer = WriterAgent("Writer", llm)
        self.critic = CriticAgent("Critic", llm)

        # ✅ Memory systems
        self.memory = MemoryManager()              # short-term
        self.long_term_memory = VectorMemory()     # long-term

        # ✅ Observability
        self.tracer = ExecutionTracer()

        # ✅ Replay storage
        self.store = ExecutionStore()

    def run(self, task: str):
        """
        Executes full multi-agent pipeline
        """

        # ✅ Reset tracer every run (IMPORTANT)
        self.tracer = ExecutionTracer()

        # ✅ Execution ID
        execution_id = "exec_" + str(len(self.store.executions))

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
