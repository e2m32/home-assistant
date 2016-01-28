"""
homeassistant.components.insteon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Support for Insteon Hub.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/insteon/
"""
import logging
import homeassistant.bootstrap as bootstrap
from homeassistant.helpers import validate_config
from homeassistant.loader import get_component
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, CONF_API_KEY, ATTR_DISCOVERED,
    ATTR_SERVICE, EVENT_PLATFORM_DISCOVERED)

DOMAIN = "insteon"
REQUIREMENTS = ['insteon_hub==0.4.5']
INSTEON = None
DISCOVER_LIGHTS = "insteon.lights"
_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """
    Setup Insteon Hub component.
    This will automatically import associated lights.
    """
    if not validate_config(
            config,
            {DOMAIN: [CONF_USERNAME, CONF_PASSWORD]},
            _LOGGER):
        return False

    import insteon
    if config[DOMAIN].get(CONF_USERNAME) is None:
        _LOGGER.error("No Insteon username found in config.")
        return
    username = config[DOMAIN][CONF_USERNAME]

    if config[DOMAIN].get(CONF_PASSWORD) is None:
        _LOGGER.error("No Insteon password found in config.")
        return
    password = config[DOMAIN][CONF_PASSWORD]

    if config[DOMAIN].get(CONF_API_KEY) is None:
        _LOGGER.error("No Insteon api_key found in config.")
        return
    api_key = config[DOMAIN][CONF_API_KEY]

    global INSTEON
    INSTEON = insteon.Insteon(username, password, api_key)

    comp_name = 'light'
    discovery = DISCOVER_LIGHTS
    component = get_component(comp_name)
    bootstrap.setup_component(hass, component.DOMAIN, config)
    hass.bus.fire(
        EVENT_PLATFORM_DISCOVERED,
        {ATTR_SERVICE: discovery, ATTR_DISCOVERED: {}})
    return True


class InsteonToggleDevice(ToggleEntity):
    """ Abstract Class for an Insteon node. """

    def __init__(self, node):
        self.node = node
        self._value = 0

    @property
    def name(self):
        """ Returns the name of the node. """
        return self.node.DeviceName

    @property
    def unique_id(self):
        """ Returns the id of this insteon node. """
        return self.node.DeviceID

    def update(self):
        """ Update state of the sensor. """
        resp = self.node.send_command('get_status', wait=True)
        try:
            self._value = resp['response']['level']
        except KeyError:
            pass

    @property
    def is_on(self):
        """ Returns boolean response if the node is on. """
        return self._value != 0

    def turn_on(self, **kwargs):
        self.node.send_command('on')

    def turn_off(self, **kwargs):
        self.node.send_command('off')
