const DOMAIN = "smartdome_heat_control";
const CONFIG_ENTITY_ID = `${DOMAIN}.config`;

function getUiLanguage() {
  const lang =
    document.documentElement.lang ||
    navigator.language ||
    navigator.userLanguage ||
    "en";

  const normalized = String(lang).toLowerCase();

  if (normalized.startsWith("de")) {
    return "de";
  }

  return "en";
}

const UI_LANG = getUiLanguage();

const WEEK_DAYS = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

const DEFAULT_WEEKLY_SCHEDULE = {
  monday: [],
  tuesday: [],
  wednesday: [],
  thursday: [],
  friday: [],
  saturday: [],
  sunday: [],
};

const I18N = {
  en: {
    title: "Smartdome Heat Control",
    subtitle:
      "Click a tile to edit a room or the global settings.",
    version: "Version",

    reload_rooms: "Reload rooms",
    reload_config: "Reload",
    save_config: "Save",
    edit_cancel: "Cancel",
    edit_delete: "Delete",
    edit_close: "Close",
    edit_discard_question: "Discard changes?",
    edit_discard_confirm: "Discard",
    edit_keep_editing: "Keep editing",
    edit_delete_question: "Really delete {name}?",
    edit_delete_keep: "Keep",
    tile_target: "Target",
    tile_now: "Now",
    tile_no_reading: "No reading",
    tile_control: "Control",
    tile_control_on: "Active",
    tile_control_off: "Off",
    tile_operation: "Operation",
    tile_outdoor: "Outdoor",
    tile_heating_mode: "Heating mode",
    tile_running_heat: "{count} of {total} heating",
    tile_running_cool: "{count} of {total} cooling",
    op_normal: "Normal",
    op_vacation: "Vacation",
    op_away: "Away",
    op_cooling: "Cooling",
    op_cutoff: "Outdoor cutoff",
    note_vacation: "Vacation",
    note_away: "Away",
    note_minimum: "Minimum temperature",
    status_disabled: "Disabled",
    status_control_off: "Control off",
    status_sensor_fault: "Sensor failed",
    status_window_pause: "Window open, paused",
    status_window_open: "Window open",
    status_cooling: "Cooling",
    status_heating: "Heating",
    status_heating_ac: "Heating via AC",
    status_residual: "Residual heat",
    status_cutoff: "Outdoor cutoff",
    status_idle: "Ready",
    tile_open: "Open settings",

    status_loading: "Loading configuration …",
    status_initializing: "Initializing panel …",
    status_loaded: "Configuration loaded.",
    status_save_loading: "Saving configuration …",
    status_save_ok: "Configuration saved successfully.",
    status_reload_ok: "Configuration reloaded.",
    status_rooms_reload_loading: "Reloading rooms …",
    status_rooms_reload_ok: "Rooms reloaded.",
    status_apply_times_ok: "Global times were applied to all rooms.",
    status_no_rooms_apply: "No rooms available to apply the times to.",
    status_vacation_on: "Vacation mode enabled.",
    status_vacation_off: "Vacation mode disabled.",
    status_away_on: "Away mode enabled.",
    status_away_off: "Away mode disabled.",
    status_live_updates_failed: "Unable to initialize live updates.",
    status_save_failed: "Saving failed",
    status_reload_failed: "Reload failed",
    status_room_reload_failed: "Room reload failed",
    status_vacation_failed: "Could not change vacation mode",
    status_away_failed: "Could not change away mode",

    global_settings: "Global settings",
    control_enabled: "Control enabled",
    control_enabled_hint:
      "If disabled, the integration no longer changes thermostat targets.",

    vacation_mode: "Vacation mode",
    vacation_mode_hint:
      "Sets all rooms to the global vacation temperature.",

    away_mode: "Away mode",
    away_mode_hint:
      "Uses the configured away temperature for each room.",

    btn_vacation_enable: "🏖 Enable vacation",
    btn_vacation_disable: "🏖 Disable vacation",
    btn_away_enable: "🚪 Enable away",
    btn_away_disable: "🚪 Disable away",

    section_control: "Control",
    section_thermostat: "Heating pump controller",
    section_heating: "Heating",
    section_times: "Times",

    main_control_type: "Control type",
    control_type_thermostat: "Thermostat",
    control_type_switch: "Smart switch",
    main_thermostat: "Heating pump controller (climate entity)",
    main_switch: "Heating pump controller (switch entity)",
    main_sensor: "Temperature sensor",
    boost_delta: "Boost delta (°C)",
    tolerance: "Tolerance (°C)",
    heating_mode: "Heating mode",
    energy_residual_heat_hold: "Residual heat hold (s)",
    vacation_temperature: "Vacation temperature (°C)",
    night_start: "Global night start",
    morning_boost_start: "Global day start",
    morning_boost_end: "Morning boost end",

    mode_comfort_desc: "Valves stay open longer — less temperature fluctuation, comfort first.",
    mode_balanced_desc: "Recommended default — good balance between comfort and efficiency.",
    mode_energy_desc: "Valves close earlier — reduces overheating, energy saving first.",
    mode_adaptive_desc: "Learns each room's behavior and stops heating early to avoid overshoot.",

    apply_times: "Apply global times to all rooms",
    footer_note:
      'The apply button sets for all rooms: <strong>Day start = global day start</strong> and <strong>Night start = global night start</strong>.',

    section_temperatures: "Temperatures",
    global_target_day: "Day target temperature (°C)",
    global_target_night: "Night target temperature (°C)",
    global_away_temperature: "Away temperature (°C)",
    apply_temps: "Apply global temperatures to all rooms",
    footer_note_temps: "The apply button overwrites the day target, night target, and away temperature for all rooms with the global values.",
    status_apply_temps_ok: "Global temperatures applied to all rooms.",

    room_heating_mode: "Heating mode",
    room_mode_global: "Global",

    rooms_title: "Rooms",
    add_room: "Add room",
    no_rooms: "No rooms configured yet.",

    room_active: "Active",
    room_delete: "Delete",
    room_label: "Label",
    room_area_id: "Area ID",
    room_thermostat: "Radiator valve",
    room_extra_thermostats: "Additional radiator valves",
    add_extra_thermostat: "Add radiator valve",
    room_switch_actuators: "Switch actuators (relay, e.g. floor heating)",
    add_switch_actuator: "Add switch actuator",
    room_switch_actuators_hint: "Switched on/off directly based on the room sensor – a room temperature sensor is required.",
    room_hysteresis: "Hysteresis (°C, empty = global tolerance)",
    room_switch_min_on: "Switch actuator: minimum on time (min)",
    room_switch_min_off: "Switch actuator: minimum off time (min)",
    room_sensor: "Room temperature sensor",
    room_window_sensor: "Window sensor",
    room_control_profile: "Thermostat control profile",
    control_profile_standard: "Standard thermostat",
    control_profile_self_regulating: "Self-regulating thermostat",
    room_target_day: "Day target temperature (°C)",
    room_target_night: "Night target temperature (°C)",
    room_night_setback_enabled: "Night setback active",
    room_thermostat_offset: "Thermostat calibration offset (°C)",
    room_away_temperature: "Away temperature (°C)",
    room_away_mode_enabled: "Away mode active for this room",
    room_target_reconcile_enabled: "Setpoint reconciliation: re-send the setpoint if the valve did not accept it (limited retries, respects manual changes)",
    room_day_start: "Day start",
    room_night_start: "Night start",
    room_manual: "Manually created",
    room_overshoot: "Adaptive overshoot",
    room_heating_now: "Room is currently heating",
    room_window_open: "Window open",
    room_new: "New room",
    room_schedule: "Schedule",

    select_not_set: "— Not set —",
    select_choose: "— Please choose —",
    select_auto_none: "— Automatic / none —",

    mode_comfort: "Comfort",
    mode_balanced: "Balanced",
    mode_energy: "Energy",
    mode_adaptive: "Adaptive",

    schedule_title: "Weekly schedule",
    schedule_add: "Add time block",
    schedule_save: "Save",
    schedule_cancel: "Cancel",
    schedule_empty: "No entries for this day yet.",
    schedule_time: "Time",
    schedule_temperature: "Temperature",
    day_monday: "Mon",
    day_tuesday: "Tue",
    day_wednesday: "Wed",
    day_thursday: "Thu",
    day_friday: "Fri",
    day_saturday: "Sat",
    day_sunday: "Sun",

    schedule_copy_rooms: "Copy to other rooms",
    schedule_copy_title: "Copy weekly schedule",
    schedule_copy_apply: "Apply",
    schedule_copy_no_rooms: "No other rooms available.",

    picker_search_placeholder: "Search entity…",
    picker_no_results: "No matching entities found.",

    add_window_sensor: "Add window sensor",
    room_advanced_show: "Advanced",
    room_advanced_hide: "Hide advanced",

    help_btn: "Help",

    section_circuits: "Heating circuits",
    circuits_hint: "Only required if the building has multiple independent heating circuits, each with its own heating pump controller.",
    add_circuit: "Add heating circuit",
    circuit_label: "Circuit name",
    circuit_thermostat: "Heating pump controller",
    circuit_sensor: "Temperature sensor",
    circuit_delete: "Delete",
    circuit_enabled: "Circuit active",
    room_circuit: "Heating circuit",
    circuit_none: "— No circuit (global) —",

    section_outdoor: "Outdoor temperature",
    outdoor_sensor: "Outdoor temperature sensor",
    outdoor_temp_cutoff_enabled: "Cutoff enabled",
    outdoor_temp_cutoff_enabled_hint: "Heating is suppressed when outdoor temperature ≥ threshold.",
    outdoor_temp_cutoff: "Threshold (°C)",
    outdoor_cutoff_hysteresis: "Hysteresis (°C)",
    outdoor_cutoff_hysteresis_hint: "The cutoff is only released once the outdoor temperature drops below threshold − hysteresis.",
    outdoor_min_room_temperature: "Minimum room temperature (°C)",
    outdoor_min_room_temperature_hint: "While the cutoff is active, rooms are only heated up to this temperature. 0 = heating fully blocked.",
    section_cooling: "Cooling",
    cooling_enabled: "Cooling active",
    cooling_enabled_hint: "Manually activates cooling mode via air conditioning. Heating valves are set to minimum.",
    cooling_auto: "Auto cooling",
    cooling_auto_hint: "Automatically activates cooling when outdoor temperature ≥ threshold.",
    cooling_threshold: "Threshold (°C)",
    room_climate_entity: "Air conditioning (climate entity)",
    room_use_climate: "Use AC for heating",
    room_use_climate_hint: "Uses the air conditioning unit for heating instead of the radiator valve.",
    room_climate_heat_boost: "Full-power boost mode",
    room_climate_heat_boost_hint: "Runs the AC at max temperature when heating is needed, then turns it completely off. Requires a room sensor.",
    section_room_cooling: "Cooling settings",
    room_cool_target_day: "Cooling target day (°C)",
    room_cool_target_night: "Cooling target night (°C)",
    room_climate_fan_mode: "Fan speed",
    room_climate_preset: "Preset",
    room_climate_hvac_mode: "HVAC mode",
    climate_fan_auto: "Auto",
    climate_fan_low: "Low",
    climate_fan_medium: "Medium",
    climate_fan_high: "High",
    climate_preset_none: "None",
    climate_preset_eco: "Eco",
    climate_preset_comfort: "Comfort",
    climate_preset_boost: "Boost",
    climate_preset_sleep: "Sleep",
    climate_hvac_cool: "Cool",
    climate_hvac_fan_only: "Fan only",
    climate_hvac_dry: "Dry",
  },

  de: {
    title: "Smartdome Heat Control",
    subtitle:
      "Tippe auf eine Kachel, um den Raum oder die globalen Einstellungen zu bearbeiten.",
    version: "Version",

    reload_rooms: "Räume neu erkennen",
    reload_config: "Neu laden",
    save_config: "Speichern",
    edit_cancel: "Abbrechen",
    edit_delete: "Löschen",
    edit_close: "Schließen",
    edit_discard_question: "Änderungen verwerfen?",
    edit_discard_confirm: "Verwerfen",
    edit_keep_editing: "Weiter bearbeiten",
    edit_delete_question: "{name} wirklich löschen?",
    edit_delete_keep: "Behalten",
    tile_target: "Ziel",
    tile_now: "Aktuell",
    tile_no_reading: "Kein Messwert",
    tile_control: "Steuerung",
    tile_control_on: "Aktiv",
    tile_control_off: "Aus",
    tile_operation: "Betrieb",
    tile_outdoor: "Außen",
    tile_heating_mode: "Heizmodus",
    tile_running_heat: "{count} von {total} heizen",
    tile_running_cool: "{count} von {total} kühlen",
    op_normal: "Normal",
    op_vacation: "Urlaub",
    op_away: "Nicht zuhause",
    op_cooling: "Kühlen",
    op_cutoff: "Außensperre",
    note_vacation: "Urlaub",
    note_away: "Nicht zuhause",
    note_minimum: "Mindesttemperatur",
    status_disabled: "Deaktiviert",
    status_control_off: "Steuerung aus",
    status_sensor_fault: "Sensor ausgefallen",
    status_window_pause: "Fenster offen, Pause",
    status_window_open: "Fenster offen",
    status_cooling: "Kühlt",
    status_heating: "Heizt",
    status_heating_ac: "Heizt über Klima",
    status_residual: "Restwärme",
    status_cutoff: "Außensperre",
    status_idle: "Bereit",
    tile_open: "Einstellungen öffnen",

    status_loading: "Lade Konfiguration …",
    status_initializing: "Initialisiere Panel …",
    status_loaded: "Konfiguration geladen.",
    status_save_loading: "Speichere Konfiguration …",
    status_save_ok: "Konfiguration erfolgreich gespeichert.",
    status_reload_ok: "Konfiguration neu geladen.",
    status_rooms_reload_loading: "Erkenne Räume neu …",
    status_rooms_reload_ok: "Räume wurden neu erkannt.",
    status_apply_times_ok: "Globale Zeiten wurden in alle Räume übernommen.",
    status_no_rooms_apply:
      "Keine Räume vorhanden, auf die Zeiten angewendet werden können.",
    status_vacation_on: "Urlaubsmodus aktiviert.",
    status_vacation_off: "Urlaubsmodus deaktiviert.",
    status_away_on: "Nicht-Zuhause-Modus aktiviert.",
    status_away_off: "Nicht-Zuhause-Modus deaktiviert.",
    status_live_updates_failed: "Live-Updates konnten nicht initialisiert werden.",
    status_save_failed: "Speichern fehlgeschlagen",
    status_reload_failed: "Neu laden fehlgeschlagen",
    status_room_reload_failed: "Raum-Neuladen fehlgeschlagen",
    status_vacation_failed: "Urlaubsmodus konnte nicht geändert werden",
    status_away_failed: "Nicht-Zuhause-Modus konnte nicht geändert werden",

    global_settings: "Globale Einstellungen",
    control_enabled: "Steuerung aktiv",
    control_enabled_hint:
      "Wenn ausgeschaltet, greift die Integration nicht mehr in Thermostate ein.",

    vacation_mode: "Urlaubsmodus",
    vacation_mode_hint:
      "Setzt alle Räume auf die globale Urlaubstemperatur.",

    away_mode: "Nicht Zuhause",
    away_mode_hint:
      "Verwendet pro Raum die konfigurierte Away-Temperatur.",

    btn_vacation_enable: "🏖 Urlaub aktivieren",
    btn_vacation_disable: "🏖 Urlaub deaktivieren",
    btn_away_enable: "🚪 Nicht Zuhause aktivieren",
    btn_away_disable: "🚪 Nicht Zuhause deaktivieren",

    section_control: "Steuerung",
    section_thermostat: "Heizpumpensteuerung",
    section_heating: "Heizung",
    section_times: "Zeiten",

    main_control_type: "Steuertyp",
    control_type_thermostat: "Thermostat",
    control_type_switch: "Smarter Schalter (Switch)",
    main_thermostat: "Heizpumpensteuerung (Climate-Entity)",
    main_switch: "Heizpumpensteuerung (Switch-Entity)",
    main_sensor: "Temperatursensor",
    boost_delta: "Boost-Delta (°C)",
    tolerance: "Toleranz (°C)",
    heating_mode: "Heizmodus",
    energy_residual_heat_hold: "Nachlaufzeit Energy (s)",
    vacation_temperature: "Urlaubstemperatur (°C)",
    night_start: "Globale Nacht-Startzeit",
    morning_boost_start: "Globale Tag-Startzeit",
    morning_boost_end: "Morgen-Boost Ende",

    mode_comfort_desc: "Ventile bleiben länger offen — weniger Temperaturschwankungen, Komfort im Vordergrund.",
    mode_balanced_desc: "Empfohlener Standard — gute Balance aus Komfort und Energieeffizienz.",
    mode_energy_desc: "Ventile schließen früher — reduziert Überhitzen, Energiesparen im Vordergrund.",
    mode_adaptive_desc: "Lernt das Raumverhalten und stoppt die Heizung früher um Überschwingen zu vermeiden.",

    apply_times: "Globale Zeiten in alle Räume übernehmen",
    footer_note:
      'Der Übernehmen-Button setzt für alle Räume: <strong>Tag-Start = globale Tag-Startzeit</strong> und <strong>Nacht-Start = globale Nacht-Startzeit</strong>.',

    section_temperatures: "Temperaturen",
    global_target_day: "Zieltemperatur Tag (°C)",
    global_target_night: "Zieltemperatur Nacht (°C)",
    global_away_temperature: "Away-Temperatur (°C)",
    apply_temps: "Globale Temperaturen in alle Räume übernehmen",
    footer_note_temps: "Der Übernehmen-Button setzt für alle Räume die Zieltemperatur Tag, Nacht und Away auf die globalen Werte.",
    status_apply_temps_ok: "Globale Temperaturen wurden in alle Räume übernommen.",

    room_heating_mode: "Heizmodus",
    room_mode_global: "Global",

    rooms_title: "Räume",
    add_room: "Raum hinzufügen",
    no_rooms: "Noch keine Räume vorhanden.",

    room_active: "Aktiv",
    room_delete: "Löschen",
    room_label: "Bezeichnung",
    room_area_id: "Area-ID",
    room_thermostat: "Heizkörperventil",
    room_extra_thermostats: "Weitere Heizkörperventile",
    add_extra_thermostat: "Heizkörperventil hinzufügen",
    room_switch_actuators: "Schalter-Aktoren (Relais, z. B. Fußbodenheizung)",
    add_switch_actuator: "Schalter-Aktor hinzufügen",
    room_switch_actuators_hint: "Werden anhand des Raumsensors direkt ein-/ausgeschaltet – dafür ist ein Raumtemperatursensor nötig.",
    room_hysteresis: "Hysterese (°C, leer = globale Toleranz)",
    room_switch_min_on: "Schalter-Aktor: Mindest-Laufzeit (min)",
    room_switch_min_off: "Schalter-Aktor: Mindest-Pause (min)",
    room_sensor: "Raumtemperatursensor",
    room_window_sensor: "Fensterkontakt",
    room_control_profile: "Thermostat-Regelprofil",
    control_profile_standard: "Standard-Thermostat",
    control_profile_self_regulating: "Selbst regelndes Thermostat",
    room_target_day: "Zieltemperatur Tag (°C)",
    room_target_night: "Zieltemperatur Nacht (°C)",
    room_night_setback_enabled: "Nachtabsenkung aktiv",
    room_thermostat_offset: "Thermostat-Kalibrierungsoffset (°C)",
    room_away_temperature: "Away-Temperatur (°C)",
    room_away_mode_enabled: "Away-Modus für diesen Raum aktiv",
    room_target_reconcile_enabled: "Sollwert-Abgleich: Sollwert erneut senden, wenn das Ventil ihn nicht übernommen hat (begrenzte Wiederholungen, manuelle Änderungen werden respektiert)",
    room_day_start: "Tag-Start",
    room_night_start: "Nacht-Start",
    room_manual: "Manuell angelegt",
    room_overshoot: "Adaptive Overshoot",
    room_heating_now: "Raum heizt gerade",
    room_window_open: "Fenster offen",
    room_new: "Neuer Raum",
    room_schedule: "Wochenschema",

    select_not_set: "— Nicht gesetzt —",
    select_choose: "— Bitte wählen —",
    select_auto_none: "— Automatisch / keiner —",

    mode_comfort: "Comfort",
    mode_balanced: "Balanced",
    mode_energy: "Energy",
    mode_adaptive: "Adaptive",

    schedule_title: "Wochenschema",
    schedule_add: "Zeitblock hinzufügen",
    schedule_save: "Speichern",
    schedule_cancel: "Abbrechen",
    schedule_empty: "Für diesen Tag sind noch keine Einträge vorhanden.",
    schedule_time: "Zeit",
    schedule_temperature: "Temperatur",
    day_monday: "Mo",
    day_tuesday: "Di",
    day_wednesday: "Mi",
    day_thursday: "Do",
    day_friday: "Fr",
    day_saturday: "Sa",
    day_sunday: "So",

    schedule_copy_rooms: "Auf andere Räume kopieren",
    schedule_copy_title: "Wochenschema kopieren",
    schedule_copy_apply: "Übernehmen",
    schedule_copy_no_rooms: "Keine anderen Räume verfügbar.",

    picker_search_placeholder: "Entity suchen…",
    picker_no_results: "Keine passenden Entities gefunden.",

    add_window_sensor: "Fensterkontakt hinzufügen",
    room_advanced_show: "Erweitert",
    room_advanced_hide: "Erweitert ausblenden",

    help_btn: "Hilfe",

    section_circuits: "Heizkreise",
    circuits_hint: "Nur erforderlich wenn das Gebäude mehrere unabhängige Heizkreise besitzt, die jeweils eine eigene Heizpumpensteuerung haben.",
    add_circuit: "Heizkreis hinzufügen",
    circuit_label: "Kreisbezeichnung",
    circuit_thermostat: "Heizpumpensteuerung",
    circuit_sensor: "Temperatursensor",
    circuit_delete: "Löschen",
    circuit_enabled: "Heizkreis aktiv",
    room_circuit: "Heizkreis",
    circuit_none: "— Kein Kreis (global) —",

    section_outdoor: "Außentemperatur",
    outdoor_sensor: "Außentemperatursensor",
    outdoor_temp_cutoff_enabled: "Abschaltung aktiv",
    outdoor_temp_cutoff_enabled_hint: "Heizung wird unterdrückt wenn Außentemperatur ≥ Schwellenwert.",
    outdoor_temp_cutoff: "Schwellenwert (°C)",
    outdoor_cutoff_hysteresis: "Hysterese (°C)",
    outdoor_cutoff_hysteresis_hint: "Die Sperre wird erst wieder aufgehoben, wenn die Außentemperatur unter Schwellenwert − Hysterese fällt.",
    outdoor_min_room_temperature: "Mindest-Raumtemperatur (°C)",
    outdoor_min_room_temperature_hint: "Während der Sperre wird nur noch bis zu dieser Temperatur geheizt. 0 = Heizung komplett gesperrt.",
    section_cooling: "Kühlen",
    cooling_enabled: "Kühlen aktiv",
    cooling_enabled_hint: "Aktiviert den Kühlmodus manuell über Klimaanlagen. Heizventile werden auf Minimum gesetzt.",
    cooling_auto: "Auto-Kühlen",
    cooling_auto_hint: "Aktiviert Kühlen automatisch wenn Außentemperatur ≥ Schwellenwert.",
    cooling_threshold: "Schwellenwert (°C)",
    room_climate_entity: "Klimaanlage (Climate-Entity)",
    room_use_climate: "Klimaanlage zum Heizen nutzen",
    room_use_climate_hint: "Nutzt die Klimaanlage zum Heizen anstatt des Heizkörperventils.",
    room_climate_heat_boost: "Volllast-Boost-Modus",
    room_climate_heat_boost_hint: "Heizt mit maximaler Leistung solange Heizbedarf besteht, schaltet danach komplett ab. Erfordert einen Raumsensor.",
    section_room_cooling: "Kühleinstellungen",
    room_cool_target_day: "Kühlziel Tag (°C)",
    room_cool_target_night: "Kühlziel Nacht (°C)",
    room_climate_fan_mode: "Lüftergeschwindigkeit",
    room_climate_preset: "Preset",
    room_climate_hvac_mode: "HVAC-Modus",
    climate_fan_auto: "Automatisch",
    climate_fan_low: "Niedrig",
    climate_fan_medium: "Mittel",
    climate_fan_high: "Hoch",
    climate_preset_none: "Kein",
    climate_preset_eco: "Eco",
    climate_preset_comfort: "Komfort",
    climate_preset_boost: "Boost",
    climate_preset_sleep: "Schlaf",
    climate_hvac_cool: "Kühlen",
    climate_hvac_fan_only: "Nur Lüfter",
    climate_hvac_dry: "Entfeuchten",
  },
};

