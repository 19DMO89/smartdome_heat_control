# Changelog

## [3.2.8] – 2026-03-27

### 🔧 Fix: Heizpumpensteuerung ist kein Pflichtfeld mehr

**Problem:** Beim Einrichten der Integration erschien die Fehlermeldung „Nicht alle Pflichtfelder ausgefüllt", obwohl laut Dokumentation das Feld „Heizpumpensteuerung" leer gelassen werden kann. Die Konfiguration ließ sich dadurch nicht abschließen.

**Ursache:** `CONF_MAIN_THERMOSTAT` war in `config_flow.py` als `vol.Required` deklariert – sowohl im initialen Setup-Schritt als auch in den globalen Einstellungen. Das machte das Feld auf Voluptuous-Ebene zum Pflichtfeld, obwohl der Controller intern bereits `None` korrekt behandelt.

**Fix:** Beide Vorkommen auf `vol.Optional` geändert. Das Feld kann jetzt leer gelassen werden; die Integration funktioniert dann ohne zentrale Heizpumpensteuerung (z. B. bei reiner Raumthermostat-Steuerung).

---

**EN:** Fixed a validation error that prevented completing the setup when "Heizpumpensteuerung" was left empty. The field was declared as `vol.Required` in both the initial config step and the global settings step, making it mandatory at the form level even though the controller already handled `None` correctly. Changed both occurrences to `vol.Optional`.

---

## [3.2.7] – 2026-03-22

### 🔧 Fix: Konfiguration springt nach „Konfiguration übernehmen" zurück

**Zwei Race-Conditions behoben:**

**Bug A – Bearbeitungs-Override:** Im WebSocket `state_changed`-Handler wurde `renderGlobalSettings()` bisher immer aufgerufen – auch wenn `isEditing = true`. Jede Minute, wenn der Controller `_evaluate()` ausführt und den Zustand pusht, wurden die laufenden Änderungen des Nutzers in den globalen Einstellungen kommentarlos überschrieben.

**Bug B – Save-Race-Condition:** In `saveConfig()` wurde `isEditing = false` *vor* dem `await callService(...)` gesetzt. Traf während dieser Wartezeit ein veraltetes `state_changed`-Event ein, renderte das Frontend kurz die alte Konfiguration – sichtbar als „Zurückspringen".

**Fix:**
- Neues `isSaving`-Flag, das während des gesamten Save-Vorgangs gesetzt ist.
- Im `state_changed`-Handler: Config wird nur neu gerendert wenn `!isSaving && !isEditing`.
- `room_states` (Live-Heizstatus-Badges) werden weiterhin immer aktualisiert.

---

**EN:** Fixed two race conditions causing the config to visually revert after saving. `renderGlobalSettings()` was always called in `state_changed` even during editing (Bug A). `isEditing` was cleared before `await callService`, allowing stale events to overwrite the UI during the save (Bug B). New `isSaving` flag blocks config re-renders during save; live `room_states` badges still update normally.

---

## [3.2.6] – 2026-03-22

### 🔧 Fix: Heizkreis schaltet sich ab obwohl Räume Wärme brauchen

**Ursache 1 – Sensor-Flackern:** Wenn ein Raumsensor kurz `unavailable` oder `unknown` zurückgab, wurde der Raum sofort auf `IDLE` gezwungen. Dadurch wurde `any_circuit_needs_heat = False` und der Heizkreis schaltete sich ab – auch wenn der Sensor nur für einen Moment nicht erreichbar war.

**Fix:** Bei `actual = None` (Sensor nicht verfügbar) wird der aktuelle Raumzustand jetzt eingefroren statt auf IDLE zurückgesetzt. Ein Raum der bereits heizte bleibt in `HEATING`. Heating kann ohne Sensor nicht neu gestartet werden (bleibt `IDLE`), aber ein laufender Heizzyklus wird nicht abgebrochen.

**Ursache 2 – `RESIDUAL_HOLD` nicht als "braucht Wärme" gewertet:** Im Energy-Modus wechseln Räume nach Zielerreichung in den Zustand `RESIDUAL_HOLD` (Restwärme-Nachlauf). Dieser Zustand wurde bisher nicht als "Heizkreis braucht Wärme" gewertet, was dazu führte, dass der Heizkreis abgeschaltet wurde bevor die Restwärme vollständig verteilt war.

