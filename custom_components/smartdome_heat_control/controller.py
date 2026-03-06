"""Smart Heating Controller – Kernlogik."""
from __future__ import annotations

import logging
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
    CONF_MAIN_THERMOSTAT,
    CONF_MORNING_BOOST_END,
    CONF_NIGHT_START,
    CONF_ROOMS,
    DEFAULT_BOOST_DELTA,
    DEFAULT_MORNING_BOOST_END,
    DEFAULT_NIGHT_START,
    DEFAULT_TARGET_DAY,
    DEFAULT_TARGET_NIGHT,
)

_LOGGER = logging.getLogger(__name__)

# Neuer optionaler Config-Key für den Sensor des Hauptthermostats.
# Kann später auch in const.py ausgelagert werden.
CONF_MAIN_SENSOR = "main_sensor"


class SmartHeatingController:
    """Kernlogik: Reagiert auf UI-Eingaben und Sensorwerte."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = config
        self._unsub: list[callable] = []

    async def async_start(self) -> None:
        """Listener registrieren."""
        self._unsubscribe_all()

        rooms = self._active_rooms()
        watch_list: set[str] = set()

        main_thermostat = self.config.get(CONF_MAIN_THERMOSTAT)
        main_sensor = self.config.get(CONF_MAIN_SENSOR)

        if isinstance(main_thermostat, str) and main_thermostat:
            watch_list.add(main_thermostat)

        if isinstance(main_sensor, str) and main_sensor:
            watch_list.add(main_sensor)

        for room in rooms.values():
            sensor = room.get("sensor")
            thermostat = room.get("thermostat")

            if isinstance(sensor, str) and sensor:
                watch_list.add(sensor)

            if isinstance(thermostat, str) and thermostat:
                watch_list.add(thermostat)

        if watch_list:
            self._unsub.append(
                async_track_state_change_event(
                    self.hass,
                    list(watch_list),
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

        _LOGGER.debug("SmartHeatingController gestartet, beobachtete Entities: %s", watch_list)

    async def async_stop(self) -> None:
        """Listener entfernen."""
        self._unsubscribe_all()

    def update_config(self, config: dict[str, Any]) -> None:
        """Konfiguration aktualisieren und Controller neu starten."""
        self.config = config
        self.hass.async_create_task(self.async_start())

    def _unsubscribe_all(self) -> None:
        """Alle Listener entfernen."""
        for unsub in self._unsub:
            try:
                unsub()
            except Exception:  # pragma: no cover
                _LOGGER.exception("Fehler beim Entfernen eines Listeners")
        self._unsub.clear()

    def _active_rooms(self) -> dict[str, dict[str, Any]]:
        """Aktive Räume zurückgeben."""
        rooms = self.config.get(CONF_ROOMS, {})
        if not isinstance(rooms, dict):
            return {}

        return {
            room_id: room_cfg
            for room_id, room_cfg in rooms.items()
            if isinstance(room_cfg, dict) and room_cfg.get("enabled", True)
        }

    def _is_night_for_room(self, room: dict[str, Any]) -> bool:
        """Prüfen, ob für den Raum Nachtbetrieb gilt."""
        now = dt_util.now().strftime("%H:%M")

        night_start = str(
            room.get(
                "night_start",
                self.config.get(CONF_NIGHT_START, DEFAULT_NIGHT_START),
            )
        )[:5]

        day_start = str(
            room.get(
                "day_start",
                self.config.get(CONF_MORNING_BOOST_END, DEFAULT_MORNING_BOOST_END),
            )
        )[:5]

        # Nacht über Mitternacht, z. B. 22:00 -> 06:00
        if night_start > day_start:
            return now >= night_start or now < day_start

        # Nacht innerhalb desselben Tages
        return night_start <= now < day_start

    def _target_for_room(self, room: dict[str, Any]) -> float:
        """Basis-Zieltemperatur für einen Raum bestimmen.

        Wichtig:
        Hier wird bewusst NICHT die aktuelle Thermostat-Solltemperatur gelesen,
        damit sich ein Boost nicht bei jedem Tick weiter aufaddiert.
        """
        if self._is_night_for_room(room):
            return float(room.get("target_night", DEFAULT_TARGET_NIGHT))

        return float(room.get("target_day", DEFAULT_TARGET_DAY))

    def _room_temp(self, room: dict[str, Any]) -> float | None:
        """Raumtemperatur über konfigurierten Sensor lesen."""
        sensor_id = room.get("sensor")
        if not sensor_id or not isinstance(sensor_id, str):
            return None

        state = self.hass.states.get(sensor_id)
        if state is None:
            return None

        if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        try:
            return float(state.state)
        except (ValueError, TypeError):
            _LOGGER.debug("Ungültiger Temperaturwert von %s: %s", sensor_id, state.state)
            return None

    def _main_reference_temp(self) -> float | None:
        """Referenztemperatur für das Hauptthermostat lesen.

        Priorität:
        1. explizit konfigurierter Hauptsensor (`main_sensor`)
        2. `current_temperature` des Hauptthermostats
        """
        main_sensor = self.config.get(CONF_MAIN_SENSOR)
        if isinstance(main_sensor, str) and main_sensor:
            sensor_state = self.hass.states.get(main_sensor)
            if sensor_state and sensor_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                try:
                    return float(sensor_state.state)
                except (ValueError, TypeError):
                    _LOGGER.warning(
                        "Ungültiger Wert für Hauptsensor %s: %s",
                        main_sensor,
                        sensor_state.state,
                    )

        main_thermostat = self.config.get(CONF_MAIN_THERMOSTAT)
        if isinstance(main_thermostat, str) and main_thermostat:
            thermostat_state = self.hass.states.get(main_thermostat)
            if thermostat_state:
                current_temp = thermostat_state.attributes.get("current_temperature")
                try:
                    if current_temp is not None:
                        return float(current_temp)
                except (ValueError, TypeError):
                    _LOGGER.warning(
                        "Ungültige current_temperature bei %s: %s",
                        main_thermostat,
                        current_temp,
                    )

        return None

    def _main_base_target(self) -> float:
        """Basis-Solltemperatur für das Hauptthermostat bestimmen.

        Hier wird der höchste Basisbedarf aller aktiven Räume verwendet.
        So orientiert sich das Hauptthermostat an den Raumzielen, ohne
        dass sich ein Boost aufschaukelt.
        """
        rooms = self._active_rooms()
        if not rooms:
            return float(DEFAULT_TARGET_DAY)

        return max(self._target_for_room(room) for room in rooms.values())

    def _set_temp_if_new(self, entity_id: str, temp: float) -> None:
        """Temperatur nur setzen, wenn sie sich relevant geändert hat."""
        state = self.hass.states.get(entity_id)
        if state is not None:
            current_target = state.attributes.get(ATTR_TEMPERATURE)
            try:
                if current_target is not None and abs(float(current_target) - float(temp)) < 0.1:
                    return
            except (ValueError, TypeError):
                pass

        _LOGGER.debug("Setze %s auf %.1f °C", entity_id, temp)

        self.hass.async_create_task(
            self.hass.services.async_call(
                CLIMATE_DOMAIN,
                "set_temperature",
                {
                    "entity_id": entity_id,
                    ATTR_TEMPERATURE: round(float(temp), 1),
                },
                blocking=True,
            )
        )

    def _evaluate(self) -> None:
        """Alle Räume prüfen und Solltemperaturen aktualisieren."""
        rooms = self._active_rooms()
        if not rooms:
            _LOGGER.debug("Keine aktiven Räume konfiguriert")
            return

        try:
            boost_delta = float(self.config.get(CONF_BOOST_DELTA, DEFAULT_BOOST_DELTA))
        except (ValueError, TypeError):
            boost_delta = float(DEFAULT_BOOST_DELTA)

        needs_heat: dict[str, bool] = {}

        for room_id, room in rooms.items():
            actual_temp = self._room_temp(room)
            target_temp = self._target_for_room(room)

            needs_heat[room_id] = (
                actual_temp is not None and actual_temp < (target_temp - 0.5)
            )

            _LOGGER.debug(
                "Raum %s: Ist=%.2f Soll=%.2f Bedarf=%s",
                room_id,
                actual_temp if actual_temp is not None else float("nan"),
                target_temp,
                needs_heat[room_id],
            )

        any_room_needs_heat = any(needs_heat.values())

        # Hauptthermostat steuern
        main_thermostat = self.config.get(CONF_MAIN_THERMOSTAT)
        if isinstance(main_thermostat, str) and main_thermostat:
            main_base_target = self._main_base_target()
            main_reference_temp = self._main_reference_temp()

            # Optionaler Boost nur dann, wenn wirklich Heizbedarf besteht.
            # Basis ist die Haupt-Solltemperatur aus den Raumzielen, nicht die
            # aktuelle Thermostat-Solltemperatur.
            main_target = main_base_target

            if any_room_needs_heat and main_reference_temp is not None:
                # Nur boosten, wenn Referenztemperatur unter Basissoll liegt.
                if main_reference_temp < main_base_target - 0.2:
                    main_target = main_base_target + boost_delta

            self._set_temp_if_new(main_thermostat, main_target)

        # Raumthermostate steuern
        for room_id, room in rooms.items():
            thermostat_id = room.get("thermostat")
            if not isinstance(thermostat_id, str) or not thermostat_id:
                continue

            room_base_target = self._target_for_room(room)
            room_target = room_base_target + boost_delta if needs_heat[room_id] else room_base_target
            self._set_temp_if_new(thermostat_id, room_target)

    @callback
    def _on_state_change(self, event: Event) -> None:
        """Bei State-Änderungen neu auswerten."""
        self._evaluate()

    @callback
    def _on_minute_tick(self, now) -> None:
        """Minütliche Zeit-basierte Auswertung."""
        self._evaluate()
