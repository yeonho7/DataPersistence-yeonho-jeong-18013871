from dataclasses import dataclass


@dataclass
class ProductionJob:
    job_id: str
    order_id: str
    actual_production_qty: int
    estimated_time_min: int
    queue_position: int