function t(key) {
  return I18N[UI_LANG]?.[key] ?? I18N.en[key] ?? key;
}

function getPanelVersion() {
  const params = new URLSearchParams(window.location.search);
  return params.get("v") || "dev";
}

const PANEL_VERSION = getPanelVersion();
const HEATING_MODES = ["comfort", "balanced", "energy", "adaptive"];
const CONTROL_PROFILES = ["standard", "self_regulating"];

const DEFAULTS = {
  enabled: true,
  main_control_type: "thermostat",
  main_thermostat: "",
  main_switch: "",
  main_sensor: "",
  boost_delta: 2.0,
  tolerance: 0.5,
  heating_mode: "balanced",
  energy_residual_heat_hold: 180,
  night_start: "22:00",
  morning_boost_start: "05:00",
  morning_boost_end: "05:30",
  vacation_enabled: false,
  vacation_temperature: 14.0,
  away_enabled: false,
  outdoor_sensor: "",
  outdoor_temp_cutoff_enabled: false,
  outdoor_temp_cutoff: 15.0,
  outdoor_cutoff_hysteresis: 2.0,
  outdoor_min_room_temperature: 0.0,
  global_target_day: 21.0,
  global_target_night: 18.0,
  global_away_temperature: 17.0,
  cooling_enabled: false,
  cooling_auto: false,
  cooling_threshold: 24.0,
  room_cool_target_day: 23.0,
  room_cool_target_night: 24.0,
  room_climate_fan_mode: "auto",
  room_climate_preset: "",
  room_climate_hvac_mode: "cool",
  rooms: {},
  circuits: {},
};

const state = {
  config: structuredClone(DEFAULTS),
  climates: [],
  sensors: [],
  switches: [],
  binarySensors: [],
  allStates: [],
  roomStatus: {},
};

const entityPickerState = new Map();
let dragSrcRoomId = null;

let els = {};

function initEls() {
  els = {
    statusBox: document.getElementById("statusBox"),
    saveBtn: document.getElementById("saveBtn"),
    reloadConfigBtn: document.getElementById("reloadConfigBtn"),
    reloadRoomsBtn: document.getElementById("reloadRoomsBtn"),
    mainWrap: document.querySelector(".wrap"),
    tileWall: document.getElementById("tileWall"),
    globalForm: document.getElementById("globalForm"),
    editModal: document.getElementById("edit-modal"),
    editModalContent: document.getElementById("edit-modal-content"),
    editModalBody: document.getElementById("edit-modal-body"),
    editModalTitle: document.getElementById("edit-modal-title"),
    editModalLive: document.getElementById("edit-modal-live"),
    editModalClose: document.getElementById("edit-modal-close"),
    editStatus: document.getElementById("edit-status"),
    editDelete: document.getElementById("edit-delete"),
    editQuestion: document.getElementById("edit-question"),
    editCancel: document.getElementById("edit-cancel"),
    editConfirm: document.getElementById("edit-confirm"),
    applyTimesToRoomsBtn: document.getElementById("applyTimesToRoomsBtn"),
    applyTempsToRoomsBtn: document.getElementById("applyTempsToRoomsBtn"),
    globalTargetDay: document.getElementById("global_target_day"),
    globalTargetNight: document.getElementById("global_target_night"),
    globalAwayTemperature: document.getElementById("global_away_temperature"),
    coolingEnabled: document.getElementById("cooling_enabled"),
    coolingAuto: document.getElementById("cooling_auto"),
    coolingThreshold: document.getElementById("cooling_threshold"),
    enabled: document.getElementById("enabled"),
    mainControlType: document.getElementById("main_control_type"),
    mainThermostatField: document.getElementById("main_thermostat_field"),
    mainThermostatPicker: document.getElementById("main_thermostat_picker"),
    mainSwitchField: document.getElementById("main_switch_field"),
    mainSwitchPicker: document.getElementById("main_switch_picker"),
    mainSensorField: document.getElementById("main_sensor_field"),
    mainSensorPicker: document.getElementById("main_sensor_picker"),
    boostDelta: document.getElementById("boost_delta"),
    tolerance: document.getElementById("tolerance"),
    modePickerContainer: document.getElementById("heating_mode_picker"),
    energyResidualHeatHold: document.getElementById("energy_residual_heat_hold"),
    energyHoldField: document.getElementById("energy_hold_field"),
    nightStart: document.getElementById("night_start"),
    morningBoostStart: document.getElementById("morning_boost_start"),
    morningBoostEnd: document.getElementById("morning_boost_end"),
    vacationEnabled: document.getElementById("vacation_enabled"),
    vacationTemperature: document.getElementById("vacation_temperature"),
    awayEnabled: document.getElementById("away_enabled"),
    roomsContainer: document.getElementById("roomsContainer"),
    versionBadge: document.getElementById("versionBadge"),
    circuitsList: document.getElementById("circuitsList"),
    addCircuitBtn: document.getElementById("addCircuitBtn"),
    entityPickerModal: document.getElementById("entity-picker-modal"),
    entityPickerModalTitle: document.getElementById("entity-picker-modal-title"),
    entityPickerModalClose: document.getElementById("entity-picker-modal-close"),
    entityPickerModalSearch: document.getElementById("entity-picker-modal-search"),
    entityPickerModalList: document.getElementById("entity-picker-modal-list"),

    scheduleModal: document.getElementById("schedule-modal"),
    scheduleModalTitle: document.getElementById("schedule-modal-title"),
    scheduleClose: document.getElementById("schedule-close"),
    scheduleCancel: document.getElementById("schedule-cancel"),
    scheduleSave: document.getElementById("schedule-save"),
    scheduleCalendar: document.getElementById("schedule-calendar"),
    scheduleCopyRoomsBtn: document.getElementById("schedule-copy-rooms"),

    scheduleCopyModal: document.getElementById("schedule-copy-modal"),
    scheduleCopyTitle: document.getElementById("schedule-copy-title"),
    scheduleCopyClose: document.getElementById("schedule-copy-close"),
    scheduleCopyCancel: document.getElementById("schedule-copy-cancel"),
    scheduleCopyApply: document.getElementById("schedule-copy-apply"),
    scheduleCopyRoomsList: document.getElementById("schedule-copy-rooms-list"),

    outdoorSensorPicker: document.getElementById("outdoor_sensor_picker"),
    outdoorTempCutoffEnabled: document.getElementById("outdoor_temp_cutoff_enabled"),
    outdoorTempCutoff: document.getElementById("outdoor_temp_cutoff"),
    outdoorCutoffHysteresis: document.getElementById("outdoor_cutoff_hysteresis"),
    outdoorMinRoomTemperature: document.getElementById("outdoor_min_room_temperature"),
  };
}

let unsubscribeStateChanged = null;
let isEditing = false;
let isSaving = false;
let pendingCircuits = null;
let activeEntityPickerId = null;
let scheduleRoomId = null;
let draftWeeklySchedule = null;
// Offenes Popup: { kind: "global" | "room", roomId, isNew, snapshot, baseline, confirm }
let editSession = null;

function setStatus(message, type = "warn") {
  els.statusBox.textContent = message;
  els.statusBox.className = `status ${type}`;

  // Hinter dem offenen Popup wäre die Statuszeile nicht zu sehen.
  if (editSession) {
    els.editStatus.textContent = message;
    els.editStatus.className = `status edit-status ${type}`;
  }
}

function setButtonsDisabled(disabled) {
  els.saveBtn.disabled = disabled;
  els.editCancel.disabled = disabled;
  els.editConfirm.disabled = disabled;
  els.editDelete.disabled = disabled;
  els.reloadConfigBtn.disabled = disabled;
  els.reloadRoomsBtn.disabled = disabled;
  els.applyTimesToRoomsBtn.disabled = disabled;

  if (els.energyResidualHeatHold) {
    els.energyResidualHeatHold.disabled = disabled;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function prettyEntityLabel(item) {
  const friendlyName = item.attributes?.friendly_name || item.entity_id;
  return `${friendlyName} (${item.entity_id})`;
}

function applyTranslations() {
  document.documentElement.lang = UI_LANG;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    el.innerHTML = t(key);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.dataset.i18nPlaceholder;
    el.placeholder = t(key);
  });

  if (els.scheduleModalTitle) {
    els.scheduleModalTitle.textContent = t("schedule_title");
  }

  if (els.scheduleSave) {
    els.scheduleSave.textContent = t("schedule_save");
  }

  if (els.scheduleCancel) {
    els.scheduleCancel.textContent = t("schedule_cancel");
  }

  if (els.scheduleCopyRoomsBtn) {
    els.scheduleCopyRoomsBtn.textContent = t("schedule_copy_rooms");
  }

  if (els.scheduleCopyTitle) {
    els.scheduleCopyTitle.textContent = t("schedule_copy_title");
  }

  if (els.scheduleCopyApply) {
    els.scheduleCopyApply.textContent = t("schedule_copy_apply");
  }

  const dayLabelMap = {
    monday: "day_monday",
    tuesday: "day_tuesday",
    wednesday: "day_wednesday",
    thursday: "day_thursday",
    friday: "day_friday",
    saturday: "day_saturday",
    sunday: "day_sunday",
  };

}

function sortByEntityId(items) {
  return [...items].sort((a, b) => a.entity_id.localeCompare(b.entity_id));
}

function isTemperatureSensor(entity) {
  // climate entities with current_temperature attribute can be used as sensors
  if (entity?.entity_id?.startsWith("climate.")) {
    const currentTemp = entity.attributes?.current_temperature;
    return currentTemp !== undefined && currentTemp !== null && !Number.isNaN(Number(currentTemp));
  }

  if (!entity?.entity_id?.startsWith("sensor.")) {
    return false;
  }

  const deviceClass = entity.attributes?.device_class;
  if (deviceClass === "temperature") {
    return true;
  }

  const entityId = entity.entity_id.toLowerCase();
  const looksLikeTemperature =
    entityId.includes("temp") || entityId.includes("temperature");
  const numericState = !Number.isNaN(Number(entity.state));

  return looksLikeTemperature && numericState;
}

function normalizeTime(value, fallback = "") {
  if (typeof value !== "string") {
    return fallback;
  }

  const raw = value.trim();
  if (!raw) {
    return fallback;
  }

  const match = raw.match(/^(\d{1,2}):(\d{2})(?::\d{2})?$/);
  if (!match) {
    return fallback;
  }

  const hoursNumber = Number(match[1]);
  const minutesNumber = Number(match[2]);

  if (hoursNumber > 23 || minutesNumber > 59) {
    return fallback;
  }

  const hours = String(hoursNumber).padStart(2, "0");
  const minutes = String(minutesNumber).padStart(2, "0");

  return `${hours}:${minutes}`;
}

