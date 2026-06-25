#!/bin/bash
set -e

echo "=========================================="
echo " Starting Digital Twin Container Services"
echo "=========================================="

# Start the Isaac Sim Physics Engine in the background
# It will run headlessly and write telemetry JSON files
echo "[1/2] Launching Isaac Sim Physics Engine..."
nohup python /workspace/isaac_twin_sim.py > /workspace/isaac_sim.log 2>&1 &

# Give Isaac Sim a few seconds to initialize Vulkan and create the JSON file
sleep 5

# Start the Streamlit Dashboard in the foreground
# Binding to 0.0.0.0 is required for Docker port forwarding to work
echo "[2/2] Launching Streamlit Dashboard on port 8501..."
python -m streamlit run /workspace/app.py --server.port 8501 --server.address 0.0.0.0
