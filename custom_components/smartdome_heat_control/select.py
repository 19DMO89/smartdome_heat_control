"""Select entities for Smartdome Heat Control."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_ACTIVE_SCHEDULE_PROFILE,
    CONF_SCHEDULE_PROFILES,
    DATA_ENABLED,
    DEFAULT_ENABLED,
    DEFAULT_SCHEDULE_PROFILE_ID,
    DEFAULT_SCHEDULE_PROFILE_LABEL,
    SIGNAL_ROOM_STATE_UPDATED,
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

    entities: list[SelectEntity] = [
        SmartdomeHeatingModeSelect(hass, entry),
        SmartdomeScheduleProfileSelect(hass, entry),
    ]

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


class SmartdomeScheduleProfileSelect(SelectEntity):
    """Aktives Zeitplan-Profil, z. B. für Dashboards und Automationen."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_name = "Zeitplan-Profil"
        self._attr_unique_id = f"{entry.entry_id}_schedule_profile"

    @property
    def available(self) -> bool:
        return self._entry.entry_id in self.hass.data.get(DOMAIN, {})

    def _config(self) -> dict:
        entry_data = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id) or {}
        return entry_data.get("config", {})

    def _label_map(self) -> dict[str, str]:
        """Anzeigename → Profil-ID (doppelte Namen bekommen die ID angehängt)."""
        profiles = self._config().get(CONF_SCHEDULE_PROFILES) or {
            DEFAULT_SCHEDULE_PROFILE_ID: {"label": DEFAULT_SCHEDULE_PROFILE_LABEL}
        }
        result: dict[str, str] = {}
        for profile_id, profile in profiles.items():
            label = str((profile or {}).get("label") or profile_id)
            if label in result:
                label = f"{label} ({profile_id})"
            result[label] = profile_id
        return result

    @property
    def options(self) -> list[str]:
        return list(self._label_map())

    @property
    def current_option(self) -> str | None:
        active = self._config().get(CONF_ACTIVE_SCHEDULE_PROFILE, DEFAULT_SCHEDULE_PROFILE_ID)
        for label, profile_id in self._label_map().items():
            if profile_id == active:
                return label
        return next(iter(self._label_map()), None)

    async def async_select_option(self, option: str) -> None:
        profile_id = self._label_map().get(option)
        entry_data = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id)
        if profile_id is None or entry_data is None:
            return

        cfg = dict(entry_data.get("config", {}))
        cfg[CONF_ACTIVE_SCHEDULE_PROFILE] = profile_id
        entry_data["config"] = cfg
        self.hass.config_entries.async_update_entry(self._entry, data=cfg)

        controller = entry_data.get(DATA_CONTROLLER)
        if controller is not None:
            controller.update_config(cfg)

        state_cfg = dict(cfg)
        state_cfg.setdefault(DATA_ENABLED, DEFAULT_ENABLED)
        self.hass.states.async_set(
            f"{DOMAIN}.config",
            "active" if state_cfg.get(DATA_ENABLED, DEFAULT_ENABLED) else "disabled",
            attributes=state_cfg,
        )
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        # Profilwechsel im Panel: Zustand bei der nächsten Auswertung nachziehen.
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_ROOM_STATE_UPDATED, self._handle_update)
        )

    @callback
    def _handle_update(self, _room_states) -> None:
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