function normalizeNumber(value, fallback) {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

function normalizeHeatingMode(value) {
  if (typeof value !== "string") {
    return DEFAULTS.heating_mode;
  }

  const normalized = value.trim().toLowerCase();
  return HEATING_MODES.includes(normalized)
    ? normalized
    : DEFAULTS.heating_mode;
}

function normalizeControlProfile(value) {
  if (typeof value !== "string") {
    return "standard";
  }

  const normalized = value.trim().toLowerCase();
  return CONTROL_PROFILES.includes(normalized) ? normalized : "standard";
}

function normalizeScheduleEntry(entry) {
  return {
    start: normalizeTime(entry?.start, "06:00"),
    temperature: normalizeNumber(entry?.temperature, 21.0),
  };
}

function normalizeWeeklySchedule(schedule) {
  const source =
    schedule && typeof schedule === "object" ? schedule : DEFAULT_WEEKLY_SCHEDULE;

  const normalized = {};
  for (const day of WEEK_DAYS) {
    const entries = Array.isArray(source[day]) ? source[day] : [];
    normalized[day] = entries.map((entry) => normalizeScheduleEntry(entry));
    normalized[day].sort((a, b) => a.start.localeCompare(b.start));
  }

  return normalized;
}

function normalizeRoom(roomId, room) {
  return {
    label:
      typeof room?.label === "string" && room.label.trim()
        ? room.label.trim()
        : roomId,
    area_id: typeof room?.area_id === "string" ? room.area_id : "",
    thermostat: typeof room?.thermostat === "string" ? room.thermostat : "",
    extra_thermostats: Array.isArray(room?.extra_thermostats)
      ? room.extra_thermostats.filter((s) => typeof s === "string" && s)
      : [],
    switch_actuators: Array.isArray(room?.switch_actuators)
      ? room.switch_actuators.filter((s) => typeof s === "string" && s)
      : [],
    hysteresis: (() => {
      const value = Number(room?.hysteresis);
      return room?.hysteresis !== "" && room?.hysteresis !== null && Number.isFinite(value) && value > 0
        ? value
        : null;
    })(),
    switch_min_on: Math.max(0, normalizeNumber(room?.switch_min_on, 5)),
    switch_min_off: Math.max(0, normalizeNumber(room?.switch_min_off, 5)),
    sensor: typeof room?.sensor === "string" ? room.sensor : "",
    window_sensor:
      typeof room?.window_sensor === "string" ? room.window_sensor : "",
    window_sensors: (() => {
      if (Array.isArray(room?.window_sensors)) {
        return room.window_sensors.filter((s) => typeof s === "string" && s);
      }
      // migrate legacy single field
      const old = typeof room?.window_sensor === "string" ? room.window_sensor : "";
      return old ? [old] : [];
    })(),
    control_profile: normalizeControlProfile(room?.control_profile),
    thermostat_offset: normalizeNumber(room?.thermostat_offset, 0.0),
    circuit_id: typeof room?.circuit_id === "string" ? room.circuit_id : "",
    target_day: normalizeNumber(room?.target_day, 21.0),
    target_night: normalizeNumber(room?.target_night, 18.0),
    away_temperature: normalizeNumber(room?.away_temperature, 17.0),
    room_away_enabled: room?.room_away_enabled === true,
    room_target_reconcile_enabled: room?.room_target_reconcile_enabled === true,
    weekly_schedule: normalizeWeeklySchedule(room?.weekly_schedule),
    day_start: normalizeTime(room?.day_start, ""),
    night_start: normalizeTime(room?.night_start, ""),
    enabled: room?.enabled !== false,
    night_setback_enabled: room?.night_setback_enabled !== false,
    learned_overshoot: normalizeNumber(room?.learned_overshoot, 0.3),
    learned_overshoot_short: normalizeNumber(room?.learned_overshoot_short, 0.2),
    learned_overshoot_medium: normalizeNumber(room?.learned_overshoot_medium, 0.4),
    learned_overshoot_long: normalizeNumber(room?.learned_overshoot_long, 0.7),
    order: typeof room?.order === "number" ? room.order : 0,
    room_heating_mode: typeof room?.room_heating_mode === "string" ? room.room_heating_mode : "",
    climate_entity: typeof room?.climate_entity === "string" ? room.climate_entity : "",
    use_climate: room?.use_climate === true,
    climate_heat_boost: room?.climate_heat_boost === true,
    cool_target_day: normalizeNumber(room?.cool_target_day, 23.0),
    cool_target_night: normalizeNumber(room?.cool_target_night, 24.0),
    climate_fan_mode: typeof room?.climate_fan_mode === "string" ? room.climate_fan_mode : "auto",
    climate_preset: typeof room?.climate_preset === "string" ? room.climate_preset : "",
    climate_hvac_mode: typeof room?.climate_hvac_mode === "string" ? room.climate_hvac_mode : "cool",
  };
}

function normalizeCircuit(circuitId, circuit) {
  return {
    label:
      typeof circuit?.label === "string" && circuit.label.trim()
        ? circuit.label.trim()
        : circuitId,
    control_type:
      circuit?.control_type === "switch" ? "switch" : "thermostat",
    main_thermostat:
      typeof circuit?.main_thermostat === "string"
        ? circuit.main_thermostat
        : "",
    main_switch:
      typeof circuit?.main_switch === "string" ? circuit.main_switch : "",
    main_sensor:
      typeof circuit?.main_sensor === "string" ? circuit.main_sensor : "",
    enabled: circuit?.enabled !== false,
  };
}

function normalizeConfig(input) {
  const cfg = {
    ...structuredClone(DEFAULTS),
    ...(input || {}),
  };

  cfg.enabled = cfg.enabled !== false;
  cfg.main_control_type =
    cfg.main_control_type === "switch" ? "switch" : "thermostat";
  cfg.main_thermostat =
    typeof cfg.main_thermostat === "string" ? cfg.main_thermostat : "";
  cfg.main_switch =
    typeof cfg.main_switch === "string" ? cfg.main_switch : "";
  cfg.main_sensor = typeof cfg.main_sensor === "string" ? cfg.main_sensor : "";
  cfg.boost_delta = normalizeNumber(cfg.boost_delta, DEFAULTS.boost_delta);
  cfg.tolerance = normalizeNumber(cfg.tolerance, DEFAULTS.tolerance);
  cfg.heating_mode = normalizeHeatingMode(cfg.heating_mode);
  cfg.energy_residual_heat_hold = normalizeNumber(
    cfg.energy_residual_heat_hold,
    DEFAULTS.energy_residual_heat_hold
  );
  cfg.night_start = normalizeTime(cfg.night_start, DEFAULTS.night_start);
  cfg.morning_boost_start = normalizeTime(
    cfg.morning_boost_start,
    DEFAULTS.morning_boost_start
  );
  cfg.morning_boost_end = normalizeTime(
    cfg.morning_boost_end,
    DEFAULTS.morning_boost_end
  );
  cfg.vacation_enabled = cfg.vacation_enabled === true;
  cfg.vacation_temperature = normalizeNumber(
    cfg.vacation_temperature,
    DEFAULTS.vacation_temperature
  );
  cfg.away_enabled = cfg.away_enabled === true;
  cfg.global_target_day = normalizeNumber(cfg.global_target_day, DEFAULTS.global_target_day);
  cfg.global_target_night = normalizeNumber(cfg.global_target_night, DEFAULTS.global_target_night);
  cfg.global_away_temperature = normalizeNumber(cfg.global_away_temperature, DEFAULTS.global_away_temperature);
  cfg.cooling_enabled = cfg.cooling_enabled === true;
  cfg.cooling_auto = cfg.cooling_auto === true;
  cfg.cooling_threshold = normalizeNumber(cfg.cooling_threshold, DEFAULTS.cooling_threshold);

  if (!cfg.rooms || typeof cfg.rooms !== "object") {
    cfg.rooms = {};
  }

  const normalizedRooms = {};
  for (const [roomId, room] of Object.entries(cfg.rooms)) {
    normalizedRooms[roomId] = normalizeRoom(roomId, room);
  }
  cfg.rooms = normalizedRooms;

  if (!cfg.circuits || typeof cfg.circuits !== "object") {
    cfg.circuits = {};
  }

  const normalizedCircuits = {};
  for (const [circuitId, circuit] of Object.entries(cfg.circuits)) {
    normalizedCircuits[circuitId] = normalizeCircuit(circuitId, circuit);
  }
  cfg.circuits = normalizedCircuits;

  return cfg;
}

function findState(entityId) {
  if (!entityId) {
    return null;
  }
  return state.allStates.find((item) => item.entity_id === entityId) || null;
}

function getSensorTemperature(sensorId) {
  const sensor = findState(sensorId);
  if (!sensor) {
    return null;
  }

  // climate entities expose temperature in attributes, not state
  const raw = sensor.entity_id?.startsWith("climate.")
    ? sensor.attributes?.current_temperature
    : sensor.state;

  const value = Number(raw);
  if (!Number.isFinite(value)) {
    return null;
  }

  return value;
}

function formatTemperature(temp) {
  if (!Number.isFinite(temp)) {
    return "—";
  }

  return `${temp.toFixed(1)} °C`;
}

function isRoomHeating(roomId) {
  const roomState = state.config.room_states?.[roomId];
  if (roomState !== undefined) {
    return roomState === "heating";
  }
  // Fallback: hvac_action vom Thermostat-Entity
  const room = state.config.rooms?.[roomId];
  const thermostat = findState(room?.thermostat);
  return thermostat?.attributes?.hvac_action === "heating";
}

function isWindowOpen(windowSensorId) {
  const sensor = findState(windowSensorId);
  if (!sensor) {
    return false;
  }

  const value = String(sensor.state || "").toLowerCase();
  return value === "on" || value === "open" || value === "true";
}

function getThermostatSetpoint(thermostatId) {
  const entity = findState(thermostatId);
  if (!entity) return null;
  const val = Number(entity.attributes?.temperature);
  return Number.isFinite(val) ? val : null;
}

function isThermostatHeating(thermostatId) {
  const entity = findState(thermostatId);
  return entity?.attributes?.hvac_action === "heating";
}

function openEntityMoreInfo(entityId) {
  if (!entityId) return;
  try {
    const haEl = window.parent?.document?.querySelector("home-assistant");
    if (haEl) {
      haEl.dispatchEvent(
        new CustomEvent("hass-more-info", {
          bubbles: true,
          composed: true,
          detail: { entityId },
        })
      );
    }
  } catch (_) {
    // cross-origin or permission error — silently ignore
  }
}

function isAnyWindowOpen(room) {
  const sensors = Array.isArray(room.window_sensors) ? room.window_sensors : [];
  return sensors.some((id) => isWindowOpen(id));
}

function renderVersion() {
  if (els.versionBadge) {
    els.versionBadge.textContent = `${t("version")} ${PANEL_VERSION}`;
  }
}

function updateMainLiveStatus() {
  const thermostatId = getEntityPickerValue("global_main_thermostat_picker");
  const sensorId = getEntityPickerValue("global_main_sensor_picker");

  const thermostatLive = document.getElementById("global_thermostat_live");
  if (thermostatLive) {
    if (thermostatId) {
      const heating = isThermostatHeating(thermostatId);
      const setpoint = getThermostatSetpoint(thermostatId);
      if (setpoint !== null) {
        thermostatLive.innerHTML = `${heating ? "🔥 " : ""}${escapeHtml(formatTemperature(setpoint))}`;
        thermostatLive.dataset.entity = thermostatId;
      } else {
        thermostatLive.textContent = "";
        delete thermostatLive.dataset.entity;
      }
    } else {
      thermostatLive.textContent = "";
      delete thermostatLive.dataset.entity;
    }
  }

  const sensorLive = document.getElementById("global_sensor_live");
  if (sensorLive) {
    const tempSrc = sensorId || thermostatId;
    const temp = tempSrc ? getSensorTemperature(tempSrc) : null;
    if (temp !== null) {
      sensorLive.textContent = formatTemperature(temp);
      sensorLive.dataset.entity = tempSrc;
    } else {
      sensorLive.textContent = "";
      delete sensorLive.dataset.entity;
    }
  }

  const switchLive = document.getElementById("global_switch_live");
  if (switchLive) {
    const switchId = getEntityPickerValue("global_main_switch_picker");
    if (switchId) {
      const switchState = findState(switchId);
      const isOn = switchState?.state === "on";
      switchLive.innerHTML = isOn ? "🟢 on" : "⚫ off";
      switchLive.dataset.entity = switchId;
    } else {
      switchLive.textContent = "";
      delete switchLive.dataset.entity;
    }
  }

  const outdoorLive = document.getElementById("global_outdoor_live");
  if (outdoorLive) {
    const outdoorId = getEntityPickerValue("global_outdoor_sensor_picker");
    const temp = outdoorId ? getSensorTemperature(outdoorId) : null;
    if (temp !== null) {
      outdoorLive.textContent = formatTemperature(temp);
      outdoorLive.dataset.entity = outdoorId;
    } else {
      outdoorLive.textContent = "";
      delete outdoorLive.dataset.entity;
    }
  }
}

let modePickerValue = "balanced";

function getModePickerValue() {
  return modePickerValue;
}

function updateEnergyFieldVisibility() {
  if (!els.energyHoldField) return;
  els.energyHoldField.classList.toggle("hidden", modePickerValue !== "energy");
}

function createModePicker(currentValue) {
  if (!els.modePickerContainer) return;

  modePickerValue = normalizeHeatingMode(currentValue);

  const modes = [
    { value: "comfort",  label: t("mode_comfort"),  desc: t("mode_comfort_desc") },
    { value: "balanced", label: t("mode_balanced"), desc: t("mode_balanced_desc") },
    { value: "energy",   label: t("mode_energy"),   desc: t("mode_energy_desc") },
    { value: "adaptive", label: t("mode_adaptive"), desc: t("mode_adaptive_desc") },
  ];

  const current = modes.find((m) => m.value === modePickerValue) || modes[1];

  els.modePickerContainer.innerHTML = `
    <div class="mode-picker" id="mode_picker_root">
      <button type="button" class="mode-picker-trigger">
        <span class="mode-picker-trigger-label">${escapeHtml(current.label)}</span>
        <span class="mode-picker-trigger-desc">${escapeHtml(current.desc)}</span>
      </button>
      <div class="mode-picker-dropdown">
        ${modes.map((m) => `
          <button type="button" class="mode-picker-option${m.value === modePickerValue ? " selected" : ""}" data-value="${m.value}">
            <span class="mode-picker-option-label">${escapeHtml(m.label)}</span>
            <span class="mode-picker-option-desc">${escapeHtml(m.desc)}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;

  const root = els.modePickerContainer.querySelector("#mode_picker_root");
  const trigger = root.querySelector(".mode-picker-trigger");
  const dropdown = root.querySelector(".mode-picker-dropdown");

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    root.classList.toggle("open");
  });

  root.addEventListener("click", (e) => e.stopPropagation());

  root.querySelectorAll(".mode-picker-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      modePickerValue = btn.dataset.value;
      root.classList.remove("open");

      const selected = modes.find((m) => m.value === modePickerValue) || modes[1];
      trigger.querySelector(".mode-picker-trigger-label").textContent = selected.label;
      trigger.querySelector(".mode-picker-trigger-desc").textContent = selected.desc;

      root.querySelectorAll(".mode-picker-option").forEach((b) => {
        b.classList.toggle("selected", b.dataset.value === modePickerValue);
      });

      updateEnergyFieldVisibility();
    });
  });

  document.addEventListener("click", () => root.classList.remove("open"), { once: false });

  updateEnergyFieldVisibility();
}

function generateCircuitId() {
  return `circuit_${Math.random().toString(16).slice(2, 10)}`;
}

function addCircuit() {
  const circuitId = generateCircuitId();
  state.config.circuits[circuitId] = {
    label: "",
    control_type: "thermostat",
    main_thermostat: "",
    main_switch: "",
    main_sensor: "",
    enabled: true,
  };
  pendingCircuits = { ...state.config.circuits };
  renderCircuits();
}

function createCircuitCard(circuitId, circuit) {
  const card = document.createElement("div");
  card.className = "circuit-card";
  card.dataset.circuitId = circuitId;

  card.innerHTML = `
    <div class="circuit-card-header">
      <input
        class="circuit-label"
        type="text"
        placeholder="${escapeHtml(t("circuit_label"))}"
        value="${escapeHtml(circuit.label || "")}"
        style="flex:1; margin:0;"
      />
      <label class="toggle-label" style="display:flex;align-items:center;gap:6px;font-size:12px;white-space:nowrap;">
        <input type="checkbox" class="circuit-enabled-checkbox" ${circuit.enabled !== false ? "checked" : ""}>
        ${escapeHtml(t("circuit_enabled"))}
      </label>
      <button type="button" class="danger circuit-delete-btn" style="padding:8px 12px; font-size:12px;">
        ${escapeHtml(t("circuit_delete"))}
      </button>
    </div>
    <div class="circuit-card-fields"${circuit.enabled === false ? ' style="opacity:0.5;pointer-events:none;"' : ""}>
      <div class="field full">
        <label>${escapeHtml(t("main_control_type"))}</label>
        <select class="circuit-control-type">
          <option value="thermostat"${circuit.control_type !== "switch" ? " selected" : ""}>${escapeHtml(t("control_type_thermostat"))}</option>
          <option value="switch"${circuit.control_type === "switch" ? " selected" : ""}>${escapeHtml(t("control_type_switch"))}</option>
        </select>
      </div>
      <div class="field circuit-thermostat-field"${circuit.control_type === "switch" ? ' style="display:none;"' : ""}>
        <label>${escapeHtml(t("circuit_thermostat"))}</label>
        <div class="circuit-thermostat-picker"></div>
      </div>
      <div class="field circuit-switch-field"${circuit.control_type !== "switch" ? ' style="display:none;"' : ""}>
        <label>${escapeHtml(t("main_switch"))}</label>
        <div class="circuit-switch-picker"></div>
      </div>
      <div class="field circuit-sensor-field"${circuit.control_type === "switch" ? ' style="display:none;"' : ""}>
        <label>${escapeHtml(t("circuit_sensor"))}</label>
        <div class="circuit-sensor-picker"></div>
      </div>
    </div>
  `;

  const ctSelect = card.querySelector(".circuit-control-type");
  ctSelect.addEventListener("change", () => {
    const isSwitch = ctSelect.value === "switch";
    card.querySelector(".circuit-thermostat-field").style.display = isSwitch ? "none" : "";
    card.querySelector(".circuit-switch-field").style.display = isSwitch ? "" : "none";
    card.querySelector(".circuit-sensor-field").style.display = isSwitch ? "none" : "";
  });

  const enabledCheckbox = card.querySelector(".circuit-enabled-checkbox");
  const fieldsDiv = card.querySelector(".circuit-card-fields");
  enabledCheckbox.addEventListener("change", () => {
    const enabled = enabledCheckbox.checked;
    fieldsDiv.style.opacity = enabled ? "" : "0.5";
    fieldsDiv.style.pointerEvents = enabled ? "" : "none";
  });

  createEntityPicker({
    container: card.querySelector(".circuit-thermostat-picker"),
    pickerId: `circuit_${circuitId}_thermostat_picker`,
    items: state.climates,
    getItems: () => state.climates,
    selectedValue: circuit.main_thermostat || "",
    emptyLabel: t("select_auto_none"),
    onChange: () => {},
  });

  createEntityPicker({
    container: card.querySelector(".circuit-switch-picker"),
    pickerId: `circuit_${circuitId}_switch_picker`,
    items: state.switches,
    getItems: () => state.switches,
    selectedValue: circuit.main_switch || "",
    emptyLabel: t("select_auto_none"),
    onChange: () => {},
  });

  createEntityPicker({
    container: card.querySelector(".circuit-sensor-picker"),
    pickerId: `circuit_${circuitId}_sensor_picker`,
    items: state.sensors,
    getItems: () => state.sensors,
    selectedValue: circuit.main_sensor || "",
    emptyLabel: t("select_auto_none"),
    onChange: () => {},
  });

  card.querySelector(".circuit-delete-btn").addEventListener("click", () => {
    delete state.config.circuits[circuitId];
    pendingCircuits = { ...state.config.circuits };
    // clear circuit_id on rooms that referenced this circuit
    for (const room of Object.values(state.config.rooms)) {
      if (room.circuit_id === circuitId) {
        room.circuit_id = "";
      }
    }
    renderCircuits();
    renderRooms();
  });

  return card;
}

