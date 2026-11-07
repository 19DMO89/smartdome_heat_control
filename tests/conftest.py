"""Test-Grundlage: lädt den Controller ohne Home-Assistant-Installation.

Ist ``homeassistant`` installiert, wird es unverändert genutzt. Sonst werden
die wenigen importierten Module durch einfache Platzhalter ersetzt. Getestet
wird reine Controller-Logik; ein laufendes Home Assistant ist nicht nötig.
"""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PACKAGE_DIR = Path(__file__).resolve().parents[1] / "custom_components" / "smartdome_heat_control"


def _install_homeassistant_stubs() -> None:
    try:
        import homeassistant  # noqa: F401

        return
    except ImportError:
        pass

    def module(name: str, **attrs):
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        sys.modules[name] = mod
        return mod

    module("homeassistant")
    module("homeassistant.components")
    module("homeassistant.components.climate", DOMAIN="climate")
    module("homeassistant.components.switch", DOMAIN="switch")
    module(
        "homeassistant.const",
        ATTR_TEMPERATURE="temperature",
        STATE_UNAVAILABLE="unavailable",
        STATE_UNKNOWN="unknown",
    )
    module(
        "homeassistant.core",
        Event=MagicMock,
        HomeAssistant=MagicMock,
        callback=lambda func: func,
    )
    module("homeassistant.helpers")
    module("homeassistant.helpers.dispatcher", async_dispatcher_send=MagicMock())
    module(
        "homeassistant.helpers.event",
        async_track_state_change_event=MagicMock(),
        async_track_time_change=MagicMock(),
    )
    module("homeassistant.util")
    util_dt = module("homeassistant.util.dt", now=MagicMock())
    sys.modules["homeassistant.util"].dt = util_dt


_install_homeassistant_stubs()

# Paket unter eigenem Namen anlegen, ohne dessen __init__ (lädt die komplette
# Integration) auszuführen. Der Controller braucht nur const.py.
_pkg = types.ModuleType("smartdome_under_test")
_pkg.__path__ = [str(PACKAGE_DIR)]
sys.modules["smartdome_under_test"] = _pkg
controller_module = importlib.import_module("smartdome_under_test.controller")
const_module = importlib.import_module("smartdome_under_test.const")


class FakeClock:
    """Steuerbare Uhr für dt_util.now()."""

    def __init__(self, start: float = 1_000_000.0) -> None:
        self.ts = start

    def now(self):
        return types.SimpleNamespace(timestamp=lambda: self.ts)

    def advance(self, seconds: float) -> None:
        self.ts += seconds


class FakeStates:
    def __init__(self) -> None:
        self._states: dict[str, types.SimpleNamespace] = {}

    def set(self, entity_id: str, temperature: float | None, **attrs) -> None:
        attributes = dict(attrs)
        if temperature is not None:
            attributes["temperature"] = temperature
        self._states[entity_id] = types.SimpleNamespace(
            entity_id=entity_id, state="heat", attributes=attributes
        )

    def get(self, entity_id: str):
        return self._states.get(entity_id)


class FakeHass:
    def __init__(self) -> None:
        self.states = FakeStates()
        self.service_calls: list[tuple] = []
        self.services = types.SimpleNamespace(async_call=self._async_call)

    def _async_call(self, domain, service, data, blocking=False):
        self.service_calls.append((domain, service, dict(data)))
        return None

    def async_create_task(self, coro):
        return coro


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(controller_module, "dt_util", fake)
    return fake


@pytest.fixture
def make_controller(clock):
    """Controller ohne vollständige Initialisierung, nur mit benötigtem Zustand."""

    def factory(rooms: dict | None = None):
        ctrl = controller_module.SmartHeatingController.__new__(
            controller_module.SmartHeatingController
        )
        ctrl.hass = FakeHass()
        ctrl.config = {const_module.CONF_ROOMS: rooms or {}}
        ctrl._desired_targets = {}
        ctrl._last_command_sent_at = {}
        ctrl._reconcile = {}
        ctrl._evaluate = MagicMock()
        return ctrl

    return factory
