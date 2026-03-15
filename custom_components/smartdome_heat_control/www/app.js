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
      "Global settings on the left, rooms on the right. Rooms can use their own schedules.",
    version: "Version",

    reload_rooms: "Reload rooms",
    reload_config: "Reload",
    save_config: "Save configuration",

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

    main_thermostat: "Main thermostat",
    main_sensor: "Main thermostat temperature sensor",
    boost_delta: "Boost delta (°C)",
    tolerance: "Tolerance (°C)",
    heating_mode: "Heating mode",
    energy_residual_heat_hold: "Residual heat hold (s)",
    vacation_temperature: "Vacation temperature (°C)",
    night_start: "Global night start",
    morning_boost_start: "Global day start",
    morning_boost_end: "Morning boost end",

    mode_hint:
      "<strong>Comfort</strong> keeps valves open longer, <strong>Balanced</strong> is the recommended default, <strong>Energy</strong> closes earlier, <strong>Adaptive</strong> uses learned room behavior.",

    apply_times: "Apply global times to all rooms",
    footer_note:
      'The apply button sets for all rooms: <strong>Day start = global day start</strong> and <strong>Night start = global night start</strong>.',

    rooms_title: "Rooms",
    rooms_subtitle:
      "Scrollable on the right so the global settings remain visible.",
    add_room: "Add room",
    no_rooms: "No rooms configured yet.",

    room_active: "Active",
    room_delete: "Delete",
    room_label: "Label",
    room_area_id: "Area ID",
    room_thermostat: "Thermostat",
    room_sensor: "Temperature sensor",
    room_window_sensor: "Window sensor",
    room_control_profile: "Thermostat control profile",
    control_profile_standard: "Standard thermostat",
    control_profile_self_regulating: "Self-regulating thermostat",
    room_target_day: "Day target temperature (°C)",
    room_target_night: "Night target temperature (°C)",
    room_away_temperature: "Away temperature (°C)",
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
  },

  de: {
    title: "Smartdome Heat Control",
    subtitle:
      "Haupteinstellungen links, Räume rechts. Räume können unabhängig eigene Zeiten bekommen.",
    version: "Version",

    reload_rooms: "Räume neu erkennen",
    reload_config: "Neu laden",
    save_config: "Konfiguration speichern",

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

    main_thermostat: "Hauptthermostat",
    main_sensor: "Temperatursensor Hauptthermostat",
    boost_delta: "Boost-Delta (°C)",
    tolerance: "Toleranz (°C)",
    heating_mode: "Heizmodus",
    energy_residual_heat_hold: "Restwärme-Nachlauf (s)",
    vacation_temperature: "Urlaubstemperatur (°C)",
    night_start: "Globale Nacht-Startzeit",
    morning_boost_start: "Globale Tag-Startzeit",
    morning_boost_end: "Morgen-Boost Ende",

    mode_hint:
      "<strong>Comfort</strong> hält Ventile länger offen, <strong>Balanced</strong> ist der empfohlene Standard, <strong>Energy</strong> schließt früher, <strong>Adaptive</strong> nutzt das gelernte Raumverhalten.",

    apply_times: "Globale Zeiten in alle Räume übernehmen",
    footer_note:
      'Der Übernehmen-Button setzt für alle Räume: <strong>Tag-Start = globale Tag-Startzeit</strong> und <strong>Nacht-Start = globale Nacht-Startzeit</strong>.',

    rooms_title: "Räume",
    rooms_subtitle:
      "Rechts scrollbar, damit die Haupteinstellungen sichtbar bleiben.",
    add_room: "Raum hinzufügen",
    no_rooms: "Noch keine Räume vorhanden.",

    room_active: "Aktiv",
    room_delete: "Löschen",
    room_label: "Bezeichnung",
    room_area_id: "Area-ID",
    room_thermostat: "Thermostat",
    room_sensor: "Temperatursensor",
    room_window_sensor: "Fensterkontakt",
    room_control_profile: "Thermostat-Regelprofil",
    control_profile_standard: "Standard-Thermostat",
    control_profile_self_regulating: "Selbst regelndes Thermostat",
    room_target_day: "Zieltemperatur Tag (°C)",
    room_target_night: "Zieltemperatur Nacht (°C)",
    room_away_temperature: "Away-Temperatur (°C)",
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
  main_thermostat: "",
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
  rooms: {},
};