function renderCircuits() {
  if (!els.circuitsList) return;

  els.circuitsList.innerHTML = "";
  const entries = Object.entries(state.config.circuits || {});

  for (const [circuitId, circuit] of entries) {
    els.circuitsList.appendChild(createCircuitCard(circuitId, circuit));
  }
}

function getCircuitOptions() {
  const options = [{ value: "", label: t("circuit_none") }];
  for (const [circuitId, circuit] of Object.entries(
    state.config.circuits || {}
  )) {
    options.push({
      value: circuitId,
      label: circuit.label || circuitId,
    });
  }
  return options;
}

function getEntityIcon(entityId) {
  if (!entityId) {
    return "—";
  }
  if (entityId.startsWith("climate.")) {
    return "🌡️";
  }
  if (entityId.startsWith("binary_sensor.")) {
    return "🪟";
  }
  if (entityId.startsWith("sensor.")) {
    return "🌡️";
  }
  return "•";
}

function getEntityTitle(item) {
  return item?.attributes?.friendly_name || item?.entity_id || "";
}

function closeAllEntityPickers() {
  closeEntityPickerModal();
}

function openEntityPickerModal(pickerId) {
  const config = entityPickerState.get(pickerId);
  if (!config || !els.entityPickerModal) return;

  activeEntityPickerId = pickerId;

  if (els.entityPickerModalTitle) {
    els.entityPickerModalTitle.textContent = config.emptyLabel || t("select_choose");
  }
  if (els.entityPickerModalSearch) {
    els.entityPickerModalSearch.value = "";
    els.entityPickerModalSearch.placeholder = t("picker_search_placeholder");
  }

  renderEntityPickerModalList("");
  els.entityPickerModal.classList.remove("hidden");
  setTimeout(() => els.entityPickerModalSearch?.focus(), 50);
}

function closeEntityPickerModal() {
  if (els.entityPickerModal) {
    els.entityPickerModal.classList.add("hidden");
  }
  activeEntityPickerId = null;
}

function renderEntityPickerModalList(query = "") {
  if (!activeEntityPickerId || !els.entityPickerModalList) return;

  const config = entityPickerState.get(activeEntityPickerId);
  if (!config) return;

  const q = String(query || "").trim().toLowerCase();

  const currentItems = config.getItems ? config.getItems() : config.items;

  const entries = [
    {
      entity_id: "",
      attributes: { friendly_name: config.emptyLabel },
      __empty: true,
    },
    ...currentItems,
  ].filter((item) => {
    if (!q) return true;
    const haystack = `${item.entity_id} ${getEntityTitle(item)}`.toLowerCase();
    return haystack.includes(q);
  });

  els.entityPickerModalList.innerHTML = "";

  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "entity-picker-no-results";
    empty.textContent = t("picker_no_results");
    els.entityPickerModalList.appendChild(empty);
    return;
  }

  for (const item of entries) {
    const option = document.createElement("button");
    option.type = "button";
    option.className = "entity-picker-option";

    if ((config.selectedValue || "") === item.entity_id) {
      option.classList.add("active");
    }

    const icon = item.__empty ? "—" : getEntityIcon(item.entity_id);
    const title = item.__empty ? config.emptyLabel : getEntityTitle(item);

    option.innerHTML = `
      <span class="entity-picker-icon">${icon}</span>
      <span class="entity-picker-option-text">
        <span class="entity-picker-option-title">${escapeHtml(title)}</span>
        <span class="entity-picker-option-id">${
          item.entity_id ? escapeHtml(item.entity_id) : "&nbsp;"
        }</span>
      </span>
    `;

    option.addEventListener("click", () => {
      const pickerId = activeEntityPickerId;
      config.selectedValue = item.entity_id || "";

      if (typeof config.onChange === "function") {
        config.onChange(config.selectedValue);
      }

      // update trigger display
      const root = document.getElementById(pickerId);
      if (root) {
        const triggerIcon = root.querySelector(".entity-picker-trigger .entity-picker-icon");
        const triggerLabel = root.querySelector(".entity-picker-trigger .entity-picker-label");
        if (triggerIcon) triggerIcon.textContent = item.__empty ? "—" : icon;
        if (triggerLabel) {
          triggerLabel.textContent = title;
          triggerLabel.classList.toggle("entity-picker-empty", !!item.__empty);
        }
      }

      closeEntityPickerModal();
    });

    els.entityPickerModalList.appendChild(option);
  }
}

function createEntityPicker({
  container,
  pickerId,
  items,
  getItems,
  selectedValue,
  emptyLabel,
  onChange,
}) {
  if (!container) return;

  const normalizedItems = Array.isArray(items) ? items : [];

  // Bestehende User-Auswahl beibehalten: Wenn der Picker schon einen State hat
  // (z.B. weil der Nutzer bereits eine Entity gewählt hat), wird dieser NICHT
  // durch einen Hintergrund-Re-Render (state_changed) überschrieben.
  // Nur beim ersten Rendern (kein existierender State) wird selectedValue aus
  // den Props verwendet.
  const existingState = entityPickerState.get(pickerId);
  const effectiveValue = existingState
    ? existingState.selectedValue
    : selectedValue || "";

  entityPickerState.set(pickerId, {
    items: normalizedItems,
    getItems: getItems || null,
    selectedValue: effectiveValue,
    onChange,
    emptyLabel,
  });

  const selectedItem =
    normalizedItems.find((item) => item.entity_id === effectiveValue) || null;

  container.innerHTML = `
    <div class="entity-picker" id="${pickerId}">
      <button type="button" class="entity-picker-trigger">
        <span class="entity-picker-icon">${
          selectedItem ? getEntityIcon(selectedItem.entity_id) : "—"
        }</span>
        <span class="entity-picker-label ${
          selectedItem ? "" : "entity-picker-empty"
        }">${
          selectedItem
            ? escapeHtml(getEntityTitle(selectedItem))
            : escapeHtml(emptyLabel)
        }</span>
      </button>
    </div>
  `;

  const root = container.querySelector(".entity-picker");
  const trigger = root.querySelector(".entity-picker-trigger");

  trigger.addEventListener("click", (event) => {
    event.stopPropagation();
    openEntityPickerModal(pickerId);
  });
}

function getEntityPickerValue(pickerId) {
  return entityPickerState.get(pickerId)?.selectedValue || "";
}

async function getHassConnection() {
  if (window.hassConnection) {
    return window.hassConnection;
  }

  if (window.parent?.hassConnection) {
    return window.parent.hassConnection;
  }

  throw new Error("Keine Home-Assistant-Verbindung verfügbar");
}

async function getAccessToken() {
  const conn = await getHassConnection();
  const token = conn?.auth?.data?.access_token;

  if (!token) {
    throw new Error("Kein Zugriffstoken verfügbar");
  }

  return token;
}

