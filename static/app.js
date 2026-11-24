/**
 * app.js
 * Real-time 2D Canvas rendering and interactive control logic
 * for the Agentic AI Indian Traffic Signal Coordinator prototype.
 */

const canvas = document.getElementById("trafficCanvas");
const ctx = canvas.getContext("2d");

// Resize canvas to match actual display container size
function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio;
  canvas.height = rect.height * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

// Global State
let simData = null;
let lastLogCount = 0;

// Dimensions & Coordinates
function getLayout() {
  const rect = canvas.getBoundingClientRect();
  const w = rect.width;
  const h = rect.height;

  const j1_cx = w * 0.28;
  const j2_cx = w * 0.72;
  const cy = h * 0.50;
  const roadW = 86; // Road width in pixels

  return { w, h, j1_cx, j2_cx, cy, roadW };
}

// Draw the Road Network
function drawRoadNetwork(layout) {
  const { w, h, j1_cx, j2_cx, cy, roadW } = layout;

  // Background asphalt color
  ctx.fillStyle = "#0f172a";
  ctx.fillRect(0, 0, w, h);

  // East-West Arterial Corridor (Main spine connecting J1 & J2)
  ctx.fillStyle = "#1e293b";
  ctx.fillRect(0, cy - roadW / 2, w, roadW);

  // J1 North-South Road (MG Road)
  ctx.fillRect(j1_cx - roadW / 2, 0, roadW, h);

  // J2 North-South Road (Indiranagar)
  ctx.fillRect(j2_cx - roadW / 2, 0, roadW, h);

  // Junction Intersections (slightly darker box)
  ctx.fillStyle = "#27354a";
  ctx.fillRect(j1_cx - roadW / 2, cy - roadW / 2, roadW, roadW);
  ctx.fillRect(j2_cx - roadW / 2, cy - roadW / 2, roadW, roadW);

  // Lane Dividers (Dashed Yellow/White)
  ctx.strokeStyle = "rgba(250, 204, 21, 0.4)";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([8, 8]);

  // Arterial center line
  ctx.beginPath();
  ctx.moveTo(0, cy);
  ctx.lineTo(w, cy);
  ctx.stroke();

  // J1 NS center line
  ctx.beginPath();
  ctx.moveTo(j1_cx, 0);
  ctx.lineTo(j1_cx, h);
  ctx.stroke();

  // J2 NS center line
  ctx.beginPath();
  ctx.moveTo(j2_cx, 0);
  ctx.lineTo(j2_cx, h);
  ctx.stroke();

  ctx.setLineDash([]); // Reset line dash

  // Zebra Crossings & Stop Lines
  drawZebraCrossing(j1_cx, cy, roadW);
  drawZebraCrossing(j2_cx, cy, roadW);

  // Labels
  ctx.fillStyle = "#94a3b8";
  ctx.font = "bold 11px system-ui";
  ctx.textAlign = "center";
  ctx.fillText("JUNCTION 1 (MG ROAD)", j1_cx, 22);
  ctx.fillText("JUNCTION 2 (INDIRANAGAR)", j2_cx, 22);

  // Corridor indicator arrow
  ctx.fillStyle = "rgba(56, 189, 248, 0.7)";
  ctx.font = "10px system-ui";
  const midX = (j1_cx + j2_cx) / 2;
  ctx.fillText("⇄ Multi-Junction Arterial Corridor (400m) ⇄", midX, cy - roadW / 2 - 8);
}

function drawZebraCrossing(cx, cy, roadW) {
  const half = roadW / 2;
  const stripeW = 4;
  ctx.fillStyle = "rgba(255, 255, 255, 0.25)";

  // North stopline zebra
  for (let x = cx - half + 4; x < cx + half - 4; x += 10) {
    ctx.fillRect(x, cy - half - 10, stripeW, 8);
  }
  // South stopline zebra
  for (let x = cx - half + 4; x < cx + half - 4; x += 10) {
    ctx.fillRect(x, cy + half + 2, stripeW, 8);
  }
  // West stopline zebra
  for (let y = cy - half + 4; y < cy + half - 4; y += 10) {
    ctx.fillRect(cx - half - 10, y, 8, stripeW);
  }
  // East stopline zebra
  for (let y = cy - half + 4; y < cy + half - 4; y += 10) {
    ctx.fillRect(cx + half + 2, y, 8, stripeW);
  }
}

