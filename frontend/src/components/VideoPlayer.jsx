import React, { useState } from 'react';
import { Play, Pause, RotateCcw, Maximize2, Video, Eye } from 'lucide-react';

export default function VideoPlayer({
  sessionId,
  telemetry,
  onPause,
  onResume,
  isPaused
}) {
  const [streamError, setStreamError] = useState(false);
  const [retryKey, setRetryKey] = useState(Date.now());

  const streamUrl = sessionId ? `/api/sessions/${sessionId}/stream?t=${retryKey}` : '';

  const handleRetry = () => {
    setStreamError(false);
    setRetryKey(Date.now());
  };

  return (
    <div className="brutal-panel bg-[#131518] flex flex-col h-full overflow-hidden border-2 border-black">
      {/* Panel Top Banner */}
      <div className="bg-[#1C1F24] px-4 py-2 border-b-2 border-black flex items-center justify-between select-none">
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="dot-indicator dot-safe" />
          <span className="font-bold text-white tracking-wider">FEED: VIDEO-01 // AI INFERENCE STREAM</span>
          <span className="text-[#8892B0] text-[11px] hidden sm:inline">| RTSP/FILE PROJECTION</span>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="text-[#8892B0]">
            FRAME: <span className="text-white font-bold">{telemetry?.frame_index || 0}</span> / {telemetry?.total_frames || '—'}
          </span>
          <span className="bg-[#22252A] px-2 py-0.5 border border-[#2F343F] text-[#00FF5B] font-bold">
            {telemetry?.fps || 0} FPS
          </span>
        </div>
      </div>

      {/* Video Display Area */}
      <div className="relative flex-1 bg-black flex items-center justify-center min-h-[380px] lg:min-h-[440px] overflow-hidden">
        {sessionId && !streamError ? (
          <img
            key={retryKey}
            src={streamUrl}
            alt="AI Surveillance Feed"
            onError={() => setStreamError(true)}
            className="w-full h-full object-contain max-h-[560px]"
          />
        ) : (
          <div className="text-center p-8 font-mono">
            <Video className="w-12 h-12 text-[#4C566A] mx-auto mb-3" />
            <p className="text-[#8892B0] text-sm mb-3">
              {streamError ? 'Stream connection interrupted' : 'No active video feed selected'}
            </p>
            {streamError && (
              <button
                onClick={handleRetry}
                className="brutal-btn brutal-btn-info px-4 py-1.5 text-xs inline-flex items-center gap-2"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>RECONNECT FEED</span>
              </button>
            )}
          </div>
        )}

        {/* Video Overlay Telemetry HUD Bar (bottom corner) */}
        <div className="absolute bottom-2 left-2 bg-[#121417]/90 backdrop-blur-sm border border-[#2F343F] px-3 py-1.5 font-mono text-[11px] flex items-center gap-3 text-white shadow-[2px_2px_0px_#000]">
          <span className="text-[#8892B0]">MODEL:</span>
          <span className="font-bold text-[#00FF5B]">YOLOv8n</span>
          <span className="text-[#4C566A]">|</span>
          <span>{telemetry?.fps || 0} FPS</span>
          <span className="text-[#4C566A]">|</span>
          <span>FRAME {telemetry?.frame_index || 0}</span>
          <span className="text-[#4C566A]">|</span>
          <div className="flex items-center gap-1 text-[#00FF5B] font-bold">
            <span className="dot-indicator dot-safe" />
            <span>AI ACTIVE</span>
          </div>
        </div>

        {/* Crowd Level Badge (top right) */}
        {telemetry?.crowd_level && (
          <div className="absolute top-2 right-2">
            <span
              className={`font-mono text-xs font-black px-3 py-1 border-2 border-black shadow-[2px_2px_0px_#000] tracking-wider ${
                telemetry.crowd_level === 'CRITICAL'
                  ? 'bg-[#FF005B] text-white'
                  : telemetry.crowd_level === 'HIGH'
                  ? 'bg-[#FFE53B] text-black'
                  : telemetry.crowd_level === 'MODERATE'
                  ? 'bg-[#2D27FF] text-white'
                  : 'bg-[#00FF5B] text-black'
              }`}
            >
              CROWD: {telemetry.crowd_level}
            </span>
          </div>
        )}
      </div>

      {/* Video Control Bar */}
      <div className="bg-[#1C1F24] px-4 py-2 border-t-2 border-black flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isPaused ? (
            <button
              onClick={onResume}
              className="brutal-btn brutal-btn-safe px-3 py-1 text-xs flex items-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5" />
              <span>RESUME</span>
            </button>
          ) : (
            <button
              onClick={onPause}
              className="brutal-btn brutal-btn-dark px-3 py-1 text-xs flex items-center gap-1.5"
            >
              <Pause className="w-3.5 h-3.5 text-[#FFE53B]" />
              <span>PAUSE</span>
            </button>
          )}

          <button
            onClick={handleRetry}
            className="brutal-btn brutal-btn-dark px-2.5 py-1 text-xs flex items-center gap-1"
            title="Refresh stream connection"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#8892B0]" />
          </button>
        </div>

        <div className="font-mono text-xs text-[#8892B0] flex items-center gap-3">
          <span>TIME: <strong className="text-white">{telemetry?.timestamp || '00:00'}</strong></span>
          <span className="text-[#4C566A]">|</span>
          <span>CAPACITY: <strong className="text-[#00FF5B]">{telemetry?.safe_capacity || 50}</strong></span>
        </div>
      </div>
    </div>
  );
}
