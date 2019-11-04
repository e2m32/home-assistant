"""Tests for the WLED switch platform."""
import aiohttp

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.wled.const import (
    ATTR_DURATION,
    ATTR_TARGET_BRIGHTNESS,
    ATTR_UDP_PORT,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_ICON,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant

from tests.components.wled import init_integration
from tests.test_util.aiohttp import AiohttpClientMocker


async def test_switch_state(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test the creation and values of the WLED switches."""
    await init_integration(hass, aioclient_mock)
    await hass.async_block_till_done()

    entity_registry = await hass.helpers.entity_registry.async_get_registry()

    state = hass.states.get("switch.wled_light_nightlight")
    assert state
    assert state.attributes.get(ATTR_DURATION) == 60
    assert state.attributes.get(ATTR_ICON) == "mdi:weather-night"
    assert state.attributes.get(ATTR_TARGET_BRIGHTNESS) == 0
    assert state.state == STATE_OFF

    entry = entity_registry.async_get("switch.wled_light_nightlight")
    assert entry
    assert entry.unique_id == "wled_aabbccddeeff_switch_nightlight"

    state = hass.states.get("switch.wled_light_sync_send")
    assert state
    assert state.attributes.get(ATTR_ICON) == "mdi:upload-network-outline"
    assert state.attributes.get(ATTR_UDP_PORT) == 21324
    assert state.state == STATE_OFF

    entry = entity_registry.async_get("switch.wled_light_sync_send")
    assert entry
    assert entry.unique_id == "wled_aabbccddeeff_switch_sync_send"

    state = hass.states.get("switch.wled_light_sync_receive")
    assert state
    assert state.attributes.get(ATTR_ICON) == "mdi:download-network-outline"
    assert state.attributes.get(ATTR_UDP_PORT) == 21324
    assert state.state == STATE_ON

    entry = entity_registry.async_get("switch.wled_light_sync_receive")
    assert entry
    assert entry.unique_id == "wled_aabbccddeeff_switch_sync_receive"


async def test_switch_change_state(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test the change of state of the WLED switches."""
    await init_integration(hass, aioclient_mock)
    await hass.async_block_till_done()

    # Nightlight
    state = hass.states.get("switch.wled_light_nightlight")
    assert state.state == STATE_OFF

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "switch.wled_light_nightlight"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("switch.wled_light_nightlight")
    assert state.state == STATE_ON

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "switch.wled_light_nightlight"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("switch.wled_light_nightlight")
    assert state.state == STATE_OFF

    # Sync send
    state = hass.states.get("switch.wled_light_sync_send")
    assert state.state == STATE_OFF

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "switch.wled_light_sync_send"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("switch.wled_light_sync_send")
    assert state.state == STATE_ON

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "switch.wled_light_sync_send"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("switch.wled_light_sync_send")
    assert state.state == STATE_OFF

    # Sync receive
    state = hass.states.get("switch.wled_light_sync_receive")
    assert state.state == STATE_ON

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "switch.wled_light_sync_receive"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("switch.wled_light_sync_receive")
    assert state.state == STATE_OFF

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "switch.wled_light_sync_receive"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("switch.wled_light_sync_receive")
    assert state.state == STATE_ON


async def test_switch_error(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test error handling of the WLED switches."""
    aioclient_mock.post("http://example.local:80/json/state", exc=aiohttp.ClientError)
    await init_integration(hass, aioclient_mock)
    await hass.async_block_till_done()

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "switch.wled_light_nightlight"},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get("switch.wled_light_nightlight")
    assert state.state == STATE_UNAVAILABLE

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "switch.wled_light_sync_send"},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get("switch.wled_light_sync_send")
    assert state.state == STATE_UNAVAILABLE

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "switch.wled_light_sync_receive"},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = hass.states.get("switch.wled_light_sync_receive")
    assert state.state == STATE_UNAVAILABLE