**Fix:** `ROOM_STATE_RESIDUAL_HOLD` wird jetzt gleichwertig mit `ROOM_STATE_HEATING` behandelt, wenn ermittelt wird ob ein Heizkreis aktiv bleiben soll.

**Neu: Debug-Logging:** Jedes Mal wenn ein Heizkreis von HEATING auf IDLE (oder umgekehrt) wechselt, wird ein `DEBUG`-Log-Eintrag mit den aktuellen Raumzuständen geschrieben. Damit lässt sich in den HA-Logs präzise nachvollziehen warum ein Heizkreis ab- oder angeschaltet hat.

---

**EN – Root causes and fixes:**
- **Sensor flicker:** A temporarily unavailable room sensor forced the room to `IDLE`, causing `any_circuit_needs_heat = False` and shutting off the circuit. Fixed by freezing the current room state when `actual is None` instead of forcing IDLE.
- **`RESIDUAL_HOLD` not counted as "needs heat":** In energy mode, rooms transition to `RESIDUAL_HOLD` after reaching target. This state is now treated the same as `HEATING` for circuit-level decisions.
- **Debug logging added:** Each circuit ON↔OFF transition now logs the per-room states at `DEBUG` level.

---

## [3.2.5] – 2026-03-22

### 🔧 Fix: Heizkreise ließen sich nach dem Speichern nicht löschen

**DE:** Der `update_config`-Service behandelte das `circuits`-Feld als Deep-Merge-Patch statt als vollständige Ersetzung. Ein leeres `circuits: {}` vom Frontend wurde mit `deep_merge({circuit_abc: {...}}, {})` verarbeitet — ein leeres Dict hat keine Keys zu iterieren, daher blieben alle bestehenden Kreise unverändert im Backend. Gelöst durch die gleiche Behandlung wie `rooms`: circuits wird im Service immer vollständig ersetzt statt gemergt.

**EN:** The `update_config` service was treating the `circuits` field as a deep-merge patch instead of a full replacement. An empty `circuits: {}` from the frontend was processed as `deep_merge({circuit_abc: {...}}, {})` — an empty dict has no keys to iterate, so all existing circuits remained unchanged in the backend. Fixed by applying the same handling as `rooms`: circuits is now always fully replaced in the service instead of merged.

---

## [3.2.4] – 2026-03-22

### 🔧 Fix: Heizkreise ließen sich nach dem Anlegen nicht mehr löschen

**DE:** Ein Fehler im Live-Update-Mechanismus führte dazu, dass gelöschte Heizkreise sofort wieder im Panel auftauchten, sobald der Controller einen Room-State-Update sendete (was sekündlich passieren kann). Die Ursache: Der WebSocket-Handler hat bei jedem Config-Entity-Update `state.config` vollständig aus dem Backend überschrieben — ohne zu berücksichtigen, ob der User gerade ungespeicherte Änderungen an Heizkreisen hatte. Gelöst durch einen `pendingCircuits`-Mechanismus, der ausstehende Änderungen bei eingehenden Live-Updates konserviert, bis der User explizit speichert.

**EN:** A bug in the live-update mechanism caused deleted heating circuits to reappear in the panel as soon as the controller sent a room-state update (which can happen every second). The root cause: the WebSocket handler was completely overwriting `state.config` from the backend on every config-entity update — without preserving unsaved circuit changes. Fixed via a `pendingCircuits` mechanism that preserves pending changes during incoming live updates until the user explicitly saves.

---

### ✅ Neu: Heizkreise aktivierbar / deaktivierbar

**DE:** Jeder Heizkreis kann über eine Checkbox im Panel deaktiviert werden. Ein deaktivierter Kreis wird vom Controller vollständig ignoriert — seine Heizpumpensteuerung wird auf Minimum gesetzt bzw. der Switch ausgeschaltet. Die Einstellung wird persistiert und überlebt einen Neustart.

