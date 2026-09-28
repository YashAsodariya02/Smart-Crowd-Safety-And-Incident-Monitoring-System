const BASE_URL = '';

export async function uploadVideo(file, safeCapacity = 50) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('safe_capacity', safeCapacity);

  const res = await fetch(`${BASE_URL}/api/videos/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function loadDemoVideo(safeCapacity = 50) {
  const formData = new FormData();
  formData.append('safe_capacity', safeCapacity);

  const res = await fetch(`${BASE_URL}/api/videos/use-demo`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to load demo video' }));
    throw new Error(err.detail || 'Failed to load demo video');
  }
  return res.json();
}

export async function startSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/start`, { method: 'POST' });
  return res.json();
}

export async function pauseSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/pause`, { method: 'POST' });
  return res.json();
}

export async function resumeSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/resume`, { method: 'POST' });
  return res.json();
}

export async function stopSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/stop`, { method: 'POST' });
  return res.json();
}

export async function getSession(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}`);
  return res.json();
}

export async function getIncidents(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/incidents`);
  return res.json();
}

export async function acknowledgeIncident(incidentId) {
  const res = await fetch(`${BASE_URL}/api/incidents/${incidentId}/acknowledge`, { method: 'PATCH' });
  return res.json();
}

export async function resolveIncident(incidentId) {
  const res = await fetch(`${BASE_URL}/api/incidents/${incidentId}/resolve`, { method: 'PATCH' });
  return res.json();
}

export async function getMetrics(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/metrics`);
  return res.json();
}

export async function getEvents(sessionId) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/events`);
  return res.json();
}

export async function updateConfig(sessionId, safeCapacity) {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/config`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ safe_capacity: safeCapacity }),
  });
  return res.json();
}

export async function getSystemStatus() {
  const res = await fetch(`${BASE_URL}/api/system/status`);
  return res.json();
}

export async function downloadFireModel() {
  const res = await fetch(`${BASE_URL}/api/system/download-fire-model`, { method: 'POST' });
  return res.json();
}