const state = {
  config: structuredClone(DEFAULTS),
  climates: [],
  sensors: [],
  binarySensors: [],
  allStates: [],
};

const entityPickerState = new Map();

const els = {
  statusBox: document.getElementById("statusBox"),
  saveBtn: document.getElementById("saveBtn"),
  reloadConfigBtn: document.getElementById("reloadConfigBtn"),
  reloadRoomsBtn: document.getElementById("reloadRoomsBtn"),
  addRoomBtn: document.getElementById("addRoomBtn"),
  applyTimesToRoomsBtn: document.getElementById("applyTimesToRoomsBtn"),
  toggleVacationBtn: document.getElementById("toggleVacationBtn"),
  toggleAwayBtn: document.getElementById("toggleAwayBtn"),
  enabled: document.getElementById("enabled"),
  mainThermostatPicker: document.getElementById("main_thermostat_picker"),
  mainSensorPicker: document.getElementById("main_sensor_picker"),
  boostDelta: document.getElementById("boost_delta"),
  tolerance: document.getElementById("tolerance"),
  heatingMode: document.getElementById("heating_mode"),
  energyResidualHeatHold: document.getElementById("energy_residual_heat_hold"),
  nightStart: document.getElementById("night_start"),
  morningBoostStart: document.getElementById("morning_boost_start"),
  morningBoostEnd: document.getElementById("morning_boost_end"),
  vacationEnabled: document.getElementById("vacation_enabled"),
  vacationTemperature: document.getElementById("vacation_temperature"),
  awayEnabled: document.getElementById("away_enabled"),
  roomsContainer: document.getElementById("roomsContainer"),
  versionBadge: document.getElementById("versionBadge"),

  scheduleModal: document.getElementById("schedule-modal"),
  scheduleModalTitle: document.getElementById("schedule-modal-title"),
  scheduleClose: document.getElementById("schedule-close"),
  scheduleCancel: document.getElementById("schedule-cancel"),
  scheduleAdd: document.getElementById("schedule-add"),
  scheduleSave: document.getElementById("schedule-save"),
  scheduleEntries: document.getElementById("schedule-entries"),
  scheduleDayButtons: document.querySelectorAll(".schedule-days button"),
  scheduleCopyRoomsBtn: document.getElementById("schedule-copy-rooms"),

  scheduleCopyModal: document.getElementById("schedule-copy-modal"),
  scheduleCopyTitle: document.getElementById("schedule-copy-title"),
  scheduleCopyClose: document.getElementById("schedule-copy-close"),
  scheduleCopyCancel: document.getElementById("schedule-copy-cancel"),
  scheduleCopyApply: document.getElementById("schedule-copy-apply"),
  scheduleCopyRoomsList: document.getElementById("schedule-copy-rooms-list"),
};

let unsubscribeStateChanged = null;
let isEditing = false;
let scheduleRoomId = null;
let currentScheduleDay = "monday";
let draftWeeklySchedule = null;

function setStatus(message, type = "warn") {
  els.statusBox.textContent = message;
  els.statusBox.className = `status ${type}`;
}

