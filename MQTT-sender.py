import paho.mqtt.client as mqtt
import ssl
import json
import time
import logging

IOT_CORE_MQTT_HOST = "mqtt.cloud.yandex.net"
IOT_CORE_MQTT_PORT = 8883
IOT_DEVICE_ID = "arenavlulht4jms10qpc"
TOPIC = f"$devices/{IOT_DEVICE_ID}/events"

CERT_PATH = "/Users/angeles/Desktop/serts/"  # Папка с сертификатами
CA_CERT = CERT_PATH + "rootCA.crt"  # Корневой сертификат Яндекса
DEVICE_CERT = CERT_PATH + "cer1t.pem"  # Сгенерированный сертификат устройства
PRIVATE_KEY = CERT_PATH + "ke1y.pem"  # Сгеренированный закрытый ключ устройства

payload_dict = {"temperature": 26.5}
payload_str = json.dumps(payload_dict) 

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Успешное подключение!")
        client.publish(TOPIC, payload=payload_str, qos=1)
        print(f" Отправлено сообщение: {payload_str}")
        client.disconnect()  
    else:
        print(f"Ошибка подключения: {rc}")

client = mqtt.Client(client_id=IOT_DEVICE_ID)
client.tls_set(CA_CERT, certfile=DEVICE_CERT, keyfile=PRIVATE_KEY, tls_version=ssl.PROTOCOL_TLS)
client.on_connect = on_connect

client.connect(IOT_CORE_MQTT_HOST, IOT_CORE_MQTT_PORT, 60)
client.loop_forever()
