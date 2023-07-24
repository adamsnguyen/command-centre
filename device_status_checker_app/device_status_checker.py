import os
import json
import asyncio
import paho.mqtt.client as mqtt
import requests
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
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

# Django app configuration
django_app_address = config["command-centre"]["address"]
post_device_status_update_path = config["command-centre"]["post_device_status_update"]

# MQTT broker configuration
mqtt_broker_url = config["mqtt"]["broker_url"]
mqtt_broker_port = config["mqtt"]["broker_port"]

# FastAPI app configuration
fastapi_port = config["device_scheduler_status_checker_app"]["port"]
fastapi_port_address = config["device_scheduler_status_checker_app"]["address"]

# Function to send MQTT message to request status
def send_mqtt_request(device_name):
    client = mqtt.Client()
    client.connect(mqtt_broker_url, mqtt_broker_port)

    topic = f"/{device_name}/get_status"
    payload = "get"
    client.publish(topic, payload)
    client.disconnect()

# Function to handle incoming MQTT messages for status update
def on_message(client, userdata, message):
    device_name = message.topic.split('/')[1]
    status = message.payload.decode("utf-8")
    print(f"device: {device_name}, status: {status}")
    update_local_device_status(device_name, status)

# Function to update local device status
def update_local_device_status(device_name, status):
    if device_name in devices_status and devices_status[device_name] != status:
        devices_status[device_name] = status
        post_status_to_django(device_name, status)
    elif device_name not in devices_status:
        devices_status[device_name] = status

# Function to post status update to Django
def post_status_to_django(device_name, status):
    # Implement logic to post status to the Django API using requests library
    try:
        url = f"{django_app_address}{post_device_status_update_path}{device_name}"
        data = {"status": status}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to update device status in Django.")
    except Exception as e:
        print(e)
# MQTT client setup
mqtt_client = mqtt.Client()

# Set the on_message callback for the MQTT client
mqtt_client.on_message = on_message

mqtt_client.connect(mqtt_broker_url, mqtt_broker_port)

def subscribe_to_topics():
    async def subscribe():
        devices = await get_devices_from_django()
        for device in devices:
            mqtt_client.subscribe(f"/{device['name']}/status")

    mqtt_client.loop_start()
    asyncio.create_task(subscribe())

# Function to get devices from Django API
async def get_devices_from_django():
    url = f"http://localhost:8000/api/get_devices"
    try:
        response = requests.get(url)
        print(response.json())
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve devices from Django.")
    except Exception as e:
        print(e)

async def background_task():
    global poll_counter
    while True:
        if poll_counter == 0:
            try:
                devices = await get_devices_from_django()
                devices_status.clear()  # Clear the existing status to re-populate it with updated device details
                for device in devices:
                    devices_status[device["name"]] = device["status"]
                    send_mqtt_request(device["name"])
            except Exception as e:
                print(e)

        poll_counter = (poll_counter + 1) % 4
        await asyncio.sleep(1)  # Poll every 10 seconds

@app.on_event("startup")
async def startup_event():
    # Start the background task when the app starts
    subscribe_to_topics()
    asyncio.create_task(background_task())

# FastAPI endpoint to get all devices and their statuses
@app.get("/devices", response_model=dict[str, str])
async def get_devices_status():
    return devices_status

# returns device status
@app.get("/device_status/{device}")
async def device_status(device: str):
    global devices_status
    status: str
    try:
        status = devices_status[device]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": status}

if __name__ == "__main__":
    mqtt_client.loop_start()
    uvicorn.run(app, host=fastapi_port_address, port=fastapi_port)
