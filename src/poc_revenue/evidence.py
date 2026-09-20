from __future__ import annotations

from decimal import Decimal

from control_spine import render_spine, seal
from poc_revenue.engine import Measurement, money

FOUNDATION = (
    "Over-time vs point-in-time is an input. This engine does not identify performance obligations.",
    "Variable consideration is measured at the constrained amount the owner supplies.",
    "Cost-to-cost is the progress measure for over-time contracts.",
    "Onerous contracts accrue the full estimated loss in the current period.",
)

ENGINE_ID = "poc-revenue-engine"
ENGINE_VERSION = "0.1.0"


def evidence_pack(rows: tuple[Measurement, ...], period_label: str, owner: str, invoked_via: str | None = None) -> dict:
    revenue = money(sum((r.revenue_to_date for r in rows), Decimal("0")))
    pack = {
        "control_id": "ICFR-ASC606-01",
        "control_objective": "Over-time revenue is measured at cost-to-cost on constrained transaction price; onerous contracts accrue the full estimated loss.",
        "period": period_label,
        "population_count": len(rows),
        "threshold": "100% of open over-time contracts; variable consideration constrained before measurement.",
        "revenue_to_date": str(revenue),
        "contracts": [
            {
                "contract_id": r.contract_id,
                "poc": str(r.poc),
                "price": str(r.price),
                "revenue_to_date": str(r.revenue_to_date),
                "costs_to_date": str(r.costs_to_date),
                "estimated_total_loss": str(r.estimated_total_loss),
                "loss_provision": str(r.loss_provision),
                "gross_profit_to_date": str(r.gross_profit_to_date),
                "contract_asset": str(r.contract_asset),
                "contract_liability": str(r.contract_liability),
            }
            for r in rows
        ],
        "prepared_by": ENGINE_ID,
        "owner_signoff": owner,
        "conclusion": f"Revenue to date {revenue}. Owner confirms estimated costs and the constraint of variable consideration.",
    }
    if invoked_via is not None:
        pack["invoked_via"] = invoked_via
    return seal(
        pack,
        engine_id=ENGINE_ID,
        engine_version=ENGINE_VERSION,
        inputs={"contract_ids": [r.contract_id for r in rows], "period": period_label},
        foundation=FOUNDATION,
    )


def evidence_markdown(pack: dict) -> str:
    lines = [
        f"# ASC 606 / POC evidence pack — {pack['period']}",
        "",
        *render_spine(pack),
        f"**Control:** {pack['control_id']}",
        f"**Revenue to date:** {pack['revenue_to_date']}",
        f"**Owner sign-off:** {pack['owner_signoff'] or '_unsigned_'}",
        "",
        "| Contract | POC | Price | Revenue | Loss provision | Asset | Liability |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in pack["contracts"]:
        lines.append(
            f"| {row['contract_id']} | {row['poc']} | {row['price']} | {row['revenue_to_date']} | "
            f"{row['loss_provision']} | {row['contract_asset']} | {row['contract_liability']} |"
        )
    lines += ["", pack["conclusion"], ""]
    return "\n".join(lines)