async function haFetch(path, options = {}) {
  const token = await getAccessToken();

  const response = await fetch(path, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const text = await response.text();

  if (!response.ok) {
    throw new Error(
      `${response.status} ${response.statusText}${text ? ` – ${text}` : ""}`
    );
  }

  return text ? JSON.parse(text) : null;
}

async function getHassWS() {
  const haConn = await getHassConnection();
  const ws = haConn?.conn || haConn;
  if (!ws || typeof ws.sendMessagePromise !== "function") {
    throw new Error("WebSocket-Verbindung nicht verfügbar");
  }
  return ws;
}

async function callService(domain, service, data = {}) {
  const ws = await getHassWS();
  return ws.sendMessagePromise({
    type: "call_service",
    domain,
    service,
    service_data: data,
  });
}

async function loadAllStates() {
  const ws = await getHassWS();
  const states = await ws.sendMessagePromise({ type: "get_states" });
  state.allStates = Array.isArray(states) ? states : [];

  state.climates = sortByEntityId(
    state.allStates.filter((item) => item.entity_id?.startsWith("climate."))
  );

  state.sensors = sortByEntityId(
    state.allStates.filter((item) => isTemperatureSensor(item))
  );

  state.switches = sortByEntityId(
    state.allStates.filter((item) => item.entity_id?.startsWith("switch."))
  );

  state.switchActuators = sortByEntityId(
    state.allStates.filter(
      (item) =>
        item.entity_id?.startsWith("switch.") ||
        item.entity_id?.startsWith("input_boolean.")
    )
  );

  state.binarySensors = sortByEntityId(
    state.allStates.filter((item) =>
      item.entity_id?.startsWith("binary_sensor.")
    )
  );
}

async function loadConfig() {
  const entity = state.allStates.find(
    (s) => s.entity_id === CONFIG_ENTITY_ID
  );
  state.config = normalizeConfig(entity?.attributes || {});
  state.roomStatus = entity?.attributes?.room_status || {};
}

function updateMainControlTypeVisibility(type) {
  const isSwitch = type === "switch";
  if (els.mainThermostatField) els.mainThermostatField.style.display = isSwitch ? "none" : "";
  if (els.mainSwitchField) els.mainSwitchField.style.display = isSwitch ? "" : "none";
  if (els.mainSensorField) els.mainSensorField.style.display = isSwitch ? "none" : "";
}

function renderGlobalSettings() {
  const cfg = state.config;

  els.enabled.checked = cfg.enabled;
  els.boostDelta.value = String(cfg.boost_delta);
  els.tolerance.value = String(cfg.tolerance);
  els.nightStart.value = cfg.night_start;
  els.morningBoostStart.value = cfg.morning_boost_start;
  els.morningBoostEnd.value = cfg.morning_boost_end;

  if (els.energyResidualHeatHold) {
    els.energyResidualHeatHold.value = String(
      normalizeNumber(
        cfg.energy_residual_heat_hold,
        DEFAULTS.energy_residual_heat_hold
      )
    );
  }

  if (els.vacationEnabled) {
    els.vacationEnabled.checked = cfg.vacation_enabled;
  }

  if (els.vacationTemperature) {
    els.vacationTemperature.value = String(cfg.vacation_temperature);
  }

  if (els.awayEnabled) {
    els.awayEnabled.checked = cfg.away_enabled;
  }

  if (els.mainControlType) {
    els.mainControlType.value = cfg.main_control_type || "thermostat";
    updateMainControlTypeVisibility(cfg.main_control_type);
    els.mainControlType.onchange = () => {
      updateMainControlTypeVisibility(els.mainControlType.value);
    };
  }

  createEntityPicker({
    container: els.mainThermostatPicker,
    pickerId: "global_main_thermostat_picker",
    items: state.climates,
    getItems: () => state.climates,
    selectedValue: cfg.main_thermostat,
    emptyLabel: t("select_choose"),
    onChange: () => {},
  });

  createEntityPicker({
    container: els.mainSwitchPicker,
    pickerId: "global_main_switch_picker",
    items: state.switches,
    getItems: () => state.switches,
    selectedValue: cfg.main_switch,
    emptyLabel: t("select_choose"),
    onChange: () => {},
  });

  createEntityPicker({
    container: els.mainSensorPicker,
    pickerId: "global_main_sensor_picker",
    items: state.sensors,
    getItems: () => state.sensors,
    selectedValue: cfg.main_sensor,
    emptyLabel: t("select_auto_none"),
    onChange: () => {},
  });

  if (els.outdoorSensorPicker) {
    createEntityPicker({
      container: els.outdoorSensorPicker,
      pickerId: "global_outdoor_sensor_picker",
      items: state.sensors,
      getItems: () => state.sensors,
      selectedValue: cfg.outdoor_sensor || "",
      emptyLabel: t("select_not_set"),
      onChange: () => {},
    });
  }

  if (els.outdoorTempCutoffEnabled) {
    els.outdoorTempCutoffEnabled.checked = cfg.outdoor_temp_cutoff_enabled ?? false;
  }

  if (els.outdoorTempCutoff) {
    els.outdoorTempCutoff.value = String(
      normalizeNumber(cfg.outdoor_temp_cutoff, DEFAULTS.outdoor_temp_cutoff)
    );
  }

  if (els.outdoorCutoffHysteresis) {
    els.outdoorCutoffHysteresis.value = String(
      normalizeNumber(cfg.outdoor_cutoff_hysteresis, DEFAULTS.outdoor_cutoff_hysteresis)
    );
  }

  if (els.outdoorMinRoomTemperature) {
    els.outdoorMinRoomTemperature.value = String(
      normalizeNumber(cfg.outdoor_min_room_temperature, DEFAULTS.outdoor_min_room_temperature)
    );
  }

  if (els.globalTargetDay) {
    els.globalTargetDay.value = String(normalizeNumber(cfg.global_target_day, DEFAULTS.global_target_day));
  }
  if (els.globalTargetNight) {
    els.globalTargetNight.value = String(normalizeNumber(cfg.global_target_night, DEFAULTS.global_target_night));
  }
  if (els.globalAwayTemperature) {
    els.globalAwayTemperature.value = String(normalizeNumber(cfg.global_away_temperature, DEFAULTS.global_away_temperature));
  }

  if (els.coolingEnabled) els.coolingEnabled.checked = cfg.cooling_enabled ?? false;
  if (els.coolingAuto) els.coolingAuto.checked = cfg.cooling_auto ?? false;
  if (els.coolingThreshold) {
    els.coolingThreshold.value = String(normalizeNumber(cfg.cooling_threshold, DEFAULTS.cooling_threshold));
  }

  createModePicker(cfg.heating_mode);
  renderCircuits();
  updateMainLiveStatus();
}

function appendWindowSensorRow(listEl, roomId, sensorId) {
  const index = listEl.children.length;
  const pickerId = `room_${roomId}_ws_${index}`;

  const row = document.createElement("div");
  row.className = "room-window-sensor-row";
  row.style.cssText = "display:flex; gap:8px; align-items:center; margin-bottom:6px;";
  row.dataset.wsPickerId = pickerId;

  const pickerContainer = document.createElement("div");
  pickerContainer.style.flex = "1";

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "ghost";
  removeBtn.style.cssText = "padding:8px 10px; flex-shrink:0;";
  removeBtn.textContent = "✕";
  removeBtn.addEventListener("click", () => row.remove());

  row.appendChild(pickerContainer);
  row.appendChild(removeBtn);
  listEl.appendChild(row);

  createEntityPicker({
    container: pickerContainer,
    pickerId,
    items: state.binarySensors,
    getItems: () => state.binarySensors,
    selectedValue: sensorId || "",
    emptyLabel: t("select_not_set"),
    onChange: () => {},
  });
}

function appendSwitchActuatorRow(listEl, roomId, switchId) {
  const index = listEl.children.length;
  const pickerId = `room_${roomId}_switch_actuator_${index}`;

  const row = document.createElement("div");
  row.className = "room-switch-actuator-row";
  row.style.cssText = "display:flex; gap:8px; align-items:center; margin-bottom:6px;";
  row.dataset.switchPickerId = pickerId;

  const pickerContainer = document.createElement("div");
  pickerContainer.style.flex = "1";

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "ghost";
  removeBtn.style.cssText = "padding:8px 10px; flex-shrink:0;";
  removeBtn.textContent = "✕";
  removeBtn.addEventListener("click", () => row.remove());

  row.appendChild(pickerContainer);
  row.appendChild(removeBtn);
  listEl.appendChild(row);

  createEntityPicker({
    container: pickerContainer,
    pickerId,
    items: state.switchActuators || [],
    getItems: () => state.switchActuators || [],
    selectedValue: switchId || "",
    emptyLabel: t("select_not_set"),
    onChange: () => {},
  });
}

function appendExtraThermostatRow(listEl, roomId, thermostatId) {
  const index = listEl.children.length;
  const pickerId = `room_${roomId}_extra_thermostat_${index}`;

  const row = document.createElement("div");
  row.className = "room-extra-thermostat-row";
  row.style.cssText = "display:flex; gap:8px; align-items:center; margin-bottom:6px;";
  row.dataset.thermostatPickerId = pickerId;

  const pickerContainer = document.createElement("div");
  pickerContainer.style.flex = "1";

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "ghost";
  removeBtn.style.cssText = "padding:8px 10px; flex-shrink:0;";
  removeBtn.textContent = "✕";
  removeBtn.addEventListener("click", () => row.remove());

  row.appendChild(pickerContainer);
  row.appendChild(removeBtn);
  listEl.appendChild(row);

  createEntityPicker({
    container: pickerContainer,
    pickerId,
    items: state.climates,
    getItems: () => state.climates,
    selectedValue: thermostatId || "",
    emptyLabel: t("select_not_set"),
    onChange: () => {},
  });
}

function createRoomCard(roomId, room) {
  const wrapper = document.createElement("div");
  wrapper.className = "room";
  wrapper.dataset.roomId = roomId;

  const isAdaptive = getModePickerValue() === "adaptive";
  const ovShort = normalizeNumber(room.learned_overshoot_short, 0.2);
  const ovMedium = normalizeNumber(room.learned_overshoot_medium, 0.4);
  const ovLong = normalizeNumber(room.learned_overshoot_long, 0.7);
  const roomMode = room.room_heating_mode || "";
  const modeOptions = [
    { value: "", label: t("room_mode_global") },
    { value: "comfort", label: t("mode_comfort") },
    { value: "balanced", label: t("mode_balanced") },
    { value: "energy", label: t("mode_energy") },
    { value: "adaptive", label: t("mode_adaptive") },
  ].map(o => `<option value="${o.value}"${roomMode === o.value ? " selected" : ""}>${escapeHtml(o.label)}</option>`).join("");

  wrapper.innerHTML = `
    <div class="room-top">
      <div class="room-top-row">
        <span class="pill">
          <input class="room-enabled" type="checkbox" ${
            room.enabled ? "checked" : ""
          } />
          <span>${escapeHtml(t("room_active"))}</span>
        </span>
        <button class="ghost room-schedule-btn" type="button">${escapeHtml(t("room_schedule"))}</button>
      </div>
      ${isAdaptive ? `
      <div class="room-adaptive room-adaptive-display">
        <span class="adaptive-bucket">
          <span style="color:var(--muted)">▲ &lt;15min</span>
          <span class="adaptive-bucket-value">${ovShort.toFixed(2)} °C</span>
        </span>
        <span class="adaptive-bucket">
          <span style="color:var(--muted)">▲ 15–45min</span>
          <span class="adaptive-bucket-value">${ovMedium.toFixed(2)} °C</span>
        </span>
        <span class="adaptive-bucket">
          <span style="color:var(--muted)">▲ &gt;45min</span>
          <span class="adaptive-bucket-value">${ovLong.toFixed(2)} °C</span>
        </span>
      </div>` : ""}
      <div class="room-mode-row" style="display:flex; align-items:center; gap:8px;">
        <label style="font-size:13px; color:var(--muted); white-space:nowrap;">${escapeHtml(t("room_heating_mode"))}:</label>
        <select class="room-heating-mode" style="font-size:13px; padding:3px 6px;">${modeOptions}</select>
      </div>
    </div>

    <div class="room-grid">
      <div class="field">
        <label>${escapeHtml(t("room_label"))}</label>
        <input class="room-label" type="text" value="${escapeHtml(
          room.label || ""
        )}" />
      </div>

      <div class="field">
        <label style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <span>${escapeHtml(t("room_thermostat"))}</span>
          <span class="label-live room-thermostat-live"></span>
        </label>
        <div class="room-thermostat-picker"></div>
      </div>

      <div class="field full">
        <label>${escapeHtml(t("room_extra_thermostats"))}</label>
        <div class="room-extra-thermostats-list"></div>
        <button type="button" class="ghost room-add-thermostat-btn" style="width:100%; margin-top:6px; font-size:13px;">
          + ${escapeHtml(t("add_extra_thermostat"))}
        </button>
      </div>

      <div class="field full">
        <label>${escapeHtml(t("room_switch_actuators"))}</label>
        <div class="room-switch-actuators-list"></div>
        <button type="button" class="ghost room-add-switch-actuator-btn" style="width:100%; margin-top:6px; font-size:13px;">
          + ${escapeHtml(t("add_switch_actuator"))}
        </button>
        <div style="font-size:12px; color:var(--muted); margin-top:4px;">${escapeHtml(t("room_switch_actuators_hint"))}</div>
      </div>

      <div class="field">
        <label style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <span>${escapeHtml(t("room_sensor"))}</span>
          <span class="label-live room-sensor-live"></span>
        </label>
        <div class="room-sensor-picker"></div>
      </div>

      <div class="field full">
        <label>${escapeHtml(t("room_window_sensor"))}</label>
        <div class="room-window-sensors-list"></div>
        <button type="button" class="ghost room-add-window-sensor-btn" style="width:100%; margin-top:6px; font-size:13px;">
          + ${escapeHtml(t("add_window_sensor"))}
        </button>
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_target_day"))}</label>
        <input class="room-target-day" type="number" min="5" max="30" step="0.5" value="${escapeHtml(
          room.target_day
        )}" />
      </div>

      <div class="field room-night-target-wrap"${room.night_setback_enabled === false ? ' style="opacity:0.5;pointer-events:none;"' : ""}>
        <label style="display:flex;align-items:center;gap:8px;">
          ${escapeHtml(t("room_target_night"))}
          <label style="display:flex;align-items:center;gap:4px;font-size:12px;font-weight:normal;white-space:nowrap;">
            <input type="checkbox" class="room-night-setback-enabled" ${room.night_setback_enabled !== false ? "checked" : ""} style="pointer-events:auto;">
            ${escapeHtml(t("room_night_setback_enabled"))}
          </label>
        </label>
        <input class="room-target-night" type="number" min="5" max="30" step="0.5" value="${escapeHtml(
          room.target_night
        )}" />
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_thermostat_offset"))}</label>
        <input class="room-thermostat-offset" type="number" min="-5" max="5" step="0.5" value="${escapeHtml(
          String(room.thermostat_offset ?? 0)
        )}" />
      </div>
    </div>

    <div class="room-climate-section" style="margin-top:12px; padding:10px; background:var(--card-bg,rgba(255,255,255,0.04)); border-radius:8px; border:1px solid var(--border,rgba(255,255,255,0.08));">
      <div style="font-size:13px; font-weight:600; color:var(--muted); margin-bottom:8px;">🌡️ ${escapeHtml(t("room_climate_entity"))}</div>
      <div class="room-grid" style="margin:0;">
        <div class="field full">
          <label>${escapeHtml(t("room_climate_entity"))}</label>
          <div class="room-climate-entity-picker"></div>
        </div>
      </div>
      <div class="room-use-climate-toggle" style="margin-top:8px; display:none;">
        <div class="toggle">
          <div class="toggle-text">
            <strong>${escapeHtml(t("room_use_climate"))}</strong>
            <span>${escapeHtml(t("room_use_climate_hint"))}</span>
          </div>
          <div class="toggle-right">
            <input class="room-use-climate" type="checkbox" ${room.use_climate ? "checked" : ""} />
          </div>
        </div>
        <div class="toggle" style="margin-top:6px;">
          <div class="toggle-text">
            <strong>${escapeHtml(t("room_climate_heat_boost"))}</strong>
            <span>${escapeHtml(t("room_climate_heat_boost_hint"))}</span>
          </div>
          <div class="toggle-right">
            <input class="room-climate-heat-boost" type="checkbox" ${room.climate_heat_boost ? "checked" : ""} />
          </div>
        </div>
      </div>
      <div class="room-cooling-settings" style="margin-top:8px; display:none;">
        <div style="font-size:12px; font-weight:600; color:var(--muted); margin-bottom:6px;">❄️ ${escapeHtml(t("section_room_cooling"))}</div>
        <div class="room-grid" style="margin:0;">
          <div class="field">
            <label>${escapeHtml(t("room_cool_target_day"))}</label>
            <input class="room-cool-target-day" type="number" min="15" max="30" step="0.5" value="${escapeHtml(String(room.cool_target_day ?? 23.0))}" />
          </div>
          <div class="field">
            <label>${escapeHtml(t("room_cool_target_night"))}</label>
            <input class="room-cool-target-night" type="number" min="15" max="30" step="0.5" value="${escapeHtml(String(room.cool_target_night ?? 24.0))}" />
          </div>
          <div class="field">
            <label>${escapeHtml(t("room_climate_fan_mode"))}</label>
            <select class="room-climate-fan-mode">
              <option value="auto" ${(room.climate_fan_mode || "auto") === "auto" ? "selected" : ""}>${escapeHtml(t("climate_fan_auto"))}</option>
              <option value="low" ${room.climate_fan_mode === "low" ? "selected" : ""}>${escapeHtml(t("climate_fan_low"))}</option>
              <option value="medium" ${room.climate_fan_mode === "medium" ? "selected" : ""}>${escapeHtml(t("climate_fan_medium"))}</option>
              <option value="high" ${room.climate_fan_mode === "high" ? "selected" : ""}>${escapeHtml(t("climate_fan_high"))}</option>
            </select>
          </div>
          <div class="field">
            <label>${escapeHtml(t("room_climate_preset"))}</label>
            <select class="room-climate-preset">
              <option value="" ${!room.climate_preset ? "selected" : ""}>${escapeHtml(t("climate_preset_none"))}</option>
              <option value="eco" ${room.climate_preset === "eco" ? "selected" : ""}>${escapeHtml(t("climate_preset_eco"))}</option>
              <option value="comfort" ${room.climate_preset === "comfort" ? "selected" : ""}>${escapeHtml(t("climate_preset_comfort"))}</option>
              <option value="boost" ${room.climate_preset === "boost" ? "selected" : ""}>${escapeHtml(t("climate_preset_boost"))}</option>
              <option value="sleep" ${room.climate_preset === "sleep" ? "selected" : ""}>${escapeHtml(t("climate_preset_sleep"))}</option>
            </select>
          </div>
          <div class="field">
            <label>${escapeHtml(t("room_climate_hvac_mode"))}</label>
            <select class="room-climate-hvac-mode">
              <option value="cool" ${(room.climate_hvac_mode || "cool") === "cool" ? "selected" : ""}>${escapeHtml(t("climate_hvac_cool"))}</option>
              <option value="fan_only" ${room.climate_hvac_mode === "fan_only" ? "selected" : ""}>${escapeHtml(t("climate_hvac_fan_only"))}</option>
              <option value="dry" ${room.climate_hvac_mode === "dry" ? "selected" : ""}>${escapeHtml(t("climate_hvac_dry"))}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <button type="button" class="ghost room-advanced-toggle" style="width:100%; margin-top:10px; font-size:12px; color:var(--muted); padding:8px;">
      <span class="room-advanced-toggle-label">${escapeHtml(t("room_advanced_show"))}</span>
      <span class="room-advanced-chevron" style="margin-left:6px; display:inline-block; transition:transform 0.2s;">▾</span>
    </button>

    <div class="room-advanced hidden">
      <div class="room-grid" style="margin-top:12px;">
        <div class="field">
          <label>${escapeHtml(t("room_area_id"))}</label>
          <input class="room-area-id" type="text" value="${escapeHtml(
            room.area_id || ""
          )}" />
        </div>

        <div class="field">
          <label>${escapeHtml(t("room_control_profile"))}</label>
          <select class="room-control-profile">
            <option value="standard" ${
              room.control_profile === "standard" ? "selected" : ""
            }>${escapeHtml(t("control_profile_standard"))}</option>
            <option value="self_regulating" ${
              room.control_profile === "self_regulating" ? "selected" : ""
            }>${escapeHtml(t("control_profile_self_regulating"))}</option>
          </select>
        </div>

        <div class="field">
          <label style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span>${escapeHtml(t("room_away_temperature"))}</span>
            <label style="display:flex;align-items:center;gap:4px;font-size:12px;font-weight:normal;white-space:nowrap;">
              <input type="checkbox" class="room-away-enabled" ${room.room_away_enabled ? "checked" : ""} />
              ${escapeHtml(t("room_away_mode_enabled"))}
            </label>
          </label>
          <input class="room-away-temperature" type="number" min="5" max="30" step="0.5" value="${escapeHtml(
            room.away_temperature
          )}" />
        </div>

        <div class="field">
          <label style="display:flex;align-items:flex-start;gap:8px;font-weight:normal;">
            <input type="checkbox" class="room-target-reconcile-enabled" ${room.room_target_reconcile_enabled ? "checked" : ""} />
            <span>${escapeHtml(t("room_target_reconcile_enabled"))}</span>
          </label>
        </div>

        <div class="field">
          <label>${escapeHtml(t("room_day_start"))}</label>
          <input class="room-day-start" type="time" value="${escapeHtml(
            room.day_start || ""
          )}" />
        </div>

        <div class="field room-night-start-wrap"${room.night_setback_enabled === false ? ' style="opacity:0.5;pointer-events:none;"' : ""}>
          <label>${escapeHtml(t("room_night_start"))}</label>
          <input class="room-night-start" type="time" value="${escapeHtml(
            room.night_start || ""
          )}" />
        </div>

        ${Object.keys(state.config.circuits || {}).length > 0 ? `
        <div class="field">
          <label>${escapeHtml(t("room_circuit"))}</label>
          <select class="room-circuit-id">
            ${getCircuitOptions().map((opt) => `
              <option value="${escapeHtml(opt.value)}" ${
                (room.circuit_id || "") === opt.value ? "selected" : ""
              }>${escapeHtml(opt.label)}</option>
            `).join("")}
          </select>
        </div>` : ""}

        <div class="field">
          <label>${escapeHtml(t("room_hysteresis"))}</label>
          <input class="room-hysteresis" type="number" min="0.1" max="5" step="0.1" value="${escapeHtml(
            room.hysteresis ?? ""
          )}" />
        </div>

        <div class="field">
          <label>${escapeHtml(t("room_switch_min_on"))}</label>
          <input class="room-switch-min-on" type="number" min="0" max="120" step="1" value="${escapeHtml(
            String(room.switch_min_on ?? 5)
          )}" />
        </div>

        <div class="field">
          <label>${escapeHtml(t("room_switch_min_off"))}</label>
          <input class="room-switch-min-off" type="number" min="0" max="120" step="1" value="${escapeHtml(
            String(room.switch_min_off ?? 5)
          )}" />
        </div>
      </div>
    </div>
  `;

  const scheduleBtn = wrapper.querySelector(".room-schedule-btn");

  createEntityPicker({
    container: wrapper.querySelector(".room-thermostat-picker"),
    pickerId: `room_${roomId}_thermostat_picker`,
    items: state.climates,
    getItems: () => state.climates,
    selectedValue: room.thermostat || "",
    emptyLabel: t("select_not_set"),
    onChange: () => {},
  });

  createEntityPicker({
    container: wrapper.querySelector(".room-sensor-picker"),
    pickerId: `room_${roomId}_sensor_picker`,
    items: state.sensors,
    getItems: () => state.sensors,
    selectedValue: room.sensor || "",
    emptyLabel: t("select_not_set"),
    onChange: () => {},
  });

  const climatePickerContainer = wrapper.querySelector(".room-climate-entity-picker");
  const useClimateToggleWrap = wrapper.querySelector(".room-use-climate-toggle");
  const coolingSettingsWrap = wrapper.querySelector(".room-cooling-settings");

  function updateClimateVisibility() {
    const hasClimate = !!getEntityPickerValue(`room_${roomId}_climate_picker`);
    useClimateToggleWrap.style.display = hasClimate ? "" : "none";
    coolingSettingsWrap.style.display = hasClimate ? "" : "none";
  }

  createEntityPicker({
    container: climatePickerContainer,
    pickerId: `room_${roomId}_climate_picker`,
    items: state.climates,
    getItems: () => state.climates,
    selectedValue: room.climate_entity || "",
    emptyLabel: t("select_not_set"),
    onChange: () => { updateClimateVisibility(); },
  });

  updateClimateVisibility();

  const windowSensorsList = wrapper.querySelector(".room-window-sensors-list");
  const initialSensors = Array.isArray(room.window_sensors) && room.window_sensors.length
    ? room.window_sensors
    : (room.window_sensor ? [room.window_sensor] : [""]);

  for (const sensorId of initialSensors) {
    appendWindowSensorRow(windowSensorsList, roomId, sensorId);
  }

  wrapper.querySelector(".room-add-window-sensor-btn").addEventListener("click", () => {
    appendWindowSensorRow(windowSensorsList, roomId, "");
  });

  const extraThermostatsList = wrapper.querySelector(".room-extra-thermostats-list");
  const initialExtraThermostats = Array.isArray(room.extra_thermostats)
    ? room.extra_thermostats
    : [];

  for (const thermostatId of initialExtraThermostats) {
    appendExtraThermostatRow(extraThermostatsList, roomId, thermostatId);
  }

  wrapper.querySelector(".room-add-thermostat-btn").addEventListener("click", () => {
    appendExtraThermostatRow(extraThermostatsList, roomId, "");
  });

  const switchActuatorsList = wrapper.querySelector(".room-switch-actuators-list");
  const initialSwitchActuators = Array.isArray(room.switch_actuators)
    ? room.switch_actuators
    : [];

  for (const switchId of initialSwitchActuators) {
    appendSwitchActuatorRow(switchActuatorsList, roomId, switchId);
  }

  wrapper.querySelector(".room-add-switch-actuator-btn").addEventListener("click", () => {
    appendSwitchActuatorRow(switchActuatorsList, roomId, "");
  });

  const advancedToggle = wrapper.querySelector(".room-advanced-toggle");
  const advancedPanel = wrapper.querySelector(".room-advanced");
  advancedToggle.addEventListener("click", () => {
    const isOpen = !advancedPanel.classList.contains("hidden");
    advancedPanel.classList.toggle("hidden", isOpen);
    advancedToggle.querySelector(".room-advanced-chevron").style.transform = isOpen ? "" : "rotate(180deg)";
    advancedToggle.querySelector(".room-advanced-toggle-label").textContent = isOpen
      ? t("room_advanced_show")
      : t("room_advanced_hide");
  });

  const nightSetbackCheckbox = wrapper.querySelector(".room-night-setback-enabled");
  const nightTargetWrap = wrapper.querySelector(".room-night-target-wrap");
  const nightStartWrap = wrapper.querySelector(".room-night-start-wrap");
  function updateNightSetbackVisibility() {
    const enabled = nightSetbackCheckbox.checked;
    if (nightTargetWrap) {
      nightTargetWrap.style.opacity = enabled ? "" : "0.5";
      nightTargetWrap.style.pointerEvents = enabled ? "" : "none";
      nightSetbackCheckbox.style.pointerEvents = "auto";
    }
    if (nightStartWrap) {
      nightStartWrap.style.opacity = enabled ? "" : "0.5";
      nightStartWrap.style.pointerEvents = enabled ? "" : "none";
    }
  }
  nightSetbackCheckbox.addEventListener("change", updateNightSetbackVisibility);

  scheduleBtn.addEventListener("click", () => {
    openScheduleModal(roomId);
  });

  return wrapper;
}

// Räume in Anzeigereihenfolge, bei Heizkreisen nach Kreis gruppiert.
function getRoomGroups() {
  const entries = Object.entries(state.config.rooms || {});
  entries.sort((a, b) => (a[1].order ?? 0) - (b[1].order ?? 0));

  const circuits = state.config.circuits || {};
  if (!Object.keys(circuits).length) {
    return [{ label: null, rooms: entries }];
  }

  const byCircuit = {};
  for (const entry of entries) {
    const circuitId = circuits[entry[1].circuit_id] ? entry[1].circuit_id : "";
    (byCircuit[circuitId] ||= []).push(entry);
  }

  const groups = Object.keys(circuits)
    .filter((circuitId) => byCircuit[circuitId])
    .map((circuitId) => ({
      label: circuits[circuitId]?.label || circuitId,
      rooms: byCircuit[circuitId],
    }));

  if (byCircuit[""]) {
    groups.push({ label: t("circuit_none"), rooms: byCircuit[""] });
  }
  return groups;
}

function renderRooms() {
  if (!els.roomsContainer) return;
  els.roomsContainer.innerHTML = "";

  for (const group of getRoomGroups()) {
    for (const [roomId, room] of group.rooms) {
      els.roomsContainer.appendChild(createRoomCard(roomId, room));
    }
  }

  applyActiveEditPane();
  renderTiles();
}

function formatTileNumber(value) {
  return Number(value).toLocaleString(UI_LANG, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
}

function formatTileTemperature(value) {
  return `${formatTileNumber(value)} °C`;
}

function getRoomTileInfo(roomId, room) {
  const live = state.roomStatus?.[roomId] || {};
  const tempSrc = room.sensor || room.thermostat;
  const actual = tempSrc ? getSensorTemperature(tempSrc) : null;
  const target = Number.isFinite(live.target) ? live.target : Number(room.target_day);

  let note = "";
  if (!live.cooling) {
    if (state.config.vacation_enabled) note = t("note_vacation");
    else if (live.away_active) note = t("note_away");
    else if (live.outdoor_minimum_active) note = t("note_minimum");
  }

  const status = (cls, icon, label) => ({ cls, icon, label, actual, target, note });

  if (!room.enabled) return status("off", "", t("status_disabled"));
  if (state.config.enabled === false) return status("off", "", t("status_control_off"));
  if (live.reason === "sensor_fault") return status("fault", "⚠️", t("status_sensor_fault"));
  if (live.reason === "window_pause") return status("pause", "🪟", t("status_window_pause"));

  if (live.cooling) {
    const action = findState(room.climate_entity)?.attributes?.hvac_action;
    const cooling = action ? action === "cooling" : actual !== null && actual > target;
    return cooling ? status("cooling", "❄️", t("status_cooling")) : status("idle", "", t("status_idle"));
  }

  // Ohne Raumsensor regelt das Gerät selbst, der Raumzustand bleibt dann idle.
  const heatedByAc = Boolean(room.climate_entity && room.use_climate);
  const deviceHeating =
    !room.sensor && isThermostatHeating(heatedByAc ? room.climate_entity : room.thermostat);
  if (live.state === "heating" || deviceHeating) {
    return status("heating", "🔥", t(heatedByAc ? "status_heating_ac" : "status_heating"));
  }

  if (live.state === "residual_hold") return status("idle", "", t("status_residual"));
  if (isAnyWindowOpen(room)) return status("pause", "🪟", t("status_window_open"));
  if (live.reason === "outdoor_cutoff") return status("pause", "", t("status_cutoff"));
  return status("idle", "", t("status_idle"));
}

function roomTileGauge(actual, target) {
  // Skala 14–28 °C: Punkt = Ist-Temperatur, Strich = Zieltemperatur
  const position = (value) => Math.min(100, Math.max(0, ((value - 14) / 14) * 100));
  const goal = Number.isFinite(target)
    ? `<i class="goal" style="left:${position(target)}%"></i>`
    : "";
  const now = actual !== null ? `<i class="now" style="left:${position(actual)}%"></i>` : "";
  return `<div class="tile-gauge" aria-hidden="true">${goal}${now}</div>`;
}

function roomTileHtml(room, info) {
  const temp = info.actual !== null ? formatTileNumber(info.actual) : "–";
  const target = Number.isFinite(info.target) ? formatTileTemperature(info.target) : "–";
  const note = info.note ? ` · ${escapeHtml(info.note)}` : "";
  const icon = info.icon ? `<span aria-hidden="true">${info.icon}</span>` : "";
  return `
    <div class="tile-name">${escapeHtml(room.label)}</div>
    <div class="tile-reading">
      <div class="tile-temp">${temp}<small>°C</small></div>
      <div class="tile-target">${escapeHtml(t("tile_target"))} ${target}${note}</div>
    </div>
    <div class="tile-foot">
      ${roomTileGauge(info.actual, info.target)}
      <span class="tile-pill">${icon}${escapeHtml(info.label)}</span>
    </div>
  `;
}

function globalTileHtml() {
  const cfg = state.config;
  const liveList = Object.values(state.roomStatus || {});
  const activeRooms = Object.entries(cfg.rooms || {}).filter(([, room]) => room.enabled);
  const countIn = (cls) =>
    activeRooms.filter(([roomId, room]) => getRoomTileInfo(roomId, room).cls === cls).length;

  const coolingActive = liveList.some((live) => live.cooling_active);
  let operation = t("op_normal");
  if (cfg.vacation_enabled) operation = t("op_vacation");
  else if (cfg.away_enabled) operation = t("op_away");
  else if (coolingActive) operation = t("op_cooling");
  else if (liveList.some((live) => live.outdoor_cutoff_active)) operation = t("op_cutoff");

  const outdoor = cfg.outdoor_sensor ? getSensorTemperature(cfg.outdoor_sensor) : null;
  const outdoorRow =
    outdoor !== null
      ? `<dt>${escapeHtml(t("tile_outdoor"))}</dt><dd>${formatTileTemperature(outdoor)}</dd>`
      : "";

  const running = t(coolingActive ? "tile_running_cool" : "tile_running_heat")
    .replace("{count}", countIn(coolingActive ? "cooling" : "heating"))
    .replace("{total}", activeRooms.length);

  return `
    <div class="tile-name">${escapeHtml(t("global_settings"))}</div>
    <dl class="tile-kv">
      <dt>${escapeHtml(t("tile_control"))}</dt>
      <dd>${escapeHtml(t(cfg.enabled ? "tile_control_on" : "tile_control_off"))}</dd>
      <dt>${escapeHtml(t("tile_operation"))}</dt><dd>${escapeHtml(operation)}</dd>
      ${outdoorRow}
      <dt>${escapeHtml(t("tile_heating_mode"))}</dt>
      <dd>${escapeHtml(t(`mode_${cfg.heating_mode}`))}</dd>
    </dl>
    <div class="tile-foot"><span class="tile-pill">${escapeHtml(running)}</span></div>
  `;
}

function setTileContent(tile, className, ariaLabel, html) {
  // Nur bei Änderung schreiben: Live-Updates kommen bei jedem HA-Ereignis.
  if (tile.dataset.className !== className) {
    tile.className = className;
    tile.dataset.className = className;
  }
  if (tile.getAttribute("aria-label") !== ariaLabel) {
    tile.setAttribute("aria-label", ariaLabel);
  }
  if (tile.tileHtml !== html) {
    tile.innerHTML = html;
    tile.tileHtml = html;
  }
}

function updateTile(tile) {
  if (tile.dataset.tile === "global") {
    setTileContent(tile, "tile global", t("global_settings"), globalTileHtml());
    return;
  }
  if (tile.dataset.tile !== "room") {
    return;
  }

  const room = state.config.rooms?.[tile.dataset.roomId];
  if (!room) {
    return;
  }
  const info = getRoomTileInfo(tile.dataset.roomId, room);
  const dragging = tile.classList.contains("dragging") ? " dragging" : "";
  const dragOver = tile.classList.contains("drag-over") ? " drag-over" : "";
  setTileContent(
    tile,
    `tile ${info.cls}${dragging}${dragOver}`,
    `${room.label}: ${info.label}. ${t("tile_open")}`,
    roomTileHtml(room, info)
  );
}

function updateTiles() {
  els.tileWall?.querySelectorAll(".tile").forEach(updateTile);
}

function createTile(kind, roomId = "") {
  const tile = document.createElement("div");
  tile.setAttribute("role", "button");
  tile.tabIndex = 0;
  tile.dataset.tile = kind;

  const open = () => {
    if (kind === "global") openEditModal("global");
    else if (kind === "add") openNewRoomModal();
    else openEditModal("room", roomId);
  };

  tile.addEventListener("click", open);
  tile.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      open();
    }
  });

  if (kind === "add") {
    tile.className = "tile add";
    tile.innerHTML = `<span class="tile-add-icon" aria-hidden="true">+</span>${escapeHtml(t("add_room"))}`;
  } else if (kind === "room") {
    tile.dataset.roomId = roomId;
    bindTileDrag(tile, roomId);
  }

  updateTile(tile);
  return tile;
}

