"""Smart Heating Controller – Kernlogik."""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.const import ATTR_TEMPERATURE, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BOOST_DELTA,
    CONF_MAIN_SENSOR,
    CONF_MAIN_THERMOSTAT,
    CONF_MORNING_BOOST_END,
    CONF_MORNING_BOOST_START,
    CONF_NIGHT_START,
    CONF_ROOMS,
    CONF_ROOM_ENABLED,
    CONF_ROOM_SENSOR,
    CONF_ROOM_TARGET_DAY,
    CONF_ROOM_TARGET_NIGHT,
    CONF_ROOM_THERMOSTAT,
    CONF_TOLERANCE,
    DEFAULT_BOOST_DELTA,
    DEFAULT_MORNING_BOOST_END,
    DEFAULT_MORNING_BOOST_START,
    DEFAULT_NIGHT_START,
    DEFAULT_TARGET_DAY,
    DEFAULT_TARGET_NIGHT,
    DEFAULT_TOLERANCE,
)

_LOGGER = logging.getLogger(__name__)


class SmartHeatingController:
    """Kernlogik: Reagiert auf Sensorwerte und steuert Thermostate."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = config
        self._enabled = True
        self._unsub: list[Callable[[], None]] = []

    async def async_start(self) -> None:
        """Listener registrieren."""
        self._unsubscribe_all()

        if not self._enabled:
            return

        watch_entities: set[str] = set()

        main_thermostat = self._as_entity_id(self.config.get(CONF_MAIN_THERMOSTAT))
        main_sensor = self._as_entity_id(self.config.get(CONF_MAIN_SENSOR))

        if main_thermostat:
            watch_entities.add(main_thermostat)

        if main_sensor:
            watch_entities.add(main_sensor)

        for room in self._active_rooms().values():
            room_sensor = self._as_entity_id(room.get(CONF_ROOM_SENSOR))
            room_thermostat = self._as_entity_id(room.get(CONF_ROOM_THERMOSTAT))

            if room_sensor:
                watch_entities.add(room_sensor)

            if room_thermostat:
                watch_entities.add(room_thermostat)

        if watch_entities:
            self._unsub.append(
                async_track_state_change_event(
                    self.hass,
                    list(watch_entities),
                    self._on_state_change,
                )
            )

        self._unsub.append(
            async_track_time_change(
                self.hass,
                self._on_minute_tick,
                second=0,
            )
        )

        _LOGGER.debug("SmartHeatingController gestartet")
        self._evaluate()

    async def async_stop(self) -> None:
        """Controller stoppen."""
        self._unsubscribe_all()

    def set_enabled(self, enabled: bool) -> None:
        """Controller aktivieren / deaktivieren."""
        self._enabled = enabled

        if not enabled:
            self._unsubscribe_all()
            _LOGGER.info("Smart Heating Controller deaktiviert")
            return

        _LOGGER.info("Smart Heating Controller aktiviert")
        self.hass.async_create_task(self.async_start())

    def update_config(self, config: dict[str, Any]) -> None:
        """Neue Konfiguration übernehmen."""
        self.config = config

        if self._enabled:
            self.hass.async_create_task(self.async_start())

    def _unsubscribe_all(self) -> None:
        """Alle Listener entfernen."""
        for unsub in self._unsub:
            try:
                unsub()
            except Exception:
                _LOGGER.exception("Fehler beim Entfernen eines Listeners")

        self._unsub.clear()

    def _as_entity_id(self, value: Any) -> str | None:
        """Entity-ID validieren."""
        return value if isinstance(value, str) and value else None

    def _active_rooms(self) -> dict[str, dict[str, Any]]:
        """Aktive Räume zurückgeben."""
        rooms = self.config.get(CONF_ROOMS, {})
        if not isinstance(rooms, dict):
            return {}

        return {
            room_id: room
            for room_id, room in rooms.items()
            if isinstance(room, dict) and room.get(CONF_ROOM_ENABLED, True)
        }

    def _safe_float(self, value: Any) -> float | None:
        """Float robust parsen."""
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _get_state_float(self, entity_id: str | None) -> float | None:
        """State als float lesen."""
        if not entity_id:
            return None

        state = self.hass.states.get(entity_id)
        if not state:
            return None

        if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        return self._safe_float(state.state)

    def _get_attr_float(self, entity_id: str | None, attr: str) -> float | None:
        """Attribut als float lesen."""
        if not entity_id:
            return None

        state = self.hass.states.get(entity_id)
        if not state:
            return None

        return self._safe_float(state.attributes.get(attr))

    def _is_night(self) -> bool:
        """Nachtbetrieb aktiv?"""
        now = dt_util.now().strftime("%H:%M")

        night = str(self.config.get(CONF_NIGHT_START, DEFAULT_NIGHT_START))[:5]
        boost_start = str(
            self.config.get(CONF_MORNING_BOOST_START, DEFAULT_MORNING_BOOST_START)
        )[:5]

        if night > boost_start:
            return now >= night or now < boost_start

        return night <= now < boost_start

    def _in_morning_boost_window(self) -> bool:
        """Morgen-Boost-Fenster aktiv?"""
        now = dt_util.now().strftime("%H:%M")

        start = str(
            self.config.get(CONF_MORNING_BOOST_START, DEFAULT_MORNING_BOOST_START)
        )[:5]
        end = str(
            self.config.get(CONF_MORNING_BOOST_END, DEFAULT_MORNING_BOOST_END)
        )[:5]

        if start <= end:
            return start <= now < end

        return now >= start or now < end

    def _room_temp(self, room: dict[str, Any]) -> float | None:
        """Raumtemperatur lesen."""
        return self._get_state_float(self._as_entity_id(room.get(CONF_ROOM_SENSOR)))

    def _base_target_for_room(self, room: dict[str, Any]) -> float:
        """Basis-Solltemperatur eines Raums."""
        if self._is_night():
            return float(room.get(CONF_ROOM_TARGET_NIGHT, DEFAULT_TARGET_NIGHT))
        return float(room.get(CONF_ROOM_TARGET_DAY, DEFAULT_TARGET_DAY))

    def _main_reference_temp(self) -> float | None:
        """Referenztemperatur für Hauptthermostat."""
        main_sensor = self._as_entity_id(self.config.get(CONF_MAIN_SENSOR))
        if main_sensor:
            value = self._get_state_float(main_sensor)
            if value is not None:
                return value

        main_thermostat = self._as_entity_id(self.config.get(CONF_MAIN_THERMOSTAT))
        if main_thermostat:
            return self._get_attr_float(main_thermostat, "current_temperature")

        return None

    def _thermostat_min_temp(self, entity_id: str) -> float:
        """Minimale Temperatur eines Thermostats."""
        state = self.hass.states.get(entity_id)
        if state:
            min_temp = self._safe_float(state.attributes.get("min_temp"))
            if min_temp is not None:
                return min_temp

        return 5.0

    def _set_temp_if_new(self, entity_id: str, temp: float) -> None:
        """Temperatur nur setzen, wenn Änderung nötig ist."""
        current = self._get_attr_float(entity_id, ATTR_TEMPERATURE)

        rounded = round(float(temp), 1)

        if current is not None and abs(current - rounded) < 0.1:
            return

        _LOGGER.debug("Setze %s auf %.1f °C", entity_id, rounded)

        self.hass.async_create_task(
            self.hass.services.async_call(
                CLIMATE_DOMAIN,
                "set_temperature",
                {
                    "entity_id": entity_id,
                    ATTR_TEMPERATURE: rounded,
                },
                blocking=True,
            )
        )

    def _evaluate(self) -> None:
        """Heizbedarf berechnen und Thermostate setzen."""
        if not self._enabled:
            return

        rooms = self._active_rooms()
        if not rooms:
            return

        boost_delta = self._safe_float(
            self.config.get(CONF_BOOST_DELTA, DEFAULT_BOOST_DELTA)
        )
        tolerance = self._safe_float(
            self.config.get(CONF_TOLERANCE, DEFAULT_TOLERANCE)
        )

        if boost_delta is None:
            boost_delta = float(DEFAULT_BOOST_DELTA)
        if tolerance is None:
            tolerance = float(DEFAULT_TOLERANCE)

        room_states: dict[str, dict[str, Any]] = {}

        for room_id, room in rooms.items():
            actual = self._room_temp(room)
            target = self._base_target_for_room(room)

            needs_heat = actual is not None and actual < (target - tolerance)
            reached_target = actual is not None and actual >= target

            room_states[room_id] = {
                "actual": actual,
                "target": target,
                "needs_heat": needs_heat,
                "reached_target": reached_target,
            }

            _LOGGER.debug(
                "Raum %s: ist=%s ziel=%.1f needs_heat=%s reached_target=%s",
                room_id,
                f"{actual:.2f}" if actual is not None else "n/a",
                target,
                needs_heat,
                reached_target,
            )

        any_room_needs_heat = any(
            room_state["needs_heat"] for room_state in room_states.values()
        )

        # Hauptthermostat:
        # Sobald irgendein Raum Wärme braucht, muss das Hauptthermostat heizen.
        main_thermostat = self._as_entity_id(self.config.get(CONF_MAIN_THERMOSTAT))
        if main_thermostat:
            main_base_target = max(
                room_state["target"] for room_state in room_states.values()
            )

            main_target = main_base_target

            if any_room_needs_heat:
                # Optional morgens etwas extra pushen
                if self._in_morning_boost_window():
                    main_target = main_base_target + boost_delta
                else:
                    # Auch tagsüber muss das Hauptthermostat hoch genug sein,
                    # damit überhaupt Wärme erzeugt wird.
                    main_target = main_base_target + boost_delta

            self._set_temp_if_new(main_thermostat, main_target)

        # Raumthermostate:
        # - Bedarf: öffnen / boosten
        # - Ziel erreicht oder überschritten: stark absenken
        # - Dazwischen: auf Basisziel halten
        for room_id, room in rooms.items():
            thermostat = self._as_entity_id(room.get(CONF_ROOM_THERMOSTAT))
            if not thermostat:
                continue

            room_state = room_states[room_id]
            target = room_state["target"]
            needs_heat = room_state["needs_heat"]
            reached_target = room_state["reached_target"]

            if needs_heat:
                room_target = target + boost_delta
            elif reached_target:
                room_target = self._thermostat_min_temp(thermostat)
            else:
                room_target = target

            self._set_temp_if_new(thermostat, room_target)

    @callback
    def _on_state_change(self, event: Event) -> None:
        """State-Änderung."""
        self._evaluate()

    @callback
    def _on_minute_tick(self, now) -> None:
        """Minütlicher Check."""
        self._evaluate()
