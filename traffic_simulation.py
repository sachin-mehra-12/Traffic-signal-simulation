"""
traffic_simulation.py
Heterogeneous Indian Traffic Network Simulator with 2 Interconnected Junctions.
Simulates mixed vehicle classes (2-wheelers, autos, cars, buses),
realistic Indian queueing dynamics, sensor degradation, and incident injections.
"""

import time
import random
import math
from typing import Dict, List, Any, Optional

# Indian Traffic PCU (Passenger Car Unit) standards (IRC:106-1990 guidelines)
PCU_FACTORS = {
    "bike": 0.5,        # Two-wheelers (Motorcycles, Scooters)
    "auto": 0.8,        # 3-Wheeler Auto-rickshaw
    "car": 1.0,         # Private Cars, Cabs, Jeeps
    "bus": 2.8,         # Buses, Heavy Commercial Trucks
    "ambulance": 1.0    # Emergency Vehicle
}

VEHICLE_COLORS = {
    "bike": "#38bdf8",       # Sky Blue
    "auto": "#facc15",       # Auto Yellow
    "car": "#e2e8f0",        # White / Silver
    "bus": "#f97316",        # Orange Bus
    "ambulance": "#ef4444"   # Red / White Emergency
}

VEHICLE_LENGTHS = {
    "bike": 1.8,
    "auto": 2.8,
    "car": 4.5,
    "bus": 10.5,
    "ambulance": 5.0
}

class Vehicle:
    def __init__(self, v_type: str, approach: str, junction_id: str):
        self.id = f"{v_type}_{int(time.time()*1000)%100000}_{random.randint(100, 999)}"
        self.v_type = v_type
        self.pcu = PCU_FACTORS[v_type]
        self.length = VEHICLE_LENGTHS[v_type]
        self.color = VEHICLE_COLORS[v_type]
        self.approach = approach  # 'N', 'S', 'E', 'W'
        self.junction_id = junction_id
        self.wait_time = 0.0
        self.distance_to_stopline = random.uniform(80.0, 180.0)  # meters
        self.speed = 0.0  # m/s
        self.max_speed = 11.0 if v_type == 'bike' else (9.0 if v_type in ['car', 'ambulance'] else (7.0 if v_type == 'auto' else 6.0))
        self.passed = False
        self.is_emergency = (v_type == "ambulance")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.v_type,
            "pcu": self.pcu,
            "approach": self.approach,
            "junction": self.junction_id,
            "wait_time": round(self.wait_time, 1),
            "distance": round(self.distance_to_stopline, 1),
            "speed": round(self.speed, 1),
            "is_emergency": self.is_emergency,
            "color": self.color
        }


class Junction:
    def __init__(self, j_id: str, name: str):
        self.id = j_id
        self.name = name
        # Signal states: 'NS_GREEN', 'NS_YELLOW', 'EW_GREEN', 'EW_YELLOW'
        self.current_phase = "NS_GREEN"
        self.phase_duration = 0.0
        self.min_green = 12.0
        self.max_green = 65.0
        self.yellow_time = 4.0
        
        # Vehicles queued on approaches
        self.queues: Dict[str, List[Vehicle]] = {
            "N": [],
            "S": [],
            "E": [],
            "W": []
        }
        
        # Incident/Hazard state on approaches
        self.blocked_approaches: Dict[str, bool] = {
            "N": False,
            "S": False,
            "E": False,
            "W": False
        }

    def get_queue_pcu(self, approach: str) -> float:
        return sum(v.pcu for v in self.queues[approach] if not v.passed)

    def get_queue_count(self, approach: str) -> int:
        return len([v for v in self.queues[approach] if not v.passed])

    def get_breakdown(self, approach: str) -> Dict[str, int]:
        counts = {"bike": 0, "auto": 0, "car": 0, "bus": 0, "ambulance": 0}
        for v in self.queues[approach]:
            if not v.passed:
                counts[v.v_type] = counts.get(v.v_type, 0) + 1
        return counts


