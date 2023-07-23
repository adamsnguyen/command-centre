#!/bin/bash

# Run uvicorn with the specified arguments
uvicorn device_status_checker:app --host 0.0.0.0 --port 8002

