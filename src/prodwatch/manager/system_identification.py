from __future__ import annotations

import os
import sys
import socket
import platform
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from dataclasses import asdict, is_dataclass
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SystemHardware:
    """Hardware-specific system information"""

    architecture: str
    processor: str
    machine: str

    @classmethod
    def from_current_system(cls) -> "SystemHardware":
        return cls(
            architecture=platform.architecture()[0],
            processor=platform.processor() or "unknown",
            machine=platform.machine() or "unknown",
        )


@dataclass(frozen=True)
class NetworkIdentity:
    """Network-related identification information"""

    hostname: str
    ip_address: str

    @classmethod
    def from_current_system(cls) -> "NetworkIdentity":
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            ip_address = "unknown"
        return cls(hostname=hostname, ip_address=ip_address)


@dataclass(frozen=True)
class RuntimeEnvironment:
    """Runtime environment information"""

    python_version: str
    platform: str
    working_directory: str
    username: Optional[str]
    system_timezone: str
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_current_system(cls) -> "RuntimeEnvironment":
        return cls(
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            working_directory=os.getcwd(),
            username=os.getenv("USER") or os.getenv("USERNAME"),
            system_timezone=datetime.now().astimezone().tzname() or "unknown",
        )


@dataclass(frozen=True)
class ProcessIdentity:
    """Process-specific identification information"""

    pid: int

    @classmethod
    def from_current_process(cls) -> "ProcessIdentity":
        return cls(pid=os.getpid())


@dataclass(frozen=True)
class SystemFingerprint:
    """Stable system fingerprint for consistent identification"""

    value: str

    @classmethod
    def from_current_system(cls) -> "SystemFingerprint":
        fingerprint_data = (
            f"{platform.node()}{platform.machine()}{platform.processor()}{os.getcwd()}"
        ).encode("utf-8")
        return cls(value=hashlib.sha256(fingerprint_data).hexdigest())


@dataclass(frozen=True)
class SystemIdentification:
    """Complete system identification information"""

    hardware: SystemHardware
    network: NetworkIdentity
    runtime: RuntimeEnvironment
    process: ProcessIdentity
    fingerprint: SystemFingerprint

    @classmethod
    def from_current_system(cls) -> "SystemIdentification":
        return cls(
            hardware=SystemHardware.from_current_system(),
            network=NetworkIdentity.from_current_system(),
            runtime=RuntimeEnvironment.from_current_system(),
            process=ProcessIdentity.from_current_process(),
            fingerprint=SystemFingerprint.from_current_system(),
        )


    @classmethod
    def create_from_flat_dict(cls, data: Dict[str, int | str | datetime | uuid.UUID]) -> "SystemIdentification":
        return cls(
            hardware=SystemHardware(
                architecture=str(data["architecture"]),
                processor=str(data["processor"]),
                machine=str(data["machine"]),
            ),
            network=NetworkIdentity(
                hostname=str(data["hostname"]),
                ip_address=str(data["ip_address"]),
            ),
            runtime=RuntimeEnvironment(
                python_version=str(data["python_version"]),
                platform=str(data["platform"]),
                working_directory=str(data["working_directory"]),
                username=str(data["username"]) if data.get("username") is not None else None,
                system_timezone=str(data["system_timezone"]),
                start_time=data["start_time"] if isinstance(data["start_time"], datetime) else datetime.fromisoformat(str(data["start_time"])),
            ),
            process=ProcessIdentity(pid=int(str(data["pid"]))),
            fingerprint=SystemFingerprint(value=str(data["fingerprint"])),
        )

def get_system_identifier() -> SystemIdentification:
    """
    Collects system information to uniquely identify the process.
    Returns a SystemIdentification object.
    """
    try:
        return SystemIdentification.from_current_system()
    except Exception:
        return SystemIdentification(
            hardware=SystemHardware(architecture="unknown", processor="unknown", machine="unknown"),
            network=NetworkIdentity(hostname="unknown", ip_address="unknown"),
            runtime=RuntimeEnvironment(
                python_version=sys.version.split()[0],
                platform="unknown",
                working_directory=os.getcwd(),
                username=None,
                system_timezone="unknown",
            ),
            process=ProcessIdentity.from_current_process(),
            fingerprint=SystemFingerprint(value="unknown"),
        )


class SystemInfoSerializer:
    class JSONEncoder(json.JSONEncoder):
        def default(self, obj: Any) -> Any:
            if is_dataclass(obj):
                return asdict(obj)  # type: ignore[arg-type]
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, uuid.UUID):
                return str(obj)
            return super().default(obj)

    @staticmethod
    def serialize(system_info: "SystemIdentification", pretty: bool = False) -> str:
        indent = 2 if pretty else None
        return json.dumps(
            system_info, cls=SystemInfoSerializer.JSONEncoder, indent=indent
        )

    @staticmethod
    def to_dict(system_info: "SystemIdentification") -> Dict[str, Any]:
        result = json.loads(SystemInfoSerializer.serialize(system_info))
        if isinstance(result, dict):
            return result
        else:
            raise ValueError("Failed to serialize SystemIdentification object") 


if __name__ == "__main__":
    system_info = get_system_identifier()
    print(f"Hardware: {system_info.hardware}")
    print(f"Network: {system_info.network}")
    print(f"Runtime: {system_info.runtime}")
    print(f"Process: {system_info.process}")
    print(f"Fingerprint: {system_info.fingerprint}")

    json_str = SystemInfoSerializer.serialize(system_info, pretty=True)
    print("JSON representation:")
    print(json_str)

    data_dict = SystemInfoSerializer.to_dict(system_info)
    print("\nDictionary representation:")
    print(data_dict)
