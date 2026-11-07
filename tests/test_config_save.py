"""Tests: Speichern erhält den Regelzustand, Live-Status für die Kacheln."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from conftest import FakeHass, controller_module
from conftest import const_module as const

ROOM = "wohnzimmer"
AC = "climate.wohnzimmer_klima"
SENSOR = "sensor.wohnzimmer"


def _room(**extra) -> dict:
    return {const.CONF_ROOM_SENSOR: SENSOR, const.CONF_ROOM_TARGET_DAY: 21.0, **extra}


def _config(**room_extra) -> dict:
    return {const.CONF_ROOMS: {ROOM: _room(**room_extra)}}


@pytest.fixture
def ctrl(clock):
    c = controller_module.SmartHeatingController(FakeHass(), _config())
    c.async_start = MagicMock()
    c.hass.async_create_task = lambda task: task
    c._effective_target_for_room = lambda room: 21.0
    return c


def _heating(c) -> None:
    c._room_state[ROOM] = controller_module.ROOM_STATE_HEATING
    c._desired_targets["climate.ventil"] = 23.0
    c._last_hvac_mode[AC] = "heat"
    c._last_command_sent_at["climate.ventil"] = 1.0


def test_speichern_behaelt_heizzustand_und_vergisst_befehle(ctrl):
    _heating(ctrl)
    ctrl.update_config(_config())
    assert ctrl._room_state[ROOM] == controller_module.ROOM_STATE_HEATING
    assert ctrl._desired_targets == {}
    assert ctrl._last_hvac_mode == {}
    assert ctrl._last_command_sent_at == {}


def test_speichern_behaelt_fensterpause_und_aussensperre(ctrl):
    ctrl._window_paused_rooms.add(ROOM)
    ctrl._window_open_since[ROOM] = 5.0
    ctrl._outdoor_cutoff_latched = True
    ctrl.update_config(_config())
    assert ROOM in ctrl._window_paused_rooms
    assert ctrl._window_open_since[ROOM] == 5.0
    assert ctrl._outdoor_cutoff_latched is True


def test_entfernter_raum_wird_vergessen(ctrl):
    _heating(ctrl)
    ctrl._window_paused_rooms.add(ROOM)
    ctrl._room_sensor_fault.add(ROOM)
    ctrl.update_config({const.CONF_ROOMS: {}})
    assert ROOM not in ctrl._room_state
    assert ROOM not in ctrl._window_paused_rooms
    assert ROOM not in ctrl._room_sensor_fault


def test_deaktivierter_raum_startet_danach_neu(ctrl):
    _heating(ctrl)
    ctrl.update_config(_config(**{const.CONF_ROOM_ENABLED: False}))
    assert ROOM not in ctrl._room_state


def test_entfernter_sensor_friert_heizen_nicht_ein(ctrl):
    _heating(ctrl)
    ctrl._room_sensor_fault.add(ROOM)
    ctrl.update_config(_config(**{const.CONF_ROOM_SENSOR: ""}))
    assert ROOM not in ctrl._room_state
    assert ROOM not in ctrl._room_sensor_fault


def test_status_zeigt_raumziel_statt_ventilwert(ctrl):
    ctrl._last_room_states[ROOM] = {
        "state": controller_module.ROOM_STATE_HEATING,
        "target": 21.0,
        "control_target": 19.0,
        "outdoor_cutoff_active": True,
        "outdoor_minimum_active": True,
    }
    status = ctrl.get_panel_room_status()[ROOM]
    assert status["state"] == controller_module.ROOM_STATE_HEATING
    assert status["target"] == 19.0
    assert status["cooling"] is False
    assert status["outdoor_minimum_active"] is True


def test_status_ohne_auswertung_nutzt_planwert(ctrl):
    assert ctrl.get_panel_room_status()[ROOM]["target"] == 21.0


def test_kuehlen_nur_mit_klimaanlage(clock):
    with_ac = controller_module.SmartHeatingController(
        FakeHass(),
        {
            const.CONF_COOLING_ENABLED: True,
            const.CONF_ROOMS: {
                "mit": _room(**{const.CONF_ROOM_CLIMATE_ENTITY: AC, const.CONF_ROOM_COOL_TARGET_DAY: 24.0}),
                "ohne": _room(),
            },
        },
    )
    with_ac._effective_target_for_room = lambda room: 21.0
    status = with_ac.get_panel_room_status()
    assert status["mit"]["cooling"] is True
    assert status["mit"]["target"] == 24.0
    assert status["ohne"]["cooling"] is False
    assert status["ohne"]["cooling_active"] is True
    assert status["ohne"]["target"] == 21.0
