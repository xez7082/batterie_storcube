import os
import asyncio
import websockets
import logging
import json
import requests
from datetime import datetime
from paho.mqtt import client as mqtt_client

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Variables d'environnement
MQTT_BROKER = os.getenv('MQTT_BROKER', '192.168.1.1')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USERNAME')
MQTT_PASS = os.getenv('MQTT_PASSWORD')
DEVICE_ID = os.getenv('DEVICE_ID')
APP_CODE = os.getenv('APP_CODE', 'Storcube')
LOGIN_NAME = os.getenv('LOGIN_NAME')
PASSWORD_AUTH = os.getenv('PASSWORD')

# Topics
TOPIC_BATTERY = os.getenv('MQTT_TOPIC_BATTERY', 'battery/reportEquip')
TOPIC_POWER_COMMAND = os.getenv('MQTT_TOPIC_POWER', 'battery/set_power')
TOPIC_THRESHOLD_COMMAND = os.getenv('MQTT_TOPIC_THRESHOLD', 'battery/set_threshold')

# API Endpoints
WS_URI = "ws://baterway.com:9501/equip/info/"
BASE_URL = "http://baterway.com/api"

def get_auth_token():
    try:
        url = f"{BASE_URL}/user/app/login"
        payload = {"appCode": APP_CODE, "loginName": LOGIN_NAME, "password": PASSWORD_AUTH}
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('code') == 200:
            return data['data']['token']
    except Exception as e:
        logging.error(f"Erreur Token: {e}")
    return None

def send_discovery_config(client):
    """Déclare l'appareil dans Home Assistant automatiquement"""
    device = {
        "identifiers": [DEVICE_ID],
        "name": "Storcube Stacker",
        "manufacturer": "Storcube",
        "model": "Stacker"
    }
    
    # Capteur SOC (Batterie %)
    soc_config = {
        "name": "Batterie",
        "unique_id": f"{DEVICE_ID}_soc",
        "state_topic": TOPIC_BATTERY,
        "device_class": "battery",
        "unit_of_measurement": "%",
        "value_template": "{{ value_json.soc }}",
        "device": device
    }
    
    # Capteur Puissance de sortie
    power_config = {
        "name": "Puissance Sortie",
        "unique_id": f"{DEVICE_ID}_power_out",
        "state_topic": TOPIC_BATTERY,
        "device_class": "power",
        "unit_of_measurement": "W",
        "value_template": "{{ value_json.outPower }}",
        "device": device
    }

    client.publish(f"homeassistant/sensor/{DEVICE_ID}/soc/config", json.dumps(soc_config), retain=True)
    client.publish(f"homeassistant/sensor/{DEVICE_ID}/power/config", json.dumps(power_config), retain=True)
    logging.info("✅ Configuration Discovery envoyée à Home Assistant")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info("✅ Connecté au broker MQTT")
        send_discovery_config(client)
        client.subscribe([(TOPIC_POWER_COMMAND, 0), (TOPIC_THRESHOLD_COMMAND, 0)])
    else:
        logging.error(f"❌ Échec connexion MQTT, code: {rc}")

def on_message(client, userdata, message):
    # Logique de traitement des commandes (ton code actuel simplifié)
    try:
        payload = json.loads(message.payload.decode())
        token = get_auth_token()
        if not token: return

        if message.topic == TOPIC_POWER_COMMAND and "power" in payload:
            val = payload["power"]
            res = requests.get(f"{BASE_URL}/slb/equip/set/power", 
                               params={"equipId": DEVICE_ID, "power": val},
                               headers={"Authorization": token, "appCode": APP_CODE})
            logging.info(f"Commande Power {val}W: {res.status_code}")

    except Exception as e:
        logging.error(f"Erreur on_message: {e}")

async def run_bridge():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    if MQTT_USER: client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()

    while True:
        token = get_auth_token()
        if not token:
            await asyncio.sleep(10)
            continue
        
        try:
            async with websockets.connect(f"{WS_URI}{token}") as ws:
                logging.info("📡 WebSocket Storcube Ouvert")
                await ws.send(json.dumps({"reportEquip": [DEVICE_ID]}))
                
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    # On extrait les datas de la batterie
                    battery_data = next(iter(data.values()), {})
                    client.publish(TOPIC_BATTERY, json.dumps(battery_data))
                    
        except Exception as e:
            logging.warning(f"WebSocket déconnecté: {e}. Reconnexion...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_bridge())
