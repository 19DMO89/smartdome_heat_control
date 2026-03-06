"""Smart Heating Controller – Integration Entry Point."""
from __future__ import annotations

import logging
import uuid
import os
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.components import frontend, websocket_api
from homeassistant.components.http import StaticPathConfig

from .const import (
    CONF_ROOMS,
    DOMAIN,
    SERVICE_ADD_ROOM,
    SERVICE_RELOAD,
    SERVICE_REMOVE_ROOM,
    SERVICE_UPDATE_CONFIG,
)
from .controller import SmartHeatingController
from .helpers import async_discover_rooms, deep_merge

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup über Config Entry."""
    
    hass.data.setdefault(DOMAIN, {})

    cfg = dict(entry.data)
    controller = SmartHeatingController(hass, cfg)
    await controller.async_start()

    hass.data[DOMAIN][entry.entry_id] = {
        "controller": controller,
        "config":     cfg,
        "entry":      entry,
    }

    # 1. Frontend Pfad & Seitenleisten-Panel registrieren
    frontend_path = os.path.join(os.path.dirname(__file__), "www")
    
    if os.path.exists(frontend_path):
        await hass.http.async_register_static_paths([
            StaticPathConfig("/smartdome_ui", frontend_path, False)
        ])
    else:
        _LOGGER.error("Frontend Ordner 'www' nicht gefunden in %s", frontend_path)

    # Panel in der Seitenleiste (Iframe zeigt deine index.html)
    # Korrekte Registrierung des Panels
    frontend.async_register_built_in_panel(
        hass,
        component_name="iframe",
        sidebar_title="Smartdome Heat",
        sidebar_icon="mdi:radiator",
        frontend_url_path="smartdome_control", # Das Argument heißt jetzt frontend_url_path
        config={"url": "/smartdome_ui/index.html"},
        require_admin=False
    )


    # 2. WebSocket API zum Speichern aus der HTML-Oberfläche
    @websocket_api.websocket_command({
        vol.Required("type"): f"{DOMAIN}/save_config",
        vol.Required("config"): dict,
    })
    @websocket_api.async_response
    async def ws_save_config(hass, connection, msg):
        """Speichert die Konfiguration direkt aus dem Web-Panel."""
        new_cfg = msg["config"]
        # Config im Entry und Controller aktualisieren
        hass.config_entries.async_update_entry(entry, data=new_cfg)
        controller.update_config(new_cfg)
        _push_state(hass, new_cfg)
        connection.send_result(msg["id"], {"success": True})

    websocket_api.async_register_command(hass, ws_save_config)

    # State für Lovelace-Karte bereitstellen
    _push_state(hass, cfg)

    # 3. Services registrieren (Abwärtskompatibilität & Automatisierungen)
    async def handle_update_config(call: ServiceCall) -> None:
        patch = call.data.get("config", {})
        deep_merge(cfg, patch)
        hass.config_entries.async_update_entry(entry, data=dict(cfg))
        controller.update_config(cfg)
        _push_state(hass, cfg)

    async def handle_add_room(call: ServiceCall) -> None:
        room_id = call.data.get("room_id") or f"room_{uuid.uuid4().hex[:8]}"
        room_label = call.data.get("label", "Neuer Raum")
        if room_id not in cfg.get(CONF_ROOMS, {}):
            cfg.setdefault(CONF_ROOMS, {})[room_id] = {
                "label":        room_label,
                "area_id":      call.data.get("area_id", ""),
                "thermostat":   call.data.get("thermostat", ""),
                "sensor":       call.data.get("sensor", ""),
                "target_day":   call.data.get("target_day", 21.0),
                "target_night": call.data.get("target_night", 18.0),
                "enabled":      True,
            }
        hass.config_entries.async_update_entry(entry, data=dict(cfg))
        controller.update_config(cfg)
        _push_state(hass, cfg)

    async def handle_remove_room(call: ServiceCall) -> None:
        room_id = call.data.get("room_id")
        if room_id and room_id in cfg.get(CONF_ROOMS, {}):
            del cfg[CONF_ROOMS][room_id]
            hass.config_entries.async_update_entry(entry, data=dict(cfg))
            controller.update_config(cfg)
            _push_state(hass, cfg)

    async def handle_reload(call: ServiceCall) -> None:
        new_rooms = await async_discover_rooms(hass)
        rooms = cfg.setdefault(CONF_ROOMS, {})
        for r_id, r_data in new_rooms.items():
            if r_id not in rooms:
                rooms[r_id] = r_data
        hass.config_entries.async_update_entry(entry, data=dict(cfg))
        controller.update_config(cfg)
        _push_state(hass, cfg)

    hass.services.async_register(DOMAIN, SERVICE_UPDATE_CONFIG, handle_update_config, schema=vol.Schema({vol.Required("config"): dict}))
    hass.services.async_register(DOMAIN, SERVICE_ADD_ROOM, handle_add_room)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_ROOM, handle_remove_room, schema=vol.Schema({vol.Required("room_id"): str}))
    hass.services.async_register(DOMAIN, SERVICE_RELOAD, handle_reload)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload bei Änderungen im Options Flow."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entladen."""
    # Sidebar Panel entfernen
    frontend.async_remove_panel(hass, "smartdome_control")
    
    data = hass.data[DOMAIN].pop(entry.entry_id, {})
    controller = data.get("controller")
    if controller:
        await controller.async_stop()

    return True

def _push_state(hass: HomeAssistant, cfg: dict) -> None:
    """Aktualisiert den globalen State für die UI."""
    hass.states.async_set(f"{DOMAIN}.config", "active", attributes=cfg)
