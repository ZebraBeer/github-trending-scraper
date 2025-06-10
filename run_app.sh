#!/bin/bash

# Initialize database
echo "Initializing database..."
python3 init_db.py

# Run the app on port 8000 (default)
echo "Starting server on port 8000..."
PORT=8000 python3 app.py