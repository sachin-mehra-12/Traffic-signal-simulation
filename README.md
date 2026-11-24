# Agentic AI for Autonomous, Real-Time Traffic Signal Coordination in Indian Urban Road Networks

A working research prototype demonstrating an **Agentic Multi-Junction Traffic Signal Coordination System** tailored for Indian urban road environments.

---

## 🚀 Quick Start (Running Tomorrow's Demo)

### 1. Requirements
- Python 3.9+ (Installed and tested with Python 3.11)
- Minimal libraries: `fastapi`, `uvicorn`, `pydantic`

### 2. Run the Application
Open a terminal in this folder and run:
```bash
python main.py
```
*(Or on Windows, simply double-click `run.bat`)*

### 3. Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🎯 How the Project Addresses the Research Objectives

| Research Document Objective | Implementation in this Prototype |
| :--- | :--- |
| **1. Agentic AI vs Passive DL** | Implemented 3 switchable paradigms: **Static Pre-Timed** (45s cycle), **Passive DL** (CCTV count thresholding), and **Agentic AI** (Autonomous goal deliberation, multi-step queue balancing, and inter-junction communication). |
| **2. Heterogeneous Indian Traffic** | Explicit modeling of Indian modal split: **Two-Wheelers** (PCU 0.5), **Auto-Rickshaws** (PCU 0.8), **Cars/Cabs** (PCU 1.0), and **City Buses** (PCU 2.8). Decisions are made using **PCU Pressure Differential ($\Delta PCU$)** instead of raw car counts. |
| **3. Sensor Reliability & Weather Outages** | Built-in **Sensor Guard Module**: Evaluates vision confidence. Under **Monsoon rain (42%)**, **Dust/Smog (52%)**, or **Camera Outage (5%)**, the agent detects degraded telemetry and shifts into **Safe Fallback Mode** (historical cycle + caution transition) rather than making erratic decisions. |
| **4. Human Escalation Protocols** | Routine traffic is managed 100% autonomously. Critical exceptions (**Accident / Lane Blockage**, **VIP Green Corridor**, **Ambulance Preemption**, or **Manual Police Override**) instantly trigger human-in-the-loop escalation alerts to the Traffic Police Command Center. |

---

## 🏗️ Architecture & Core Components

```
                +------------------------------------------------+
                |          Indian Urban Road Network             |
                |  Junction 1 (MG Road) <---> Junction 2 (Indira)|
                +------------------------------------------------+
                                       |
                   [Camera & IoT Telemetry Stream]
                                       |
                                       v
                +------------------------------------------------+
                |        Module 1: Sensor Guard & Reliability    |
                |      (Monsoon Rain / Dust / Outage Filter)     |
                +------------------------------------------------+
                       | (>60% Confidence)           | (<60% Fail)
                       v                             v
+------------------------------------+      +--------------------+
|  Module 2: Agentic Decision Engine |      | Safe Fallback Mode |
|  - PCU Weighted Queue Deliberation |      | (Fixed Base Cycle) |
|  - J1 <-> J2 Inter-Agent Comms     |      +--------------------+
|  - Dynamic Green Wave Extension    |
+------------------------------------+
                   |
     [Is Exception Detected?]
      /                    \
    (No)                   (Yes: Accident / VIP / Ambulance)
    /                        \
Routine Phase Adjust      +--------------------------------------+
                          | Module 3: Human Escalation Protocol  |
                          | Dispatch alert to Police Command HQ  |
                          +--------------------------------------+
```

### 1. Heterogeneous Traffic Engine (`traffic_simulation.py`)
- Real-time physics simulator supporting two interconnected 4-way junctions along an arterial corridor (e.g., MG Road and Indiranagar).
- Vehicles obey Indian IRC:106 guidelines for Passenger Car Units:
  - **Two-Wheelers (Bikes/Scooters)**: 45% modal share, PCU = 0.5, agile filtering.
  - **Auto-Rickshaws**: 23% modal share, PCU = 0.8, intermediate speed.
  - **Private Cars / Taxis**: 22% modal share, PCU = 1.0.
  - **City Buses / Commercial Trucks**: 10% modal share, PCU = 2.8.
- Cleared eastward vehicles from Junction 1 realistically travel along the 400m corridor and join Junction 2's western queue after transit delay.

### 2. Multi-Junction Agentic Coordinator (`agentic_coordinator.py`)
- **Perception Step**: Converts heterogeneous vehicle counts into cumulative PCU pressure.
- **Agent-to-Agent Message Passing**: Junction 1 Agent calculates the discharged platoon size and transmits an early warning packet to Junction 2 (`"18.5 PCU en route Eastbound, ETA ~14s"`).
- **Green Wave Deliberation**: Junction 2 schedules green phase pre-alignment to let the platoon pass without stopping, preventing corridor spillback.

