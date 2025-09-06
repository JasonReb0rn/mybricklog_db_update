#!/bin/bash
set -e

echo "Starting LEGO data update process..."
echo "Environment check:"
echo "SQL_DB_HOST: ${SQL_DB_HOST}"
echo "SQL_DB_USER: ${SQL_DB_USER}"
echo "SQL_DB_NAME: ${SQL_DB_NAME}"
echo "SQL_DB_PORT: ${SQL_DB_PORT}"

# Run the Python script
python3 update_data.py

echo "LEGO data update process completed."
