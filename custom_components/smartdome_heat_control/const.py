"""Konstanten für Smartdome Heat Control."""

DOMAIN = "smartdome_heat_control"

DATA_CONTROLLER = "controller"
DATA_ENABLED = "enabled"

PLATFORMS: list[str] = ["switch", "number", "select"]

# Services
SERVICE_UPDATE_CONFIG = "update_config"
SERVICE_ADD_ROOM = "add_room"
SERVICE_REMOVE_ROOM = "remove_room"
SERVICE_RELOAD = "reload"

# Globale Config-Keys
CONF_MAIN_THERMOSTAT = "main_thermostat"
CONF_MAIN_SENSOR = "main_sensor"

# Heizkreise
CONF_CIRCUITS = "circuits"
CONF_CIRCUIT_LABEL = "label"
CONF_CIRCUIT_MAIN_THERMOSTAT = "main_thermostat"
CONF_CIRCUIT_MAIN_SENSOR = "main_sensor"
CONF_CIRCUIT_ENABLED = "enabled"
CONF_ROOM_CIRCUIT_ID = "circuit_id"
CONF_BOOST_DELTA = "boost_delta"
CONF_TOLERANCE = "tolerance"
CONF_NIGHT_START = "night_start"
CONF_MORNING_BOOST_START = "morning_boost_start"
CONF_MORNING_BOOST_END = "morning_boost_end"
CONF_ROOMS = "rooms"
CONF_ROOM_WINDOW_SENSOR = "window_sensor"
CONF_ROOM_WINDOW_SENSORS = "window_sensors"

CONF_ENERGY_RESIDUAL_HEAT_HOLD = "energy_residual_heat_hold"
DEFAULT_ENERGY_RESIDUAL_HEAT_HOLD = 180

# Room-Keys
CONF_ROOM_LABEL = "label"
CONF_ROOM_AREA_ID = "area_id"
CONF_ROOM_THERMOSTAT = "thermostat"
CONF_ROOM_SENSOR = "sensor"
CONF_ROOM_TARGET_DAY = "target_day"
CONF_ROOM_TARGET_NIGHT = "target_night"
CONF_ROOM_DAY_START = "day_start"
CONF_ROOM_NIGHT_START = "night_start"
CONF_ROOM_ENABLED = "enabled"
CONF_ROOM_NIGHT_SETBACK_ENABLED = "night_setback_enabled"
CONF_ROOM_CALLING_FOR_HEAT = "calling_for_heat"

#Uralub und weg
CONF_VACATION_ENABLED = "vacation_enabled"
CONF_VACATION_TEMPERATURE = "vacation_temperature"
CONF_AWAY_ENABLED = "away_enabled"
CONF_ROOM_AWAY_TEMPERATURE = "away_temperature"
CONF_WINDOW_OPEN_DELAY = "window_open_delay"
CONF_WINDOW_CLOSE_DELAY = "window_close_delay"

# Global config
CONF_HEATING_MODE = "heating_mode"

# Room learning keys
CONF_ROOM_LEARNED_OVERSHOOT = "learned_overshoot"
CONF_ROOM_LEARNED_OVERSHOOT_SHORT = "learned_overshoot_short"
CONF_ROOM_LEARNED_OVERSHOOT_MEDIUM = "learned_overshoot_medium"
CONF_ROOM_LEARNED_OVERSHOOT_LONG = "learned_overshoot_long"
CONF_ROOM_HEATING_CYCLE_ACTIVE = "heating_cycle_active"
CONF_ROOM_CYCLE_TARGET_TEMP = "cycle_target_temp"
CONF_ROOM_CYCLE_PEAK_TEMP = "cycle_peak_temp"
CONF_ROOM_CYCLE_START_TS = "cycle_start_ts"
CONF_ROOM_CYCLE_PEAKED = "cycle_peaked"

# Adaptive bucket boundaries (seconds)
ADAPTIVE_BUCKET_SHORT_MAX_SECS = 900   # < 15 min
ADAPTIVE_BUCKET_MEDIUM_MAX_SECS = 2700  # 15–45 min
                                        # > 45 min = long bucket

