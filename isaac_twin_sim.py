import os
import sys

# Force Matplotlib to use headless Agg backend before importing it
os.environ["MPLBACKEND"] = "Agg"

import json
import time
import random
import subprocess
import matplotlib
import numpy as np

# Accept EULA for Isaac Sim
os.environ["OMNI_KIT_ACCEPT_EULA"] = "YES"

# Import Isaac Sim
try:
    from isaacsim import SimulationApp
    print("SimulationApp imported successfully!")
except Exception as e:
    print(f"Error importing SimulationApp: {e}")
    sys.exit(1)

# Initialize Simulation App in headless mode
print("Initializing headless SimulationApp on GPU...")
simulation_app = SimulationApp({"headless": True})

# Import Isaac Sim Core APIs
try:
    from isaacsim.core.api.world import World
    from isaacsim.core.api.objects import DynamicCuboid, FixedCuboid
    from isaacsim.core.utils.prims import is_prim_path_valid
    print("Isaac Sim Core APIs imported successfully!")
except Exception as e:
    print(f"Error importing Isaac Sim Core APIs: {e}")
    simulation_app.close()
    sys.exit(1)

SHARED_FILE = "/workspace/twin_shared.json"
TELEMETRY_FILE = "/workspace/twin_telemetry.json"

# Helper to get GPU statistics via nvidia-smi
def get_gpu_stats():
    try:
        cmd = "nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.used --format=csv,noheader,nounits"
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
        if output:
            parts = output.split(",")
            return {
                "utilization": float(parts[0].strip()),
                "temperature": float(parts[1].strip()),
                "memory_mb": float(parts[2].strip())
            }
    except Exception:
        pass
    return {"utilization": 25.0, "temperature": 40.0, "memory_mb": 1200}