function bindTileDrag(tile, roomId) {
  tile.draggable = true;

  tile.addEventListener("dragstart", (e) => {
    dragSrcRoomId = roomId;
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", roomId);
    tile.classList.add("dragging");
  });

  tile.addEventListener("dragend", () => {
    dragSrcRoomId = null;
    tile.classList.remove("dragging");
    els.tileWall.querySelectorAll(".drag-over").forEach((n) => n.classList.remove("drag-over"));
  });

  tile.addEventListener("dragover", (e) => {
    if (!dragSrcRoomId || dragSrcRoomId === roomId) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    tile.classList.add("drag-over");
  });

  tile.addEventListener("dragleave", () => {
    tile.classList.remove("drag-over");
  });

  tile.addEventListener("drop", (e) => {
    e.preventDefault();
    tile.classList.remove("drag-over");
    const srcRoomId = dragSrcRoomId;
    dragSrcRoomId = null;
    if (srcRoomId && srcRoomId !== roomId) {
      moveRoom(srcRoomId, roomId);
    }
  });
}

function moveRoom(srcRoomId, dstRoomId) {
  const ids = getRoomGroups().flatMap((group) => group.rooms.map(([roomId]) => roomId));
  const srcIdx = ids.indexOf(srcRoomId);
  const dstIdx = ids.indexOf(dstRoomId);
  ids.splice(srcIdx, 1);
  ids.splice(dstIdx, 0, srcRoomId);
  ids.forEach((roomId, index) => {
    state.config.rooms[roomId].order = index;
  });

  renderRooms();
  saveConfig();
}

function renderTiles() {
  if (!els.tileWall) return;
  els.tileWall.innerHTML = "";

  const groups = getRoomGroups();
  const addGrid = (children) => {
    const grid = document.createElement("div");
    grid.className = "tile-grid";
    grid.append(...children);
    els.tileWall.appendChild(grid);
    return grid;
  };

  const firstGrid = addGrid([createTile("global")]);
  let lastGrid = firstGrid;

  for (const group of groups) {
    const tiles = group.rooms.map(([roomId]) => createTile("room", roomId));
    if (group.label === null) {
      firstGrid.append(...tiles);
      continue;
    }
    const header = document.createElement("div");
    header.className = "room-group-header";
    header.textContent = group.label;
    els.tileWall.appendChild(header);
    lastGrid = addGrid(tiles);
  }

  lastGrid.appendChild(createTile("add"));
}

// ─── Edit popup ──────────────────────────────────────────────────────────────
// Global- und Raumformulare bleiben dauerhaft im DOM, weil collectFormState()
// immer alle liest. Das Popup blendet nur das gerade bearbeitete ein.
function applyActiveEditPane() {
  const session = editSession;
  els.globalForm?.classList.toggle("active", session?.kind === "global");
  els.roomsContainer?.querySelectorAll(".room").forEach((node) => {
    node.classList.toggle("active", session?.kind === "room" && node.dataset.roomId === session.roomId);
  });
}

function updateEditHeader() {
  if (!editSession) return;

  if (editSession.kind === "global") {
    els.editModalTitle.textContent = t("global_settings");
    els.editModalLive.textContent = "";
    return;
  }

  const room = state.config.rooms?.[editSession.roomId];
  if (!room) return;

  const labelInput = els.roomsContainer.querySelector(
    `.room[data-room-id="${CSS.escape(editSession.roomId)}"] .room-label`
  );
  els.editModalTitle.textContent = labelInput?.value.trim() || room.label;

  const info = getRoomTileInfo(editSession.roomId, room);
  const actual =
    info.actual !== null
      ? `${t("tile_now")} ${formatTileTemperature(info.actual)}`
      : t("tile_no_reading");
  const target = Number.isFinite(info.target)
    ? ` · ${t("tile_target")} ${formatTileTemperature(info.target)}`
    : "";
  els.editModalLive.textContent = editSession.isNew ? "" : `${actual}${target} · ${info.label}`;
}

function setEditConfirm(mode) {
  editSession.confirm = mode;
  const hasConfirm = mode !== null;

  els.saveBtn.classList.toggle("hidden", hasConfirm);
  els.editConfirm.classList.toggle("hidden", !hasConfirm);
  els.editDelete.classList.toggle(
    "hidden",
    hasConfirm || editSession.kind !== "room" || editSession.isNew
  );

  if (mode === "discard") {
    els.editQuestion.textContent = t("edit_discard_question");
    els.editConfirm.textContent = t("edit_discard_confirm");
    els.editCancel.textContent = t("edit_keep_editing");
  } else if (mode === "delete") {
    const name = state.config.rooms?.[editSession.roomId]?.label || "";
    els.editQuestion.textContent = t("edit_delete_question").replace("{name}", name);
    els.editConfirm.textContent = t("edit_delete");
    els.editCancel.textContent = t("edit_delete_keep");
  } else {
    els.editQuestion.textContent = "";
    els.editCancel.textContent = t("edit_cancel");
  }
}

function openEditModal(kind, roomId = null, { isNew = false, snapshot = null } = {}) {
  editSession = {
    kind,
    roomId,
    isNew,
    snapshot: snapshot || structuredClone(state.config),
    baseline: JSON.stringify(collectFormState()),
    confirm: null,
  };

  applyActiveEditPane();
  setEditConfirm(null);
  updateEditHeader();
  els.editStatus.className = "status edit-status hidden";
  els.editModal.classList.remove("hidden");
  els.mainWrap.inert = true;
  els.editModalBody.scrollTop = 0;

  if (isNew) {
    const labelInput = els.roomsContainer.querySelector(
      `.room[data-room-id="${CSS.escape(roomId)}"] .room-label`
    );
    labelInput?.focus();
    labelInput?.select();
  } else {
    els.editModalContent.focus();
  }
}

function openNewRoomModal() {
  const snapshot = structuredClone(state.config);
  const roomId = addRoom();
  openEditModal("room", roomId, { isNew: true, snapshot });
}

function closeEditModal() {
  const session = editSession;
  editSession = null;
  isEditing = false;

  els.editModal.classList.add("hidden");
  els.mainWrap.inert = false;
  applyActiveEditPane();
  updateRoomLiveState();

  const selector =
    session?.kind === "room"
      ? `.tile[data-room-id="${CSS.escape(session.roomId)}"]`
      : '.tile[data-tile="global"]';
  (els.tileWall.querySelector(selector) || els.tileWall.querySelector(".tile"))?.focus();
}

function restoreEditSnapshot() {
  state.config = editSession.snapshot;
  pendingCircuits = null;
  entityPickerState.clear();
  renderGlobalSettings();
  renderRooms();
}

function discardEdit() {
  restoreEditSnapshot();
  closeEditModal();
}

function requestCloseEdit() {
  if (!editSession) return;
  if (JSON.stringify(collectFormState()) === editSession.baseline) {
    discardEdit();
  } else {
    setEditConfirm("discard");
  }
}

async function saveEdit() {
  if (await saveConfig()) {
    closeEditModal();
  }
}

async function deleteEditedRoom() {
  const { roomId } = editSession;
  delete state.config.rooms[roomId];
  renderRooms();

  if (await saveConfig()) {
    closeEditModal();
    return;
  }
  restoreEditSnapshot();
  setEditConfirm(null);
}

function bindEditModalEvents() {
  els.saveBtn.addEventListener("click", saveEdit);
  els.editModalClose.setAttribute("aria-label", t("edit_close"));
  els.editModalClose.addEventListener("click", requestCloseEdit);
  els.editDelete.addEventListener("click", () => setEditConfirm("delete"));

  els.editCancel.addEventListener("click", () => {
    if (editSession?.confirm) setEditConfirm(null);
    else requestCloseEdit();
  });

  els.editConfirm.addEventListener("click", () => {
    if (editSession?.confirm === "discard") discardEdit();
    else if (editSession?.confirm === "delete") deleteEditedRoom();
  });

  els.editModal.addEventListener("mousedown", (e) => {
    if (e.target === els.editModal) requestCloseEdit();
  });

  els.editModalBody.addEventListener("input", (e) => {
    if (e.target.classList.contains("room-label")) updateEditHeader();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || !editSession) return;
    // Darüber liegende Dialoge (Wochenplan, Entity-Auswahl, Hilfe) gehen vor.
    const otherModalOpen = [...document.querySelectorAll(".modal:not(.hidden)")].some(
      (modal) => modal !== els.editModal
    );
    if (otherModalOpen) return;
    if (editSession.confirm) setEditConfirm(null);
    else requestCloseEdit();
  });
}

function updateRoomLiveState() {
  const roomNodes = els.roomsContainer.querySelectorAll(".room");

  for (const node of roomNodes) {
    const roomId = node.dataset.roomId;
    const room = state.config.rooms?.[roomId];

    if (!room) {
      continue;
    }

    // live thermostat label: setpoint + heating indicator
    const thermostatLive = node.querySelector(".room-thermostat-live");
    if (thermostatLive) {
      const setpoint = getThermostatSetpoint(room.thermostat);
      const heating = isRoomHeating(roomId);
      if (setpoint !== null) {
        thermostatLive.innerHTML = `${heating ? "🔥 " : ""}${escapeHtml(formatTemperature(setpoint))}`;
        thermostatLive.dataset.entity = room.thermostat;
      } else {
        thermostatLive.textContent = "";
        delete thermostatLive.dataset.entity;
      }
    }

    // live sensor label: current measured temperature
    const sensorLive = node.querySelector(".room-sensor-live");
    if (sensorLive) {
      const tempSrc = room.sensor || room.thermostat;
      const temp = getSensorTemperature(tempSrc);
      if (temp !== null) {
        sensorLive.textContent = formatTemperature(temp);
        sensorLive.dataset.entity = tempSrc;
      } else {
        sensorLive.textContent = "";
        delete sensorLive.dataset.entity;
      }
    }

    // update adaptive bucket display
    const adaptiveDiv = node.querySelector(".room-adaptive-display");
    if (adaptiveDiv) {
      const ovShort = normalizeNumber(room.learned_overshoot_short, 0.2);
      const ovMedium = normalizeNumber(room.learned_overshoot_medium, 0.4);
      const ovLong = normalizeNumber(room.learned_overshoot_long, 0.7);
      const buckets = adaptiveDiv.querySelectorAll(".adaptive-bucket-value");
      if (buckets.length === 3) {
        buckets[0].textContent = `${ovShort.toFixed(2)} °C`;
        buckets[1].textContent = `${ovMedium.toFixed(2)} °C`;
        buckets[2].textContent = `${ovLong.toFixed(2)} °C`;
      }
    }
  }

  updateMainLiveStatus();
  updateTiles();
  updateEditHeader();
}