CONF_ROOM_CONTROL_PROFILE = "control_profile"
CONF_ROOM_THERMOSTAT_OFFSET = "thermostat_offset"

CONTROL_PROFILE_STANDARD = "standard"
CONTROL_PROFILE_SELF_REGULATING = "self_regulating"

DEFAULT_ROOM_CONTROL_PROFILE = CONTROL_PROFILE_STANDARD
DEFAULT_ROOM_THERMOSTAT_OFFSET = 0.0

# Steuertyp Hauptthermostat / Heizkreis (Thermostat oder Switch)
CONF_MAIN_CONTROL_TYPE = "main_control_type"
CONF_MAIN_SWITCH = "main_switch"
CONF_CIRCUIT_CONTROL_TYPE = "control_type"
CONF_CIRCUIT_MAIN_SWITCH = "main_switch"

CONTROL_TYPE_THERMOSTAT = "thermostat"
CONTROL_TYPE_SWITCH = "switch"

DEFAULT_MAIN_CONTROL_TYPE = CONTROL_TYPE_THERMOSTAT

#Wochenplan
CONF_ROOM_WEEKLY_SCHEDULE = "weekly_schedule"

DEFAULT_ROOM_WEEKLY_SCHEDULE = {
    "monday": [],
    "tuesday": [],
    "wednesday": [],
    "thursday": [],
    "friday": [],
    "saturday": [],
    "sunday": [],
}

# Heating modes
HEATING_MODE_COMFORT = "comfort"
HEATING_MODE_BALANCED = "balanced"
HEATING_MODE_ENERGY = "energy"
HEATING_MODE_ADAPTIVE = "adaptive"

HEATING_MODES = [
    HEATING_MODE_COMFORT,
    HEATING_MODE_BALANCED,
    HEATING_MODE_ENERGY,
    HEATING_MODE_ADAPTIVE,
]

DEFAULT_HEATING_MODE = HEATING_MODE_BALANCED

# Adaptive defaults
DEFAULT_ADAPTIVE_OVERSHOOT = 0.3
MIN_ADAPTIVE_OVERSHOOT = 0.0
MAX_ADAPTIVE_OVERSHOOT = 1.5

# Per-bucket defaults (short cycles overshoot less, long cycles overshoot more)
DEFAULT_ADAPTIVE_OVERSHOOT_SHORT = 0.2
DEFAULT_ADAPTIVE_OVERSHOOT_MEDIUM = 0.4
DEFAULT_ADAPTIVE_OVERSHOOT_LONG = 0.7

DEFAULT_WINDOW_OPEN_DELAY = 120
DEFAULT_WINDOW_CLOSE_DELAY = 60



# Außentemperatur-Abschaltung
CONF_OUTDOOR_SENSOR = "outdoor_sensor"
CONF_OUTDOOR_TEMP_CUTOFF_ENABLED = "outdoor_temp_cutoff_enabled"
CONF_OUTDOOR_TEMP_CUTOFF = "outdoor_temp_cutoff"
DEFAULT_OUTDOOR_TEMP_CUTOFF_ENABLED = False
DEFAULT_OUTDOOR_TEMP_CUTOFF = 15.0

# Defaults
DEFAULT_ENABLED = True
DEFAULT_BOOST_DELTA = 2.0
DEFAULT_TOLERANCE = 0.5
DEFAULT_NIGHT_START = "22:00"
DEFAULT_MORNING_BOOST_START = "05:00"
DEFAULT_MORNING_BOOST_END = "05:30"
DEFAULT_TARGET_DAY = 21.0
DEFAULT_TARGET_NIGHT = 18.0
DEFAULT_VACATION_ENABLED = False
DEFAULT_VACATION_TEMPERATURE = 14.0
DEFAULT_AWAY_ENABLED = False
DEFAULT_ROOM_AWAY_TEMPERATURE = 17.0