**EN:** Each heating circuit can now be disabled via a checkbox in the panel. A disabled circuit is fully ignored by the controller — its pump controller is set to minimum temperature or the switch is turned off. The setting is persisted and survives restarts.

---

### 🌙 Neu: Nachtabsenkung pro Raum aktivierbar / deaktivierbar

**DE:** Pro Raum kann die Nachtabsenkung über eine Checkbox direkt neben der Nacht-Zieltemperatur deaktiviert werden. Ist die Nachtabsenkung deaktiviert, verwendet der Raum unabhängig von der Uhrzeit immer die Tages-Zieltemperatur. Die Felder für Nacht-Zieltemperatur und Nacht-Startzeit werden optisch ausgegraut wenn die Funktion deaktiviert ist.

**EN:** Night setback can now be disabled per room via a checkbox directly next to the night target temperature. When disabled, the room always uses the day target temperature regardless of the time of day. The night target temperature and night start time fields are visually greyed out when the feature is disabled.

---

### 🌡️ Temperatureingaben in 0,5 °C-Schritten

**DE:** Alle Temperaturfelder im Panel (Zieltemperatur Tag/Nacht, Away-Temperatur, Urlaubstemperatur, Wochenplan, Boost-Delta, Toleranz) verwenden jetzt 0,5 °C-Schritte statt 0,1 °C. Das entspricht der praktischen Auflösung gängiger Heizkörperthermostate.

**EN:** All temperature inputs in the panel (day/night target, away temperature, vacation temperature, weekly schedule, boost delta, tolerance) now use 0.5 °C steps instead of 0.1 °C, matching the practical resolution of common radiator thermostats.

---

## [3.2.3] – 2026-03-21

### 🔧 Fix: UI-Felder nach Updates nicht sichtbar (Browser-Cache)

**DE:** Der Browser hat `app.js` aggressiv gecacht, wodurch neue UI-Felder nach einem Update nicht angezeigt wurden — obwohl der neue Code bereits aktiv war. Der Script-Tag enthält jetzt einen Versions-Parameter (`?v=3.2.3`), der den Browser zwingt, die neue Version zu laden.

**EN:** The browser was aggressively caching `app.js`, causing newly added UI fields to remain invisible after an update — even though the new code was already active. The script tag now includes a version parameter (`?v=3.2.3`) that forces the browser to load the updated file.

---

### 🌡️ Neu: Thermostat-Kalibrierungsoffset pro Raum

**DE:** Selbst-regelnde Thermostate (z. B. OCCU/Homematic, Better Thermostat) messen die Temperatur am Ventilkörper — dieser liegt durch das zurückfließende Kaltwasser systematisch ~1 °C unter der tatsächlichen Raumtemperatur. Das führt dazu, dass der Raum ~1 °C wärmer geregelt wird als gewünscht. Mit dem neuen Offset-Feld kann das pro Raum korrigiert werden (z. B. `−1,0 °C` → Thermostat erhält 18 °C als Sollwert → regelt auf 19 °C Raumtemperatur).

**EN:** Self-regulating thermostats (e.g. OCCU/Homematic, Better Thermostat) measure temperature at the valve body — which reads systematically ~1 °C lower than actual room temperature due to cold return water. This causes rooms to be regulated ~1 °C warmer than desired. The new offset field allows per-room correction (e.g. `−1.0 °C` → thermostat receives 18 °C setpoint → regulates to 19 °C room temperature).

**Einstellungen / Settings → Raumkarte:**
- Thermostat-Kalibrierungsoffset (°C) / Thermostat calibration offset (°C): −5 bis +5 °C (Standard / Default: 0 °C)

**Verhalten / Behavior:**
- Der Offset wird nur auf den an den Thermostat gesendeten Sollwert angewendet
- Die interne Steuerlogik (Heizen starten/stoppen) arbeitet weiterhin mit der unkorrigierten Raumtemperatur
- Fensterkontakt-Pause (Frostschutztemperatur) bleibt unberührt

---

## [3.2.2] – 2026-03-21

- chore: interne Versionsvorbereitung für 3.2.x-Releases

## [3.2.1] – 2026-03-20

- feat: Außentemperatur-Abschaltung jetzt vollständig im Panel konfigurierbar (Sensor, Schwellenwert, Toggle)

