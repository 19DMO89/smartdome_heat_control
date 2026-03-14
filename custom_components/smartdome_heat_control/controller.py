"""Smart Heating Controller."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.const import ATTR_TEMPERATURE, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ROOMS,
    CONF_MAIN_THERMOSTAT,
    CONF_ROOM_SENSOR,
    CONF_ROOM_THERMOSTAT,
    CONF_ROOM_WINDOW_SENSOR,
    CONF_ROOM_CONTROL_PROFILE,
    CONF_HEATING_MODE,
    CONF_BOOST_DELTA,
    CONF_TOLERANCE,
    CONF_ENERGY_RESIDUAL_HEAT_HOLD,
    CONTROL_PROFILE_STANDARD,
    CONTROL_PROFILE_SELF_REGULATING,
    DEFAULT_BOOST_DELTA,
    DEFAULT_TOLERANCE,
)

_LOGGER = logging.getLogger(__name__)

ROOM_STATE_IDLE = "idle"
ROOM_STATE_HEATING = "heating"
ROOM_STATE_RESIDUAL_HOLD = "residual_hold"


class SmartHeatingController:
    """Main controller."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = config

        self._enabled = True
        self._unsub = []

        self._desired_targets: dict[str, float] = {}
        self._room_state: dict[str, str] = {}
        self._residual_heat_hold_until: dict[str, float] = {}
        self._last_command_sent_at: dict[str, float] = {}

    async def async_start(self) -> None:
        """Start controller."""

        self._unsubscribe_all()

        rooms = self.config.get(CONF_ROOMS, {})
        watch_entities = []

        for room in rooms.values():
            sensor = room.get(CONF_ROOM_SENSOR)
            window = room.get(CONF_ROOM_WINDOW_SENSOR)

            if sensor:
                watch_entities.append(sensor)

            if window:
                watch_entities.append(window)

        if watch_entities:
            self._unsub.append(
                async_track_state_change_event(
                    self.hass,
                    watch_entities,
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
        """Stop controller."""
        self._unsubscribe_all()

    def _unsubscribe_all(self) -> None:
        for unsub in self._unsub:
            try:
                unsub()
            except Exception:
                _LOGGER.exception("Failed to unsubscribe")

        self._unsub.clear()

    def _safe_float(self, value: Any) -> float | None:
        try:
            return float(value)
        except Exception:
            return None

    def _get_room_temp(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None

        state = self.hass.states.get(entity_id)

        if not state:
            return None

        if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None

        return self._safe_float(state.state)

    def _thermostat_min_temp(self, entity_id: str) -> float:
        state = self.hass.states.get(entity_id)

        if state:
            val = self._safe_float(state.attributes.get("min_temp"))
            if val is not None:
                return val

        return 5.0

    def _thermostat_step(self, entity_id: str) -> float:
        state = self.hass.states.get(entity_id)

        if state:
            step = self._safe_float(state.attributes.get("target_temp_step"))
            if step:
                return step

        return 0.5

    def _round_step(self, value: float, step: float) -> float:
        return round(round(value / step) * step, 2)

    def _set_temp_if_needed(
        self,
        entity_id: str,
        temp: float,
        min_interval: float = 0.0,
    ) -> None:

        step = self._thermostat_step(entity_id)
        desired = self._round_step(temp, step)

        previous = self._desired_targets.get(entity_id)

        if previous is not None and abs(previous - desired) < 0.01:
            return

        now = dt_util.now().timestamp()
        last = self._last_command_sent_at.get(entity_id, 0)

        if min_interval > 0 and now - last < min_interval:
            return

        self._desired_targets[entity_id] = desired
        self._last_command_sent_at[entity_id] = now

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

    def _get_room_profile(self, room: dict[str, Any]) -> str:
        profile = room.get(CONF_ROOM_CONTROL_PROFILE, CONTROL_PROFILE_STANDARD)

        if profile == CONTROL_PROFILE_SELF_REGULATING:
            return CONTROL_PROFILE_SELF_REGULATING

        return CONTROL_PROFILE_STANDARD

    def _get_interval(self, room: dict[str, Any]) -> float:
        if self._get_room_profile(room) == CONTROL_PROFILE_SELF_REGULATING:
            return 120.0

        return 0.0

    def _update_room_state(
        self,
        room_id: str,
        target: float,
        actual: float | None,
        tolerance: float,
    ) -> str:

        current_state = self._room_state.get(room_id, ROOM_STATE_IDLE)

        if actual is None:
            self._room_state[room_id] = ROOM_STATE_IDLE
            return ROOM_STATE_IDLE

        if current_state == ROOM_STATE_IDLE:
            if actual < target - tolerance:
                self._room_state[room_id] = ROOM_STATE_HEATING
                return ROOM_STATE_HEATING

        if current_state == ROOM_STATE_HEATING:
            if actual >= target:
                self._room_state[room_id] = ROOM_STATE_IDLE
                return ROOM_STATE_IDLE

        return current_state

    def _evaluate(self) -> None:

        rooms = self.config.get(CONF_ROOMS, {})

        boost = self._safe_float(self.config.get(CONF_BOOST_DELTA, DEFAULT_BOOST_DELTA))
        tolerance = self._safe_float(self.config.get(CONF_TOLERANCE, DEFAULT_TOLERANCE))

        if boost is None:
            boost = DEFAULT_BOOST_DELTA

        if tolerance is None:
            tolerance = DEFAULT_TOLERANCE

        any_heating = False
        room_targets = {}

        for room_id, room in rooms.items():

            sensor = room.get(CONF_ROOM_SENSOR)
            thermostat = room.get(CONF_ROOM_THERMOSTAT)

            if not thermostat:
                continue

            actual = self._get_room_temp(sensor)
            target = room.get("target_day", 21)

            state = self._update_room_state(
                room_id,
                target,
                actual,
                tolerance,
            )

            if state == ROOM_STATE_HEATING:
                any_heating = True
                room_target = target + boost
            else:
                room_target = target - 1

            room_targets[room_id] = room_target

            interval = self._get_interval(room)

            self._set_temp_if_needed(
                thermostat,
                room_target,
                interval,
            )

        main = self.config.get(CONF_MAIN_THERMOSTAT)

        if main and room_targets:
            main_target = max(room_targets.values())

            if any_heating:
                main_target += boost

            self._set_temp_if_needed(main, main_target)

    @callback
    def _on_state_change(self, event) -> None:
        self._evaluate()

    @callback
    def _on_minute_tick(self, now) -> None:
        self._evaluate()
