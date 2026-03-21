# Changelog

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
