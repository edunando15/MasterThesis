from .type import Type
import requests
from .adapter import IAdapter
from typing import Any


class OpenRemoteAdapter(IAdapter):
    def __init__(self, platform_url: str):
        super().__init__(platform_url)
        self.token = ""
        self.realm = ""

    def authenticate(self, user: str, password: str) -> str:
        url = f"{self.platform_url}/auth/realms/master/protocol/openid-connect/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {"grant_type": "password", "client_id": "openremote", "username": user, "password": password}
        response = requests.post(url, data=payload, headers=headers, verify=False)
        response.raise_for_status()
        self.token = response.json().get("access_token")
        return self.token

    def set_realm(self, realm: str) -> None:
        self.realm = realm

    def _headers(self):
        if not self.token:
            raise RuntimeError("Call authenticate() first")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _api_base(self) -> str:
        if not self.realm:
            raise RuntimeError("Call set_realm() first")
        return f"{self.platform_url}/api/{self.realm}"

    def add_device(self, device: Any, **kwargs: Any) -> str:
        payload = {
            "name": getattr(device, "name", str(device)),
            "type": Type.DEVICE.value,
            "attributes": {},
        }
        if parent := kwargs.get("parent"):
            payload["parentId"] = parent
        desc = ""
        if kwargs.get("has_id") is not None:
            desc = f"original_id: {kwargs.get('has_id')}"

        payload["attributes"]["notes"] = {
            "value": desc
        }
        device_attrs = kwargs.get("attributes") or []
        for attr_name in device_attrs:
            payload["attributes"][attr_name] = {
                "type": "number",
                "meta": {
                    "storeDataPoints": True,
                    "readOnly": False,
                }
            }
        response = requests.post(
            f"{self._api_base()}/asset",
            json=payload,
            headers=self._headers(),
            verify=False,
        )
        if response.status_code in (200, 201):
            return str(response.json().get("id", ""))
        return ""

    def add_relationship(self, parent: str, parent_type: Type, child: str, child_type: Type) -> bool:
        payload = {
            "id": child,
            "realm": self.realm,
            "parentId": parent,
        }
        response = requests.put(
            f"{self._api_base()}/asset/{child}",
            json=payload,
            headers=self._headers(),
            verify=False,
        )
        return response.status_code in (200, 201)

    def upload_telemetry(self, device_id: str, telemetry: dict) -> bool:
        success = True
        asset_resp = requests.get(
            f"{self._api_base()}/asset/{device_id}",
            headers=self._headers(),
            verify=False
        )
        actual_attributes = asset_resp.json().get("attributes", {})
        attr_map = {k.lower(): k for k in actual_attributes.keys()}
        for attr_name, value in telemetry.items():
            target_attr = attr_map.get(attr_name.lower())
            if not target_attr:
                print(f"Warning: Attribute {attr_name} not found on device {device_id}. Skipping.")
                continue
            response = requests.put(
                f"{self._api_base()}/asset/{device_id}/attribute/{target_attr}",
                json=value,
                headers=self._headers(),
                verify=False,
            )
            if response.status_code not in (200, 201, 204):
                success = False
        return success

    def add_zone(self, zone: Any, **kwargs: Any) -> str:
        payload = {
            "name": getattr(zone, "name", str(zone)),
            "type": kwargs.get("has_type", ""),
        }
        if kwargs.get("parent") is not None:
            payload["parentId"] = kwargs.get("parent")

        response = requests.post(
            f"{self._api_base()}/asset",
            json=payload,
            headers=self._headers(),
            verify=False,
        )
        if response.status_code in (200, 201):
            return str(response.json().get("id", ""))
        return ""

    def delete_asset(self, asset_id):
        url = f"{self.platform_url}/api/{self.realm}/asset"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        params = {"assetId": asset_id}

        response = requests.delete(url, headers=headers, params=params, verify=False)
        if response.status_code in (200, 204):
            print(f"Deleted: {asset_id}")
        else:
            print(f"Failed ({response.status_code}): {asset_id}")