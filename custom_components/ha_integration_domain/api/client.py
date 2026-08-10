"""
API Client for ha_integration_domain.

This module provides the API client for communicating with external services.
It demonstrates proper error handling, authentication patterns, and async operations.

For more information on creating API clients:
https://developers.home-assistant.io/docs/api_lib_index
"""

import asyncio
import socket
from typing import Any

import aiohttp


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

    Raises appropriate exceptions for authentication and HTTP errors.

    Args:
        response: The aiohttp ClientResponse to verify.

    Raises:
        IntegrationBlueprintApiClientAuthenticationError: For 401/403 errors.
        aiohttp.ClientResponseError: For other HTTP errors.

    """
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise IntegrationBlueprintApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class IntegrationBlueprintApiClient:
    """
    API Client for Smart Air Purifier integration.

    This client demonstrates authentication and API communication patterns
    for Home Assistant integrations. It handles HTTP requests, error handling,
    and credential management.

    The username and password are stored and would be used for:
    - HTTP Basic Auth headers
    - OAuth token exchange
    - API key generation
    - Session token management

    Note: JSONPlaceholder is used as a demo endpoint and doesn't require auth.
    In production, replace with your actual API endpoint that validates credentials.

    For more information on API clients:
    https://developers.home-assistant.io/docs/api_lib_index

    Attributes:
        _username: The username for API authentication.
        _password: The password for API authentication.
        _session: The aiohttp ClientSession for making requests.

    """

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """
        Initialize the API Client with credentials.

        Args:
            username: The username for authentication from config flow.
            password: The password for authentication from config flow.
            session: The aiohttp ClientSession to use for requests.

        """
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> Any:
        """
        Get data from the API.

        This method fetches the current state and sensor data from the device.
        It demonstrates where credentials would be used in production:
        - Authorization headers (Basic Auth, Bearer Token)
        - Query parameters (username, api_key)
        - Session cookies (after login)

        Returns:
            A dictionary containing the device data.

        Raises:
            IntegrationBlueprintApiClientAuthenticationError: If authentication fails.
            IntegrationBlueprintApiClientCommunicationError: If communication fails.
            IntegrationBlueprintApiClientError: For other API errors.

        """
        # In production: Use username/password for authentication
        # Example patterns:
        # 1. Basic Auth: auth=aiohttp.BasicAuth(self._username, self._password)
        # 2. Token: headers={"Authorization": f"Bearer {self._get_token()}"}
        # 3. API Key: params={"username": self._username, "key": self._password}

        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
            # For demo purposes with JSONPlaceholder (no auth required)
            # In production, add authentication here
        )

    async def async_set_fan_speed(self, speed: str) -> Any:
        """
        Set the fan speed on the device.

        Args:
            speed: The fan speed to set (low, medium, high, auto).

        Returns:
            A dictionary containing the API response.

        Raises:
            IntegrationBlueprintApiClientAuthenticationError: If authentication fails.
            IntegrationBlueprintApiClientCommunicationError: If communication fails.
            IntegrationBlueprintApiClientError: For other API errors.

        """
        # In production: Send authenticated request to change fan speed
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"fan_speed": speed, "user": self._username},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def async_set_target_humidity(self, humidity: int) -> Any:
        """
        Set the target humidity on the device.

        Args:
            humidity: The target humidity percentage (30-80).

        Returns:
            A dictionary containing the API response.

        Raises:
            IntegrationBlueprintApiClientAuthenticationError: If authentication fails.
            IntegrationBlueprintApiClientCommunicationError: If communication fails.
            IntegrationBlueprintApiClientError: For other API errors.

        """
        # In production: Send authenticated request to change humidity setting
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"target_humidity": humidity, "user": self._username},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """
        Wrapper for API requests with error handling.

        This method handles all HTTP requests and translates exceptions
        into integration-specific exceptions.

        Args:
            method: The HTTP method (get, post, patch, etc.).
            url: The URL to request.
            data: Optional data to send in the request body.
            headers: Optional headers to include in the request.

        Returns:
            The JSON response from the API.

        Raises:
            IntegrationBlueprintApiClientAuthenticationError: If authentication fails.
            IntegrationBlueprintApiClientCommunicationError: If communication fails.
            IntegrationBlueprintApiClientError: For other API errors.

        """
        try:
            async with asyncio.timeout(10):
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
            raise IntegrationBlueprintApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:
            msg = f"Something really wrong happened! - {exception}"
            raise IntegrationBlueprintApiClientError(
                msg,
            ) from exception
