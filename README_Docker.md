# Battery Twin Simulation - Docker Container

This directory contains everything you need to build and run the complete Battery Digital Twin simulation as a single, portable Docker container. 

Containerizing the application eliminates the need for messy virtual environments, complicated tunneling services (like Cloudflare or Serveo), and manual script executions. 

## 1. Prerequisites
- **Docker** installed on your host machine.
- **NVIDIA GPU** with NVIDIA Container Toolkit (nvidia-docker) installed so the container can access the GPU for Isaac Sim's physics and Vulkan rendering.

## 2. Building the Image
Open a terminal in this directory and run the following command to build the image.

> [!WARNING]  
> The NVIDIA Isaac Sim package is very large (approx 5-6 GB). Depending on your internet speed, the build process may take 10-20 minutes the first time you run it.

```bash
docker build -t twinsim-app .
```

## 3. Running the Container
Once the image is built, you can run it using the following command. This command maps the container's Streamlit port (8501) directly to your host machine's port 8501, and grants the container access to all GPUs.

```bash
docker run --gpus all -p 8501:8501 -d twinsim-app
```

## 4. Accessing the Dashboard
After running the container, wait about 10-15 seconds for the Isaac Sim engine to initialize its headless Vulkan renderer. 

Then, open your web browser and go to:
- **Locally:** `http://localhost:8501`
- **From another machine:** `http://<your-machine-ip>:8501`

### Using with RunPod
If you are deploying this Docker image on a fresh RunPod instance:
1. Push your built image to DockerHub (`docker tag twinsim-app yourusername/twinsim-app`, then `docker push yourusername/twinsim-app`).
2. When creating a new Pod in RunPod, select your custom image (`yourusername/twinsim-app`).
3. Under "Edit Template", set the **Exposed HTTP Ports** to `8501`.
4. RunPod will now give you a direct public URL to port 8501, and everything will "just work"!
