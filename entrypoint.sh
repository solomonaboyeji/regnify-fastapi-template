#!/bin/bash

# * run migrations
cd /usr/src/stratpoll-api/ && alembic upgrade head

# * init platform
python /usr/src/stratpoll-api/src/init_platform.py

CMD ["hypercorn", "src.main:app", "--workers", "1", "--bind",  "0.0.0.0:8100" ]