import time
import threading
import requests
from typing import Optional
from ..injection.function_injector import FunctionInjector


class ServerPoller:
    def __init__(self, server_url: str, poll_interval: int = 5):
        self.server_url = server_url
        self.poll_interval = poll_interval
        self.active = False
        self.polling_thread: Optional[threading.Thread] = None
        self.injector = FunctionInjector()

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
        response = requests.get(f"{self.server_url}/pending-injections")
        if response.status_code != 200:
            return []
        payload = response.json()
        return payload.get("function_names", [])

    def _report_injection_success(self, function_name: str):
        """Report successful injection back to server."""
        requests.post(
            f"{self.server_url}/injection-status",
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