# Messerinzidenz Discord Bot

Ein Discord-Bot, der täglich Messerangriff-Vorfälle in Deutschland trackt und in einem Discord-Channel anzeigt. Der Bot nutzt die API von [messerinzidenz.de](https://messerinzidenz.de), um aktuelle Vorfälle abzurufen und diese in Form von detaillierten Embed-Nachrichten mit Standortkarten (über Mapbox) anzuzeigen.

## Funktionen

- **Automatische Aktualisierung**: Der Bot überprüft alle 30 Minuten auf neue Messerangriff-Vorfälle.
- **Standortkarten**: Zeigt den Standort des Vorfalls auf einer Karte an, die mit Mapbox generiert wird.
- **Detaillierte Informationen**: Enthält Informationen wie Ort, Bundesland, Datum, Verletzte und einen Link zur Pressemeldung.
- **Zähler für Vorfälle**: Zeigt die Gesamtanzahl der getrackten Vorfälle an, seit dem der Bot aktiv ist.
- **Persistenz**: Speichert bereits gesendete Vorfälle, um Duplikate zu vermeiden.

## Voraussetzungen

- Python 3.8 oder höher
- Ein Discord-Bot-Token (erstellt über das [Discord Developer Portal](https://discord.com/developers/applications))
- Ein Mapbox Access Token (kostenlos erhältlich über [Mapbox](https://www.mapbox.com/))
- Eine `config.ini`-Datei mit den erforderlichen Konfigurationen

## Installation

1. **Repository klonen**:
   ```bash
   git clone https://github.com/revunix/Messerinzidenz-Bot.git
   cd Messerinzidenz-Bot
   ```

2. **Python-Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurationsdatei erstellen**:
   Erstelle eine `config.ini`-Datei im Stammverzeichnis des Projekts mit folgendem Inhalt:
   ```ini
   [revBot]
   TOKEN = dein-discord-bot-token

   [knife]
   channel_id = dein-discord-channel-id

   [mapbox]
   access_token = dein-mapbox-access-token
   ```

4. **Bot starten**:
   ```bash
   python knife.py
   ```

## Verwendung

Sobald der Bot läuft, überprüft er automatisch alle 30 Minuten auf neue Messerangriff-Vorfälle und sendet diese in den konfigurierten Discord-Channel. Jeder Vorfall wird als Embed-Nachricht mit einer Standortkarte und detaillierten Informationen angezeigt.

## Beispiel

![Beispiel-Embed](https://i.imgur.com/rbfVL08.png)  
*Beispiel für eine Embed-Nachricht, die der Bot sendet.*

---

## Beitrag

Falls du Verbesserungsvorschläge hast oder einen Fehler gefunden hast, erstelle gerne ein Issue oder einen Pull Request. Beiträge sind immer willkommen!

---

## Danksagung

- [messerinzidenz.de](https://messerinzidenz.de) für die Bereitstellung der API.
- [Mapbox](https://www.mapbox.com/) für die Kartenintegration.
- [Discord.py](https://discordpy.readthedocs.io/) für die Discord-Bot-Entwicklung.

---

Diese Beschreibung bietet einen guten Überblick über dein Projekt und erklärt, wie man es einrichtet und verwendet. Du kannst sie in die `README.md`-Datei deines GitHub-Repositorys einfügen.
