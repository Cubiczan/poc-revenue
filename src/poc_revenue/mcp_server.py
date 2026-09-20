"""MCP server for the poc-revenue engine.

Exposes deterministic ASC 606 cost-to-cost measurement as Model Context
Protocol tools. Thin wrapper — all measurement logic lives in
``poc_revenue.engine`` and ``poc_revenue.evidence`` and is reused verbatim;
nothing here touches the network, and identifying performance obligations
stays with the control owner.

Follows the same publishing path proven by invoice-audit-engine /
codesentinel: namespace ``io.github.Cubiczan``, stdio transport, published
via the ``mcp-publisher`` CLI.

Run it:

    uvx --from poc-revenue poc-revenue-mcp
    # or, from a checkout:
    python -m poc_revenue.mcp_server
"""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from enum import Enum
from typing import Any

from mcp.server.fastmcp import FastMCP

from poc_revenue.engine import Contract, Timing, measure
from poc_revenue.evidence import evidence_pack

mcp = FastMCP(
    "poc-revenue",
    instructions=(
        "Deterministic ASC 606 over-time (cost-to-cost) revenue measurement. "
        "Supply contract terms; the tools measure percentage of completion on "
        "the constrained transaction price, accrue onerous-contract losses, "
        "and render the evidence pack a tester can reperform. The number "
        "never comes from a language model; identifying the performance "
        "obligation stays with the control owner."
    ),
)


def _contract_from_dict(item: dict[str, Any]) -> Contract:
    """Build a Contract from the CLI/JSON shape (same keys as the CLI's input file)."""
    return Contract(
        contract_id=item["contract_id"],
        description=item.get("description", ""),
        timing=Timing(item.get("timing", "over_time")),
        transaction_price=item["transaction_price"],
        constrained_price=item["constrained_price"],
        estimated_total_cost=item["estimated_total_cost"],
        costs_incurred_to_date=item["costs_incurred_to_date"],
        billings_to_date=item["billings_to_date"],
        complete=item.get("complete", False),
    )


def _jsonify(value: Any) -> Any:
    """JSON-safe conversion: Decimals become strings so cents survive exactly."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: _jsonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonify(v) for v in value]
    return value


@mcp.tool()
def measure_contract(contract: dict[str, Any]) -> dict[str, Any]:
    """Measure one performance obligation at cost-to-cost (ASC 606 over-time).

    Returns percentage of completion, constrained price, revenue and cost to
    date, onerous-contract loss provision, gross profit, and the
    contract asset / liability positions. Amounts are exact decimal strings.

    Args:
        contract: Contract terms. Expected keys mirror the CLI input file:
            contract_id, timing ("over_time" | "point_in_time"),
            transaction_price, constrained_price, estimated_total_cost,
            costs_incurred_to_date, billings_to_date, complete.
    """
    return _jsonify(asdict(measure(_contract_from_dict(contract))))


@mcp.tool()
def revenue_evidence_pack(
    contracts: list[dict[str, Any]],
    period_label: str = "current",
) -> dict[str, Any]:
    """Build the ASC 606 evidence pack a tester can reperform without the source code.

    Measures every supplied contract and aggregates the population into the
    control-spine pack (revenue to date, per-contract detail, owner sign-off).

    Args:
        contracts: Contract terms, same shape as measure_contract's input.
        period_label: Close period label (e.g. "H1 2026").
        Sign-off: MCP never accepts an owner — packs built here are always
        unsigned (EXPLORING, not evidence). A named human signs via the CLI
        (--owner), never through MCP.
    """
    rows = tuple(measure(_contract_from_dict(item)) for item in contracts)
    pack = evidence_pack(rows, period_label, owner="", invoked_via="mcp")
    return _jsonify(pack)


def main() -> None:
    """Console-script entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
