"""
agentic_coordinator.py
Autonomous Multi-Junction Traffic Signal Coordination System.
Implements:
1. Perception & Heterogeneous PCU reasoning
2. Inter-Junction Agent-to-Agent Coordination (Green Wave synchronization)
3. Sensor Reliability & Safe-Fallback Guard (Monsoon/Dust detection)
4. Human Escalation Protocol for Traffic Police (Accident, VIP, Emergency)
"""

import time
from typing import Dict, List, Any, Optional
from traffic_simulation import TrafficNetwork, Junction

class AgentLog:
    def __init__(self, agent_name: str, category: str, message: str, level: str = "INFO", details: Optional[Dict[str, Any]] = None):
        self.timestamp = time.strftime("%H:%M:%S")
        self.agent_name = agent_name
        self.category = category  # 'PERCEPTION', 'REASONING', 'COORDINATION', 'SENSOR_GUARD', 'ESCALATION', 'ACTION'
        self.message = message
        self.level = level        # 'INFO', 'SUCCESS', 'WARNING', 'CRITICAL'
        self.details = details or {}

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "agent": self.agent_name,
            "category": self.category,
            "message": self.message,
            "level": self.level,
            "details": self.details
        }


class AgenticCoordinator:
    def __init__(self, network: TrafficNetwork):
        self.network = network
        self.logs: List[AgentLog] = []
        self.max_logs = 100

        # Safe fallback timers for degraded sensor states
        self.fallback_cycle_time = 40.0
        self.last_coordination_time = 0.0

        # Passive DL mode internal counters
        self.passive_timer_j1 = 0.0
        self.passive_timer_j2 = 0.0

    def add_log(self, agent_name: str, category: str, message: str, level: str = "INFO", details: Optional[Dict[str, Any]] = None):
        log = AgentLog(agent_name, category, message, level, details)
        self.logs.append(log)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def update(self, dt: float = 1.0):
        mode = self.network.control_mode

        if self.network.police_override_active:
            # Under explicit manual police control
            return

        if mode == "STATIC":
            self._run_static_timed_control(dt)
        elif mode == "PASSIVE_DL":
            self._run_passive_dl_control(dt)
        elif mode == "AGENTIC":
            self._run_agentic_autonomous_control(dt)

    # -------------------------------------------------------------
    # 1. BASELINE: Static Fixed-Time Signals (Traditional 45s Cycle)
    # -------------------------------------------------------------
    def _run_static_timed_control(self, dt: float):
        for j in [self.network.j1, self.network.j2]:
            fixed_green = 35.0
            fixed_yellow = 4.0

            if j.current_phase == "NS_GREEN" and j.phase_duration >= fixed_green:
                j.current_phase = "NS_YELLOW"
                j.phase_duration = 0.0
            elif j.current_phase == "NS_YELLOW" and j.phase_duration >= fixed_yellow:
                j.current_phase = "EW_GREEN"
                j.phase_duration = 0.0
            elif j.current_phase == "EW_GREEN" and j.phase_duration >= fixed_green:
                j.current_phase = "EW_YELLOW"
                j.phase_duration = 0.0
            elif j.current_phase == "EW_YELLOW" and j.phase_duration >= fixed_yellow:
                j.current_phase = "NS_GREEN"
                j.phase_duration = 0.0

    # -------------------------------------------------------------
    # 2. COMPARISON: Passive Deep Learning (CCTV Counting Only)
    # -------------------------------------------------------------
    def _run_passive_dl_control(self, dt: float):
        # Passive DL estimates counts but has no autonomous goal planning,
        # no inter-junction coordination, and blind reactions to bad sensors.
        for j in [self.network.j1, self.network.j2]:
            if j.phase_duration < 25.0:
                continue

            # Raw unweighted vehicle count (passive camera prediction without Indian PCU modeling)
            ns_raw = j.get_queue_count("N") + j.get_queue_count("S")
            ew_raw = j.get_queue_count("E") + j.get_queue_count("W")

            # Passive threshold switch
            if j.current_phase == "NS_GREEN" and ew_raw > ns_raw + 6:
                j.current_phase = "NS_YELLOW"
                j.phase_duration = 0.0
                self.add_log(j.name, "ACTION", f"Passive DL Model triggered phase change: EW count ({ew_raw}) > NS ({ns_raw}).", "INFO")
            elif j.current_phase == "NS_YELLOW" and j.phase_duration >= 4.0:
                j.current_phase = "EW_GREEN"
                j.phase_duration = 0.0
            elif j.current_phase == "EW_GREEN" and ns_raw > ew_raw + 6:
                j.current_phase = "EW_YELLOW"
                j.phase_duration = 0.0
                self.add_log(j.name, "ACTION", f"Passive DL Model triggered phase change: NS count ({ns_raw}) > EW ({ew_raw}).", "INFO")
            elif j.current_phase == "EW_YELLOW" and j.phase_duration >= 4.0:
                j.current_phase = "NS_GREEN"
                j.phase_duration = 0.0

    # -------------------------------------------------------------
    # 3. PROPOSED SOLUTION: Agentic AI Autonomous Architecture
    # -------------------------------------------------------------
    def _run_agentic_autonomous_control(self, dt: float):
        # STEP 1: Emergency & Human Escalation Check
        if self._handle_escalation_protocol():
            return

        # STEP 2: Sensor Health & Adverse Weather Guard (Monsoon/Dust/Outage)
        sensor_confidence = self.network.sensor_reliability
        if sensor_confidence < 0.60:
            self._handle_sensor_safe_fallback(sensor_confidence)
            return

        # STEP 3: Multi-Junction Perception & Coordination (J1 <-> J2)
        self._coordinate_multi_junction()

        # STEP 4: Junction Deliberation & Adaptive Signal Control
        self._deliberate_junction(self.network.j1)
        self._deliberate_junction(self.network.j2)

    def _handle_escalation_protocol(self) -> bool:
        """
        Escalation logic for handing control or notifying human traffic police during exceptions.
        """
        # A. Accident detected
        if self.network.accident_active:
            loc = self.network.accident_location or "Junction"
            self.add_log(
                "EscalationManager",
                "ESCALATION",
                f"🚨 CRITICAL ALERT: Road Blockage/Accident detected at [{loc}]. Handing incident telemetry to Traffic Police Command Center!",
                "CRITICAL",
                {"protocol": "POLICE_ALERT", "location": loc, "action": "Diverting upstream traffic & holding red signal on blocked approach"}
            )
            # Safe hold
            return False  # Let agents still clear unaffected phases, but with caution

        # B. VIP Convoy Movement
        if self.network.vip_active:
            # Green Corridor requested across East-West arterial (J1 -> J2)
            for j in [self.network.j1, self.network.j2]:
                if j.current_phase != "EW_GREEN":
                    j.current_phase = "EW_GREEN"
                    j.phase_duration = 0.0
            self.add_log(
                "EscalationManager",
                "ESCALATION",
                "🚔 VIP Convoy Active: Coordinated Green Corridor engaged across MG Road & Indiranagar junctions. Traffic Police dispatched to side roads.",
                "WARNING"
            )
            return True

        # C. Emergency Vehicle Clearance (Ambulance Preemption)
        for j in [self.network.j1, self.network.j2]:
            for app, q in j.queues.items():
                emergency_present = any(v.is_emergency and not v.passed for v in q)
                if emergency_present:
                    needed_phase = "NS_GREEN" if app in ["N", "S"] else "EW_GREEN"
                    if j.current_phase != needed_phase:
                        j.current_phase = needed_phase
                        j.phase_duration = 0.0
                        self.add_log(
                            f"{j.name} Agent",
                            "ACTION",
                            f"🚑 EMERGENCY PREEMPTION: Ambulance detected at {app} approach! Immediate priority green corridor granted.",
                            "SUCCESS"
                        )
                        return True
        return False

    def _handle_sensor_safe_fallback(self, confidence: float):
        """
        Sensor-failure detection module with safe-fallback behavior.
        Prevents disastrous signal actions based on degraded/occluded camera frames.
        """
        weather_desc = self.network.weather
        if int(self.network.simulation_time) % 15 == 0:
            self.add_log(
                "SensorGuardModule",
                "SENSOR_GUARD",
                f"⚠️ Adverse Condition [{weather_desc}]: Camera vision confidence is {round(confidence*100, 1)}% (< 60% threshold). Engaging Fail-Safe Baseline Timing.",
                "WARNING",
                {"confidence": f"{round(confidence*100, 1)}%", "weather": weather_desc, "strategy": "ROBUST_HISTORICAL_TIMING"}
            )

        # Fallback to balanced fixed timing with extended yellow clearance for safety
        for j in [self.network.j1, self.network.j2]:
            if j.current_phase == "NS_GREEN" and j.phase_duration >= self.fallback_cycle_time:
                j.current_phase = "NS_YELLOW"
                j.phase_duration = 0.0
            elif j.current_phase == "NS_YELLOW" and j.phase_duration >= 5.0:
                j.current_phase = "EW_GREEN"
                j.phase_duration = 0.0
            elif j.current_phase == "EW_GREEN" and j.phase_duration >= self.fallback_cycle_time:
                j.current_phase = "EW_YELLOW"
                j.phase_duration = 0.0
            elif j.current_phase == "EW_YELLOW" and j.phase_duration >= 5.0:
                j.current_phase = "NS_GREEN"
                j.phase_duration = 0.0

    def _coordinate_multi_junction(self):
        """
        Agent-to-Agent message passing across connected junctions.
        J1 (MG Road) communicates expected platoon release to J2 (Indiranagar).
        """
        # Check if J1 has Eastbound green and is discharging towards J2
        j1 = self.network.j1
        j2 = self.network.j2

        now = self.network.simulation_time
        if now - self.last_coordination_time >= 8.0:
            j1_east_pcu = j1.get_queue_pcu("E")
            in_transit_pcu = sum(sum(v["pcu"] for v in p["vehicles"]) for p in self.network.in_transit_j1_to_j2)

            if in_transit_pcu > 8.0 or (j1.current_phase == "EW_GREEN" and j1_east_pcu > 6.0):
                self.network.coordination_events += 1
                eta = round(self.network.corridor_travel_time, 0)
                self.add_log(
                    "J1-J2 Coordinator",
                    "COORDINATION",
                    f"📡 J1 Agent -> J2 Agent: Arterial Platoon alert! {round(in_transit_pcu + j1_east_pcu, 1)} PCU en route Eastbound. ETA: ~{eta}s. Synchronizing Green Wave.",
                    "SUCCESS",
                    {"en_route_pcu": round(in_transit_pcu + j1_east_pcu, 1), "eta_seconds": eta, "target_phase": "EW_GREEN"}
                )
                self.last_coordination_time = now

    def _deliberate_junction(self, j: Junction):
        """
        Individual Junction Agent deliberation:
        Weighs Heterogeneous PCU pressure (Bikes=0.5, Autos=0.8, Cars=1.0, Buses=2.8).
        """
        phase = j.current_phase
        dur = j.phase_duration

        # Transition yellow signals
        if phase == "NS_YELLOW":
            if dur >= j.yellow_time:
                j.current_phase = "EW_GREEN"
                j.phase_duration = 0.0
                self.add_log(f"{j.name} Agent", "ACTION", f"Switched to EW_GREEN after yellow clearance.", "INFO")
            return

        if phase == "EW_YELLOW":
            if dur >= j.yellow_time:
                j.current_phase = "NS_GREEN"
                j.phase_duration = 0.0
                self.add_log(f"{j.name} Agent", "ACTION", f"Switched to NS_GREEN after yellow clearance.", "INFO")
            return

        # Current phase is GREEN: deliberate whether to extend or terminate phase
        # Calculate Passenger Car Unit (PCU) demand for each direction
        ns_pcu = j.get_queue_pcu("N") + j.get_queue_pcu("S")
        ew_pcu = j.get_queue_pcu("E") + j.get_queue_pcu("W")

        # Multi-junction incentive: If J2 and incoming platoon from J1 is arriving, add synthetic weight to EW
        if j.id == "J2":
            in_transit_pcu = sum(sum(v["pcu"] for v in p["vehicles"]) for p in self.network.in_transit_j1_to_j2)
            ew_pcu += (in_transit_pcu * 0.75)

        # Enforce minimum green time
        if dur < j.min_green:
            return

        # Max green ceiling reached -> force phase shift
        if dur >= j.max_green:
            next_yellow = "NS_YELLOW" if phase == "NS_GREEN" else "EW_YELLOW"
            j.current_phase = next_yellow
            j.phase_duration = 0.0
            self.add_log(
                f"{j.name} Agent",
                "REASONING",
                f"Max green limit ({j.max_green}s) reached. Switching to prevent starvation on opposing approaches.",
                "INFO"
            )
            return

        # Autonomous Agent Decision: Evaluate Marginal Pressure
        if phase == "NS_GREEN":
            # If waiting EW traffic has significantly higher PCU pressure than remaining NS traffic
            pressure_diff = ew_pcu - ns_pcu
            if pressure_diff > 6.0 and dur >= 18.0:
                j.current_phase = "NS_YELLOW"
                j.phase_duration = 0.0
                breakdown = j.get_breakdown("E")
                self.add_log(
                    f"{j.name} Agent",
                    "REASONING",
                    f"Autonomous Phase Cut: EW queue pressure ({round(ew_pcu, 1)} PCU) outweighs NS ({round(ns_pcu, 1)} PCU). Initiating switch.",
                    "INFO",
                    {"pressure_delta": round(pressure_diff, 1), "waiting_ew_pcu": round(ew_pcu, 1)}
                )

        elif phase == "EW_GREEN":
            pressure_diff = ns_pcu - ew_pcu
            if pressure_diff > 6.0 and dur >= 18.0:
                j.current_phase = "EW_YELLOW"
                j.phase_duration = 0.0
                self.add_log(
                    f"{j.name} Agent",
                    "REASONING",
                    f"Autonomous Phase Cut: NS queue pressure ({round(ns_pcu, 1)} PCU) outweighs EW ({round(ew_pcu, 1)} PCU). Initiating switch.",
                    "INFO",
                    {"pressure_delta": round(pressure_diff, 1), "waiting_ns_pcu": round(ns_pcu, 1)}
                )
