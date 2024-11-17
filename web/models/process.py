from dataclasses import dataclass
from datetime import datetime

@dataclass
class Process:
    instance_id: str
    connected_at: datetime
