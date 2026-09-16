"""Read-only Packet Tracer Network Controller northbound adapter."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

class ControllerError(Exception):
    pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class PacketTracerController:
    def __init__(self, url, username, password, timeout=1.5, cache_seconds=5):
        parsed = urlsplit(url)
        if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"} or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path.rstrip("/") not in {"", "/api/v1"}:
            raise ValueError("PT_CONTROLLER_URL must be a localhost HTTP URL, optionally ending in /api/v1")
        self.url = url.rstrip("/")
        if not self.url.endswith("/api/v1"):
            self.url += "/api/v1"
        self.username, self.password = username, password
        self.timeout, self.cache_seconds = timeout, cache_seconds
        self.token = None
        self.cached = None
        self.next_poll = 0
        self.lock = threading.Lock()
        self.http = build_opener(ProxyHandler({}), NoRedirect())

    def _request(self, path, payload=None):
        headers = {"Content-Type": "application/json"}
        if self.token and payload is None:
            headers["X-Auth-Token"] = self.token
        request = Request(self.url + path, headers=headers,
                          data=None if payload is None else json.dumps(payload).encode())
        with self.http.open(request, timeout=self.timeout) as response:
            data = json.load(response)
        if not isinstance(data, dict) or "response" not in data:
            raise ControllerError("INVALID_RESPONSE")
        return data["response"]

    def _login(self):
        if not self.username or not self.password:
            raise ControllerError("MISSING_CREDENTIALS")
        response = self._request("/ticket", {"username": self.username, "password": self.password})
        token = response.get("serviceTicket") if isinstance(response, dict) else None
        if not isinstance(token, str) or not token:
            raise ControllerError("INVALID_AUTH_RESPONSE")
        self.token = token

    def _get(self, path):
        if not self.token:
            self._login()
        try:
            return self._request(path)
        except HTTPError as error:
            if error.code != 401:
                raise
            self.token = None
            self._login()
            return self._request(path)

    def snapshot(self):
        with self.lock:
            if self.cached is not None and time.monotonic() < self.next_poll:
                return deepcopy(self.cached)
            result = {"configured": True, "source": "PT_CONTROLLER", "url": self.url,
                      "status": "UNAVAILABLE", "devices": [], "topology": None,
                      "observed_at": None, "error": None, "topology_error": None,
                      "polled_at": datetime.now(timezone.utc).isoformat()}
            try:
                devices = self._get("/network-device")
                if not isinstance(devices, list) or any(not isinstance(device, dict) for device in devices):
                    raise ControllerError("INVALID_INVENTORY_RESPONSE")
                # Return only inventory fields needed by the UI; never device credentials.
                result["devices"] = [{key: device[key] for key in
                    ("id", "hostname", "name", "managementIpAddress", "ipAddress", "type", "deviceType", "family", "reachabilityStatus", "collectionStatus") if key in device} for device in devices]
                result["status"] = "CONNECTED"
                result["observed_at"] = datetime.now(timezone.utc).isoformat()
                try:
                    topology = self._get("/topology/physical-topology")
                    if not isinstance(topology, dict):
                        raise ControllerError("INVALID_TOPOLOGY_RESPONSE")
                    result["topology"] = {key: topology[key] for key in ("nodes", "links") if key in topology}
                except (HTTPError, URLError, TimeoutError, ValueError, ControllerError):
                    result["topology_error"] = "TOPOLOGY_UNAVAILABLE"
            except HTTPError as error:
                result["error"] = "AUTH_FAILED" if error.code in (401, 403) else f"HTTP_{error.code}"
                self.token = None
            except (URLError, TimeoutError, OSError):
                result["error"] = "CONNECTION_FAILED"
                self.token = None
            except (ValueError, ControllerError) as error:
                result["error"] = str(error) if isinstance(error, ControllerError) else "INVALID_JSON"
                self.token = None
            self.cached = result
            self.next_poll = time.monotonic() + self.cache_seconds
            return deepcopy(result)


def controller_from_environment():
    url = os.getenv("PT_CONTROLLER_URL", "")
    if not url:
        return None
    return PacketTracerController(url, os.getenv("PT_CONTROLLER_USERNAME", ""), os.getenv("PT_CONTROLLER_PASSWORD", ""))
