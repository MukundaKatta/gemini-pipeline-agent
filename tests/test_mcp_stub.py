from gemini_pipeline_agent.mcp_stub import (
    _PROJECTS,
    _PIPELINES,
    _JOBS,
    _JOB_LOGS,
    list_projects_response,
    get_project_response,
    list_pipelines_response,
    list_pipeline_jobs_response,
    get_job_log_response,
)


def test_data_seeded():
    assert len(_PROJECTS) >= 2
    assert 42 in _PIPELINES
    assert 11457 in _JOBS
    assert 50003 in _JOB_LOGS


def test_list_projects_returns_checkout_and_payment():
    payload = list_projects_response()
    names = [p["name"] for p in payload["projects"]]
    assert "checkout-api" in names
    assert "payment-svc" in names


def test_get_project_resolves_id():
    payload = get_project_response(42)
    assert payload["path"] == "acme/checkout-api"


def test_list_pipelines_filters_by_failed_status():
    payload = list_pipelines_response(42, status="failed")
    assert payload["count"] >= 2
    assert all(p["status"] == "failed" for p in payload["pipelines"])


def test_list_pipeline_jobs_finds_failed_job():
    payload = list_pipeline_jobs_response(11457)
    failed = [j for j in payload["jobs"] if j["status"] == "failed"]
    assert len(failed) == 1
    assert failed[0]["name"] == "integration"


def test_get_job_log_returns_assertion_message():
    payload = get_job_log_response(50003)
    assert "router.integration.test.ts" in payload["log"]
    assert "Received number of calls: 3" in payload["log"]
    assert "ERROR: Job failed" in payload["log"]


def test_get_job_log_unknown_returns_error():
    payload = get_job_log_response(99999)
    assert "error" in payload
