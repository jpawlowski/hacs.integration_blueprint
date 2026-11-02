"""Tests for how the integration handles a rate limit."""

from datetime import timedelta

from freezegun.api import FrozenDateTimeFactory
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.ha_integration_domain.api.client import API_URL, DEFAULT_RETRY_AFTER
from custom_components.ha_integration_domain.coordinator.base import MIN_RETRY_AFTER, UPDATE_INTERVAL
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant

ENTITY_ID = "sensor.demo_filter_life_remaining"
DEMO_RESPONSE = {"userId": 1, "id": 1}


async def _tick(hass: HomeAssistant, freezer: FrozenDateTimeFactory, delta: timedelta) -> None:
    freezer.tick(delta)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


@pytest.mark.parametrize(
    ("headers", "wait"),
    [
        ({"Retry-After": "120"}, 120),
        ({}, DEFAULT_RETRY_AFTER),
        ({"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}, DEFAULT_RETRY_AFTER),
        ({"Retry-After": "0"}, MIN_RETRY_AFTER),
        ({"Retry-After": "99999999"}, UPDATE_INTERVAL.total_seconds()),
    ],
)
async def test_rate_limit_delays_the_next_refresh(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    aioclient_mock: AiohttpClientMocker,
    freezer: FrozenDateTimeFactory,
    headers: dict[str, str],
    wait: float,
) -> None:
    """After a 429 the next poll waits as long as the API asked, within ten seconds and the usual hour."""
    aioclient_mock.get(API_URL, json=DEMO_RESPONSE)
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    aioclient_mock.clear_requests()
    aioclient_mock.get(API_URL, status=429, headers=headers)
    await _tick(hass, freezer, UPDATE_INTERVAL)
    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE

    aioclient_mock.clear_requests()
    aioclient_mock.get(API_URL, json=DEMO_RESPONSE)
    await _tick(hass, freezer, timedelta(seconds=wait - 10))
    assert aioclient_mock.call_count == 0

    await _tick(hass, freezer, timedelta(seconds=11))
    assert aioclient_mock.call_count == 1
    assert hass.states.get(ENTITY_ID).state != STATE_UNAVAILABLE
