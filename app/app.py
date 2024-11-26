from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from asyncio import Queue
from collections import defaultdict


class WatcherStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILURE = "failure"


@dataclass
class Watcher:
    function_name: str
    status: WatcherStatus
    calls: list[dict]


@dataclass
class Process:
    instance_id: str
    connected_at: datetime


class ProdwatchApp:
    def __init__(self) -> None:
        self.watchers: list[Watcher] = []
        self.processes: list[Process] = []
        self.function_queues: dict[str, Queue] = defaultdict(Queue)

    def add_process(self, instance_id: str) -> None:
        self.processes.append(Process(instance_id, datetime.now()))

    def get_process_ids(self) -> list[str]:
        return [process.instance_id for process in self.processes]

    def add_watcher(self, function_name: str) -> None:
        self.watchers.append(Watcher(function_name, WatcherStatus.PENDING, []))

    def get_function_calls(self, function_name: str) -> list[dict]:
        for watcher in self.watchers:
            if watcher.function_name == function_name:
                return watcher.calls
        return []

    def confirm_watcher(self, function_name: str) -> None:
        for watcher in self.watchers:
            if watcher.function_name == function_name:
                watcher.status = WatcherStatus.CONFIRMED
                return

    def get_pending_function_names(self) -> list[str]:
        return [
            watcher.function_name
            for watcher in self.watchers
            if watcher.status == WatcherStatus.PENDING
        ]

    def log_function_call(self, function_name: str, data: dict) -> None:
        for watcher in self.watchers:
            if watcher.function_name == function_name:
                watcher.calls.append(data)
                self.function_queues[function_name].put_nowait(data)
