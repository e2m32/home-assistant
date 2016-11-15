"""
Support for interfacing with the XBMC/Kodi JSON-RPC API.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.kodi/
"""
import logging
import urllib

import voluptuous as vol

from homeassistant.components.media_player import (
    SUPPORT_NEXT_TRACK, SUPPORT_PAUSE, SUPPORT_PREVIOUS_TRACK, SUPPORT_SEEK,
    SUPPORT_PLAY_MEDIA, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_STOP,
    SUPPORT_TURN_OFF, MediaPlayerDevice, PLATFORM_SCHEMA)
from homeassistant.const import (
    STATE_IDLE, STATE_OFF, STATE_PAUSED, STATE_PLAYING, CONF_HOST, CONF_NAME,
    CONF_PORT, CONF_USERNAME, CONF_PASSWORD)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['jsonrpc-requests==0.3']

_LOGGER = logging.getLogger(__name__)

CONF_TURN_OFF_ACTION = 'turn_off_action'

DEFAULT_NAME = 'Kodi'
DEFAULT_PORT = 8080

TURN_OFF_ACTION = [None, 'quit', 'hibernate', 'suspend', 'reboot', 'shutdown']

SUPPORT_KODI = SUPPORT_PAUSE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
    SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | SUPPORT_SEEK | \
    SUPPORT_PLAY_MEDIA | SUPPORT_STOP

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_TURN_OFF_ACTION, default=None): vol.In(TURN_OFF_ACTION),
    vol.Optional(CONF_USERNAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Kodi platform."""
    url = '{}:{}'.format(config.get(CONF_HOST), config.get(CONF_PORT))

    jsonrpc_url = config.get('url')  # deprecated
    if jsonrpc_url:
        url = jsonrpc_url.rstrip('/jsonrpc')

    add_devices([
        KodiDevice(
            config.get(CONF_NAME),
            url,
            auth=(config.get(CONF_USERNAME), config.get(CONF_PASSWORD)),
            turn_off_action=config.get(CONF_TURN_OFF_ACTION)),
    ])


class KodiDevice(MediaPlayerDevice):
    """Representation of a XBMC/Kodi device."""

    def __init__(self, name, url, auth=None, turn_off_action=None):
        """Initialize the Kodi device."""
        import jsonrpc_requests
        self._name = name
        self._url = url
        self._server = jsonrpc_requests.Server(
            '{}/jsonrpc'.format(self._url),
            auth=auth,
            timeout=5)
        self._turn_off_action = turn_off_action
        self._players = list()
        self._properties = None
        self._item = None
        self._app_properties = None
        self.update()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    def _get_players(self):
        """Return the active player objects or None."""
        import jsonrpc_requests
        try:
            return self._server.Player.GetActivePlayers()
        except jsonrpc_requests.jsonrpc.TransportError:
            if self._players is not None:
                _LOGGER.warning('Unable to fetch kodi data')
                _LOGGER.debug('Unable to fetch kodi data', exc_info=True)
            return None

    @property
    def state(self):
        """Return the state of the device."""
        if self._players is None:
            return STATE_OFF

        if len(self._players) == 0:
            return STATE_IDLE

        if self._properties['speed'] == 0 and not self._properties['live']:
            return STATE_PAUSED
        else:
            return STATE_PLAYING

    def update(self):
        """Retrieve latest state."""
        self._players = self._get_players()

        if self._players is not None and len(self._players) > 0:
            player_id = self._players[0]['playerid']

            assert isinstance(player_id, int)

            self._properties = self._server.Player.GetProperties(
                player_id,
                ['time', 'totaltime', 'speed', 'live']
            )

            self._item = self._server.Player.GetItem(
                player_id,
                ['title', 'file', 'uniqueid', 'thumbnail', 'artist']
            )['item']

            self._app_properties = self._server.Application.GetProperties(
                ['volume', 'muted']
            )
        else:
            self._properties = None
            self._item = None
            self._app_properties = None

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        if self._app_properties is not None:
            return self._app_properties['volume'] / 100.0

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        if self._app_properties is not None:
            return self._app_properties['muted']

    @property
    def media_content_id(self):
        """Content ID of current playing media."""
        if self._item is not None:
            return self._item.get('uniqueid', None)

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        if self._players is not None and len(self._players) > 0:
            return self._players[0]['type']

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        if self._properties is not None and not self._properties['live']:
            total_time = self._properties['totaltime']

            return (
                total_time['hours'] * 3600 +
                total_time['minutes'] * 60 +
                total_time['seconds'])

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        if self._item is not None:
            return self._get_image_url()

    def _get_image_url(self):
        """Helper function that parses the thumbnail URLs used by Kodi."""
        url_components = urllib.parse.urlparse(self._item['thumbnail'])

        if url_components.scheme == 'image':
            return '{}/image/{}'.format(
                self._url,
                urllib.parse.quote_plus(self._item['thumbnail']))

    @property
    def media_title(self):
        """Title of current playing media."""
        # find a string we can use as a title
        if self._item is not None:
            return self._item.get(
                'title',
                self._item.get('label', self._item.get('file', 'unknown')))

    @property
    def supported_media_commands(self):
        """Flag of media commands that are supported."""
        supported_media_commands = SUPPORT_KODI

        if self._turn_off_action in TURN_OFF_ACTION:
            supported_media_commands |= SUPPORT_TURN_OFF

        return supported_media_commands

    def turn_off(self):
        """Execute turn_off_action to turn off media player."""
        if self._turn_off_action == 'quit':
            self._server.Application.Quit()
        elif self._turn_off_action == 'hibernate':
            self._server.System.Hibernate()
        elif self._turn_off_action == 'suspend':
            self._server.System.Suspend()
        elif self._turn_off_action == 'reboot':
            self._server.System.Reboot()
        elif self._turn_off_action == 'shutdown':
            self._server.System.Shutdown()
        else:
            _LOGGER.warning('turn_off requested but turn_off_action is none')

        self.update_ha_state()

    def volume_up(self):
        """Volume up the media player."""
        assert self._server.Input.ExecuteAction('volumeup') == 'OK'
        self.update_ha_state()

    def volume_down(self):
        """Volume down the media player."""
        assert self._server.Input.ExecuteAction('volumedown') == 'OK'
        self.update_ha_state()

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        self._server.Application.SetVolume(int(volume * 100))
        self.update_ha_state()

    def mute_volume(self, mute):
        """Mute (true) or unmute (false) media player."""
        self._server.Application.SetMute(mute)
        self.update_ha_state()

    def _set_play_state(self, state):
        """Helper method for play/pause/toggle."""
        players = self._get_players()

        if len(players) != 0:
            self._server.Player.PlayPause(players[0]['playerid'], state)

        self.update_ha_state()

    def media_play_pause(self):
        """Pause media on media player."""
        self._set_play_state('toggle')

    def media_play(self):
        """Play media."""
        self._set_play_state(True)

    def media_pause(self):
        """Pause the media player."""
        self._set_play_state(False)

    def media_stop(self):
        """Stop the media player."""
        players = self._get_players()

        if len(players) != 0:
            self._server.Player.Stop(players[0]['playerid'])

    def _goto(self, direction):
        """Helper method used for previous/next track."""
        players = self._get_players()

        if len(players) != 0:
            self._server.Player.GoTo(players[0]['playerid'], direction)

        self.update_ha_state()

    def media_next_track(self):
        """Send next track command."""
        self._goto('next')

    def media_previous_track(self):
        """Send next track command."""
        # first seek to position 0, Kodi seems to go to the beginning
        # of the current track current track is not at the beginning
        self.media_seek(0)
        self._goto('previous')

    def media_seek(self, position):
        """Send seek command."""
        players = self._get_players()

        time = {}

        time['milliseconds'] = int((position % 1) * 1000)
        position = int(position)

        time['seconds'] = int(position % 60)
        position /= 60

        time['minutes'] = int(position % 60)
        position /= 60

        time['hours'] = int(position)

        if len(players) != 0:
            self._server.Player.Seek(players[0]['playerid'], time)

        self.update_ha_state()

    def play_media(self, media_type, media_id, **kwargs):
        """Send the play_media command to the media player."""
        if media_type == "CHANNEL":
            self._server.Player.Open({"item": {"channelid": int(media_id)}})
        else:
            self._server.Player.Open({"item": {"file": str(media_id)}})
