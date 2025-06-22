import os
import uuid
from datetime import datetime, timezone
import json
from unittest.mock import patch

from prodwatch.manager.system_identification import (
    SystemHardware,
    NetworkIdentity,
    RuntimeEnvironment,
    ProcessIdentity,
    SystemInfoSerializer,
    SystemIdentification,
)


class TestSystemHardware:
    def test_initialization(self, fake_hardware):
        assert fake_hardware.architecture == "64bit"
        assert fake_hardware.processor == "arm"
        assert fake_hardware.machine == "arm64"

    @patch("platform.architecture", return_value=("64bit", ""))
    @patch("platform.processor", return_value="arm")
    def test_from_current_system(self, fake_processor, mock_architecture):
        hardware = SystemHardware.from_current_system()
        assert hardware.architecture == "64bit"
        assert hardware.processor == "arm"


class TestNetworkIdentity:
    def test_initialization(self, fake_network):
        assert fake_network.hostname == "rpmac.local"
        assert fake_network.ip_address == "127.0.0.1"

    @patch("socket.gethostname", return_value="rpmac.local")
    @patch("socket.gethostbyname", return_value="127.0.0.1")
    def test_from_current_system(self, mock_gethostbyname, mock_gethostname):
        network = NetworkIdentity.from_current_system()
        assert network.hostname == "rpmac.local"
        assert network.ip_address == "127.0.0.1"


class TestRuntimeEnvironment:
    def test_initialization(self, fake_runtime):
        assert fake_runtime.python_version == "3.12.7"
        assert fake_runtime.platform == "macOS-13.6.2-arm64-arm-64bit"
        assert (
            fake_runtime.working_directory == "/Users/standsleeping/Developer/prodwatch"
        )
        assert fake_runtime.username == "standsleeping"
        assert fake_runtime.system_timezone == "CST"
        assert fake_runtime.start_time == datetime(
            2024, 11, 16, 15, 21, 36, 739667, tzinfo=timezone.utc
        )

    @patch("sys.version", new="3.12.7 (default)")
    @patch("platform.platform")
    @patch("os.getcwd")
    @patch("os.getenv")
    def test_from_current_system(self, mock_getenv, mock_getcwd, mock_platform):
        def get_env_side_effect(x):
            if x in ("USER", "USERNAME"):
                return "standsleeping"
            return None

        mock_platform.return_value = "macOS-13.6.2-arm64-arm-64bit"
        mock_getcwd.return_value = "/Users/standsleeping/Developer/prodwatch"
        mock_getenv.side_effect = get_env_side_effect

        runtime = RuntimeEnvironment.from_current_system()

        assert runtime.python_version == "3.12.7"
        assert runtime.platform == "macOS-13.6.2-arm64-arm-64bit"
        assert runtime.working_directory == "/Users/standsleeping/Developer/prodwatch"
        assert runtime.username == "standsleeping"

        mock_platform.assert_called_once()
        mock_getcwd.assert_called_once()

        # Could be called for both USER and USERNAME
        assert mock_getenv.call_count >= 1


class TestProcessIdentity:
    def test_initialization(self, fake_process):
        assert fake_process.pid == os.getpid()

    @patch("os.getpid", return_value=17515)
    def test_from_current_process(self, mock_getpid):
        process = ProcessIdentity.from_current_process()
        assert process.pid == os.getpid()


class TestSystemFingerprint:
    def test_initialization(self, fake_fingerprint):
        assert (
            fake_fingerprint.value
            == "7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
        )


class TestSystemInfoSerializer:
    def test_serialize_matches_expected_output(self, fake_system_identification):
        expected_json = {
            "hardware": {
                "architecture": "64bit",
                "processor": "arm",
                "machine": "arm64",
            },
            "network": {"hostname": "rpmac.local", "ip_address": "127.0.0.1"},
            "runtime": {
                "python_version": "3.12.7",
                "platform": "macOS-13.6.2-arm64-arm-64bit",
                "working_directory": "/Users/standsleeping/Developer/prodwatch",
                "username": "standsleeping",
                "system_timezone": "CST",
                "start_time": "2024-11-16T15:21:36.739667+00:00",
            },
            "process": {
                "pid": os.getpid(),
            },
            "fingerprint": {
                "value": "7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
            },
        }

        json_str = SystemInfoSerializer.serialize(
            fake_system_identification, pretty=True
        )
        assert json.loads(json_str) == expected_json

    def test_to_dict_matches_expected_output(self, fake_system_identification):
        expected_dict = {
            "hardware": {
                "architecture": "64bit",
                "processor": "arm",
                "machine": "arm64",
            },
            "network": {"hostname": "rpmac.local", "ip_address": "127.0.0.1"},
            "runtime": {
                "python_version": "3.12.7",
                "platform": "macOS-13.6.2-arm64-arm-64bit",
                "working_directory": "/Users/standsleeping/Developer/prodwatch",
                "username": "standsleeping",
                "system_timezone": "CST",
                "start_time": "2024-11-16T15:21:36.739667+00:00",
            },
            "process": {
                "pid": os.getpid(),
            },
            "fingerprint": {
                "value": "7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
            },
        }

        data_dict = SystemInfoSerializer.to_dict(fake_system_identification)
        assert data_dict == expected_dict


class TestCreateFromFlatDict:
    def test_create_from_flat_dict(self):
        """Creates a SystemIdentification object from a flat dictionary."""
        user_id = uuid.uuid4()
        process_id = uuid.uuid4()
        added_at = datetime(2025, 3, 15, 15, 0, 0, 0, tzinfo=timezone.utc).isoformat()
        architecture = "64bit"
        processor = "arm"
        machine = "arm64"
        pid = os.getpid()
        fingerprint = "7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
        hostname = "rpmac.local"
        ip_address = "127.0.0.1"
        python_version = "3.12.7"
        platform = "macOS-13.6.2-arm64-arm-64bit"
        working_directory = "/Users/standsleeping/Developer/prodwatch"
        username = "standsleeping"
        system_timezone = "CST"

        data = {
            "process_id": process_id,
            "user_id": user_id,
            "added_at": added_at,
            "architecture": architecture,
            "processor": processor,
            "machine": machine,
            "hostname": hostname,
            "ip_address": ip_address,
            "python_version": python_version,
            "platform": platform,
            "working_directory": working_directory,
            "username": username,
            "system_timezone": system_timezone,
            "start_time": added_at,
            "pid": pid,
            "fingerprint": fingerprint,
        }

        system_info = SystemIdentification.create_from_flat_dict(data)
        assert system_info.hardware.architecture == architecture
        assert system_info.hardware.processor == processor
        assert system_info.hardware.machine == machine
        assert system_info.network.hostname == hostname
        assert system_info.network.ip_address == ip_address
        assert system_info.runtime.python_version == python_version
        assert system_info.runtime.platform == platform
        assert system_info.runtime.working_directory == working_directory
        assert system_info.runtime.username == username
        assert system_info.runtime.system_timezone == system_timezone
        assert system_info.runtime.start_time == datetime.fromisoformat(added_at)
        assert system_info.process.pid == pid
        assert system_info.fingerprint.value == fingerprint
