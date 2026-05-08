from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer: str
    quantity: int
    status: str = field(default="RESERVED")
    created_at: str = field(default="")
    updated_at: str = field(default="")

    def __post_init__(self):
        if not self.created_at:
            now = datetime.now(timezone.utc).isoformat()
            self.created_at = now
            self.updated_at = now
