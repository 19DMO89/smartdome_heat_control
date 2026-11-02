"""Tests für den optionalen, zeitlich begrenzten Komfort-Override pro Raum."""

from __future__ import annotations

import types
from unittest.mock import MagicMock

import pytest
from conftest import const_module as const

VALVE = "climate.wohnzimmer_valve"
ROOM_ID = "wohnzimmer"
PLANNED = 20.0


def _event(old: float, new: float):
    def state(value):
        return types.SimpleNamespace(attributes={"temperature": value})

    return types.SimpleNamespace(
        data={"entity_id": VALVE, "old_state": state(old), "new_state": state(new)}
    )


@pytest.fixture
def ctrl(make_controller, clock):
    """Raum mit aktiviertem Override; Valve steht auf dem geplanten Sollwert."""
    room = {
        const.CONF_ROOM_THERMOSTAT: VALVE,
        const.CONF_ROOM_COMFORT_OVERRIDE_ENABLED: True,
    }
    c = make_controller({ROOM_ID: room})
    c._comfort_override = {}
    c._recent_sent_targets = {}
    c._config_changed_at = 0.0
    c._window_last_active = {}
    c._window_paused_rooms = set()
    c._room_sensor_fault = set()
    c._effective_target_for_room = lambda room: PLANNED
    c._room_temp = lambda room: 18.0  # Raum ist kälter als der Wunsch
    c._is_window_open = lambda room: False
    c._desired_targets[VALVE] = PLANNED
    c._last_command_sent_at[VALVE] = clock.ts
    clock.advance(3600)  # letzter eigener Befehl liegt lange zurück
    return c


def _raise(ctrl, new=22.0, old=PLANNED):
    ctrl._on_state_change(_event(old, new))


def test_default_ist_aus(make_controller):
    c = make_controller()
    assert c._comfort_override_enabled({}) is False
    assert const.DEFAULT_ROOM_COMFORT_OVERRIDE_ENABLED is False


def test_anhebung_am_thermostat_startet_60_min_override(ctrl, clock):
    _raise(ctrl)
    assert ctrl._active_comfort_target(ROOM_ID) == 22.0
    assert ctrl.get_room_target_temperature(ROOM_ID) == 22.0

    clock.advance(const.COMFORT_OVERRIDE_DURATION_SECONDS - 1)
    assert ctrl._active_comfort_target(ROOM_ID) == 22.0
    clock.advance(2)
    assert ctrl._active_comfort_target(ROOM_ID) is None
    assert ROOM_ID not in ctrl._comfort_override


def test_plan_bleibt_unveraendert(ctrl):
    _raise(ctrl)
    assert ctrl._planned_target_for_room(ctrl.config[const.CONF_ROOMS][ROOM_ID]) == PLANNED


def test_ohne_option_passiert_nichts(ctrl):
    ctrl.config[const.CONF_ROOMS][ROOM_ID][const.CONF_ROOM_COMFORT_OVERRIDE_ENABLED] = False
    _raise(ctrl)
    assert ctrl._comfort_override == {}
    assert ctrl.set_comfort_override(ROOM_ID, 22.0) is False


def test_kleine_anhebung_zaehlt_nicht(ctrl):
    _raise(ctrl, new=PLANNED + 0.4)
    assert ctrl._comfort_override == {}


def test_anhebung_nicht_ueber_geplantem_wert_zaehlt_nicht(ctrl):
    ctrl._effective_target_for_room = lambda room: 22.0
    ctrl._desired_targets[VALVE] = 21.0
    _raise(ctrl, new=22.0, old=21.0)  # liegt nicht über dem Plan
    assert ctrl._comfort_override == {}


def test_urlaubsmodus_hat_vorrang(ctrl):
    ctrl.config[const.CONF_VACATION_ENABLED] = True
    _raise(ctrl)
    assert ctrl._comfort_override == {}
    assert ctrl.set_comfort_override(ROOM_ID, 22.0) is False  # Climate-Entity lehnt ab


def test_laufender_override_endet_im_urlaubsmodus(ctrl):
    _raise(ctrl)
    ctrl.config[const.CONF_VACATION_ENABLED] = True
    assert ctrl._active_comfort_target(ROOM_ID) is None


