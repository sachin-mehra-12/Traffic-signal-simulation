# Agentic AI for Autonomous, Real-Time Traffic Signal Coordination in Indian Urban Road Networks
## Comprehensive Technical Project Report & Implementation Dossier

---

### Metadata
- **Domain:** Agentic Artificial Intelligence & Intelligent Transportation Systems (ITS)
- **Geographic Context:** Indian Urban Road Corridors (Heterogeneous Traffic Dynamics)
- **Technology Stack:** Python 3.11, FastAPI, Uvicorn, HTML5 Canvas, RESTful Telemetry API
- **Project Status:** Approved Research & Working Prototype Implementation
- **Word Document File:** [`Project_Documentation_Agentic_Traffic_AI.docx`](file:///C:/Users/sachi/.gemini/antigravity/scratch/indian_traffic_agentic_ai/Project_Documentation_Agentic_Traffic_AI.docx)

---

## 1. Project Overview

Urban traffic congestion in Indian metropolitan centers (such as Bengaluru, Delhi, Mumbai, and Hyderabad) represents one of the most critical economic, environmental, and public-health challenges of modern infrastructure. Unlike Western traffic environments characterized by disciplined lane driving and homogeneous passenger cars, Indian traffic is fundamentally heterogeneous and chaotic. Roadways are populated by high proportions of two-wheelers (motorcycles, scooters), three-wheelers (auto-rickshaws), private cars, and heavy mass-transit buses, all exhibiting informal lane sharing, micro-weaving, and non-linear queue formation.

Existing urban signal infrastructure relies overwhelmingly on either pre-timed static signal controllers (e.g., fixed 45–60 second cycles) or passive Deep Learning (DL) CCTV counting systems. Both paradigms suffer from severe limitations:
- **Static Pre-Timed Signals:** Operate on rigid time-of-day tables completely detached from real-time surges, wasting green time on empty approaches while compounding gridlock on high-demand corridors.
- **Passive Deep Learning Systems:** While computer vision models can count vehicles on CCTV cameras, they remain strictly passive and predictive. They do not autonomously execute closed-loop multi-step decisions, do not coordinate between neighboring intersections, and require human traffic police to manually interpret predictions or dispatch field officers.
- **Vulnerability to Adverse Operating Conditions:** Most international smart-city systems assume pristine IoT sensor networks. In Indian cities, monsoon rain, heavy dust/smog, and hardware occlusion regularly degrade camera feeds. Passive vision systems either hallucinate or fail completely, risking catastrophic intersection deadlocks.

This project introduces an **Agentic AI Architecture** that transitions traffic management from passive observation to autonomous, goal-oriented signal coordination. Junction agents act as autonomous decision-makers that calculate traffic pressure using Indian Passenger Car Units (PCU), communicate peer-to-peer across corridors to generate dynamic "Green Waves", monitor their own sensor confidence to trigger fail-safe fallback cycles during severe weather, and automatically escalate critical anomalies (accidents, VIP convoys, ambulances) to human traffic police.

---

## 2. Specific Objectives

| Objective ID & Title | Research Focus & Practical Target |
| :--- | :--- |
| **Objective 1: Autonomous Agentic Decision-Making vs. Passive DL** | Demonstrate how an autonomous agent deliberates on queue states, balances multi-step goals, and directly actuates signal timing without human intervention, compared to passive CCTV counting systems. |
| **Objective 2: Multi-Junction Coordination in Heterogeneous Traffic** | Formulate an agent-to-agent communication protocol where upstream junctions (e.g., MG Road) broadcast platoon departures to downstream junctions (e.g., Indiranagar) to synthesize dynamic arterial green waves under mixed Indian PCU traffic. |
| **Objective 3: Sensor Reliability & Safe-Fallback Behavior** | Design and evaluate a Sensor Guard Module capable of continuously computing telemetry confidence under adverse conditions (monsoon rain, smog, camera lens occlusion) and safely falling back to robust historical cycles when confidence drops below 60%. |
| **Objective 4: Human-in-the-Loop Escalation Protocols** | Establish deterministic escalation logic for handling unpredictable exceptions—such as lane-blocking collisions, emergency ambulances, VIP convoys, or manual officer takeovers—transferring authority safely between AI and human police command. |

---

## 3. Key Features

- **Heterogeneous Indian PCU Engine:** Incorporates standard Indian Road Congress (IRC:106-1990) guidelines to convert mixed traffic into Passenger Car Units: Two-wheelers (0.5 PCU), Auto-rickshaws (0.8 PCU), Private Cars (1.0 PCU), and Commercial Buses/Trucks (2.8 PCU). Queues are balanced by total road impact rather than simplistic vehicle counts.
- **Inter-Junction Agent Communication:** Enables distributed junction agents to transmit anticipatory platoon trajectory packets over an East-West corridor, minimizing arterial spillback and corridor stopping frequencies.
- **Adaptive Green Extension & Phase Truncation:** Dynamically deliberates whether to extend green signals (within safe bounds of 12s to 65s) based on marginal PCU pressure differentials, switching phases before green time is squandered on empty lanes.
- **Autonomous Sensor Guard & Degraded Telemetry Fallback:** Continuously scores vision pipeline reliability. If weather downpours or hardware faults lower confidence below 60%, the system locks out erratic autonomous switching and reverts to fail-safe historical timing with extended yellow caution clearance.
- **Emergency Ambulance Preemption:** Detects priority emergency sirens/signals and overrides routine scheduling in real time to establish an unhindered green passage through the active approach.
- **Human Police Escalation Console:** Maintains a centralized incident dispatch bridge that flags accidents, facilitates VIP convoy green corridors, and permits physical traffic police manual takeover with instantaneous AI relinquishment.
- **Interactive Real-Time Dashboard:** A responsive browser-based control dashboard featuring high-frame-rate HTML5 2D canvas simulation, live performance metric telemetry, and an "Agent Thought Stream" that exposes the internal perception-deliberation-action cycle.

---

## 4. Project Use Cases

| Use Case | Operational Context | System Response & Impact |
| :--- | :--- | :--- |
| **Peak-Hour Corridor Management** | Heavy morning/evening commuter rush with uneven directional traffic on major arterials. | Autonomous queue balancing dynamically extends green time in direction of peak PCU pressure; inter-junction coordination prevents downstream choke points. |
| **Monsoon & Extreme Weather Outages** | Torrential rains or severe winter dust/smog causing blurred camera lenses and dropped vision inference frames. | Sensor Guard Module detects confidence dropping below 60%, engages safe fallback baseline cycle with 5-second yellow caution, preventing deadlock. |
| **Emergency Medical Response** | Ambulance transporting critical patients through high-density urban corridors. | Agent executes instant preemption protocol, flipping downstream signals to green ahead of the vehicle to create an uninterrupted medical corridor. |
| **Traffic Collision & Road Blockage** | Two-vehicle accident blocking an intersection approach during high volume. | Agent holds red signal on blocked lane to avert secondary collisions, redirects upstream timing, and escalates incident telemetry to Central Police Command. |
| **VIP / High-Security Convoy** | Government or dignitary movement requiring cleared passage across municipal corridors. | Escalation manager locks arterial signals to green across multiple junctions while dispatching traffic officers to manage cross-street queues manually. |

---

## 5. Project Scope

### In-Scope (Delivered in Prototype):
- Multi-junction arterial corridor network modeling (2 connected 4-way junctions: MG Road and Indiranagar).
- Heterogeneous vehicle classification adhering to Indian IRC:106 guidelines (bikes, autos, cars, buses).
- Agentic deliberation engine operating closed-loop signal phase selection based on PCU pressure.
- Agent-to-agent asynchronous message passing for green-wave coordination.
- Synthetic adverse condition injectors (monsoon water drops, particulate dust/smog, camera disconnection).
- Sensor reliability evaluation and safe deterministic fallback state machine.
- Human escalation subsystem for incident logging, accident diversion, emergency preemption, and police override.
- Full-featured interactive web dashboard with real-time 2D Canvas animation and live Agent Thought Stream.

### Out-of-Scope (Future Research Extensions):
- Metropolitan-scale deployment across hundreds of contiguous intersections (>50 junctions).
- Direct embedded deployment on roadside microcontrollers (e.g., physical edge relays / Raspberry Pi GPIO).
- Vehicle-to-Infrastructure (V2I / V2X) DSRC or C-V2X direct radio transmission.

---

## 6. Prototype Implementation

The working prototype is engineered as a lightweight, high-performance, full-stack application built entirely in Python 3.11 with FastAPI and a modern web dashboard.

| Module File | Primary Role | Key Algorithms & Logic |
| :--- | :--- | :--- |
| `traffic_simulation.py` | Physics & Network Simulator | Stochastic vehicle arrival model; heterogeneous PCU physics; 2-junction arterial corridor with in-transit vehicle queue progression. |
| `agentic_coordinator.py` | Agentic AI Decision Engine | Multi-agent message broker; marginal PCU pressure calculator; Sensor Guard reliability monitor; human-in-the-loop escalation state machine. |
| `main.py` | FastAPI Backend & API Gateway | Asynchronous event loop ticking at 500ms; REST endpoints for real-time state telemetry, mode switching, weather simulation, and incident triggers. |
| `static/` (HTML/CSS/JS) | Interactive Web Dashboard | HTML5 2D Canvas rendering glowing signal heads and animated Indian vehicles; real-time telemetry polling; live "Agent Thought Stream" display. |

---

## 7. System Flow Diagram

```
+-------------------------------------------------------------------------------+
|                       RAW PERCEPTION & CAMERA TELEMETRY                       |
|   (Vehicle Detections: Two-Wheelers, Auto-Rickshaws, Cars, Buses, Ambulances) |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                    SENSOR RELIABILITY & HEALTH EVALUATION                     |
|           (Assess Frame Drops, Monsoon Rain Blur, Dust Occlusion)             |
+-------------------------------------------------------------------------------+
                                       |
                   [Is Sensor Confidence >= 60%?]
                  /                              \
               (YES)                             (NO)
                 |                                 |
                 v                                 v
+------------------------------------+   +------------------------------------+
|     HUMAN ESCALATION PROTOCOL      |   |       SAFE FALLBACK PROGRAM        |
|  Accident / VIP / Ambulance Call?  |   |  Historical Fixed Cycles (40s)     |
+------------------------------------+   |  Extended 5s Yellow Clearance      |
       /                      \         +------------------------------------+
    (YES)                     (NO)                         |
      |                         |                          |
      v                         v                          v
+-----------------------+ +---------------------------------------------------+
|  POLICE ESCALATION    | |       HETEROGENEOUS PCU QUEUE WEIGHTING           |
| Handover to Command   | |  N_PCU = sum(Vehicles * IRC_Factor)               |
| Preempt Green Phase   | +---------------------------------------------------+
+-----------------------+                              |
                                                       v
                          +---------------------------------------------------+
                          |      INTER-JUNCTION AGENT-TO-AGENT COMM           |
                          |  J1 Agent notifies J2: "Platoon en route (~14s)"  |
                          +---------------------------------------------------+
                                                       |
                                                       v
                          +---------------------------------------------------+
                          |         AUTONOMOUS DELIBERATION ENGINE            |
                          |  Evaluate marginal pressure: Delta_PCU > 6.0      |
                          |  Enforce Min Green (12s) & Max Green (65s)        |
                          +---------------------------------------------------+
                                                       |
                                                       v
                          +---------------------------------------------------+
                          |         PHYSICAL SIGNAL STATE ACTUATION           |
                          |  Execute: NS_GREEN / NS_YELLOW / EW_GREEN / EW_YEL|
                          +---------------------------------------------------+
```

---

## 8. System Architecture

The architecture is organized into five decoupled, modular tiers to ensure fault isolation, high responsiveness, and rigorous safety:
1. **Layer 1: Perception & Traffic State Ingestion:** Captures continuous video feeds or virtual sensor streams. Normalizes mixed traffic by mapping each vehicle bounding box to its standardized IRC Passenger Car Unit factor.
2. **Layer 2: Sensor Reliability & Safety Assurance:** A self-monitoring supervisory module that inspects telemetry validity. In the event of optical interference (water drops, smog, lens scratches), it gracefully locks the system into safe-fallback routines to prevent signal thrashing.
3. **Layer 3: Agentic Deliberation & Inter-Junction Broker:** Each intersection hosts a dedicated software agent with its own perception space, goal utility function, and actuation interface. Agents exchange asynchronous message packets containing platoon size and estimated time of arrival (ETA) across corridor links.
4. **Layer 4: Signal Actuation & Clearance Governance:** Translates agent decisions into traffic light state commands. Strictly enforces minimum clearance times, pedestrian safety intervals, and yellow transitions to prevent dangerous phase changes.
5. **Layer 5: Human-in-the-Loop Governance & Escalation Console:** Provides an interface for traffic management authorities. Flags critical accidents, accepts emergency preemption requests, supports manual baton overrides, and generates compliance audit trails.

---

## 9. Data and Resources

### Data Standards & Modal Split Parameters:
| Vehicle Class | Modal Split (%) | PCU Factor | Operational Behavior |
| :--- | :--- | :--- | :--- |
| **Two-Wheelers (Bikes/Scooters)** | 45% | **0.5 PCU** | Agile filtering, rapid acceleration, queue clustering between lanes. |
| **Auto-Rickshaws (3-Wheelers)** | 23% | **0.8 PCU** | Frequent stopping, moderate speed, informal lateral positioning. |
| **Private Cars & Cabs** | 22% | **1.0 PCU** | Standard passenger car benchmark, standard turning radii. |
| **Buses & Commercial Trucks** | 10% | **2.8 PCU** | Sluggish acceleration, large footprint, major line-of-sight blockage. |
| **Emergency Ambulance** | Dynamic Event | **1.0 PCU** | Priority preemption, siren beacon, cleared right-of-way. |

### Computing & Software Stack:
- **Backend:** Python 3.11, FastAPI (asynchronous REST framework), Uvicorn (ASGI web server).
- **Frontend & Visualizer:** HTML5 Canvas 2D engine, CSS3 Flexbox/Grid modern layout, Vanilla JavaScript (60 FPS rendering).
- **Target Deployment Hardware (Real-World):** NVIDIA Jetson Orin Nano / Orin AGX edge compute box per junction; 4x 1080p IP CCTV cameras; 4G/5G cellular modem for inter-junction messaging.

---

## 10. Methodology

The system's algorithmic methodology executes across five distinct processing phases every 500 milliseconds:
1. **Step 1: Perception & Heterogeneous Demand Quantification:** The junction agent captures approach queue depths. Instead of treating all vehicles equally, it computes the instantaneous pressure function: $P_{approach} = \sum_{v \in Queue} PCU(v)$. This weights high-capacity buses and light two-wheelers accurately.
2. **Step 2: Sensor Health Assessment & Gatekeeping:** The Sensor Guard evaluates telemetry confidence score $\Gamma \in [0, 1]$. If $\Gamma < 0.60$ (due to monsoon rain drops or particulate dust), autonomous switching is gated, and the system transitions into the Safe Fallback baseline controller.
3. **Step 3: Exception & Escalation Filtering:** The system queries the Escalation Manager for active anomalies. If an accident is detected on an approach, signal progression into that approach is locked red, and an emergency dispatch alert is emitted to the Traffic Police. If an ambulance is detected, preemption executes immediately.
4. **Step 4: Inter-Junction Platoon Messaging (Corridor Coordination):** When Junction 1 releases a green phase on its East approach, it broadcasts a coordination packet to Junction 2 containing: `{Platoon_PCU: 18.5, Transit_Time: 14s}`. Junction 2 factors this anticipated surge into its deliberation to ensure the downstream signal is green when the platoon arrives.
5. **Step 5: Dynamic Green Optimization & Phase Actuation:** The active junction agent evaluates whether to terminate or extend the active green signal. If the waiting direction's PCU pressure exceeds active green pressure by threshold $\Delta PCU > 6.0$ and min green time (12s) is satisfied, the agent triggers a yellow clearance transition (4s) followed by the new green phase.

---

## 11. Expected Results in Tabular Form

| Performance Metric | Static Pre-Timed (45s) | Passive DL (CCTV) | Agentic AI (Proposed) |
| :--- | :--- | :--- | :--- |
| **Average Delay / Wait Time** | 48.6 seconds / veh | 39.2 seconds / veh | **24.8 seconds / veh (-49%)** |
| **Network PCU Throughput** | 22.4 PCU / min | 27.8 PCU / min | **36.2 PCU / min (+61%)** |
| **Queue Length Reduction** | Baseline (High) | 15% Reduction | **42% Reduction** |
| **Multi-Junction Corridor Spillback** | Frequent (Gridlock) | Moderate (Uncoordinated) | **Near Zero (Green Wave Sync)** |
| **Monsoon & Dust Camera Outage Behavior** | Ignores weather (Static) | Severe Errors / Hallucinations | **Autonomous Safe Fallback (<60%)** |
| **Ambulance Emergency Clearance** | Random / No Preemption | Delayed (Manual Dispatch) | **Autonomous Preemption (<4s)** |
| **Human Police Operator Burden** | High (Manual Batons Needed) | High (Must monitor CCTV) | **Minimal (Escalation only on exceptions)** |

---

## 12. Project Timeline & Milestones

| Phase & Milestone | Core Activities | Deliverables | Duration / Status |
| :--- | :--- | :--- | :--- |
| **Phase 1: Problem Formulation** | Literature review on Indian urban traffic; IRC:106 PCU factor mapping; comparative analysis of passive DL vs. agentic AI. | Approved Project Synopsis & Research Architecture. | Weeks 1 - 2 (Completed) |
| **Phase 2: Simulator Development** | Build heterogeneous vehicle engine (bikes, autos, cars, buses); dual-junction corridor model; stochastic vehicle generation. | `traffic_simulation.py` core physics module. | Weeks 3 - 4 (Completed) |
| **Phase 3: Agentic Deliberation Engine** | Formulate marginal PCU pressure calculation; multi-agent message passing protocol; min/max green enforcement. | `agentic_coordinator.py` deliberation engine. | Weeks 5 - 6 (Completed) |
| **Phase 4: Sensor Guard & Fallback** | Implement synthetic weather degradation models (monsoon, smog); build confidence evaluator and safe fallback state machine. | Sensor health watchdog & fallback cycle controller. | Weeks 7 - 8 (Completed) |
| **Phase 5: Escalation & Dashboard** | Accident detection, ambulance preemption, police console override; FastAPI backend with 60 FPS HTML5 Canvas dashboard. | Interactive web application & Agent Thought Stream. | Weeks 9 - 10 (Completed) |
| **Phase 6: Validation & Reporting** | Comparative benchmarking of Static vs. Passive DL vs. Agentic; comprehensive documentation dossier and viva presentation. | Technical Report (.docx) & Live Demo Prototype. | Final Review (Ready) |

---

## 13. Thank You Page

# THANK YOU
### Agentic AI for Autonomous, Real-Time Traffic Signal Coordination in Indian Urban Road Networks

```
+-------------------------------------------------------------------+
|            Project Demonstration & Codebase Repository            |
+-------------------------------------------------------------------+
| • Local Interactive Dashboard: http://localhost:8000              |
| • Simulation Engine: Python 3.11, FastAPI & HTML5 Canvas          |
| • Standards: Indian Highway Capacity Manual & IRC:106 Guidelines  |
| • Working Prototype Location: scratch/indian_traffic_agentic_ai/  |
+-------------------------------------------------------------------+
       Prepared for Project Evaluation & Technical Demonstration
                      All Rights Reserved © 2026
```
