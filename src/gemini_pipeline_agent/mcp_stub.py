"""Stub GitLab MCP server.

Exposes a slice of the official GitLab MCP server's tool surface
(`list_projects`, `get_project`, `list_pipelines`, `get_pipeline`,
`list_pipeline_jobs`, `get_job_log`) shaped so the same agent code drops
in unchanged against a real GitLab tenant via the published MCP server.

Run with: python -m gemini_pipeline_agent.mcp_stub
"""

from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


NOW = datetime.now(timezone.utc)
_RNG = random.Random(2026)


_PROJECTS = [
    {
        "id":   42,
        "path": "acme/checkout-api",
        "name": "checkout-api",
        "default_branch": "main",
        "visibility": "private",
        "last_activity_at": (NOW - timedelta(minutes=7)).isoformat(),
    },
    {
        "id":   43,
        "path": "acme/payment-svc",
        "name": "payment-svc",
        "default_branch": "main",
        "visibility": "private",
        "last_activity_at": (NOW - timedelta(hours=2)).isoformat(),
    },
]

_PIPELINES = {
    42: [
        {
            "id":      11457,
            "iid":     332,
            "ref":     "feat/whatsapp-no-stream",
            "sha":     "9f2a1b...",
            "status":  "failed",
            "source":  "merge_request_event",
            "user":    "mukundakatta",
            "created_at": (NOW - timedelta(minutes=23)).isoformat(),
            "duration_seconds": 612,
        },
        {
            "id":      11455,
            "iid":     331,
            "ref":     "main",
            "sha":     "a3c1d8...",
            "status":  "success",
            "source":  "push",
            "user":    "release-bot",
            "created_at": (NOW - timedelta(hours=4)).isoformat(),
            "duration_seconds": 547,
        },
        {
            "id":      11448,
            "iid":     330,
            "ref":     "feat/inhouse-jwt",
            "sha":     "7d9e22...",
            "status":  "failed",
            "source":  "merge_request_event",
            "user":    "some-contractor",
            "created_at": (NOW - timedelta(hours=6)).isoformat(),
            "duration_seconds": 932,
        },
    ],
    43: [
        {
            "id":      8721,
            "iid":     97,
            "ref":     "main",
            "sha":     "b4e88c...",
            "status":  "success",
            "source":  "push",
            "user":    "release-bot",
            "created_at": (NOW - timedelta(hours=2)).isoformat(),
            "duration_seconds": 410,
        },
    ],
}

_JOBS = {
    11457: [
        {"id": 50001, "name": "lint",            "stage": "test",   "status": "success", "duration_seconds": 32},
        {"id": 50002, "name": "unit-tests",      "stage": "test",   "status": "success", "duration_seconds": 184},
        {"id": 50003, "name": "integration",     "stage": "test",   "status": "failed",  "duration_seconds": 274},
        {"id": 50004, "name": "build-image",     "stage": "build",  "status": "skipped", "duration_seconds": 0},
        {"id": 50005, "name": "deploy-staging",  "stage": "deploy", "status": "skipped", "duration_seconds": 0},
    ],
    11448: [
        {"id": 50101, "name": "lint",            "stage": "test",   "status": "success", "duration_seconds": 41},
        {"id": 50102, "name": "unit-tests",      "stage": "test",   "status": "failed",  "duration_seconds": 218},
        {"id": 50103, "name": "integration",     "stage": "test",   "status": "skipped", "duration_seconds": 0},
        {"id": 50104, "name": "build-image",     "stage": "build",  "status": "skipped", "duration_seconds": 0},
    ],
}

_JOB_LOGS = {
    50003: (
        "Starting integration tests against staging-mirror...\n"
        "PASS  test/whatsapp/router.test.ts  (12 / 12)\n"
        "PASS  test/whatsapp/buffer.test.ts  (8 / 8)\n"
        "FAIL  test/channels/router.integration.test.ts\n"
        "  ● Router › flushes once per is_final\n"
        "    expect(sendChunk).toHaveBeenCalledTimes(1)\n"
        "    Received number of calls: 3\n"
        "    at Object.<anonymous> (test/channels/router.integration.test.ts:42:38)\n"
        "Tests:       1 failed, 19 passed, 20 total\n"
        "ERROR: integration tests failed\n"
        "Cleaning up project directory and file based variables\n"
        "ERROR: Job failed: exit code 1\n"
    ),
    50102: (
        "Running unit tests...\n"
        "FAIL  src/auth/jwt.test.ts\n"
        "  ● jwt › verifies RS256 token signed by jose\n"
        "    Error: signature verification failed\n"
        "    at Object.<anonymous> (src/auth/jwt.test.ts:88:14)\n"
        "  ● jwt › rejects expired token\n"
        "    Error: signature verification failed\n"
        "    at Object.<anonymous> (src/auth/jwt.test.ts:104:14)\n"
        "Tests:       2 failed, 38 passed, 40 total\n"
        "ERROR: unit tests failed\n"
        "ERROR: Job failed: exit code 1\n"
    ),
}


