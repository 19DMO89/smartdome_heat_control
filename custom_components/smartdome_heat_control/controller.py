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
    CONF_AWAY_ENABLED,
    CONF_BOOST_DELTA,
    CONF_HEATING_MODE,
    CONF_MAIN_SENSOR,
    CONF_MAIN_THERMOSTAT,
    CONF_MORNING_BOOST_END,
    CONF_MORNING_BOOST_START,
    CONF_NIGHT_START,
    CONF_ROOMS,
    CONF_ROOM_AWAY_TEMPERATURE,
    CONF_ROOM_CYCLE_PEAK_TEMP,
    CONF_ROOM_CYCLE_TARGET_TEMP,
    CONF_ROOM_DAY_START,
    CONF_ROOM_ENABLED,
    CONF_ROOM_HEATING_CYCLE_ACTIVE,
    CONF_ROOM_LEARNED_OVERSHOOT,
    CONF_ROOM_NIGHT_START,
    CONF_ROOM_SENSOR,
    CONF_ROOM_TARGET_DAY,
    CONF_ROOM_TARGET_NIGHT,
    CONF_ROOM_THERMOSTAT,
    CONF_ROOM_WINDOW_SENSOR,
    CONF_TOLERANCE,
    CONF_VACATION_ENABLED,
    CONF_VACATION_TEMPERATURE,
    CONF_WINDOW_CLOSE_DELAY,
    CONF_WINDOW_OPEN_DELAY,
    DEFAULT_ADAPTIVE_OVERSHOOT,
    DEFAULT_AWAY_ENABLED,
    DEFAULT_BOOST_DELTA,
    DEFAULT_HEATING_MODE,
    DEFAULT_MORNING_BOOST_END,
    DEFAULT_MORNING_BOOST_START,
    DEFAULT_NIGHT_START,
    DEFAULT_ROOM_AWAY_TEMPERATURE,
    DEFAULT_TARGET_DAY,
    DEFAULT_TARGET_NIGHT,
    DEFAULT_TOLERANCE,
    DEFAULT_VACATION_ENABLED,
    DEFAULT_VACATION_TEMPERATURE,
    DEFAULT_WINDOW_CLOSE_DELAY,
    DEFAULT_WINDOW_OPEN_DELAY,
    HEATING_MODE_ADAPTIVE,
    HEATING_MODE_BALANCED,
    HEATING_MODE_COMFORT,
    HEATING_MODE_ENERGY,
    MAX_ADAPTIVE_OVERSHOOT,
    MIN_ADAPTIVE_OVERSHOOT,
)

_LOGGER = logging.getLogger(__name__)


