"""Smartdome Heat Control – Integration Entry Point."""
from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

import voluptuous as vol
from homeassistant.components import frontend, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_AWAY_ENABLED,
    CONF_CIRCUIT_LABEL,
    CONF_CIRCUIT_MAIN_SENSOR,
    CONF_CIRCUIT_MAIN_THERMOSTAT,
    CONF_CIRCUITS,
    CONF_HEATING_MODE,
    CONF_ROOMS,
    CONF_ROOM_CIRCUIT_ID,
    CONF_ROOM_CONTROL_PROFILE,
    CONF_ROOM_WINDOW_SENSORS,
    DEFAULT_ROOM_CONTROL_PROFILE,
    CONF_ROOM_AWAY_TEMPERATURE,
    CONF_ROOM_CALLING_FOR_HEAT,
    CONF_ROOM_CYCLE_PEAK_TEMP,
    CONF_ROOM_CYCLE_START_TS,
    CONF_ROOM_CYCLE_TARGET_TEMP,
    CONF_ROOM_HEATING_CYCLE_ACTIVE,
    CONF_ROOM_LEARNED_OVERSHOOT,
    CONF_ROOM_LEARNED_OVERSHOOT_LONG,
    CONF_ROOM_LEARNED_OVERSHOOT_MEDIUM,
    CONF_ROOM_LEARNED_OVERSHOOT_SHORT,
    CONF_VACATION_ENABLED,
    CONF_VACATION_TEMPERATURE,
    CONF_ENERGY_RESIDUAL_HEAT_HOLD,
    DEFAULT_ENERGY_RESIDUAL_HEAT_HOLD,
    DATA_CONTROLLER,
    DATA_ENABLED,
    DEFAULT_ADAPTIVE_OVERSHOOT,
    DEFAULT_ADAPTIVE_OVERSHOOT_LONG,
    DEFAULT_ADAPTIVE_OVERSHOOT_MEDIUM,
    DEFAULT_ADAPTIVE_OVERSHOOT_SHORT,
    DEFAULT_AWAY_ENABLED,
    DEFAULT_ENABLED,
    DEFAULT_HEATING_MODE,
    DEFAULT_ROOM_AWAY_TEMPERATURE,
    DEFAULT_VACATION_ENABLED,
    DEFAULT_VACATION_TEMPERATURE,
    CONF_ROOM_WEEKLY_SCHEDULE,
    DEFAULT_ROOM_WEEKLY_SCHEDULE,
    DOMAIN,
    PLATFORMS,
    SERVICE_ADD_ROOM,
    SERVICE_RELOAD,
    SERVICE_REMOVE_ROOM,
    SERVICE_UPDATE_CONFIG,
)
from .helpers import async_discover_rooms, deep_merge

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def _get_integration_version(hass: HomeAssistant) -> str:
    """Version aus manifest.json lesen (async-safe)."""
    manifest_path = os.path.join(os.path.dirname(__file__), "manifest.json")

    def _read_manifest() -> str:
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
            return str(manifest.get("version", "dev"))
        except Exception:
            _LOGGER.exception("Version aus manifest.json konnte nicht gelesen werden")
            return "dev"

    return await hass.async_add_executor_job(_read_manifest)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """YAML-Setup wird nicht verwendet."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup der Integration über Config Entry."""
    from .controller import SmartHeatingController

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["_version"] = await _get_integration_version(hass)

    cfg = _normalize_config(dict(entry.data))

    controller = SmartHeatingController(hass, dict(cfg))
    controller._enabled = bool(cfg.get(DATA_ENABLED, DEFAULT_ENABLED))

    domain_data: dict[str, Any] = {
        DATA_CONTROLLER: controller,
        "config": cfg,
        "entry": entry,
    }
    hass.data[DOMAIN][entry.entry_id] = domain_data

    async def _persist_learned(config: dict[str, Any]) -> None:
        hass.config_entries.async_update_entry(entry, data=config)
        domain_data["config"] = config

    controller.set_persist_callback(_persist_learned)

    def _on_room_states_updated(room_states: dict[str, str]) -> None:
        _push_state(hass, domain_data["config"], room_states=room_states)

    controller.set_state_callback(_on_room_states_updated)

    await _async_register_frontend(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _async_register_ws_save_config(hass)
    _async_register_services(hass)
    _push_state(hass, cfg)

    if hass.is_running:
        await controller.async_start()
    else:
        start_listener = None

        @callback
        def _start_when_ready(event) -> None:
            nonlocal start_listener
            start_listener = None
            hass.async_create_task(controller.async_start())

        start_listener = hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED,
            _start_when_ready,
        )

        def _cleanup_start_listener() -> None:
            nonlocal start_listener
            if start_listener is not None:
                start_listener()
                start_listener = None

        entry.async_on_unload(_cleanup_start_listener)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entladen."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, {})
    controller = data.get(DATA_CONTROLLER)
    if controller is not None:
        await controller.async_stop()

    remaining_entries = [
        key for key in hass.data.get(DOMAIN, {}) if not key.startswith("_")
    ]

    if not remaining_entries:
        try:
            hass.states.async_remove(f"{DOMAIN}.config")
        except Exception:
            _LOGGER.debug("State %s.config konnte nicht entfernt werden", DOMAIN)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Integration neu laden."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload bei Änderungen im Options Flow."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Statisches Frontend und Sidebar-Panel registrieren."""
    frontend_path = os.path.join(os.path.dirname(__file__), "www")
    version = hass.data.get(DOMAIN, {}).get("_version", "dev")

    if hass.data[DOMAIN].get("_frontend_registered"):
        return

    if os.path.exists(frontend_path):
        await hass.http.async_register_static_paths(
            [StaticPathConfig("/smartdome_ui", frontend_path, False)]
        )
    else:
        _LOGGER.error("Frontend-Ordner 'www' nicht gefunden in %s", frontend_path)
        return

    frontend.async_register_built_in_panel(
        hass,
        component_name="iframe",
        sidebar_title="Smartdome Heat",
        sidebar_icon="mdi:radiator",
        frontend_url_path="smartdome_control",
        config={"url": f"/smartdome_ui/index.html?v={version}"},
        require_admin=False,
    )

    hass.data[DOMAIN]["_frontend_registered"] = True


def _normalize_window_sensors(room: dict[str, Any]) -> list[str]:
    """Fenstersensoren normalisieren und altes window_sensor-Feld migrieren."""
    sensors = room.get(CONF_ROOM_WINDOW_SENSORS)
    if isinstance(sensors, list):
        return [s for s in sensors if isinstance(s, str) and s]
    # migrate legacy single-sensor field
    old = room.get("window_sensor", "")
    return [old] if isinstance(old, str) and old else []


def _normalize_rooms(rooms: Any) -> dict[str, dict[str, Any]]:
    """Räume normalisieren."""
    if not isinstance(rooms, dict):
        return {}

    normalized: dict[str, dict[str, Any]] = {}

    for room_id, room in rooms.items():
        if not isinstance(room, dict):
            continue

        normalized[room_id] = {
            "label": room.get("label", room_id),
            "area_id": room.get("area_id", ""),
            "thermostat": room.get("thermostat", ""),
            "sensor": room.get("sensor", ""),
            "window_sensor": room.get("window_sensor", ""),
            CONF_ROOM_WINDOW_SENSORS: _normalize_window_sensors(room),
            "target_day": room.get("target_day", 21.0),
            "target_night": room.get("target_night", 18.0),
            "away_temperature": room.get(
                "away_temperature",
                DEFAULT_ROOM_AWAY_TEMPERATURE,
            ),
            "day_start": room.get("day_start", ""),
            "night_start": room.get("night_start", ""),
            "enabled": room.get("enabled", True),
            CONF_ROOM_CALLING_FOR_HEAT: room.get(CONF_ROOM_CALLING_FOR_HEAT, False),
            CONF_ROOM_LEARNED_OVERSHOOT: room.get(
                CONF_ROOM_LEARNED_OVERSHOOT,
                DEFAULT_ADAPTIVE_OVERSHOOT,
            ),
            CONF_ROOM_LEARNED_OVERSHOOT_SHORT: room.get(
                CONF_ROOM_LEARNED_OVERSHOOT_SHORT,
                DEFAULT_ADAPTIVE_OVERSHOOT_SHORT,
            ),
            CONF_ROOM_LEARNED_OVERSHOOT_MEDIUM: room.get(
                CONF_ROOM_LEARNED_OVERSHOOT_MEDIUM,
                DEFAULT_ADAPTIVE_OVERSHOOT_MEDIUM,
            ),
            CONF_ROOM_LEARNED_OVERSHOOT_LONG: room.get(
                CONF_ROOM_LEARNED_OVERSHOOT_LONG,
                DEFAULT_ADAPTIVE_OVERSHOOT_LONG,
            ),
            CONF_ROOM_HEATING_CYCLE_ACTIVE: room.get(
                CONF_ROOM_HEATING_CYCLE_ACTIVE,
                False,
            ),
            CONF_ROOM_WEEKLY_SCHEDULE: room.get(
                CONF_ROOM_WEEKLY_SCHEDULE,
                DEFAULT_ROOM_WEEKLY_SCHEDULE,
            ),
            CONF_ROOM_CYCLE_TARGET_TEMP: room.get(CONF_ROOM_CYCLE_TARGET_TEMP),
            CONF_ROOM_CYCLE_PEAK_TEMP: room.get(CONF_ROOM_CYCLE_PEAK_TEMP),
            CONF_ROOM_CYCLE_START_TS: None,
            CONF_ROOM_CIRCUIT_ID: room.get(CONF_ROOM_CIRCUIT_ID, ""),
            "control_profile": room.get(
            "control_profile",
            DEFAULT_ROOM_CONTROL_PROFILE,
            ),
        }

    return normalized


def _normalize_circuits(circuits: Any) -> dict[str, dict[str, Any]]:
    """Heizkreise normalisieren."""
    if not isinstance(circuits, dict):
        return {}

    normalized: dict[str, dict[str, Any]] = {}
    for circuit_id, circuit in circuits.items():
        if not isinstance(circuit, dict):
            continue
        normalized[circuit_id] = {
            CONF_CIRCUIT_LABEL: circuit.get(CONF_CIRCUIT_LABEL, circuit_id),
            CONF_CIRCUIT_MAIN_THERMOSTAT: circuit.get(CONF_CIRCUIT_MAIN_THERMOSTAT, ""),
            CONF_CIRCUIT_MAIN_SENSOR: circuit.get(CONF_CIRCUIT_MAIN_SENSOR, ""),
        }
    return normalized


def _normalize_config(cfg: dict[str, Any]) -> dict[str, Any]:
    """Gesamte Config normalisieren."""
    normalized = dict(cfg)
    normalized.setdefault(DATA_ENABLED, DEFAULT_ENABLED)
    normalized.setdefault(CONF_VACATION_ENABLED, DEFAULT_VACATION_ENABLED)
    normalized.setdefault(CONF_VACATION_TEMPERATURE, DEFAULT_VACATION_TEMPERATURE)
    normalized.setdefault(CONF_AWAY_ENABLED, DEFAULT_AWAY_ENABLED)
    normalized.setdefault(CONF_HEATING_MODE, DEFAULT_HEATING_MODE)
    normalized[CONF_ROOMS] = _normalize_rooms(normalized.get(CONF_ROOMS, {}))
    normalized[CONF_CIRCUITS] = _normalize_circuits(normalized.get(CONF_CIRCUITS, {}))
    normalized.setdefault(CONF_ENERGY_RESIDUAL_HEAT_HOLD,DEFAULT_ENERGY_RESIDUAL_HEAT_HOLD,)
    return normalized


def _async_register_ws_save_config(hass: HomeAssistant) -> None:
    """WebSocket-Command für direktes Speichern aus dem Web-Panel registrieren."""
    command_type = f"{DOMAIN}/save_config"

    if hass.data[DOMAIN].get("_ws_registered"):
        return

    @websocket_api.websocket_command(
        {
            vol.Required("type"): command_type,
            vol.Required("config"): dict,
        }
    )
    @websocket_api.async_response
    async def ws_save_config(
        hass: HomeAssistant,
        connection: websocket_api.ActiveConnection,
        msg: dict[str, Any],
    ) -> None:
        target_entry = _get_single_entry(hass)
        if target_entry is None:
            connection.send_error(msg["id"], "not_found", "Keine Config Entry gefunden")
            return

        data = hass.data[DOMAIN][target_entry.entry_id]
        controller = data[DATA_CONTROLLER]

        new_cfg = _normalize_config(dict(msg["config"]))

        hass.config_entries.async_update_entry(target_entry, data=new_cfg)
        data["config"] = new_cfg

        controller.update_config(new_cfg)
        controller.set_enabled(bool(new_cfg.get(DATA_ENABLED, DEFAULT_ENABLED)))

        _push_state(hass, new_cfg)
        connection.send_result(msg["id"], {"success": True})

    websocket_api.async_register_command(hass, ws_save_config)
    hass.data[DOMAIN]["_ws_registered"] = True


def _async_register_services(hass: HomeAssistant) -> None:
    """Services für UI, Automationen und Abwärtskompatibilität registrieren."""
    if hass.data[DOMAIN].get("_services_registered"):
        return

    async def handle_update_config(call: ServiceCall) -> None:
        target_entry = _get_single_entry(hass)
        if target_entry is None:
            _LOGGER.warning("Kein Config Entry für update_config gefunden")
            return

        data = hass.data[DOMAIN][target_entry.entry_id]
        current_cfg = dict(data["config"])
        patch = dict(call.data.get("config", {}))

        # Rooms must be replaced entirely, not merged, so that deleted rooms
        # are actually removed and don't reappear after reload.
        if CONF_ROOMS in patch:
            current_cfg[CONF_ROOMS] = patch.pop(CONF_ROOMS)

        deep_merge(current_cfg, patch)
        current_cfg = _normalize_config(current_cfg)

        hass.config_entries.async_update_entry(target_entry, data=current_cfg)
        data["config"] = current_cfg

        controller = data[DATA_CONTROLLER]
        controller.update_config(current_cfg)
        controller.set_enabled(bool(current_cfg.get(DATA_ENABLED, DEFAULT_ENABLED)))

        _push_state(hass, current_cfg)

    async def handle_add_room(call: ServiceCall) -> None:
        target_entry = _get_single_entry(hass)
        if target_entry is None:
            _LOGGER.warning("Kein Config Entry für add_room gefunden")
            return

        data = hass.data[DOMAIN][target_entry.entry_id]
        cfg = dict(data["config"])

        room_id = call.data.get("room_id") or f"room_{uuid.uuid4().hex[:8]}"
        room_label = call.data.get("label", "Neuer Raum")

        rooms = cfg.setdefault(CONF_ROOMS, {})
        if room_id not in rooms:
            rooms[room_id] = {
                "label": room_label,
                "area_id": call.data.get("area_id", ""),
                "thermostat": call.data.get("thermostat", ""),
                "sensor": call.data.get("sensor", ""),
                "window_sensor": call.data.get("window_sensor", ""),
                "target_day": call.data.get("target_day", 21.0),
                "target_night": call.data.get("target_night", 18.0),
                "away_temperature": call.data.get(
                    "away_temperature",
                    DEFAULT_ROOM_AWAY_TEMPERATURE,
                ),
                "day_start": call.data.get("day_start", ""),
                "night_start": call.data.get("night_start", ""),
                "enabled": call.data.get("enabled", True),
            }

        cfg = _normalize_config(cfg)

        hass.config_entries.async_update_entry(target_entry, data=cfg)
        data["config"] = cfg

        controller = data[DATA_CONTROLLER]
        controller.update_config(cfg)

        _push_state(hass, cfg)

    async def handle_remove_room(call: ServiceCall) -> None:
        target_entry = _get_single_entry(hass)
        if target_entry is None:
            _LOGGER.warning("Kein Config Entry für remove_room gefunden")
            return

        data = hass.data[DOMAIN][target_entry.entry_id]
        cfg = dict(data["config"])

        room_id = call.data.get("room_id")
        if room_id and room_id in cfg.get(CONF_ROOMS, {}):
            del cfg[CONF_ROOMS][room_id]

            cfg = _normalize_config(cfg)

            hass.config_entries.async_update_entry(target_entry, data=cfg)
            data["config"] = cfg

            controller = data[DATA_CONTROLLER]
            controller.update_config(cfg)

            _push_state(hass, cfg)

    async def handle_reload(call: ServiceCall) -> None:
        target_entry = _get_single_entry(hass)
        if target_entry is None:
            _LOGGER.warning("Kein Config Entry für reload gefunden")
            return

        data = hass.data[DOMAIN][target_entry.entry_id]
        cfg = dict(data["config"])

        discovered_rooms = await async_discover_rooms(hass)
        existing_rooms = cfg.setdefault(CONF_ROOMS, {})

        for room_id, discovered_room in discovered_rooms.items():
            if room_id not in existing_rooms:
                existing_rooms[room_id] = {
                    **discovered_room,
                    "away_temperature": discovered_room.get(
                        "away_temperature",
                        DEFAULT_ROOM_AWAY_TEMPERATURE,
                    ),
                }
                continue

            existing = existing_rooms[room_id]
            existing_rooms[room_id] = {
                "label": existing.get("label", discovered_room.get("label", room_id)),
                "area_id": existing.get("area_id", discovered_room.get("area_id", "")),
                "thermostat": existing.get(
                    "thermostat",
                    discovered_room.get("thermostat", ""),
                ),
                "sensor": existing.get("sensor", discovered_room.get("sensor", "")),
                "window_sensor": existing.get(
                    "window_sensor",
                    discovered_room.get("window_sensor", ""),
                ),
                CONF_ROOM_WINDOW_SENSORS: existing.get(
                    CONF_ROOM_WINDOW_SENSORS,
                    _normalize_window_sensors(discovered_room),
                ),
                "target_day": existing.get(
                    "target_day",
                    discovered_room.get("target_day", 21.0),
                ),
                "target_night": existing.get(
                    "target_night",
                    discovered_room.get("target_night", 18.0),
                ),
                "away_temperature": existing.get(
                    "away_temperature",
                    discovered_room.get(
                        "away_temperature",
                        DEFAULT_ROOM_AWAY_TEMPERATURE,
                    ),
                ),
                "day_start": existing.get("day_start", ""),
                "night_start": existing.get("night_start", ""),
                "enabled": existing.get("enabled", True),
            }

        cfg = _normalize_config(cfg)

        hass.config_entries.async_update_entry(target_entry, data=cfg)
        data["config"] = cfg

        controller = data[DATA_CONTROLLER]
        controller.update_config(cfg)

        _push_state(hass, cfg)

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_CONFIG,
        handle_update_config,
        schema=vol.Schema({vol.Required("config"): dict}),
    )
    hass.services.async_register(DOMAIN, SERVICE_ADD_ROOM, handle_add_room)
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_ROOM,
        handle_remove_room,
        schema=vol.Schema({vol.Required("room_id"): str}),
    )
    hass.services.async_register(DOMAIN, SERVICE_RELOAD, handle_reload)

    hass.data[DOMAIN]["_services_registered"] = True


def _get_single_entry(hass: HomeAssistant) -> ConfigEntry | None:
    """Die erste verfügbare Config Entry holen."""
    domain_data = hass.data.get(DOMAIN, {})
    for key, value in domain_data.items():
        if key.startswith("_"):
            continue
        entry = value.get("entry")
        if entry is not None:
            return entry
    return None


def _push_state(
    hass: HomeAssistant,
    cfg: dict[str, Any],
    room_states: dict[str, str] | None = None,
) -> None:
    """Globalen UI-State aktualisieren."""
    state_cfg = _normalize_config(cfg)
    if room_states is not None:
        state_cfg["room_states"] = room_states

    hass.states.async_set(
        f"{DOMAIN}.config",
        "active" if state_cfg.get(DATA_ENABLED, DEFAULT_ENABLED) else "disabled",
        attributes=state_cfg,
    )