function setButtonsDisabled(disabled) {
  els.saveBtn.disabled = disabled;
  els.reloadConfigBtn.disabled = disabled;
  els.reloadRoomsBtn.disabled = disabled;
  els.addRoomBtn.disabled = disabled;
  els.applyTimesToRoomsBtn.disabled = disabled;

  if (els.toggleVacationBtn) {
    els.toggleVacationBtn.disabled = disabled;
  }

  if (els.toggleAwayBtn) {
    els.toggleAwayBtn.disabled = disabled;
  }

  if (els.heatingMode) {
    els.heatingMode.disabled = disabled;
  }

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

  if (els.scheduleAdd) {
    els.scheduleAdd.textContent = t("schedule_add");
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

  els.scheduleDayButtons.forEach((btn) => {
    const key = dayLabelMap[btn.dataset.day];
    if (key) {
      btn.textContent = t(key);
    }
  });
}

function sortByEntityId(items) {
  return [...items].sort((a, b) => a.entity_id.localeCompare(b.entity_id));
}

function isTemperatureSensor(entity) {
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

  const hours = match[1].padStart(2, "0");
  const minutes = match[2];

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
    sensor: typeof room?.sensor === "string" ? room.sensor : "",
    window_sensor:
      typeof room?.window_sensor === "string" ? room.window_sensor : "",
    control_profile: normalizeControlProfile(room?.control_profile),
    target_day: normalizeNumber(room?.target_day, 21.0),
    target_night: normalizeNumber(room?.target_night, 18.0),
    away_temperature: normalizeNumber(room?.away_temperature, 17.0),
    weekly_schedule: normalizeWeeklySchedule(room?.weekly_schedule),
    day_start: normalizeTime(room?.day_start, ""),
    night_start: normalizeTime(room?.night_start, ""),
    enabled: room?.enabled !== false,
    learned_overshoot: normalizeNumber(room?.learned_overshoot, 0.3),
  };
}

