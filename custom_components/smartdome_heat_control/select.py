"""Select entities for Smartdome Heat Control."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_HEATING_MODE,
    DATA_CONTROLLER,
    DEFAULT_HEATING_MODE,
    DOMAIN,
    HEATING_MODES,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([SmartdomeHeatingModeSelect(hass, entry)])


class SmartdomeHeatingModeSelect(SelectEntity):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_name = "Heating mode"
        self._attr_unique_id = "smartdome_heat_control_heating_mode"
        self._attr_options = HEATING_MODES
        self._attr_icon = "mdi:radiator"

    @property
    def current_option(self) -> str:
        data = self.hass.data[DOMAIN][self._entry.entry_id]
        cfg = data.get("config", {})
        return cfg.get(CONF_HEATING_MODE, DEFAULT_HEATING_MODE)

    async def async_select_option(self, option: str) -> None:
        if option not in HEATING_MODES:
            return

        data = self.hass.data[DOMAIN][self._entry.entry_id]
        cfg = dict(data.get("config", {}))
        cfg[CONF_HEATING_MODE] = option

        self.hass.config_entries.async_update_entry(self._entry, data=cfg)
        data["config"] = cfg

        controller = data[DATA_CONTROLLER]
        controller.update_config(cfg)
        controller._evaluate()

        self.async_write_ha_state()
