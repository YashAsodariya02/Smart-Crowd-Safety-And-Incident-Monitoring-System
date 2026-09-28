import React, { useState, useEffect } from 'react';
import { Upload, Settings, ShieldAlert, Cpu, Activity, Clock } from 'lucide-react';

export default function Header({
  systemStatus,
  streamStatus = 'LIVE',
  onUploadClick,
  onConfigClick
}) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const h = String(now.getHours()).padStart(2, '0');
      const m = String(now.getMinutes()).padStart(2, '0');
      const s = String(now.getSeconds()).padStart(2, '0');
      setTimeStr(`${h}:${m}:${s}`);
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  const personActive = systemStatus?.models?.person_model?.status === 'ACTIVE';
  const fireSmokeActive = systemStatus?.models?.fire_smoke_model?.status === 'ACTIVE';

  return (
    <header className="brutal-panel border-b-2 border-black px-6 py-3 bg-[#181A1E] flex flex-wrap items-center justify-between gap-4 select-none">
      {/* Brand Left */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-[#FF005B] border-2 border-black flex items-center justify-center font-bold text-white shadow-[2px_2px_0px_#000]">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="heading-font font-black text-xl tracking-tight text-white">CROWD//MONITOR</span>
            <span className="text-[10px] bg-[#2D27FF] text-white px-1.5 py-0.5 font-mono border border-black font-bold">
              SURVEILLANCE v1.0
            </span>
          </div>
          <div className="text-[11px] text-[#8892B0] font-mono tracking-wider">
            SMART CROWD SAFETY & INCIDENT SYSTEM
          </div>
        </div>
      </div>

      {/* Middle Status Indicators */}
      <div className="flex items-center gap-4 text-xs font-mono">
        {/* Person Model Status */}
        <div className="flex items-center gap-2 bg-[#121417] px-3 py-1.5 border border-[#2F343F] shadow-[1px_1px_0px_#000]">
          <span className="text-[#8892B0]">PERSON MODEL</span>
          <div className="flex items-center gap-1.5 font-bold">
            <span className={`dot-indicator ${personActive ? 'dot-safe' : 'dot-inactive'}`} />
            <span className={personActive ? 'text-[#00FF5B]' : 'text-[#8892B0]'}>
              {personActive ? 'ACTIVE' : 'OFFLINE'}
            </span>
          </div>
        </div>

        {/* Fire/Smoke Model Status */}
        <div className="flex items-center gap-2 bg-[#121417] px-3 py-1.5 border border-[#2F343F] shadow-[1px_1px_0px_#000]">
          <span className="text-[#8892B0]">FIRE/SMOKE</span>
          <div className="flex items-center gap-1.5 font-bold">
            <span className={`dot-indicator ${fireSmokeActive ? 'dot-safe' : 'dot-inactive'}`} />
            <span className={fireSmokeActive ? 'text-[#00FF5B]' : 'text-[#FFE53B]'}>
              {fireSmokeActive ? 'ACTIVE' : 'NOT INSTALLED'}
            </span>
          </div>
        </div>

        {/* Video / Stream Status */}
        <div className="flex items-center gap-2 bg-[#121417] px-3 py-1.5 border border-[#2F343F] shadow-[1px_1px_0px_#000]">
          <span className="text-[#8892B0]">FEED</span>
          <div className="flex items-center gap-1.5 font-bold">
            <span className={`dot-indicator ${streamStatus === 'LIVE' ? 'dot-safe' : 'dot-warning'}`} />
            <span className={streamStatus === 'LIVE' ? 'text-[#00FF5B]' : 'text-[#FFE53B]'}>
              {streamStatus}
            </span>
          </div>
        </div>

        {/* Live Clock */}
        <div className="hidden md:flex items-center gap-2 bg-[#121417] px-3 py-1.5 border border-[#2F343F] text-[#ECEFF4] font-mono shadow-[1px_1px_0px_#000]">
          <Clock className="w-3.5 h-3.5 text-[#8892B0]" />
          <span className="font-bold tracking-widest">{timeStr}</span>
        </div>
      </div>

      {/* Action Buttons Right */}
      <div className="flex items-center gap-3">
        {onConfigClick && (
          <button
            onClick={onConfigClick}
            className="brutal-btn brutal-btn-dark px-3 py-2 text-xs flex items-center gap-1.5 border border-[#2F343F]"
            title="Configure Safe Capacity & Thresholds"
          >
            <Settings className="w-3.5 h-3.5 text-[#8892B0]" />
            <span className="hidden sm:inline">CONFIG</span>
          </button>
        )}

        <button
          onClick={onUploadClick}
          className="brutal-btn brutal-btn-primary px-4 py-2 text-xs flex items-center gap-2 font-bold tracking-wider"
        >
          <Upload className="w-4 h-4" />
          <span>UPLOAD VIDEO FEED</span>
        </button>
      </div>
    </header>
  );
}
