"""Constants for ha_integration_domain."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "ha_integration_domain"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

CONF_API_VERSION = "api_version"
CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"

DEFAULT_UPDATE_INTERVAL_HOURS = 1.0

ISSUE_DEPRECATED_API = "deprecated_api_endpoint"
