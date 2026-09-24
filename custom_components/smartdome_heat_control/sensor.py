"""Sensor-Entities für Smartdome Heat Control."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_ROOMS,
    CONF_ROOM_LABEL,
    DATA_CONTROLLER,
    DOMAIN,
    SIGNAL_ROOM_STATE_UPDATED,
)

ROOM_STATUS_OPTIONS = ["off", "idle", "heating", "residual_hold", "window_pause"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor-Entities für einen Config Entry anlegen."""
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    cfg = entry_data.get("config", {})
    rooms = cfg.get(CONF_ROOMS, {})

    entities: list[SensorEntity] = []
    for room_id, room in rooms.items():
        if not isinstance(room, dict):
            continue
        label = str(room.get(CONF_ROOM_LABEL, room_id))
        entities.append(SmartdomeRoomStatusSensor(hass, entry, room_id, label))

    async_add_entities(entities, True)


class SmartdomeRoomStatusSensor(SensorEntity):
    """Zustand eines Raums mit Zieltemperatur, Ist-Temperatur und Heizmodus als Attribute."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ROOM_STATUS_OPTIONS
    _attr_icon = "mdi:home-thermometer"

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
        self._attr_unique_id = f"{entry.entry_id}_room_{room_id}_status"
        self._attr_name = f"{room_label} – Status"

    @property
    def available(self) -> bool:
        """Entity ist verfügbar, solange der Config Entry geladen ist."""
        return self._entry.entry_id in self.hass.data.get(DOMAIN, {})

    def _get_controller(self) -> Any:
        entry_data = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id)
        if entry_data is None:
            return None
        return entry_data.get(DATA_CONTROLLER)

    @property
    def native_value(self) -> str | None:
        controller = self._get_controller()
        if controller is None:
            return None
        return controller.get_room_status(self._room_id)["state"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        controller = self._get_controller()
        if controller is None:
            return {}
        status = controller.get_room_status(self._room_id)
        return {
            "target_temperature": status["target_temperature"],
            "current_temperature": status["current_temperature"],
            "heating_mode": status["heating_mode"],
            "enabled": status["enabled"],
            "away_active": status["away_active"],
        }

    async def async_added_to_hass(self) -> None:
        """Auf Raumzustands-Updates reagieren, ohne zu pollen."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_ROOM_STATE_UPDATED,
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self, room_states: dict[str, Any]) -> None:
        # room_states enthält nur aktive Räume – bei einem deaktivierten Raum
        # (state wechselt auf "off") ist dieser Raum hier NICHT enthalten,
        # daher unabhängig vom Payload-Inhalt immer aktualisieren.
        self.async_write_ha_state()
