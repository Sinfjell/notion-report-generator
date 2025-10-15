#!/bin/bash
set -e

# Start uvicorn server
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}




