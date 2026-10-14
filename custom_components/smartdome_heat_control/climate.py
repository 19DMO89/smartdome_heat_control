"""Climate-Entities (ein Thermostat pro Raum) für Smartdome Heat Control."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_ROOMS,
    CONF_ROOM_ENABLED,
    CONF_ROOM_LABEL,
    DATA_CONTROLLER,
    DOMAIN,
    SIGNAL_ROOM_STATE_UPDATED,
)
from .helpers import apply_room_config_update

MIN_TEMP = 5.0
MAX_TEMP = 30.0
TEMP_STEP = 0.5


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Pro Raum eine Climate-Entity anlegen."""
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    rooms = entry_data.get("config", {}).get(CONF_ROOMS, {})

    entities: list[ClimateEntity] = []
    for room_id, room in rooms.items():
        if not isinstance(room, dict):
            continue
        label = str(room.get(CONF_ROOM_LABEL, room_id))
        entities.append(SmartdomeRoomClimate(hass, entry, room_id, label))

    async_add_entities(entities)


class SmartdomeRoomClimate(ClimateEntity):
    """Raum als Thermostat: zeigt Soll/Ist an und erlaubt, den Sollwert zu ändern.

    Die Entity steuert keine Hardware direkt. Sie zeigt die von der Integration
    berechnete Solltemperatur des Raums an. Ein manuell gesetzter Wert wird in
    die Raumkonfiguration geschrieben (Tag-, Nacht- oder Away-Temperatur, je
    nachdem, was gerade aktiv ist).
    """

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:radiator"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = TEMP_STEP

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        room_id: str,
        room_label: str,
    ) -> None:
        self.hass = hass
        self._entry = entry
        self._room_id = room_id
        self._attr_unique_id = f"{entry.entry_id}_room_{room_id}_climate"
        self._attr_name = f"{room_label} – Heizung"

    # --- Helfer -----------------------------------------------------------

    def _get_entry_data(self) -> dict | None:
        return self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id)

    def _get_controller(self) -> Any:
        data = self._get_entry_data()
        return None if data is None else data.get(DATA_CONTROLLER)

    def _get_room(self) -> dict:
        data = self._get_entry_data()
        if data is None:
            return {}
        room = data.get("config", {}).get(CONF_ROOMS, {}).get(self._room_id)
        return dict(room) if isinstance(room, dict) else {}

    def _status(self) -> dict[str, Any] | None:
        controller = self._get_controller()
        if controller is None:
            return None
        return controller.get_room_status(self._room_id)

    # --- Zustand ----------------------------------------------------------

    @property
    def available(self) -> bool:
        return self._get_entry_data() is not None and bool(self._get_room())

    @property
    def hvac_mode(self) -> HVACMode:
        if bool(self._get_room().get(CONF_ROOM_ENABLED, True)):
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        status = self._status()
        if status is None or not status["enabled"]:
            return HVACAction.OFF
        if status["state"] == "heating":
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def current_temperature(self) -> float | None:
        status = self._status()
        if status is None:
            return None
        value = status["current_temperature"]
        return float(value) if value is not None else None

    @property
    def target_temperature(self) -> float | None:
        controller = self._get_controller()
        room = self._get_room()
        if controller is None or not room:
            return None
        try:
            override = controller._active_comfort_target(self._room_id)
            return float(override if override is not None else controller._effective_target_for_room(room))
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        status = self._status()
        if status is None:
            return {}
        return {
            "room_state": status["state"],
            "heating_mode": status["heating_mode"],
            "away_active": status["away_active"],
        }

    # --- Steuerung --------------------------------------------------------

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        controller = self._get_controller()
        if controller is None:
            raise ServiceValidationError("Smartdome Controller nicht verfügbar.")
        value = min(MAX_TEMP, max(MIN_TEMP, float(temperature)))
        controller.set_comfort_override(self._room_id, value)
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode not in self._attr_hvac_modes:
            return
        apply_room_config_update(
            self.hass,
            self._entry,
            self._room_id,
            {CONF_ROOM_ENABLED: hvac_mode == HVACMode.HEAT},
        )
        self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    # --- Updates ----------------------------------------------------------

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_ROOM_STATE_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self, room_states: dict[str, Any]) -> None:
        self.async_write_ha_state()
