from fastapi import FastAPI
from fastapi_mqtt import FastMQTT, MQTTConfig
import json
import uvicorn

app = FastAPI()

# Local list to store devices and their status
devices_status = {}
poll_counter = 0

# Read configuration from config.json file one directory up
# config_file_path = os.path.join(os.path.dirname(__file__),'common', 'config.json')
config_file_path = "/app/common/config.json"
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# MQTT broker configuration
mqtt_broker_url = config["mqtt"]["broker_url"]
mqtt_broker_port = config["mqtt"]["broker_port"]

# FastAPI app configuration
app_port = config["scheduler_mqtt_helper_app"]["port"]
app_address = config["scheduler_mqtt_helper_app"]["address"]

mqtt_config = MQTTConfig(host = mqtt_broker_url,
    port= int(mqtt_broker_port),
    keepalive = 60,
)

mqtt = FastMQTT(
    config=mqtt_config
)

mqtt.init_app(app)

@mqtt.on_connect()
def connect(client, flags, rc, properties):
    pass
    # mqtt.client.subscribe("/mqtt") #subscribing mqtt topic
    # print("Connected: ", client, flags, rc, properties)

@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ",topic, payload.decode(), qos, properties)

# @mqtt.subscribe("my/mqtt/topic/#")
# async def message_to_topic(client, topic, payload, qos, properties):
#     print("Received message to specific topic: ", topic, payload.decode(), qos, properties)

@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")

@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)

@app.get("/{device}/change_status/{status}")
async def change_status(device: str, status: str):
    topic = f"/{device}/change_status"
    payload = status
    mqtt.publish(topic, payload) 
    return {"result": True,"topic":topic, "payload":payload }

if __name__ == "__main__":
    uvicorn.run(app, host=app_address, port=app_port)
