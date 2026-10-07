"""Bank Statement config evaluation and opt-in real MCP/agent acceptance tests."""

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "mcp" / "http" / "bank-statement" / "config.exs"
AGENT = ROOT / "agents" / "bank_statement_agent.exs"
HARNESS = ROOT.parent / "aetheris"


def test_agent_uses_config_and_discovered_schemas_only():
    source = AGENT.read_text()
    assert "Code.eval_file(config_path)" in source
    assert "mcp_servers: mcp_servers" in source
    assert "tools: []" in source
    assert "context_strategy: :full" in source
    for name in ("bank_statement_list", "find_bank_statement", "bank_statement_to_hledger"):
        assert name not in source
    assert "run_command" not in source
    assert 'user_prompt: "Help me with my bank statements."' in source


@pytest.fixture
def evaluate_config():
    if shutil.which("elixir") is None:
        pytest.skip("elixir not on PATH")

    def evaluate(overrides, assertion):
        env = {k: v for k, v in os.environ.items() if not k.startswith("BANK_STATEMENT_")}
        env.update(overrides)
        script = (
            f"{{config, _}} = Code.eval_file({json.dumps(str(CONFIG))})\n"
            f"unless {assertion}, do: raise(\"unexpected configuration\")"
        )
        return subprocess.run(
            ["elixir", "-e", script], env=env, capture_output=True, text=True, timeout=30
        )

    return evaluate


@pytest.mark.integration
@pytest.mark.parametrize("enabled", [None, "false", "TRUE", "1"])
def test_disabled_config_needs_no_url(evaluate_config, enabled):
    env = {} if enabled is None else {"BANK_STATEMENT_MCP_ENABLED": enabled}
    result = evaluate_config(env, "is_nil(config)")
    assert result.returncode == 0, result.stderr


@pytest.mark.integration
def test_enabled_config_forwards_url_headers_and_timeout(evaluate_config):
    result = evaluate_config(
        {
            "BANK_STATEMENT_MCP_ENABLED": "true",
            "BANK_STATEMENT_MCP_URL": "https://bank.example/mcp",
            "BANK_STATEMENT_MCP_TIMEOUT_MS": "45000",
            "BANK_STATEMENT_MCP_HEADER_AUTHORIZATION": "******",
            "BANK_STATEMENT_MCP_HEADER_X_TENANT_ID": "test-tenant",
        },
        'config == %{server_id: "bank_statement", transport: :http, '
        'url: "https://bank.example/mcp", timeout_ms: 45000, '
        'headers: %{"authorization" => "******", '
        '"x-tenant-id" => "test-tenant"}}',
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.integration
def test_loopback_config_defaults(evaluate_config):
    result = evaluate_config(
        {
            "BANK_STATEMENT_MCP_ENABLED": "true",
            "BANK_STATEMENT_MCP_URL": "http://127.0.0.1:3000/mcp",
        },
        "config.timeout_ms == 30000 && config.headers == %{}",
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.integration
@pytest.mark.parametrize(
    "overrides,error",
    [
        ({}, "BANK_STATEMENT_MCP_URL"),
        ({"BANK_STATEMENT_MCP_URL": ""}, "BANK_STATEMENT_MCP_URL"),
        ({"BANK_STATEMENT_MCP_URL": "file:///tmp/mcp"}, "BANK_STATEMENT_MCP_URL"),
        ({"BANK_STATEMENT_MCP_URL": "https://user@bank.example/mcp"}, "BANK_STATEMENT_MCP_URL"),
        ({"BANK_STATEMENT_MCP_URL": "http://bank.example/mcp"}, "HTTPS"),
        ({"BANK_STATEMENT_MCP_TIMEOUT_MS": "0"}, "BANK_STATEMENT_MCP_TIMEOUT_MS"),
        ({"BANK_STATEMENT_MCP_TIMEOUT_MS": "-1"}, "BANK_STATEMENT_MCP_TIMEOUT_MS"),
        ({"BANK_STATEMENT_MCP_TIMEOUT_MS": "30oops"}, "BANK_STATEMENT_MCP_TIMEOUT_MS"),
        ({"BANK_STATEMENT_MCP_HEADER_X_TENANT_ID": ""}, "Invalid Bank Statement MCP header"),
        ({"BANK_STATEMENT_MCP_HEADER_AUTHORIZATION": "value\r\nInjected: yes"}, "Invalid Bank Statement MCP header"),
    ],
)
def test_invalid_enabled_config_fails(evaluate_config, overrides, error):
    env = {
        "BANK_STATEMENT_MCP_ENABLED": "true",
        "BANK_STATEMENT_MCP_URL": "https://bank.example/mcp",
    }
    if not overrides:
        del env["BANK_STATEMENT_MCP_URL"]
    env.update(overrides)
    result = evaluate_config(env, "true")
    assert result.returncode != 0
    assert error in result.stderr


@pytest.mark.integration
@pytest.mark.parametrize(
    "user_request,tool",
    [
        ("List my available bank statements.", "bank_statement_list"),
        ("Find my bank statement.", "find_bank_statement"),
        ("Convert the bank statement to hledger format.", "bank_statement_to_hledger"),
    ],
)
def test_live_agent_flow(user_request, tool):
    if os.environ.get("BANK_STATEMENT_MCP_TEST_LIVE") != "true":
        pytest.skip("set BANK_STATEMENT_MCP_TEST_LIVE=true with a test server and LLM credentials")
    assert HARNESS.is_dir(), "sibling Aetheris harness is required"
    assert shutil.which("mix"), "mix is required"
    assert os.environ.get("BANK_STATEMENT_MCP_ENABLED") == "true"
    run_id = f"bank-statement-test-{uuid.uuid4().hex}"
    script = f"""
    alias Aetheris.CLI.Commands.RunHelpers
    :ok = RunHelpers.ensure_started()
    {{:ok, config}} = RunHelpers.load_agent_file({json.dumps(str(AGENT))})
    config = %{{config | run_id: {json.dumps(run_id)}, user_prompt: {json.dumps(user_request)}}}
    {{:ok, id}} = Aetheris.start_run(config)
    {{:ok, _}} = RunHelpers.await_run(id, verbose: false)
    """
    result = subprocess.run(
        ["mix", "run", "--eval", script],
        cwd=HARNESS, env=os.environ.copy(), capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, "agent run failed; inspect local harness logs"
    trajectory = json.loads((HARNESS / "priv" / "runs" / run_id / "trajectory.json").read_text())
    events = trajectory["events"]
    calls = [
        event for event in events
        if event["type"] == "tool_called"
        and event["payload"].get("server_id") == "bank_statement"
        and tool in event["payload"].get("tool_name", "")
    ]
    assert calls, f"agent did not select {tool} from the discovered schemas"
    tool_names = {event["payload"]["tool_name"] for event in calls}
    results = [
        event["payload"] for event in events
        if event["type"] == "tool_result" and event["payload"].get("tool_name") in tool_names
    ]
    assert results, "no MCP response was recorded"
    assert any(
        not payload.get("is_error", False)
        and payload.get("exit_code", 0) in (0, None)
        and (payload.get("output") or payload.get("result"))
        for payload in results
    ), "no successful MCP response was recorded"
