
import sys
import os

# ✅ FIX: Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from app.core.agents.agent_orchestrator import AgentOrchestrator
# from google.colab import userdata # No longer directly using userdata inside the app

# ✅ Initialize orchestrator with secure API key from environment variable
groq_api_key = os.environ.get('GROQ_API_KEY') # Get from environment variable
if not groq_api_key:
    st.error("GROQ_API_KEY not found. Please set it in Colab secrets and ensure it's passed as an environment variable.")
    st.stop()
orchestrator = AgentOrchestrator(api_key=groq_api_key)

st.set_page_config(layout="wide")

st.title("🚀 AgentForge OS")

# Input
task = st.text_area("Enter Task")

if st.button("Run Agent"):

    result = orchestrator.run(task)

    st.subheader("✅ Final Output")
    st.write(result["final"])

    st.subheader("🧠 Execution Logs")

    for log in result["logs"]:
        st.write("### 🔹 Step:", log["step"])
        st.write("**Input:**", str(log["input"])[:200])
        st.write("**Output:**", str(log["output"])[:200])
        st.write("----------")
