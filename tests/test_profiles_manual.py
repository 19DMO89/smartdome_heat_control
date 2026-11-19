"""Zeitplan-Profile und manuelle Bedienung am Thermostat."""

from __future__ import annotations

import datetime
import types

import pytest

from conftest import FakeHass
from conftest import const_module as const
from conftest import controller_module

TRV = "climate.wz_trv"


class DateClock:
    def __init__(self) -> None:
        # Donnerstag, 19.11.2026, 10:00
        self.current = datetime.datetime(2026, 11, 19, 10, 0, 0)

    def now(self):
        return self.current

    def advance(self, seconds: float) -> None:
        self.current += datetime.timedelta(seconds=seconds)


@pytest.fixture
def date_clock(monkeypatch):
    clock = DateClock()
    monkeypatch.setattr(controller_module, "dt_util", clock)
    return clock


def _state(hass, entity_id, state, **attrs):
    hass.states._states[entity_id] = types.SimpleNamespace(
        entity_id=entity_id, state=state, attributes=attrs
    )


def _schedule(thursday):
    days = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    return {day: (thursday if day == "thursday" else []) for day in days}


def _controller(room_extra=None, config_extra=None, room_temp="21.0"):
    hass = FakeHass()
    room = {
        "label": "Wohnzimmer",
        const.CONF_ROOM_THERMOSTAT: TRV,
        const.CONF_ROOM_SENSOR: "sensor.wz_temp",
        const.CONF_ROOM_TARGET_DAY: 21.0,
        const.CONF_ROOM_TARGET_NIGHT: 18.0,
        const.CONF_ROOM_ENABLED: True,
        const.CONF_ROOM_CONTROL_PROFILE: "self_regulating",
        **(room_extra or {}),
    }
    config = {
        "enabled": True,
        const.CONF_TOLERANCE: 0.5,
        const.CONF_ROOMS: {"wz": room},
        **(config_extra or {}),
    }
    _state(hass, "sensor.wz_temp", room_temp)
    _state(hass, TRV, "heat", temperature=21.0, min_temp=5, max_temp=30)
    return controller_module.SmartHeatingController(hass, config), hass


def _target(ctrl):
    return ctrl._last_room_states["wz"]["target"]


# --- Zeitplan-Profile -----------------------------------------------------


def test_standardprofil_nutzt_bisheriges_wochenschema(date_clock):
    ctrl, _ = _controller({const.CONF_ROOM_WEEKLY_SCHEDULE: _schedule([{"start": "08:00", "temperature": 22.5}])})
    ctrl._evaluate()
    assert _target(ctrl) == 22.5


def test_aktives_profil_bestimmt_den_plan(date_clock):
    room = {
        const.CONF_ROOM_WEEKLY_SCHEDULE: _schedule([{"start": "08:00", "temperature": 22.5}]),
        const.CONF_ROOM_WEEKLY_SCHEDULES: {
            "homeoffice": _schedule([{"start": "08:00", "temperature": 23.5}])
        },
    }
    config = {
        const.CONF_SCHEDULE_PROFILES: {
            "default": {"label": "Standard"},
            "homeoffice": {"label": "Homeoffice"},
        },
        const.CONF_ACTIVE_SCHEDULE_PROFILE: "homeoffice",
    }
    ctrl, _ = _controller(room, config)
    ctrl._evaluate()
    assert _target(ctrl) == 23.5


def test_raum_ohne_plan_im_profil_nutzt_tag_nacht(date_clock):
    room = {const.CONF_ROOM_WEEKLY_SCHEDULE: _schedule([{"start": "08:00", "temperature": 22.5}])}
    config = {
        const.CONF_SCHEDULE_PROFILES: {"default": {"label": "Standard"}, "ferien": {"label": "Ferien"}},
        const.CONF_ACTIVE_SCHEDULE_PROFILE: "ferien",
    }
    ctrl, _ = _controller(room, config)
    ctrl._evaluate()
    assert _target(ctrl) == 21.0


def test_unbekanntes_profil_faellt_auf_standard_zurueck(date_clock):
    room = {const.CONF_ROOM_WEEKLY_SCHEDULE: _schedule([{"start": "08:00", "temperature": 22.5}])}
    ctrl, _ = _controller(room, {const.CONF_ACTIVE_SCHEDULE_PROFILE: "geloescht"})
    ctrl._evaluate()
    assert _target(ctrl) == 22.5


# --- Manuelle Bedienung ---------------------------------------------------


def _turn_trv(ctrl, hass, new_value):
    old = hass.states.get(TRV)
    _state(hass, TRV, "heat", temperature=new_value, min_temp=5, max_temp=30)
    event = types.SimpleNamespace(
        data={"entity_id": TRV, "old_state": old, "new_state": hass.states.get(TRV)}
    )
    ctrl._on_state_change(event)


def _ready(date_clock, config_extra=None, room_extra=None):
    config = {const.CONF_MANUAL_OVERRIDE_ENABLED: True, **(config_extra or {})}
    ctrl, hass = _controller(room_extra, config)
    ctrl._evaluate()  # sendet den Leerlauf-Sollwert ans Ventil
    _state(hass, TRV, "heat", temperature=ctrl._desired_targets[TRV], min_temp=5, max_temp=30)
    date_clock.advance(600)
    return ctrl, hass


