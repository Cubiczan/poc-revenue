"""The MCP server registers the engine's deterministic measurement as callable tools.

Pins the README's canonical example ($1M price, $800K estimate, $200K incurred,
$300K billed -> POC 25%, revenue 250,000, liability 50,000) through the MCP tool
path. Skipped cleanly when the optional ``mcp`` SDK is not installed.
"""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("mcp")

from poc_revenue import mcp_server  # noqa: E402


def _tool_names() -> set[str]:
    tools = asyncio.run(mcp_server.mcp.list_tools())
    return {t.name for t in tools}


def _contract() -> dict:
    return {
        "contract_id": "C-1000",
        "description": "readme canonical example",
        "timing": "over_time",
        "transaction_price": "1000000",
        "constrained_price": "1000000",
        "estimated_total_cost": "800000",
        "costs_incurred_to_date": "200000",
        "billings_to_date": "300000",
    }


def test_expected_tools_registered() -> None:
    assert _tool_names() >= {"measure_contract", "revenue_evidence_pack"}


def test_measure_contract_pins_the_readme_numbers() -> None:
    m = mcp_server.measure_contract(_contract())
    assert m["poc"] == "0.2500"
    assert m["revenue_to_date"] == "250000.00"
    assert m["contract_liability"] == "50000.00"
    assert m["contract_asset"] == "0.00"


def test_evidence_pack_totals_population() -> None:
    pack = mcp_server.revenue_evidence_pack(
        [_contract()], period_label="H1 2026", owner="Controller"
    )
    assert pack["population_count"] == 1
    assert pack["revenue_to_date"] == "250000.00"
