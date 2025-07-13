import os
import uuid
import time
import threading
import requests
import logging
from typing import Optional, List, Dict, Any, cast
from requests.exceptions import RequestException
from ..exceptions import TokenError
from .function_manager import FunctionManager
from .system_identification import (
    SystemInfoSerializer,
    SystemIdentification,
    get_system_identifier,
)


class Manager:
    def __init__(self, base_server_url: str, app_name: str, poll_interval: int = 5):
        self.base_server_url = base_server_url
        self.poll_interval = poll_interval
        self.active = False
        self.polling_thread: Optional[threading.Thread] = None
        self.process_id: uuid.UUID = uuid.uuid4()
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)

        self.token = os.getenv("PRODWATCH_API_TOKEN")
        if not self.token:
            raise TokenError("PRODWATCH_API_TOKEN environment variable is required.")

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.watched_functions: set[str] = set()

        self.function_manager = FunctionManager(
            log_function_call=self.log_function_call,
        )

    def start(self) -> None:
        if self.active:
            return

        self.active = True
        self.polling_thread = threading.Thread(target=self.polling_loop, daemon=True)
        self.polling_thread.start()

    def stop(self) -> None:
        if not self.active:
            return

        self.active = False
        if self.polling_thread:
            self.polling_thread.join()

    def handle_error(self, response: requests.Response, endpoint: str) -> None:
        """Handle non-200 responses by logging the error."""
        self.logger.error(f"Error from {endpoint}: Status {response.status_code}.")

    def get_pending_function_names(self) -> List[str]:
        """Get list of pending function watch requests from server."""
        params = {
            "process_id": str(self.process_id),
            "app_name": self.app_name
        }
        response = self.session.get(
            f"{self.base_server_url}/pending-function-names", 
            params=params, 
            allow_redirects=False
        )
        if response.status_code != 200:
            self.handle_error(response, "pending-function-names")
            return []
        payload = response.json()
        return cast(List[str], payload.get("function_names", []))

    def confirm_watcher(
        self, function_name: str, finder_result: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report successful watch request back to server."""
        payload: Dict[str, Any] = {
            "event_name": "confirm-watcher",
            "function_name": function_name,
            "process_id": str(self.process_id),
            "app_name": self.app_name,
        }

        if finder_result:
            payload["finder_result"] = finder_result

        response = self.session.post(
            f"{self.base_server_url}/events",
            json=payload,
            allow_redirects=False,
        )

        if response.status_code != 200:
            self.handle_error(response, "confirm-watcher")

    def log_function_call(
        self,
        function_name: str,
        args: List[Any],  # Can be a list of any type
        kwargs: Dict[str, Any],  # Can be a dict of any type
        execution_time_ms: float,
        error: Optional[str] = None,
    ) -> None:
        """Report function call back to server."""
        data = {
            "event_name": "log-function-call",
            "function_name": function_name,
            "process_id": str(self.process_id),
            "app_name": self.app_name,
            "args": args,
            "kwargs": kwargs,
            "execution_time_ms": execution_time_ms,
            "error": error,
        }

        # Serialize args and kwargs to JSON strings
        data["args"] = [str(arg) for arg in args]
        data["kwargs"] = {k: str(v) for k, v in kwargs.items()}

        response = self.session.post(
            f"{self.base_server_url}/events",
            json=data,
            allow_redirects=False,
        )
        if response.status_code != 200:
            self.handle_error(response, "log-function-call")

    def process_pending_watchers(self, function_names: List[str]) -> None:
        """Process list of pending function watch requests."""
        for function_name in function_names:
            if function_name in self.watched_functions:
                continue
            success, finder_result = self.function_manager.watch_function(function_name)
            if success:
                self.confirm_watcher(function_name, finder_result.to_dict())
                self.watched_functions.add(function_name)
            else:
                self.failed_watcher(function_name, finder_result.to_dict())

    def polling_loop(self) -> None:
        while self.active:
            try:
                function_names = self.get_pending_function_names()
                self.process_pending_watchers(function_names)
            except Exception as e:
                self.logger.error(f"Error polling Prodwatch server: {e}")

            time.sleep(self.poll_interval)

    def check_connection(self) -> bool:
        events_url = f"{self.base_server_url}/events"
        system_info: SystemIdentification = get_system_identifier()
        payload = {
            "event_name": "add-process",
            "process_id": str(self.process_id),
            "app_name": self.app_name,
            "system_info": SystemInfoSerializer.to_dict(system_info),
        }
        try:
            response = self.session.post(
                events_url, json=payload, allow_redirects=False
            )
            response.raise_for_status()
            message = f"Successfully connected to prodwatch server at {events_url}"
            self.logger.info(message)
            return True
        except RequestException as err:
            message = f"Failed to connect to prodwatch server at {events_url}: {err}"
            self.logger.error(message)
            return False

    def failed_watcher(
        self, function_name: str, finder_result: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report failed watch request back to server."""
        payload: Dict[str, Any] = {
            "event_name": "failed-watcher",
            "function_name": function_name,
            "process_id": str(self.process_id),
            "app_name": self.app_name,
        }

        if finder_result:
            payload["finder_result"] = finder_result

        response = self.session.post(
            f"{self.base_server_url}/events",
            json=payload,
            allow_redirects=False,
        )

        if response.status_code != 200:
            self.handle_error(response, "failed-watcher")
