"""gemini-pipeline-agent dashboard."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gemini_pipeline_agent.runner import ask  # noqa: E402


st.set_page_config(page_title="gemini-pipeline-agent", layout="wide", page_icon=":construction:")
st.title("gemini-pipeline-agent")
st.caption(
    "GitLab CI failure triage agent on Google Cloud Agent Builder (ADK) "
    "+ Gemini 2.5, wired to the GitLab MCP server. Apache 2.0."
)

with st.sidebar:
    st.header("Triage a pipeline")
    question = st.text_area(
        "Your question",
        value="What broke on the latest failed pipeline for checkout-api?",
        height=120,
    )
    model = st.selectbox(
        "Gemini model",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"],
        index=0,
    )
    stub = st.toggle(
        "Use stub GitLab MCP",
        value=True,
        help="On = local stub with canned projects and pipelines. Off = real tenant (set GITLAB_URL + GITLAB_TOKEN).",
    )
    run = st.button("Run triage", type="primary", use_container_width=True)
    st.divider()
    st.caption(
        f"Project: `{os.getenv('GOOGLE_CLOUD_PROJECT', 'not-set')}`  "
        f"Vertex AI: `{os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'true')}`"
    )

st.markdown(
    """
The agent walks these GitLab MCP tools to triage a failed CI run:
- **list_projects** / **get_project** to resolve names to IDs
- **list_pipelines** (filtered to status=failed) for recent failures
- **list_pipeline_jobs** to find the failing job
- **get_job_log** to read the actual failure
"""
)

if run:
    with st.status("Running Vertex AI Gemini...", expanded=True) as status:
        t0 = time.perf_counter()
        try:
            resp = ask(question, stub=stub, model=model)
        except Exception as e:  # pragma: no cover
            status.update(label=f"Error: {e}", state="error")
            st.exception(e)
            st.stop()
        elapsed = (time.perf_counter() - t0) * 1000
        status.update(label=f"Done in {elapsed:.0f} ms", state="complete")

    st.subheader("Triage")
    st.markdown(resp.final_text or "_(no final response)_")

    with st.expander(f"Agent event trace ({len(resp.events)} events)"):
        for i, ev in enumerate(resp.events):
            st.markdown(f"**{i}.** author=`{ev.get('author')}` final=`{ev.get('is_final')}`")
            text = ev.get("text") or ""
            if text:
                st.code(text[:1500], language=None)
else:
    st.info("Use the sidebar to fire a triage against the stub GitLab MCP.")
