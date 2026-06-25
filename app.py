import streamlit as st
import pandas as pd
import time
import random
import json
import os

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Intelligent Battery Twin | NTT DATA",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

SHARED_FILE = "/workspace/twin_shared.json"
TELEMETRY_FILE = "/workspace/twin_telemetry.json"

# ==========================================
# 2. FILE IPC HELPERS
# ==========================================
def read_telemetry():
    if os.path.exists(TELEMETRY_FILE):
        try:
            with open(TELEMETRY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def write_controls(web_speed, auto_pilot, target_min, target_max, ai_step, manual_speed, is_running, active_anomaly):
    try:
        controls = {
            "web_speed": float(web_speed),
            "auto_pilot": bool(auto_pilot),
            "target_min": float(target_min),
            "target_max": float(target_max),
            "ai_step": float(ai_step),
            "manual_speed": float(manual_speed),
            "is_running": bool(is_running),
            "active_anomaly": str(active_anomaly)
        }
        with open(SHARED_FILE, "w") as f:
            json.dump(controls, f)
    except Exception:
        pass

# ==========================================
# 3. STATE MANAGEMENT & DATA WARMUP
# ==========================================
def generate_ideal_history():
    """Pre-fills the charts with 40 seconds of nominal, steady-state data so graphs aren't blank on load."""
    history = []
    now = time.time()
    for i in range(40, 0, -1):
        t = time.strftime("%H:%M:%S", time.localtime(now - i))
        history.append({
            "Time": t,
            "Yield Rate (%)": 99.5 + random.uniform(-0.1, 0.1),
            "Throughput (ppm)": 300.0 + random.uniform(-2.0, 2.0),
            "Web Speed (m/min)": 50.0,
            "Oven Temp (°C)": 120.0 + random.uniform(-0.5, 0.5),
            "Thickness Dev (µm)": 2.0 + random.uniform(-0.1, 0.1),
            "Slurry Visc (cP)": 3500.0 + random.uniform(-10.0, 10.0),
            "Coating Wt (mg/cm²)": 15.0 + random.uniform(-0.05, 0.05),
            "Roller Press (kN)": 400.0 + random.uniform(-1.0, 1.0),
            "Defect Rate (ppm)": 10.0 + random.uniform(-2.0, 2.0),
            "Wind Tension (N)": 25.0 + random.uniform(-0.2, 0.2)
        })
    return history

def init_state(key: str, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value

# State initialization moved inside main() to prevent module-level execution on startup

# ==========================================
# 4. CORE LOGIC & SIMULATION
# ==========================================
def log_event(level: str, message: str):
    timestamp = time.strftime("%H:%M:%S")
    log_entry = {"time": timestamp, "level": level, "message": message}
    st.session_state.agent_log.insert(0, log_entry)
    if len(st.session_state.agent_log) > 6: st.session_state.agent_log.pop()
    st.session_state.all_logs.insert(0, log_entry)
    if len(st.session_state.all_logs) > 100: st.session_state.all_logs.pop()

# --- 5 Station-Specific Disturbance Injectors ---
def inject_anomaly(anomaly_type):
    st.session_state.active_anomaly = anomaly_type
    if anomaly_type == "mixing":
        st.session_state.slurry_visc += 1500.0
        st.session_state.coating_wt += 3.5
        st.session_state.yield_rate -= 4.0
        log_event("system", "🧪 STAGE 1 ANOMALY: Severe Slurry Viscosity Spike. Solvent ratio imbalance detected.")
    elif anomaly_type == "coating":
        st.session_state.oven_temp += 30.0
        st.session_state.thickness_dev += 2.0
        st.session_state.yield_rate -= 8.0
        log_event("system", "🔥 STAGE 2 ANOMALY: Coating Oven Thermal Drift. Heating element #4 runaway.")
    elif anomaly_type == "calendaring":
        st.session_state.roller_press -= 150.0
        st.session_state.thickness_dev += 5.5
        st.session_state.yield_rate -= 12.0
        log_event("system", "⚙️ STAGE 3 ANOMALY: Calendaring Hydraulic Pressure Loss. Foil compression failing.")
    elif anomaly_type == "vision":
        st.session_state.defect_rate += 200.0
        st.session_state.yield_rate -= 25.0
        log_event("system", "🚨 STAGE 4 ANOMALY: Vision System flags massive surface defect cluster (Pinholes/Scratches).")
    elif anomaly_type == "winding":
        st.session_state.wind_tension -= 18.0
        st.session_state.web_speed *= 0.5
        log_event("system", "🧵 STAGE 5 ANOMALY: Winder Tension Loss. Material slack causing severe bottleneck.")
    elif anomaly_type == "none":
        st.session_state.active_anomaly = "none"
        log_event("success", "✅ System anomaly cleared. Resuming nominal conditions.")

def apply_scenario(scenario_name):
    if scenario_name == "1. Nominal Operations (Steady State)":
        st.session_state.is_running = True
        st.session_state.auto_pilot = False
        st.session_state.web_speed = 50.0
        st.session_state.manual_speed = 50.0
        st.session_state.oven_temp = 120.0
        st.session_state.thickness_dev = 2.0
        st.session_state.slurry_visc = 3500.0
        st.session_state.roller_press = 400.0
        st.session_state.defect_rate = 10.0
        st.session_state.wind_tension = 25.0
        st.session_state.coating_wt = 15.0
        st.session_state.yield_rate = 99.5
        st.session_state.active_anomaly = "none"
        log_event("system", "📖 DEMO: Initialized Nominal Operations (Steady State). System performing optimally.")
        
    elif scenario_name == "2. Autopilot Yield Optimization":
        st.session_state.is_running = True
        st.session_state.auto_pilot = True
        st.session_state.target_min = 280.0
        st.session_state.target_max = 320.0
        st.session_state.ai_step = 2.0
        st.session_state.active_anomaly = "none"
        log_event("action", "📖 DEMO: Autopilot Optimization enabled. Agent dynamically balancing line speed for max throughput.")
        
    elif scenario_name == "3. Slurry Viscosity Crisis (Mixing Anomaly)":
        st.session_state.is_running = True
        st.session_state.auto_pilot = True
        st.session_state.active_anomaly = "mixing"
        log_event("system", "🧪 DEMO: Slurry Viscosity Anomaly injected. Autopilot activating solvent micro-dosing...")
        
    elif scenario_name == "4. Thermal Runaway Mitigation (Coating Anomaly)":
        st.session_state.is_running = True
        st.session_state.auto_pilot = True
        st.session_state.active_anomaly = "coating"
        log_event("system", "🔥 DEMO: Oven Temperature Runaway injected. Autopilot overriding PID controllers and adjusting line speed...")
        
    elif scenario_name == "5. Calendaring Pressure Loss (Mechanical Anomaly)":
        st.session_state.is_running = True
        st.session_state.auto_pilot = True
        st.session_state.active_anomaly = "calendaring"
        log_event("system", "⚙️ DEMO: Calendaring pressure loss injected. Autopilot ramping hydraulic pump speed...")
        
    elif scenario_name == "6. Quality Defect Lot Isolation (Vision Anomaly)":
        st.session_state.is_running = True
        st.session_state.auto_pilot = True
        st.session_state.active_anomaly = "vision"
        log_event("system", "🚨 DEMO: Surface defect cluster detected. Autopilot isolating suspect lots and reducing web speed...")

def get_predictions():
    predictions = []
    
    # 1. Oven Temp / Coating Blistering Prediction
    if st.session_state.oven_temp > 135:
        predictions.append({
            "title": "🔥 Anode Coating Blistering Risk",
            "status": "CRITICAL RISK (92%)",
            "color": "#ef4444",
            "time": "Est. 15s to defect",
            "reason": f"Oven temperature is critical ({st.session_state.oven_temp:.1f}°C). Evaporation rate of NMP solvent exceeds threshold, creating micro-bubbles.",
            "remediation": "Autopilot overriding thermal elements. Slowing web speed to increase residence time."
        })
    elif st.session_state.oven_temp > 125:
        predictions.append({
            "title": "🔥 Coating Thermal Drift",
            "status": "WARNING RISK (45%)",
            "color": "#f59e0b",
            "time": "Est. 2m to defect",
            "reason": f"Oven temperature ({st.session_state.oven_temp:.1f}°C) is drifting above nominal 120°C.",
            "remediation": "PID tuning calibration recommended."
        })

    # 2. Viscosity / Coating Thickness
    if st.session_state.slurry_visc > 4500:
        predictions.append({
            "title": "🧪 Slurry Nozzle Clogging Risk",
            "status": "CRITICAL RISK (88%)",
            "color": "#ef4444",
            "time": "Est. 30s to nozzle clog",
            "reason": f"Slurry viscosity is extremely high ({st.session_state.slurry_visc:.0f} cP), leading to uneven mass distribution and nozzle backpressure.",
            "remediation": "Injecting solvent micro-dose to mixing vat."
        })
    elif st.session_state.slurry_visc > 4000:
        predictions.append({
            "title": "🧪 Flow Rate Instability",
            "status": "WARNING RISK (50%)",
            "color": "#f59e0b",
            "time": "Est. 90s to out-of-spec",
            "reason": f"Viscosity ({st.session_state.slurry_visc:.0f} cP) exceeds normal envelope.",
            "remediation": "Monitor solvent ratio controls."
        })

    # 3. Calendaring / Density
    if st.session_state.roller_press < 320:
        predictions.append({
            "title": "⚙️ Calendaring Porosity Defect",
            "status": "CRITICAL RISK (95%)",
            "color": "#ef4444",
            "time": "Est. 10s to out-of-spec",
            "reason": f"Hydraulic press pressure is too low ({st.session_state.roller_press:.0f} kN). Active material density will fail target porosity spec ({st.session_state.thickness_dev:.1f}µm dev).",
            "remediation": "Increase hydraulic pump RPM."
        })
    elif st.session_state.roller_press < 370:
        predictions.append({
            "title": "⚙️ Low Roll Compression",
            "status": "WARNING RISK (40%)",
            "color": "#f59e0b",
            "time": "Est. 1m to defect",
            "reason": f"Pressure ({st.session_state.roller_press:.0f} kN) is below optimal 400 kN.",
            "remediation": "Hydraulic pressure regulation alert."
        })

    # 4. Tension / Telescoping
    if st.session_state.wind_tension < 12:
        predictions.append({
            "title": "🧵 Roll Telescoping & Slack",
            "status": "CRITICAL RISK (90%)",
            "color": "#ef4444",
            "time": "Est. 20s to telescoping",
            "reason": f"Wind tension has collapsed ({st.session_state.wind_tension:.1f} N). Loose core winding will cause telescoping defects in the final cell roll.",
            "remediation": "Ramp tension servo motor torque."
        })
    elif st.session_state.wind_tension < 20:
        predictions.append({
            "title": "🧵 Tension Slack Threat",
            "status": "WARNING RISK (35%)",
            "color": "#f59e0b",
            "time": "Est. 3m to roll slippage",
            "reason": f"Winding tension ({st.session_state.wind_tension:.1f} N) is below nominal 25 N.",
            "remediation": "Tension controller auto-adjustment in progress."
        })

    # 5. Throughput Bottleneck
    if st.session_state.cell_throughput < st.session_state.target_min:
        predictions.append({
            "title": "📦 Throughput Bottleneck Alert",
            "status": "WARNING RISK (75%)",
            "color": "#f59e0b",
            "time": "Active bottleneck",
            "reason": f"Throughput ({st.session_state.cell_throughput:.0f} ppm) is below target minimum ({st.session_state.target_min:.0f} ppm) due to slow line speed.",
            "remediation": "Autopilot ramping web speed (+2 m/min per cycle)."
        })

    # 6. Default Nominal state if empty
    if not predictions:
        predictions.append({
            "title": "✅ Health Status: Nominal",
            "status": "0% Failure Risk",
            "color": "#10b981",
            "time": "Stable operations",
            "reason": "All 10 physical process variables are fully within their nominal target tolerances.",
            "remediation": "Maintain current web speed of 50.0 m/min."
        })
        
    return predictions

def run_simulation_step():
    if not st.session_state.is_running: return

    # --- 1. ATTEMPT READ FROM ISAAC SIM ---
    telemetry = read_telemetry()
    
    if telemetry and (time.time() - os.path.getmtime(TELEMETRY_FILE) < 5.0):
        # We have fresh real-time physics data from NVIDIA Isaac Sim!
        st.session_state.using_isaac_sim = True
        
        # Pull simulation values directly
        st.session_state.web_speed = telemetry.get("web_speed", 50.0)
        st.session_state.cell_throughput = telemetry.get("cell_throughput", 300.0)
        st.session_state.yield_rate = telemetry.get("yield_rate", 99.5)
        st.session_state.defect_rate = telemetry.get("defect_rate", 10.0)
        st.session_state.oven_temp = telemetry.get("oven_temp", 120.0)
        st.session_state.slurry_visc = telemetry.get("slurry_visc", 3500.0)
        st.session_state.coating_wt = telemetry.get("coating_wt", 15.0)
        st.session_state.roller_press = telemetry.get("roller_press", 400.0)
        st.session_state.thickness_dev = telemetry.get("thickness_dev", 2.0)
        st.session_state.wind_tension = telemetry.get("wind_tension", 25.0)
        
        # Pull GPU variables
        st.session_state.gpu_util = telemetry.get("gpu_util", 0.0)
        st.session_state.gpu_temp = telemetry.get("gpu_temp", 0.0)
        st.session_state.gpu_mem = telemetry.get("gpu_mem", 0.0)
        st.session_state.sim_step = telemetry.get("sim_step", 0)
        
        # Write agent commands back to simulator if Autopilot is enabled
        if st.session_state.auto_pilot:
            tp = st.session_state.cell_throughput
            step = st.session_state.ai_step
            new_speed = st.session_state.web_speed
            
            # Autopilot logic adjusts line speed based on telemetry
            if st.session_state.defect_rate > 100 or st.session_state.thickness_dev > 5.0:
                new_speed = max(10.0, st.session_state.web_speed - (step * 4))
                log_event("critical", "Defects High. ACTION: Slowing line speed.")
            elif st.session_state.slurry_visc > 4500:
                log_event("action", "High Viscosity. ACTION: Activating automated NMP solvent micro-dosing.")
            elif st.session_state.oven_temp > 135:
                new_speed = max(10.0, st.session_state.web_speed - (step * 2))
                log_event("critical", f"Temp Drift ({st.session_state.oven_temp:.1f}°C). ACTION: Overriding PID controllers.")
            elif st.session_state.roller_press < 300:
                log_event("action", "Low Calendaring Pressure. ACTION: Ramping hydraulic pump RPM.")
            elif st.session_state.wind_tension < 15:
                log_event("critical", "Slack Detected. ACTION: Recalibrating winding servo torque.")
            elif tp < st.session_state.target_min:
                new_speed = min(80.0, st.session_state.web_speed + step)
                log_event("action", f"Queue clearance. ACTION: Increasing line speed (+{step} m/min).")
            elif tp > st.session_state.target_max:
                new_speed = max(10.0, st.session_state.web_speed - step)
                log_event("action", f"Queue limit reached. ACTION: Reducing speed (-{step} m/min).")
                
            st.session_state.web_speed = new_speed
            
        else:
            st.session_state.web_speed = st.session_state.manual_speed
            
        # Push controls to shared file
        write_controls(
            web_speed=st.session_state.web_speed,
            auto_pilot=st.session_state.auto_pilot,
            target_min=st.session_state.target_min,
            target_max=st.session_state.target_max,
            ai_step=st.session_state.ai_step,
            manual_speed=st.session_state.manual_speed,
            is_running=st.session_state.is_running,
            active_anomaly=st.session_state.active_anomaly
        )
        
    else:
        # --- 2. FALLBACK TO LOCAL MOCKUP SIMULATION ---
        st.session_state.using_isaac_sim = False
        st.session_state.cell_throughput = (st.session_state.web_speed * 6) + random.uniform(-5.0, 5.0)
        
        # Natural variance / decay for recovery
        if st.session_state.oven_temp > 120: st.session_state.oven_temp -= 1.5
        if st.session_state.thickness_dev > 2.0: st.session_state.thickness_dev -= 0.3
        if st.session_state.defect_rate > 10.0: st.session_state.defect_rate -= 5.0
        if st.session_state.slurry_visc > 3500.0: st.session_state.slurry_visc -= 50.0
        if st.session_state.roller_press < 400.0: st.session_state.roller_press += 5.0
        if st.session_state.wind_tension < 25.0: st.session_state.wind_tension += 1.0
        if st.session_state.coating_wt > 15.0: st.session_state.coating_wt -= 0.1
        
        st.session_state.slurry_visc += random.uniform(-10.0, 10.0)
        st.session_state.coating_wt += random.uniform(-0.05, 0.05)
        st.session_state.roller_press += random.uniform(-2.0, 2.0)
        st.session_state.wind_tension += random.uniform(-0.5, 0.5)
        
        yield_penalty = 0
        if st.session_state.oven_temp > 130: yield_penalty += (st.session_state.oven_temp - 130) * 0.5
        if st.session_state.thickness_dev > 3.0: yield_penalty += (st.session_state.thickness_dev - 3.0) * 2.5
        if st.session_state.defect_rate > 50: yield_penalty += 4.0
        if st.session_state.roller_press < 350: yield_penalty += 2.0
        
        st.session_state.yield_rate = max(0.0, min(100.0, 99.8 - yield_penalty + random.uniform(-0.2, 0.2)))
        
        # Autopilot Local Control Loop
        if st.session_state.auto_pilot:
            tp = st.session_state.cell_throughput
            step = st.session_state.ai_step
            
            if st.session_state.defect_rate > 100 or st.session_state.thickness_dev > 5.0:
                st.session_state.web_speed = max(10.0, st.session_state.web_speed - (step * 4))
                log_event("critical", "Defects High. ACTION: Slowing line speed.")
            elif st.session_state.slurry_visc > 4500:
                log_event("action", "High Viscosity. ACTION: Activating automated NMP solvent micro-dosing.")
            elif st.session_state.oven_temp > 135:
                st.session_state.web_speed = max(10.0, st.session_state.web_speed - (step * 2))
                log_event("critical", f"Temp Drift ({st.session_state.oven_temp:.1f}°C). ACTION: Overriding PID controllers Zone 4.")
            elif st.session_state.roller_press < 300:
                log_event("action", "Low Calendaring Pressure. ACTION: Ramping hydraulic pump RPM.")
            elif st.session_state.wind_tension < 15:
                log_event("critical", "Slack Detected. ACTION: Recalibrating winding servo motors.")
            elif tp < st.session_state.target_min:
                st.session_state.web_speed = min(80.0, st.session_state.web_speed + step)
                log_event("action", f"Queue clearance. ACTION: Increasing line speed (+{step} m/min).")
            elif tp > st.session_state.target_max:
                st.session_state.web_speed = max(10.0, st.session_state.web_speed - step)
                log_event("action", f"Queue limit reached. ACTION: Reducing speed to rebalance (-{step} m/min).")
        else:
            st.session_state.web_speed = st.session_state.manual_speed

    # Append to History for graphing
    st.session_state.history.append({
        "Time": time.strftime("%H:%M:%S"),
        "Yield Rate (%)": st.session_state.yield_rate,
        "Throughput (ppm)": st.session_state.cell_throughput,
        "Web Speed (m/min)": st.session_state.web_speed,
        "Oven Temp (°C)": st.session_state.oven_temp,
        "Thickness Dev (µm)": st.session_state.thickness_dev,
        "Slurry Visc (cP)": st.session_state.slurry_visc,
        "Coating Wt (mg/cm²)": st.session_state.coating_wt,
        "Roller Press (kN)": st.session_state.roller_press,
        "Defect Rate (ppm)": st.session_state.defect_rate,
        "Wind Tension (N)": st.session_state.wind_tension
    })
    if len(st.session_state.history) > 40: 
        st.session_state.history.pop(0)

# ==========================================
# 5. UI COMPONENTS (Animations & Layouts)
# ==========================================
def render_factory_animation():
    speed, temp, thick = st.session_state.web_speed, st.session_state.oven_temp, st.session_state.thickness_dev
    anim_dur = max(0.2, 20.0 / speed) if (speed > 5.0 and st.session_state.is_running) else 0
    dur_str = f"{anim_dur:.2f}s"
    dur_fast = f"{anim_dur * 0.5:.2f}s"
    dur_slow = f"{anim_dur * 2:.2f}s"
    
    oven_color = "#ef4444" if temp > 135 else ("#f97316" if temp > 125 else "#3b82f6")
    laser_color = "#ef4444" if st.session_state.defect_rate > 50 else "#22c55e"
    belt_color = "#ef4444" if thick > 5.0 else "#8b5cf6"
    press_color = "#ef4444" if st.session_state.roller_press < 350 else "#94a3b8"
    
    svg_code = f"""
    <svg viewBox="0 0 1200 180" width="100%" xmlns="http://www.w3.org/2000/svg" style="background-color: #0f172a; border-radius: 10px; border: 1px solid #334155; margin-bottom: 20px;">
        <line x1="0" y1="140" x2="1200" y2="140" stroke="#1e293b" stroke-width="12" />
        <line x1="0" y1="140" x2="1200" y2="140" stroke="#475569" stroke-width="12" stroke-dasharray="30 15">
            {f'<animate attributeName="stroke-dashoffset" from="45" to="0" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </line>
        <line x1="140" y1="110" x2="1000" y2="110" stroke="{belt_color}" stroke-width="6" stroke-dasharray="60 10" opacity="0.9">
            {f'<animate attributeName="stroke-dashoffset" from="70" to="0" dur="{dur_fast}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </line>
        
        <text x="50" y="20" fill="#64748b" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">RAW MATERIALS</text>
        <path d="M 20 30 L 80 30 L 60 70 L 40 70 Z" fill="#475569" stroke="#94a3b8" stroke-width="2"/>
        <rect x="45" y="70" width="10" height="20" fill="#475569" />
        <circle cx="50" cy="80" r="4" fill="#cbd5e1">
             {f'<animate attributeName="cy" from="75" to="100" dur="0.8s" repeatCount="indefinite" />' if anim_dur > 0 else ''}
             {f'<animate attributeName="opacity" values="1;0" dur="0.8s" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </circle>
        
        <text x="140" y="30" fill="#cbd5e1" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">1. SLURRY MIXING</text>
        <path d="M 100 50 L 100 130 Q 140 150 180 130 L 180 50 Z" fill="#1e293b" stroke="#94a3b8" stroke-width="4" />
        <g stroke="#64748b" stroke-width="4">
            <line x1="140" y1="40" x2="140" y2="120" />
            <line x1="110" y1="100" x2="170" y2="100">
                {f'<animateTransform attributeName="transform" type="rotate" from="0 140 100" to="360 140 100" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
            </line>
        </g>
        
        <text x="360" y="30" fill="#cbd5e1" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">2. COATING &amp; OVEN</text>
        <rect x="240" y="50" width="240" height="80" fill="#1e293b" stroke="{oven_color}" stroke-width="4" rx="4" />
        <path d="M 280 100 Q 300 80 320 100 T 360 100" fill="none" stroke="{oven_color}" stroke-width="3" opacity="0.6">
            {f'<animate attributeName="opacity" values="0.2;1;0.2" dur="{dur_slow}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </path>
        <path d="M 340 100 Q 360 80 380 100 T 420 100" fill="none" stroke="{oven_color}" stroke-width="3" opacity="0.6">
            {f'<animate attributeName="opacity" values="1;0.2;1" dur="{dur_slow}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </path>
        
        <text x="580" y="30" fill="#cbd5e1" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">3. CALENDARING</text>
        <circle cx="580" cy="75" r="30" fill="#334155" stroke="{press_color}" stroke-width="4">
            {f'<animateTransform attributeName="transform" type="rotate" from="0 580 75" to="-360 580 75" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </circle>
        <circle cx="580" cy="145" r="30" fill="#334155" stroke="{press_color}" stroke-width="4">
            {f'<animateTransform attributeName="transform" type="rotate" from="0 580 145" to="360 580 145" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </circle>
        <line x1="580" y1="45" x2="580" y2="105" stroke="#1e293b" stroke-width="4">
            {f'<animateTransform attributeName="transform" type="rotate" from="0 580 75" to="-360 580 75" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </line>
        <line x1="580" y1="115" x2="580" y2="175" stroke="#1e293b" stroke-width="4">
            {f'<animateTransform attributeName="transform" type="rotate" from="0 580 145" to="360 580 145" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </line>
        
        <text x="780" y="30" fill="#cbd5e1" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">4. VISION SCAN</text>
        <path d="M 730 120 L 730 60 L 830 60 L 830 120" fill="none" stroke="#475569" stroke-width="6" />
        <line x1="780" y1="60" x2="780" y2="110" stroke="{laser_color}" stroke-width="4" opacity="0.8">
            {f'<animate attributeName="x1" values="740;820;740" dur="1.2s" repeatCount="indefinite" />' if anim_dur > 0 else ''}
            {f'<animate attributeName="x2" values="740;820;740" dur="1.2s" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </line>
        
        <text x="960" y="30" fill="#cbd5e1" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">5. CELL WINDING</text>
        <rect x="880" y="50" width="160" height="80" fill="#1e293b" stroke="#3b82f6" stroke-width="4" rx="8" />
        <circle cx="925" cy="90" r="22" fill="none" stroke="#94a3b8" stroke-width="6" stroke-dasharray="15 8">
            {f'<animateTransform attributeName="transform" type="rotate" from="0 925 90" to="360 925 90" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </circle>
        <circle cx="995" cy="90" r="22" fill="none" stroke="#94a3b8" stroke-width="6" stroke-dasharray="15 8">
            {f'<animateTransform attributeName="transform" type="rotate" from="360 995 90" to="0 995 90" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
        </circle>
        
        <text x="1110" y="30" fill="#22c55e" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle">OUTPUT CELLS</text>
        <line x1="1040" y1="120" x2="1200" y2="120" stroke="#1e293b" stroke-width="6" />
        <g>
            {f'<animateTransform attributeName="transform" type="translate" from="0 0" to="80 0" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
            <rect x="1050" y="90" width="15" height="28" fill="#0ea5e9" rx="2" />
            <rect x="1054" y="86" width="7" height="4" fill="#cbd5e1" />
        </g>
        <g>
            {f'<animateTransform attributeName="transform" type="translate" from="0 0" to="80 0" dur="{dur_str}" repeatCount="indefinite" />' if anim_dur > 0 else ''}
            <rect x="1130" y="90" width="15" height="28" fill="#0ea5e9" rx="2" />
            <rect x="1134" y="86" width="7" height="4" fill="#cbd5e1" />
        </g>
    </svg>
    """
    
    clean_svg_code = "\n".join([line for line in svg_code.split("\n") if line.strip() != ""])
    st.markdown(clean_svg_code, unsafe_allow_html=True)


# ==========================================
# 6. MAIN APPLICATION RENDER
# ==========================================
def main():
    # Initialize session states safely inside script execution context
    init_state('web_speed', 50.0)
    init_state('cell_throughput', 300.0)
    init_state('oven_temp', 120.0)
    init_state('thickness_dev', 2.0)
    init_state('yield_rate', 99.5)
    init_state('slurry_visc', 3500.0)
    init_state('coating_wt', 15.0)
    init_state('roller_press', 400.0)
    init_state('defect_rate', 10.0)
    init_state('wind_tension', 25.0)

    # GPU Metrics
    init_state('gpu_util', 0.0)
    init_state('gpu_temp', 0.0)
    init_state('gpu_mem', 0.0)
    init_state('sim_step', 0)
    init_state('using_isaac_sim', False)

    # Initialize history
    init_state('history', generate_ideal_history())            

    # Digital Twin / AI States
    init_state('auto_pilot', False)
    init_state('target_min', 280.0)
    init_state('target_max', 320.0)
    init_state('ai_step', 2.0)
    init_state('manual_speed', 50.0)
    init_state('is_running', True)       
    init_state('active_anomaly', 'none')

    # Log States
    initial_log = {
        "time": time.strftime("%H:%M:%S"), 
        "level": "system", 
        "message": "AWS Edge Ingestion: PLC streams connected."
    }
    init_state('agent_log', [initial_log])
    init_state('all_logs', [initial_log])

    run_simulation_step()
    
    # --- SIDEBAR CONTROLS ---
    with st.sidebar:
        st.header("⚙️ Operational Controls")
        st.session_state.is_running = st.toggle("▶️ Run Simulation", value=st.session_state.is_running)
        
        st.divider()
        st.subheader("📖 Demo Guiding Scenarios")
        scenario_options = [
            "Select Scenario...",
            "1. Nominal Operations (Steady State)",
            "2. Autopilot Yield Optimization",
            "3. Slurry Viscosity Crisis (Mixing Anomaly)",
            "4. Thermal Runaway Mitigation (Coating Anomaly)",
            "5. Calendaring Pressure Loss (Mechanical Anomaly)",
            "6. Quality Defect Lot Isolation (Vision Anomaly)"
        ]
        selected_scenario = st.selectbox("Trigger preset scenarios for demo:", scenario_options, index=0)
        
        if "last_scenario" not in st.session_state:
            st.session_state.last_scenario = "Select Scenario..."
            
        if selected_scenario != st.session_state.last_scenario:
            st.session_state.last_scenario = selected_scenario
            if selected_scenario != "Select Scenario...":
                apply_scenario(selected_scenario)
                st.rerun()

        st.divider()
        st.subheader("🧠 Digital Twin / Agent")
        auto = st.toggle("Enable Auto-Pilot", key="auto_pilot", help="AI autonomously adjusts line speed and fixes anomalies.")
        st.session_state.manual_speed = st.slider("Manual Web Speed (m/min)", 10.0, 80.0, st.session_state.web_speed, step=5.0, disabled=auto)
        
        st.divider()
        st.subheader("🎯 Throughput Targets")
        c1, c2 = st.columns(2)
        with c1: st.number_input("Target Min", min_value=150.0, max_value=300.0, key="target_min", step=10.0)
        with c2: st.number_input("Target Max", min_value=250.0, max_value=400.0, key="target_max", step=10.0)
        
        st.divider()
        st.subheader("🚨 Edge IoT Ingestion (Anomalies)")
        st.caption("Trigger these to demonstrate AI response protocols:")
        if st.button("🧪 1. Mixing: Viscosity Spike", use_container_width=True): inject_anomaly("mixing")
        if st.button("🔥 2. Coating: Oven Drift", use_container_width=True): inject_anomaly("coating")
        if st.button("⚙️ 3. Calendaring: Pressure Drop", use_container_width=True): inject_anomaly("calendaring")
        if st.button("📷 4. Vision: Defect Cluster", use_container_width=True): inject_anomaly("vision")
        if st.button("🧵 5. Winding: Tension Loss", use_container_width=True): inject_anomaly("winding")
        if st.button("🟢 Resolve Anomalies / Reset", use_container_width=True): inject_anomaly("none")

    render_dashboard_body()



@st.fragment(run_every="1.0s")
def render_dashboard_body():
    run_simulation_step()
    # --- HEADER & BANNER (Full-width top sticky banner) ---
    import base64
    def get_image_base64(path):
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return ""
    img_b64 = get_image_base64("bnr_hd_cropped.png")

    st.markdown(f"""
    <style>
    @keyframes laserSweep {{
        0% {{ transform: translateY(0px); opacity: 0.3; }}
        50% {{ transform: translateY(117px); opacity: 1.0; }}
        100% {{ transform: translateY(0px); opacity: 0.3; }}
    }}
    @keyframes neonPulse {{
        0%, 100% {{ border-color: #1e293b; box-shadow: inset 0 0 10px rgba(59, 130, 246, 0.1), 0 0 5px rgba(59, 130, 246, 0.1); }}
        50% {{ border-color: #3b82f6; box-shadow: inset 0 0 20px rgba(96, 165, 250, 0.3), 0 0 10px rgba(96, 165, 250, 0.2); }}
    }}
    @keyframes rotateCW {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    @keyframes rotateCCW {{
        0% {{ transform: rotate(360deg); }}
        100% {{ transform: rotate(0deg); }}
    }}
    @keyframes gridPulse {{
        0%, 100% {{ opacity: 0.05; }}
        50% {{ opacity: 0.2; }}
    }}
    
    .animated-banner-hud {{
        position: fixed;
        top: 3.75rem;
        left: 0;
        width: 100vw;
        height: 120px;
        z-index: 999999;
        background: url("data:image/png;base64,{img_b64}") no-repeat center center;
        background-size: 100% 100%;
        border-bottom: 2px solid #3b82f6;
        margin-bottom: 0;
        overflow: hidden;
        animation: neonPulse 6s infinite ease-in-out;
        transition: left 0.3s ease, width 0.3s ease !important;
    }}

    /* When the sidebar is expanded, limit the banner to the main page only */
    body:has([data-testid="stSidebar"][aria-expanded="true"]) .animated-banner-hud {{
        left: 21rem !important;
        width: calc(100vw - 21rem) !important;
    }}
    
    .hud-grid {{
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            linear-gradient(to right, rgba(59, 130, 246, 0.08) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(59, 130, 246, 0.08) 1px, transparent 1px);
        background-size: 30px 30px;
        animation: gridPulse 6s infinite ease-in-out;
        pointer-events: none;
    }}
    
    .animated-banner-hud-scanline {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 3px;
        background: linear-gradient(to right, transparent, rgba(59, 130, 246, 0.2), #60a5fa, rgba(59, 130, 246, 0.2), transparent);
        box-shadow: 0 0 10px 2px rgba(96, 165, 250, 0.6);
        animation: laserSweep 4s infinite ease-in-out;
        pointer-events: none;
    }}
    
    /* Spinning HUD Rings */
    .hud-ring-left-1, .hud-ring-left-2, .hud-ring-right-1, .hud-ring-right-2 {{
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
        opacity: 0.35;
    }}
    
    .hud-ring-left-1 {{
        width: 140px;
        height: 140px;
        left: 20px;
        top: -10px;
        border: 2px dashed rgba(59, 130, 246, 0.25);
        animation: rotateCW 25s infinite linear;
    }}
    .hud-ring-left-2 {{
        width: 100px;
        height: 100px;
        left: 40px;
        top: 10px;
        border: 1px dotted rgba(96, 165, 250, 0.35);
        animation: rotateCCW 15s infinite linear;
    }}
    
    .hud-ring-right-1 {{
        width: 160px;
        height: 160px;
        right: 40px;
        top: -20px;
        border: 2px dashed rgba(59, 130, 246, 0.25);
        animation: rotateCW 30s infinite linear;
    }}
    .hud-ring-right-2 {{
        width: 120px;
        height: 120px;
        right: 60px;
        top: 0px;
        border: 1.5px dotted rgba(96, 165, 250, 0.45);
        animation: rotateCCW 18s infinite linear;
    }}
    
    [data-testid="stAppHeader"], [data-testid="stHeader"] {{
        background-color: #0f172a !important;
        z-index: 1000000 !important;
        pointer-events: auto !important;
        display: flex !important;
    }}
    
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {{
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid #334155 !important;
        color: #3b82f6 !important;
        border-radius: 4px !important;
        z-index: 1000001 !important;
        pointer-events: auto !important;
        transition: all 0.3s ease !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover {{
        border-color: #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.5) !important;
    }}
 
    [data-testid="stMain"] > div {{
        padding-top: 190px !important;
    }}
    </style>
    <div class="animated-banner-hud">
        <div class="hud-grid"></div>
        <div class="hud-ring-left-1"></div>
        <div class="hud-ring-left-2"></div>
        <div class="hud-ring-right-1"></div>
        <div class="hud-ring-right-2"></div>
        <div class="animated-banner-hud-scanline"></div>
    </div>
    """, unsafe_allow_html=True)

    # --- ENGINE STATUS HUD ---
    if st.session_state.using_isaac_sim:
        sim_badge = f"""
        <div style='display: flex; gap: 10px; margin-bottom: 20px; align-items: center; background-color: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 6px; padding: 10px 15px;'>
            <div style='width: 10px; height: 10px; background-color: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e; animation: pulse 1.5s infinite;'></div>
            <div style='font-size: 0.85rem; color: #22c55e; font-weight: bold;'>NVIDIA ISAAC SIM ACTIVE (GPU-ACCELERATED) | Steps: {st.session_state.sim_step}</div>
            <div style='font-size: 0.8rem; color: #cbd5e1; margin-left: auto;'><b>GPU Load:</b> {st.session_state.gpu_util:.1f}% | <b>Temp:</b> {st.session_state.gpu_temp:.1f}°C | <b>VRAM:</b> {st.session_state.gpu_mem:.0f} MB</div>
        </div>
        """
        st.markdown(sim_badge, unsafe_allow_html=True)
    else:
        fallback_badge = """
        <div style='display: flex; gap: 10px; margin-bottom: 20px; align-items: center; background-color: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; border-radius: 6px; padding: 10px 15px;'>
            <div style='width: 10px; height: 10px; background-color: #f59e0b; border-radius: 50%;'></div>
            <div style='font-size: 0.85rem; color: #f59e0b; font-weight: bold;'>LOCAL EMULATOR ACTIVE</div>
            <div style='font-size: 0.8rem; color: #cbd5e1; margin-left: auto;'>Start <span style='font-family: monospace; background: #1e293b; padding: 2px 4px; border-radius: 3px;'>isaac_twin_sim.py</span> on the pod to stream real-time physics telemetry.</div>
        </div>
        """
        st.markdown(fallback_badge, unsafe_allow_html=True)

    status_color, status_border, status_text = "rgba(16, 185, 129, 0.1)", "#10b981", "✅ PRODUCTION NOMINAL: HIGH YIELD EXPECTED"
    if st.session_state.thickness_dev > 5.0 or st.session_state.oven_temp > 135 or st.session_state.defect_rate > 100:
        status_color, status_border, status_text = "rgba(239, 68, 68, 0.1)", "#ef4444", "🚨 QUALITY EXCURSION ALERT: ROOT CAUSE DETECTED"
    elif st.session_state.cell_throughput < st.session_state.target_min or st.session_state.yield_rate < 95.0:
        status_color, status_border, status_text = "rgba(245, 158, 11, 0.1)", "#f59e0b", "⚠️ WARNING: YIELD LOSS OR BOTTLENECK PREDICTED"

    st.markdown(f"<div style='padding:12px 15px; background-color:{status_color}; border-left: 5px solid {status_border}; color:{status_border}; border-radius:4px; margin-bottom:25px; font-weight: 600; letter-spacing: 0.5px;'>{status_text}</div>", unsafe_allow_html=True)

    render_factory_animation()
    
    # --- DIGITAL TWIN PREDICTIVE AI INSIGHTS ---
    st.markdown("### 🔮 Digital Twin Predictive AI Insights")
    preds = get_predictions()
    cols = st.columns(len(preds)) if len(preds) <= 3 else st.columns(3)
    
    for idx, pred in enumerate(preds[:3]):
        col = cols[idx % len(cols)]
        with col:
            st.markdown(f"""
            <div style='border: 1px solid {pred["color"]}; border-radius: 8px; padding: 15px; background-color: rgba(15, 23, 42, 0.6); box-shadow: 0 0 10px rgba(59,130,246,0.05); height: 100%;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                    <span style='font-weight: 700; color: #fff; font-size: 0.95rem;'>{pred["title"]}</span>
                    <span style='font-size: 0.75rem; font-weight: 800; color: {pred["color"]}; border: 1px solid {pred["color"]}; padding: 2px 6px; border-radius: 3px;'>{pred["status"]}</span>
                </div>
                <div style='color: #94a3b8; font-size: 0.8rem; margin-bottom: 8px;'>⏱️ <b>Estimated:</b> {pred["time"]}</div>
                <div style='color: #cbd5e1; font-size: 0.8rem; margin-bottom: 10px; line-height: 1.45;'>🧠 <b>Reason:</b> {pred["reason"]}</div>
                <div style='font-size: 0.8rem; border-top: 1px solid #1e293b; padding-top: 8px; color: #60a5fa;'>🛠️ <b>Mitigation:</b> {pred["remediation"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.write("") # Spacer
    
    # --- 10 METRICS GRID WITH HOVER TOOLTIPS ---
    st.markdown("### 📊 Live Process Telemetry (Hover over titles for details)")
    
    row1 = st.columns(5)
    row1[0].metric("1. Web Speed", f"{st.session_state.web_speed:.1f} m/m", "Active", help="The speed of the foil substrate moving through the production line. Controlled by user or AI agent.")
    row1[1].metric("2. Throughput", f"{st.session_state.cell_throughput:.0f} ppm", "Targeted", help="Calculated Parts Per Million (Cells per minute) based on web speed and material availability.")
    row1[2].metric("3. Yield Rate", f"{st.session_state.yield_rate:.1f} %", delta="Risk" if st.session_state.yield_rate < 95 else "Optimal", delta_color="inverse" if st.session_state.yield_rate < 95 else "normal", help="The percentage of usable material compared to scrap. Drops when process variables exceed quality thresholds.")
    row1[3].metric("4. Defect Rate", f"{st.session_state.defect_rate:.0f} ppm", delta="High" if st.session_state.defect_rate > 50 else "Nominal", delta_color="inverse" if st.session_state.defect_rate > 50 else "normal", help="Detected surface defects (scratches, pinholes) via the laser vision scanning station.")
    row1[4].metric("5. Oven Temp", f"{st.session_state.oven_temp:.1f} °C", delta="Drift" if st.session_state.oven_temp > 130 else "Stable", delta_color="inverse" if st.session_state.oven_temp > 130 else "off", help="Temperature of the drying oven. High temps cause coating blisters; low temps cause wet rolls.")
 
    st.write("") # Spacer

    row2 = st.columns(5)
    row2[0].metric("6. Slurry Visc.", f"{st.session_state.slurry_visc:.0f} cP", help="Centipoise measurement of the anode/cathode slurry. Thick slurry clogs coating nozzles; thin slurry runs off edges.")
    row2[1].metric("7. Coating Wt.", f"{st.session_state.coating_wt:.1f} mg/cm²", help="The mass of active material applied per square centimeter of the current collector foil.")
    row2[2].metric("8. Roller Press.", f"{st.session_state.roller_press:.0f} kN", help="KiloNewtons of hydraulic pressure applied by the calendaring rollers to compress the coated foil to targeted porosity.")
    row2[3].metric("9. Thick Dev.", f"± {st.session_state.thickness_dev:.2f} µm", delta="Out of Spec" if st.session_state.thickness_dev > 3.0 else "In Spec", delta_color="inverse" if st.session_state.thickness_dev > 3.0 else "normal", help="Micrometers of deviation from the target foil thickness after calendaring.")
    row2[4].metric("10. Wind Tension", f"{st.session_state.wind_tension:.1f} N", help="Newtons of pulling force at the winding station. Low tension causes telescope defects; high tension tears the foil.")
    
    st.divider()

    # --- CHARTS & LOGS ROW (UPGRADED LAYOUT) ---
    col_chart, col_logs = st.columns([1.8, 1])
    
    with col_chart:
        st.subheader("📈 Live Telemetry Graphs")
        if len(st.session_state.history) > 0:
            df = pd.DataFrame(st.session_state.history).set_index("Time")
            
            # --- The 5 Tabs for Clean Scaling ---
            tab_all, tab_prod, tab_qual, tab_therm, tab_mech = st.tabs([
                "🌐 Master Overview", 
                "🚀 Speed & Flow", 
                "⚖️ Yield & Defects", 
                "🌡️ Thermal & Fluids", 
                "⚙️ Mechanics"
            ])
            
            with tab_all:
                st.caption("High-Level KPIs (Sparkline Grid)")
                g1, g2 = st.columns(2)
                with g1:
                    st.line_chart(df["Yield Rate (%)"], height=140)
                    st.line_chart(df["Throughput (ppm)"], height=140)
                with g2:
                    st.area_chart(df["Defect Rate (ppm)"], height=140)
                    st.line_chart(df["Oven Temp (°C)"], height=140)
                    
            with tab_prod:
                st.caption("Production Flow Rates")
                st.line_chart(df[["Throughput (ppm)", "Web Speed (m/min)"]], height=280)
                
            with tab_qual:
                st.caption("Quality Excursion Tracking")
                st.area_chart(df["Yield Rate (%)"], height=150)
                st.line_chart(df[["Defect Rate (ppm)", "Thickness Dev (µm)"]], height=150)
                
            with tab_therm:
                st.caption("Viscosity & Heating Elements")
                st.line_chart(df["Slurry Visc (cP)"], height=150)
                st.area_chart(df["Oven Temp (°C)"], height=150)
                
            with tab_mech:
                st.caption("Mechanical Stresses & Pressures")
                st.line_chart(df[["Roller Press (kN)", "Wind Tension (N)"]], height=150)
                st.line_chart(df["Coating Wt (mg/cm²)"], height=150)

        else:
            st.info("Awaiting telemetry data...")

    with col_logs:
        st.subheader("🤖 Recommended Actions")
        for log in st.session_state.agent_log[:5]:
            if log["level"] == "critical": st.error(f"**[{log['time']}]** {log['message']}", icon="🚨")
            elif log["level"] == "action": st.info(f"**[{log['time']}]** {log['message']}", icon="🤖")
            elif log["level"] == "system": st.warning(f"**[{log['time']}]** {log['message']}", icon="📡")
            else: st.success(f"**[{log['time']}]** {log['message']}", icon="✅")

    st.divider()
    
    # --- DATA GRIDS ---
    st.subheader("📋 Comprehensive Logs & Data Grids")
    tab_data, tab_events = st.tabs(["10-Metric Telemetry History", "System Event & Anomaly Log"])
    
    with tab_data:
        if len(st.session_state.history) > 0:
            st.dataframe(pd.DataFrame(st.session_state.history).iloc[::-1], use_container_width=True, hide_index=True, height=250)
            
    with tab_events:
        df_logs = pd.DataFrame(st.session_state.all_logs)
        df_logs['level'] = df_logs['level'].str.upper()
        st.dataframe(df_logs, use_container_width=True, hide_index=True, height=250)


if __name__ == "__main__":
    main()
