<h1>
<img src="https://raw.githubusercontent.com/19DMO89/smartdome_heat_control/main/images/icon.png" width="48">
Smartdome Heat Control
</h1>

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2026.1%2B-blue.svg)](https://home-assistant.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-PayPal-blue.svg)](https://www.paypal.me/DominikSchremser)

Smartdome Heat Control is an advanced **multi-room heating controller for Home Assistant**.

It works in two ways — with or without a central heating system:

| Setup | Description |
|---|---|
| **With main thermostat** | Smartdome activates your central heating system when one or more rooms need heat, and shuts it off when no room needs heat anymore. |
| **Without main thermostat** | Smartdome controls only the individual radiator thermostats per room. No central heating system required. |

> **Important:** The main thermostat is only used to switch the heating system on or off. All room-level control (temperatures, schedules, modes) works the same regardless of whether a main thermostat is configured.

---

# How It Works

Each room is monitored individually using a temperature sensor and a radiator thermostat.

1. Smartdome compares the current room temperature against the target temperature.
2. If a room needs heat:
   - the **radiator thermostat opens**
   - the **main thermostat activates the heating system** *(if configured)*
3. Once the target temperature is reached:
   - the **radiator thermostat closes**
   - if no other room needs heat, the **main thermostat shuts the system down** *(if configured)*

---

# Features

### Smart Room Heating

Each room can be configured individually with:

- Radiator thermostat *(optional — see Sensor-only Rooms below)*
- Temperature sensor
- Day and night target temperatures
- Day/night schedule or weekly schedule
- Window contact sensor
- Away temperature
- Enable/disable per room

---

### Sensor-only Rooms

Rooms **without a smart thermostat** can still be integrated using only a temperature sensor. In sensor-only mode:

- The room **contributes to the central heating signal** — if it falls below its target temperature, the main controller is activated
- **No thermostat commands are sent** — individual valve control is not possible
- Mechanical TRVs and the central heating system handle heat distribution naturally

To enable: configure the room with a sensor and target temperature, leave the thermostat field empty.

> **Note:** Smartdome cannot prevent an overheated sensor-only room from receiving heat when another room triggers the heating system. Mechanical TRVs will limit this naturally once their set temperature is reached.

---

### Weekly Schedule

Each room supports a fully customizable weekly schedule.

![Week Schedule](images/weekschedule.png)

You can define different time slots for every day of the week, each with its own target temperature. This allows precise control over when a room heats up — for example warmer in the morning and evening, cooler during the day.

---

### Thermostat Control Profiles

Each room can be assigned one of two control profiles depending on the type of thermostat used:

| Profile | Description |
|---|---|
| **Standard** | Smartdome controls the thermostat by setting the target temperature above the desired value (boost) to force the valve open. Recommended for most thermostats (e.g. Shelly TRV, Tado, etc.). |
| **Self-Regulating** | Smartdome only sets the exact target temperature and does not apply a boost. The thermostat handles valve control autonomously. Required for thermostats that self-regulate and must not receive override commands. |

> **Homematic / Homematic IP via CCU (OCCU):** These thermostats regulate themselves internally and react negatively to frequent target temperature overrides. **Always use the Self-Regulating profile for Homematic thermostats connected via OCCU.** Smartdome will then only send the exact target temperature and respect a minimum 120-second interval between commands.

---

### Window Open Detection

When a window sensor detects an open window:

- Heating in that room is paused automatically
- The radiator thermostat is set to minimum temperature
- Heating resumes automatically once the window is closed

A configurable delay prevents the system from reacting to very short ventilation.

---

### Vacation Mode

Reduces heating across all rooms for longer absences.

Entities:

    switch.smartdome_heat_control_vacation_mode
    number.smartdome_heat_control_vacation_temperature

---

### Away Mode

Reduces heating to each room's configured away temperature for short absences.

Entity:

    switch.smartdome_heat_control_away_mode

---

### Heating Modes

A global heating strategy controls how the system behaves when rooms reach their target temperature.

| Mode | Description |
|---|---|
| **Comfort** | Radiator valves stay open longer — reduces temperature fluctuations, prioritizes comfort. |
| **Balanced** *(default)* | Recommended standard mode — good balance between comfort and energy efficiency. |
| **Energy** | Valves close earlier to reduce overheating — prioritizes energy saving. |
| **Adaptive** | Smartdome learns how each room behaves and automatically compensates for temperature overshoot. |

Entity:

    select.smartdome_heat_control_heating_mode

---

### Adaptive Learning

In Adaptive mode, Smartdome measures how much a room overshoots its target temperature after a heating cycle and automatically adjusts future behavior.

Smartdome uses **three separate learning buckets** based on heating cycle duration:

| Bucket | Duration | Default overshoot |
|---|---|---|
| Short | < 15 min | 0.2 °C |
| Medium | 15 – 45 min | 0.4 °C |
| Long | > 45 min | 0.7 °C |

Example:

    Target temperature:  21.0 °C
    Actual peak:         21.5 °C
    Learned overshoot:    0.5 °C (medium bucket)
    → Next cycle: heating stops 0.5 °C earlier

Learned values are persisted across Home Assistant restarts.

---

### Main Controller Type

Smartdome supports two types of central heating control. You choose the type once in the global settings — it applies to the main controller and can be set independently for each heating circuit.

| Type | When to use | How it works |
|---|---|---|
| **Thermostat** | You have a smart heating controller (e.g. Lambdatronic, Fröling, Viessmann, Nilan) connected as a `climate` entity | Smartdome sets the target temperature above the current sensor value to activate the circuit, and below to deactivate it |
| **Smart switch** | You have no thermostat but a simple smart relay or switch (e.g. Shelly, Sonoff, WLED) that directly powers the heating pump or boiler | Smartdome calls `switch.turn_on` when any room needs heat and `switch.turn_off` when no room needs heat — no sensor required |

> If you have no central controller at all, simply leave the field empty. Smartdome will then only control the individual room thermostats.

---

### Heating Circuits

For buildings with **multiple independent heating circuits** (e.g. underfloor + radiators, or different floors), each circuit can be configured with its own main controller (thermostat **or** switch) and sensor.

| Setup | Description |
|---|---|
| **No circuits configured** | Works with the global main controller setting for all rooms. |
| **Circuits configured** | Each circuit has its own main controller. Rooms are assigned to circuits and grouped accordingly in the UI. Each circuit can independently use a thermostat or a switch. |

> Circuits are only needed if the building has multiple physically separate heating systems. For most homes, no circuits need to be configured.

---

# Dashboard

### Main Interface

![Smartdome UI](images/ui.png)

The main dashboard shows all rooms and global settings at a glance.

---

### Global Settings

![Global Settings](images/global.png)

Configure:

- **Controller type** — Thermostat or Smart switch *(optional)*
- Main thermostat or main switch *(optional)*
- Main temperature sensor *(optional, thermostat mode only)*
- Boost delta
- Temperature tolerance
- Global day/night times
- Heating mode
- Vacation and away mode
- Heating circuits *(optional — only for multi-circuit buildings)*

---

### Room Configuration

![Room View](images/room.png)

Configure each room individually:

- Thermostat *(optional — leave empty for sensor-only mode)*, sensor, window sensor
- Day/night target temperatures
- Away temperature
- Day/night schedule or weekly schedule
- Thermostat control profile
- Heating circuit assignment *(optional)*
- Enable/disable

---

# Installation

### HACS (Recommended)

1. Open **HACS**
2. Go to **Integrations**
3. Click **Custom repositories**
4. Add this repository URL:

       https://github.com/19DMO89/smartdome_heat_control

   Category: `Integration`

5. Install **Smartdome Heat Control**
6. Restart Home Assistant

---

# Configuration

After installation:

    Settings → Devices & Services → Add Integration → Smartdome Heat Control

The setup asks for:

- **Main thermostat** *(optional — only needed if you have a central heating system)*
- **Main temperature sensor** *(optional)*

Rooms can then be discovered automatically from your Home Assistant areas, or added and configured manually in the dashboard.

---

# Home Assistant Entities

### Switches

    switch.smartdome_heat_control_enabled
    switch.smartdome_heat_control_away_mode
    switch.smartdome_heat_control_vacation_mode

### Numbers

    number.smartdome_heat_control_vacation_temperature

### Selects

    select.smartdome_heat_control_heating_mode

### State Entity

    smartdome_heat_control.config

---

---

<h1>
<img src="https://raw.githubusercontent.com/19DMO89/smartdome_heat_control/main/images/icon.png" width="48">
Smartdome Heat Control (Deutsch)
</h1>

Smartdome Heat Control ist eine **intelligente Mehrraum-Heizungssteuerung für Home Assistant**.

Die Integration funktioniert auf zwei Arten — mit oder ohne zentrale Heizungsanlage:

| Setup | Beschreibung |
|---|---|
| **Mit Hauptthermostat** | Smartdome aktiviert die Heizungsanlage, wenn ein oder mehrere Räume Wärme benötigen, und schaltet sie ab, wenn kein Raum mehr Wärme braucht. |
| **Ohne Hauptthermostat** | Smartdome steuert nur die einzelnen Heizkörperthermostate je Raum. Keine zentrale Heizungsanlage notwendig. |

> **Wichtig:** Das Hauptthermostat dient ausschließlich dazu, die Heizungsanlage ein- oder auszuschalten. Die gesamte Raumsteuerung (Temperaturen, Zeitpläne, Modi) funktioniert unabhängig davon, ob ein Hauptthermostat konfiguriert ist oder nicht.

---

# Funktionsweise

Jeder Raum wird individuell über einen Temperatursensor und ein Heizkörperthermostat überwacht.

1. Smartdome vergleicht die aktuelle Raumtemperatur mit der Zieltemperatur.
2. Wenn ein Raum Wärme benötigt:
   - öffnet das **Heizkörperthermostat**
   - aktiviert das **Hauptthermostat die Heizungsanlage** *(falls konfiguriert)*
3. Sobald die Zieltemperatur erreicht ist:
   - schließt das **Heizkörperthermostat**
   - schaltet das **Hauptthermostat die Anlage ab**, wenn kein Raum mehr heizt *(falls konfiguriert)*

---

# Funktionen

### Raumsteuerung

Jeder Raum kann individuell konfiguriert werden mit:

- Heizkörperthermostat *(optional — siehe Sensor-only Räume)*
- Temperatursensor
- Tag- und Nacht-Zieltemperaturen
- Tag/Nacht-Zeitplan oder Wochenschema
- Fensterkontaktsensor
- Abwesenheitstemperatur
- Aktivieren/Deaktivieren pro Raum

---

### Sensor-only Räume

Räume **ohne smarten Thermostat** können allein über einen Temperatursensor eingebunden werden. Im Sensor-only Modus:

- Trägt der Raum zum **Heiz-Signal des Zentralreglers** bei — fällt er unter die Zieltemperatur, wird der Hauptregler aktiviert
- Werden **keine Thermostat-Befehle gesendet** — eine individuelle Ventilsteuerung ist nicht möglich
- Übernehmen mechanische TRVs und der Zentralregler die Wärmeverteilung

Einrichten: Raum mit Sensor und Zieltemperatur konfigurieren, Thermostat-Feld leer lassen.

> **Hinweis:** Smartdome kann nicht verhindern, dass ein überhitzter Sensor-only Raum Wärme bekommt, wenn ein anderer Raum den Kessel auslöst. Mechanische TRVs begrenzen dies natürlich, sobald ihre eingestellte Temperatur erreicht ist.

---

### Wochenschema

Jeder Raum unterstützt ein frei konfigurierbares Wochenschema.

![Wochenschema](images/weekschedule.png)

Für jeden Wochentag können individuelle Zeitslots mit eigener Zieltemperatur definiert werden. So lässt sich zum Beispiel morgens und abends wärmer heizen und tagsüber kühler halten.

---

### Thermostat-Regelprofile

Jedem Raum kann eines von zwei Regelprofilen zugewiesen werden, je nach verwendetem Thermostattyp:

| Profil | Beschreibung |
|---|---|
| **Standard** | Smartdome steuert das Thermostat, indem es die Zieltemperatur über den gewünschten Wert anhebt (Boost), um das Ventil zu öffnen. Empfohlen für die meisten Thermostate (z.B. Shelly TRV, Tado, etc.). |
| **Selbst regelnd** | Smartdome setzt nur die exakte Zieltemperatur und wendet keinen Boost an. Das Thermostat übernimmt die Ventilsteuerung eigenständig. Erforderlich für Thermostate, die sich selbst regeln und keine Überschreibungsbefehle vertragen. |

> **Homematic / Homematic IP über CCU (OCCU):** Diese Thermostate regeln sich intern selbst und reagieren negativ auf häufige Sollwertüberschreibungen. **Für alle Homematic-Thermostate, die über die OCCU eingebunden sind, muss das Profil „Selbst regelnd" verwendet werden.** Smartdome sendet dann nur die exakte Zieltemperatur und hält einen Mindestabstand von 120 Sekunden zwischen Befehlen ein.

---

### Fenster-Erkennung

Wenn ein Fensterkontakt ein geöffnetes Fenster meldet:

- Wird die Heizung in diesem Raum automatisch pausiert
- Das Thermostat wird auf Mindesttemperatur abgesenkt
- Nach dem Schließen des Fensters wird die Heizung automatisch wieder aufgenommen

Eine konfigurierbare Verzögerung verhindert, dass das System auf kurzes Lüften reagiert.

---

### Urlaubsmodus

Senkt die Heizung aller Räume für längere Abwesenheiten ab.

Entitäten:

    switch.smartdome_heat_control_vacation_mode
    number.smartdome_heat_control_vacation_temperature

---

### Abwesenheitsmodus

Senkt die Heizung auf die je Raum konfigurierte Abwesenheitstemperatur — gedacht für kurze Abwesenheiten.

Entität:

    switch.smartdome_heat_control_away_mode

---

### Heizmodi

Eine globale Heisstrategie bestimmt, wie das System reagiert wenn Räume ihre Zieltemperatur erreichen.

| Modus | Beschreibung |
|---|---|
| **Comfort** | Heizkörperventile bleiben länger offen — weniger Temperaturschwankungen, Komfort im Vordergrund. |
| **Balanced** *(Standard)* | Empfohlener Standardmodus — gute Balance zwischen Komfort und Energieeffizienz. |
| **Energy** | Ventile schließen früher um Überhitzen zu vermeiden — Energiesparen im Vordergrund. |
| **Adaptive** | Smartdome lernt das Verhalten jedes Raumes und kompensiert automatisch Temperatur-Überschwingen. |

Entität:

    select.smartdome_heat_control_heating_mode

---

### Adaptives Lernen

Im Adaptive-Modus misst Smartdome, wie stark ein Raum nach einem Heizzyklus über die Zieltemperatur hinausschießt, und passt das zukünftige Verhalten automatisch an.

Smartdome verwendet **drei separate Lern-Buckets** basierend auf der Heizzyklusdauer:

| Bucket | Dauer | Standard-Überschwingen |
|---|---|---|
| Kurz | < 15 Min | 0,2 °C |
| Mittel | 15 – 45 Min | 0,4 °C |
| Lang | > 45 Min | 0,7 °C |

Beispiel:

    Zieltemperatur:          21,0 °C
    Tatsächlicher Peak:      21,5 °C
    Gelerntes Überschwingen:  0,5 °C (Mittel-Bucket)
    → Nächster Zyklus: Heizung stoppt 0,5 °C früher

Gelernte Werte bleiben über Home Assistant-Neustarts hinweg erhalten.

---

### Steuertyp Hauptregler

Smartdome unterstützt zwei Arten der zentralen Heizungssteuerung. Der Typ wird einmalig in den globalen Einstellungen gewählt — pro Heizkreis kann er unabhängig festgelegt werden.

| Typ | Wann verwenden | Wie es funktioniert |
|---|---|---|
| **Thermostat** | Du hast einen smarten Heizkreisregler (z.B. Lambdatronic, Fröling, Viessmann, Nilan) als `climate`-Entity eingebunden | Smartdome setzt den Sollwert über den aktuellen Sensorwert um den Kreis zu aktivieren, und darunter um ihn abzuschalten |
| **Smarter Schalter (Switch)** | Du hast kein Thermostat sondern ein smarten Relais oder Schalter (z.B. Shelly, Sonoff), der die Heizungspumpe oder den Kessel direkt schaltet | Smartdome ruft `switch.turn_on` auf wenn ein Raum Wärme braucht und `switch.turn_off` wenn kein Raum mehr heizt — kein Sensor erforderlich |

> Wenn kein zentraler Regler vorhanden ist, das Feld einfach leer lassen. Smartdome steuert dann nur die einzelnen Raumthermostate.

---

### Heizkreise

Für Gebäude mit **mehreren unabhängigen Heizkreisen** (z.B. Fußbodenheizung + Heizkörper oder verschiedene Etagen) kann jeder Heizkreis mit eigenem Hauptregler (Thermostat **oder** Switch) und Sensor konfiguriert werden.

| Setup | Beschreibung |
|---|---|
| **Keine Heizkreise konfiguriert** | Nutzt den globalen Hauptregler für alle Räume. |
| **Heizkreise konfiguriert** | Jeder Kreis hat seinen eigenen Hauptregler. Räume werden Kreisen zugewiesen und im Dashboard entsprechend gruppiert. Jeder Kreis kann unabhängig einen Thermostat oder einen Switch verwenden. |

> Heizkreise werden nur benötigt, wenn das Gebäude mehrere physisch getrennte Heizsysteme besitzt. In den meisten Häusern ist keine Konfiguration von Heizkreisen erforderlich.

---

# Dashboard

### Hauptansicht

![Smartdome UI](images/ui.png)

Das Dashboard zeigt alle Räume und globale Einstellungen auf einen Blick.

---

### Globale Einstellungen

![Globale Einstellungen](images/global.png)

Konfigurierbar:

- **Steuertyp** — Thermostat oder Smarter Schalter *(optional)*
- Hauptthermostat oder Hauptschalter *(optional)*
- Haupttemperatursensor *(optional, nur im Thermostat-Modus)*
- Boost-Delta
- Temperaturtoleranz
- Globale Tag/Nacht-Zeiten
- Heizmodus
- Urlaubs- und Abwesenheitsmodus
- Heizkreise *(optional — nur für Mehrkreis-Gebäude)*

---

### Raumkonfiguration

![Raumansicht](images/room.png)

Jeden Raum einzeln konfigurieren:

- Thermostat *(optional — leer lassen für Sensor-only Modus)*, Sensor, Fensterkontakt
- Tag/Nacht-Zieltemperaturen
- Abwesenheitstemperatur
- Tag/Nacht-Zeitplan oder Wochenschema
- Thermostat-Regelprofil
- Heizkreis-Zuweisung *(optional)*
- Aktivieren/Deaktivieren

---

# Installation

### HACS (Empfohlen)

1. **HACS** öffnen
2. **Integrationen** auswählen
3. **Benutzerdefinierte Repositories** klicken
4. Repository-URL hinzufügen:

       https://github.com/19DMO89/smartdome_heat_control

   Kategorie: `Integration`

5. **Smartdome Heat Control** installieren
6. Home Assistant neu starten

---

# Konfiguration

Nach der Installation:

    Einstellungen → Geräte & Dienste → Integration hinzufügen → Smartdome Heat Control

Der Einrichtungsassistent fragt nach:

- **Hauptthermostat** *(optional — nur nötig wenn eine zentrale Heizungsanlage vorhanden ist)*
- **Haupttemperatursensor** *(optional)*

Räume können anschließend automatisch aus den Home Assistant Areas erkannt oder manuell im Dashboard angelegt und konfiguriert werden.

---

# Lizenz

MIT License
