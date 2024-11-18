import time
import threading
import requests
from typing import Optional
from .function_watcher import FunctionWatcher
import logging
from requests.exceptions import RequestException
from .system_identification import SystemInfoSerializer, get_system_identifier


class Listener:
    def __init__(self, base_listening_url: str, poll_interval: int = 5):
        self.base_listening_url = base_listening_url
        self.poll_interval = poll_interval
        self.active = False
        self.polling_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger("prodwatch")
        self.watcher = FunctionWatcher(
            log_function_call=self._log_function_call,
        )

    def start(self):
        if self.active:
            return

        self.active = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()

    def stop(self):
        if not self.active:
            return

        self.active = False
        if self.polling_thread:
            self.polling_thread.join()

    def _get_pending_watchers(self):
        """Get list of pending function watch requests from server."""
        response = requests.get(f"{self.base_listening_url}/pending-function-names")
        if response.status_code != 200:
            return []
        payload = response.json()
        return payload.get("function_names", [])

    def _confirm_watcher(self, function_name: str):
        """Report successful watch request back to server."""
        requests.post(
            f"{self.base_listening_url}/confirm-watcher",
            json={
                "function_name": function_name,
                "status": "success",
            },
        )

    def _log_function_call(self, function_name: str, args: list, kwargs: dict):
        """Report function call back to server."""
        requests.post(
            f"{self.base_listening_url}/log-function-call",
            json={
                "function_name": function_name,
                "args": args,
                "kwargs": kwargs,
            },
        )

    def _process_pending_watchers(self, function_names: list[str]):
        """Process list of pending function watch requests."""
        for function_name in function_names:
            success = self.watcher.watch_function(function_name)
            if success:
                self._confirm_watcher(function_name)

    def _polling_loop(self):
        while self.active:
            try:
                function_names = self._get_pending_watchers()
                self._process_pending_watchers(function_names)
            except Exception as e:
                self.logger.error(f"Error polling Prodwatch server: {e}")

            time.sleep(self.poll_interval)

    def check_connection(self) -> bool:
        connection_url = f"{self.base_listening_url}/add-process"
        system_info = get_system_identifier()
        payload = {"system_info": SystemInfoSerializer.to_dict(system_info)}
        try:
            response = requests.post(connection_url, json=payload)
            response.raise_for_status()
            message = f"Successfully connected to prodwatch server at {connection_url}"
            self.logger.info(message)
            return True
        except RequestException:
            message = f"Failed to connect to prodwatch server at {connection_url}"
            self.logger.error(message)
            return False
