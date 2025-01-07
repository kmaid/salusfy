"""
Adds support for the Salus Thermostat units.
"""
import datetime
import time
import logging
import re
import json
import aiohttp

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.climate.const import (
    HVACAction,
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_ID,
    UnitOfTemperature,
)

try:
    from homeassistant.components.climate import (
        ClimateEntity,
        PLATFORM_SCHEMA,
    )
except ImportError:
    from homeassistant.components.climate import (
        ClimateDevice as ClimateEntity,
        PLATFORM_SCHEMA,
    )

from homeassistant.helpers.reload import async_setup_reload_service
from asyncio import Lock

__version__ = "0.0.3"

_LOGGER = logging.getLogger(__name__)

URL_LOGIN = "https://salus-it500.com/public/login.php"
URL_GET_TOKEN = "https://salus-it500.com/public/control.php"
URL_GET_DATA = "https://salus-it500.com/public/ajax_device_values.php"
URL_SET_DATA = "https://salus-it500.com/includes/set.php"

DEFAULT_NAME = "Salus Thermostat"

CONF_NAME = "name"

# Values from web interface
MIN_TEMP = 5
MAX_TEMP = 34.5

SUPPORT_FLAGS = (
    ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF
)

DOMAIN = "salusfy"
PLATFORMS = ["climate"]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_ID): cv.string,
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)
    name = config.get(CONF_NAME)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    id = config.get(CONF_ID)

    async_add_entities([SalusThermostat(name, username, password, id)])

class SalusThermostat(ClimateEntity):
    """Representation of a Salus Thermostat device."""

    def __init__(self, name, username, password, id):
        """Initialize the thermostat."""
        self._name = name
        self._username = username
        self._password = password
        self._id = id
        self._current_temperature = None
        self._target_temperature = None
        self._frost = None
        self._status = None
        self._current_operation_mode = None
        self._token = None
        self._session = aiohttp.ClientSession()
        self._update_lock = Lock()

    async def close(self):
        """Close the aiohttp session."""
        await self._session.close()

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this thermostat."""
        return "_".join([self._name, "climate"])

    @property
    def should_poll(self):
        """Return if polling is required."""
        return True

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return MAX_TEMP

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode."""
        climate_mode = self._current_operation_mode
        return HVACMode.HEAT if climate_mode == "ON" else HVACMode.OFF

    @property
    def hvac_modes(self):
        """HVAC modes."""
        return [HVACMode.HEAT, HVACMode.OFF]

    @property
    def hvac_action(self):
        """Return the current running hvac operation."""
        return HVACAction.HEATING if self._status == "ON" else HVACAction.IDLE

    @property
    def preset_mode(self):
        """Return the current preset mode, e.g., home, away, temp."""
        return self._status

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return []  # Define preset modes if applicable

    async def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            await self._set_temperature(temperature)

    async def _set_temperature(self, temperature):
        """Set new target temperature, via URL commands."""
        payload = {
            "token": self._token,
            "devId": self._id,
            "tempUnit": "0",
            "current_tempZ1_set": "1",
            "current_tempZ1": temperature,
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        async with self._session.post(URL_SET_DATA, data=payload, headers=headers) as response:
            if response.status == 200:
                self._target_temperature = temperature
                _LOGGER.info("Salusfy set_temperature OK")
            else:
                _LOGGER.error(f"Failed to set temperature, status: {response.status}")

    async def set_hvac_mode(self, hvac_mode):
        """Set HVAC mode, via URL commands."""
        headers = {"content-type": "application/x-www-form-urlencoded"}
        payload = {
            "token": self._token,
            "devId": self._id,
            "auto": "1" if hvac_mode == HVACMode.OFF else "0",
            "auto_setZ1": "1",
        }
        async with self._session.post(URL_SET_DATA, data=payload, headers=headers) as response:
            if response.status == 200:
                self._current_operation_mode = "OFF" if hvac_mode == HVACMode.OFF else "ON"
                _LOGGER.info("Salusfy set_hvac_mode OK")
            else:
                _LOGGER.error(f"Failed to set HVAC mode, status: {response.status}")

    async def get_token(self):
        """Get the Session Token of the Thermostat."""
        payload = {
            "IDemail": self._username,
            "password": self._password,
            "login": "Login",
            "keep_logged_in": "1",
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        async with self._session.post(URL_LOGIN, data=payload, headers=headers) as response:
            if response.status == 200:
                params = {"devId": self._id}
                async with self._session.get(URL_GET_TOKEN, params=params) as token_response:
                    text = await token_response.text()
                    result = re.search('<input id="token" type="hidden" value="(.*)" />', text)
                    if result:
                        self._token = result.group(1)
                        _LOGGER.info("Salusfy get_token OK")
                    else:
                        _LOGGER.error("Failed to extract token.")
            else:
                _LOGGER.error(f"Login failed with status {response.status}.")

    async def _get_data(self):
        if self._token is None:
            await self.get_token()
        params = {
            "devId": self._id,
            "token": self._token,
            "&_": str(int(round(time.time() * 1000))),
        }
        try:
            async with self._session.get(URL_GET_DATA, params=params) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    text = await response.text()
                    if 'application/json' in content_type or text.startswith('{'):
                        data = json.loads(text)
                        _LOGGER.info("Salusfy get_data output OK")
                        self._target_temperature = float(data["CH1currentSetPoint"])
                        self._current_temperature = float(data["CH1currentRoomTemp"])
                        self._frost = float(data["frost"])
                        self._status = "ON" if data['CH1heatOnOffStatus'] == "1" else "OFF"
                        self._current_operation_mode = "OFF" if data['CH1heatOnOff'] == "1" else "ON"
                    else:
                        _LOGGER.error(f"Unexpected content type: {content_type}. Response: {text}")
                elif response.status == 401:
                    _LOGGER.warning("Token expired, re-authenticating.")
                    await self.get_token()
                    await self._get_data()
                else:
                    _LOGGER.error(f"Failed to get data, status: {response.status}")
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error occurred: {e}")
        except json.JSONDecodeError:
            _LOGGER.error("Failed to decode JSON response.")

    async def async_update(self):
        """Asynchronous update for Home Assistant."""
        async with self._update_lock:
            await self._get_data()
