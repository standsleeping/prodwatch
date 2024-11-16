from datetime import datetime


class SimpleStore:
    def __init__(self):
        self.processes = {}

    def connect_process(self, instance_id: str):
        in_memory_process = {
            "instance_id": instance_id,
            "connected_at": datetime.now(),
        }
        self.processes[instance_id] = in_memory_process

    def get_process(self, instance_id: str):
        return self.processes.get(instance_id)

    def get_processes(self):
        return list(self.processes.values())