// Render Traffic Lights for a Junction
function drawTrafficSignals(cx, cy, roadW, phase) {
  const is_ns_green = phase === "NS_GREEN";
  const is_ns_yellow = phase === "NS_YELLOW";
  const is_ew_green = phase === "EW_GREEN";
  const is_ew_yellow = phase === "EW_YELLOW";

  const nsColor = is_ns_green ? "#10b981" : is_ns_yellow ? "#f59e0b" : "#ef4444";
  const ewColor = is_ew_green ? "#10b981" : is_ew_yellow ? "#f59e0b" : "#ef4444";

  // North Signal Box
  drawSignalHead(cx - 24, cy - roadW / 2 - 18, nsColor, is_ns_green);
  // South Signal Box
  drawSignalHead(cx + 16, cy + roadW / 2 + 10, nsColor, is_ns_green);
  // West Signal Box
  drawSignalHead(cx - roadW / 2 - 18, cy + 16, ewColor, is_ew_green);
  // East Signal Box
  drawSignalHead(cx + roadW / 2 + 10, cy - 24, ewColor, is_ew_green);
}

function drawSignalHead(x, y, color, isGlowing) {
  ctx.fillStyle = "#030712";
  ctx.strokeStyle = "#374151";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.roundRect(x, y, 14, 14, 3);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x + 7, y + 7, 4.5, 0, Math.PI * 2);
  ctx.fill();

  if (isGlowing) {
    ctx.shadowColor = color;
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(x + 7, y + 7, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0; // Reset
  }
}

// Render Indian Vehicles based on type, PCU, distance, and approach
function drawVehicles(junction, cx, cy, roadW) {
  const queues = junction.queues;
  const laneOffset = 18; // offset from center divider

  // Approach: North (incoming going South)
  if (queues.N && queues.N.vehicles) {
    queues.N.vehicles.forEach((v, idx) => {
      const dist = Math.max(8, v.distance);
      const vx = cx - laneOffset + (v.type === "bike" ? (idx % 2 === 0 ? -6 : 6) : 0);
      const vy = cy - roadW / 2 - dist * 1.6;
      drawSingleVehicle(v, vx, vy, 0);
    });
  }

  // Approach: South (incoming going North)
  if (queues.S && queues.S.vehicles) {
    queues.S.vehicles.forEach((v, idx) => {
      const dist = Math.max(8, v.distance);
      const vx = cx + laneOffset + (v.type === "bike" ? (idx % 2 === 0 ? -6 : 6) : 0);
      const vy = cy + roadW / 2 + dist * 1.6;
      drawSingleVehicle(v, vx, vy, Math.PI);
    });
  }

  // Approach: West (incoming going East)
  if (queues.W && queues.W.vehicles) {
    queues.W.vehicles.forEach((v, idx) => {
      const dist = Math.max(8, v.distance);
      const vx = cx - roadW / 2 - dist * 1.6;
      const vy = cy + laneOffset + (v.type === "bike" ? (idx % 2 === 0 ? -6 : 6) : 0);
      drawSingleVehicle(v, vx, vy, Math.PI / 2);
    });
  }

  // Approach: East (incoming going West)
  if (queues.E && queues.E.vehicles) {
    queues.E.vehicles.forEach((v, idx) => {
      const dist = Math.max(8, v.distance);
      const vx = cx + roadW / 2 + dist * 1.6;
      const vy = cy - laneOffset + (v.type === "bike" ? (idx % 2 === 0 ? -6 : 6) : 0);
      drawSingleVehicle(v, vx, vy, -Math.PI / 2);
    });
  }
}

function drawSingleVehicle(v, x, y, rotation) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(rotation);

  if (v.is_emergency) {
    // Ambulance with flashing beacon
    ctx.fillStyle = "#ffffff";
    ctx.strokeStyle = "#ef4444";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(-6, -11, 12, 22, 3);
    ctx.fill();
    ctx.stroke();

    // Red Cross
    ctx.fillStyle = "#ef4444";
    ctx.fillRect(-1.5, -6, 3, 12);
    ctx.fillRect(-6, -1.5, 12, 3);

    // Flashing light
    const flash = Math.sin(Date.now() / 80) > 0;
    ctx.fillStyle = flash ? "#38bdf8" : "#ef4444";
    ctx.beginPath();
    ctx.arc(0, 0, 3, 0, Math.PI * 2);
    ctx.fill();
  } else if (v.type === "bike") {
    // 2-Wheeler (Motorbike / Scooter)
    ctx.fillStyle = v.color;
    ctx.beginPath();
    ctx.ellipse(0, 0, 3, 6, 0, 0, Math.PI * 2);
    ctx.fill();
    // Rider helmet dot
    ctx.fillStyle = "#0284c7";
    ctx.beginPath();
    ctx.arc(0, 0, 2, 0, Math.PI * 2);
    ctx.fill();
  } else if (v.type === "auto") {
    // Indian 3-Wheeler Auto-rickshaw (Yellow / Green hood)
    ctx.fillStyle = "#15803d"; // dark green base
    ctx.beginPath();
    ctx.roundRect(-5, -7, 10, 14, 2);
    ctx.fill();

    ctx.fillStyle = "#facc15"; // yellow roof
    ctx.beginPath();
    ctx.roundRect(-4.5, -3, 9, 9, 2);
    ctx.fill();
  } else if (v.type === "bus") {
    // Heavy City Bus / Truck
    ctx.fillStyle = "#ea580c";
    ctx.strokeStyle = "#7c2d12";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(-7, -18, 14, 36, 4);
    ctx.fill();
    ctx.stroke();

    // Bus Windshield
    ctx.fillStyle = "#bae6fd";
    ctx.fillRect(-5.5, -16, 11, 4);
  } else {
    // Car / Cab
    ctx.fillStyle = v.color;
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(-5.5, -9, 11, 18, 2);
    ctx.fill();
    ctx.stroke();

    // Windshield
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(-4, -6, 8, 3);
  }

  ctx.restore();
}