def main():
    print("Creating Physics World...")
    world = World(stage_units_in_meters=1.0)
    
    # Spawn a local floor plane to avoid external NVIDIA S3/Nucleus downloads
    floor = FixedCuboid(
        prim_path="/World/Floor",
        name="floor",
        position=[0.0, 0.0, -0.05],
        scale=[20.0, 20.0, 0.1],
        color=np.array([0.15, 0.15, 0.15])
    )
    world.scene.add(floor)
    
    # Spawn 10 cuboids representing battery cells on the conveyor
    num_cells = 10
    cells = []
    
    print(f"Spawning {num_cells} rigid body cells on simulated conveyor...")
    for i in range(num_cells):
        prim_path = f"/World/Cell_{i}"
        cell = DynamicCuboid(
            prim_path=prim_path,
            name=f"cell_{i}",
            position=[(i - num_cells/2) * 1.2, 0.0, 0.1],  # spaced along X
            scale=[0.4, 0.6, 0.08],  # dimensions of battery cell
            color=np.array(random.choice([[0.1, 0.6, 0.9], [0.1, 0.8, 0.3], [0.9, 0.6, 0.1]]))
        )
        world.scene.add(cell)
        cells.append(cell)
        
    world.reset()
    print("Simulation setup complete. Starting twin loop...")
    
    # Initialize shared control file if it doesn't exist
    if not os.path.exists(SHARED_FILE):
        default_controls = {
            "web_speed": 50.0,
            "auto_pilot": False,
            "target_min": 280.0,
            "target_max": 320.0,
            "ai_step": 2.0,
            "manual_speed": 50.0,
            "is_running": True,
            "active_anomaly": "none"
        }
        with open(SHARED_FILE, "w") as f:
            json.dump(default_controls, f)
            
    # Process variables tracking
    oven_temp = 120.0
    slurry_visc = 3500.0
    coating_wt = 15.0
    roller_press = 400.0
    wind_tension = 25.0
    
    throughput_counter = 0
    last_throughput_calc = time.time()
    ppm_value = 300.0
    sim_step = 0
    
    while True:
        sim_step += 1
        
        # 1. Read controls from shared file
        try:
            with open(SHARED_FILE, "r") as f:
                controls = json.load(f)
        except Exception:
            controls = {
                "web_speed": 50.0,
                "is_running": True,
                "active_anomaly": "none"
            }
            
        if not controls.get("is_running", True):
            time.sleep(0.5)
            continue
            
        web_speed = controls.get("web_speed", 50.0)
        anomaly = controls.get("active_anomaly", "none")
        
        # 2. Physics logic based on web_speed
        # Map web speed (10 - 80 m/min) to linear velocity (m/s) in physics engine
        # e.g., 60 m/min = 1.0 m/s
        speed_mps = web_speed / 60.0
        
        # Move cells along X axis (conveyor flow)
        for i, cell in enumerate(cells):
            pos, rot = cell.get_world_pose()
            
            # Anomaly impacts: Winding Tension Loss or High speed causes cell slippage/vibration
            vibration = 0.0
            if anomaly == "winding":
                vibration = random.uniform(-0.05, 0.05)
            elif web_speed > 70.0:
                vibration = random.uniform(-0.02, 0.02)
                
            # If cell goes past the end of conveyor (x > 6.0), recycle to start (x = -6.0)
            if pos[0] > 6.0:
                cell.set_world_pose(position=[-6.0, 0.0, 0.1])
                cell.set_linear_velocity([speed_mps, 0.0, 0.0])
                throughput_counter += 1
            else:
                # Keep them moving
                curr_vel = cell.get_linear_velocity()
                target_vel = [speed_mps, vibration, curr_vel[2]]
                cell.set_linear_velocity(target_vel)
                
        # 3. Simulate process variables (Thermal, Fluid, Mechanics)
        # Steady-state recovery
        if oven_temp > 120.0: oven_temp -= 1.0
        if oven_temp < 120.0: oven_temp += 0.5
        if slurry_visc > 3500.0: slurry_visc -= 40.0
        if slurry_visc < 3500.0: slurry_visc += 20.0
        if roller_press < 400.0: roller_press += 3.0
        if roller_press > 400.0: roller_press -= 1.0
        if wind_tension < 25.0: wind_tension += 0.8
        if wind_tension > 25.0: wind_tension -= 0.2
        if coating_wt > 15.0: coating_wt -= 0.08
        if coating_wt < 15.0: coating_wt += 0.03
        
        # Apply anomaly disturbances to process variables
        if anomaly == "mixing":
            slurry_visc = min(6000.0, slurry_visc + 300.0 + random.uniform(-50, 50))
            coating_wt = min(20.0, coating_wt + 0.2)
        elif anomaly == "coating":
            oven_temp = min(170.0, oven_temp + 6.0 + random.uniform(-1, 1))
        elif anomaly == "calendaring":
            roller_press = max(180.0, roller_press - 20.0)
        elif anomaly == "winding":
            wind_tension = max(8.0, wind_tension - 2.5)
            
        # Add normal operational variance
        oven_temp += random.uniform(-0.1, 0.1)
        slurry_visc += random.uniform(-5.0, 5.0)
        coating_wt += random.uniform(-0.02, 0.02)
        roller_press += random.uniform(-1.0, 1.0)
        wind_tension += random.uniform(-0.2, 0.2)
        
        # Step the Isaac Sim physics engine (run 10 steps per twin iteration)
        for _ in range(10):
            world.step(render=False)
            
        # 4. Calculate actual Throughput and Yield
        now = time.time()
        time_elapsed = now - last_throughput_calc
        if time_elapsed >= 2.0:  # recalculate throughput every 2 seconds
            # physical count scaled to ppm
            ppm_value = (throughput_counter / time_elapsed) * 60.0
            throughput_counter = 0
            last_throughput_calc = now
            
        # If speed is too low, throughput matches the physical rate. If normal:
        if anomaly == "winding":
            ppm_value *= 0.5  # Material slack bottleneck
            
        # Calculate thickness deviation and defect rate based on physical forces
        # Low calendaring pressure causes high deviation
        thickness_dev = 2.0 + max(0.0, (400.0 - roller_press) / 25.0) + random.uniform(-0.05, 0.05)
        
        # Defect rate calculation based on speed, oven temp, tension and slurry viscosity
        base_defects = 10.0
        if web_speed > 70.0:
            base_defects += (web_speed - 70.0) * 4.0  # high speed defects
        if oven_temp > 135.0:
            base_defects += (oven_temp - 135.0) * 8.0  # blistering
        if slurry_visc > 4500.0:
            base_defects += 35.0  # uneven coating
        if wind_tension < 15.0:
            base_defects += 50.0  # loose winding scratches
        if anomaly == "vision":
            base_defects += 180.0  # explicit vision defect cluster
            
        defect_rate = max(5.0, base_defects + random.uniform(-2, 2))
        
        # Yield rate based on spec limits
        yield_penalty = 0.0
        if oven_temp > 130.0: yield_penalty += (oven_temp - 130.0) * 0.4
        if thickness_dev > 3.0: yield_penalty += (thickness_dev - 3.0) * 3.0
        if defect_rate > 50.0: yield_penalty += (defect_rate - 50.0) * 0.15
        if wind_tension < 18.0: yield_penalty += (18.0 - wind_tension) * 0.5
        
        yield_rate = max(0.0, min(100.0, 99.8 - yield_penalty + random.uniform(-0.1, 0.1)))
        
        # 5. Fetch GPU stats
        gpu = get_gpu_stats()
        
        # 6. Write telemetry back to JSON file
        telemetry = {
            "web_speed": float(web_speed),
            "cell_throughput": float(ppm_value),
            "yield_rate": float(yield_rate),
            "defect_rate": float(defect_rate),
            "oven_temp": float(oven_temp),
            "slurry_visc": float(slurry_visc),
            "coating_wt": float(coating_wt),
            "roller_press": float(roller_press),
            "thickness_dev": float(thickness_dev),
            "wind_tension": float(wind_tension),
            "sim_step": int(sim_step),
            "gpu_util": float(gpu["utilization"]),
            "gpu_temp": float(gpu["temperature"]),
            "gpu_mem_mb": float(gpu["memory_mb"])
        }
        
        try:
            with open(TELEMETRY_FILE, "w") as f:
                json.dump(telemetry, f)
        except Exception as e:
            print(f"Error writing telemetry: {e}")
            
        # Sleep for a bit to simulate real-time loop speed (~5 Hz refresh rate)
        time.sleep(0.2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Shutting down twin simulation...")
    finally:
        simulation_app.close()
