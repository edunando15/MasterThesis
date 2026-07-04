from abc import ABC, abstractmethod
from typing import Any, Optional
from .type import Type

"""
An Adapter invokes an IoT platform's APIs to deploy entities.
"""
class IAdapter(ABC):
    def __init__(self, platform_url):
        if not platform_url:
            raise ValueError("Platform url is required")

        self.platform_url = platform_url.rstrip("/")
        self.token: Optional[str] = None

    @abstractmethod
    def authenticate(self, user: str, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def add_zone(self, zone: Any, parent: Any = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def add_device(self, device: Any, description: str = None, has_id: str = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def add_relationship(self, parent: str, parent_type: Type, child: str, child_type: Type) -> bool:
        raise NotImplementedError

    @abstractmethod
    def upload_telemetry(self, device_id: str, telemetry: dict) -> bool:
        raise NotImplementedError