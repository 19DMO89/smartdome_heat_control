"""End-to-End: Hauptthermostat folgt dem Wärmebedarf der Räume."""

from __future__ import annotations

import datetime
import types

import pytest

from conftest import FakeHass
from conftest import const_module as const
from conftest import controller_module

WALL = "climate.wand"
CIRCUIT_VALVE = "climate.kreis_og"


class DateClock:
    def __init__(self) -> None:
        self.current = datetime.datetime(2026, 11, 15, 12, 0, 0)

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


def _room(name, target, circuit_id=""):
    return {
        "label": name,
        const.CONF_ROOM_THERMOSTAT: f"climate.{name}_trv",
        const.CONF_ROOM_SENSOR: f"sensor.{name}_temp",
        const.CONF_ROOM_TARGET_DAY: target,
        const.CONF_ROOM_TARGET_NIGHT: 18.0,
        const.CONF_ROOM_ENABLED: True,
        const.CONF_ROOM_CIRCUIT_ID: circuit_id,
    }


def _controller(circuits=None, klo_circuit="", wz_circuit=""):
    """Klo 16 °C (braucht Wärme), Wohnzimmer 23 °C, Wandthermostat-Fühler 23 °C."""
    hass = FakeHass()
    config = {
        "enabled": True,
        const.CONF_MAIN_THERMOSTAT: WALL,
        const.CONF_MAIN_SENSOR: "sensor.wand_temp",
        const.CONF_BOOST_DELTA: 2.0,
        const.CONF_TOLERANCE: 0.5,
        const.CONF_ROOMS: {
            "klo": _room("klo", 21.0, klo_circuit),
            "wz": _room("wz", 22.0, wz_circuit),
        },
    }
    if circuits is not None:
        config[const.CONF_CIRCUITS] = circuits
    _state(hass, "sensor.klo_temp", "16.0")
    _state(hass, "sensor.wz_temp", "23.0")
    _state(hass, "sensor.wand_temp", "23.0")
    for entity_id, current in ((WALL, 23.0), (CIRCUIT_VALVE, 20.0)):
        _state(hass, entity_id, "heat", temperature=22.5, current_temperature=current, min_temp=5, max_temp=30)
    for name in ("klo", "wz"):
        _state(hass, f"climate.{name}_trv", "heat", temperature=18, min_temp=5, max_temp=30)
    return controller_module.SmartHeatingController(hass, config), hass


def _sent(hass, entity_id):
    return [
        data["temperature"]
        for _domain, service, data in hass.service_calls
        if service == "set_temperature" and data["entity_id"] == entity_id
    ]


def test_wandthermostat_geht_zwei_grad_ueber_ist(date_clock):
    ctrl, hass = _controller()
    ctrl._evaluate()
    assert _sent(hass, WALL) == [25.0]


def test_leerer_heizkreis_schaltet_hauptthermostat_nicht_ab(date_clock):
    ctrl, hass = _controller(circuits={"og": {"label": "OG", "main_thermostat": ""}})
    ctrl._evaluate()
    assert _sent(hass, WALL) == [25.0]


def test_raum_im_heizkreis_heizt_ueber_kreis_nicht_ueber_hauptthermostat(date_clock):
    circuits = {"og": {"label": "OG", "main_thermostat": CIRCUIT_VALVE}}
    ctrl, hass = _controller(circuits=circuits, klo_circuit="og")
    ctrl._evaluate()
    assert _sent(hass, CIRCUIT_VALVE) == [22.0]  # Eigentemperatur 20 °C + 2 °C
    assert _sent(hass, WALL) == [5.0]  # Wohnzimmer (global) braucht keine Wärme


def test_ohne_globale_raeume_bleibt_hauptthermostat_unberuehrt(date_clock):
    circuits = {"og": {"label": "OG", "main_thermostat": CIRCUIT_VALVE}}
    ctrl, hass = _controller(circuits=circuits, klo_circuit="og", wz_circuit="og")
    ctrl._evaluate()
    assert _sent(hass, WALL) == []


def test_verlorener_sollwert_wird_nach_wartezeit_erneut_gesendet(date_clock):
    ctrl, hass = _controller()
    ctrl._evaluate()
    # Das Gerät meldet weiter 22,5 °C (eigenes Zeitprogramm / am Gerät verstellt).
    date_clock.advance(60)
    ctrl._evaluate()
    assert _sent(hass, WALL) == [25.0]
    date_clock.advance(const.MAIN_RESEND_INTERVAL)
    ctrl._evaluate()
    assert _sent(hass, WALL) == [25.0, 25.0]


def test_uebernommener_sollwert_wird_nicht_wiederholt(date_clock):
    ctrl, hass = _controller()
    ctrl._evaluate()
    hass.states.get(WALL).attributes["temperature"] = 25.0
    date_clock.advance(const.MAIN_RESEND_INTERVAL + 60)
    ctrl._evaluate()
    assert _sent(hass, WALL) == [25.0]


def _use_ac_in_klo(ctrl, hass):
    klo = ctrl.config[const.CONF_ROOMS]["klo"]
    klo[const.CONF_ROOM_CLIMATE_ENTITY] = "climate.klo_ac"
    klo[const.CONF_ROOM_USE_CLIMATE] = True
    _state(hass, "climate.klo_ac", "off", temperature=20, min_temp=16, max_temp=30)


def test_klima_raum_schaltet_hauptthermostat_nicht_ein(date_clock):
    ctrl, hass = _controller()
    _use_ac_in_klo(ctrl, hass)
    ctrl._evaluate()
    assert ctrl._last_room_states["klo"]["state"] == controller_module.ROOM_STATE_HEATING
    assert _sent(hass, WALL) == [5.0]
    assert _sent(hass, "climate.klo_ac") == [21.0]


def test_heizkoerper_raum_schaltet_trotz_klima_raum_ein(date_clock):
    ctrl, hass = _controller()
    _use_ac_in_klo(ctrl, hass)
    _state(hass, "sensor.wz_temp", "19.0")  # Wohnzimmer braucht Wärme über Heizkörper
    ctrl._evaluate()
    assert _sent(hass, WALL) == [25.0]
