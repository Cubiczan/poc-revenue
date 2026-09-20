# poc-revenue

> **Cubiczan stack** — [CHP](https://github.com/Cubiczan/consensus-hardening-protocol) · [control-spine](https://github.com/Cubiczan/control-spine) · **You are here:** `poc-revenue`

**ASC 606 over-time / percentage-of-completion.** Cost-to-cost POC, constrained transaction price, contract asset vs liability, full estimated loss on an onerous contract. Built for any listed company whose over-time revenue control cannot be reperformed from the close file.

Identify the performance obligation first. This engine measures it. It does not decide over-time vs point-in-time.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What it produces

| Artefact | What a tester samples |
|---|---|
| Contract register | TP, constrained price, estimated costs, costs incurred, billings |
| POC computation | costs incurred / estimated total cost, quantized to 4 decimals |
| Balance sheet split | contract asset (unbilled) vs contract liability (billings in excess) |
| Onerous-contract provision | remaining loss so cumulative GP equals the full estimated loss |

A $1,000,000 contract, $800,000 estimated cost, $200,000 incurred, $300,000 billed: POC **25%**, revenue **250,000**, liability **50,000**. A $1,200,000 cost estimate on the same price: estimated loss **200,000**, provision **150,000**. Both are in the tests.

## Quick start

```bash
pip install -e ".[dev]"
pytest -q
poc-revenue examples/contracts.json --period "H1 2026" --owner "Controller"
```

UiPath can hand off the same `contracts.json` shape to this CLI, so a document/workorder flow can feed the POC engine without any parser changes.

## Compliance spine

Vendored `control-spine`. Over-time vs point-in-time is an input in the foundation. The engine measures; it does not identify performance obligations. Unsigned packs are `EXPLORING`. A named owner on a non-empty population reaches `LOCKED`.

## MCP server

`src/poc_revenue/mcp_server.py` publishes the engine over Model Context Protocol: a thin wrapper in the `io.github.Cubiczan` namespace (stdio transport) whose tools — `measure_contract` and `revenue_evidence_pack` — call `poc_revenue.engine` and `poc_revenue.evidence` verbatim. All measurement logic lives in the engine module; the wrapper adds no logic, touches no network, and makes no performance-obligation judgment calls a human owns. Evidence packs built through MCP are always unsigned — the tool takes no owner, so the spine renders `EXPLORING` and `is_evidence: false`; a named human signs via the CLI (`--owner`), never through MCP.

```bash
uvx --from poc-revenue poc-revenue-mcp
# or from a checkout:
python -m poc_revenue.mcp_server
```