function collectFormState() {
  const cfg = structuredClone(state.config);

  cfg.enabled = els.enabled.checked;
  cfg.main_control_type = els.mainControlType?.value || "thermostat";
  cfg.main_thermostat = getEntityPickerValue("global_main_thermostat_picker");
  cfg.main_switch = getEntityPickerValue("global_main_switch_picker");
  cfg.main_sensor = getEntityPickerValue("global_main_sensor_picker");
  cfg.boost_delta = normalizeNumber(els.boostDelta.value, DEFAULTS.boost_delta);
  cfg.tolerance = normalizeNumber(els.tolerance.value, DEFAULTS.tolerance);
  cfg.heating_mode = normalizeHeatingMode(getModePickerValue());
  cfg.energy_residual_heat_hold = els.energyResidualHeatHold
    ? normalizeNumber(
        els.energyResidualHeatHold.value,
        DEFAULTS.energy_residual_heat_hold
      )
    : DEFAULTS.energy_residual_heat_hold;
  cfg.night_start = normalizeTime(els.nightStart.value, DEFAULTS.night_start);
  cfg.morning_boost_start = normalizeTime(
    els.morningBoostStart.value,
    DEFAULTS.morning_boost_start
  );
  cfg.morning_boost_end = normalizeTime(
    els.morningBoostEnd.value,
    DEFAULTS.morning_boost_end
  );
  cfg.vacation_enabled = els.vacationEnabled
    ? els.vacationEnabled.checked
    : false;
  cfg.vacation_temperature = els.vacationTemperature
    ? normalizeNumber(
        els.vacationTemperature.value,
        DEFAULTS.vacation_temperature
      )
    : DEFAULTS.vacation_temperature;
  cfg.away_enabled = els.awayEnabled ? els.awayEnabled.checked : false;

  cfg.outdoor_sensor = getEntityPickerValue("global_outdoor_sensor_picker");
  cfg.outdoor_temp_cutoff_enabled = els.outdoorTempCutoffEnabled
    ? els.outdoorTempCutoffEnabled.checked
    : false;
  cfg.outdoor_temp_cutoff = els.outdoorTempCutoff
    ? normalizeNumber(els.outdoorTempCutoff.value, DEFAULTS.outdoor_temp_cutoff)
    : DEFAULTS.outdoor_temp_cutoff;
  cfg.outdoor_cutoff_hysteresis = els.outdoorCutoffHysteresis
    ? Math.max(0, normalizeNumber(els.outdoorCutoffHysteresis.value, DEFAULTS.outdoor_cutoff_hysteresis))
    : DEFAULTS.outdoor_cutoff_hysteresis;
  cfg.outdoor_min_room_temperature = els.outdoorMinRoomTemperature
    ? Math.max(0, normalizeNumber(els.outdoorMinRoomTemperature.value, DEFAULTS.outdoor_min_room_temperature))
    : DEFAULTS.outdoor_min_room_temperature;

  cfg.global_target_day = els.globalTargetDay
    ? normalizeNumber(els.globalTargetDay.value, DEFAULTS.global_target_day)
    : DEFAULTS.global_target_day;
  cfg.global_target_night = els.globalTargetNight
    ? normalizeNumber(els.globalTargetNight.value, DEFAULTS.global_target_night)
    : DEFAULTS.global_target_night;
  cfg.global_away_temperature = els.globalAwayTemperature
    ? normalizeNumber(els.globalAwayTemperature.value, DEFAULTS.global_away_temperature)
    : DEFAULTS.global_away_temperature;
  cfg.cooling_enabled = els.coolingEnabled ? els.coolingEnabled.checked : false;
  cfg.cooling_auto = els.coolingAuto ? els.coolingAuto.checked : false;
  cfg.cooling_threshold = els.coolingThreshold
    ? normalizeNumber(els.coolingThreshold.value, DEFAULTS.cooling_threshold)
    : DEFAULTS.cooling_threshold;

  const rooms = {};
  const roomNodes = els.roomsContainer.querySelectorAll(".room");

  for (let i = 0; i < roomNodes.length; i++) {
    const node = roomNodes[i];
    const roomId = node.dataset.roomId;
    const existingRoom = state.config.rooms[roomId] || {};

    rooms[roomId] = normalizeRoom(roomId, {
      label: node.querySelector(".room-label").value.trim() || roomId,
      area_id: node.querySelector(".room-area-id").value.trim(),
      thermostat: getEntityPickerValue(`room_${roomId}_thermostat_picker`) || "",
      extra_thermostats: [...node.querySelectorAll(".room-extra-thermostat-row")].map(
        (row) => getEntityPickerValue(row.dataset.thermostatPickerId)
      ).filter(Boolean),
      switch_actuators: [...node.querySelectorAll(".room-switch-actuator-row")].map(
        (row) => getEntityPickerValue(row.dataset.switchPickerId)
      ).filter(Boolean),
      hysteresis: node.querySelector(".room-hysteresis")?.value ?? "",
      switch_min_on: node.querySelector(".room-switch-min-on")?.value || undefined,
      switch_min_off: node.querySelector(".room-switch-min-off")?.value || undefined,
      sensor: getEntityPickerValue(`room_${roomId}_sensor_picker`) || "",
      window_sensors: [...node.querySelectorAll(".room-window-sensor-row")].map(
        (row) => getEntityPickerValue(row.dataset.wsPickerId)
      ).filter(Boolean),
      control_profile:
        node.querySelector(".room-control-profile")?.value || "standard",
      thermostat_offset: normalizeNumber(
        node.querySelector(".room-thermostat-offset")?.value,
        0.0
      ),
      target_day: node.querySelector(".room-target-day").value,
      target_night: node.querySelector(".room-target-night").value,
      away_temperature: node.querySelector(".room-away-temperature").value,
      room_away_enabled: node.querySelector(".room-away-enabled")?.checked === true,
      room_target_reconcile_enabled:
        node.querySelector(".room-target-reconcile-enabled")?.checked === true,
      weekly_schedule: existingRoom.weekly_schedule || DEFAULT_WEEKLY_SCHEDULE,
      day_start: node.querySelector(".room-day-start").value || "",
      night_start: node.querySelector(".room-night-start").value || "",
      enabled: node.querySelector(".room-enabled").checked,
      night_setback_enabled: node.querySelector(".room-night-setback-enabled")?.checked !== false,
      learned_overshoot: existingRoom.learned_overshoot,
      circuit_id: node.querySelector(".room-circuit-id")?.value || existingRoom.circuit_id || "",
      order: i,
      room_heating_mode: node.querySelector(".room-heating-mode")?.value || "",
      climate_entity: getEntityPickerValue(`room_${roomId}_climate_picker`) || "",
      use_climate: node.querySelector(".room-use-climate")?.checked === true,
      climate_heat_boost: node.querySelector(".room-climate-heat-boost")?.checked === true,
      cool_target_day: normalizeNumber(node.querySelector(".room-cool-target-day")?.value, 23.0),
      cool_target_night: normalizeNumber(node.querySelector(".room-cool-target-night")?.value, 24.0),
      climate_fan_mode: node.querySelector(".room-climate-fan-mode")?.value || "auto",
      climate_preset: node.querySelector(".room-climate-preset")?.value || "",
      climate_hvac_mode: node.querySelector(".room-climate-hvac-mode")?.value || "cool",
    });
  }

  cfg.rooms = rooms;

  // collect circuits
  const circuits = {};
  const circuitNodes = els.circuitsList
    ? els.circuitsList.querySelectorAll(".circuit-card")
    : [];
  for (const node of circuitNodes) {
    const circuitId = node.dataset.circuitId;
    circuits[circuitId] = normalizeCircuit(circuitId, {
      label: node.querySelector(".circuit-label")?.value?.trim() || "",
      control_type: node.querySelector(".circuit-control-type")?.value || "thermostat",
      main_thermostat:
        getEntityPickerValue(`circuit_${circuitId}_thermostat_picker`) || "",
      main_switch:
        getEntityPickerValue(`circuit_${circuitId}_switch_picker`) || "",
      main_sensor:
        getEntityPickerValue(`circuit_${circuitId}_sensor_picker`) || "",
      enabled: node.querySelector(".circuit-enabled-checkbox")?.checked !== false,
    });
  }
  cfg.circuits = circuits;

  // Live-Status gehört nicht in die gespeicherte Konfiguration.
  delete cfg.room_states;
  delete cfg.room_status;

  return normalizeConfig(cfg);
}

function generateRoomId() {
  return `room_${Math.random().toString(16).slice(2, 10)}`;
}

function addRoom() {
  const roomId = generateRoomId();
  const existingCount = Object.keys(state.config.rooms).length;
  state.config.rooms[roomId] = {
    label: t("room_new"),
    area_id: "",
    thermostat: "",
    extra_thermostats: [],
    switch_actuators: [],
    hysteresis: null,
    switch_min_on: 5,
    switch_min_off: 5,
    sensor: "",
    window_sensor: "",
    window_sensors: [],
    control_profile: "standard",
    thermostat_offset: 0.0,
    circuit_id: "",
    target_day: normalizeNumber(els.globalTargetDay?.value, DEFAULTS.global_target_day),
    target_night: normalizeNumber(els.globalTargetNight?.value, DEFAULTS.global_target_night),
    away_temperature: normalizeNumber(els.globalAwayTemperature?.value, DEFAULTS.global_away_temperature),
    room_away_enabled: false,
    room_target_reconcile_enabled: false,
    weekly_schedule: structuredClone(DEFAULT_WEEKLY_SCHEDULE),
    day_start: "",
    night_start: "",
    enabled: true,
    night_setback_enabled: true,
    learned_overshoot: 0.3,
    order: existingCount,
    room_heating_mode: "",
    climate_entity: "",
    use_climate: false,
    climate_heat_boost: false,
    cool_target_day: DEFAULTS.room_cool_target_day,
    cool_target_night: DEFAULTS.room_cool_target_night,
    climate_fan_mode: DEFAULTS.room_climate_fan_mode,
    climate_preset: DEFAULTS.room_climate_preset,
    climate_hvac_mode: DEFAULTS.room_climate_hvac_mode,
  };
  renderRooms();
  return roomId;
}

function applyGlobalTempsToAllRooms() {
  const globalDay = normalizeNumber(els.globalTargetDay?.value, DEFAULTS.global_target_day);
  const globalNight = normalizeNumber(els.globalTargetNight?.value, DEFAULTS.global_target_night);
  const globalAway = normalizeNumber(els.globalAwayTemperature?.value, DEFAULTS.global_away_temperature);

  const roomNodes = els.roomsContainer.querySelectorAll(".room");
  if (!roomNodes.length) {
    setStatus(t("status_no_rooms_apply"), "warn");
    return;
  }

  for (const node of roomNodes) {
    const dayInput = node.querySelector(".room-target-day");
    const nightInput = node.querySelector(".room-target-night");
    const awayInput = node.querySelector(".room-away-temperature");
    if (dayInput) dayInput.value = String(globalDay);
    if (nightInput) nightInput.value = String(globalNight);
    if (awayInput) awayInput.value = String(globalAway);
  }

  state.config = collectFormState();
  setStatus(t("status_apply_temps_ok"), "ok");
}

function applyGlobalTimesToAllRooms() {
  const globalNight = normalizeTime(els.nightStart.value, DEFAULTS.night_start);
  const globalDay = normalizeTime(
    els.morningBoostStart.value,
    DEFAULTS.morning_boost_start
  );

  const roomNodes = els.roomsContainer.querySelectorAll(".room");
  if (!roomNodes.length) {
    setStatus(t("status_no_rooms_apply"), "warn");
    return;
  }

  for (const node of roomNodes) {
    const dayInput = node.querySelector(".room-day-start");
    const nightInput = node.querySelector(".room-night-start");

    dayInput.value = globalDay;
    nightInput.value = globalNight;
  }

  state.config = collectFormState();
  setStatus(t("status_apply_times_ok"), "ok");
}

async function saveConfig() {
  try {
    isEditing = false;
    isSaving = true;
    pendingCircuits = null;
    setButtonsDisabled(true);
    setStatus(t("status_save_loading"), "warn");

    const cfg = collectFormState();

    await callService(DOMAIN, "update_config", {
      config: cfg,
    });

    state.config = cfg;
    await loadAllStates();
    renderGlobalSettings();
    renderRooms();
    setStatus(t("status_save_ok"), "ok");
    return true;
  } catch (error) {
    console.error(error);
    setStatus(`${t("status_save_failed")}: ${error.message}`, "err");
    return false;
  } finally {
    isSaving = false;
    setButtonsDisabled(false);
  }
}

async function reloadRooms() {
  try {
    setButtonsDisabled(true);
    setStatus(t("status_rooms_reload_loading"), "warn");

    await callService(DOMAIN, "reload", {});
    await refreshAll();

    setStatus(t("status_rooms_reload_ok"), "ok");
  } catch (error) {
    console.error(error);
    setStatus(`${t("status_room_reload_failed")}: ${error.message}`, "err");
  } finally {
    setButtonsDisabled(false);
  }
}

async function reloadConfig() {
  try {
    setButtonsDisabled(true);
    setStatus(t("status_loading"), "warn");

    await refreshAll();
    setStatus(t("status_reload_ok"), "ok");
  } catch (error) {
    console.error(error);
    setStatus(`${t("status_reload_failed")}: ${error.message}`, "err");
  } finally {
    setButtonsDisabled(false);
  }
}

async function refreshAll() {
  await loadAllStates();
  await loadConfig();
  // Picker-State leeren damit explizite Reloads immer frische Backend-Werte zeigen.
  entityPickerState.clear();
  renderGlobalSettings();
  renderRooms();
}

function getDayLabel(day) {
  const map = {
    monday: t("day_monday"),
    tuesday: t("day_tuesday"),
    wednesday: t("day_wednesday"),
    thursday: t("day_thursday"),
    friday: t("day_friday"),
    saturday: t("day_saturday"),
    sunday: t("day_sunday"),
  };
  return map[day] || day;
}

function openScheduleModal(roomId) {
  const room = state.config.rooms?.[roomId];
  if (!room) {
    return;
  }

  scheduleRoomId = roomId;
  draftWeeklySchedule = normalizeWeeklySchedule(room.weekly_schedule);

  if (els.scheduleModalTitle) {
    const label = room.label || roomId;
    els.scheduleModalTitle.textContent = `${t("schedule_title")} · ${label}`;
  }

  els.scheduleModal.classList.remove("hidden");
  renderScheduleCalendar();

  // scroll to 07:00
  requestAnimationFrame(() => {
    const wrap = els.scheduleModal?.querySelector(".schedule-calendar-wrap");
    if (wrap) wrap.scrollTop = calMinToPx(7 * 60) - 36;
  });
}

function closeScheduleModal() {
  scheduleRoomId = null;
  draftWeeklySchedule = null;
  if (els.scheduleCalendar) els.scheduleCalendar.innerHTML = "";
  els.scheduleModal.classList.add("hidden");
  closeScheduleCopyModal();
}

function sortScheduleEntries(entries) {
  entries.sort((a, b) => a.start.localeCompare(b.start));
}

// ── Calendar helpers ────────────────────────────────
const CAL_PX_PER_HOUR = 60;
const CAL_SNAP_MIN = 30;
const CAL_DAYS = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"];

function calMinToPx(min) { return (min / 60) * CAL_PX_PER_HOUR; }
function calPxToMin(px)  { return (px / CAL_PX_PER_HOUR) * 60; }
function calSnapMin(min) { return Math.round(min / CAL_SNAP_MIN) * CAL_SNAP_MIN; }
function calClampMin(min){ return Math.max(0, Math.min(23 * 60 + 30, min)); }
function calMinToHHMM(min) {
  min = Math.max(0, Math.min(1439, min));
  return `${String(Math.floor(min / 60)).padStart(2, "0")}:${String(min % 60).padStart(2, "0")}`;
}
function calHHMMToMin(hhmm) {
  const [h, m] = String(hhmm || "0:0").split(":").map(Number);
  return (h || 0) * 60 + (m || 0);
}

// ── Calendar render ─────────────────────────────────
function renderScheduleCalendar() {
  const cal = els.scheduleCalendar;
  if (!cal) return;
  cal.innerHTML = "";

  const totalH = CAL_PX_PER_HOUR * 24;
  const today = new Date().toLocaleDateString("en-US", { weekday: "long" }).toLowerCase();

  // corner
  const corner = document.createElement("div");
  corner.className = "schedule-cal-corner";
  cal.appendChild(corner);

  // day headers
  for (const day of CAL_DAYS) {
    const hdr = document.createElement("div");
    hdr.className = "schedule-cal-day-hdr" + (day === today ? " today" : "");
    hdr.textContent = getDayLabel(day);
    cal.appendChild(hdr);
  }

  // time gutter
  const timeCol = document.createElement("div");
  timeCol.className = "schedule-cal-time-col";
  timeCol.style.height = `${totalH}px`;
  for (let h = 0; h <= 24; h++) {
    const lbl = document.createElement("div");
    lbl.className = "schedule-cal-hour-lbl";
    lbl.style.top = `${calMinToPx(h * 60)}px`;
    lbl.textContent = `${String(h).padStart(2, "0")}:00`;
    timeCol.appendChild(lbl);
  }
  cal.appendChild(timeCol);

  // day columns
  for (const day of CAL_DAYS) {
    cal.appendChild(buildCalDayCol(day, totalH));
  }
}

function buildCalDayCol(day, totalH) {
  const col = document.createElement("div");
  col.className = "schedule-cal-day-col";
  col.dataset.day = day;
  col.style.height = `${totalH}px`;

  for (let h = 0; h <= 24; h++) {
    const hl = document.createElement("div");
    hl.className = "schedule-cal-hour-line";
    hl.style.top = `${calMinToPx(h * 60)}px`;
    col.appendChild(hl);
    if (h < 24) {
      const hh = document.createElement("div");
      hh.className = "schedule-cal-half-line";
      hh.style.top = `${calMinToPx(h * 60 + 30)}px`;
      col.appendChild(hh);
    }
  }

  renderCalBlocks(day, col);

  col.addEventListener("mousedown", (e) => {
    if (e.button !== 0 || e.target.closest(".schedule-block")) return;
    calCreateDragStart(e, col, day);
  });
  col.addEventListener("touchstart", (e) => {
    if (e.target.closest(".schedule-block")) return;
    e.preventDefault();
    calCreateDragStart(e.touches[0], col, day, true);
  }, { passive: false });

  return col;
}

function renderCalBlocks(day, col) {
  col.querySelectorAll(".schedule-block, .schedule-ghost").forEach(b => b.remove());
  if (!draftWeeklySchedule) return;

  const entries = [...(draftWeeklySchedule[day] || [])].sort((a, b) => a.start.localeCompare(b.start));

  entries.forEach((entry, i) => {
    const startMin = calHHMMToMin(entry.start);
    const endMin   = i < entries.length - 1 ? calHHMMToMin(entries[i + 1].start) : 24 * 60;
    const blockH   = Math.max(calMinToPx(endMin - startMin), 22);

    const block = document.createElement("div");
    block.className = "schedule-block";
    block.style.top    = `${calMinToPx(startMin)}px`;
    block.style.height = `${blockH}px`;

    const inner = document.createElement("div");
    inner.className = "schedule-block-inner";

    const startLbl = document.createElement("div");
    startLbl.className = "schedule-block-start";
    startLbl.textContent = entry.start;
    inner.appendChild(startLbl);

    const tempInput = document.createElement("input");
    tempInput.className = "schedule-block-temp-input";
    tempInput.type  = "number";
    tempInput.min   = "5";
    tempInput.max   = "35";
    tempInput.step  = "0.5";
    tempInput.value = String(entry.temperature);
    tempInput.addEventListener("change", () => { entry.temperature = parseFloat(tempInput.value) || 20; });
    tempInput.addEventListener("click",      (e) => e.stopPropagation());
    tempInput.addEventListener("mousedown",  (e) => e.stopPropagation());
    tempInput.addEventListener("touchstart", (e) => e.stopPropagation());
    inner.appendChild(tempInput);

    const unit = document.createElement("div");
    unit.className = "schedule-block-unit";
    unit.textContent = "°C";
    inner.appendChild(unit);

    block.appendChild(inner);

    const del = document.createElement("button");
    del.className  = "schedule-block-del";
    del.type       = "button";
    del.textContent = "×";
    del.addEventListener("click", (e) => {
      e.stopPropagation();
      const idx = draftWeeklySchedule[day].findIndex(en => en.start === entry.start);
      if (idx >= 0) draftWeeklySchedule[day].splice(idx, 1);
      renderCalBlocks(day, col);
    });
    block.appendChild(del);

    calBlockMoveDrag(block, day, entry, col);
    col.appendChild(block);
  });
}

