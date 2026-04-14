"""Smart Heating Controller – Kernlogik."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_TEMPERATURE, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.util import dt as dt_util

from .const import (
    ADAPTIVE_BUCKET_MEDIUM_MAX_SECS,
    ADAPTIVE_BUCKET_SHORT_MAX_SECS,
    CONF_AWAY_ENABLED,
    CONF_BOOST_DELTA,
    CONF_OUTDOOR_SENSOR,
    CONF_OUTDOOR_TEMP_CUTOFF,
    CONF_OUTDOOR_TEMP_CUTOFF_ENABLED,
    DEFAULT_OUTDOOR_TEMP_CUTOFF,
    DEFAULT_OUTDOOR_TEMP_CUTOFF_ENABLED,
    CONF_CIRCUIT_CONTROL_TYPE,
    CONF_CIRCUIT_ENABLED,
    CONF_CIRCUIT_LABEL,
    CONF_CIRCUIT_MAIN_SENSOR,
    CONF_CIRCUIT_MAIN_SWITCH,
    CONF_CIRCUIT_MAIN_THERMOSTAT,
    CONF_CIRCUITS,
    CONF_MAIN_CONTROL_TYPE,
    CONF_MAIN_SWITCH,
    CONTROL_TYPE_SWITCH,
    CONF_ENERGY_RESIDUAL_HEAT_HOLD,
    CONF_HEATING_MODE,
    CONF_MAIN_SENSOR,
    CONF_MAIN_THERMOSTAT,
    CONF_ROOM_CIRCUIT_ID,
    CONF_ROOM_HEATING_MODE,
    CONF_MORNING_BOOST_START,
    CONF_NIGHT_START,
    CONF_ROOMS,
    CONF_ROOM_AWAY_TEMPERATURE,
    CONF_ROOM_CONTROL_PROFILE,
    CONF_ROOM_THERMOSTAT_OFFSET,
    CONF_ROOM_CYCLE_PEAK_TEMP,
    CONF_ROOM_CYCLE_PEAKED,
    CONF_ROOM_CYCLE_START_TS,
    CONF_ROOM_CYCLE_TARGET_TEMP,
    CONF_ROOM_DAY_START,
    CONF_ROOM_ENABLED,
    CONF_ROOM_NIGHT_SETBACK_ENABLED,
    CONF_ROOM_HEATING_CYCLE_ACTIVE,
    CONF_ROOM_LEARNED_OVERSHOOT,
    CONF_ROOM_LEARNED_OVERSHOOT_LONG,
    CONF_ROOM_LEARNED_OVERSHOOT_MEDIUM,
    CONF_ROOM_LEARNED_OVERSHOOT_SHORT,
    CONF_ROOM_NIGHT_START,
    CONF_ROOM_SENSOR,
    CONF_ROOM_TARGET_DAY,
    CONF_ROOM_TARGET_NIGHT,
    CONF_ROOM_THERMOSTAT,
    CONF_ROOM_WEEKLY_SCHEDULE,
    CONF_ROOM_WINDOW_SENSOR,
    CONF_ROOM_WINDOW_SENSORS,
    CONF_TOLERANCE,
    CONF_VACATION_ENABLED,
    CONF_VACATION_TEMPERATURE,
    CONF_WINDOW_CLOSE_DELAY,
    CONF_WINDOW_OPEN_DELAY,
    CONTROL_PROFILE_SELF_REGULATING,
    CONTROL_PROFILE_STANDARD,
    DEFAULT_ADAPTIVE_OVERSHOOT,
    DEFAULT_ADAPTIVE_OVERSHOOT_LONG,
    DEFAULT_ADAPTIVE_OVERSHOOT_MEDIUM,
    DEFAULT_ADAPTIVE_OVERSHOOT_SHORT,
    DEFAULT_AWAY_ENABLED,
    DEFAULT_BOOST_DELTA,
    DEFAULT_ENERGY_RESIDUAL_HEAT_HOLD,
    DEFAULT_HEATING_MODE,
    DEFAULT_MORNING_BOOST_START,
    DEFAULT_NIGHT_START,
    DEFAULT_ROOM_AWAY_TEMPERATURE,
    DEFAULT_ROOM_CONTROL_PROFILE,
    DEFAULT_ROOM_THERMOSTAT_OFFSET,
    DEFAULT_ROOM_WEEKLY_SCHEDULE,
    DEFAULT_TARGET_DAY,
    DEFAULT_TARGET_NIGHT,
    DEFAULT_TOLERANCE,
    DEFAULT_VACATION_ENABLED,
    DEFAULT_VACATION_TEMPERATURE,
    DEFAULT_WINDOW_CLOSE_DELAY,
    DEFAULT_WINDOW_OPEN_DELAY,
    CONF_ROOM_CLIMATE_ENTITY,
    CONF_ROOM_USE_CLIMATE,
    CONF_COOLING_ENABLED,
    CONF_COOLING_AUTO,
    CONF_COOLING_THRESHOLD,
    DEFAULT_COOLING_ENABLED,
    DEFAULT_COOLING_AUTO,
    DEFAULT_COOLING_THRESHOLD,
    CONF_ROOM_COOL_TARGET_DAY,
    CONF_ROOM_COOL_TARGET_NIGHT,
    CONF_ROOM_CLIMATE_FAN_MODE,
    CONF_ROOM_CLIMATE_PRESET,
    CONF_ROOM_CLIMATE_HVAC_MODE,
    DEFAULT_ROOM_COOL_TARGET_DAY,
    DEFAULT_ROOM_COOL_TARGET_NIGHT,
    DEFAULT_ROOM_CLIMATE_FAN_MODE,
    DEFAULT_ROOM_CLIMATE_PRESET,
    DEFAULT_ROOM_CLIMATE_HVAC_MODE,
)

_LOGGER = logging.getLogger(__name__)

HEATING_MODE_COMFORT = "comfort"
HEATING_MODE_BALANCED = "balanced"
HEATING_MODE_ENERGY = "energy"
HEATING_MODE_ADAPTIVE = "adaptive"

ROOM_STATE_IDLE = "idle"
ROOM_STATE_HEATING = "heating"
ROOM_STATE_RESIDUAL_HOLD = "residual_hold"
ROOM_STATE_WINDOW_PAUSE = "window_pause"


class SmartHeatingController:
    """Kernlogik: Reagiert auf Sensorwerte und steuert Thermostate."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = config
        self._persist_callback: Any = None
        self._state_callback: Any = None
        self._window_open_since: dict[str, float] = {}
        self._window_closed_since: dict[str, float] = {}
        self._window_paused_rooms: set[str] = set()
        self._enabled = True
        self._unsub: list[Callable[[], None]] = []

        # Zuletzt wirklich gesendeter Zielwert pro Thermostat
        self._desired_targets: dict[str, float] = {}

        # Zuletzt berechneter Zielwert pro Thermostat
        self._last_computed_targets: dict[str, float] = {}

        # Raumzustände
        self._room_state: dict[str, str] = {}
        self._residual_heat_hold_until: dict[str, float] = {}

        # Letzte echte Schreibzeit pro Thermostat
        self._last_command_sent_at: dict[str, float] = {}

        # Zuletzt wirklich angewendeter effektiver Zustand pro Raum
        self._last_applied_room_state: dict[str, str] = {}

        # Ob der Heizkreis-Hauptthermostat im letzten Zyklus aktiv war
        # (True = mind. ein Raum heizte). Wird genutzt um beim Übergang
        # heating→idle einen garantierten min_temp-Befehl zu senden.
        self._circuit_heating_active: dict[str, bool] = {}

        # Zuletzt gesendeter HVAC-/Fan-/Preset-Modus pro Climate-Entity
        self._last_hvac_mode: dict[str, str] = {}
        self._last_fan_mode: dict[str, str] = {}
        self._last_preset_mode: dict[str, str] = {}

        self._apply_config_defaults()

    async def async_start(self) -> None:
        """Listener registrieren.

        Wichtig:
        Es werden nur Sensoren beobachtet, nicht die Thermostate selbst.
        """
        self._unsubscribe_all()

        if not self._enabled:
            return

        self._apply_config_defaults()

        watch_entities: set[str] = set()

        main_sensor = self._as_entity_id(self.config.get(CONF_MAIN_SENSOR))
        if main_sensor:
            watch_entities.add(main_sensor)

        if bool(self.config.get(CONF_OUTDOOR_TEMP_CUTOFF_ENABLED, False)):
            outdoor_sensor = self._as_entity_id(self.config.get(CONF_OUTDOOR_SENSOR))
            if outdoor_sensor:
                watch_entities.add(outdoor_sensor)

        for circuit in self.config.get(CONF_CIRCUITS, {}).values():
            if isinstance(circuit, dict):
                circuit_sensor = self._as_entity_id(circuit.get(CONF_CIRCUIT_MAIN_SENSOR))
                if circuit_sensor:
                    watch_entities.add(circuit_sensor)

        for room in self._active_rooms().values():
            room_sensor = self._as_entity_id(room.get(CONF_ROOM_SENSOR))
            if room_sensor:
                watch_entities.add(room_sensor)

            for ws in room.get(CONF_ROOM_WINDOW_SENSORS, []):
                ws_id = self._as_entity_id(ws)
                if ws_id:
                    watch_entities.add(ws_id)

            # Bei selbst regelnden Räumen auch den Thermostat beobachten,
            # damit _evaluate() greift sobald die CCU den State bestätigt.
            if self._is_self_regulating_room(room):
                thermostat = self._as_entity_id(room.get(CONF_ROOM_THERMOSTAT))
                if thermostat:
                    watch_entities.add(thermostat)

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
            self._reset_runtime_states()
            self._restore_non_boost_targets()
            self._unsubscribe_all()
            return

        self.hass.async_create_task(self.async_start())

    def update_config(self, config: dict[str, Any]) -> None:
        """Config aktualisieren."""
        rooms = config.get("rooms", {})
        _LOGGER.warning(
            "[Smartdome Diagnose] UPDATE_CONFIG: Controller erhält neue Config. "
            "Räume: %s | heating_mode: %s | enabled: %s",
            {rid: r.get("label", rid) for rid, r in rooms.items()},
            config.get("heating_mode"),
            config.get("enabled"),
        )
        self.config = config
        self._apply_config_defaults()
        self._reset_runtime_states()
        self._window_open_since.clear()
        self._window_closed_since.clear()
        self._window_paused_rooms.clear()

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
        self.config.setdefault(
            CONF_OUTDOOR_TEMP_CUTOFF_ENABLED, DEFAULT_OUTDOOR_TEMP_CUTOFF_ENABLED
        )
        self.config.setdefault(CONF_OUTDOOR_TEMP_CUTOFF, DEFAULT_OUTDOOR_TEMP_CUTOFF)
        self.config.setdefault(
            CONF_ENERGY_RESIDUAL_HEAT_HOLD,
            DEFAULT_ENERGY_RESIDUAL_HEAT_HOLD,
        )

        rooms = self.config.get(CONF_ROOMS, {})
        if isinstance(rooms, dict):
            for room in rooms.values():
                if isinstance(room, dict):
                    room.setdefault(
                        CONF_ROOM_AWAY_TEMPERATURE,
                        DEFAULT_ROOM_AWAY_TEMPERATURE,
                    )
                    room.setdefault(CONF_ROOM_WINDOW_SENSOR, "")
                    room.setdefault(
                        CONF_ROOM_CONTROL_PROFILE,
                        DEFAULT_ROOM_CONTROL_PROFILE,
                    )
                    room.setdefault(
                        CONF_ROOM_WEEKLY_SCHEDULE,
                        DEFAULT_ROOM_WEEKLY_SCHEDULE,
                    )
                    room.setdefault(
                        CONF_ROOM_LEARNED_OVERSHOOT,
                        DEFAULT_ADAPTIVE_OVERSHOOT,
                    )
                    room.setdefault(
                        CONF_ROOM_LEARNED_OVERSHOOT_SHORT,
                        DEFAULT_ADAPTIVE_OVERSHOOT_SHORT,
                    )
                    room.setdefault(
                        CONF_ROOM_LEARNED_OVERSHOOT_MEDIUM,
                        DEFAULT_ADAPTIVE_OVERSHOOT_MEDIUM,
                    )
                    room.setdefault(
                        CONF_ROOM_LEARNED_OVERSHOOT_LONG,
                        DEFAULT_ADAPTIVE_OVERSHOOT_LONG,
                    )
                    room.setdefault(CONF_ROOM_HEATING_CYCLE_ACTIVE, False)
                    room.setdefault(CONF_ROOM_CYCLE_TARGET_TEMP, None)
                    room.setdefault(CONF_ROOM_CYCLE_PEAK_TEMP, None)
                    room.setdefault(CONF_ROOM_CYCLE_START_TS, None)
                    room.setdefault(CONF_ROOM_CYCLE_PEAKED, False)

    def _unsubscribe_all(self) -> None:
        """Alle Listener entfernen."""
        for unsub in self._unsub:
            try:
                unsub()
            except Exception:
                _LOGGER.exception("Fehler beim Entfernen eines Listeners")
        self._unsub.clear()

    def set_persist_callback(self, callback: Any) -> None:
        """Callback setzen der nach dem Lernen die Config persistiert."""
        self._persist_callback = callback

    def set_state_callback(self, callback: Any) -> None:
        """Callback setzen der nach jeder Auswertung den Raumzustand publiziert."""
        self._state_callback = callback

    def _persist_learned_values(self) -> None:
        """Gelernte Werte in den Config Entry schreiben."""
        if self._persist_callback is not None:
            rooms = self.config.get("rooms", {})
            _LOGGER.warning(
                "[Smartdome Diagnose] PERSIST_LEARNED_VALUES: Erstelle Persist-Task. "
                "Räume: %s | heating_mode: %s | enabled: %s",
                {rid: r.get("label", rid) for rid, r in rooms.items()},
                self.config.get("heating_mode"),
                self.config.get("enabled"),
            )
            self.hass.async_create_task(self._persist_callback(dict(self.config)))

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
        """Numerischen Zustand einer Entity lesen.

        Für climate.*-Entities wird current_temperature aus den Attributen
        gelesen, da state dort den HVAC-Modus enthält (z.B. 'heat_cool').
        """
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if not state or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        if entity_id.startswith("climate."):
            return self._safe_float(state.attributes.get("current_temperature"))
        return self._safe_float(state.state)

    def _room_temp(self, room: dict[str, Any]) -> float | None:
        """Raumtemperatur lesen."""
        return self._get_state_float(self._as_entity_id(room.get(CONF_ROOM_SENSOR)))

    def _is_window_open(self, room: dict[str, Any]) -> bool:
        """Prüfen, ob mindestens ein Fensterkontakt im Raum offen ist."""
        sensors = room.get(CONF_ROOM_WINDOW_SENSORS, [])
        if not isinstance(sensors, list):
            sensors = []
        for entity_id in sensors:
            if not entity_id:
                continue
            state = self.hass.states.get(entity_id)
            if not state:
                continue
            if str(state.state).lower() in {"on", "open", "true"}:
                return True
        return False

    def _window_pause_active(self, room_id: str, room: dict[str, Any]) -> bool:
        """Fensterlogik mit Open-/Close-Delay."""
        sensors = room.get(CONF_ROOM_WINDOW_SENSORS, [])
        has_sensor = isinstance(sensors, list) and any(s for s in sensors if s)
        if not has_sensor:
            self._window_open_since.pop(room_id, None)
            self._window_closed_since.pop(room_id, None)
            self._window_paused_rooms.discard(room_id)
            return False

        now = dt_util.now().timestamp()
        open_delay = int(
            self.config.get(CONF_WINDOW_OPEN_DELAY, DEFAULT_WINDOW_OPEN_DELAY)
        )
        close_delay = int(
            self.config.get(CONF_WINDOW_CLOSE_DELAY, DEFAULT_WINDOW_CLOSE_DELAY)
        )

        window_open = self._is_window_open(room)

        if window_open:
            self._window_closed_since.pop(room_id, None)

            opened_since = self._window_open_since.get(room_id)
            if opened_since is None:
                self._window_open_since[room_id] = now
                return open_delay <= 0

            if now - opened_since >= open_delay:
                self._window_paused_rooms.add(room_id)
                return True

            return False

        self._window_open_since.pop(room_id, None)

        if room_id in self._window_paused_rooms:
            closed_since = self._window_closed_since.get(room_id)
            if closed_since is None:
                self._window_closed_since[room_id] = now
                return close_delay > 0

            if now - closed_since >= close_delay:
                self._window_paused_rooms.discard(room_id)
                self._window_closed_since.pop(room_id, None)
                return False

            return True

        self._window_closed_since.pop(room_id, None)
        return False

    def _time_hhmm(self) -> str:
        """Aktuelle Uhrzeit als HH:MM."""
        return dt_util.now().strftime("%H:%M")

    def _normalize_weekly_schedule(
        self,
        schedule: Any,
    ) -> dict[str, list[dict[str, Any]]]:
        """Weekly schedule normalisieren."""
        base = {
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": [],
        }

        if not isinstance(schedule, dict):
            return base

        normalized: dict[str, list[dict[str, Any]]] = {}

        for day in base:
            entries = schedule.get(day, [])
            if not isinstance(entries, list):
                normalized[day] = []
                continue

            valid_entries: list[dict[str, Any]] = []

            for entry in entries:
                if not isinstance(entry, dict):
                    continue

                start = str(entry.get("start", "")).strip()
                temperature = self._safe_float(entry.get("temperature"))

                if not start or temperature is None:
                    continue

                if not self._is_valid_schedule_time(start):
                    continue

                valid_entries.append(
                    {
                        "start": start[:5],
                        "temperature": float(temperature),
                    }
                )

            valid_entries.sort(key=lambda item: item["start"])
            normalized[day] = valid_entries

        return normalized

    def _is_valid_schedule_time(self, value: str) -> bool:
        """Zeitformat HH:MM prüfen."""
        if len(value) < 5:
            return False

        try:
            hours = int(value[:2])
            minutes = int(value[3:5])
        except (TypeError, ValueError):
            return False

        return (
            len(value[:5]) == 5
            and value[2] == ":"
            and 0 <= hours <= 23
            and 0 <= minutes <= 59
        )

    def _scheduled_target_for_room(self, room: dict[str, Any]) -> float | None:
        """Zieltemperatur aus dem Wochenplan lesen.

        Gibt None zurück, wenn für den aktuellen Tag keine gültigen
        Schedule-Einträge vorhanden sind.
        """
        schedule = self._normalize_weekly_schedule(
            room.get(CONF_ROOM_WEEKLY_SCHEDULE, DEFAULT_ROOM_WEEKLY_SCHEDULE)
        )

        day_key = dt_util.now().strftime("%A").lower()
        entries = schedule.get(day_key, [])

        if not entries:
            return None

        now_hhmm = self._time_hhmm()
        active_temperature: float | None = None

        for entry in entries:
            start = str(entry.get("start", ""))[:5]
            temperature = self._safe_float(entry.get("temperature"))

            if temperature is None:
                continue

            if start <= now_hhmm:
                active_temperature = float(temperature)
            else:
                break

        if active_temperature is not None:
            return active_temperature

        return None

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
                self.config.get(CONF_MORNING_BOOST_START, DEFAULT_MORNING_BOOST_START),
            )
        )[:5]

        if room_night_start > room_day_start:
            return now >= room_night_start or now < room_day_start

        return room_night_start <= now < room_day_start

    def _base_target_for_room(self, room: dict[str, Any]) -> float:
        """Normale Tag-/Nacht-Solltemperatur."""
        night_setback_enabled = bool(room.get(CONF_ROOM_NIGHT_SETBACK_ENABLED, True))
        if night_setback_enabled and self._is_night_for_room(room):
            return float(room.get(CONF_ROOM_TARGET_NIGHT, DEFAULT_TARGET_NIGHT))
        return float(room.get(CONF_ROOM_TARGET_DAY, DEFAULT_TARGET_DAY))

    def _effective_target_for_room(self, room: dict[str, Any]) -> float:
        """Ermittelt die gültige Zieltemperatur."""
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
            return (
                vacation_temp
                if vacation_temp is not None
                else float(DEFAULT_VACATION_TEMPERATURE)
            )

        if away_enabled:
            away_temp = self._safe_float(
                room.get(
                    CONF_ROOM_AWAY_TEMPERATURE,
                    DEFAULT_ROOM_AWAY_TEMPERATURE,
                )
            )
            return (
                away_temp
                if away_temp is not None
                else float(DEFAULT_ROOM_AWAY_TEMPERATURE)
            )

        scheduled_target = self._scheduled_target_for_room(room)
        if scheduled_target is not None:
            return scheduled_target

        return self._base_target_for_room(room)

    def _thermostat_min_temp(self, entity_id: str) -> float:
        """Minimale Solltemperatur eines Thermostats lesen."""
        state = self.hass.states.get(entity_id)
        if state:
            min_temp = self._safe_float(state.attributes.get("min_temp"))
            if min_temp is not None:
                return min_temp
        return 5.0

    def _thermostat_target_step(self, entity_id: str) -> float:
        """Schrittweite des Thermostats lesen, fallback 0.5°C."""
        state = self.hass.states.get(entity_id)
        if state:
            step = self._safe_float(state.attributes.get("target_temp_step"))
            if step is not None and step > 0:
                return step
        return 0.5

    def _round_to_step(self, value: float, step: float) -> float:
        """Zieltemperatur auf Schrittweite runden."""
        if step <= 0:
            return round(value, 1)
        return round(round(value / step) * step, 2)

    def _get_room_control_profile(self, room: dict[str, Any]) -> str:
        """Raum-Regelprofil lesen."""
        profile = str(
            room.get(CONF_ROOM_CONTROL_PROFILE, DEFAULT_ROOM_CONTROL_PROFILE)
        ).strip().lower()

        if profile == CONTROL_PROFILE_SELF_REGULATING:
            return CONTROL_PROFILE_SELF_REGULATING

        return CONTROL_PROFILE_STANDARD

    def _is_self_regulating_room(self, room: dict[str, Any]) -> bool:
        """Prüfen, ob der Raum ein selbst regelndes Thermostat nutzt."""
        return self._get_room_control_profile(room) == CONTROL_PROFILE_SELF_REGULATING

    def _get_min_command_interval_for_room(self, room: dict[str, Any]) -> float:
        """Mindestabstand zwischen Befehlen je nach Raumprofil."""
        if self._is_self_regulating_room(room):
            return 120.0
        return 0.0

    def _should_force_send_for_self_regulating(
        self,
        thermostat: str,
        desired: float,
    ) -> bool:
        """Prüfen, ob ein selbst regelndes Thermostat trotz Drosselung sofort
        aktualisiert werden soll, weil sich der berechnete Zielwert geändert hat.
        """
        # Wenn ein anderer Pfad (z.B. Haupt-Thermostat-Logik) denselben Thermostat
        # zwischenzeitlich auf einen anderen Wert gesetzt hat, sofort korrigieren.
        last_sent = self._desired_targets.get(thermostat)
        if last_sent is not None and abs(last_sent - desired) >= 0.5:
            self._last_computed_targets[thermostat] = desired
            return True

        previous_computed = self._last_computed_targets.get(thermostat)

        if previous_computed is None:
            self._last_computed_targets[thermostat] = desired
            return True

        if abs(previous_computed - desired) >= 0.5:
            self._last_computed_targets[thermostat] = desired
            return True

        return False

    def _set_temp_if_needed(
        self,
        entity_id: str,
        temp: float,
        min_interval: float = 0.0,
    ) -> None:
        """Nur schreiben, wenn sich der gewünschte Smartdome-Zielwert geändert hat.

        Optional mit Mindestabstand für selbst regelnde Thermostate.
        """
        step = self._thermostat_target_step(entity_id)
        desired = self._round_to_step(float(temp), step)
        previous = self._desired_targets.get(entity_id)

        if previous is not None and abs(previous - desired) < 0.01:
            return

        now_ts = dt_util.now().timestamp()
        last_sent = self._last_command_sent_at.get(entity_id, 0.0)

        if min_interval > 0 and (now_ts - last_sent) < min_interval:
            return

        self._desired_targets[entity_id] = desired
        self._last_command_sent_at[entity_id] = now_ts

        self.hass.async_create_task(
            self.hass.services.async_call(
                CLIMATE_DOMAIN,
                "set_temperature",
                {
                    "entity_id": entity_id,
                    ATTR_TEMPERATURE: desired,
                },
                blocking=True,
            )
        )

    def _turn_switch_if_needed(self, entity_id: str, turn_on: bool) -> None:
        """Switch ein- oder ausschalten, aber nur wenn sich der Zustand ändert."""
        last = self._desired_targets.get(entity_id)
        desired = 1.0 if turn_on else 0.0
        if last is not None and abs(last - desired) < 0.01:
            return
        self._desired_targets[entity_id] = desired
        self.hass.async_create_task(
            self.hass.services.async_call(
                SWITCH_DOMAIN,
                "turn_on" if turn_on else "turn_off",
                {"entity_id": entity_id},
                blocking=True,
            )
        )

    def _set_hvac_mode_if_needed(self, entity_id: str, hvac_mode: str) -> None:
        """HVAC-Modus setzen, aber nur wenn er sich geändert hat."""
        if self._last_hvac_mode.get(entity_id) == hvac_mode:
            return
        self._last_hvac_mode[entity_id] = hvac_mode
        self.hass.async_create_task(
            self.hass.services.async_call(
                CLIMATE_DOMAIN,
                "set_hvac_mode",
                {"entity_id": entity_id, "hvac_mode": hvac_mode},
                blocking=True,
            )
        )

    def _set_fan_mode_if_needed(self, entity_id: str, fan_mode: str) -> None:
        """Lüftermodus setzen, aber nur wenn er sich geändert hat."""
        if self._last_fan_mode.get(entity_id) == fan_mode:
            return
        self._last_fan_mode[entity_id] = fan_mode
        self.hass.async_create_task(
            self.hass.services.async_call(
                CLIMATE_DOMAIN,
                "set_fan_mode",
                {"entity_id": entity_id, "fan_mode": fan_mode},
                blocking=True,
            )
        )

    def _set_preset_mode_if_needed(self, entity_id: str, preset_mode: str) -> None:
        """Preset-Modus setzen, aber nur wenn er sich geändert hat."""
        if self._last_preset_mode.get(entity_id) == preset_mode:
            return
        self._last_preset_mode[entity_id] = preset_mode
        self.hass.async_create_task(
            self.hass.services.async_call(
                CLIMATE_DOMAIN,
                "set_preset_mode",
                {"entity_id": entity_id, "preset_mode": preset_mode},
                blocking=True,
            )
        )

    def _is_cooling_active(self) -> bool:
        """Prüfen ob der Kühlmodus aktiv ist (manuell oder automatisch)."""
        if self.config.get(CONF_COOLING_ENABLED, DEFAULT_COOLING_ENABLED):
            return True
        if self.config.get(CONF_COOLING_AUTO, DEFAULT_COOLING_AUTO):
            outdoor_sensor = self.config.get(CONF_OUTDOOR_SENSOR, "")
            threshold = float(self.config.get(CONF_COOLING_THRESHOLD, DEFAULT_COOLING_THRESHOLD))
            if outdoor_sensor:
                sensor_state = self.hass.states.get(outdoor_sensor)
                if sensor_state is not None:
                    try:
                        return float(sensor_state.state) >= threshold
                    except (ValueError, TypeError):
                        pass
        return False

    def _get_heating_mode(self) -> str:
        """Globalen Heizmodus lesen."""
        return str(self.config.get(CONF_HEATING_MODE, DEFAULT_HEATING_MODE))

    def _get_room_heating_mode(self, room: dict[str, Any]) -> str:
        """Heizmodus für einen Raum lesen (room-Override oder globaler Modus)."""
        room_mode = str(room.get(CONF_ROOM_HEATING_MODE, "")).strip()
        if room_mode in (HEATING_MODE_COMFORT, HEATING_MODE_BALANCED, HEATING_MODE_ENERGY, HEATING_MODE_ADAPTIVE):
            return room_mode
        return self._get_heating_mode()

    def _get_energy_residual_heat_hold_seconds(self) -> int:
        """Nachlaufzeit im Energy Mode."""
        value = self._safe_float(
            self.config.get(
                CONF_ENERGY_RESIDUAL_HEAT_HOLD,
                DEFAULT_ENERGY_RESIDUAL_HEAT_HOLD,
            )
        )
        if value is None:
            return int(DEFAULT_ENERGY_RESIDUAL_HEAT_HOLD)
        return max(0, int(value))

    def _get_bucket_key(self, duration_secs: float) -> str:
        """Bucket-Schlüssel anhand der Heizdauer bestimmen."""
        if duration_secs < ADAPTIVE_BUCKET_SHORT_MAX_SECS:
            return "short"
        if duration_secs < ADAPTIVE_BUCKET_MEDIUM_MAX_SECS:
            return "medium"
        return "long"

    def _get_learned_overshoot_for_bucket(
        self,
        room: dict[str, Any],
        bucket: str,
    ) -> float:
        """Gelernten Overshoot-Wert für einen bestimmten Bucket lesen."""
        key_map = {
            "short": (CONF_ROOM_LEARNED_OVERSHOOT_SHORT, DEFAULT_ADAPTIVE_OVERSHOOT_SHORT),
            "medium": (CONF_ROOM_LEARNED_OVERSHOOT_MEDIUM, DEFAULT_ADAPTIVE_OVERSHOOT_MEDIUM),
            "long": (CONF_ROOM_LEARNED_OVERSHOOT_LONG, DEFAULT_ADAPTIVE_OVERSHOOT_LONG),
        }
        key, default = key_map[bucket]
        return float(room.get(key, default))

    def _get_predicted_overshoot(self, room: dict[str, Any], tolerance: float) -> float:
        """Vorhergesagten Overshoot anhand der aktuellen Heizdauer bestimmen.

        Wird auf tolerance * 0.9 begrenzt damit die Stoppbedingung immer
        oberhalb der Startbedingung liegt und keine sofortige Oszillation
        entsteht.
        """
        start_ts = room.get(CONF_ROOM_CYCLE_START_TS)
        if start_ts is None:
            bucket = "medium"
        else:
            duration = dt_util.now().timestamp() - float(start_ts)
            bucket = self._get_bucket_key(duration)

        predicted = self._get_learned_overshoot_for_bucket(room, bucket)
        return min(predicted, tolerance * 0.9)

    def _get_idle_target_for_room(
        self,
        room_id: str,
        room: dict[str, Any],
        thermostat_id: str,
        target_temp: float,
    ) -> float:
        """Fester Idle-Sollwert je nach Modus."""
        mode = self._get_room_heating_mode(room)
        min_temp = self._thermostat_min_temp(thermostat_id)
        step = self._thermostat_target_step(thermostat_id)

        if mode == HEATING_MODE_COMFORT:
            return self._round_to_step(target_temp, step)

        if mode == HEATING_MODE_BALANCED:
            return self._round_to_step(max(min_temp, target_temp - 1.0), step)

        if mode == HEATING_MODE_ENERGY:
            return self._round_to_step(min_temp, step)

        if mode == HEATING_MODE_ADAPTIVE:
            avg_learned = (
                self._get_learned_overshoot_for_bucket(room, "short")
                + self._get_learned_overshoot_for_bucket(room, "medium")
                + self._get_learned_overshoot_for_bucket(room, "long")
            ) / 3.0
            avg_learned = max(0.2, min(1.0, avg_learned))
            return self._round_to_step(max(min_temp, target_temp - avg_learned), step)

        return self._round_to_step(target_temp, step)

    def _get_heating_target_for_room(
        self,
        thermostat_id: str,
        target_temp: float,
        boost_delta: float,
    ) -> float:
        """Fester Heiz-Sollwert."""
        step = self._thermostat_target_step(thermostat_id)
        return self._round_to_step(target_temp + boost_delta, step)

    def _get_residual_hold_target_for_room(
        self,
        thermostat_id: str,
        target_temp: float,
    ) -> float:
        """Fester Sollwert während Restwärme-Nachlauf."""
        step = self._thermostat_target_step(thermostat_id)
        return self._round_to_step(target_temp, step)

    def _reset_runtime_states(self) -> None:
        """Laufzeit-Heizzustände zurücksetzen."""
        for room in self._active_rooms().values():
            room[CONF_ROOM_HEATING_CYCLE_ACTIVE] = False
            room[CONF_ROOM_CYCLE_TARGET_TEMP] = None
            room[CONF_ROOM_CYCLE_PEAK_TEMP] = None
            room[CONF_ROOM_CYCLE_PEAKED] = False

        self._desired_targets.clear()
        self._last_computed_targets.clear()
        self._room_state.clear()
        self._residual_heat_hold_until.clear()
        self._last_command_sent_at.clear()
        self._last_applied_room_state.clear()
        self._circuit_heating_active.clear()
        self._last_hvac_mode.clear()
        self._last_fan_mode.clear()
        self._last_preset_mode.clear()

    def _restore_non_boost_targets(self) -> None:
        """Thermostate beim Deaktivieren auf normale Zielwerte zurücksetzen."""
        rooms = self._active_rooms()

        for room_id, room in rooms.items():
            thermostat = self._as_entity_id(room.get(CONF_ROOM_THERMOSTAT))
            if not thermostat:
                continue

            target = self._effective_target_for_room(room)
            idle_target = self._get_idle_target_for_room(
                room_id,
                room,
                thermostat,
                target,
            )
            min_interval = self._get_min_command_interval_for_room(room)
            self._set_temp_if_needed(
                thermostat,
                idle_target,
                min_interval=min_interval,
            )

        circuits = self.config.get(CONF_CIRCUITS, {})
        if circuits and isinstance(circuits, dict):
            for circuit in circuits.values():
                if not isinstance(circuit, dict):
                    continue
                ct = self._as_entity_id(circuit.get(CONF_CIRCUIT_MAIN_THERMOSTAT))
                if not ct:
                    continue
                self._set_temp_if_needed(ct, self._thermostat_min_temp(ct))
        else:
            main_thermostat = self._as_entity_id(self.config.get(CONF_MAIN_THERMOSTAT))
            if main_thermostat:
                self._set_temp_if_needed(
                    main_thermostat, self._thermostat_min_temp(main_thermostat)
                )

    def _update_room_state(
        self,
        room_id: str,
        room: dict[str, Any],
        target: float,
        actual: float | None,
        pause_active: bool,
        tolerance: float,
        predicted_overshoot: float = 0.0,
    ) -> str:
        """Raumzustand bestimmen und nur bei echten Zustandswechseln ändern."""
        current_state = self._room_state.get(room_id, ROOM_STATE_IDLE)
        mode = self._get_room_heating_mode(room)
        now_ts = dt_util.now().timestamp()

        if pause_active:
            self._room_state[room_id] = ROOM_STATE_IDLE
            self._residual_heat_hold_until.pop(room_id, None)
            return ROOM_STATE_IDLE

        if actual is None:
            # Sensor vorübergehend nicht verfügbar: aktuellen Zustand einfrieren.
            # Wenn der Raum bereits heizte, weiter heizen – nicht abrupt stoppen,
            # nur weil ein Sensor kurz "unavailable" meldet.
            # Heizung STARTEN ohne Sensor ist nicht erlaubt (bleibt IDLE).
            return self._room_state.get(room_id, ROOM_STATE_IDLE)

        if current_state == ROOM_STATE_IDLE:
            if actual < (target - tolerance):
                self._room_state[room_id] = ROOM_STATE_HEATING
                self._residual_heat_hold_until.pop(room_id, None)
                return ROOM_STATE_HEATING

        stop_at = target - predicted_overshoot
        if current_state == ROOM_STATE_HEATING and actual >= stop_at:
            if mode == HEATING_MODE_ENERGY:
                hold_seconds = self._get_energy_residual_heat_hold_seconds()
                if hold_seconds > 0:
                    self._residual_heat_hold_until[room_id] = now_ts + hold_seconds
                    self._room_state[room_id] = ROOM_STATE_RESIDUAL_HOLD
                    return ROOM_STATE_RESIDUAL_HOLD

            self._room_state[room_id] = ROOM_STATE_IDLE
            return ROOM_STATE_IDLE

        if current_state == ROOM_STATE_RESIDUAL_HOLD:
            hold_until = self._residual_heat_hold_until.get(room_id, 0.0)
            if now_ts >= hold_until:
                self._residual_heat_hold_until.pop(room_id, None)
                self._room_state[room_id] = ROOM_STATE_IDLE
                return ROOM_STATE_IDLE

        return self._room_state.get(room_id, ROOM_STATE_IDLE)

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
            if room.get(CONF_ROOM_CYCLE_PEAKED):
                # Previous cycle peaked but never finished (temperature didn't
                # drop back below target before the next heat request came in).
                # Force-finish it so learning is recorded, then start fresh.
                self._finish_room_heating_cycle(room)
            else:
                peak = room.get(CONF_ROOM_CYCLE_PEAK_TEMP)
                if peak is None or current_temp > peak:
                    room[CONF_ROOM_CYCLE_PEAK_TEMP] = current_temp
                return

        room[CONF_ROOM_HEATING_CYCLE_ACTIVE] = True
        room[CONF_ROOM_CYCLE_TARGET_TEMP] = target_temp
        room[CONF_ROOM_CYCLE_PEAK_TEMP] = current_temp
        room[CONF_ROOM_CYCLE_START_TS] = dt_util.now().timestamp()

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
        """Overshoot messen, richtigen Bucket updaten und Werte persistieren."""
        if not room.get(CONF_ROOM_HEATING_CYCLE_ACTIVE):
            return

        target = room.get(CONF_ROOM_CYCLE_TARGET_TEMP)
        peak = room.get(CONF_ROOM_CYCLE_PEAK_TEMP)
        start_ts = room.get(CONF_ROOM_CYCLE_START_TS)

        if target is not None and peak is not None and start_ts is not None:
            duration = dt_util.now().timestamp() - float(start_ts)
            overshoot = max(0.0, float(peak) - float(target))
            bucket = self._get_bucket_key(duration)

            key_map = {
                "short": (CONF_ROOM_LEARNED_OVERSHOOT_SHORT, DEFAULT_ADAPTIVE_OVERSHOOT_SHORT),
                "medium": (CONF_ROOM_LEARNED_OVERSHOOT_MEDIUM, DEFAULT_ADAPTIVE_OVERSHOOT_MEDIUM),
                "long": (CONF_ROOM_LEARNED_OVERSHOOT_LONG, DEFAULT_ADAPTIVE_OVERSHOOT_LONG),
            }
            key, default = key_map[bucket]
            old_value = float(room.get(key, default))
            new_value = (old_value * 0.7) + (overshoot * 0.3)
            room[key] = round(new_value, 2)

            # Durchschnitt aller Buckets als Anzeigewert speichern
            avg = (
                self._get_learned_overshoot_for_bucket(room, "short")
                + self._get_learned_overshoot_for_bucket(room, "medium")
                + self._get_learned_overshoot_for_bucket(room, "long")
            ) / 3.0
            room[CONF_ROOM_LEARNED_OVERSHOOT] = round(avg, 2)

            self._persist_learned_values()

        room[CONF_ROOM_HEATING_CYCLE_ACTIVE] = False
        room[CONF_ROOM_CYCLE_TARGET_TEMP] = None
        room[CONF_ROOM_CYCLE_PEAK_TEMP] = None
        room[CONF_ROOM_CYCLE_START_TS] = None
        room[CONF_ROOM_CYCLE_PEAKED] = False

    def _is_outdoor_cutoff_active(self) -> bool:
        """Prüfen ob die Außentemperatur-Abschaltung aktiv ist."""
        if not bool(
            self.config.get(CONF_OUTDOOR_TEMP_CUTOFF_ENABLED, DEFAULT_OUTDOOR_TEMP_CUTOFF_ENABLED)
        ):
            return False
        outdoor_sensor = self._as_entity_id(self.config.get(CONF_OUTDOOR_SENSOR))
        if not outdoor_sensor:
            return False
        outdoor_temp = self._get_state_float(outdoor_sensor)
        if outdoor_temp is None:
            return False
        cutoff = self._safe_float(
            self.config.get(CONF_OUTDOOR_TEMP_CUTOFF, DEFAULT_OUTDOOR_TEMP_CUTOFF)
        )
        if cutoff is None:
            cutoff = float(DEFAULT_OUTDOOR_TEMP_CUTOFF)
        return outdoor_temp >= cutoff

    def _evaluate(self) -> None:
        """Heizlogik auswerten."""
        if not self._enabled:
            return

        rooms = self._active_rooms()

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

        outdoor_cutoff_active = self._is_outdoor_cutoff_active()
        if outdoor_cutoff_active:
            _LOGGER.debug("Außentemperatur-Abschaltung aktiv – Heizung gesperrt")

        for room_id, room in rooms.items():
            actual = self._room_temp(room)
            target = self._effective_target_for_room(room)
            pause_active = self._window_pause_active(room_id, room)
            mode = self._get_room_heating_mode(room)

            predicted_overshoot = (
                self._get_predicted_overshoot(room, tolerance)
                if mode == HEATING_MODE_ADAPTIVE
                else 0.0
            )

            state = self._update_room_state(
                room_id=room_id,
                room=room,
                target=target,
                actual=actual,
                pause_active=pause_active,
                tolerance=tolerance,
                predicted_overshoot=predicted_overshoot,
            )

            # Außentemperatur-Abschaltung: Heizung unterdrücken, aber
            # Raumthermostate auf normalen Idle-Sollwert belassen (kein Frost-Modus).
            if outdoor_cutoff_active and state == ROOM_STATE_HEATING:
                state = ROOM_STATE_IDLE
                self._room_state[room_id] = ROOM_STATE_IDLE

            room_states[room_id] = {
                "actual": actual,
                "target": target,
                "state": state,
                "pause_active": pause_active,
            }

            if state == ROOM_STATE_HEATING:
                self._start_room_heating_cycle(room, target, actual)
            else:
                self._update_room_cycle_peak(room, actual)
                if room.get(CONF_ROOM_HEATING_CYCLE_ACTIVE) and actual is not None:
                    start_ts = room.get(CONF_ROOM_CYCLE_START_TS)
                    cycle_age = (dt_util.now().timestamp() - float(start_ts)) if start_ts is not None else 0.0
                    if actual >= target:
                        # Temperature crossed target: mark peak phase reached.
                        room[CONF_ROOM_CYCLE_PEAKED] = True
                    elif room.get(CONF_ROOM_CYCLE_PEAKED):
                        # Temperature has peaked above target and is now declining
                        # below it → full overshoot captured, finish the cycle.
                        self._finish_room_heating_cycle(room)
                    elif cycle_age > 7200:
                        # Safety: target never reached within 2 h – finish to
                        # avoid stale state.
                        self._finish_room_heating_cycle(room)

        # Any thermostat entity that is already managed as a room thermostat
        # handles its own idle setpoint via the room step (_get_idle_target_for_room).
        # If the main thermostat entity is one of these, skip it here to avoid
        # both code paths fighting each other.  This applies to all control
        # profiles (self-regulating and non-self-regulating alike).
        room_managed_thermostats = {
            self._as_entity_id(room.get(CONF_ROOM_THERMOSTAT))
            for room in rooms.values()
            if room.get(CONF_ROOM_THERMOSTAT)
        }

        circuits = self.config.get(CONF_CIRCUITS, {})
        if circuits and isinstance(circuits, dict):
            # Multi-circuit mode: each circuit controls its own main thermostat or switch
            for circuit_id, circuit in circuits.items():
                if not isinstance(circuit, dict):
                    continue
                if not circuit.get(CONF_CIRCUIT_ENABLED, True):
                    # Disabled circuit: ensure its output is off
                    circuit_control_type = circuit.get(CONF_CIRCUIT_CONTROL_TYPE, "thermostat")
                    if circuit_control_type == CONTROL_TYPE_SWITCH:
                        ct = self._as_entity_id(circuit.get(CONF_CIRCUIT_MAIN_SWITCH))
                    else:
                        ct = self._as_entity_id(circuit.get(CONF_CIRCUIT_MAIN_THERMOSTAT))
                    if ct:
                        self._desired_targets.pop(ct, None)
                        if circuit_control_type == CONTROL_TYPE_SWITCH:
                            self._turn_switch_if_needed(ct, False)
                        else:
                            self._set_temp_if_needed(ct, self._thermostat_min_temp(ct))
                    continue
                circuit_control_type = circuit.get(CONF_CIRCUIT_CONTROL_TYPE, "thermostat")
                if circuit_control_type == CONTROL_TYPE_SWITCH:
                    ct = self._as_entity_id(circuit.get(CONF_CIRCUIT_MAIN_SWITCH))
                else:
                    ct = self._as_entity_id(circuit.get(CONF_CIRCUIT_MAIN_THERMOSTAT))
                if not ct or ct in room_managed_thermostats:
                    continue
                circuit_room_states = {
                    rid: rs for rid, rs in room_states.items()
                    if rooms[rid].get(CONF_ROOM_CIRCUIT_ID) == circuit_id
                }
                if not circuit_room_states:
                    # Keine Räume in diesem Kreis → Schalten ausschalten / min_temp
                    self._desired_targets.pop(ct, None)
                    if circuit_control_type == CONTROL_TYPE_SWITCH:
                        self._turn_switch_if_needed(ct, False)
                    else:
                        self._set_temp_if_needed(ct, self._thermostat_min_temp(ct))
                    continue
                # RESIDUAL_HOLD zählt ebenfalls als "braucht Wärme":
                # Im Energy-Modus halten Räume den Heizkreis nach Zielerreichung
                # noch kurz aktiv, damit Restwärme verteilt wird.
                any_circuit_needs_heat = any(
                    rs["state"] in (ROOM_STATE_HEATING, ROOM_STATE_RESIDUAL_HOLD)
                    for rs in circuit_room_states.values()
                )
                # Übergang heating → idle: _desired_targets löschen damit
                # Befehl garantiert gesendet wird.
                was_heating = self._circuit_heating_active.get(circuit_id, False)
                if was_heating and not any_circuit_needs_heat:
                    _LOGGER.debug(
                        "Heizkreis '%s' schaltet auf IDLE. Raumzustände: %s",
                        circuit.get(CONF_CIRCUIT_LABEL, circuit_id),
                        {rid: rs["state"] for rid, rs in circuit_room_states.items()},
                    )
                    self._desired_targets.pop(ct, None)
                elif not was_heating and any_circuit_needs_heat:
                    _LOGGER.debug(
                        "Heizkreis '%s' schaltet auf HEATING. Raumzustände: %s",
                        circuit.get(CONF_CIRCUIT_LABEL, circuit_id),
                        {rid: rs["state"] for rid, rs in circuit_room_states.items()},
                    )
                self._circuit_heating_active[circuit_id] = any_circuit_needs_heat

                if circuit_control_type == CONTROL_TYPE_SWITCH:
                    self._turn_switch_if_needed(ct, any_circuit_needs_heat)
                else:
                    # Read circuit sensor once – used for both heating and idle target.
                    ct_sensor_id = self._as_entity_id(
                        circuit.get(CONF_CIRCUIT_MAIN_SENSOR)
                    )
                    ct_current = (
                        self._get_state_float(ct_sensor_id) if ct_sensor_id else None
                    )
                    if ct_current is None:
                        ct_state = self.hass.states.get(ct)
                        if ct_state:
                            ct_current = self._safe_float(
                                ct_state.attributes.get("current_temperature")
                            )
                    if any_circuit_needs_heat:
                        # Dynamic boost: setpoint = current sensor + boost_delta so the
                        # heating circuit turns ON reliably regardless of room targets.
                        if ct_current is not None:
                            circuit_target = ct_current + boost_delta
                        else:
                            circuit_target = (
                                max(rs["target"] for rs in circuit_room_states.values())
                                + boost_delta
                            )
                    else:
                        # Idle: set 5°C below current sensor so the circuit shuts off
                        # reliably even if the thermostat has no min_temp attribute.
                        if ct_current is not None:
                            circuit_target = ct_current - 5.0
                        else:
                            circuit_target = self._thermostat_min_temp(ct)
                    self._set_temp_if_needed(ct, circuit_target)
        else:
            # Single-circuit fallback: use global main_thermostat or main_switch
            any_room_needs_heat = any(
                rs["state"] == ROOM_STATE_HEATING
                for rs in room_states.values()
            )
            main_control_type = self.config.get(CONF_MAIN_CONTROL_TYPE, "thermostat")
            if main_control_type == CONTROL_TYPE_SWITCH:
                main_entity = self._as_entity_id(self.config.get(CONF_MAIN_SWITCH))
            else:
                main_entity = self._as_entity_id(self.config.get(CONF_MAIN_THERMOSTAT))
            if main_entity and main_entity not in room_managed_thermostats:
                # Übergang heating → idle: _desired_targets löschen damit
                # Befehl garantiert gesendet wird.
                was_heating = self._circuit_heating_active.get(main_entity, False)
                if was_heating and not any_room_needs_heat:
                    self._desired_targets.pop(main_entity, None)
                self._circuit_heating_active[main_entity] = any_room_needs_heat

                if main_control_type == CONTROL_TYPE_SWITCH:
                    self._turn_switch_if_needed(main_entity, any_room_needs_heat)
                else:
                    # Read main sensor once – used for both heating and idle target.
                    main_sensor_id = self._as_entity_id(
                        self.config.get(CONF_MAIN_SENSOR)
                    )
                    main_current = (
                        self._get_state_float(main_sensor_id)
                        if main_sensor_id
                        else None
                    )
                    if main_current is None:
                        mt_state = self.hass.states.get(main_entity)
                        if mt_state:
                            main_current = self._safe_float(
                                mt_state.attributes.get("current_temperature")
                            )
                    if any_room_needs_heat:
                        # Dynamic boost: setpoint = current sensor + boost_delta so the
                        # heating circuit turns ON reliably regardless of room targets.
                        if main_current is not None:
                            main_target = main_current + boost_delta
                        else:
                            main_target = (
                                max(rs["target"] for rs in room_states.values())
                                + boost_delta
                            )
                    else:
                        # Idle: set 5°C below current sensor so the circuit shuts off
                        # reliably even if the thermostat has no min_temp attribute.
                        if main_current is not None:
                            main_target = main_current - 5.0
                        else:
                            main_target = self._thermostat_min_temp(main_entity)
                    self._set_temp_if_needed(main_entity, main_target)

        for room_id, room in rooms.items():
            thermostat = self._as_entity_id(room.get(CONF_ROOM_THERMOSTAT))
            climate_entity = self._as_entity_id(room.get(CONF_ROOM_CLIMATE_ENTITY, ""))
            use_climate = bool(room.get(CONF_ROOM_USE_CLIMATE, False))
            cooling_active = self._is_cooling_active()

            # --- Klimaanlage / Kühllogik (#69 + #70) ---
            if climate_entity:
                rstate = room_states.get(room_id, {})
                if cooling_active:
                    # Kühlmodus: Klimaanlage übernimmt
                    hvac_mode = str(room.get(CONF_ROOM_CLIMATE_HVAC_MODE, DEFAULT_ROOM_CLIMATE_HVAC_MODE))
                    fan_mode = str(room.get(CONF_ROOM_CLIMATE_FAN_MODE, DEFAULT_ROOM_CLIMATE_FAN_MODE))
                    preset = str(room.get(CONF_ROOM_CLIMATE_PRESET, DEFAULT_ROOM_CLIMATE_PRESET))
                    cool_target = float(room.get(CONF_ROOM_COOL_TARGET_DAY, DEFAULT_ROOM_COOL_TARGET_DAY))
                    self._set_hvac_mode_if_needed(climate_entity, hvac_mode)
                    if fan_mode:
                        self._set_fan_mode_if_needed(climate_entity, fan_mode)
                    if preset:
                        self._set_preset_mode_if_needed(climate_entity, preset)
                    self._set_temp_if_needed(climate_entity, cool_target)
                    # Heizventil ausschalten
                    if thermostat:
                        self._set_temp_if_needed(
                            thermostat, self._thermostat_min_temp(thermostat)
                        )
                    continue
                elif use_climate:
                    # Heizen via Klimaanlage
                    if rstate.get("pause_active"):
                        self._set_hvac_mode_if_needed(climate_entity, "off")
                    else:
                        heat_target = float(
                            rstate.get(
                                "target",
                                room.get(CONF_ROOM_TARGET_DAY, DEFAULT_TARGET_DAY),
                            )
                        )
                        self._set_hvac_mode_if_needed(climate_entity, "heat")
                        self._set_temp_if_needed(climate_entity, heat_target)
                    # Heizventil ausschalten
                    if thermostat:
                        self._set_temp_if_needed(
                            thermostat, self._thermostat_min_temp(thermostat)
                        )
                    continue
                else:
                    # Klimaanlage vorhanden aber nicht verwendet → ausschalten
                    self._set_hvac_mode_if_needed(climate_entity, "off")

            # --- Bestehende Thermostat-Logik (unverändert) ---
            if not thermostat:
                continue

            room_state = room_states[room_id]
            target = room_state["target"]
            state = room_state["state"]
            min_interval = self._get_min_command_interval_for_room(room)

            if room_state["pause_active"]:
                room_target = self._thermostat_min_temp(thermostat)
                effective_state = ROOM_STATE_WINDOW_PAUSE
            elif state == ROOM_STATE_HEATING:
                if self._is_self_regulating_room(room):
                    room_target = self._round_to_step(
                        target,
                        self._thermostat_target_step(thermostat),
                    )
                else:
                    room_target = self._get_heating_target_for_room(
                        thermostat,
                        target,
                        boost_delta,
                    )
                effective_state = ROOM_STATE_HEATING
            elif state == ROOM_STATE_RESIDUAL_HOLD:
                room_target = self._get_residual_hold_target_for_room(
                    thermostat,
                    target,
                )
                effective_state = ROOM_STATE_RESIDUAL_HOLD
            else:
                room_target = self._get_idle_target_for_room(
                    room_id,
                    room,
                    thermostat,
                    target,
                )
                effective_state = ROOM_STATE_IDLE

            if not room_state["pause_active"]:
                thermostat_offset = float(
                    room.get(CONF_ROOM_THERMOSTAT_OFFSET, DEFAULT_ROOM_THERMOSTAT_OFFSET)
                )
                if thermostat_offset != 0.0:
                    room_target = room_target + thermostat_offset

            desired = self._round_to_step(
                float(room_target),
                self._thermostat_target_step(thermostat),
            )

            if self._is_self_regulating_room(room):
                last_state = self._last_applied_room_state.get(room_id)
                state_changed = last_state != effective_state
                force_send = self._should_force_send_for_self_regulating(
                    thermostat,
                    desired,
                )

                if state_changed:
                    # Zustandswechsel (z.B. idle→heating) immer sofort senden –
                    # CCU-Verzögerung spielt hier keine Rolle.
                    self._set_temp_if_needed(thermostat, room_target, min_interval=0.0)
                    self._last_applied_room_state[room_id] = effective_state
                elif force_send:
                    # Zielwert hat sich geändert, aber kein Zustandswechsel →
                    # Cooldown respektieren, damit CCU-Polling-Verzögerung keine
                    # Befehlsflut auslöst.
                    self._set_temp_if_needed(thermostat, room_target, min_interval=min_interval)
                    self._last_applied_room_state[room_id] = effective_state
            else:
                self._set_temp_if_needed(
                    thermostat,
                    room_target,
                    min_interval=min_interval,
                )
                self._last_applied_room_state[room_id] = effective_state

        if self._state_callback is not None:
            self._state_callback(dict(self._room_state))

    @callback
    def _on_state_change(self, event: Event) -> None:
        """Bei Sensor-Änderung sofort neu bewerten."""
        self._evaluate()

    @callback
    def _on_minute_tick(self, now) -> None:
        """Zyklische Auswertung jede Minute."""
        self._evaluate()