class SmartHeatingController:
    """Kernlogik: Reagiert auf Sensorwerte und steuert Thermostate."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = config
        self._window_open_since: dict[str, float] = {}
        self._window_closed_since: dict[str, float] = {}
        self._window_paused_rooms: set[str] = set()
        self._enabled = True
        self._unsub: list[Callable[[], None]] = []
        self._apply_config_defaults()

    async def async_start(self) -> None:
        """Listener registrieren."""
        self._unsubscribe_all()

        if not self._enabled:
            return

        self._apply_config_defaults()

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
            room_window_sensor = self._as_entity_id(room.get(CONF_ROOM_WINDOW_SENSOR))

            if room_sensor:
                watch_entities.add(room_sensor)
            if room_thermostat:
                watch_entities.add(room_thermostat)
            if room_window_sensor:
                watch_entities.add(room_window_sensor)

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

        self._evaluate()

    async def async_stop(self) -> None:
        """Listener entfernen."""
        self._unsubscribe_all()

    def set_enabled(self, enabled: bool) -> None:
        """Controller aktivieren/deaktivieren."""
        self._enabled = enabled
        if not enabled:
            self._unsubscribe_all()
            return
        self.hass.async_create_task(self.async_start())

    def update_config(self, config: dict[str, Any]) -> None:
        """Config aktualisieren."""
        self.config = config
        self._apply_config_defaults()
        if self._enabled:
            self.hass.async_create_task(self.async_start())

    def _apply_config_defaults(self) -> None:
        """Fehlende Werte für alte Konfigurationen ergänzen."""
        self.config.setdefault(CONF_VACATION_ENABLED, DEFAULT_VACATION_ENABLED)
        self.config.setdefault(CONF_VACATION_TEMPERATURE, DEFAULT_VACATION_TEMPERATURE)
        self.config.setdefault(CONF_AWAY_ENABLED, DEFAULT_AWAY_ENABLED)
        self.config.setdefault(CONF_HEATING_MODE, DEFAULT_HEATING_MODE)
        self.config.setdefault(CONF_WINDOW_OPEN_DELAY, DEFAULT_WINDOW_OPEN_DELAY)
        self.config.setdefault(CONF_WINDOW_CLOSE_DELAY, DEFAULT_WINDOW_CLOSE_DELAY)

        rooms = self.config.get(CONF_ROOMS, {})
        if isinstance(rooms, dict):
            for room in rooms.values():
                if isinstance(room, dict):
                    room.setdefault(CONF_ROOM_AWAY_TEMPERATURE, DEFAULT_ROOM_AWAY_TEMPERATURE)
                    room.setdefault(CONF_ROOM_WINDOW_SENSOR, "")
                    room.setdefault(
                        CONF_ROOM_LEARNED_OVERSHOOT,
                        DEFAULT_ADAPTIVE_OVERSHOOT,
                    )
                    room.setdefault(CONF_ROOM_HEATING_CYCLE_ACTIVE, False)
                    room.setdefault(CONF_ROOM_CYCLE_TARGET_TEMP, None)
                    room.setdefault(CONF_ROOM_CYCLE_PEAK_TEMP, None)

    def _unsubscribe_all(self) -> None:
        """Alle Listener entfernen."""
        for unsub in self._unsub:
            try:
                unsub()
            except Exception:
                _LOGGER.exception("Fehler beim Entfernen eines Listeners")
        self._unsub.clear()

    def _as_entity_id(self, value: Any) -> str | None:
        """String als Entity-ID zurückgeben oder None."""
        return value if isinstance(value, str) and value else None

    def _active_rooms(self) -> dict[str, dict[str, Any]]:
        """Nur aktive Räume zurückgeben."""
        rooms = self.config.get(CONF_ROOMS, {})
        if not isinstance(rooms, dict):
            return {}
        return {
            room_id: room
            for room_id, room in rooms.items()
            if isinstance(room, dict) and room.get(CONF_ROOM_ENABLED, True)
        }

    def _safe_float(self, value: Any) -> float | None:
        """Beliebigen Wert sicher in float umwandeln."""
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _get_state_float(self, entity_id: str | None) -> float | None:
        """Numerischen Zustand einer Entity lesen."""
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if not state or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        return self._safe_float(state.state)

    def _get_attr_float(self, entity_id: str | None, attr: str) -> float | None:
        """Numerisches Attribut einer Entity lesen."""
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if not state:
            return None
        return self._safe_float(state.attributes.get(attr))

    def _room_temp(self, room: dict[str, Any]) -> float | None:
        return self._get_state_float(self._as_entity_id(room.get(CONF_ROOM_SENSOR)))

    def _window_pause_active(self, room_id: str, room: dict[str, Any]) -> bool:
        """Fensterlogik mit Delay."""
        sensor = self._as_entity_id(room.get(CONF_ROOM_WINDOW_SENSOR))
        if not sensor:
            return False

        state = self.hass.states.get(sensor)
        if not state:
            return False

        now = dt_util.now().timestamp()
        open_delay = int(
            self.config.get(CONF_WINDOW_OPEN_DELAY, DEFAULT_WINDOW_OPEN_DELAY)
        )
        close_delay = int(
            self.config.get(CONF_WINDOW_CLOSE_DELAY, DEFAULT_WINDOW_CLOSE_DELAY)
        )

        raw = str(state.state).lower()
        window_open = raw in {"on", "open", "true"}

        if window_open:
            self._window_closed_since.pop(room_id, None)

            if room_id not in self._window_open_since:
                self._window_open_since[room_id] = now
                return False

            if now - self._window_open_since[room_id] >= open_delay:
                self._window_paused_rooms.add(room_id)
                return True

            return False

        self._window_open_since.pop(room_id, None)

        if room_id in self._window_paused_rooms:
            if room_id not in self._window_closed_since:
                self._window_closed_since[room_id] = now
                return True

            if now - self._window_closed_since[room_id] >= close_delay:
                self._window_paused_rooms.discard(room_id)
                self._window_closed_since.pop(room_id, None)
                return False

            return True

        return False

    def _time_hhmm(self) -> str:
        """Aktuelle Uhrzeit als HH:MM."""
        return dt_util.now().strftime("%H:%M")

    def _is_night_for_room(self, room: dict[str, Any]) -> bool:
        """Raumbezogene Tag-/Nacht-Zeit prüfen."""
        now = self._time_hhmm()

        room_night_start = str(
            room.get(
                CONF_ROOM_NIGHT_START,
                self.config.get(CONF_NIGHT_START, DEFAULT_NIGHT_START),
            )
        )[:5]

        room_day_start = str(
            room.get(
                CONF_ROOM_DAY_START,
                self.config.get(
                    CONF_MORNING_BOOST_START,
                    DEFAULT_MORNING_BOOST_START,
                ),
            )
        )[:5]

        if room_night_start > room_day_start:
            return now >= room_night_start or now < room_day_start

        return room_night_start <= now < room_day_start

    def _base_target_for_room(self, room: dict[str, Any]) -> float:
        """Normale Tag-/Nacht-Solltemperatur."""
        if self._is_night_for_room(room):
            return float(room.get(CONF_ROOM_TARGET_NIGHT, DEFAULT_TARGET_NIGHT))
        return float(room.get(CONF_ROOM_TARGET_DAY, DEFAULT_TARGET_DAY))

    def _effective_target_for_room(self, room: dict[str, Any]) -> float:
        """Ermittelt die gültige Zieltemperatur.

        Priorität:
        1. Urlaub
        2. Away / Nicht Zuhause
        3. Normale Tag-/Nacht-Logik
        """
        vacation_enabled = bool(
            self.config.get(CONF_VACATION_ENABLED, DEFAULT_VACATION_ENABLED)
        )
        away_enabled = bool(self.config.get(CONF_AWAY_ENABLED, DEFAULT_AWAY_ENABLED))

        if vacation_enabled:
            vacation_temp = self._safe_float(
                self.config.get(
                    CONF_VACATION_TEMPERATURE,
                    DEFAULT_VACATION_TEMPERATURE,
                )
            )
            if vacation_temp is not None:
                return vacation_temp
            return float(DEFAULT_VACATION_TEMPERATURE)

        if away_enabled:
            away_temp = self._safe_float(
                room.get(
                    CONF_ROOM_AWAY_TEMPERATURE,
                    DEFAULT_ROOM_AWAY_TEMPERATURE,
                )
            )
            if away_temp is not None:
                return away_temp
            return float(DEFAULT_ROOM_AWAY_TEMPERATURE)

        return self._base_target_for_room(room)

    def _is_window_open(self, room: dict[str, Any]) -> bool:
        """Prüfen, ob das Fenster im Raum offen ist."""
        entity_id = self._as_entity_id(room.get(CONF_ROOM_WINDOW_SENSOR))
        if not entity_id:
            return False

        state = self.hass.states.get(entity_id)
        if not state:
            return False

        raw = str(state.state).lower()
        return raw in {"on", "open", "true"}

    def _main_reference_temp(self) -> float | None:
        """Referenztemperatur am Hauptthermostat lesen."""
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
        """Minimale Solltemperatur eines Thermostats lesen."""
        state = self.hass.states.get(entity_id)
        if state:
            min_temp = self._safe_float(state.attributes.get("min_temp"))
            if min_temp is not None:
                return min_temp
        return 5.0

    def _in_morning_boost_window(self) -> bool:
        """Prüfen, ob wir im Morgen-Boost-Fenster sind."""
        now = self._time_hhmm()
        start = str(
            self.config.get(CONF_MORNING_BOOST_START, DEFAULT_MORNING_BOOST_START)
        )[:5]
        end = str(
            self.config.get(CONF_MORNING_BOOST_END, DEFAULT_MORNING_BOOST_END)
        )[:5]

        if start <= end:
            return start <= now < end
        return now >= start or now < end

    def _set_temp_if_new(self, entity_id: str, temp: float) -> None:
        """Solltemperatur nur setzen, wenn sie sich wirklich geändert hat."""
        current = self._get_attr_float(entity_id, ATTR_TEMPERATURE)
        rounded = round(float(temp), 1)

        if current is not None and abs(current - rounded) < 0.1:
            return

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

    def _get_heating_mode(self) -> str:
        """Aktuellen Heizmodus lesen."""
        return str(self.config.get(CONF_HEATING_MODE, DEFAULT_HEATING_MODE))

    def _get_room_min_temp(self, room: dict[str, Any], thermostat_id: str) -> float:
        """Minimale Zieltemperatur für inaktive Räume."""
        thermostat_min = self._thermostat_min_temp(thermostat_id)
        room_night = self._safe_float(room.get(CONF_ROOM_TARGET_NIGHT, DEFAULT_TARGET_NIGHT))
        if room_night is None:
            room_night = float(DEFAULT_TARGET_NIGHT)
        return min(thermostat_min, room_night)

    def _get_idle_target_for_room(
        self,
        room: dict[str, Any],
        thermostat_id: str,
        target_temp: float,
    ) -> float:
        """Zieltemperatur für Räume ohne akuten Heizbedarf je nach Modus."""
        mode = self._get_heating_mode()
        min_temp = self._get_room_min_temp(room, thermostat_id)

        if mode == HEATING_MODE_COMFORT:
            return max(min_temp, target_temp)

        if mode == HEATING_MODE_BALANCED:
            return max(min_temp, target_temp - 0.5)

        if mode == HEATING_MODE_ENERGY:
            return min_temp

        if mode == HEATING_MODE_ADAPTIVE:
            learned = float(
                room.get(CONF_ROOM_LEARNED_OVERSHOOT, DEFAULT_ADAPTIVE_OVERSHOOT)
            )
            learned = max(MIN_ADAPTIVE_OVERSHOOT, min(MAX_ADAPTIVE_OVERSHOOT, learned))
            return max(min_temp, target_temp - learned)

        return max(min_temp, target_temp - 0.5)

    def _start_room_heating_cycle(
        self,
        room: dict[str, Any],
        target_temp: float,
        current_temp: float | None,
    ) -> None:
        """Heizzyklus für Lernlogik starten oder fortführen."""
        if current_temp is None:
            return

        if room.get(CONF_ROOM_HEATING_CYCLE_ACTIVE):
            peak = room.get(CONF_ROOM_CYCLE_PEAK_TEMP)
            if peak is None or current_temp > peak:
                room[CONF_ROOM_CYCLE_PEAK_TEMP] = current_temp
            return

        room[CONF_ROOM_HEATING_CYCLE_ACTIVE] = True
        room[CONF_ROOM_CYCLE_TARGET_TEMP] = target_temp
        room[CONF_ROOM_CYCLE_PEAK_TEMP] = current_temp

    def _update_room_cycle_peak(
        self,
        room: dict[str, Any],
        current_temp: float | None,
    ) -> None:
        """Maximale Temperatur während/kurz nach Heizphase nachführen."""
        if current_temp is None:
            return

        if not room.get(CONF_ROOM_HEATING_CYCLE_ACTIVE):
            return

        peak = room.get(CONF_ROOM_CYCLE_PEAK_TEMP)
        if peak is None or current_temp > peak:
            room[CONF_ROOM_CYCLE_PEAK_TEMP] = current_temp

    def _finish_room_heating_cycle(self, room: dict[str, Any]) -> None:
        """Overshoot berechnen und gelernt abspeichern."""
        if not room.get(CONF_ROOM_HEATING_CYCLE_ACTIVE):
            return

        target = room.get(CONF_ROOM_CYCLE_TARGET_TEMP)
        peak = room.get(CONF_ROOM_CYCLE_PEAK_TEMP)

        if target is not None and peak is not None:
            overshoot = max(0.0, float(peak) - float(target))
            old_value = float(
                room.get(CONF_ROOM_LEARNED_OVERSHOOT, DEFAULT_ADAPTIVE_OVERSHOOT)
            )
            new_value = (old_value * 0.7) + (overshoot * 0.3)
            new_value = max(MIN_ADAPTIVE_OVERSHOOT, min(MAX_ADAPTIVE_OVERSHOOT, new_value))
            room[CONF_ROOM_LEARNED_OVERSHOOT] = round(new_value, 2)

        room[CONF_ROOM_HEATING_CYCLE_ACTIVE] = False
        room[CONF_ROOM_CYCLE_TARGET_TEMP] = None
        room[CONF_ROOM_CYCLE_PEAK_TEMP] = None

    def _evaluate(self) -> None:
        """Heizlogik auswerten."""
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
            target = self._effective_target_for_room(room)
            window_open = self._window_pause_active(room_id, room)

            needs_heat = (
                not window_open
                and actual is not None
                and actual < (target - tolerance)
            )
            reached_target = actual is not None and actual >= target

            room_states[room_id] = {
                "actual": actual,
                "target": target,
                "needs_heat": needs_heat,
                "reached_target": reached_target,
                "window_open": window_open,
            }

            if needs_heat:
                self._start_room_heating_cycle(room, target, actual)
            else:
                self._update_room_cycle_peak(room, actual)
                if room.get(CONF_ROOM_HEATING_CYCLE_ACTIVE):
                    self._finish_room_heating_cycle(room)

        any_room_needs_heat = any(
            room_state["needs_heat"] for room_state in room_states.values()
        )

        main_thermostat = self._as_entity_id(self.config.get(CONF_MAIN_THERMOSTAT))
        if main_thermostat:
            main_base_target = max(
                room_state["target"] for room_state in room_states.values()
            )
            main_target = (
                main_base_target + boost_delta
                if any_room_needs_heat
                else main_base_target
            )
            self._set_temp_if_new(main_thermostat, main_target)

        for room_id, room in rooms.items():
            thermostat = self._as_entity_id(room.get(CONF_ROOM_THERMOSTAT))
            if not thermostat:
                continue

            room_state = room_states[room_id]
            target = room_state["target"]

            if room_state["window_open"]:
                room_target = self._thermostat_min_temp(thermostat)
            elif room_state["needs_heat"]:
                room_target = target + boost_delta
            elif room_state["reached_target"]:
                room_target = self._get_idle_target_for_room(
                    room,
                    thermostat,
                    target,
                )
            else:
                room_target = target

            self._set_temp_if_new(thermostat, room_target)

    @callback
    def _on_state_change(self, event: Event) -> None:
        """Bei State-Änderung sofort neu bewerten."""
        self._evaluate()

    @callback
    def _on_minute_tick(self, now) -> None:
        """Zyklische Auswertung jede Minute."""
        self._evaluate()
