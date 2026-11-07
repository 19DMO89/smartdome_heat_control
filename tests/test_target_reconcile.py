"""Tests für den optionalen Sollwert-Abgleich pro Raum."""

from __future__ import annotations

import logging
import types

from conftest import const_module as const
from conftest import controller_module

VALVE = "climate.bad_valve"


def _room(enabled: bool) -> dict:
    return {
        const.CONF_ROOM_THERMOSTAT: VALVE,
        const.CONF_ROOM_TARGET_RECONCILE_ENABLED: enabled,
    }


def _setup(make_controller, clock, observed: float, desired: float = 21.0):
    ctrl = make_controller({"bad": _room(True)})
    ctrl._desired_targets[VALVE] = desired
    ctrl._last_command_sent_at[VALVE] = clock.ts  # gerade gesendet
    ctrl.hass.states.set(VALVE, observed)
    return ctrl


def test_default_ist_aus(make_controller):
    ctrl = make_controller()
    assert ctrl._reconcile_enabled({}) is False
    assert ctrl._reconcile_enabled(_room(False)) is False
    assert ctrl._reconcile_enabled(_room(True)) is True


def test_uebernommener_sollwert_loest_nichts_aus(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=21.0)
    clock.advance(3600)
    ctrl._reconcile_thermostat_target(VALVE)
    assert ctrl.hass.service_calls == []


def test_abweichung_wird_erst_nach_wartezeit_erneut_gesendet(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=19.0)
    clock.advance(60)  # < RECONCILE_RETRY_INTERVAL
    ctrl._reconcile_thermostat_target(VALVE)
    assert ctrl.hass.service_calls == []

    clock.advance(const.RECONCILE_RETRY_INTERVAL)
    ctrl._reconcile_thermostat_target(VALVE)
    assert ctrl.hass.service_calls == [
        ("climate", "set_temperature", {"entity_id": VALVE, "temperature": 21.0})
    ]


def test_begrenzendes_ventil_wird_hoechstens_zweimal_nachgesendet(
    make_controller, clock, caplog
):
    """Ventil mit Maximalwert 19 °C: Sollwert 21 wird nie übernommen."""
    ctrl = _setup(make_controller, clock, observed=19.0)
    caplog.set_level(logging.DEBUG, logger=controller_module.__name__)

    for _ in range(10):  # entspricht vielen Auswertungen über Stunden
        clock.advance(const.RECONCILE_RETRY_INTERVAL + 1)
        ctrl._reconcile_thermostat_target(VALVE)

    assert len(ctrl.hass.service_calls) == const.RECONCILE_MAX_ATTEMPTS
    assert ctrl._reconcile[VALVE]["limited"] is True
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
    infos = [r for r in caplog.records if r.levelno == logging.INFO]
    assert len(infos) == 1


def test_neuer_zielwert_hebt_begrenzung_auf(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=19.0)
    for _ in range(5):
        clock.advance(const.RECONCILE_RETRY_INTERVAL + 1)
        ctrl._reconcile_thermostat_target(VALVE)
    calls_before = len(ctrl.hass.service_calls)

    ctrl._desired_targets[VALVE] = 20.0  # Wochenplan wechselt
    ctrl._last_command_sent_at[VALVE] = clock.ts
    clock.advance(const.RECONCILE_RETRY_INTERVAL + 1)
    ctrl._reconcile_thermostat_target(VALVE)
    assert len(ctrl.hass.service_calls) == calls_before + 1


def test_uebernahme_setzt_zaehler_zurueck(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=19.0)
    clock.advance(const.RECONCILE_RETRY_INTERVAL + 1)
    ctrl._reconcile_thermostat_target(VALVE)
    assert ctrl._reconcile[VALVE]["attempts"] == 1

    ctrl.hass.states.set(VALVE, 21.0)
    ctrl._reconcile_thermostat_target(VALVE)
    assert ctrl._reconcile[VALVE]["attempts"] == 0


def test_nicht_erreichbares_ventil_wird_ignoriert(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=19.0)
    ctrl.hass.states.set(VALVE, None)  # kein temperature-Attribut
    clock.advance(3600)
    ctrl._reconcile_thermostat_target(VALVE)
    assert ctrl.hass.service_calls == []


def test_manuelle_absenkung_wird_nicht_ueberschrieben(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=17.0)
    clock.advance(3600)  # lange nach unserem letzten Befehl
    ctrl._note_possible_manual_change(VALVE, old_target=21.0, new_target=17.0)
    assert ctrl._reconcile[VALVE]["hold"] is True

    for _ in range(5):
        clock.advance(const.RECONCILE_RETRY_INTERVAL + 1)
        ctrl._reconcile_thermostat_target(VALVE)
    assert ctrl.hass.service_calls == []


def test_manuelle_anhebung_wird_nicht_ueberschrieben(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=23.0)
    clock.advance(3600)  # lange nach unserem letzten Befehl
    ctrl._on_state_change(_event(VALVE, 21.0, 23.0))
    assert ctrl._reconcile[VALVE]["hold"] is True

    for _ in range(5):
        clock.advance(const.RECONCILE_RETRY_INTERVAL + 1)
        ctrl._reconcile_thermostat_target(VALVE)
    assert ctrl.hass.service_calls == []


def test_absenkung_kurz_nach_eigenem_befehl_ist_keine_manuelle(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=19.0)
    clock.advance(30)  # innerhalb der Schonfrist nach unserem Befehl
    ctrl._note_possible_manual_change(VALVE, old_target=21.0, new_target=19.0)
    assert VALVE not in ctrl._reconcile


def test_bestaetigung_des_eigenen_wertes_ist_keine_absenkung(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=20.0, desired=20.0)
    clock.advance(3600)
    # Ventil meldet nach unserem Befehl 20 °C (vorher 21 °C): entspricht Sollwert
    ctrl._note_possible_manual_change(VALVE, old_target=20.5, new_target=20.0)
    assert VALVE not in ctrl._reconcile


def _event(entity_id: str, old: float, new: float):
    def state(value):
        return types.SimpleNamespace(attributes={"temperature": value})

    return types.SimpleNamespace(
        data={"entity_id": entity_id, "old_state": state(old), "new_state": state(new)}
    )


def test_state_change_erkennt_absenkung_nur_bei_aktivierter_option(make_controller, clock):
    ctrl = _setup(make_controller, clock, observed=17.0)
    clock.advance(3600)
    ctrl._on_state_change(_event(VALVE, 21.0, 17.0))
    assert ctrl._reconcile[VALVE]["hold"] is True
    ctrl._evaluate.assert_called_once()

    aus = make_controller({"bad": _room(False)})
    aus._desired_targets[VALVE] = 21.0
    aus._on_state_change(_event(VALVE, 21.0, 17.0))
    assert aus._reconcile == {}
    aus._evaluate.assert_called_once()
