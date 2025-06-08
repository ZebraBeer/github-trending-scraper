#!/bin/bash

# Initialize database
echo "Initializing database..."
python3 init_db.py

# Run the app on a different port (54035)
echo "Starting server on port 54035..."
PORT=54035 python3 app.py