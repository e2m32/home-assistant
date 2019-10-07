"""
Support for MQTT lights.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.mqtt/
"""
import logging

import voluptuous as vol

from homeassistant.components import light
from homeassistant.components.mqtt import ATTR_DISCOVERY_HASH
from homeassistant.components.mqtt.discovery import (
    MQTT_DISCOVERY_NEW,
    clear_discovery_hash,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from . import schema_basic, schema_json, schema_template

_LOGGER = logging.getLogger(__name__)

CONF_SCHEMA = "schema"


def validate_mqtt_light(value):
    """Validate MQTT light schema."""

    schemas = {
        "basic": schema_basic.PLATFORM_SCHEMA_BASIC,
        "json": schema_json.PLATFORM_SCHEMA_JSON,
        "template": schema_template.PLATFORM_SCHEMA_TEMPLATE,
    }
    return schemas[value[CONF_SCHEMA]](value)


MQTT_LIGHT_SCHEMA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SCHEMA, default="basic"): vol.All(
            vol.Lower, vol.Any("basic", "json", "template")
        )
    }
)

PLATFORM_SCHEMA = vol.All(
    MQTT_LIGHT_SCHEMA_SCHEMA.extend({}, extra=vol.ALLOW_EXTRA), validate_mqtt_light
)


async def async_setup_platform(
    hass: HomeAssistantType, config: ConfigType, async_add_entities, discovery_info=None
):
    """Set up MQTT light through configuration.yaml."""
    await _async_setup_entity(config, async_add_entities)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up MQTT light dynamically through MQTT discovery."""

    async def async_discover(discovery_payload):
        """Discover and add a MQTT light."""
        try:
            discovery_hash = discovery_payload.pop(ATTR_DISCOVERY_HASH)
            config = PLATFORM_SCHEMA(discovery_payload)
            await _async_setup_entity(
                config, async_add_entities, config_entry, discovery_hash
            )
        except Exception:
            if discovery_hash:
                clear_discovery_hash(hass, discovery_hash)
            raise

    async_dispatcher_connect(
        hass, MQTT_DISCOVERY_NEW.format(light.DOMAIN, "mqtt"), async_discover
    )


async def _async_setup_entity(
    config, async_add_entities, config_entry=None, discovery_hash=None
):
    """Set up a MQTT Light."""

    setup_entity = {
        "basic": schema_basic.async_setup_entity_basic,
        "json": schema_json.async_setup_entity_json,
        "template": schema_template.async_setup_entity_template,
    }
    await setup_entity[config[CONF_SCHEMA]](
        config, async_add_entities, config_entry, discovery_hash
    )
