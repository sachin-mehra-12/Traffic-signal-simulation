"""
main.py
FastAPI Web Server for Indian Urban Traffic Agentic AI Prototype.
Serves interactive real-time dashboard and handles API triggers.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from traffic_simulation import TrafficNetwork
from agentic_coordinator import AgenticCoordinator

network = TrafficNetwork()
coordinator = AgenticCoordinator(network)
sim_task = None
sim_running = True
sim_speed = 1.0

async def simulation_loop():
    global sim_running, sim_speed
    dt = 0.5  # 500ms step
    while True:
        if sim_running:
            network.step(dt * sim_speed)
            coordinator.update(dt * sim_speed)
        await asyncio.sleep(dt)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global sim_task
    sim_task = asyncio.create_task(simulation_loop())
    yield
    if sim_task:
        sim_task.cancel()

app = FastAPI(title="Agentic AI Traffic Coordination", lifespan=lifespan)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Loading Dashboard...</h1>")

@app.get("/api/state")
async def get_state():
    state = network.get_state()
    state["logs"] = [log.to_dict() for log in reversed(coordinator.logs[-30:])]
    state["sim_speed"] = sim_speed
    state["sim_running"] = sim_running
    return state

class ModePayload(BaseModel):
    mode: str

@app.post("/api/set_mode")
async def set_mode(payload: ModePayload):
    if payload.mode in ["STATIC", "PASSIVE_DL", "AGENTIC"]:
        network.control_mode = payload.mode
        coordinator.add_log("System", "ACTION", f"Switched signal control paradigm to: {payload.mode}", "SUCCESS")
        return {"status": "ok", "mode": payload.mode}
    return {"status": "error", "message": "Invalid mode"}

class WeatherPayload(BaseModel):
    weather: str

@app.post("/api/set_weather")
async def set_weather(payload: WeatherPayload):
    network.set_weather(payload.weather)
    coordinator.add_log(
        "SensorModule",
        "SENSOR_GUARD",
        f"Weather environment updated to '{payload.weather}'. Sensor reliability adjusted to {int(network.sensor_reliability * 100)}%.",
        "WARNING" if network.sensor_reliability < 0.6 else "INFO"
    )
    return {"status": "ok", "weather": network.weather, "reliability": network.sensor_reliability}

class IncidentPayload(BaseModel):
    junction: str = "J1"
    approach: str = "N"

@app.post("/api/trigger_accident")
async def trigger_accident(payload: IncidentPayload):
    network.trigger_accident(payload.junction, payload.approach)
    coordinator.add_log(
        "EscalationManager",
        "ESCALATION",
        f"⚠️ Incident Injected: Multi-vehicle collision at {payload.junction} approach [{payload.approach}]. Lane blocked!",
        "CRITICAL"
    )
    return {"status": "ok", "location": f"{payload.junction}_{payload.approach}"}

@app.post("/api/clear_accident")
async def clear_accident():
    network.clear_accident()
    coordinator.add_log("EscalationManager", "ESCALATION", "Accident cleared. Traffic restoration protocol complete.", "SUCCESS")
    return {"status": "ok"}

@app.post("/api/spawn_ambulance")
async def spawn_ambulance(payload: IncidentPayload):
    network.spawn_ambulance(payload.junction, payload.approach)
    coordinator.add_log(
        "EscalationManager",
        "ACTION",
        f"Emergency Call: Priority Ambulance en route to {payload.junction} via approach [{payload.approach}].",
        "WARNING"
    )
    return {"status": "ok"}

@app.post("/api/trigger_vip")
async def trigger_vip():
    network.trigger_vip_convoy()
    coordinator.add_log("EscalationManager", "ESCALATION", "VIP Escort movement request received. Arterial green corridor requested.", "WARNING")
    return {"status": "ok"}

@app.post("/api/clear_vip")
async def clear_vip():
    network.clear_vip_convoy()
    coordinator.add_log("EscalationManager", "ESCALATION", "VIP Convoy passed safely. Returning control to autonomous multi-junction agent.", "SUCCESS")
    return {"status": "ok"}

class PoliceOverridePayload(BaseModel):
    override: bool

@app.post("/api/police_override")
async def police_override(payload: PoliceOverridePayload):
    network.police_override_active = payload.override
    msg = "Manual Police Override ACTIVATED. Local officer has manual baton control." if payload.override else "Manual Police Override DEACTIVATED. Agentic AI resumed."
    coordinator.add_log("EscalationManager", "ESCALATION", msg, "WARNING" if payload.override else "SUCCESS")
    return {"status": "ok", "override": network.police_override_active}

class SpeedPayload(BaseModel):
    speed: float

@app.post("/api/set_speed")
async def set_speed(payload: SpeedPayload):
    global sim_speed
    sim_speed = max(0.2, min(5.0, payload.speed))
    return {"status": "ok", "speed": sim_speed}

@app.post("/api/toggle_pause")
async def toggle_pause():
    global sim_running
    sim_running = not sim_running
    return {"status": "ok", "running": sim_running}

@app.post("/api/reset")
async def reset_simulation():
    global network, coordinator
    network = TrafficNetwork()
    coordinator = AgenticCoordinator(network)
    coordinator.add_log("System", "ACTION", "Simulation reset to initial state.", "INFO")
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print(" [AGENTIC AI] TRAFFIC SIGNAL COORDINATOR FOR INDIAN ROAD NETWORKS")
    print(" Starting web dashboard at: http://127.0.0.1:8000")
    print("="*70 + "\n")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