def list_projects_response() -> dict[str, Any]:
    return {"projects": _PROJECTS}


def get_project_response(project_id: int) -> dict[str, Any]:
    for p in _PROJECTS:
        if p["id"] == project_id:
            return p
    return {"error": f"unknown project {project_id}"}


def list_pipelines_response(project_id: int, status: str | None = None) -> dict[str, Any]:
    pipelines = list(_PIPELINES.get(project_id, []))
    if status:
        pipelines = [p for p in pipelines if p["status"] == status]
    return {"project_id": project_id, "count": len(pipelines), "pipelines": pipelines}


def get_pipeline_response(project_id: int, pipeline_id: int) -> dict[str, Any]:
    for p in _PIPELINES.get(project_id, []):
        if p["id"] == pipeline_id:
            return p
    return {"error": f"unknown pipeline {pipeline_id} on project {project_id}"}


def list_pipeline_jobs_response(pipeline_id: int) -> dict[str, Any]:
    jobs = _JOBS.get(pipeline_id, [])
    return {"pipeline_id": pipeline_id, "count": len(jobs), "jobs": jobs}


def get_job_log_response(job_id: int) -> dict[str, Any]:
    log = _JOB_LOGS.get(job_id)
    if log is None:
        return {"error": f"no log captured for job {job_id}", "job_id": job_id}
    return {"job_id": job_id, "log": log}


def _make_server() -> Server:
    server = Server("gitlab-stub")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="list_projects",
                 description="List GitLab projects accessible to the configured user/token.",
                 inputSchema={"type": "object", "properties": {}, "required": []}),
            Tool(name="get_project",
                 description="Fetch one project's metadata.",
                 inputSchema={"type": "object",
                              "properties": {"project_id": {"type": "integer"}},
                              "required": ["project_id"]}),
            Tool(name="list_pipelines",
                 description=("List CI pipelines for a project. Optionally filter by status "
                              "(running / pending / success / failed / canceled / skipped)."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "project_id": {"type": "integer"},
                                  "status": {"type": "string"},
                              },
                              "required": ["project_id"]}),
            Tool(name="get_pipeline",
                 description="Fetch one pipeline's status, source, ref, sha, duration.",
                 inputSchema={"type": "object",
                              "properties": {
                                  "project_id":  {"type": "integer"},
                                  "pipeline_id": {"type": "integer"},
                              },
                              "required": ["project_id", "pipeline_id"]}),
            Tool(name="list_pipeline_jobs",
                 description="List the jobs (with stage + status) for one pipeline.",
                 inputSchema={"type": "object",
                              "properties": {"pipeline_id": {"type": "integer"}},
                              "required": ["pipeline_id"]}),
            Tool(name="get_job_log",
                 description=("Fetch the captured stdout/stderr log for one job. Returns "
                              "the raw text so the agent can pattern-match failures."),
                 inputSchema={"type": "object",
                              "properties": {"job_id": {"type": "integer"}},
                              "required": ["job_id"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        a = arguments
        if name == "list_projects":
            payload = list_projects_response()
        elif name == "get_project":
            payload = get_project_response(int(a.get("project_id") or 0))
        elif name == "list_pipelines":
            payload = list_pipelines_response(int(a.get("project_id") or 0),
                                              a.get("status"))
        elif name == "get_pipeline":
            payload = get_pipeline_response(int(a.get("project_id") or 0),
                                             int(a.get("pipeline_id") or 0))
        elif name == "list_pipeline_jobs":
            payload = list_pipeline_jobs_response(int(a.get("pipeline_id") or 0))
        elif name == "get_job_log":
            payload = get_job_log_response(int(a.get("job_id") or 0))
        else:
            payload = {"error": f"unknown tool {name!r}"}
        return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]

    return server


async def _main() -> None:
    server = _make_server()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
