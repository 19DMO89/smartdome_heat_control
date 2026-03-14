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

    select_not_set: "— Not set —",
    select_choose: "— Please choose —",
    select_auto_none: "— Automatic / none —",

    mode_comfort: "Comfort",
    mode_balanced: "Balanced",
    mode_energy: "Energy",
    mode_adaptive: "Adaptive",
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

    select_not_set: "— Nicht gesetzt —",
    select_choose: "— Bitte wählen —",
    select_auto_none: "— Automatisch / keiner —",

    mode_comfort: "Comfort",
    mode_balanced: "Balanced",
    mode_energy: "Energy",
    mode_adaptive: "Adaptive",
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
  mainThermostat: document.getElementById("main_thermostat"),
  mainSensor: document.getElementById("main_sensor"),
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
};

let unsubscribeStateChanged = null;
let isEditing = false;

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

function buildSelectOptions(selectEl, items, selectedValue, options = {}) {
  const {
    includeEmpty = true,
    emptyLabel = t("select_not_set"),
  } = options;

  selectEl.innerHTML = "";

  if (includeEmpty) {
    const emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = emptyLabel;
    selectEl.appendChild(emptyOption);
  }

  for (const item of items) {
    const option = document.createElement("option");
    option.value = item.entity_id;
    option.textContent = prettyEntityLabel(item);
    if (item.entity_id === selectedValue) {
      option.selected = true;
    }
    selectEl.appendChild(option);
  }
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
    state.allStates.filter((item) => item.entity_id?.startsWith("binary_sensor."))
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

  buildSelectOptions(els.mainThermostat, state.climates, cfg.main_thermostat, {
    includeEmpty: true,
    emptyLabel: t("select_choose"),
  });

  buildSelectOptions(els.mainSensor, state.sensors, cfg.main_sensor, {
    includeEmpty: true,
    emptyLabel: t("select_auto_none"),
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
          <input class="room-enabled" type="checkbox" ${room.enabled ? "checked" : ""} />
          <span>${escapeHtml(t("room_active"))}</span>
        </span>
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
        <select class="room-thermostat"></select>
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_sensor"))}</label>
        <select class="room-sensor"></select>
      </div>

      <div class="field">
        <label>${escapeHtml(t("room_window_sensor"))}</label>
        <select class="room-window-sensor"></select>
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

  const thermostatSelect = wrapper.querySelector(".room-thermostat");
  const sensorSelect = wrapper.querySelector(".room-sensor");
  const windowSensorSelect = wrapper.querySelector(".room-window-sensor");
  const deleteBtn = wrapper.querySelector(".room-delete-btn");

  buildSelectOptions(thermostatSelect, state.climates, room.thermostat || "", {
    includeEmpty: true,
    emptyLabel: t("select_not_set"),
  });

  buildSelectOptions(sensorSelect, state.sensors, room.sensor || "", {
    includeEmpty: true,
    emptyLabel: t("select_not_set"),
  });

  buildSelectOptions(
    windowSensorSelect,
    state.binarySensors,
    room.window_sensor || "",
    {
      includeEmpty: true,
      emptyLabel: t("select_not_set"),
    }
  );

  deleteBtn.addEventListener("click", () => {
    delete state.config.rooms[roomId];
    renderRooms();
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
  cfg.main_thermostat = els.mainThermostat.value || "";
  cfg.main_sensor = els.mainSensor.value || "";
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
      thermostat: node.querySelector(".room-thermostat").value || "",
      sensor: node.querySelector(".room-sensor").value || "",
      window_sensor: node.querySelector(".room-window-sensor").value || "",
      control_profile:
        node.querySelector(".room-control-profile")?.value || "standard",
      target_day: node.querySelector(".room-target-day").value,
      target_night: node.querySelector(".room-target-night").value,
      away_temperature: node.querySelector(".room-away-temperature").value,
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
}

function enableEditTracking() {
  document.addEventListener("focusin", (e) => {
    if (e.target.closest(".room") || e.target.closest(".fields")) {
      isEditing = true;
    }
  });

  document.addEventListener("focusout", () => {
    setTimeout(() => {
      const active = document.activeElement;
      if (!active || (!active.closest(".room") && !active.closest(".fields"))) {
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
