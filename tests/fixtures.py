import os
import pytest
from datetime import datetime, timezone
from prodwatch.manager import Manager
from prodwatch.manager.system_identification import (
    SystemHardware,
    NetworkIdentity,
    SystemFingerprint,
    SystemIdentification,
    RuntimeEnvironment,
    ProcessIdentity,
)


@pytest.fixture
def manager():
    test_token = "test-token-123"
    os.environ["PRODWATCH_API_TOKEN"] = test_token
    return Manager("http://test-server.com", poll_interval=1, app_name="test-app")


@pytest.fixture
def fake_logger():
    calls = []

    def log_function_call(function_name, args, kwargs, execution_time_ms, error=None):
        calls.append(
            {
                "function_name": function_name,
                "args": args,
                "kwargs": kwargs,
                "execution_time_ms": execution_time_ms,
                "error": error,
            }
        )

    return log_function_call, calls


@pytest.fixture
def fake_hardware():
    return SystemHardware(
        architecture="64bit",
        processor="arm",
        machine="arm64",
    )


@pytest.fixture
def fake_network():
    return NetworkIdentity(
        hostname="rpmac.local",
        ip_address="127.0.0.1",
    )


@pytest.fixture
def fake_runtime():
    return RuntimeEnvironment(
        python_version="3.12.7",
        platform="macOS-13.6.2-arm64-arm-64bit",
        working_directory="/Users/standsleeping/Developer/prodwatch",
        username="standsleeping",
        system_timezone="CST",
        start_time=datetime(2024, 11, 16, 15, 21, 36, 739667, tzinfo=timezone.utc),
    )


@pytest.fixture
def fake_process():
    return ProcessIdentity(pid=os.getpid())


@pytest.fixture
def fake_fingerprint():
    return SystemFingerprint(
        value="7dc19808df5271143c1032f4a09b961d75b3bb6f4bbbb34036a69faecabee22d"
    )


@pytest.fixture
def fake_system_identification(
    fake_hardware, fake_network, fake_runtime, fake_process, fake_fingerprint
):
    return SystemIdentification(
        hardware=fake_hardware,
        network=fake_network,
        runtime=fake_runtime,
        process=fake_process,
        fingerprint=fake_fingerprint,
    )
