# Use NVIDIA CUDA base image for GPU and Vulkan support
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

# Set environment variables for non-interactive installs and Isaac Sim
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV WANDB_DISABLED=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    libegl1 \
    libvulkan1 \
    libgl1 \
    curl \
    tmux \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workspace

# Create a virtual environment for Python
RUN python3.10 -m venv /workspace/isaac-env
ENV PATH="/workspace/isaac-env/bin:$PATH"

# Install Streamlit and basic requirements
RUN pip install --upgrade pip && \
    pip install streamlit pandas numpy websocket-client paramiko

# Install NVIDIA Isaac Sim bundle from the NVIDIA PyPI server
# This will take a while as the package is large (~5GB)
RUN pip install "isaacsim[all,extscache]" --extra-index-url https://pypi.nvidia.com

# Copy application files to the container
COPY app.py /workspace/app.py
COPY isaac_twin_sim.py /workspace/isaac_twin_sim.py
COPY start.sh /workspace/start.sh

# Ensure the startup script is executable
RUN chmod +x /workspace/start.sh

# Expose the Streamlit port
EXPOSE 8501

# Run the unified start script when the container launches
ENTRYPOINT ["/workspace/start.sh"]