def test_eigener_wert_mit_verzoegerter_bestaetigung_zaehlt_nicht(ctrl, clock):
    """Wir senden 22 °C (z. B. Plan-Wechsel); das Ventil bestätigt erst später."""
    ctrl._desired_targets[VALVE] = PLANNED
    ctrl._remember_sent_target(VALVE, 22.0, clock.ts - 200)
    ctrl._last_command_sent_at[VALVE] = clock.ts - 200
    _raise(ctrl)
    assert ctrl._comfort_override == {}


def test_kurz_nach_eigenem_befehl_keine_erkennung(ctrl, clock):
    ctrl._last_command_sent_at[VALVE] = clock.ts - 60
    _raise(ctrl)
    assert ctrl._comfort_override == {}


def test_ruhezeit_nach_speichern_im_panel(ctrl, clock):
    ctrl._config_changed_at = clock.ts - (const.COMFORT_OVERRIDE_CONFIG_GRACE - 10)
    _raise(ctrl)
    assert ctrl._comfort_override == {}

    clock.advance(20)
    _raise(ctrl)
    assert ctrl._active_comfort_target(ROOM_ID) == 22.0


def test_fenster_offen_oder_pausiert_keine_erkennung(ctrl):
    ctrl._is_window_open = lambda room: True
    _raise(ctrl)
    assert ctrl._comfort_override == {}

    ctrl._is_window_open = lambda room: False
    ctrl._window_paused_rooms.add(ROOM_ID)
    _raise(ctrl)
    assert ctrl._comfort_override == {}


def test_ruhezeit_nach_fensterpause(ctrl, clock):
    ctrl._window_last_active[ROOM_ID] = clock.ts - (const.COMFORT_OVERRIDE_WINDOW_GRACE - 10)
    _raise(ctrl)
    assert ctrl._comfort_override == {}

    clock.advance(20)
    _raise(ctrl)
    assert ctrl._active_comfort_target(ROOM_ID) == 22.0


def test_ventil_stellt_nach_eigener_fenster_erkennung_sollwert_wieder_her(ctrl):
    """Ventil senkt selbst auf 5 °C ab (Fenster), der Plan wechselt auf 18 °C, dann
    stellt das Ventil seinen alten Wert 21 °C wieder her. Kein Benutzereingriff."""
    ctrl._effective_target_for_room = lambda room: 18.0
    ctrl._desired_targets[VALVE] = 18.0
    _raise(ctrl, new=21.0, old=5.0)
    assert ctrl._comfort_override == {}


def test_sensorausfall_keine_erkennung(ctrl):
    ctrl._room_sensor_fault.add(ROOM_ID)
    _raise(ctrl)
    assert ctrl._comfort_override == {}


def test_raum_hat_wunschtemperatur_bereits_erreicht(ctrl):
    ctrl._room_temp = lambda room: 22.5
    _raise(ctrl)
    assert ctrl._comfort_override == {}


def test_gleicher_wert_wie_plan_beendet_override(ctrl):
    _raise(ctrl)
    assert ctrl._active_comfort_target(ROOM_ID) == 22.0
    assert ctrl.set_comfort_override(ROOM_ID, PLANNED) is True  # z. B. Climate-Karte
    assert ctrl._active_comfort_target(ROOM_ID) is None


def test_fenster_oeffnen_beendet_override(ctrl):
    _raise(ctrl)
    ctrl._window_paused_rooms.add(ROOM_ID)
    assert ctrl._active_comfort_target(ROOM_ID) is None


def test_deaktivieren_der_option_beendet_override(ctrl):
    _raise(ctrl)
    ctrl.config[const.CONF_ROOMS][ROOM_ID][const.CONF_ROOM_COMFORT_OVERRIDE_ENABLED] = False
    assert ctrl._active_comfort_target(ROOM_ID) is None


def test_climate_entity_setzt_override_ohne_plan_zu_aendern(ctrl):
    assert ctrl.set_comfort_override(ROOM_ID, 23.0) is True
    assert ctrl.get_room_target_temperature(ROOM_ID) == 23.0
    ctrl._evaluate.assert_called()
    assert ctrl._effective_target_for_room({}) == PLANNED
