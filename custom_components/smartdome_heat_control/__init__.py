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

from .const import (
    CONF_ROOM_CALLING_FOR_HEAT,
    CONF_AWAY_ENABLED,
    CONF_ROOMS,
    CONF_ROOM_AWAY_TEMPERATURE,
    CONF_VACATION_ENABLED,
    CONF_VACATION_TEMPERATURE,
    DATA_CONTROLLER,
    DATA_ENABLED,
    DEFAULT_AWAY_ENABLED,
    DEFAULT_ENABLED,
    DEFAULT_ROOM_AWAY_TEMPERATURE,
    DEFAULT_VACATION_ENABLED,
    DEFAULT_VACATION_TEMPERATURE,
    DOMAIN,
    PLATFORMS,
    SERVICE_ADD_ROOM,
    SERVICE_RELOAD,
    SERVICE_REMOVE_ROOM,
    SERVICE_UPDATE_CONFIG,
    CONF_HEATING_MODE,
    CONF_ROOM_LEARNED_OVERSHOOT,
    CONF_ROOM_HEATING_CYCLE_ACTIVE,
    CONF_ROOM_CYCLE_TARGET_TEMP,
    CONF_ROOM_CYCLE_PEAK_TEMP,
    DEFAULT_HEATING_MODE,
    DEFAULT_ADAPTIVE_OVERSHOOT,
)
from .helpers import async_discover_rooms, deep_merge

_LOGGER = logging.getLogger(__name__)


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

    cfg = dict(entry.data)
    cfg = _normalize_config(cfg)

    controller = SmartHeatingController(hass, dict(cfg))
    controller._enabled = bool(cfg.get(DATA_ENABLED, DEFAULT_ENABLED))

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_CONTROLLER: controller,
        "config": cfg,
        "entry": entry,
    }

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

        def _cleanup_start_listener():
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

    if not hass.data[DOMAIN].get("_frontend_registered"):
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
            CONF_ROOM_HEATING_CYCLE_ACTIVE: room.get(
                CONF_ROOM_HEATING_CYCLE_ACTIVE,
                False,
            ),
            CONF_ROOM_CYCLE_TARGET_TEMP: room.get(CONF_ROOM_CYCLE_TARGET_TEMP),
            CONF_ROOM_CYCLE_PEAK_TEMP: room.get(CONF_ROOM_CYCLE_PEAK_TEMP),
        }

    return normalized


def _normalize_config(cfg: dict[str, Any]) -> dict[str, Any]:
    """Gesamte Config normalisieren."""
    normalized = dict(cfg)
    normalized.setdefault(DATA_ENABLED, DEFAULT_ENABLED)
    normalized.setdefault(CONF_VACATION_ENABLED, DEFAULT_VACATION_ENABLED)
    normalized.setdefault(
        CONF_VACATION_TEMPERATURE,
        DEFAULT_VACATION_TEMPERATURE,
    )
    normalized.setdefault(CONF_AWAY_ENABLED, DEFAULT_AWAY_ENABLED)
    normalized[CONF_ROOMS] = _normalize_rooms(normalized.get(CONF_ROOMS, {}))
    normalized.setdefault(CONF_HEATING_MODE, DEFAULT_HEATING_MODE)
    return normalized


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


def _push_state(hass: HomeAssistant, cfg: dict[str, Any]) -> None:
    """Globalen UI-State aktualisieren."""
    state_cfg = _normalize_config(cfg)

    hass.states.async_set(
        f"{DOMAIN}.config",
        "active" if state_cfg.get(DATA_ENABLED, DEFAULT_ENABLED) else "disabled",
        attributes=state_cfg,
    )