// Render Incident / Hazard markers
function drawIncidents(layout, state) {
  const { j1_cx, j2_cx, cy, roadW } = layout;

  if (state.accident_active && state.accident_location) {
    const isJ1 = state.accident_location.startsWith("J1");
    const cx = isJ1 ? j1_cx : j2_cx;
    const ax = cx - 18;
    const ay = cy - roadW / 2 - 25;

    // Pulsing Hazard Icon
    ctx.fillStyle = "rgba(239, 68, 68, 0.3)";
    ctx.beginPath();
    ctx.arc(ax, ay, 18 + Math.sin(Date.now() / 150) * 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#ef4444";
    ctx.font = "bold 14px system-ui";
    ctx.textAlign = "center";
    ctx.fillText("⚠️", ax, ay + 5);

    ctx.font = "bold 10px system-ui";
    ctx.fillText("ACCIDENT - LANE BLOCKED", ax, ay - 14);
  }
}

// Main Render Loop
function render() {
  const layout = getLayout();
  ctx.clearRect(0, 0, layout.w, layout.h);

  drawRoadNetwork(layout);

  if (simData && simData.junctions) {
    const j1 = simData.junctions.J1;
    const j2 = simData.junctions.J2;

    // Draw signals
    drawTrafficSignals(layout.j1_cx, layout.cy, layout.roadW, j1.phase);
    drawTrafficSignals(layout.j2_cx, layout.cy, layout.roadW, j2.phase);

    // Draw vehicles
    drawVehicles(j1, layout.j1_cx, layout.cy, layout.roadW);
    drawVehicles(j2, layout.j2_cx, layout.cy, layout.roadW);

    // Draw incidents
    drawIncidents(layout, simData);

    // Draw Weather overlay if adverse
    if (simData.weather === "MONSOON") {
      drawRainOverlay(layout);
    } else if (simData.weather === "DUST_SMOG") {
      drawSmogOverlay(layout);
    } else if (simData.weather === "SENSOR_FAILURE") {
      drawSensorFailOverlay(layout);
    }
  }

  requestAnimationFrame(render);
}

function drawRainOverlay(layout) {
  ctx.fillStyle = "rgba(30, 58, 138, 0.12)";
  ctx.fillRect(0, 0, layout.w, layout.h);

  ctx.strokeStyle = "rgba(147, 197, 253, 0.4)";
  ctx.lineWidth = 1;
  const time = Date.now() / 10;
  for (let i = 0; i < 40; i++) {
    const x = (i * 27 + (time * 4)) % layout.w;
    const y = (i * 33 + (time * 9)) % layout.h;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - 4, y + 10);
    ctx.stroke();
  }
}

function drawSmogOverlay(layout) {
  ctx.fillStyle = "rgba(180, 83, 9, 0.15)";
  ctx.fillRect(0, 0, layout.w, layout.h);
}

function drawSensorFailOverlay(layout) {
  ctx.fillStyle = "rgba(220, 38, 38, 0.08)";
  ctx.fillRect(0, 0, layout.w, layout.h);
}

// Start rendering
requestAnimationFrame(render);

// -------------------------------------------------------------
// API Sync & Dashboard Updates
// -------------------------------------------------------------
async function fetchState() {
  try {
    const res = await fetch("/api/state");
    if (!res.ok) return;
    const data = await res.json();
    simData = data;
    updateDashboardUI(data);
  } catch (err) {
    console.error("Fetch state error:", err);
  }
}

