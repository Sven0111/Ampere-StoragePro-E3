# Ampere StoragePro E3

Home-Assistant-Integration für den **Ampere StoragePro E3** (Hybrid-Wechselrichter / Batteriespeicher, FoxESS-basiert) über **Modbus TCP** – komplett lokal, ohne Cloud.

## ✨ Features

- 🔌 **Lokal über Modbus TCP** – keine Cloud, keine Zugangsdaten nötig
- ⚡ **Umfangreiche Sensorik**: PV-Strings & MPPTs, Netz, Last, EPS/Notstrom, Wechselrichter-Leistungen
- 🔋 **Batterie/BMS**: SoC, SOH, Spannung, Strom, Temperaturen, Fehler- und Alarmstatus im Klartext
- 📊 **Native Energiezähler** (kWh) – direkt aus dem Gerät, ideal fürs **Energie-Dashboard**
- 🧩 **Automatische Erkennung** von BMS1/BMS2 und Meter1/Meter2 – nicht verbundene Komponenten werden ausgeblendet
- ⚙️ **Effizientes Polling** über einen zentralen Coordinator mit persistenter Verbindung
- 🌐 Oberfläche auf **Deutsch & Englisch**

## 📦 Installation

1. In **HACS** das Repository (falls nicht vorhanden) als benutzerdefiniertes Repository hinzufügen und herunterladen.
2. **Home Assistant neu starten.**
3. *Einstellungen → Geräte & Dienste → Integration hinzufügen* → **Ampere StoragePro E3**.

## ⚙️ Einrichtung

Bei der Einrichtung werden abgefragt:

| Feld | Beschreibung | Standard |
|------|--------------|----------|
| **Host / IP-Adresse** | IP des Wechselrichters bzw. des Modbus-Gateways | – |
| **Port** | Modbus-TCP-Port | `502` |
| **Modbus Slave-ID** | Geräteadresse auf dem Bus | `247` |

In den **Optionen** lassen sich nachträglich das **Aktualisierungsintervall** (10/30/60/120 s) und die **Diagnose-Sensoren** einstellen.

> 💡 Die Geräteinfos (Modell, Seriennummer, Hersteller) werden beim Einrichten automatisch ausgelesen.

## 📈 Energie-Dashboard

Für das HA-Energie-Dashboard eignen sich die nativen kumulativen Zähler, u. a.:

- **Erzeugung:** `Total PV input Power` / `PV Power Total`
- **Batterie:** `Total Charging Capacity` (Laden) / `Total Discharge Power` (Entladen)
- **Netz:** `Total Power Taken` (Bezug) / `Total Feeder Network Power` (Einspeisung)
- **Verbrauch:** `Total Load Power`

## ❓ Hinweise

- Benötigt einen erreichbaren **Modbus-TCP-Zugang** zum Gerät (direkt oder via Gateway).
- Polling-Intervall ist konfigurierbar; sehr kurze Intervalle erhöhen die Buslast.

## 🐛 Probleme melden

Fehler und Wünsche bitte als **Issue** im Repository melden:
👉 https://github.com/Sven0111/Ampere-StoragePro-E3/issues