def test_von_hand_hoeher_gedreht_wird_zieltemperatur(date_clock):
    ctrl, hass = _ready(date_clock)
    _turn_trv(ctrl, hass, 24.0)
    assert _target(ctrl) == 24.0
    assert ctrl.get_panel_room_status()["wz"]["manual_override"]["target"] == 24.0


def test_manuell_endet_beim_naechsten_wechsel(date_clock):
    schedule = _schedule([{"start": "08:00", "temperature": 21.0}, {"start": "12:00", "temperature": 21.0}])
    ctrl, hass = _ready(date_clock, room_extra={const.CONF_ROOM_WEEKLY_SCHEDULE: schedule})
    _turn_trv(ctrl, hass, 24.0)
    date_clock.advance(3600)  # 11:10, gleicher Block
    ctrl._evaluate()
    assert _target(ctrl) == 24.0
    date_clock.advance(3600)  # 12:10, neuer Block (gleiche Temperatur)
    ctrl._evaluate()
    assert _target(ctrl) == 21.0
    assert ctrl.get_panel_room_status()["wz"]["manual_override"] is None


def test_manuell_endet_am_abend_auch_ohne_nachtabsenkung(date_clock):
    ctrl, hass = _ready(date_clock, room_extra={const.CONF_ROOM_NIGHT_SETBACK_ENABLED: False})
    _turn_trv(ctrl, hass, 24.0)
    date_clock.advance(11 * 3600)  # 21:10
    ctrl._evaluate()
    assert _target(ctrl) == 24.0
    date_clock.advance(3600)  # 22:10, Nachtbeginn
    ctrl._evaluate()
    assert _target(ctrl) == 21.0


def test_klima_von_hand_verstellt_wird_zieltemperatur(date_clock):
    room = {const.CONF_ROOM_CLIMATE_ENTITY: "climate.wz_ac", const.CONF_ROOM_USE_CLIMATE: True}
    ctrl, hass = _controller(room, {const.CONF_MANUAL_OVERRIDE_ENABLED: True}, room_temp="19.0")
    _state(hass, "climate.wz_ac", "off", temperature=20, min_temp=16, max_temp=30)
    ctrl._evaluate()  # Raum heizt: Klima an, 21 °C
    _state(hass, "climate.wz_ac", "heat", temperature=21.0, min_temp=16, max_temp=30)
    date_clock.advance(600)
    old = hass.states.get("climate.wz_ac")
    _state(hass, "climate.wz_ac", "heat", temperature=23.0, min_temp=16, max_temp=30)
    ctrl._on_state_change(
        types.SimpleNamespace(
            data={"entity_id": "climate.wz_ac", "old_state": old, "new_state": hass.states.get("climate.wz_ac")}
        )
    )
    assert _target(ctrl) == 23.0
    assert ctrl._desired_targets["climate.wz_ac"] == 23.0


def test_manuell_endet_beim_profilwechsel(date_clock):
    config = {const.CONF_SCHEDULE_PROFILES: {"default": {"label": "Standard"}, "ferien": {"label": "Ferien"}}}
    ctrl, hass = _ready(date_clock, config_extra=config)
    _turn_trv(ctrl, hass, 24.0)
    ctrl.config[const.CONF_ACTIVE_SCHEDULE_PROFILE] = "ferien"
    ctrl._evaluate()
    assert _target(ctrl) == 21.0


def test_eigener_befehl_gilt_nicht_als_manuell(date_clock):
    ctrl, hass = _ready(date_clock)
    ctrl._last_command_sent_at[TRV] = date_clock.now().timestamp()  # gerade gesendet
    _turn_trv(ctrl, hass, 24.0)
    assert _target(ctrl) == 21.0


def test_ventil_auf_minimum_ist_keine_uebersteuerung(date_clock):
    ctrl, hass = _ready(date_clock)
    _turn_trv(ctrl, hass, 5.0)  # Fensterfunktion / aus
    assert ctrl.get_panel_room_status()["wz"]["manual_override"] is None


def test_ohne_einstellung_keine_uebersteuerung(date_clock):
    ctrl, hass = _ready(date_clock, config_extra={const.CONF_MANUAL_OVERRIDE_ENABLED: False})
    _turn_trv(ctrl, hass, 24.0)
    assert _target(ctrl) == 21.0


def test_offset_wird_abgezogen(date_clock):
    ctrl, hass = _ready(date_clock, room_extra={const.CONF_ROOM_THERMOSTAT_OFFSET: 1.0})
    _turn_trv(ctrl, hass, 24.0)
    assert _target(ctrl) == 23.0


def test_automatik_per_dienst_zurueck(date_clock):
    ctrl, hass = _ready(date_clock)
    _turn_trv(ctrl, hass, 24.0)
    ctrl.clear_manual_override("wz")
    assert _target(ctrl) == 21.0
