#!/bin/bash

echo "===== BUILD START ====="

echo "===== Installing dependencies with uv ====="
uv pip install --system -r requirements.txt

echo "===== Collecting static files ====="
python3 manage.py collectstatic --noinput --clear

echo "===== Running migrations ====="
python3 manage.py migrate --noinput

echo "===== BUILD END ====="