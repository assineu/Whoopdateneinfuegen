# Whoopdateneinfuegen

Diese Repo enthält eine **Custom Integration für Home Assistant**, mit der du zentrale WHOOP-Werte (Recovery, Strain, Schlaf usw.) direkt als Sensoren bekommst.

## Enthalten

- `custom_components/whoop`: Home-Assistant Integration mit Config Flow
- `lovelace/whoop_dashboard.yaml`: Beispiel-Karten (Gauge + Entities + Verlauf)
- `hacs.json`: HACS-Metadaten für die Installation als Custom Repository

## 1) Integration installieren

### Option A: Über HACS (empfohlen)

1. Stelle sicher, dass HACS bereits in Home Assistant installiert ist.
2. Öffne **HACS → Integrations → ⋮ (oben rechts) → Custom repositories**.
3. Füge diese Repository-URL ein und wähle als Kategorie **Integration**.
4. Danach in HACS nach **WHOOP for Home Assistant** suchen und installieren.
5. Home Assistant neu starten.

### Option B: Manuell

1. Kopiere den Ordner `custom_components/whoop` in dein Home-Assistant-Config-Verzeichnis.
2. Starte Home Assistant neu.

## 2) Integration in Home Assistant hinzufügen

1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
2. Suche nach **WHOOP**.
3. Hinterlege:
   - **API Token** (WHOOP Developer Token)
   - **User-ID** (WHOOP User-ID)

## 3) Sensoren

Die Integration legt u. a. folgende Sensoren an:

- `sensor.whoop_recovery`
- `sensor.whoop_strain`
- `sensor.whoop_sleep_performance`
- `sensor.whoop_resting_heart_rate`
- `sensor.whoop_hrv`
- `sensor.whoop_sleep_efficiency`
- `sensor.whoop_energy`
- `sensor.whoop_sleep_need`

Update-Intervall: alle 5 Minuten.

## 4) Karten/Dashboard erstellen

Nutze die Datei `lovelace/whoop_dashboard.yaml` als Vorlage.

### Als neues Dashboard

- **Einstellungen → Dashboards → Dashboard hinzufügen**
- Typ: YAML
- Inhalt aus `lovelace/whoop_dashboard.yaml` einfügen

### In bestehender Ansicht

- Eine Karte manuell hinzufügen (Gauge/Entities/History Graph)
- Entity-IDs aus der YAML Vorlage übernehmen

## 5) Hinweise

- Wenn die Entitäten bei dir anders heißen (z. B. durch Sprach-/Namensänderungen), passe die IDs im Dashboard an.
- Bei Auth-Fehlern Integration löschen und mit frischem Token neu anlegen.