### 3. Sensor Health & Safe-Fallback Guard (`agentic_coordinator.py`)
- Monitors camera and vision inference confidence.
- When weather events (e.g., torrential monsoon downpours or heavy particulate dust storms) reduce confidence below 60%, the agent refuses to make volatile timing decisions and falls back to a deterministic, fail-safe historical timing program with extended yellow caution intervals.

### 4. Human-in-the-Loop Escalation Manager
- **Accident Handler**: Freezes signal advancement into the blocked approach, updates upstream agents to divert traffic, and dispatches an emergency report to the human police console.
- **Emergency Ambulance Preemption**: Grants immediate green priority across the active path.
- **VIP Convoy / Police Override**: Allows manual traffic police takeover at any moment.

---

## 🎬 Step-by-Step Presentation Guide for Tomorrow

When presenting the working prototype to your evaluators or professors:

### Step 1: Show the Live Indian Traffic Environment
1. Open `http://127.0.0.1:8000`.
2. Point out the **2D Visualizer**: Show the two junctions (MG Road and Indiranagar) and explain the color-coded heterogeneous vehicles (cyan bikes, yellow autos, white cars, orange buses).
3. Highlight that decision-making uses **PCU (Passenger Car Units)** rather than raw car counts, reflecting the real Indian traffic reality.

### Step 2: Demonstrate Agentic AI vs Static Signals
1. Click **`⏱️ Static Timer (45s)`**: Observe how queues build up unnecessarily on busy approaches while empty approaches get wasted green time. Average wait time rises.
2. Click **`🤖 Agentic AI (Proposed)`**: Show how the agents autonomously detect queue pressure differentials and adjust green times dynamically. Average wait time drops significantly.
3. Direct attention to the **Agent Thought Stream** on the right side: Show the real-time reasoning logs (`[REASONING]`, `[COORDINATION]`).

### Step 3: Demonstrate Multi-Junction Coordination (Green Wave)
1. Point to the arterial road connecting Junction 1 and Junction 2.
2. Point out the coordination logs in the Agent Thought Stream:
   > `[J1-J2 Coordinator] J1 Agent -> J2 Agent: Arterial Platoon alert! 16.2 PCU en route Eastbound. Synchronizing Green Wave.`
3. Explain that without multi-junction agent communication, downstream junctions choke when upstream signals turn green.

### Step 4: Demonstrate Sensor Failure & Monsoon Safe Fallback
1. Click the **`🌧️ Monsoon (42%)`** or **`❌ Camera Cut (5%)`** button.
2. Watch the **Sensor Health** metric drop below 60% and turn red.
3. Observe the Agent Thought Stream:
   > `[SensorGuardModule] Adverse Condition [MONSOON]: Camera vision confidence is 42% (< 60%). Engaging Fail-Safe Baseline Timing.`
4. Explain to the evaluators: *"Global smart traffic models assume 100% reliable IoT sensors. In Indian cities, monsoon rain or dust blinds cameras. Our system includes an autonomous Sensor Guard that detects degraded telemetry and prevents hallucinated signal switching."*

### Step 5: Demonstrate Exception & Human Escalation
1. Click **`💥 Simulate Accident`**:
   - The red hazard alert icon pulses on the road canvas.
   - The top banner flashes: `🚨 INCIDENT DETECTED: Escalating to Human Traffic Police Command!`
   - The agent locks the blocked lane to red and requests human dispatch.
2. Click **`🚑 Ambulance Call`**:
   - Notice the emergency ambulance with flashing beacon.
   - The agent instantly preempts the signal to green and clears the intersection.
3. Click **`👮 Police Override`**: Show that human traffic police retain ultimate override authority at all times.

---

## 📁 Project Structure

```
indian_traffic_agentic_ai/
│
├── main.py                     # FastAPI server, REST API endpoints, background simulation loop
├── traffic_simulation.py       # Indian heterogeneous traffic physics, PCU modeling, dual-junction corridor
├── agentic_coordinator.py      # Agentic AI deliberation, J1-J2 coordination, Sensor Guard, Escalation
├── run.bat                     # Windows one-click startup script
├── requirements.txt            # Minimal dependencies (fastapi, uvicorn, pydantic)
├── README.md                   # Full documentation & project presentation guide
│
└── static/
    ├── index.html              # Modern, responsive dashboard interface
    ├── style.css               # Clean dark-mode UI, glowing signal heads, responsive cards
    └── app.js                  # HTML5 Canvas 2D road renderer, real-time telemetry polling
```
