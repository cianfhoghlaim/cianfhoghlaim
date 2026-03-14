#!/bin/bash
set -e

# Run the pre-computation script for the default index
# This will check if the visualization exists and compute it if missing (or if cached embeddings are available)
echo "Starting pre-computation check for full index visualization..."
python compute_full_visualization.py

# Execute the main command (CMD from Dockerfile or docker-compose)
echo "Starting application..."
exec "$@"