## [3.2.0] – 2026-03-20

### 🌡️ Neu: Außentemperatur-Abschaltung / Outdoor Temperature Cutoff

**DE:** Die Heizung kann jetzt automatisch abgeschaltet werden, sobald die Außentemperatur einen konfigurierbaren Schwellenwert erreicht oder überschreitet. Die Funktion ist standardmäßig deaktiviert und lässt sich jederzeit ein- oder ausschalten.

**EN:** Heating can now be automatically suppressed when the outdoor temperature reaches or exceeds a configurable threshold. The feature is disabled by default and can be toggled at any time.

**Einstellungen / Settings → Globale Einstellungen / Global Settings:**
- Außentemperatursensor / Outdoor temperature sensor
- Abschaltung aktiv (Checkbox) / Outdoor temperature cutoff enabled (checkbox)
- Schwellenwert / Threshold: –20 °C bis +30 °C (Standard / Default: 15 °C)

**Verhalten / Behavior:**
- Raumthermostate bleiben auf ihrem normalen Idle-Sollwert (kein Frostschutzmodus)
- Haupt-Thermostat / Pumpen-Switch wird nicht eingeschaltet
- Reagiert in Echtzeit auf Sensorzustandsänderungen

---

### 🖥️ UI: Live-Zustand des Pumpen-Switches

**DE:** Neben dem Feld für den Pumpen-Switch wird jetzt der aktuelle Schaltzustand der Entität angezeigt (`🟢 on` / `⚫ off`). Ein Klick auf das Badge öffnet den Home Assistant More-Info-Dialog der Entität — genauso wie bei den Thermostat- und Sensorfeldern.

**EN:** The pump switch field now shows the current entity state inline (`🟢 on` / `⚫ off`). Clicking the badge opens the Home Assistant More-Info dialog for that entity — consistent with the thermostat and sensor live badges.

---

### 🌍 Fix: Konfigurationsflow jetzt international

**DE:** Die `strings.json` war versehentlich auf Deutsch, was dazu führte, dass der HA-Integrationsbereich (Einstellungen → Integrationen) für alle nicht-deutschen Nutzer ebenfalls auf Deutsch angezeigt wurde. Die Datei enthält jetzt Englisch als internationale Basis-Sprache. Die deutschen Texte bleiben in `translation/de.json` und funktionieren wie gewohnt.

**EN:** `strings.json` was accidentally in German, causing the HA integrations UI to display in German for all non-German users. The file now contains English as the international base language. German translations remain in `translation/de.json` and work as before.

---

## [3.1.9] – 2026-03-14

- UI: Sektionsüberschriften und Feldlabels auf "Heizpumpensteuerung" vereinheitlicht

## [3.1.8] – 2026-03-12

- UI: Zentralregler-Felder einheitlich umbenannt

## [3.1.7] – 2026-03-10

- UI: Feldbeschriftungen Räume und Switch/Thermostat Hilfstexte verbessert

## [3.1.6] – 2026-03-08

- Docs: Sensor-only Räume dokumentiert, Translations synchronisiert

## [3.1.5] – 2026-03-07

- Docs: Steuertyp-Feature dokumentiert
- feat: Steuertyp-Auswahl (Thermostat oder Switch) für Hauptregler und Heizkreise

## [3.1.4] – 2026-03-05

- fix: Idle-Sollwert des Hauptthermostats = Sensor − 5 °C (statt min_temp)

## [3.1.3] – 2026-03-04

- fix: Hauptthermostat auch ohne aktive Räume auf min_temp setzen

## [3.1.2] – 2026-03-03

- fix: Hauptthermostat beim Deaktivieren auf min_temp setzen

## [3.1.0] – 2026-03-01

- feat: Multi-Heizkreis-Unterstützung (Circuits)
- feat: Adaptive Overshoot-Lernlogik mit Dauer-Buckets

## [3.0.0] – 2026-02-20

- feat: Komplette UI-Überarbeitung
- feat: Selbst regelnde Thermostate (z. B. Homematic OCCU)
- feat: Mehrere Fensterkontakte pro Raum
- feat: Wochenplan pro Raum
