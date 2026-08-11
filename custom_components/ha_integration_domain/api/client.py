"""API client for ha_integration_domain."""

import asyncio
import socket
from typing import Any

import aiohttp

API_URL = "https://jsonplaceholder.typicode.com/posts/1"
REQUEST_TIMEOUT = 10

FAN_SPEEDS = ("low", "medium", "high", "auto")
SPEED_PERCENTAGES = {"low": 33, "medium": 66, "high": 100, "auto": 66}


class IntegrationBlueprintApiClientError(Exception):
    """Base exception to indicate a general API error."""


class IntegrationBlueprintApiClientCommunicationError(
    IntegrationBlueprintApiClientError,
):
    """Exception to indicate a communication error with the API."""


class IntegrationBlueprintApiClientAuthenticationError(
    IntegrationBlueprintApiClientError,
):
    """Exception to indicate an authentication error with the API."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """
    Verify that the API response is valid.

    Raises:
        IntegrationBlueprintApiClientAuthenticationError: For 401 and 403 responses.
        aiohttp.ClientResponseError: For every other unsuccessful status.

    """
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise IntegrationBlueprintApiClientAuthenticationError(msg)
    response.raise_for_status()


class IntegrationBlueprintApiClient:
    """
    Stand-in for the client of a real device or service.

    JSONPlaceholder is queried so that a real request happens on every poll, and its
    response is turned into a device-shaped payload. The writable values are kept in
    memory because the demo endpoint stores nothing; a real client sends them to the
    device and reads them back on the next poll.
    """

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._username = username
        self._password = password
        self._session = session
        self._settings: dict[str, Any] = {
            "fan_on": True,
            "fan_speed": "auto",
            "child_lock": False,
            "led_display": True,
            "target_humidity": 50.0,
        }
        self._filter_reset_offset = 0

    async def async_get_data(self) -> dict[str, Any]:
        """
        Fetch the current device state.

        Returns:
            The device state, keyed the way entities read it.

        """
        response = await self._api_wrapper(method="get", url=API_URL)
        return self._build_payload(response)

    async def async_set_fan_speed(self, speed: str) -> None:
        """Set the fan speed."""
        await self._api_wrapper(
            method="patch",
            url=API_URL,
            data={"fan_speed": speed},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )
        self._settings["fan_speed"] = speed
        self._settings["fan_on"] = True

    async def async_set_fan_state(self, *, is_on: bool) -> None:
        """Turn the fan on or off."""
        await self._api_wrapper(
            method="patch",
            url=API_URL,
            data={"fan_on": is_on},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )
        self._settings["fan_on"] = is_on

    async def async_set_target_humidity(self, humidity: float) -> None:
        """Set the target humidity."""
        await self._api_wrapper(
            method="patch",
            url=API_URL,
            data={"target_humidity": humidity},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )
        self._settings["target_humidity"] = humidity

    async def async_set_toggle(self, key: str, *, enabled: bool) -> None:
        """Set one of the device's boolean settings."""
        await self._api_wrapper(
            method="patch",
            url=API_URL,
            data={key: enabled},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )
        self._settings[key] = enabled

    async def async_reset_filter(self) -> None:
        """Reset the filter timer."""
        await self._api_wrapper(
            method="post",
            url=API_URL,
            data={"command": "reset_filter"},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )
        self._filter_reset_offset = 0

    def _build_payload(self, response: dict[str, Any]) -> dict[str, Any]:
        """Derive a device-shaped payload from the demo endpoint's response."""
        seed = int(response.get("userId", 1)) * 47 + int(response.get("id", 1)) * 13
        fan_speed = str(self._settings["fan_speed"])
        filter_life = max(0, 100 - (seed % 100) - self._filter_reset_offset)

        return {
            "model": "Blueprint Air Purifier",
            "serial_number": f"BP-{seed:06d}",
            "sw_version": "1.4.2",
            "air_quality_index": seed % 501,
            "pm25": round((seed * 0.37) % 300, 1),
            "filter_life": filter_life,
            "filter_replacement": filter_life < 10,
            "runtime": (seed * 12) % 10000,
            "fan_on": self._settings["fan_on"],
            "fan_speed": fan_speed,
            "fan_percentage": SPEED_PERCENTAGES[fan_speed] if self._settings["fan_on"] else 0,
            "child_lock": self._settings["child_lock"],
            "led_display": self._settings["led_display"],
            "target_humidity": self._settings["target_humidity"],
        }

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Perform a request and translate transport errors into client exceptions.

        Returns:
            The decoded JSON response.

        Raises:
            IntegrationBlueprintApiClientAuthenticationError: If the credentials are rejected.
            IntegrationBlueprintApiClientCommunicationError: If the request does not complete.
            IntegrationBlueprintApiClientError: For any other failure.

        """
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(msg) from exception
        except IntegrationBlueprintApiClientError:
            raise
        except Exception as exception:
            msg = f"Unexpected error talking to the API - {exception}"
            raise IntegrationBlueprintApiClientError(msg) from exception