function normalizeConfig(input) {
  const cfg = {
    ...structuredClone(DEFAULTS),
    ...(input || {}),
  };

  cfg.enabled = cfg.enabled !== false;
  cfg.main_thermostat =
    typeof cfg.main_thermostat === "string" ? cfg.main_thermostat : "";
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

  if (!cfg.rooms || typeof cfg.rooms !== "object") {
    cfg.rooms = {};
  }

  const normalizedRooms = {};
  for (const [roomId, room] of Object.entries(cfg.rooms)) {
    normalizedRooms[roomId] = normalizeRoom(roomId, room);
  }

  cfg.rooms = normalizedRooms;
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

  const value = Number(sensor.state);
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

function isRoomHeating(thermostatId) {
  const thermostat = findState(thermostatId);
  if (!thermostat) {
    return false;
  }

  const hvacAction = thermostat.attributes?.hvac_action;
  return hvacAction === "heating";
}

function isWindowOpen(windowSensorId) {
  const sensor = findState(windowSensorId);
  if (!sensor) {
    return false;
  }

  const value = String(sensor.state || "").toLowerCase();
  return value === "on" || value === "open" || value === "true";
}

function roomTitleMeta(room) {
  const temp = getSensorTemperature(room.sensor);
  const heating = isRoomHeating(room.thermostat);
  const windowOpen = isWindowOpen(room.window_sensor);

  const metaParts = [];

  if (temp !== null) {
    metaParts.push(
      `<span class="room-live-temp">${escapeHtml(formatTemperature(temp))}</span>`
    );
  }

  if (heating) {
    metaParts.push(
      `<span class="room-heating" title="${escapeHtml(
        t("room_heating_now")
      )}">🔥</span>`
    );
  }

  if (windowOpen) {
    metaParts.push(
      `<span class="room-window-open" title="${escapeHtml(
        t("room_window_open")
      )}">🪟</span>`
    );
  }

  return metaParts.join(" ");
}

function renderVersion() {
  if (els.versionBadge) {
    els.versionBadge.textContent = `${t("version")} ${PANEL_VERSION}`;
  }
}

function renderModeButtons() {
  if (els.toggleVacationBtn) {
    els.toggleVacationBtn.textContent = state.config.vacation_enabled
      ? t("btn_vacation_disable")
      : t("btn_vacation_enable");
  }

  if (els.toggleAwayBtn) {
    els.toggleAwayBtn.textContent = state.config.away_enabled
      ? t("btn_away_disable")
      : t("btn_away_enable");
  }
}

function renderHeatingMode() {
  if (!els.heatingMode) {
    return;
  }

  const current = normalizeHeatingMode(state.config.heating_mode);
  els.heatingMode.innerHTML = "";

  const options = [
    { value: "comfort", label: t("mode_comfort") },
    { value: "balanced", label: t("mode_balanced") },
    { value: "energy", label: t("mode_energy") },
    { value: "adaptive", label: t("mode_adaptive") },
  ];

  for (const item of options) {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    option.selected = item.value === current;
    els.heatingMode.appendChild(option);
  }
}

function getEntityIcon(entityId) {
  if (!entityId) {
    return "—";
  }
  if (entityId.startsWith("climate.")) {
    return "🔥";
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
  entityPickerState.forEach((_, id) => {
    const root = document.getElementById(id);
    if (root) {
      root.classList.remove("open");
    }
  });
}

function createEntityPicker({
  container,
  pickerId,
  items,
  selectedValue,
  emptyLabel,
  onChange,
}) {
  if (!container) {
    return;
  }

  const normalizedItems = Array.isArray(items) ? items : [];
  entityPickerState.set(pickerId, {
    items: normalizedItems,
    selectedValue: selectedValue || "",
    onChange,
    emptyLabel,
  });

  const selectedItem =
    normalizedItems.find((item) => item.entity_id === selectedValue) || null;

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
      <div class="entity-picker-dropdown">
        <input
          type="text"
          class="entity-picker-search"
          placeholder="${escapeHtml(t("picker_search_placeholder"))}"
        />
        <div class="entity-picker-list"></div>
      </div>
    </div>
  `;

  const root = container.querySelector(".entity-picker");
  const trigger = root.querySelector(".entity-picker-trigger");
  const searchInput = root.querySelector(".entity-picker-search");

  trigger.addEventListener("click", (event) => {
    event.stopPropagation();
    const willOpen = !root.classList.contains("open");
    closeAllEntityPickers();
    if (willOpen) {
      root.classList.add("open");
      renderEntityPickerOptions(pickerId, "");
      searchInput.value = "";
      setTimeout(() => searchInput.focus(), 0);
    }
  });

  searchInput.addEventListener("input", () => {
    renderEntityPickerOptions(pickerId, searchInput.value);
  });

  root.addEventListener("click", (event) => {
    event.stopPropagation();
  });

  renderEntityPickerOptions(pickerId, "");
}

function renderEntityPickerOptions(pickerId, query = "") {
  const config = entityPickerState.get(pickerId);
  const root = document.getElementById(pickerId);
  if (!config || !root) {
    return;
  }

  const list = root.querySelector(".entity-picker-list");
  const q = String(query || "").trim().toLowerCase();

  const entries = [
    {
      entity_id: "",
      attributes: { friendly_name: config.emptyLabel },
      __empty: true,
    },
    ...config.items,
  ].filter((item) => {
    if (!q) {
      return true;
    }
    const haystack = `${item.entity_id} ${getEntityTitle(item)}`.toLowerCase();
    return haystack.includes(q);
  });

  list.innerHTML = "";

  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "entity-picker-no-results";
    empty.textContent = t("picker_no_results");
    list.appendChild(empty);
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
      config.selectedValue = item.entity_id || "";

      if (typeof config.onChange === "function") {
        config.onChange(config.selectedValue);
      }

      const triggerIcon = root.querySelector(
        ".entity-picker-trigger .entity-picker-icon"
      );
      const triggerLabel = root.querySelector(
        ".entity-picker-trigger .entity-picker-label"
      );

      triggerIcon.textContent = item.__empty ? "—" : icon;
      triggerLabel.textContent = title;
      triggerLabel.classList.toggle("entity-picker-empty", !!item.__empty);

      closeAllEntityPickers();
      renderEntityPickerOptions(pickerId, "");
    });

    list.appendChild(option);
  }
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

async function callService(domain, service, data = {}) {
  return haFetch(`/api/services/${domain}/${service}`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

async function loadAllStates() {
  const states = await haFetch("/api/states");
  state.allStates = Array.isArray(states) ? states : [];

  state.climates = sortByEntityId(
    state.allStates.filter((item) => item.entity_id?.startsWith("climate."))
  );

  state.sensors = sortByEntityId(
    state.allStates.filter((item) => isTemperatureSensor(item))
  );

  state.binarySensors = sortByEntityId(
    state.allStates.filter((item) =>
      item.entity_id?.startsWith("binary_sensor.")
    )
  );
}

async function loadConfig() {
  try {
    const entity = await haFetch(`/api/states/${CONFIG_ENTITY_ID}`);
    state.config = normalizeConfig(entity?.attributes || {});
  } catch (error) {
    if (String(error.message).includes("404")) {
      state.config = normalizeConfig({});
      return;
    }
    throw error;
  }
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

  createEntityPicker({
    container: els.mainThermostatPicker,
    pickerId: "global_main_thermostat_picker",
    items: state.climates,
    selectedValue: cfg.main_thermostat,
    emptyLabel: t("select_choose"),
    onChange: () => {},
  });

  createEntityPicker({
    container: els.mainSensorPicker,
    pickerId: "global_main_sensor_picker",
    items: state.sensors,
    selectedValue: cfg.main_sensor,
    emptyLabel: t("select_auto_none"),
    onChange: () => {},
  });

  renderHeatingMode();
  renderModeButtons();
}

function createRoomCard(roomId, room) {
  const wrapper = document.createElement("div");
  wrapper.className = "room";
  wrapper.dataset.roomId = roomId;

  const areaText = room.area_id ? `Area: ${room.area_id}` : t("room_manual");
  const roomMeta = roomTitleMeta(room);
  const learnedOvershoot = normalizeNumber(room.learned_overshoot, 0.3);

  wrapper.innerHTML = `
    <div class="room-top">
      <div>
        <div class="room-title-row" style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
          <div class="room-title">${escapeHtml(room.label || roomId)}</div>
          <div class="room-title-meta" style="display:flex; align-items:center; gap:8px; font-size:14px;">
            ${roomMeta}
          </div>
        </div>
        <div class="room-subtitle">${escapeHtml(areaText)}</div>
        <div class="room-subtitle">${escapeHtml(t("room_overshoot"))}: ${escapeHtml(
          learnedOvershoot.toFixed(1)
        )} °C</div>
      </div>
      <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <span class="pill">
          <input class="room-enabled" type="checkbox" ${
            room.enabled ? "checked" : ""
          } />
          <span>${escapeHtml(t("room_active"))}</span>
        </span>
        <button class="ghost room-schedule-btn" type="button">${escapeHtml(
          t("room_schedule")
        )}</button>
        <button class="danger room-delete-btn" type="button">${escapeHtml(
          t("room_delete")
        )}</button>
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
        <label>${escapeHtml(t("room_area_id"))}</label>
        <input class="room-area-id" type="text" value="${escapeHtml(
          room.area_id || ""
        )}" />
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_thermostat"))}</label>
        <div class="room-thermostat-picker"></div>
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_sensor"))}</label>
        <div class="room-sensor-picker"></div>
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_window_sensor"))}</label>
        <div class="room-window-sensor-picker"></div>
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
        <label>${escapeHtml(t("room_target_day"))}</label>
        <input class="room-target-day" type="number" min="5" max="30" step="0.1" value="${escapeHtml(
          room.target_day
        )}" />
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_target_night"))}</label>
        <input class="room-target-night" type="number" min="5" max="30" step="0.1" value="${escapeHtml(
          room.target_night
        )}" />
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_away_temperature"))}</label>
        <input class="room-away-temperature" type="number" min="5" max="30" step="0.1" value="${escapeHtml(
          room.away_temperature
        )}" />
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_day_start"))}</label>
        <input class="room-day-start" type="time" value="${escapeHtml(
          room.day_start || ""
        )}" />
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_night_start"))}</label>
        <input class="room-night-start" type="time" value="${escapeHtml(
          room.night_start || ""
        )}" />
      </div>
    </div>
  `;

  const deleteBtn = wrapper.querySelector(".room-delete-btn");
  const scheduleBtn = wrapper.querySelector(".room-schedule-btn");

  createEntityPicker({
    container: wrapper.querySelector(".room-thermostat-picker"),
    pickerId: `room_${roomId}_thermostat_picker`,
    items: state.climates,
    selectedValue: room.thermostat || "",
    emptyLabel: t("select_not_set"),
    onChange: () => {},
  });

  createEntityPicker({
    container: wrapper.querySelector(".room-sensor-picker"),
    pickerId: `room_${roomId}_sensor_picker`,
    items: state.sensors,
    selectedValue: room.sensor || "",
    emptyLabel: t("select_not_set"),
    onChange: () => {},
  });

  createEntityPicker({
    container: wrapper.querySelector(".room-window-sensor-picker"),
    pickerId: `room_${roomId}_window_sensor_picker`,
    items: state.binarySensors,
    selectedValue: room.window_sensor || "",
    emptyLabel: t("select_not_set"),
    onChange: () => {},
  });

  deleteBtn.addEventListener("click", () => {
    delete state.config.rooms[roomId];
    renderRooms();
  });

  scheduleBtn.addEventListener("click", () => {
    openScheduleModal(roomId);
  });

  return wrapper;
}

function renderRooms() {
  els.roomsContainer.innerHTML = "";

  const entries = Object.entries(state.config.rooms || {});
  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = t("no_rooms");
    els.roomsContainer.appendChild(empty);
    return;
  }

  for (const [roomId, room] of entries) {
    els.roomsContainer.appendChild(createRoomCard(roomId, room));
  }
}

function updateRoomLiveState() {
  const roomNodes = els.roomsContainer.querySelectorAll(".room");

  for (const node of roomNodes) {
    const roomId = node.dataset.roomId;
    const room = state.config.rooms?.[roomId];

    if (!room) {
      continue;
    }

    const titleMeta = node.querySelector(".room-title-meta");
    if (titleMeta) {
      titleMeta.innerHTML = roomTitleMeta(room);
    }

    const subtitleNodes = node.querySelectorAll(".room-subtitle");
    if (subtitleNodes.length >= 2) {
      const learnedOvershoot = normalizeNumber(room.learned_overshoot, 0.3);
      subtitleNodes[1].textContent = `${t("room_overshoot")}: ${learnedOvershoot.toFixed(
        1
      )} °C`;
    }
  }
}

function collectFormState() {
  const cfg = structuredClone(state.config);

  cfg.enabled = els.enabled.checked;
  cfg.main_thermostat = getEntityPickerValue("global_main_thermostat_picker");
  cfg.main_sensor = getEntityPickerValue("global_main_sensor_picker");
  cfg.boost_delta = normalizeNumber(els.boostDelta.value, DEFAULTS.boost_delta);
  cfg.tolerance = normalizeNumber(els.tolerance.value, DEFAULTS.tolerance);
  cfg.heating_mode = els.heatingMode
    ? normalizeHeatingMode(els.heatingMode.value)
    : DEFAULTS.heating_mode;
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

  const rooms = {};
  const roomNodes = els.roomsContainer.querySelectorAll(".room");

  for (const node of roomNodes) {
    const roomId = node.dataset.roomId;
    const existingRoom = state.config.rooms[roomId] || {};

    rooms[roomId] = normalizeRoom(roomId, {
      label: node.querySelector(".room-label").value.trim() || roomId,
      area_id: node.querySelector(".room-area-id").value.trim(),
      thermostat: getEntityPickerValue(`room_${roomId}_thermostat_picker`) || "",
      sensor: getEntityPickerValue(`room_${roomId}_sensor_picker`) || "",
      window_sensor:
        getEntityPickerValue(`room_${roomId}_window_sensor_picker`) || "",
      control_profile:
        node.querySelector(".room-control-profile")?.value || "standard",
      target_day: node.querySelector(".room-target-day").value,
      target_night: node.querySelector(".room-target-night").value,
      away_temperature: node.querySelector(".room-away-temperature").value,
      weekly_schedule: existingRoom.weekly_schedule || DEFAULT_WEEKLY_SCHEDULE,
      day_start: node.querySelector(".room-day-start").value || "",
      night_start: node.querySelector(".room-night-start").value || "",
      enabled: node.querySelector(".room-enabled").checked,
      learned_overshoot: existingRoom.learned_overshoot,
    });
  }

  cfg.rooms = rooms;
  return normalizeConfig(cfg);
}

function generateRoomId() {
  return `room_${Math.random().toString(16).slice(2, 10)}`;
}

function addRoom() {
  const roomId = generateRoomId();
  state.config.rooms[roomId] = {
    label: t("room_new"),
    area_id: "",
    thermostat: "",
    sensor: "",
    window_sensor: "",
    control_profile: "standard",
    target_day: 21.0,
    target_night: 18.0,
    away_temperature: 17.0,
    weekly_schedule: structuredClone(DEFAULT_WEEKLY_SCHEDULE),
    day_start: "",
    night_start: "",
    enabled: true,
    learned_overshoot: 0.3,
  };
  renderRooms();
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

async function toggleVacationMode() {
  try {
    setButtonsDisabled(true);

    const newValue = !state.config.vacation_enabled;

    await callService(DOMAIN, "update_config", {
      config: {
        vacation_enabled: newValue,
      },
    });

    await refreshAll();
    setStatus(
      newValue ? t("status_vacation_on") : t("status_vacation_off"),
      "ok"
    );
  } catch (error) {
    console.error(error);
    setStatus(`${t("status_vacation_failed")}: ${error.message}`, "err");
  } finally {
    setButtonsDisabled(false);
  }
}

async function toggleAwayMode() {
  try {
    setButtonsDisabled(true);

    const newValue = !state.config.away_enabled;

    await callService(DOMAIN, "update_config", {
      config: {
        away_enabled: newValue,
      },
    });

    await refreshAll();
    setStatus(newValue ? t("status_away_on") : t("status_away_off"), "ok");
  } catch (error) {
    console.error(error);
    setStatus(`${t("status_away_failed")}: ${error.message}`, "err");
  } finally {
    setButtonsDisabled(false);
  }
}

async function saveConfig() {
  try {
    isEditing = false;
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
  } catch (error) {
    console.error(error);
    setStatus(`${t("status_save_failed")}: ${error.message}`, "err");
  } finally {
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
  currentScheduleDay = "monday";
  draftWeeklySchedule = normalizeWeeklySchedule(room.weekly_schedule);

  if (els.scheduleModalTitle) {
    const label = room.label || roomId;
    els.scheduleModalTitle.textContent = `${t("schedule_title")} · ${label}`;
  }

  els.scheduleModal.classList.remove("hidden");
  renderScheduleEditor();
}

function closeScheduleModal() {
  scheduleRoomId = null;
  currentScheduleDay = "monday";
  draftWeeklySchedule = null;
  els.scheduleModal.classList.add("hidden");
  closeScheduleCopyModal();
}

function renderScheduleDayButtons() {
  els.scheduleDayButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.day === currentScheduleDay);
    btn.textContent = getDayLabel(btn.dataset.day);
  });
}

function sortScheduleEntries(entries) {
  entries.sort((a, b) => a.start.localeCompare(b.start));
}

function renderScheduleEditor() {
  renderScheduleDayButtons();

  if (!draftWeeklySchedule || !scheduleRoomId) {
    els.scheduleEntries.innerHTML = "";
    return;
  }

  const entries = draftWeeklySchedule[currentScheduleDay] || [];
  els.scheduleEntries.innerHTML = "";

  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "schedule-empty";
    empty.textContent = t("schedule_empty");
    els.scheduleEntries.appendChild(empty);
    return;
  }

  entries.forEach((entry, index) => {
    const row = document.createElement("div");
    row.className = "schedule-entry";

    row.innerHTML = `
      <input class="schedule-time" type="time" value="${escapeHtml(
        entry.start
      )}" />
      <input class="schedule-temp" type="number" min="5" max="30" step="0.1" value="${escapeHtml(
        entry.temperature
      )}" />
      <button type="button" class="danger schedule-delete">✕</button>
    `;

    const timeInput = row.querySelector(".schedule-time");
    const tempInput = row.querySelector(".schedule-temp");
    const deleteBtn = row.querySelector(".schedule-delete");

    timeInput.addEventListener("change", () => {
      entry.start = normalizeTime(timeInput.value, "06:00");
      sortScheduleEntries(entries);
      renderScheduleEditor();
    });

    tempInput.addEventListener("change", () => {
      entry.temperature = normalizeNumber(tempInput.value, 21.0);
    });

    deleteBtn.addEventListener("click", () => {
      entries.splice(index, 1);
      renderScheduleEditor();
    });

    els.scheduleEntries.appendChild(row);
  });
}

function addScheduleEntry() {
  if (!draftWeeklySchedule || !scheduleRoomId) {
    return;
  }

  if (!Array.isArray(draftWeeklySchedule[currentScheduleDay])) {
    draftWeeklySchedule[currentScheduleDay] = [];
  }

  draftWeeklySchedule[currentScheduleDay].push({
    start: "06:00",
    temperature: 21.0,
  });

  sortScheduleEntries(draftWeeklySchedule[currentScheduleDay]);
  renderScheduleEditor();
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
  if (els.scheduleClose) {
    els.scheduleClose.addEventListener("click", closeScheduleModal);
  }

  if (els.scheduleCancel) {
    els.scheduleCancel.addEventListener("click", closeScheduleModal);
  }

  if (els.scheduleAdd) {
    els.scheduleAdd.addEventListener("click", addScheduleEntry);
  }

  if (els.scheduleSave) {
    els.scheduleSave.addEventListener("click", saveScheduleDraft);
  }

  if (els.scheduleCopyRoomsBtn) {
    els.scheduleCopyRoomsBtn.addEventListener("click", openScheduleCopyModal);
  }

  if (els.scheduleCopyClose) {
    els.scheduleCopyClose.addEventListener("click", closeScheduleCopyModal);
  }

  if (els.scheduleCopyCancel) {
    els.scheduleCopyCancel.addEventListener("click", closeScheduleCopyModal);
  }

  if (els.scheduleCopyApply) {
    els.scheduleCopyApply.addEventListener("click", applyScheduleToSelectedRooms);
  }

  els.scheduleDayButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      currentScheduleDay = btn.dataset.day;
      renderScheduleEditor();
    });
  });

  if (els.scheduleModal) {
    els.scheduleModal.addEventListener("click", (event) => {
      if (event.target === els.scheduleModal) {
        closeScheduleModal();
      }
    });
  }

  if (els.scheduleCopyModal) {
    els.scheduleCopyModal.addEventListener("click", (event) => {
      if (event.target === els.scheduleCopyModal) {
        closeScheduleCopyModal();
      }
    });
  }
}

function bindEvents() {
  els.saveBtn.addEventListener("click", saveConfig);
  els.reloadRoomsBtn.addEventListener("click", reloadRooms);
  els.reloadConfigBtn.addEventListener("click", reloadConfig);
  els.addRoomBtn.addEventListener("click", addRoom);
  els.applyTimesToRoomsBtn.addEventListener(
    "click",
    applyGlobalTimesToAllRooms
  );

  if (els.toggleVacationBtn) {
    els.toggleVacationBtn.addEventListener("click", toggleVacationMode);
  }

  if (els.toggleAwayBtn) {
    els.toggleAwayBtn.addEventListener("click", toggleAwayMode);
  }

  bindScheduleEvents();

  document.addEventListener("click", () => {
    closeAllEntityPickers();
  });
}

function enableEditTracking() {
  document.addEventListener("focusin", (e) => {
    if (
      e.target.closest(".room") ||
      e.target.closest(".fields") ||
      e.target.closest(".modal-content") ||
      e.target.closest(".entity-picker")
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
          !active.closest(".entity-picker"))
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
        state.config = normalizeConfig(entity.attributes || {});
        renderGlobalSettings();

        if (!isEditing) {
          renderRooms();
        }

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

async function init() {
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

init();
