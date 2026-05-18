# gemini-pipeline-agent

A GitLab CI failure triage agent built on Google Cloud Agent Builder
(ADK), Gemini 2.5, and the GitLab MCP server.

**Live demo:** https://gemini-pipeline-agent-1029931682737.us-central1.run.app
**Demo video:** https://youtu.be/CwABJ9053O4 (2:02)
**License:** Apache 2.0

## What it does

You ask "what broke on the latest failed pipeline for checkout-api?" The
agent walks the GitLab MCP tools (`list_projects`, `list_pipelines`,
`list_pipeline_jobs`, `get_job_log`), finds the failed job, reads its
log, and returns a structured triage with the root cause quoted verbatim
from the log.

Tool surface matches the official GitLab MCP server (published by
GitLab.org). A stub MCP server ships in the repo so demos run without a
GitLab tenant — canned dataset: 2 projects, 4 pipelines (2 failed), 5
jobs (2 failed), 2 captured job logs with realistic Jest output.

## Try it locally

```bash
git clone https://github.com/MukundaKatta/gemini-pipeline-agent
cd gemini-pipeline-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_LOCATION=us-central1

PYTHONPATH=src streamlit run app/dashboard.py
```

## Try it against a real GitLab tenant

```bash
export GITLAB_URL="https://gitlab.com"
export GITLAB_TOKEN="glpat-..."
```

Untick "Use stub GitLab MCP" in the sidebar.

## Tests

```bash
PYTHONPATH=src pytest -q
```

10 tests cover stub responses + the agent wiring.

## License

Apache 2.0. Mukunda Katta, independent developer.
