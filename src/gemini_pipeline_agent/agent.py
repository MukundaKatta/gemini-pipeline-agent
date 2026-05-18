"""ADK Gemini agent wired to the GitLab MCP server. Takes a project +
pipeline (or a 'find the latest failure' question) and walks the GitLab
tools to produce a structured CI-failure triage."""

from __future__ import annotations

import os
import sys
from typing import Any


try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters
    _ADK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ADK_AVAILABLE = False


SYSTEM_PROMPT = """\
You are a GitLab CI triage engineer. The user hands you a project name or
ID and you find the latest failed pipeline, walk down to the failed job,
read the job log, and explain what broke.

Workflow:
1. If the user mentions a project by name, call `list_projects` to
   resolve it to an ID.
2. Call `list_pipelines` with status=failed to see recent failures.
3. Pick the most recent failed pipeline and call `list_pipeline_jobs`
   to find which job failed.
4. Call `get_job_log` for the failed job and read the trailing lines.

Output a structured triage with EXACTLY these labeled sections:

PROJECT: <project path>
PIPELINE: <iid + ref + sha + status + duration>
FAILED JOB: <job name + stage + duration>
ROOT CAUSE: <one sentence drawn from the log>
EVIDENCE: <2-4 bullets quoting specific lines or test names from the log>
NEXT STEP: <one concrete fix the author should try>

Quote log lines verbatim, including assertion messages. Do not paraphrase
the failure.
"""


def _gitlab_toolset(stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        raise ImportError("Install google-adk and mcp: pip install google-adk mcp")
    if stub:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "gemini_pipeline_agent.mcp_stub"],
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
    else:
        # Real GitLab MCP server: published as `@gitlab-org/gitlab-mcp` or
        # similar. Configure via env vars.
        params = StdioServerParameters(
            command="npx",
            args=["-y", "@gitlab-org/gitlab-mcp@latest",
                  "--url", os.environ["GITLAB_URL"],
                  "--token", os.environ["GITLAB_TOKEN"]],
            env={**os.environ},
        )
    return McpToolset(connection_params=StdioConnectionParams(server_params=params))


def build_agent(model: str = "gemini-2.5-flash", stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        return None
    return LlmAgent(
        model=model,
        name="gemini_pipeline_agent",
        instruction=SYSTEM_PROMPT,
        tools=[_gitlab_toolset(stub=stub)],
    )