// ── Drag: create block ──────────────────────────────
function calCreateDragStart(e, col, day) {
  if (!draftWeeklySchedule) return;
  const rect     = col.getBoundingClientRect();
  const startMin = calSnapMin(calClampMin(Math.round(calPxToMin(e.clientY - rect.top))));

  const ghost = document.createElement("div");
  ghost.className   = "schedule-ghost";
  ghost.style.top   = `${calMinToPx(startMin)}px`;
  ghost.style.height = `${calMinToPx(CAL_SNAP_MIN)}px`;
  col.appendChild(ghost);

  let currentEndMin = startMin + CAL_SNAP_MIN;

  const onMove = (ev) => {
    const cy   = ev.touches ? ev.touches[0].clientY : ev.clientY;
    const rect2 = col.getBoundingClientRect();
    currentEndMin = calSnapMin(calClampMin(Math.round(calPxToMin(cy - rect2.top))));
    const top  = calMinToPx(Math.min(startMin, currentEndMin));
    const hpx  = calMinToPx(Math.max(Math.abs(currentEndMin - startMin), CAL_SNAP_MIN));
    ghost.style.top    = `${top}px`;
    ghost.style.height = `${hpx}px`;
    if (ev.cancelable) ev.preventDefault();
  };

  const onUp = (ev) => {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup",   onUp);
    document.removeEventListener("touchmove", onMove);
    document.removeEventListener("touchend",  onUp);
    ghost.remove();

    const cy  = ev.changedTouches ? ev.changedTouches[0].clientY : ev.clientY;
    const r2   = col.getBoundingClientRect();
    const endM = calSnapMin(calClampMin(Math.round(calPxToMin(cy - r2.top))));
    const finalMin = Math.min(startMin, endM);
    const hhmm = calMinToHHMM(finalMin);

    if (!Array.isArray(draftWeeklySchedule[day])) draftWeeklySchedule[day] = [];
    if (draftWeeklySchedule[day].some(en => en.start === hhmm)) return;

    // default temp: active temperature at that time, or 21
    const sorted = [...draftWeeklySchedule[day]].sort((a, b) => a.start.localeCompare(b.start));
    let defTemp = 21.0;
    for (const en of sorted) {
      if (en.start <= hhmm) defTemp = en.temperature;
    }

    draftWeeklySchedule[day].push({ start: hhmm, temperature: defTemp });
    draftWeeklySchedule[day].sort((a, b) => a.start.localeCompare(b.start));
    renderCalBlocks(day, col);
  };

  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup",   onUp);
  document.addEventListener("touchmove", onMove, { passive: false });
  document.addEventListener("touchend",  onUp);
}

// ── Drag: move block ────────────────────────────────
function calBlockMoveDrag(block, fromDay, entry, fromCol) {
  const onDown = (e) => {
    if (e.target.closest(".schedule-block-del") || e.target.tagName === "INPUT") return;
    if (e.button !== undefined && e.button !== 0) return;
    e.preventDefault();
    e.stopPropagation();

    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const rect    = block.getBoundingClientRect();
    const offsetY = clientY - rect.top;

    // floating clone
    const clone       = block.cloneNode(true);
    clone.style.position    = "fixed";
    clone.style.width       = `${rect.width}px`;
    clone.style.left        = `${rect.left}px`;
    clone.style.top         = `${rect.top}px`;
    clone.style.zIndex      = "9999";
    clone.style.opacity     = "0.85";
    clone.style.cursor      = "grabbing";
    clone.style.pointerEvents = "none";
    clone.style.transition  = "none";
    document.body.appendChild(clone);
    block.style.opacity = "0.3";

    let currentDay = fromDay;
    let currentMin = calHHMMToMin(entry.start);

    const onMove = (ev) => {
      const cy = ev.touches ? ev.touches[0].clientY : ev.clientY;
      const cx = ev.touches ? ev.touches[0].clientX : ev.clientX;
      clone.style.top  = `${cy - offsetY}px`;
      clone.style.left = `${cx - rect.width / 2}px`;

      const target    = document.elementFromPoint(cx, cy);
      const targetCol = target?.closest(".schedule-cal-day-col");
      if (targetCol?.dataset.day) {
        currentDay = targetCol.dataset.day;
        const cr   = targetCol.getBoundingClientRect();
        currentMin = calSnapMin(calClampMin(Math.round(calPxToMin(cy - offsetY - cr.top))));
      }
      if (ev.cancelable) ev.preventDefault();
    };

    const onUp = () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup",   onUp);
      document.removeEventListener("touchmove", onMove);
      document.removeEventListener("touchend",  onUp);
      clone.remove();
      block.style.opacity = "";

      const newHHMM = calMinToHHMM(currentMin);

      // remove from original day
      const oldArr = draftWeeklySchedule[fromDay];
      const idx    = oldArr?.findIndex(en => en.start === entry.start);
      if (idx >= 0) oldArr.splice(idx, 1);

      // insert into target day (skip if duplicate start)
      if (!Array.isArray(draftWeeklySchedule[currentDay])) draftWeeklySchedule[currentDay] = [];
      const targetArr = draftWeeklySchedule[currentDay];
      if (!targetArr.some(en => en.start === newHHMM)) {
        targetArr.push({ start: newHHMM, temperature: entry.temperature });
        targetArr.sort((a, b) => a.start.localeCompare(b.start));
      }

      // re-render affected columns
      const affectedDays = currentDay === fromDay ? [fromDay] : [fromDay, currentDay];
      for (const d of affectedDays) {
        const c = els.scheduleCalendar?.querySelector(`.schedule-cal-day-col[data-day="${d}"]`);
        if (c) renderCalBlocks(d, c);
      }
    };

    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup",   onUp);
    document.addEventListener("touchmove", onMove, { passive: false });
    document.addEventListener("touchend",  onUp);
  };

  block.addEventListener("mousedown",  onDown);
  block.addEventListener("touchstart", onDown, { passive: false });
}

function saveScheduleDraft() {
  if (!scheduleRoomId || !draftWeeklySchedule) {
    closeScheduleModal();
    return;
  }

  const room = state.config.rooms?.[scheduleRoomId];
  if (!room) {
    closeScheduleModal();
    return;
  }

  room.weekly_schedule = normalizeWeeklySchedule(draftWeeklySchedule);
  closeScheduleModal();
}

function openScheduleCopyModal() {
  if (!scheduleRoomId || !draftWeeklySchedule) {
    return;
  }

  if (els.scheduleCopyTitle) {
    els.scheduleCopyTitle.textContent = t("schedule_copy_title");
  }

  renderScheduleCopyRoomList();
  els.scheduleCopyModal.classList.remove("hidden");
}

function closeScheduleCopyModal() {
  els.scheduleCopyModal.classList.add("hidden");
}

function renderScheduleCopyRoomList() {
  if (!els.scheduleCopyRoomsList) {
    return;
  }

  els.scheduleCopyRoomsList.innerHTML = "";

  const entries = Object.entries(state.config.rooms || {}).filter(
    ([roomId]) => roomId !== scheduleRoomId
  );

  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "schedule-empty";
    empty.textContent = t("schedule_copy_no_rooms");
    els.scheduleCopyRoomsList.appendChild(empty);
    return;
  }

  for (const [roomId, room] of entries) {
    const row = document.createElement("label");
    row.className = "schedule-copy-room";

    row.innerHTML = `
      <input type="checkbox" value="${escapeHtml(roomId)}" />
      <span class="schedule-copy-room-label">${escapeHtml(room.label || roomId)}</span>
    `;

    els.scheduleCopyRoomsList.appendChild(row);
  }
}

function applyScheduleToSelectedRooms() {
  if (!scheduleRoomId || !draftWeeklySchedule) {
    closeScheduleCopyModal();
    return;
  }

  const selectedIds = [
    ...els.scheduleCopyRoomsList.querySelectorAll('input[type="checkbox"]:checked'),
  ].map((checkbox) => checkbox.value);

  if (!selectedIds.length) {
    closeScheduleCopyModal();
    return;
  }

  const copiedSchedule = normalizeWeeklySchedule(draftWeeklySchedule);

  for (const roomId of selectedIds) {
    if (!state.config.rooms[roomId]) {
      continue;
    }

    state.config.rooms[roomId].weekly_schedule = structuredClone(copiedSchedule);
  }

  closeScheduleCopyModal();
}

function bindScheduleEvents() {
  if (els.scheduleClose)        els.scheduleClose.addEventListener("click", closeScheduleModal);
  if (els.scheduleCancel)       els.scheduleCancel.addEventListener("click", closeScheduleModal);
  if (els.scheduleSave)         els.scheduleSave.addEventListener("click", saveScheduleDraft);
  if (els.scheduleCopyRoomsBtn) els.scheduleCopyRoomsBtn.addEventListener("click", openScheduleCopyModal);
  if (els.scheduleCopyClose)    els.scheduleCopyClose.addEventListener("click", closeScheduleCopyModal);
  if (els.scheduleCopyCancel)   els.scheduleCopyCancel.addEventListener("click", closeScheduleCopyModal);
  if (els.scheduleCopyApply)    els.scheduleCopyApply.addEventListener("click", applyScheduleToSelectedRooms);

  if (els.scheduleModal) {
    els.scheduleModal.addEventListener("click", (e) => {
      if (e.target === els.scheduleModal) closeScheduleModal();
    });
  }

  if (els.scheduleCopyModal) {
    els.scheduleCopyModal.addEventListener("click", (e) => {
      if (e.target === els.scheduleCopyModal) closeScheduleCopyModal();
    });
  }
}

function bindEvents() {
  els.reloadRoomsBtn.addEventListener("click", reloadRooms);
  els.reloadConfigBtn.addEventListener("click", reloadConfig);
  els.applyTimesToRoomsBtn.addEventListener(
    "click",
    applyGlobalTimesToAllRooms
  );
  if (els.applyTempsToRoomsBtn) {
    els.applyTempsToRoomsBtn.addEventListener("click", applyGlobalTempsToAllRooms);
  }
  if (els.addCircuitBtn) {
    els.addCircuitBtn.addEventListener("click", addCircuit);
  }

  if (els.entityPickerModalClose) {
    els.entityPickerModalClose.addEventListener("click", closeEntityPickerModal);
  }
  if (els.entityPickerModal) {
    els.entityPickerModal.addEventListener("click", (e) => {
      if (e.target === els.entityPickerModal) closeEntityPickerModal();
    });
  }
  if (els.entityPickerModalSearch) {
    els.entityPickerModalSearch.addEventListener("input", () => {
      renderEntityPickerModalList(els.entityPickerModalSearch.value);
    });
  }

  document.addEventListener("click", (e) => {
    const badge = e.target.closest(".label-live[data-entity]");
    if (badge?.dataset.entity) {
      openEntityMoreInfo(badge.dataset.entity);
    }
  });

  bindScheduleEvents();
  bindEditModalEvents();
}

function enableEditTracking() {
  document.addEventListener("focusin", (e) => {
    if (
      e.target.closest(".room") ||
      e.target.closest(".fields") ||
      e.target.closest(".modal-content") ||
      e.target.closest(".entity-picker") ||
      e.target.closest(".circuit-card")
    ) {
      isEditing = true;
    }
  });

  document.addEventListener("focusout", () => {
    setTimeout(() => {
      const active = document.activeElement;
      if (
        !active ||
        (!active.closest(".room") &&
          !active.closest(".fields") &&
          !active.closest(".modal-content") &&
          !active.closest(".entity-picker") &&
          !active.closest(".circuit-card"))
      ) {
        isEditing = false;
      }
    }, 0);
  });
}

function updateStateInMemory(entity) {
  const index = state.allStates.findIndex(
    (item) => item.entity_id === entity.entity_id
  );

  if (index >= 0) {
    state.allStates[index] = entity;
  } else {
    state.allStates.push(entity);
  }

  state.climates = sortByEntityId(
    state.allStates.filter((item) => item.entity_id?.startsWith("climate."))
  );

  state.sensors = sortByEntityId(
    state.allStates.filter((item) => isTemperatureSensor(item))
  );

  state.switches = sortByEntityId(
    state.allStates.filter((item) => item.entity_id?.startsWith("switch."))
  );

  state.switchActuators = sortByEntityId(
    state.allStates.filter(
      (item) =>
        item.entity_id?.startsWith("switch.") ||
        item.entity_id?.startsWith("input_boolean.")
    )
  );

  state.binarySensors = sortByEntityId(
    state.allStates.filter((item) => item.entity_id?.startsWith("binary_sensor."))
  );
}

async function setupLiveUpdates() {
  try {
    const haConn = await getHassConnection();
    const ws = haConn?.conn || haConn;

    if (!ws || typeof ws.subscribeEvents !== "function") {
      console.warn("WebSocket subscribeEvents ist nicht verfügbar");
      return;
    }

    if (typeof unsubscribeStateChanged === "function") {
      unsubscribeStateChanged();
      unsubscribeStateChanged = null;
    }

    unsubscribeStateChanged = await ws.subscribeEvents((event) => {
      const entity = event?.data?.new_state;
      if (!entity?.entity_id) {
        return;
      }

      updateStateInMemory(entity);

      if (entity.entity_id === CONFIG_ENTITY_ID) {
        const incoming = normalizeConfig(entity.attributes || {});

        // room_states immer aktuell halten (Live-Heizstatus-Badges)
        if (incoming.room_states) {
          state.config.room_states = incoming.room_states;
        }
        if (entity.attributes?.room_status) {
          state.roomStatus = entity.attributes.room_status;
        }

        // Config still update im Hintergrund (damit collectFormState() frische
        // Metadaten wie learned_overshoot, weekly_schedule hat), aber KEIN
        // Form-Re-Render: renderGlobalSettings/renderRooms würden alle
        // ungespeicherten Nutzer-Eingaben (Checkboxen, Inputs, Dropdowns,
        // Fensterkontakt-Picker) überschreiben.
        // Vollständiger Re-Render nur bei: init→refreshAll(), saveConfig()-Erfolg,
        // explizitem Reload-Button.
        if (!isSaving && !isEditing && !editSession) {
          state.config = incoming;
          if (pendingCircuits !== null) {
            state.config.circuits = pendingCircuits;
          }
        }

        // Nur Live-Status-Elemente aktualisieren (kein Form-Reset)
        updateRoomLiveState();
        return;
      }

      if (isEditing) {
        return;
      }

      updateRoomLiveState();
    }, "state_changed");
  } catch (error) {
    console.warn(t("status_live_updates_failed"), error);
  }
}

// ─── −/+ stepper for temperature inputs ──────────────────────────────────────
const STEPPER_SELECTOR = 'input[type="number"][step="0.5"]';

function enhanceNumberStepper(input) {
  if (input.closest(".num-stepper")) return;

  const wrapper = document.createElement("div");
  wrapper.className = "num-stepper";
  if (input.classList.contains("toggle-temp")) {
    wrapper.classList.add("num-stepper-compact");
  }

  const makeButton = (label, direction) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "num-stepper-btn";
    btn.textContent = label;
    btn.tabIndex = -1;
    btn.addEventListener("click", () => {
      if (input.disabled || input.readOnly) return;
      const step = Number(input.step) || 0.5;
      const min = input.min !== "" ? Number(input.min) : -Infinity;
      const max = input.max !== "" ? Number(input.max) : Infinity;
      let value = Number(input.value);
      if (input.value === "" || !Number.isFinite(value)) {
        value = Number.isFinite(min) ? min : 0;
      } else {
        // snap to the step grid first, then move one step
        value = Math.round(value / step) * step + direction * step;
      }
      value = Math.min(max, Math.max(min, value));
      input.value = String(Number(value.toFixed(2)));
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
    return btn;
  };

  input.parentNode.insertBefore(wrapper, input);
  wrapper.append(makeButton("−", -1), input, makeButton("+", 1));
}

function enhanceNumberSteppers(root) {
  if (root.matches?.(STEPPER_SELECTOR)) {
    enhanceNumberStepper(root);
  }
  root.querySelectorAll?.(STEPPER_SELECTOR).forEach(enhanceNumberStepper);
}

function observeNumberSteppers() {
  enhanceNumberSteppers(document.body);
  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE && !node.classList.contains("num-stepper")) {
          enhanceNumberSteppers(node);
        }
      }
    }
  }).observe(document.body, { childList: true, subtree: true });
}

async function init() {
  initEls();
  observeNumberSteppers();
  applyTranslations();
  bindEvents();
  enableEditTracking();
  renderVersion();
  setButtonsDisabled(true);
  setStatus(t("status_initializing"), "warn");

  try {
    await refreshAll();
    await setupLiveUpdates();
    setStatus(t("status_loaded"), "ok");
  } catch (error) {
    console.error(error);
    setStatus(`Initialisierung fehlgeschlagen: ${error.message}`, "err");
  } finally {
    setButtonsDisabled(false);
  }
}

// ─── Help modal ──────────────────────────────────────────────────────────────
function setupHelpModal() {
  const modal = document.getElementById("help-modal");
  if (!modal) return;

  let helpLang = UI_LANG;

  function setHelpLang(lang) {
    helpLang = lang;
    modal.querySelectorAll(".help-lang-content").forEach((el) => {
      el.classList.toggle("hidden", el.dataset.lang !== lang);
    });
    document.getElementById("help-lang-de").classList.toggle("active", lang === "de");
    document.getElementById("help-lang-en").classList.toggle("active", lang === "en");
  }

  document.getElementById("helpBtn").addEventListener("click", () => {
    modal.classList.remove("hidden");
    setHelpLang(helpLang);
  });

  document.getElementById("help-modal-close").addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.add("hidden");
  });

  document.getElementById("help-lang-de").addEventListener("click", () => setHelpLang("de"));
  document.getElementById("help-lang-en").addEventListener("click", () => setHelpLang("en"));

  setHelpLang(UI_LANG);
}

setupHelpModal();
init();
