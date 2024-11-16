import pytest
from datetime import datetime, timezone
import uuid
import json
from unittest.mock import patch

from prodwatch.listener.system_identification import (
    SystemHardware,
    NetworkIdentity,
    RuntimeEnvironment,
    ProcessIdentity,
    SystemFingerprint,
    SystemIdentification,
    SystemInfoSerializer,
)


@pytest.fixture
def mock_hardware():
    return SystemHardware(
        architecture="64bit",
        processor="arm",
    )


@pytest.fixture
def mock_network():
    return NetworkIdentity(
        hostname="rpmac.local",
        ip_address="127.0.0.1",
    )


@pytest.fixture
def mock_runtime():
    return RuntimeEnvironment(
        python_version="3.12.7",
        platform="macOS-13.6.2-arm64-arm-64bit",
        working_directory="/Users/standsleeping/Developer/prodwatch",
        username="standsleeping",
        timezone="CST",
        start_time=datetime(2024, 11, 16, 15, 21, 36, 739667, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_process():
    return ProcessIdentity(
        process_id=17515,
        instance_id=uuid.UUID("3227e246-5713-40aa-8af7-1c20a2dcd10b"),
    )


@pytest.fixture
def mock_fingerprint():
    return SystemFingerprint(
        value="7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
    )


@pytest.fixture
def mock_system_identification(
    mock_hardware, mock_network, mock_runtime, mock_process, mock_fingerprint
):
    return SystemIdentification(
        hardware=mock_hardware,
        network=mock_network,
        runtime=mock_runtime,
        process=mock_process,
        fingerprint=mock_fingerprint,
    )


# SystemHardware tests
class TestSystemHardware:
    def test_initialization(self, mock_hardware):
        assert mock_hardware.architecture == "64bit"
        assert mock_hardware.processor == "arm"
        assert mock_hardware.machine == "arm64"

    @patch("platform.architecture", return_value=("64bit", ""))
    @patch("platform.processor", return_value="arm")
    def test_from_current_system(self, mock_processor, mock_architecture):
        hardware = SystemHardware.from_current_system()
        assert hardware.architecture == "64bit"
        assert hardware.processor == "arm"


# NetworkIdentity tests
class TestNetworkIdentity:
    def test_initialization(self, mock_network):
        assert mock_network.hostname == "rpmac.local"
        assert mock_network.ip_address == "127.0.0.1"

    @patch("socket.gethostname", return_value="rpmac.local")
    @patch("socket.gethostbyname", return_value="127.0.0.1")
    def test_from_current_system(self, mock_gethostbyname, mock_gethostname):
        network = NetworkIdentity.from_current_system()
        assert network.hostname == "rpmac.local"
        assert network.ip_address == "127.0.0.1"


# RuntimeEnvironment tests
class TestRuntimeEnvironment:
    def test_initialization(self, mock_runtime):
        assert mock_runtime.python_version == "3.12.7"
        assert mock_runtime.platform == "macOS-13.6.2-arm64-arm-64bit"
        assert (
            mock_runtime.working_directory == "/Users/standsleeping/Developer/prodwatch"
        )
        assert mock_runtime.username == "standsleeping"
        assert mock_runtime.timezone == "CST"
        assert mock_runtime.start_time == datetime(
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


# ProcessIdentity tests
class TestProcessIdentity:
    def test_initialization(self, mock_process):
        assert mock_process.process_id == 17515
        assert mock_process.instance_id == uuid.UUID(
            "3227e246-5713-40aa-8af7-1c20a2dcd10b"
        )

    @patch("os.getpid", return_value=17515)
    def test_from_current_process(self, mock_getpid):
        process = ProcessIdentity.from_current_process()
        assert process.process_id == 17515
        assert isinstance(process.instance_id, uuid.UUID)


# SystemFingerprint tests
class TestSystemFingerprint:
    def test_initialization(self, mock_fingerprint):
        assert (
            mock_fingerprint.value
            == "7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
        )


# SystemInfoSerializer tests
class TestSystemInfoSerializer:
    def test_serialize_matches_expected_output(self, mock_system_identification):
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
                "timezone": "CST",
                "start_time": "2024-11-16T15:21:36.739667+00:00",
            },
            "process": {
                "process_id": 17515,
                "instance_id": "3227e246-5713-40aa-8af7-1c20a2dcd10b",
            },
            "fingerprint": {
                "value": "7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
            },
        }

        json_str = SystemInfoSerializer.serialize(
            mock_system_identification, pretty=True
        )
        assert json.loads(json_str) == expected_json

    def test_to_dict_matches_expected_output(self, mock_system_identification):
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
                "timezone": "CST",
                "start_time": "2024-11-16T15:21:36.739667+00:00",
            },
            "process": {
                "process_id": 17515,
                "instance_id": "3227e246-5713-40aa-8af7-1c20a2dcd10b",
            },
            "fingerprint": {
                "value": "7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
            },
        }

        data_dict = SystemInfoSerializer.to_dict(mock_system_identification)
        assert data_dict == expected_dict
