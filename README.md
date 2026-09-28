# SMART CROWD SAFETY & INCIDENT MONITORING SYSTEM
**AI-Powered Real-Time Video Surveillance & Crowd Hazard Perception Platform**

Built for college viva and research demonstrations. Demonstrates how modern computer vision and multi-model YOLO pipelines can monitor crowd density, detect critical hazards (fire, smoke), enforce safe occupancy limits, and manage incident life-cycles in real time.

---

## 1. System Architecture

```
                                  [ Operator Web Browser ]
                               (React 18 + Dark Neo-Brutalism)
                                    /                 \
                     MJPEG Video   /                   \ WebSocket
                        Stream    /                     \ (Telemetry & Alerts)
                                 v                       v
                         +--------------------------------------+
                         |        FastAPI Backend Engine        |
                         +--------------------------------------+
                                     |             |
                        OpenCV Frame |             | SQLite Database
                        Reader Loop  v             v (Sessions, Incidents,
                         +---------------+            Crowd Metrics)
                         | ModelManager  |
                         +---------------+
                         /               \
       (Every 2 Frames) /                 \ (Every 5 Frames)
                       v                   v
            [ YOLOv8n (Person) ]    [ YOLOv8n (Fire/Smoke) ]
            - Person Bounding Box    - Verified D-Fire Model
            - Head/Foot Tracking     - Failsafe Mode if Missing
                       \                   /
                        \                 /
                         v               v
                         +---------------+
                         |  Risk Engine  |
                         +---------------+
                         - Configurable Safe Capacity
                         - Crowd Level Hysteresis (Safe, Mod, High, Critical)
                         - Temporal Stabilization (Persistence Frames)
                                 |
                                 v
                         [ IncidentManager ]
                         - INC-XXXX Generation
                         - Operator Acknowledge / Resolve
                         - Chronological Event Log
```

---

## 2. Key Engineering Highlights

1. **Separated Video and Telemetry Transports**:
   - **Video Feed**: Streamed via an efficient MJPEG HTTP endpoint (`/api/sessions/{id}/stream`) with custom OpenCV surveillance HUD and bounding box overlays.
   - **Telemetry & Alerts**: Streamed via WebSocket (`/ws/monitor/{id}`) with zero lag, delivering frame metrics, occupancy percentages, and real-time alert dispatches.

2. **Independent Multi-Model YOLO Scheduling**:
   - Person detection runs every **2 frames**.
   - Fire/Smoke detection runs every **5 frames**.
   - Detections are cached between inference intervals to ensure smooth, non-flickering overlays while conserving CPU/GPU cycles.

3. **Temporal Stabilization & Hysteresis**:
   - **Anti-Flicker Hysteresis**: Prevents rapid status oscillation around threshold boundaries (e.g. 50% upward -> MODERATE, but drops to SAFE only below 46%).
   - **Persistence Requirement**: Critical incidents (Fire, Smoke, Critical Crowd Density) require positive detection across $N$ consecutive inference frames before an incident is created, preventing false positives from single-frame optical noise.

4. **Multi-Model Failsafe**:
   - If `fire_smoke.pt` is not present, the system cleanly displays `FIRE/SMOKE MODEL: ○ NOT INSTALLED` and crowd monitoring continues uninterrupted.
   - Weights can be installed on-demand from the UI settings modal.

5. **Resource-Efficient Metric Persistence**:
   - Live telemetry updates every frame on the dashboard, while historical metrics are persisted to SQLite at approximately **1 sample per second** to prevent database bloat.

6. **Future-Ready ZoneManager**:
   - Built-in polygonal zone definition service for restricted-area entry alerts and targeted zone counting.

---

## 3. Technology Stack

- **Frontend**: React 18, Vite, Recharts, Lucide-React, Tailwind CSS.
- **Backend**: Python 3.12, FastAPI, Uvicorn, WebSockets, OpenCV.
- **AI Models**: Ultralytics YOLOv8n (COCO) + YOLOv8n Fire/Smoke (`rabahdev/fire-smoke-yolov8n`, AGPL-3.0).
- **Database**: SQLite with SQLAlchemy 2.0.

---

## 4. Quick Start Guide

### Step 1: Start Backend Server
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
*The FastAPI backend will automatically serve both the REST API and the pre-built React frontend at `http://127.0.0.1:8000/`.*

### Step 2: (Optional) Run Frontend in Development Mode
If you want hot-reloading for frontend modifications:
```bash
cd frontend
npm run dev
```
*Access the development dashboard at `http://127.0.0.1:5173/`.*

---

## 5. College Viva Demonstration Walkthrough

When presenting to examiners or professors, follow this structured demo:

1. **Open the System**:
   - Navigate to `http://127.0.0.1:8000/`.
   - Point out the **Neo-Brutalist surveillance aesthetic**: high contrast, bold borders, clear telemetry.

2. **Select Video Source**:
   - Either drag and drop your **Blender rendered MP4 crowd simulation**, or click **"USE DEMO SIMULATION"** to use the built-in developer verification video.
   - Adjust the **Safe Crowd Capacity** (e.g. set to 35 persons).

3. **Start Analysis & Review Initialization Steps**:
   - Click **START ANALYSIS**.
   - Watch the multi-step initialization sequence:
     1. `INITIALIZING MONITORING SESSION`
     2. `LOADING YOLOv8...`
     3. `PREPARING VIDEO...`
     4. `AI SYSTEM READY`

4. **Observe the Live Dashboard**:
   - **Video Monitoring Panel (70%)**: Show the real-time OpenCV overlay with person bounding boxes, labels, and bottom telemetry HUD (`YOLOv8n | 24 FPS | FRAME XXX | AI ACTIVE`).
   - **Active Alerts Panel (30%)**: Watch dynamic alert cards pop up as crowd density increases or hazards emerge.
   - **Monitoring KPI Cards**:
     - `PEOPLE`: Live count & session peak.
     - `CROWD OCCUPANCY`: Dynamic percentage and colored segmented bar.
     - `HAZARDS`: Count of detected flame/smoke/violation events.
     - `MODEL`: Average confidence & active AI engine.
   - **Crowd Density Timeline Graph**: Point to the Recharts timeline displaying occupancy trends against `SAFE`, `MODERATE`, `HIGH`, and `CRITICAL` guidelines.
   - **Event Log**: Chronological operational timeline tracking significant milestones.

5. **Demonstrate Incident Workflow**:
   - When an alert appears (e.g., `CRITICAL FIRE DETECTED` or `HIGH CROWD OCCUPANCY`), click **ACKNOWLEDGE**.
   - The status updates to `ACKNOWLEDGED` with an operator event recorded in the Event Log.
   - Once resolved, click **RESOLVE**.

6. **Demonstrate Configuration & Failsafe**:
   - Click the **CONFIG** button in the header.
   - Demonstrate dynamic safe capacity adjustment and model status inspection.

---

