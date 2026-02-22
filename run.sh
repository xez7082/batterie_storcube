#!/usr/bin/with-contenu-env bashio

# On récupère les options configurées par l'utilisateur dans l'interface HA
export MQTT_BROKER=$(bashio::config 'MQTT_BROKER')
export MQTT_PORT=$(bashio::config 'MQTT_PORT')
export MQTT_USERNAME=$(bashio::config 'MQTT_USERNAME')
export MQTT_PASSWORD=$(bashio::config 'MQTT_PASSWORD')
export LOGIN_NAME=$(bashio::config 'LOGIN_NAME')
export PASSWORD=$(bashio::config 'PASSWORD')
export DEVICE_ID=$(bashio::config 'DEVICE_ID')

echo "Démarrage du pont Storcube Stacker..."
python3 /usr/src/app/batteryMqtt.py
