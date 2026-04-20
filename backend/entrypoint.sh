#!/bin/sh
echo "Waiting for Neo4j..."
while ! nc -z db 7687; do
  sleep 0.5
done
echo "Neo4j started"

cd scripts && python3 seed_users.py
cd ../
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
