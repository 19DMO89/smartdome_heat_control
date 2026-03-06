"""Smart Heating Controller – Kernlogik mit UI-Anbindung."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.const import ATTR_TEMPERATURE, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)

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
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

class SmartHeatingController:
    """Kernlogik: Reagiert auf UI-Eingaben und Sensorwerte."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = config
        self._unsub: list = []

    async def async_start(self) -> None:
        """Listener für Sensoren, Thermostate (UI) und Zeitsteuerung registrieren."""
        self._unsubscribe_all()

        active_rooms = self._active_rooms()
        
        # 1. Sensoren überwachen (Ist-Temperatur)
        sensors = [r["sensor"] for r in active_rooms.values() if r.get("sensor")]
        # 2. Thermostate überwachen (Soll-Temperatur aus der UI)
        thermostats = [r["thermostat"] for r in active_rooms.values() if r.get("thermostat")]
        
        watch_list = list(set(sensors + thermostats))
        
        if watch_list:
            self._unsub.append(
                async_track_state_change_event(self.hass, watch_list, self._on_state_change)
            )

        # Prüft jede Minute auf Zeitplan-Wechsel
        self._unsub.append(
            async_track_time_change(self.hass, self._on_minute_tick, second=0)
        )

        _LOGGER.info("Smart Heating Controller aktiv: Überwachungskreis für %s Entitäten erstellt", len(watch_list))

    async def async_stop(self) -> None:
        self._unsubscribe_all()

    def update_config(self, config: dict[str, Any]) -> None:
        self.config = config
        self.hass.async_create_task(self.async_start())

    def _unsubscribe_all(self) -> None:
        for unsub in self._unsub:
            unsub()
        self._unsub.clear()

    # ── Zielwert-Logik (Berücksichtigt UI) ──────────────────────────────────

    def _target_for_room(self, room: dict) -> float:
        """Ermittelt die Zieltemperatur (Priorität: UI-Einstellung)."""
        t_id = room.get("thermostat")
        state = self.hass.states.get(t_id) if t_id else None
        
        # Wenn in der UI ein Wert gesetzt wurde, nehmen wir diesen
        if state and ATTR_TEMPERATURE in state.attributes:
            try:
                ui_temp = float(state.attributes[ATTR_TEMPERATURE])
                if ui_temp > 0: # Plausibilitätscheck
                    return ui_temp
            except (ValueError, TypeError):
                pass

        # Fallback auf Zeitplan (Config)
        if self._is_night_for_room(room):
            return float(room.get("target_night", DEFAULT_TARGET_NIGHT))
        return float(room.get("target_day", DEFAULT_TARGET_DAY))

    def _is_night_for_room(self, room: dict) -> bool:
        now = datetime.now().strftime("%H:%M")
        ns = str(room.get("night_start", self.config.get(CONF_NIGHT_START, DEFAULT_NIGHT_START)))[:5]
        ds = str(room.get("day_start", self.config.get(CONF_MORNING_BOOST_END, DEFAULT_MORNING_BOOST_END)))[:5]
        
        if ns > ds:
            return now >= ns or now < ds
        return ns <= now < ds

    # ── Kern-Logik (Evaluation) ───────────────────────────────────────────────

    def _evaluate(self) -> None:
        rooms = self._active_rooms()
        if not rooms:
            return

        boost_delta = self.config.get(CONF_BOOST_DELTA, DEFAULT_BOOST_DELTA)
        hysterese = 0.5
        needs_heat = {}

        for rid, room in rooms.items():
            temp = self._room_temp(room)
            target = self._target_for_room(room)
            
            if temp is None:
                needs_heat[rid] = False
                continue

            # Harte Abschaltung bei Erreichen der Zieltemperatur
            if temp >= target:
                needs_heat[rid] = False
                continue

            # Einschaltlogik mit Hysterese
            needs_heat[rid] = temp < (target - hysterese)

        # ── Hauptthermostat Logik ──
        any_cold = any(needs_heat.values())
        main_id = self.config.get(CONF_MAIN_THERMOSTAT)
        main_state = self.hass.states.get(main_id) if main_id else None
        
        if any_cold and main_state:
            main_current = main_state.attributes.get("current_temperature")
            final_main = float(main_current) + boost_delta if main_current else 24.0
        else:
            final_main = 22.0

        self._main_set_temp_if_new(final_main)

        # ── Einzel-Thermostate setzen (Boost-Logik) ──
        for rid, room in rooms.items():
            t_id = room.get("thermostat")
            if not t_id: continue

            target = self._target_for_room(room)
            temp = self._room_temp(room)
            
            # Wenn Wärme gebraucht wird: Setze Ziel + Boost (damit das Ventil voll öffnet)
            # Wenn warm genug: Setze exakten Zielwert (Ventil drosselt)
            if needs_heat[rid]:
                new_val = target + boost_delta
            else:
                new_val = target
            
            self._set_temp_if_new(t_id, new_val)

    # ── Hilfsfunktionen ───────────────────────────────────────────────────────

    def _active_rooms(self) -> dict:
        return {k: v for k, v in self.config.get(CONF_ROOMS, {}).items() if v.get("enabled", True)}

    def _room_temp(self, room: dict) -> float | None:
        sensor = room.get("sensor")
        if not sensor: return None
        state = self.hass.states.get(sensor)
        if not state or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN): return None
        try: return float(state.state)
        except ValueError: return None

    def _set_temp_if_new(self, entity_id: str, temp: float) -> None:
        state = self.hass.states.get(entity_id)
        if state:
            current = state.attributes.get(ATTR_TEMPERATURE)
            if current is not None and abs(float(current) - float(temp))  None:
        main = self.config.get(CONF_MAIN_THERMOSTAT)
        if main: self._set_temp_if_new(main, temp)

    @callback
    def _on_state_change(self, event) -> None:
        """Wird ausgelöst bei Sensor- ODER UI-Änderungen."""
        self._evaluate()

    @callback
    def _on_minute_tick(self, now) -> None:
        self._evaluate()
