"""Switch-Entity für Smartdome Heat Control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DATA_CONTROLLER,
    DATA_ENABLED,
    DEFAULT_ENABLED,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Switch-Entity für einen Config Entry anlegen."""
    async_add_entities([SmartHeatingEnableSwitch(hass, entry)], True)


class SmartHeatingEnableSwitch(SwitchEntity):
    """Globaler Ein/Aus-Schalter für Smartdome Heat Control."""

    _attr_has_entity_name = True
    _attr_name = "Enabled"
    _attr_icon = "mdi:radiator"
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_enabled"

    @property
    def is_on(self) -> bool:
        """Aktuellen Schalterzustand zurückgeben."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id, {})
        config = entry_data.get("config", {})
        return bool(config.get(DATA_ENABLED, DEFAULT_ENABLED))

    @property
    def available(self) -> bool:
        """Entity ist verfügbar, solange der Config Entry geladen ist."""
        return self._entry.entry_id in self.hass.data.get(DOMAIN, {})

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Integration aktivieren."""
        await self._async_set_enabled(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Integration deaktivieren."""
        await self._async_set_enabled(False)

    async def _async_set_enabled(self, enabled: bool) -> None:
        """Enabled-Status setzen, speichern und Controller informieren."""
        domain_data = self.hass.data.get(DOMAIN, {})
        entry_data = domain_data.get(self._entry.entry_id)

        if entry_data is None:
            _LOGGER.warning(
                "Kein Entry-Status für %s gefunden, Schalter kann nicht gesetzt werden",
                self._entry.entry_id,
            )
            return

        config = dict(entry_data.get("config", {}))
        config[DATA_ENABLED] = enabled
        entry_data["config"] = config

        self.hass.config_entries.async_update_entry(self._entry, data=config)

        controller = entry_data.get(DATA_CONTROLLER)
        if controller is not None:
            controller.update_config(config)
            controller.set_enabled(enabled)

        self._push_state(config)

        _LOGGER.info(
            "Smartdome Heat Control wurde %s",
            "aktiviert" if enabled else "deaktiviert",
        )

        self.async_write_ha_state()

    def _push_state(self, cfg: dict[str, Any]) -> None:
        """Globalen UI-State aktualisieren."""
        state_cfg = dict(cfg)
        state_cfg.setdefault(DATA_ENABLED, DEFAULT_ENABLED)

        self.hass.states.async_set(
            f"{DOMAIN}.config",
            "active" if state_cfg.get(DATA_ENABLED, DEFAULT_ENABLED) else "disabled",
            attributes=state_cfg,
        )
