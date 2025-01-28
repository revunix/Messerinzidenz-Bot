import discord
import aiohttp
import asyncio
import json
import os
import configparser
import datetime
import logging
from typing import List, Dict, Any

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurationsdatei laden
def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser(interpolation=None)
    if not config.read('config.ini'):
        logging.error("Konfigurationsdatei 'config.ini' nicht gefunden oder konnte nicht gelesen werden.")
        exit(1)
    return config

config = load_config()

# TOKEN und andere Konfigurationen aus der config.ini
try:
    TOKEN = config['revBot']['TOKEN']
    CHANNEL_ID = int(config['knife']['channel_id'])
    MAPBOX_TOKEN = config['mapbox']['access_token']
except KeyError as e:
    logging.error(f"Fehlender Konfigurationswert: {e}")
    exit(1)

SAVED_ENTRIES_FILE = '/opt/knife_database.json'

# Definiere die Intents
intents = discord.Intents.default()
intents.messages = True

# Erstelle den Client mit den Intents
client = discord.Client(intents=intents)

# Zähler für die getrackten Messer-Taten
incident_count = 1  # Initialisiere den Zähler

def generate_api_url() -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.date()

    start_date = datetime.datetime.combine(today, datetime.time.min)
    end_date = datetime.datetime.combine(today, datetime.time.max)

    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S.000Z")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S.000Z")

    api_url = (
        "https://messerinzidenz.de/api/collections/incidents/records"
        f"?page=1&perPage=500&skipTotal=1&fields=id,title,geoData,date,link,location,wounded,timeOfCrime"
        f"&filter=date>='{start_date_str}'&&date<='{end_date_str}'&&geoData!=null"
    )

    logging.info(f"Generated API URL: {api_url}")
    return api_url

def load_saved_entries() -> List[str]:
    if os.path.exists(SAVED_ENTRIES_FILE):
        try:
            with open(SAVED_ENTRIES_FILE, 'r') as f:
                data = json.load(f)
                return data.get("entries", [])
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Fehler beim Laden der JSON-Daten: {e}")
            return []
    return []

def save_entries(entries: List[str]) -> None:
    try:
        data_to_save = {
            "entries": entries,
            "incident_count": incident_count
        }
        with open(SAVED_ENTRIES_FILE, 'w') as f:
            json.dump(data_to_save, f)
    except IOError as e:
        logging.error(f"Fehler beim Speichern der JSON-Daten: {e}")

async def fetch_incidents() -> None:
    global incident_count
    last_ids = load_saved_entries()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        logging.error(f"Channel mit ID {CHANNEL_ID} nicht gefunden.")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            api_url = generate_api_url()
            logging.info(f"Fetching data from API URL: {api_url}")
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    new_entries = [item for item in data['items'] if item['id'] not in last_ids]

                    if new_entries:
                        for item in new_entries[:5]:
                            await send_incident_embed(channel, item)
                            last_ids.append(item['id'])
                            incident_count += 1

                        save_entries(last_ids)
                    else:
                        logging.info("Keine neuen Einträge gefunden.")
                else:
                    logging.error(f"Fehler beim Abrufen der Daten: {response.status}")

            await asyncio.sleep(1800)  # Warte 30 Minuten

async def send_incident_embed(channel: discord.TextChannel, item: Dict[str, Any]) -> None:
    time_of_crime = datetime.datetime.fromisoformat(item['timeOfCrime'].replace('Z', '+00:00'))
    formatted_time = time_of_crime.strftime("%d.%m.%Y %H:%M")

    lat, lon, state = extract_geo_data(item)

    embed = discord.Embed(
        title=f"🚨 **{item['title']}**",
        color=0xFF0000,
        description=(
            f"📍 **Ort:** {item['location']}\n"
            f"🏛️ **Bundesland:** {state}\n"
            f"🕰️ **Datum:** {formatted_time}\n"
            f"🤕 **Verletzte:** {'Ja' if item['wounded'] else 'Nein'}\n"
            f"📰 **Pressemeldung:** [Details]({item['link']})\n"
        ),
    )

    if lat and lon:
        map_url = (
            f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/"
            f"pin-l+FF0000({lon},{lat})/{lon},{lat},18.0,0,0/600x400?access_token={MAPBOX_TOKEN}"
        )
        embed.set_image(url=map_url)
        embed.set_footer(text=f"{incident_count} Messerangriffe insgesamt!")
        embed.set_thumbnail(url="https://i.imgur.com/P7H1PqY.png")
    else:
        embed.set_footer(text=f"{incident_count} Messerangriffe insgesamt!")
        embed.set_thumbnail(url="https://i.imgur.com/P7H1PqY.png")

    if len(embed.description) > 2048:
        embed.description = embed.description[:2045] + "..."

    await channel.send(embed=embed)

def extract_geo_data(item: Dict[str, Any]) -> tuple:
    lat, lon, state = None, None, ""
    if 'geoData' in item:
        geo_data = item['geoData']
        if 'lat' in geo_data and 'lng' in geo_data:
            lat, lon = geo_data['lat'], geo_data['lng']
        if 'components' in geo_data:
            for component in geo_data['components']:
                if 'types' in component and 'administrative_area_level_1' in component['types']:
                    state = component['long_name']
    return lat, lon, state

@client.event
async def on_ready():
    logging.info(f'Bot ist eingeloggt als {client.user}')
    await fetch_incidents()

client.run(TOKEN)
