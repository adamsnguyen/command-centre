#!/bin/bash

# Run uvicorn with the specified arguments
uvicorn scheduler_api:app --host 0.0.0.0 --port 8001
