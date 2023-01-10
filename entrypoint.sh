#!/bin/bash

# * run migrations
cd /usr/src/stratpoll-api/ && alembic upgrade head

# * init platform
python /usr/src/stratpoll-api/src/init_platform.py

gunicorn -w 1 -b 0.0.0.0:8000 -t 0 -k uvicorn.workers.UvicornWorker --threads 8 src.main:app