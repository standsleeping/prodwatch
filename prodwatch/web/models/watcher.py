from dataclasses import dataclass


@dataclass
class Watcher:
    function_name: str
    status: str
    calls: list[dict]
