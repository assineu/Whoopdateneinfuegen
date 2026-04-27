# Whoopdateneinfuegen

Diese Repo enthält eine **Custom Integration für Home Assistant**, mit der du zentrale WHOOP-Werte (Recovery, Strain, Schlaf usw.) als Sensoren anzeigen kannst.

## Enthalten

- `custom_components/whoop`: Home-Assistant Integration mit Config Flow
- `lovelace/whoop_dashboard.yaml`: Beispiel-Karten (Gauge + Entities + Verlauf)
- `hacs.json`: HACS-Metadaten für die Installation als Custom Repository

## 1) Installation

### Option A: Über HACS (empfohlen)

1. Stelle sicher, dass HACS installiert ist.
2. Öffne **HACS → Integrations → ⋮ → Custom repositories**.
3. Füge diese URL als **Integration** hinzu:
   - `https://github.com/assineu/Whoopdateneinfuegen`
4. Suche in HACS nach **WHOOP for Home Assistant** und installiere die Integration.
5. Starte Home Assistant neu.

#### HACS/GitHub 404 Fehler

- Prüfe, ob die Repository-URL im Browser erreichbar ist.
- Prüfe, ob die Repository öffentlich ist.
- Prüfe User/Repo-Namen auf Tippfehler.
- Wenn die Repo umbenannt wurde: altes Custom Repo aus HACS entfernen und neu hinzufügen.

### Option B: Manuell

1. Kopiere `custom_components/whoop` in dein HA-Config-Verzeichnis.
2. Starte Home Assistant neu.

## 2) Integration einrichten

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Nach **WHOOP** suchen
3. Eingaben:
   - **API Token** (WHOOP Developer Token)
   - **User-ID** optional (wird automatisch erkannt, wenn leer)

## 3) User-ID Format

- WHOOP `user_id` ist **numerisch** (Integer), z. B. `10129`.
- Wenn das Feld leer bleibt, versucht die Integration die User-ID automatisch aus dem Token zu ermitteln.
- Falls das fehlschlägt, trage die numerische User-ID manuell ein.

## 4) Verfügbare Sensoren

- `sensor.whoop_recovery`
- `sensor.whoop_strain`
- `sensor.whoop_sleep_performance`
- `sensor.whoop_resting_heart_rate`
- `sensor.whoop_hrv`
- `sensor.whoop_sleep_efficiency`
- `sensor.whoop_energy`
- `sensor.whoop_sleep_need`

Update-Intervall: alle 5 Minuten.

## 5) Dashboard/Karten

Nutze `lovelace/whoop_dashboard.yaml` als Vorlage.

### Als neues Dashboard

- **Einstellungen → Dashboards → Dashboard hinzufügen**
- Typ: YAML
- Inhalt aus `lovelace/whoop_dashboard.yaml` einfügen

### In bestehender Ansicht

- Karten manuell hinzufügen (Gauge/Entities/History Graph)
- Entity-IDs aus der Vorlage übernehmen

## 6) Hinweise

- Wenn Entitäten bei dir anders heißen, IDs im Dashboard anpassen.
- Bei Auth-Fehlern Integration löschen und mit neuem Token neu einrichten.
