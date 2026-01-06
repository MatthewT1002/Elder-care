/* ===== CONFIG ===== */
const USE_SIMULATED_DATA = true; // Set false to use backend APIs

/* ===== DOM ELEMENTS ===== */
const doorState = document.getElementById("doorState");
const alertText = document.getElementById("alert");
const cameraStatus = document.getElementById("cameraStatus");

/* ===== UPDATE FUNCTION ===== */
async function getData() {
  if (USE_SIMULATED_DATA) {
    // Simulated data
    const doorLocked = Math.random() > 0.3;      // 70% chance locked
    const emergency = Math.random() > 0.8;       // 20% chance alert
    const cameraOnline = Math.random() > 0.1;    // 90% chance online
    updateDashboard(doorLocked, emergency, cameraOnline);

  } else {
    // Live backend example
    try {
      const doorResp = await fetch("/api/door");       // { locked: true/false }
      const alertResp = await fetch("/api/emergency"); // { active: true/false }
      const cameraResp = await fetch("/api/camera-status"); // { online: true/false }

      const doorData = await doorResp.json();
      const alertData = await alertResp.json();
      const cameraData = await cameraResp.json();

      updateDashboard(doorData.locked, alertData.active, cameraData.online);

    } catch (err) {
      console.error("Error fetching live data:", err);
    }
  }
}

/* ===== UPDATE DASHBOARD ===== */
function updateDashboard(locked, emergencyActive, cameraOnline) {
  // Door state
  doorState.innerText = locked ? "Locked" : "Unlocked";
  doorState.className = locked ? "status-normal" : "status-alert";

  // Emergency alert
  if (emergencyActive) {
    alertText.innerText = "EMERGENCY!";
    alertText.classList.add("blink");
  } else {
    alertText.innerText = "No active alerts";
    alertText.classList.remove("blink");
  }

  // Camera status overlay
  cameraStatus.innerText = cameraOnline ? "Online" : "Offline";
  cameraStatus.className = "camera-status " + (cameraOnline ? "online" : "offline");
}

/* ===== INTERVAL ===== */
setInterval(getData, 3000);

/* ===== DARK MODE ===== */
document.getElementById("toggleTheme").onclick = () => {
  document.body.classList.toggle("dark-mode");
};
