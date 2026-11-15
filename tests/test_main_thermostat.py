"""Tests für den Sollwert des Hauptthermostats und die Wärmeanforderung der Räume."""

from __future__ import annotations

from conftest import const_module as const
from conftest import controller_module

MAIN = "climate.wand"
VALVE = "climate.klo_valve"


def _target(ctrl, sensor_temp, own_temp, boost_delta=2.0, fallback=21.0, **attrs):
    ctrl.hass.states.set(MAIN, None, current_temperature=own_temp, **attrs)
    ctrl._get_state_float = lambda entity_id: sensor_temp if entity_id else None
    sensor_id = "sensor.wand" if sensor_temp is not None else None
    return ctrl._main_heating_target(MAIN, sensor_id, boost_delta, fallback)


def test_basis_ist_die_hoehere_der_beiden_messungen(make_controller):
    ctrl = make_controller()
    assert _target(ctrl, sensor_temp=23.0, own_temp=23.0) == 25.0
    assert _target(ctrl, sensor_temp=20.0, own_temp=23.0) == 25.0
    assert _target(ctrl, sensor_temp=24.0, own_temp=22.0) == 26.0


def test_mindestens_zwei_grad_auch_bei_kleinem_boost_delta(make_controller):
    ctrl = make_controller()
    assert _target(ctrl, sensor_temp=22.0, own_temp=22.0, boost_delta=0.5) == 24.0
    assert _target(ctrl, sensor_temp=22.0, own_temp=22.0, boost_delta=3.0) == 25.0


def test_ohne_messwerte_gilt_der_raumsollwert(make_controller):
    ctrl = make_controller()
    ctrl.hass.states.set(MAIN, None)
    ctrl._get_state_float = lambda entity_id: None
    assert ctrl._main_heating_target(MAIN, None, 2.0, 21.0) == 23.0


def test_deckelung_auf_maximaltemperatur(make_controller):
    ctrl = make_controller()
    assert _target(ctrl, sensor_temp=29.0, own_temp=29.0, max_temp=30.0) == 30.0


def _room(**extra):
    return {const.CONF_ROOM_THERMOSTAT: VALVE, **extra}


def test_raum_mit_sensor_nutzt_zustandsmaschine(make_controller):
    ctrl = make_controller()
    room = _room(**{const.CONF_ROOM_SENSOR: "sensor.klo"})
    assert ctrl._room_needs_heat(room, {"state": controller_module.ROOM_STATE_HEATING})
    ctrl.hass.states.set(VALVE, None, hvac_action="heating")
    assert not ctrl._room_needs_heat(room, {"state": controller_module.ROOM_STATE_IDLE})


def test_raum_ohne_sensor_fordert_an_wenn_ventil_heizt(make_controller):
    ctrl = make_controller()
    idle = {"state": controller_module.ROOM_STATE_IDLE}
    ctrl.hass.states.set(VALVE, None, hvac_action="heating")
    assert ctrl._room_needs_heat(_room(), idle)
    ctrl.hass.states.set(VALVE, None, hvac_action="idle")
    assert not ctrl._room_needs_heat(_room(), idle)


def test_fensterpause_und_klimaanlage_fordern_nicht_an(make_controller):
    ctrl = make_controller()
    ctrl.hass.states.set(VALVE, None, hvac_action="heating")
    paused = {"state": controller_module.ROOM_STATE_IDLE, "pause_active": True}
    assert not ctrl._room_needs_heat(_room(), paused)
    ac_room = _room(
        **{const.CONF_ROOM_CLIMATE_ENTITY: "climate.ac", const.CONF_ROOM_USE_CLIMATE: True}
    )
    assert not ctrl._room_needs_heat(ac_room, {"state": controller_module.ROOM_STATE_IDLE})


def test_restwaerme_nur_mit_include_residual(make_controller):
    ctrl = make_controller()
    room = _room(**{const.CONF_ROOM_SENSOR: "sensor.klo"})
    hold = {"state": controller_module.ROOM_STATE_RESIDUAL_HOLD}
    assert not ctrl._room_needs_heat(room, hold)
    assert ctrl._room_needs_heat(room, hold, include_residual=True)


def test_klima_raum_fordert_auch_im_zustand_heizt_nicht_an(make_controller):
    ctrl = make_controller()
    ac_room = _room(
        **{
            const.CONF_ROOM_SENSOR: "sensor.klo",
            const.CONF_ROOM_CLIMATE_ENTITY: "climate.ac",
            const.CONF_ROOM_USE_CLIMATE: True,
        }
    )
    heating = {"state": controller_module.ROOM_STATE_HEATING}
    assert not ctrl._room_needs_heat(ac_room, heating)
    assert not ctrl._room_needs_heat(ac_room, heating, include_residual=True)
    # Klimaanlage eingetragen, aber nicht zum Heizen genutzt: normale Anforderung.
    ac_room[const.CONF_ROOM_USE_CLIMATE] = False
    assert ctrl._room_needs_heat(ac_room, heating)