class TrafficNetwork:
    def __init__(self):
        # 2 Connected Junctions along an East-West Arterial Corridor
        # J1 (e.g. MG Road) is West of J2 (e.g. Indiranagar)
        # Vehicles clearing Eastbound from J1 travel ~350m and enter J2's West approach!
        self.j1 = Junction("J1", "MG Road Junction")
        self.j2 = Junction("J2", "Indiranagar Junction")
        self.corridor_travel_time = 14.0  # seconds travel time between J1 and J2
        self.in_transit_j1_to_j2: List[Dict[str, Any]] = []

        # Weather & Sensor conditions
        # 'CLEAR', 'MONSOON', 'DUST_SMOG', 'SENSOR_FAILURE'
        self.weather = "CLEAR"
        self.sensor_reliability = 1.0  # 100%

        # Escalation & Incident states
        self.accident_active = False
        self.accident_location: Optional[str] = None
        self.vip_active = False
        self.police_override_active = False
        self.emergency_vehicle_active = False

        # System Metrics
        self.total_cleared_pcu = 0.0
        self.total_cleared_vehicles = 0
        self.total_wait_time = 0.0
        self.simulation_time = 0.0
        self.total_decisions = 0
        self.coordination_events = 0
        self.escalations_triggered = 0

        # Mode: 'STATIC', 'PASSIVE_DL', 'AGENTIC'
        self.control_mode = "AGENTIC"

        # Populate initial traffic so demo looks lively from second 1
        self._seed_initial_vehicles()

    def _seed_initial_vehicles(self):
        for j in [self.j1, self.j2]:
            for app in ["N", "S", "E", "W"]:
                n_veh = random.randint(3, 8)
                for _ in range(n_veh):
                    v_type = self._sample_indian_vehicle_type()
                    v = Vehicle(v_type, app, j.id)
                    v.distance_to_stopline = random.uniform(10.0, 100.0)
                    j.queues[app].append(v)

    def _sample_indian_vehicle_type(self) -> str:
        # Typical Indian urban modal split
        r = random.random()
        if r < 0.45:
            return "bike"       # 45% 2-wheelers
        elif r < 0.68:
            return "auto"       # 23% auto-rickshaws
        elif r < 0.90:
            return "car"        # 22% cars/cabs
        else:
            return "bus"        # 10% buses/trucks

    def set_weather(self, weather_type: str):
        self.weather = weather_type
        if weather_type == "CLEAR":
            self.sensor_reliability = 0.98
        elif weather_type == "MONSOON":
            self.sensor_reliability = 0.42  # Heavy water drops on camera, low confidence
        elif weather_type == "DUST_SMOG":
            self.sensor_reliability = 0.52  # Haze, vision models suffer
        elif weather_type == "SENSOR_FAILURE":
            self.sensor_reliability = 0.05  # Camera signal down/frozen

    def trigger_accident(self, junction_id: str = "J1", approach: str = "N"):
        self.accident_active = True
        self.accident_location = f"{junction_id}_{approach}"
        target_j = self.j1 if junction_id == "J1" else self.j2
        target_j.blocked_approaches[approach] = True
        self.escalations_triggered += 1

    def clear_accident(self):
        self.accident_active = False
        self.accident_location = None
        self.j1.blocked_approaches = {a: False for a in ["N", "S", "E", "W"]}
        self.j2.blocked_approaches = {a: False for a in ["N", "S", "E", "W"]}

    def trigger_vip_convoy(self):
        self.vip_active = True
        self.escalations_triggered += 1

    def clear_vip_convoy(self):
        self.vip_active = False

    def spawn_ambulance(self, junction_id: str = "J1", approach: str = "W"):
        target_j = self.j1 if junction_id == "J1" else self.j2
        amb = Vehicle("ambulance", approach, junction_id)
        amb.distance_to_stopline = 130.0
        target_j.queues[approach].insert(0, amb)  # Push to front of lane
        self.emergency_vehicle_active = True
        self.escalations_triggered += 1

    def step(self, dt: float = 1.0):
        self.simulation_time += dt

        # 1. Random Vehicle Influx (Indian urban arrival model with stochastic bursts)
        for j in [self.j1, self.j2]:
            for app in ["N", "S", "E", "W"]:
                # If Eastbound corridor from J1 to J2, J2 West gets inflow from J1 departures
                if j.id == "J2" and app == "W":
                    arrival_prob = 0.20  # baseline local arrivals
                else:
                    arrival_prob = 0.38 if app in ["N", "S"] else 0.45

                if random.random() < arrival_prob * dt:
                    v_type = self._sample_indian_vehicle_type()
                    veh = Vehicle(v_type, app, j.id)
                    j.queues[app].append(veh)

        # 2. Update corridor in-transit vehicles (J1 East exit -> J2 West entrance)
        remaining_transit = []
        for packet in self.in_transit_j1_to_j2:
            packet["time_left"] -= dt
            if packet["time_left"] <= 0:
                # Arrived at J2 West approach
                for v_info in packet["vehicles"]:
                    v = Vehicle(v_info["type"], "W", "J2")
                    v.distance_to_stopline = random.uniform(90.0, 150.0)
                    self.j2.queues["W"].append(v)
            else:
                remaining_transit.append(packet)
        self.in_transit_j1_to_j2 = remaining_transit

        # 3. Simulate vehicle dynamics and signal clearance at both junctions
        for j in [self.j1, self.j2]:
            j.phase_duration += dt
            cleared_this_step = []

            is_ns_green = (j.current_phase == "NS_GREEN")
            is_ew_green = (j.current_phase == "EW_GREEN")
            active_approaches = ["N", "S"] if is_ns_green else (["E", "W"] if is_ew_green else [])

            for app, v_list in j.queues.items():
                is_green = (app in active_approaches)
                is_blocked = j.blocked_approaches[app]

                for v in v_list:
                    if v.passed:
                        continue

                    # If signal is red or yellow, or approach blocked, vehicles decelerate and queue
                    if not is_green or is_blocked:
                        if v.distance_to_stopline > 5.0:
                            v.speed = max(0.0, v.speed - 3.5 * dt)
                            v.distance_to_stopline -= v.speed * dt
                        else:
                            v.speed = 0.0
                            v.wait_time += dt
                            self.total_wait_time += dt
                    else:
                        # Green phase: discharge vehicles based on saturation flow rate
                        v.speed = min(v.max_speed, v.speed + 3.0 * dt)
                        v.distance_to_stopline -= v.speed * dt

                        if v.distance_to_stopline <= 0.0:
                            v.passed = True
                            self.total_cleared_pcu += v.pcu
                            self.total_cleared_vehicles += 1
                            cleared_this_step.append(v)

                # Keep queue reasonable length
                j.queues[app] = [v for v in v_list if not v.passed or v.distance_to_stopline > -40.0]

            # If J1 cleared Eastbound vehicles, schedule arrival at J2 West approach!
            if j.id == "J1" and is_ew_green:
                east_cleared = [v for v in cleared_this_step if v.approach == "E"]
                if east_cleared:
                    self.in_transit_j1_to_j2.append({
                        "time_left": self.corridor_travel_time,
                        "vehicles": [{"type": v.v_type, "pcu": v.pcu} for v in east_cleared]
                    })

    def get_state(self) -> Dict[str, Any]:
        avg_wait = (self.total_wait_time / max(1, self.total_cleared_vehicles)) if self.total_cleared_vehicles > 0 else 0.0
        throughput = (self.total_cleared_pcu / max(1.0, self.simulation_time / 60.0))

        return {
            "simulation_time": round(self.simulation_time, 1),
            "control_mode": self.control_mode,
            "weather": self.weather,
            "sensor_reliability": round(self.sensor_reliability * 100, 1),
            "accident_active": self.accident_active,
            "accident_location": self.accident_location,
            "vip_active": self.vip_active,
            "police_override": self.police_override_active,
            "emergency_vehicle_active": self.emergency_vehicle_active,
            "metrics": {
                "avg_wait_seconds": round(avg_wait, 1),
                "throughput_pcu_per_min": round(throughput, 1),
                "cleared_vehicles": self.total_cleared_vehicles,
                "cleared_pcu": round(self.total_cleared_pcu, 1),
                "total_wait_time": round(self.total_wait_time, 1),
                "coordination_events": self.coordination_events,
                "escalations": self.escalations_triggered
            },
            "junctions": {
                "J1": {
                    "id": self.j1.id,
                    "name": self.j1.name,
                    "phase": self.j1.current_phase,
                    "phase_duration": round(self.j1.phase_duration, 1),
                    "blocked": self.j1.blocked_approaches,
                    "queues": {
                        app: {
                            "count": self.j1.get_queue_count(app),
                            "pcu": round(self.j1.get_queue_pcu(app), 1),
                            "breakdown": self.j1.get_breakdown(app),
                            "vehicles": [v.to_dict() for v in self.j1.queues[app][:15]]
                        } for app in ["N", "S", "E", "W"]
                    }
                },
                "J2": {
                    "id": self.j2.id,
                    "name": self.j2.name,
                    "phase": self.j2.current_phase,
                    "phase_duration": round(self.j2.phase_duration, 1),
                    "blocked": self.j2.blocked_approaches,
                    "queues": {
                        app: {
                            "count": self.j2.get_queue_count(app),
                            "pcu": round(self.j2.get_queue_pcu(app), 1),
                            "breakdown": self.j2.get_breakdown(app),
                            "vehicles": [v.to_dict() for v in self.j2.queues[app][:15]]
                        } for app in ["N", "S", "E", "W"]
                    }
                }
            },
            "corridor_transit_pcu": round(sum(sum(v["pcu"] for v in p["vehicles"]) for p in self.in_transit_j1_to_j2), 1)
        }
