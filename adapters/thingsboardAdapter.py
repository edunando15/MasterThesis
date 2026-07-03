from .type import Type
import requests
from .adapter import IAdapter
from typing import Any

class ThingsboardAdapter(IAdapter):
    def __init__(self, platform_url: str):
        super().__init__(platform_url)
        self.token = ""

    def authenticate(self, user: str, password: str) -> str:
        response = requests.post(
            f"{self.platform_url}/api/auth/login",
            json={"username": user, "password": password},
        )
        response.raise_for_status()
        self.token = response.json().get("token")
        return self.token

    def _headers(self):
        if not self.token:
            raise RuntimeError("Call authenticate() first")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def add_zone(self, zone: Any, parent: Any = None) -> str:
        payload = {
            "name": getattr(zone, "name", str(zone)),
            "type": Type.ASSET.value,
        }
        if parent is not None:
            payload["parentId"] = parent

        response = requests.post(
            f"{self.platform_url}/api/asset",
            json=payload,
            headers=self._headers(),
        )
        if response.status_code in (200, 201):
            return str(response.json().get("id", {}).get("id", ""))
        return ""

    def add_device(self, device: Any, description: str = None) -> str:
        payload = {
            "name": getattr(device, "name", str(device)),
            "type": Type.DEVICE.value,
        }
        if description is not None:
            payload["additionalInfo"] = {
                "description": description
            }

        response = requests.post(
            f"{self.platform_url}/api/device",
            json=payload,
            headers=self._headers(),
        )
        if response.status_code in (200, 201):
            return str(response.json().get("id", {}).get("id", ""))
        return ""

    def add_relationship(self, parent: str, parent_type: Type, child: str, child_type: Type) -> bool:
        payload = {
            "from": {
                "id": parent,
                "entityType": parent_type.value,
            },
            "to": {
                "id": child,
                "entityType": child_type.value,
            },
            "type": Type.CONTAINS.value,
            "typeGroup": "COMMON",
        }

        response = requests.post(
            f"{self.platform_url}/api/relation",
            json=payload,
            headers=self._headers(),
        )

        return response.status_code in (200, 201)