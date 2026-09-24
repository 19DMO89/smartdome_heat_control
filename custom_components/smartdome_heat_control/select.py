"""Select entities for Smartdome Heat Control."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_HEATING_MODE,
    CONF_ROOMS,
    CONF_ROOM_ENABLED,
    CONF_ROOM_HEATING_MODE,
    CONF_ROOM_LABEL,
    DATA_CONTROLLER,
    DEFAULT_HEATING_MODE,
    DOMAIN,
    HEATING_MODES,
)
from .helpers import apply_room_config_update

ROOM_HEATING_MODE_OFF = "off"
ROOM_HEATING_MODE_DEFAULT = "default"
ROOM_HEATING_MODE_OPTIONS = [ROOM_HEATING_MODE_OFF, ROOM_HEATING_MODE_DEFAULT, *HEATING_MODES]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    cfg = entry_data.get("config", {})
    rooms = cfg.get(CONF_ROOMS, {})

    entities: list[SelectEntity] = [SmartdomeHeatingModeSelect(hass, entry)]

    for room_id, room in rooms.items():
        if not isinstance(room, dict):
            continue
        label = str(room.get(CONF_ROOM_LABEL, room_id))
        entities.append(SmartdomeRoomHeatingModeSelect(hass, entry, room_id, label))

    async_add_entities(entities)


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


class SmartdomeRoomHeatingModeSelect(SelectEntity):
    """Heizmodus-Auswahl pro Raum, inklusive Option 'off' zum Deaktivieren."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_options = ROOM_HEATING_MODE_OPTIONS
    _attr_icon = "mdi:radiator"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        room_id: str,
        room_label: str,
    ) -> None:
        self.hass = hass
        self._entry = entry
        self._room_id = room_id
        self._attr_unique_id = f"{entry.entry_id}_room_{room_id}_heating_mode"
        self._attr_name = f"{room_label} – Heizmodus"

    @property
    def available(self) -> bool:
        return self._entry.entry_id in self.hass.data.get(DOMAIN, {})

    def _get_room(self) -> dict:
        entry_data = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id)
        if entry_data is None:
            return {}
        cfg = entry_data.get("config", {})
        rooms = cfg.get(CONF_ROOMS, {})
        return dict(rooms.get(self._room_id, {}))

    @property
    def current_option(self) -> str:
        room = self._get_room()

        if not bool(room.get(CONF_ROOM_ENABLED, True)):
            return ROOM_HEATING_MODE_OFF

        mode = str(room.get(CONF_ROOM_HEATING_MODE, "")).strip()
        if mode in HEATING_MODES:
            return mode

        return ROOM_HEATING_MODE_DEFAULT

    async def async_select_option(self, option: str) -> None:
        if option not in ROOM_HEATING_MODE_OPTIONS:
            return

        if option == ROOM_HEATING_MODE_OFF:
            updates = {CONF_ROOM_ENABLED: False}
        elif option == ROOM_HEATING_MODE_DEFAULT:
            updates = {CONF_ROOM_ENABLED: True, CONF_ROOM_HEATING_MODE: ""}
        else:
            updates = {CONF_ROOM_ENABLED: True, CONF_ROOM_HEATING_MODE: option}

        apply_room_config_update(self.hass, self._entry, self._room_id, updates)
        self.async_write_ha_state()
