import React, { useState, useEffect } from 'react';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import { getSystemStatus } from './services/api';

export default function App() {
  const [currentSession, setCurrentSession] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  const fetchStatus = async () => {
    try {
      const data = await getSystemStatus();
      setSystemStatus(data);
    } catch (e) {
      console.warn('Backend system status check failed:', e);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSessionReady = (session) => {
    setCurrentSession(session);
  };

  const handleBackToUpload = () => {
    setCurrentSession(null);
  };

  return (
    <div>
      {!currentSession ? (
        <UploadPage
          onSessionReady={handleSessionReady}
          systemStatus={systemStatus}
        />
      ) : (
        <DashboardPage
          session={currentSession}
          onBackToUpload={handleBackToUpload}
          systemStatus={systemStatus}
          onRefreshSystemStatus={fetchStatus}
        />
      )}
    </div>
  );
}
