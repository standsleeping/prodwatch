import time
import threading
import requests
from typing import Optional
from .function_manager import FunctionManager
import logging
from requests.exceptions import RequestException
from .system_identification import SystemInfoSerializer, get_system_identifier


class Manager:
    def __init__(self, base_server_url: str, poll_interval: int = 5):
        self.base_server_url = base_server_url
        self.poll_interval = poll_interval
        self.active = False
        self.polling_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger("prodwatch")
        self.function_manager = FunctionManager(
            log_function_call=self.log_function_call,
        )

    def start(self):
        if self.active:
            return

        self.active = True
        self.polling_thread = threading.Thread(target=self.polling_loop, daemon=True)
        self.polling_thread.start()

    def stop(self):
        if not self.active:
            return

        self.active = False
        if self.polling_thread:
            self.polling_thread.join()

    def get_pending_function_names(self):
        """Get list of pending function watch requests from server."""
        response = requests.get(f"{self.base_server_url}/pending-function-names")
        if response.status_code != 200:
            return []
        payload = response.json()
        return payload.get("function_names", [])

    def confirm_watcher(self, function_name: str):
        """Report successful watch request back to server."""
        requests.post(
            f"{self.base_server_url}/events",
            json={
                "event_name": "confirm-watcher",
                "function_name": function_name,
            },
        )

    def log_function_call(self, function_name: str, args: list, kwargs: dict, execution_time_ms: float):
        """Report function call back to server."""
        requests.post(
            f"{self.base_server_url}/events",
            json={
                "event_name": "log-function-call",
                "function_name": function_name,
                "args": args,
                "kwargs": kwargs,
                "execution_time_ms": execution_time_ms,
            },
        )

    def process_pending_watchers(self, function_names: list[str]):
        """Process list of pending function watch requests."""
        for function_name in function_names:
            success = self.function_manager.watch_function(function_name)
            if success:
                self.confirm_watcher(function_name)

    def polling_loop(self):
        while self.active:
            try:
                function_names = self.get_pending_function_names()
                self.process_pending_watchers(function_names)
            except Exception as e:
                self.logger.error(f"Error polling Prodwatch server: {e}")

            time.sleep(self.poll_interval)

    def check_connection(self) -> bool:
        events_url = f"{self.base_server_url}/events"
        system_info = get_system_identifier()
        payload = {"event_name": "add-process", "system_info": SystemInfoSerializer.to_dict(system_info)}
        try:
            response = requests.post(events_url, json=payload)
            response.raise_for_status()
            message = f"Successfully connected to prodwatch server at {events_url}"
            self.logger.info(message)
            return True
        except RequestException:
            message = f"Failed to connect to prodwatch server at {events_url}"
            self.logger.error(message)
            return False
