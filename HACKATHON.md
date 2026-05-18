# Google Cloud Rapid Agent Hackathon — GitLab partner track submission

Devpost: https://rapid-agent.devpost.com
Deadline: 2026-06-11 14:00 PDT
Track: **GitLab**

This is the sixth substantively-different submission from Mukunda Katta
to this hackathon (rule 7B explicitly allows multiple unique submissions):

- `ragvitals` — RAG drift agent
- `gemini-ops-agent` — Dynatrace MCP incident investigator
- `gemini-eval-agent` — Arize Phoenix MCP LLM-eval auditor
- `gemini-data-agent` — MongoDB MCP NL-to-query agent
- `gemini-search-agent` — Elastic MCP NL-to-search agent
- `gemini-pipeline-agent` (this entry) — GitLab MCP CI-failure triage

Different partner, different MCP, different agent goal.

## Rule compliance

| Rule | How we meet it |
|---|---|
| Powered by Gemini | gemini-2.5-flash via Vertex AI |
| Powered by Google Cloud Agent Builder | `google.adk.agents.LlmAgent` (ADK) |
| Integrates a Partner's MCP server | Tool surface matches the official GitLab MCP server (gitlab-org/gitlab); stub for demos, real tenant via env vars |
| Newly created during Contest Period | Repo init 2026-05-18, within May 5 – Jun 11 window |
| Original creation, not extension | Standalone repo |
| OSI license at repo root | Apache 2.0 |
| Runs on web | Streamlit dashboard, Cloud Run deployable |

## Elevator pitch
A Gemini agent that walks down from a failed GitLab pipeline to the
specific job log line that broke it, via the GitLab MCP server.

## Description
gemini-pipeline-agent treats every red pipeline as a triage job. The
agent walks the GitLab MCP tools in order: `list_projects` to resolve
the project name, `list_pipelines` (status=failed) to find the most
recent failure, `list_pipeline_jobs` to identify which job failed, and
`get_job_log` to pull the captured stdout/stderr.

A real Vertex AI Gemini run on the canned 'checkout-api' project
identified the failure: pipeline 332 on `feat/whatsapp-no-stream` failed
because the `integration` job's test `Router > flushes once per
is_final` got `Received number of calls: 3` when it expected 1, at
`test/channels/router.integration.test.ts:42:38`. The agent quoted five
specific log lines verbatim and proposed the right next step.

## Built with
python, gemini, gemini-2-5, vertex-ai, google-cloud-agent-builder,
agent-development-kit, mcp, model-context-protocol, gitlab, gitlab-mcp,
streamlit, google-cloud-run, apache-2

## Try it out
- Code repo: https://github.com/MukundaKatta/gemini-pipeline-agent
- Live demo (Cloud Run): <PASTE_AFTER_DEPLOY>
- Demo video (YouTube unlisted): <PASTE_AFTER_REC>
