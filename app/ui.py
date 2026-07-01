
import sys, os
import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv # Import load_dotenv

load_dotenv() # Load environment variables from .env

# Ensure the project root is in the path
sys.path.append("/content")

from app.core.agents.agent_orchestrator import AgentOrchestrator
from app.core.replay.replay_engine import ReplayEngine
from app.core.acl.lexer import tokenize
from app.core.acl.parser import Parser
from app.core.acl.compiler import ACLCompiler
from app.core.models.workflow import Workflow # Needed for ACLCompiler output
from app.services.llm_service import LLMService # Import to get available models

# ---------------- SESSION STATE INITIALIZATION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Initialize API keys for all supported providers by reading from environment variables
for provider in LLMService.AVAILABLE_MODELS.keys():
    key_name = f"{provider.upper().replace(' ', '_')}_API_KEY"
    if f"{provider.lower().replace(' ', '_')}_api_key" not in st.session_state:
        api_key_value = os.getenv(key_name, "") # Use os.getenv instead of os.environ.get()
        st.session_state[f"{provider.lower().replace(' ', '_')}_api_key"] = api_key_value

if "selected_llm_provider" not in st.session_state:
    st.session_state.selected_llm_provider = "Groq"

# Initialize selected models for all providers
for provider, models in LLMService.AVAILABLE_MODELS.items():
    if f"{provider.lower().replace(' ', '_')}_model" not in st.session_state:
        st.session_state[f"{provider.lower().replace(' ', '_')}_model"] = models[0] if models else ""

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
if "replay_engine" not in st.session_state:
    st.session_state.replay_engine = None
if "res" not in st.session_state:
    st.session_state.res = None # For debugger
if "stored_workflows" not in st.session_state:
    st.session_state.stored_workflows = {}
if "short_term_memory_session_id" not in st.session_state:
    st.session_state.short_term_memory_session_id = "default" # Default session ID for memory

# ---------------- CUSTOM CSS FOR ENHANCED LOOK AND FEEL ----------------
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
        color: #c9d1d9; /* GitHub light grey for text */
    }

    .stApp {
        background-color: #0d1117; /* GitHub dark background */
        /* padding-top: 1rem; */
    }

    /* Sidebar styling */
    .st-emotion-cache-zt5ig8 {
        background-color: #161b22; /* Slightly lighter dark for sidebar */
        padding: 20px;
        border-right: 1px solid #30363d;
        box-shadow: 2px 0 5px rgba(0,0,0,0.2);
    }
    .st-emotion-cache-zt5ig8 .st-emotion-cache-1jmvea6 {
        color: #c9d1d9; /* Sidebar header text */
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 20px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #238636; /* GitHub green */
        color: white;
        border-radius: 6px;
        border: none;
        padding: 10px 15px;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.2s, transform 0.1s;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        transform: translateY(-1px);
    }
    .stButton>button:active {
        transform: translateY(0);
    }

    /* Text Inputs & Text Areas */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background-color: #0d1117;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 10px;
        transition: border-color 0.2s;
    }
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #2188ff; /* Blue focus border */
        outline: none;
        box-shadow: 0 0 0 3px rgba(33, 136, 255, 0.3);
    }

    /* Selectbox */
    .stSelectbox>div>div {
        background-color: #0d1117;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 5px 10px;
    }
    .stSelectbox>div>div:focus-within {
        border-color: #2188ff;
        box-shadow: 0 0 0 3px rgba(33, 136, 255, 0.3);
    }

    /* Expander */
    .streamlit-expanderHeader > div > div > p {
        font-weight: 500;
        color: #58a6ff; /* GitHub blue for expander headers */
    }
    .streamlit-expanderContent {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
        margin-top: 5px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #161b22;
        color: #c9d1d9;
        border-radius: 6px 6px 0 0;
        margin-right: 5px;
        border: 1px solid #30363d;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: #2ea043;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #238636;
        color: white;
        border-color: #238636;
    }

    /* Code Blocks */
    .stCode {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 10px;
        overflow-x: auto;
    }

    /* Alerts */
    .stAlert {
        border-radius: 6px;
        border: none;
    }
    .stAlert.info {
        background-color: rgba(56,139,253,0.15);
        color: #58a6ff;
    }
    .stAlert.warning {
        background-color: rgba(255,193,7,0.15);
        color: #ffc107;
    }
    .stAlert.error {
        background-color: rgba(248,81,73,0.15);
        color: #f85149;
    }
    .stAlert.success {
        background-color: rgba(46,164,79,0.15);
        color: #2ea043;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #c9d1d9;
        font-weight: 600;
    }

    a {
        color: #58a6ff;
    }
    a:hover {
        color: #8ac7ff;
    }

    .st-emotion-cache-1r6dm7m {
      background-color: #0d1117;
    }

