"""Helper-Funktionen für Smartdome Heat Control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import (
    CONF_ROOM_AREA_ID,
    CONF_ROOM_DAY_START,
    CONF_ROOM_ENABLED,
    CONF_ROOM_LABEL,
    CONF_ROOM_NIGHT_START,
    CONF_ROOM_SENSOR,
    CONF_ROOM_TARGET_DAY,
    CONF_ROOM_TARGET_NIGHT,
    CONF_ROOM_THERMOSTAT,
    CONF_ROOM_WINDOW_SENSOR,
    CONF_ROOM_WINDOW_SENSORS,
    CONF_ROOMS,
    DATA_CONTROLLER,
    DATA_ENABLED,
    DEFAULT_ENABLED,
    DEFAULT_TARGET_DAY,
    DEFAULT_TARGET_NIGHT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def normalize_window_sensors(room: dict[str, Any] | None) -> list[str]:
    """Fensterkontakte eines Raums als Liste liefern.

    Einzige Quelle ist ``window_sensors`` (Liste). Das alte Einzelfeld
    ``window_sensor`` wird nur noch migriert und dabei mit der Liste
    zusammengeführt, damit ein dort gesetzter Wert nicht verloren geht.
    """
    if not isinstance(room, dict):
        return []
    result: list[str] = []
    sensors = room.get(CONF_ROOM_WINDOW_SENSORS)
    if isinstance(sensors, str):
        sensors = [sensors]
    if isinstance(sensors, list):
        for sensor in sensors:
            if isinstance(sensor, str) and sensor and sensor not in result:
                result.append(sensor)
    legacy = room.get(CONF_ROOM_WINDOW_SENSOR)
    if isinstance(legacy, str) and legacy and legacy not in result:
        result.append(legacy)
    return result


def _is_state_available(state: State | None) -> bool:
    return state is not None and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _entity_area(entity: Any, area_id: str, device_registry: Any) -> bool:
    if getattr(entity, "area_id", None) == area_id:
        return True

    device_id = getattr(entity, "device_id", None)
    if device_id:
        device = device_registry.async_get(device_id)
        if device and getattr(device, "area_id", None) == area_id:
            return True

    return False


def _available_entities(hass: HomeAssistant, entities: list[Any]) -> list[Any]:
    result: list[Any] = []
    for entity in entities:
        state = hass.states.get(entity.entity_id)
        if _is_state_available(state):
            result.append(entity)
    return result


def _best_entity(
    hass: HomeAssistant,
    entities: list[Any],
    domain: str,
    prefer_available: bool = True,
) -> str | None:
    candidates = [
        entity
        for entity in entities
        if entity.domain == domain
        and not entity.disabled_by
        and entity.platform != DOMAIN
    ]
    if not candidates:
        return None

    if prefer_available:
        available = _available_entities(hass, candidates)
        if available:
            return available[0].entity_id

    return candidates[0].entity_id


def _sensor_score(hass: HomeAssistant, entity: Any) -> tuple[int, int]:
    score = 0
    state = hass.states.get(entity.entity_id)

    if state and state.attributes.get("device_class") == "temperature":
        score += 100

    if state and _safe_float(state.state) is not None:
        score += 10

    entity_id_lower = entity.entity_id.lower()
    if "temperature" in entity_id_lower:
        score += 3
    elif "temp" in entity_id_lower:
        score += 2

    return score, -len(entity.entity_id)


def _best_sensor(hass: HomeAssistant, entities: list[Any]) -> str | None:
    # Never autodiscover arbitrary numeric sensors (e.g. printer or battery).
    candidates = [
        entity for entity in entities
        if entity.domain == SENSOR_DOMAIN
        and not entity.disabled_by
        and (state := hass.states.get(entity.entity_id)) is not None
        and state.attributes.get("device_class") == "temperature"
        and state.attributes.get("unit_of_measurement") in ("°C", "°F")
    ]
    if not candidates:
        return None

    available_candidates = _available_entities(hass, candidates)
    pool = available_candidates or candidates

    best = sorted(pool, key=lambda entity: _sensor_score(hass, entity), reverse=True)
    top = best[0]
    top_state = hass.states.get(top.entity_id)

    if top_state is None:
        return None

    if top_state.attributes.get("device_class") == "temperature":
        return top.entity_id

    return None


async def async_discover_rooms(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    area_registry = async_get_area_registry(hass)
    entity_registry = async_get_entity_registry(hass)
    device_registry = async_get_device_registry(hass)

    rooms: dict[str, dict[str, Any]] = {}

    for area in area_registry.async_list_areas():
        area_id = area.id
        area_name = area.name

        area_entities = [
            entity
            for entity in entity_registry.entities.values()
            if _entity_area(entity, area_id, device_registry)
        ]

        thermostat = _best_entity(hass, area_entities, domain=CLIMATE_DOMAIN, prefer_available=True)
        sensor = _best_sensor(hass, area_entities)

        if thermostat or sensor:
            rooms[area_id] = {
                CONF_ROOM_LABEL: area_name,
                CONF_ROOM_AREA_ID: area_id,
                CONF_ROOM_THERMOSTAT: thermostat or "",
                CONF_ROOM_SENSOR: sensor or "",
                CONF_ROOM_TARGET_DAY: float(DEFAULT_TARGET_DAY),
                CONF_ROOM_TARGET_NIGHT: float(DEFAULT_TARGET_NIGHT),
                CONF_ROOM_DAY_START: "",
                CONF_ROOM_NIGHT_START: "",
                CONF_ROOM_ENABLED: True,
            }

    return rooms


def _is_own_entity(hass: HomeAssistant, entity_id: str) -> bool:
    """True, wenn die Entity von dieser Integration selbst angelegt wurde."""
    entry = async_get_entity_registry(hass).async_get(entity_id)
    return entry is not None and entry.platform == DOMAIN


async def async_get_all_thermostats(hass: HomeAssistant) -> list[str]:
    # Eigene Raum-Climate-Entities nicht als Heizkörperventil anbieten.
    return sorted(
        entity_id
        for entity_id in hass.states.async_entity_ids(CLIMATE_DOMAIN)
        if not _is_own_entity(hass, entity_id)
    )


async def async_get_all_sensors(hass: HomeAssistant) -> list[str]:
    result: list[str] = []

    for entity_id in hass.states.async_entity_ids(SENSOR_DOMAIN):
        state = hass.states.get(entity_id)
        if state is None:
            continue

        device_class = state.attributes.get("device_class")
        if device_class == "temperature":
            result.append(entity_id)
            continue

        entity_id_lower = entity_id.lower()
        if (
            entity_id_lower.startswith("sensor.")
            and ("temp" in entity_id_lower or "temperature" in entity_id_lower)
            and _safe_float(state.state) is not None
        ):
            result.append(entity_id)

    return sorted(set(result))


def apply_room_config_update(
    hass: HomeAssistant,
    entry: ConfigEntry,
    room_id: str,
    updates: dict[str, Any],
) -> None:
    """Raumconfig-Felder setzen, speichern und Controller sofort auslösen.

    Gemeinsam genutzt von raumbasierten Switch- und Select-Entities, damit
    beide Entity-Typen denselben Update-/Persist-Ablauf verwenden.
    """
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if entry_data is None:
        _LOGGER.warning(
            "Kein Entry-Status für %s, Raumconfig kann nicht gesetzt werden",
            entry.entry_id,
        )
        return

    cfg = dict(entry_data["config"])
    rooms = dict(cfg.get(CONF_ROOMS, {}))
    room = dict(rooms.get(room_id, {}))
    room.update(updates)
    rooms[room_id] = room
    cfg[CONF_ROOMS] = rooms

    entry_data["config"] = cfg
    hass.config_entries.async_update_entry(entry, data=cfg)

    controller = entry_data.get(DATA_CONTROLLER)
    if controller is not None:
        controller.update_config(cfg)
        controller._evaluate()  # sofort reagieren

    state_cfg = dict(cfg)
    state_cfg.setdefault(DATA_ENABLED, DEFAULT_ENABLED)
    hass.states.async_set(
        f"{DOMAIN}.config",
        "active" if state_cfg.get(DATA_ENABLED, DEFAULT_ENABLED) else "disabled",
        attributes=state_cfg,
    )


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value

    return base
