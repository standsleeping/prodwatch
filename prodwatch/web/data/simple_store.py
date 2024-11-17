from ..models import Watcher, Process


class SimpleStore:
    def __init__(self):
        self.processes = {}
        self.watchers = {}

    def add_process(self, process: Process):
        self.processes[process.instance_id] = process

    def get_process(self, instance_id: str):
        return self.processes.get(instance_id)

    def get_processes(self):
        return list(self.processes.values())

    def add_watcher(self, watcher: Watcher):
        self.watchers[watcher.function_name] = watcher

    def get_watchers(self):
        return list(self.watchers.values())

    def get_watcher(self, function_name: str):
        return self.watchers.get(function_name)