</style>
''', unsafe_allow_html=True)

# ---------------- LOGIN ----------------
def login_page():
    st.title("🔐 AgentForge OS Login")
    u = st.text_input("Username", key="login_username")
    p = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if u == "admin" and p == "admin":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

if not st.session_state.logged_in:
    login_page()

# ---------------- INITIALIZE AGENTS (after login and API key is set) ----------------
def initialize_orchestrator():
    if st.session_state.logged_in and st.session_state.selected_llm_provider:
        provider = st.session_state.selected_llm_provider
        api_key_session_key = f"{provider.lower().replace(' ', '_')}_api_key"
        model_session_key = f"{provider.lower().replace(' ', '_')}_model"

        api_key = st.session_state.get(api_key_session_key, "")
        model_name = st.session_state.get(model_session_key, "")

        if api_key:
            try:
                st.session_state.orchestrator = AgentOrchestrator(
                    llm_provider=provider,
                    api_key=api_key,
                    model_name=model_name
                )
                st.session_state.replay_engine = ReplayEngine(st.session_state.orchestrator.store)
                st.sidebar.success(f"Orchestrator initialized with {provider} ({model_name})!")
            except Exception as e:
                st.sidebar.error(f"Error initializing orchestrator: {e}")
                st.session_state.orchestrator = None
                st.session_state.replay_engine = None
                # Don't clear API key, let user re-enter or correct
        else:
            st.sidebar.warning(f"Please enter your {provider} API Key in Settings.")
            st.session_state.orchestrator = None # Ensure it's None if API key is missing
            st.session_state.replay_engine = None
    else:
        st.session_state.orchestrator = None # Ensure it's None if conditions aren't met
        st.session_state.replay_engine = None

# Initialize orchestrator on app load if not already, or if API key changes
if st.session_state.logged_in and st.session_state.orchestrator is None:
    initialize_orchestrator()


# ---------------- SIDEBAR MENU ----------------
with st.sidebar:
    st.title("⚙️ AgentForge OS")
    menu = st.selectbox(
        "Navigation",
        ["Home", "Run", "Workflow Builder", "Debugger", "Replay", "Memory", "Metrics", "Settings", "Contact"]
    )

    if st.session_state.orchestrator:
        st.metric("Total Executions", len(st.session_state.orchestrator.store.executions))
        st.metric("Stored Workflows", len(st.session_state.stored_workflows))
    else:
        st.warning("Orchestrator not initialized. Check API Key in Settings.")


# ---------------- PAGE FUNCTIONS ----------------

# Home Page
def home_page():
    st.title("🚀 AgentForge OS Dashboard")
    if st.session_state.orchestrator:
        st.metric("Total Executions", len(st.session_state.orchestrator.store.executions))
        st.metric("Stored Workflows", len(st.session_state.stored_workflows))
        st.markdown("### Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Run Agent", key="home_run_button"):
                st.session_state.menu = "Run"
                st.rerun()
        with col2:
            if st.button("Build Workflow", key="home_build_workflow_button"):
                st.session_state.menu = "Workflow Builder"
                st.rerun()
    else:
        st.warning("Please configure your API key in the Settings page to enable full functionality.")

# Run Agent Page
def run_page():
    st.title("🏃 Run Agent")

    if not st.session_state.orchestrator:
        st.warning("Orchestrator not initialized. Please go to Settings and set your API Key.")
        return

    workflow_names = list(st.session_state.stored_workflows.keys())
    selected_workflow_name = st.selectbox("Select Stored Workflow (Optional)", [""] + workflow_names, key="run_select_workflow")

    task_input = st.text_area("Enter Task", key="run_task_input", height=150)

    if st.button("Run Agent", key="run_agent_button"):
        if not task_input:
            st.error("Please enter a task.")
            return

        with st.spinner("Running agent..."):
            try:
                result = None
                if selected_workflow_name and selected_workflow_name != "":
                    workflow = st.session_state.stored_workflows[selected_workflow_name]
                    # The 'task_input' here could be used to dynamically set prompts within the workflow
                    # For now, assuming workflow prompts are self-contained or can be updated by a pre-processor
                    result = asyncio.run(st.session_state.orchestrator.execute_workflow(workflow))
                    st.info(f"Executing workflow '{selected_workflow_name}' with task context: '{task_input}'")
                else:
                    result = st.session_state.orchestrator.run(task_input)
                    st.info(f"Running default agent orchestration for task: '{task_input}'")

                st.session_state["res"] = result # Store result for debugger
                st.success("Agent run completed!")
                st.subheader(f"✅ Final Output (Execution ID: {result['execution_id']})")

                if selected_workflow_name and selected_workflow_name != "":
                    # For workflow execution, final output is a placeholder, direct user to debugger
                    st.write("Workflow executed. See Debugger for detailed node outputs.")
                else:
                    st.markdown(result["final"])

            except Exception as e:
                st.error(f"An error occurred during agent execution: {e}")
                st.exception(e)

# Workflow Builder Page
def workflow_builder_page():
    st.title("🏗️ Workflow Builder (ACL)")

    st.markdown("Define your agent workflow using Agent Control Language (ACL).")
    acl_code = st.text_area(
        "Enter ACL Code",
        height=300,
        value='''agent my_agent {
    step1: llm("What is the capital of France?")
    step2: tool("print", "The capital is {step1}")

    step1 -> step2
}'''
    )

    workflow_name_input = st.text_input("Workflow Name (e.g., 'CapitalFinder')", key="workflow_name_input")

    if st.button("Compile & Save Workflow", key="compile_save_workflow_button"):
        if not acl_code or not workflow_name_input:
            st.error("Please enter ACL code and a workflow name.")
            return

        with st.spinner("Compiling workflow..."):
            try:
                tokens = tokenize(acl_code)
                parser = Parser(tokens)
                ast = parser.parse()
                compiler = ACLCompiler()
                workflow = compiler.compile(ast)

                st.session_state.stored_workflows[workflow_name_input] = workflow
                st.success(f"Workflow '{workflow_name_input}' compiled and saved!")
                st.subheader("Compiled Workflow JSON:")
                st.json(workflow.model_dump_json())
            except SyntaxError as e:
                st.error(f"ACL Syntax Error: {e}")
            except Exception as e:
                st.error(f"Error compiling workflow: {e}")
                st.exception(e)

    st.markdown("### Stored Workflows")
    if st.session_state.stored_workflows:
        for name, wf in st.session_state.stored_workflows.items():
            with st.expander(f"Workflow: {name}"):
                st.json(wf.model_dump_json())
    else:
        st.info("No workflows stored yet.")

# Debugger Page
def debugger_page():
    st.title("🐞 Debugger")

    res = st.session_state.get("res")

    if res:
        st.subheader(f"Execution Logs for: {res['execution_id']}")
        # Reverse logs to show latest first, or keep original order as per preference
        for log in res["logs"]:
            with st.expander(f"{log['step']} (Timestamp: {log['timestamp']:.2f})"):
                st.write("**Input:**")
                st.json(log["input"])
                st.write("**Output:**")
                st.json(log["output"])
    else:
        st.warning("Run an agent first to see execution logs here.")

# Replay Page
def replay_page():
    st.title("🔁 Replay Execution")

    if not st.session_state.orchestrator:
        st.warning("Orchestrator not initialized. Please go to Settings and set your API Key.")
        return

    ids = list(st.session_state.orchestrator.store.executions.keys())

    if ids:
        sel = st.selectbox("Select Execution to Replay", ids, key="replay_select_execution")

        if st.button("Replay", key="replay_button"):
            if st.session_state.replay_engine:
                with st.spinner(f"Replaying execution {sel}... "):
                    logs = st.session_state.replay_engine.replay(sel)
                    st.success(f"Replay of {sel} completed!")
                    for log_entry in logs:
                        st.write("--- :rocket:")
                        st.markdown(f"**Step:** ` {log_entry['step']} `")
                        st.markdown(f"**Input (truncated):** ` {str(log_entry['input'])[:500]}... `")
                        st.markdown(f"**Output (truncated):** ` {str(log_entry['output'])[:500]}... `")
            else:
                st.error("Replay engine not initialized.")
    else:
        st.info("No executions available for replay. Run an agent first.")

# Memory Page
def memory_page():
    st.title("🧠 Memory Management")

    if not st.session_state.orchestrator:
        st.warning("Orchestrator not initialized. Please go to Settings and set your API Key.")
        return

    st.subheader("Short-Term Memory")
    session_id = st.text_input("Session ID for Short-Term Memory", value=st.session_state.short_term_memory_session_id, key="memory_session_id")
    st.session_state.short_term_memory_session_id = session_id # Update session state

    current_short_term_memory = st.session_state.orchestrator.memory.get(session_id)
    if current_short_term_memory:
        st.json(current_short_term_memory)
    else:
        st.info(f"No short-term memory for session ID '{session_id}'.")

    if st.button("Clear Short-Term Memory", key="clear_short_term_memory_button"):
        st.session_state.orchestrator.memory.clear(session_id)
        st.success(f"Short-term memory for session ID '{session_id}' cleared!")
        st.rerun()

    st.subheader("Long-Term Memory Search")
    long_term_query = st.text_input("Search Long-Term Memory", key="long_term_query_input")
    if st.button("Search Long-Term Memory", key="search_long_term_memory_button"):
        if long_term_query:
            results = st.session_state.orchestrator.long_term_memory.search(long_term_query)
            if results:
                st.write("Found in Long-Term Memory:")
                for res in results:
                    st.markdown(f"- {res}")
            else:
                st.info("No matching results found in long-term memory.")
        else:
            st.warning("Please enter a query to search long-term memory.")

# Metrics Page
def metrics_page():
    st.title("📈 Agent Performance Metrics")

    if not st.session_state.orchestrator:
        st.warning("Orchestrator not initialized. Please go to Settings and set your API Key.")
        return

    metrics_manager = st.session_state.orchestrator.metrics_manager
    all_metrics = metrics_manager.get_all_executions_metrics()

    if not all_metrics:
        st.info("No metrics available yet. Run an agent or workflow to generate metrics.")
        return

    st.subheader("All Execution Metrics")

    # Prepare data for DataFrame
    metrics_data = []
    for execution_id, steps_metrics in all_metrics.items():
        for metric_entry in steps_metrics:
            metrics_data.append({
                "Execution ID": execution_id,
                "Step Name": metric_entry.get("step_name", "N/A"),
                "LLM Response (Truncated)": metric_entry.get("llm_response_content", "N/A")[:100] + "...",
                "Prompt Tokens": metric_entry.get("prompt_tokens", 0),
                "Completion Tokens": metric_entry.get("completion_tokens", 0),
                "Total Tokens": metric_entry.get("total_tokens", 0),
                "Total Cost ($)": round(metric_entry.get("total_cost", 0.0), 6),
                "Duration (s)": round(metric_entry.get("duration", 0.0), 4),
                "Timestamp": pd.to_datetime(metric_entry.get("timestamp", 0), unit='s')
            })

    if metrics_data:
        df = pd.DataFrame(metrics_data)
        st.dataframe(df.set_index("Timestamp").sort_index(ascending=False), use_container_width=True)

        st.markdown("--- ")
        st.subheader("Aggregated Metrics")

        # Aggregated Cost and Tokens per Execution
        agg_df_exec = df.groupby("Execution ID").agg(
            Total_Cost=("Total Cost ($)", "sum"),
            Total_Tokens=("Total Tokens", "sum"),
            Total_Duration=("Duration (s)", "sum")
        ).reset_index()

        st.markdown("#### Cost and Tokens per Execution")
        col1, col2 = st.columns(2)
        with col1:
            fig_cost = px.bar(agg_df_exec, x="Execution ID", y="Total_Cost", title="Total Cost per Execution",
                              labels={"Total_Cost": "Total Cost ($)"})
            st.plotly_chart(fig_cost, use_container_width=True)
        with col2:
            fig_tokens = px.bar(agg_df_exec, x="Execution ID", y="Total_Tokens", title="Total Tokens per Execution",
                               labels={"Total_Tokens": "Total Tokens"})
            st.plotly_chart(fig_tokens, use_container_width=True)

        st.markdown("#### Average Metrics per Step Type (Across all executions)")
        agg_df_step = df.groupby("Step Name").agg(
            Avg_Cost=("Total Cost ($)", "mean"),
            Avg_Tokens=("Total Tokens", "mean"),
            Avg_Duration=("Duration (s)", "mean"),
            Count=("Step Name", "count")
        ).reset_index()

        col3, col4 = st.columns(2)
        with col3:
            fig_avg_cost = px.bar(agg_df_step, x="Step Name", y="Avg_Cost", title="Average Cost per Step",
                                 labels={"Avg_Cost": "Average Cost ($)"})
            st.plotly_chart(fig_avg_cost, use_container_width=True)
        with col4:
            fig_avg_duration = px.bar(agg_df_step, x="Step Name", y="Avg_Duration", title="Average Duration per Step",
                                    labels={"Avg_Duration": "Average Duration (s)"})
            st.plotly_chart(fig_avg_duration, use_container_width=True)

        st.markdown("--- ")
        if st.button("Clear All Metrics", key="clear_metrics_button"):
            metrics_manager.clear_metrics()
            st.success("All metrics cleared!")
            st.rerun()


# Settings Page
def settings_page():
    st.title("⚙️ Settings")

    st.subheader("LLM Provider Configuration")

    available_providers = list(LLMService.AVAILABLE_MODELS.keys())
    selected_provider = st.selectbox(
        "Select LLM Provider",
        available_providers,
        index=available_providers.index(st.session_state.selected_llm_provider) if st.session_state.selected_llm_provider in available_providers else 0,
        key="llm_provider_select"
    )
    st.session_state.selected_llm_provider = selected_provider

    # Dynamically generate API key and model selection for each provider
    current_provider_models = LLMService.AVAILABLE_MODELS.get(selected_provider, [])

    api_key_session_key = f"{selected_provider.lower().replace(' ', '_')}_api_key"
    model_session_key = f"{selected_provider.lower().replace(' ', '_')}_model"

    api_key_input = st.text_input(
        f"Enter your {selected_provider} API Key",
        value=st.session_state.get(api_key_session_key, ""),
        type="password",
        key=f"{selected_provider.lower().replace(' ', '_')}_api_key_input"
    )
    st.session_state[api_key_session_key] = api_key_input

    if current_provider_models:
        model_select = st.selectbox(
            f"Select {selected_provider} Model",
            current_provider_models,
            index=current_provider_models.index(st.session_state.get(model_session_key, current_provider_models[0])) if st.session_state.get(model_session_key, current_provider_models[0]) in current_provider_models else 0,
            key=f"{selected_provider.lower().replace(' ', '_')}_model_select"
        )
        st.session_state[model_session_key] = model_select
    else:
        st.warning(f"No models available for {selected_provider}.")
        st.session_state[model_session_key] = ""

    if st.button("Save Settings and Re-initialize Orchestrator", key="save_settings_button"):
        initialize_orchestrator()
        if st.session_state.orchestrator:
            st.success("Settings saved and Orchestrator re-initialized!")

    # Check if any API key is present
    any_api_key_present = False
    for provider_key in LLMService.AVAILABLE_MODELS.keys():
        if st.session_state.get(f"{provider_key.lower().replace(' ', '_')}_api_key", ""):
            any_api_key_present = True
            break

    if not any_api_key_present:
        st.warning("Please enter at least one API Key to enable agent functionality.")


# Contact Page
def contact_page():
    st.title("📞 Contact")
    st.write("AgentForge OS by You 🚀")
    st.markdown("Feel free to reach out for support or feedback!")

# ---------------- PAGE DISPATCHER ----------------
page_functions = {
    "Home": home_page,
    "Run": run_page,
    "Workflow Builder": workflow_builder_page,
    "Debugger": debugger_page,
    "Replay": replay_page,
    "Memory": memory_page,
    "Metrics": metrics_page,
    "Settings": settings_page,
    "Contact": contact_page,
}

# Get the selected menu item from session state (if set by a quick action button)
# Otherwise, use the value from the sidebar selectbox
current_menu_selection = st.session_state.get("menu", menu)

# Call the appropriate page function
if current_menu_selection in page_functions:
    page_functions[current_menu_selection]()
else:
    st.error("Page not found.")
