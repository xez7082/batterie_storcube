import logging

DOMAIN = "storcube_bridge"

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    _LOGGER.info("Storcube Bridge integration loaded")
    return True
