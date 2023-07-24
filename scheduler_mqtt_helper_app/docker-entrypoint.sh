#!/bin/bash

# Run uvicorn with the specified arguments
uvicorn scheduler_mqtt_helper:app --host 0.0.0.0 --port 8003

