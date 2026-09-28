import React, { useState, useEffect, useRef } from 'react';
import Header from '../components/Header';
import VideoPlayer from '../components/VideoPlayer';
import AlertsPanel from '../components/AlertsPanel';
import StatsGrid from '../components/StatsGrid';
import CrowdDensityChart from '../components/CrowdDensityChart';
import EventLogPanel from '../components/EventLogPanel';
import ConfigModal from '../components/ConfigModal';

import {
  pauseSession,
  resumeSession,
  getIncidents,
  acknowledgeIncident,
  resolveIncident,
  getEvents,
  getMetrics,
  updateConfig,
  downloadFireModel,
} from '../services/api';
import { MonitorWebSocket } from '../services/websocket';

export default function DashboardPage({ session, onBackToUpload, systemStatus, onRefreshSystemStatus }) {
  const [telemetry, setTelemetry] = useState({
    person_count: 0,
    peak_people: session?.peak_people || 0,
    occupancy: 0,
    crowd_level: 'SAFE',
    hazards_count: 0,
    avg_confidence: 0,
    fps: session?.fps || 24,
    frame_index: 0,
    total_frames: session?.total_frames || 0,
    timestamp: '00:00',
    safe_capacity: session?.safe_capacity || 50,
  });

  const [incidents, setIncidents] = useState([]);
  const [events, setEvents] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [streamStatus, setStreamStatus] = useState('LIVE');
  const [isConfigOpen, setIsConfigOpen] = useState(false);

  const wsRef = useRef(null);

  // Initial fetch of existing incidents & events from DB
  useEffect(() => {
    if (!session?.id) return;

    const loadInitialData = async () => {
      try {
        const [incList, evtList, metricList] = await Promise.all([
          getIncidents(session.id),
          getEvents(session.id),
          getMetrics(session.id),
        ]);
        if (incList) setIncidents(incList);
        if (evtList) setEvents(evtList);
        if (metricList && metricList.length > 0) {
          setChartData(
            metricList.map((m) => ({
              time: m.video_timestamp,
              occupancy: m.occupancy,
              persons: m.person_count,
            }))
          );
        }
      } catch (err) {
        console.error('Failed to load initial session data:', err);
      }
    };

    loadInitialData();
  }, [session?.id]);

  // Connect WebSocket for live telemetry & incident push
  useEffect(() => {
    if (!session?.id) return;

    const handleWsMessage = (msg) => {
      if (msg.type === 'telemetry') {
        setTelemetry((prev) => ({
          ...prev,
          person_count: msg.person_count,
          peak_people: msg.peak_people,
          occupancy: msg.occupancy,
          crowd_level: msg.crowd_level,
          hazards_count: msg.hazards_count,
          avg_confidence: msg.avg_confidence,
          fps: msg.fps,
          frame_index: msg.frame_index,
          total_frames: msg.total_frames,
          timestamp: msg.timestamp,
          safe_capacity: msg.safe_capacity,
        }));

        // Append to density timeline chart (keep latest 50 points)
        setChartData((prev) => {
          const lastPoint = prev[prev.length - 1];
          if (lastPoint && lastPoint.time === msg.timestamp) {
            return prev;
          }
          const next = [...prev, { time: msg.timestamp, occupancy: msg.occupancy, persons: msg.person_count }];
          return next.slice(-60);
        });
      } else if (msg.type === 'incident_created') {
        const newInc = msg.data;
        setIncidents((prev) => {
          if (prev.some((i) => i.id === newInc.id)) return prev;
          return [newInc, ...prev];
        });
        if (msg.event) {
          setEvents((prev) => [msg.event, ...prev]);
        }
      }
    };

    const handleStatusChange = (status) => {
      setStreamStatus(status === 'CONNECTED' ? 'LIVE' : 'RECONNECTING');
    };

    const ws = new MonitorWebSocket(session.id, handleWsMessage, handleStatusChange);
    ws.connect();
    wsRef.current = ws;

    return () => {
      ws.disconnect();
    };
  }, [session?.id]);

  const handlePause = async () => {
    try {
      await pauseSession(session.id);
      setIsPaused(true);
      setStreamStatus('PAUSED');
    } catch (e) {
      console.error(e);
    }
  };

  const handleResume = async () => {
    try {
      await resumeSession(session.id);
      setIsPaused(false);
      setStreamStatus('LIVE');
    } catch (e) {
      console.error(e);
    }
  };

  const handleAcknowledge = async (incidentId) => {
    try {
      const res = await acknowledgeIncident(incidentId);
      if (res?.incident) {
        setIncidents((prev) =>
          prev.map((i) => (i.id === incidentId ? res.incident : i))
        );
        if (res.event) {
          setEvents((prev) => [res.event, ...prev]);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleResolve = async (incidentId) => {
    try {
      const res = await resolveIncident(incidentId);
      if (res?.incident) {
        setIncidents((prev) =>
          prev.map((i) => (i.id === incidentId ? res.incident : i))
        );
        if (res.event) {
          setEvents((prev) => [res.event, ...prev]);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveCapacity = async (newCapacity) => {
    try {
      await updateConfig(session.id, newCapacity);
      setTelemetry((prev) => ({ ...prev, safe_capacity: newCapacity }));
    } catch (e) {
      console.error('Failed to update safe capacity:', e);
    }
  };

  const handleDownloadFireModel = async () => {
    try {
      await downloadFireModel();
      if (onRefreshSystemStatus) onRefreshSystemStatus();
    } catch (e) {
      console.error('Failed to install fire model:', e);
    }
  };

  return (
    <div className="min-h-screen bg-[#181A1E] flex flex-col">
      {/* Top Header */}
      <Header
        systemStatus={systemStatus}
        streamStatus={streamStatus}
        onUploadClick={onBackToUpload}
        onConfigClick={() => setIsConfigOpen(true)}
      />

      {/* Main Monitoring Dashboard */}
      <main className="flex-1 p-4 lg:p-6 max-w-[1920px] w-full mx-auto flex flex-col gap-4">
        {/* TOP SECTION: Video Monitor (70%) + Active Alerts (30%) */}
        <div className="grid grid-cols-1 lg:grid-cols-10 gap-4 items-stretch">
          {/* LEFT 70%: Video Monitoring Panel */}
          <div className="lg:col-span-7 flex flex-col">
            <VideoPlayer
              sessionId={session?.id}
              telemetry={telemetry}
              onPause={handlePause}
              onResume={handleResume}
              isPaused={isPaused}
            />
          </div>

          {/* RIGHT 30%: Active Alerts Panel */}
          <div className="lg:col-span-3 flex flex-col">
            <AlertsPanel
              incidents={incidents}
              onAcknowledge={handleAcknowledge}
              onResolve={handleResolve}
            />
          </div>
        </div>

        {/* MIDDLE SECTION: 4 KPI Statistics Cards */}
        <StatsGrid telemetry={telemetry} />

        {/* BOTTOM SECTION: Crowd Density Timeline Graph + Event Log */}
        <div className="grid grid-cols-1 lg:grid-cols-10 gap-4 items-stretch">
          {/* LEFT 65%: Timeline Graph */}
          <div className="lg:col-span-6 flex flex-col">
            <CrowdDensityChart data={chartData} />
          </div>

          {/* RIGHT 35%: Event Log */}
          <div className="lg:col-span-4 flex flex-col">
            <EventLogPanel events={events} />
          </div>
        </div>
      </main>

      {/* Settings Modal */}
      <ConfigModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        safeCapacity={telemetry.safe_capacity}
        onSaveCapacity={handleSaveCapacity}
        systemStatus={systemStatus}
        onDownloadFireModel={handleDownloadFireModel}
      />
    </div>
  );
}
