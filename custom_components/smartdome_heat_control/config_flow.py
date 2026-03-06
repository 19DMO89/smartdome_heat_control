"""Config Flow für Smartdome Heat Control."""
from __future__ import annotations

import uuid
import logging
import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_BOOST_DELTA,
    CONF_MAIN_THERMOSTAT,
    CONF_MORNING_BOOST_END,
    CONF_MORNING_BOOST_START,
    CONF_NIGHT_START,
    CONF_ROOMS,
    CONF_TOLERANCE,
    DEFAULT_BOOST_DELTA,
    DEFAULT_MORNING_BOOST_END,
    DEFAULT_MORNING_BOOST_START,
    DEFAULT_NIGHT_START,
    DEFAULT_TOLERANCE,
    DOMAIN,
)
from .helpers import async_discover_rooms

_LOGGER = logging.getLogger(__name__)

class SmartdomeHeatControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow: Schritt-für-Schritt Einrichtung."""

    VERSION = 1

    def __init__(self):
        self._data: dict[str, Any] = {}
        self._discovered_rooms: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Schritt 1: Hauptthermostat & globale Parameter."""
        if user_input is not None:
            self._data.update(user_input)
            # Weiter zu Schritt 2: Räume entdecken
            self._discovered_rooms = await async_discover_rooms(self.hass)
            return await self.async_step_rooms()

        schema = vol.Schema({
            vol.Required(CONF_MAIN_THERMOSTAT): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate")
            ),
            vol.Optional(CONF_BOOST_DELTA, default=DEFAULT_BOOST_DELTA): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0.5, max=5.0, step=0.5, unit_of_measurement="°C", mode="slider")
            ),
            vol.Optional(CONF_TOLERANCE, default=DEFAULT_TOLERANCE): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0.1, max=2.0, step=0.1, unit_of_measurement="°C", mode="slider")
            ),
            vol.Optional(CONF_NIGHT_START, default=DEFAULT_NIGHT_START): selector.TimeSelector(),
            vol.Optional(CONF_MORNING_BOOST_START, default=DEFAULT_MORNING_BOOST_START): selector.TimeSelector(),
            vol.Optional(CONF_MORNING_BOOST_END, default=DEFAULT_MORNING_BOOST_END): selector.TimeSelector(),
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_rooms(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Schritt 2: Erkannte Räume bestätigen."""
        if user_input is not None:
            self._data[CONF_ROOMS] = self._discovered_rooms
            return self.async_create_entry(title="Smartdome Heat Control", data=self._data)

        room_names = ", ".join(r["label"] for r in self._discovered_rooms.values()) or "Keine gefunden"
        
        return self.async_show_form(
            step_id="rooms",
            data_schema=vol.Schema({
                vol.Required("confirm", default=True): bool
            }),
            description_placeholders={
                "room_count": str(len(self._discovered_rooms)),
                "room_names": room_names,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> SmartdomeOptionsFlow:
        return SmartdomeOptionsFlow(config_entry)


class SmartdomeOptionsFlow(config_entries.OptionsFlow):
    """Options Flow: Nachträgliche Konfiguration über Einstellungen."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self._entry = config_entry
        self._rooms: dict = dict(config_entry.data.get(CONF_ROOMS, {}))
        self._edit_room_id: str | None = None

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Hauptmenü der Einstellungen."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "global":
                return await self.async_step_global()
            if action == "rooms":
                return await self.async_step_rooms_list()
            if action == "discover":
                return await self.async_step_discover()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action", default="rooms"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "global", "label": "⚙️ Globale Einstellungen"},
                            {"value": "rooms", "label": "🏠 Räume verwalten"},
                            {"value": "discover", "label": "🔍 Räume neu erkennen"},
                        ],
                        mode="list"
                    )
                ),
            }),
        )

    async def async_step_global(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Globale Werte ändern."""
        data = self._entry.data
        if user_input is not None:
            new_data = {**data, **user_input}
            self.hass.config_entries.async_update_entry(self._entry, data=new_data)
            return self.async_create_entry(title="", data={})

        schema = vol.Schema({
            vol.Required(CONF_MAIN_THERMOSTAT, default=data.get(CONF_MAIN_THERMOSTAT)): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate")
            ),
            vol.Optional(CONF_BOOST_DELTA, default=data.get(CONF_BOOST_DELTA, DEFAULT_BOOST_DELTA)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0.5, max=5.0, step=0.5, mode="slider")
            ),
            vol.Optional(CONF_NIGHT_START, default=data.get(CONF_NIGHT_START, DEFAULT_NIGHT_START)): selector.TimeSelector(),
        })
        return self.async_show_form(step_id="global", data_schema=schema)

    async def async_step_rooms_list(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Liste aller Räume zur Auswahl."""
        if user_input is not None:
            action = user_input.get("room_action")
            if action == "__add__":
                return await self.async_step_add_room()
            if action in self._rooms:
                self._edit_room_id = action
                return await self.async_step_edit_room()

        room_options = [{"value": rid, "label": f"✏️ {r.get('label', rid)}"} for rid, r in self._rooms.items()]
        room_options.append({"value": "__add__", "label": "➕ Neuen Raum hinzufügen"})

        return self.async_show_form(
            step_id="rooms_list",
            data_schema=vol.Schema({
                vol.Required("room_action"): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=room_options, mode="list")
                )
            })
        )

    async def async_step_edit_room(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Raum bearbeiten oder löschen."""
        room_id = self._edit_room_id
        room = self._rooms[room_id]

        if user_input is not None:
            if user_input.get("delete_room"):
                del self._rooms[room_id]
            else:
                self._rooms[room_id].update(user_input)
            
            new_data = {**self._entry.data, CONF_ROOMS: self._rooms}
            self.hass.config_entries.async_update_entry(self._entry, data=new_data)
            return self.async_create_entry(title="", data={})

        schema = vol.Schema({
            vol.Required("label", default=room.get("label", "")): str,
            vol.Optional("thermostat", default=room.get("thermostat", "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate")
            ),
            vol.Optional("sensor", default=room.get("sensor", "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Optional("enabled", default=room.get("enabled", True)): bool,
            vol.Optional("delete_room", default=False): bool,
        })
        return self.async_show_form(step_id="edit_room", data_schema=schema)

    async def async_step_add_room(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manuell einen Raum hinzufügen."""
        if user_input is not None:
            new_id = f"room_{uuid.uuid4().hex[:8]}"
            self._rooms[new_id] = user_input
            new_data = {**self._entry.data, CONF_ROOMS: self._rooms}
            self.hass.config_entries.async_update_entry(self._entry, data=new_data)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="add_room",
            data_schema=vol.Schema({
                vol.Required("label"): str,
                vol.Optional("thermostat"): selector.EntitySelector(selector.EntitySelectorConfig(domain="climate")),
            })
        )

    async def async_step_discover(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Neu-Erkennung von Räumen."""
        discovered = await async_discover_rooms(self.hass)
        for rid, rdata in discovered.items():
            if rid not in self._rooms:
                self._rooms[rid] = rdata
        
        new_data = {**self._entry.data, CONF_ROOMS: self._rooms}
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        return self.async_create_entry(title="", data={})
