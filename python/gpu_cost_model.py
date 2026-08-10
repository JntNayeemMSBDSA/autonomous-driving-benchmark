"""Build transparent GPU, storage, simulation, and transfer cost scenarios."""
from __future__ import annotations

import math

import pandas as pd

from config import CLEAN_DIR, MANUAL_DIR

STORAGE_USD_PER_TB_MONTH = 23.0
EGRESS_USD_PER_TB = 90.0
PRICE_FACTORS = {
    "On-demand": 1.00,
    "Committed scenario": 0.70,
    "Interruptible scenario": 0.45,
}


def calculate(scenario, price, model: str, factor: float) -> dict:
    instances = math.ceil(scenario.required_gpus / price.gpus_per_instance)
    provisioned_gpus = instances * price.gpus_per_instance
    training = (
        instances
        * price.hourly_price_usd
        * scenario.training_hours_per_run
        * scenario.number_of_runs
        / scenario.utilization_rate
        * factor
    )
    simulation = (
        scenario.simulation_gpu_hours
        * price.price_per_gpu_hour_usd
        / scenario.utilization_rate
        * factor
    )
    base_storage = scenario.storage_tb * scenario.storage_months * STORAGE_USD_PER_TB_MONTH
    checkpoint_storage = (
        scenario.checkpoint_tb * scenario.storage_months * STORAGE_USD_PER_TB_MONTH
    )
    egress = scenario.egress_tb * EGRESS_USD_PER_TB

    return {
        "scenario_id": scenario.scenario_id,
        "scenario_name": scenario.scenario_name,
        "gpu_price_id": price.gpu_price_id,
        "cloud_provider": price.cloud_provider,
        "instance_type": price.instance_type,
        "gpu_model": price.gpu_model,
        "required_gpus": scenario.required_gpus,
        "instances_required": instances,
        "provisioned_gpus": provisioned_gpus,
        "training_hours_per_run": scenario.training_hours_per_run,
        "number_of_runs": scenario.number_of_runs,
        "utilization_rate": scenario.utilization_rate,
        "discount_model": model,
        "price_factor": factor,
        "training_compute_cost_usd": training,
        "simulation_compute_cost_usd": simulation,
        "base_storage_cost_usd": base_storage,
        "checkpoint_storage_cost_usd": checkpoint_storage,
        "egress_cost_usd": egress,
        "total_cost_usd": training + simulation + base_storage + checkpoint_storage + egress,
        "source_id": price.source_id,
        "interpretation_note": (
            "Standardized analytical scenario; not an estimate of confidential company expenditure"
        ),
    }


def main() -> None:
    scenarios = pd.read_csv(MANUAL_DIR / "gpu_scenarios.csv")
    prices = pd.read_csv(CLEAN_DIR / "fact_gpu_pricing.csv")
    rows = []
    for scenario in scenarios.itertuples(index=False):
        for price in prices.itertuples(index=False):
            for model, factor in PRICE_FACTORS.items():
                rows.append(calculate(scenario, price, model, factor))

    output = pd.DataFrame(rows)
    output.insert(0, "cost_scenario_id", range(1, len(output) + 1))
    output.to_csv(CLEAN_DIR / "fact_training_cost_scenario.csv", index=False)
    print(output.groupby(["scenario_name", "discount_model"]).total_cost_usd.min().round(2))


if __name__ == "__main__":
    main()
