import time
import threading
import requests
from typing import Optional
from ..injection.function_injector import FunctionInjector
import logging
from requests.exceptions import RequestException


class Listener:
    def __init__(self, base_listening_url: str, poll_interval: int = 5):
        self.base_listening_url = base_listening_url
        self.poll_interval = poll_interval
        self.active = False
        self.polling_thread: Optional[threading.Thread] = None
        self.injector = FunctionInjector()
        self.logger = logging.getLogger("prodwatch")

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

    def _get_pending_injections(self):
        """Get list of pending function injections from server."""
        response = requests.get(f"{self.base_listening_url}/pending-injections")
        if response.status_code != 200:
            return []
        payload = response.json()
        return payload.get("function_names", [])

    def _report_injection_success(self, function_name: str):
        """Report successful injection back to server."""
        requests.post(
            f"{self.base_listening_url}/injection-status",
            json={
                "function_name": function_name,
                "status": "success",
            },
        )

    def _process_pending_injections(self, function_names: list[str]):
        """Process list of pending function injections."""
        for function_name in function_names:
            success = self.injector.inject_function(function_name)
            if success:
                self._report_injection_success(function_name)

    def _polling_loop(self):
        while self.active:
            try:
                function_names = self._get_pending_injections()
                self._process_pending_injections(function_names)
            except Exception as e:
                print(f"Error polling server: {e}")

            time.sleep(self.poll_interval)

    def check_connection(self) -> bool:
        try:
            response = requests.get(self.base_listening_url)
            response.raise_for_status()
            message = f"Successfully connected to prodwatch server at {self.base_listening_url}"
            self.logger.info(message)
            return True
        except RequestException:
            message = f"Failed to connect to prodwatch server at {self.base_listening_url}"
            self.logger.error(message)
            return False