function updateDashboardUI(data) {
  // Update Metrics
  document.getElementById("avgWait").textContent = data.metrics.avg_wait_seconds + "s";
  document.getElementById("throughput").textContent = data.metrics.throughput_pcu_per_min;
  document.getElementById("clearedVehicles").textContent = data.metrics.cleared_vehicles;
  document.getElementById("sensorHealth").textContent = data.sensor_reliability + "%";

  const sensorHealthCard = document.getElementById("sensorHealthCard");
  if (data.sensor_reliability < 60) {
    sensorHealthCard.style.setProperty("--card-accent", "#ef4444");
    document.getElementById("sensorHealthSub").textContent = "Safe-Fallback Activated";
    document.getElementById("sensorHealthSub").style.color = "#ef4444";
  } else {
    sensorHealthCard.style.setProperty("--card-accent", "#10b981");
    document.getElementById("sensorHealthSub").textContent = "Vision AI Nominal";
    document.getElementById("sensorHealthSub").style.color = "#10b981";
  }

  // Active Mode indicator
  document.getElementById("activeModeBadge").textContent = data.control_mode;
  document.querySelectorAll(".btn-mode").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.mode === data.control_mode);
  });

  // Weather indicator
  document.querySelectorAll(".btn-weather").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.weather === data.weather);
  });

  // Escalation Banner
  const alertBanner = document.getElementById("escalationBanner");
  const alertText = document.getElementById("escalationBannerText");
  if (data.accident_active || data.vip_active || data.police_override || data.emergency_vehicle_active) {
    alertBanner.classList.add("active");
    if (data.accident_active) {
      alertText.textContent = `🚨 ACCIDENT ALERT: Road blockage at ${data.accident_location}. Human Police Dispatch Escalated!`;
    } else if (data.vip_active) {
      alertText.textContent = "🚔 VIP CONVOY PROTOCOL: Coordinated arterial green corridor held for escort.";
    } else if (data.police_override) {
      alertText.textContent = "👮 MANUAL POLICE TAKEOVER: Autonomous agent yielded control to human traffic officer.";
    } else if (data.emergency_vehicle_active) {
      alertText.textContent = "🚑 AMBULANCE PREEMPTION: High-priority corridor cleared for emergency vehicle.";
    }
  } else {
    alertBanner.classList.remove("active");
  }

  // Update Logs Stream
  if (data.logs) {
    const stream = document.getElementById("logStream");
    // Only update if logs changed
    const newLogs = data.logs.slice(0, 15);
    stream.innerHTML = newLogs.map(l => `
      <div class="log-entry level-${l.level}">
        <div class="log-meta">
          <span><span class="log-cat">${l.category}</span> ${l.agent}</span>
          <span>${l.timestamp}</span>
        </div>
        <div class="log-msg">${l.message}</div>
        ${l.details && Object.keys(l.details).length > 0 ? 
          `<div class="log-details">${JSON.stringify(l.details)}</div>` : ''}
      </div>
    `).join("");
  }
}

// Periodic Polling
setInterval(fetchState, 500);
fetchState();

// -------------------------------------------------------------
// Interactive Control Handlers
// -------------------------------------------------------------
async function postAPI(endpoint, body = {}) {
  await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  fetchState();
}

// Mode Buttons
document.querySelectorAll(".btn-mode").forEach(btn => {
  btn.addEventListener("click", () => {
    postAPI("/api/set_mode", { mode: btn.dataset.mode });
  });
});

// Weather Buttons
document.querySelectorAll(".btn-weather").forEach(btn => {
  btn.addEventListener("click", () => {
    postAPI("/api/set_weather", { weather: btn.dataset.weather });
  });
});

// Incidents & Escalation
document.getElementById("btnAccident").addEventListener("click", () => {
  postAPI("/api/trigger_accident", { junction: "J1", approach: "N" });
});

document.getElementById("btnClearAccident").addEventListener("click", () => {
  postAPI("/api/clear_accident");
});

document.getElementById("btnAmbulance").addEventListener("click", () => {
  postAPI("/api/spawn_ambulance", { junction: "J1", approach: "W" });
});

document.getElementById("btnVip").addEventListener("click", () => {
  postAPI("/api/trigger_vip");
});

document.getElementById("btnClearVip").addEventListener("click", () => {
  postAPI("/api/clear_vip");
});

let policeOverride = false;
document.getElementById("btnPoliceOverride").addEventListener("click", () => {
  policeOverride = !policeOverride;
  const btn = document.getElementById("btnPoliceOverride");
  btn.classList.toggle("active", policeOverride);
  btn.textContent = policeOverride ? "👮 Restore AI Control" : "👮 Police Override";
  postAPI("/api/police_override", { override: policeOverride });
});

document.getElementById("btnReset").addEventListener("click", () => {
  postAPI("/api/reset");
});
