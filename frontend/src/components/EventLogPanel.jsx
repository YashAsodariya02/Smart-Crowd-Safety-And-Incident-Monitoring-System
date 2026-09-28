import React from 'react';
import { Terminal } from 'lucide-react';

export default function EventLogPanel({ events = [] }) {
  const getSeverityStyle = (severity) => {
    if (severity === 'CRITICAL') return 'text-[#FF005B]';
    if (severity === 'WARNING') return 'text-[#FFE53B]';
    return 'text-[#ECEFF4]';
  };

  return (
    <div className="brutal-panel p-4 bg-[#131518] border-2 border-black flex flex-col h-full">
      {/* Panel Header */}
      <div className="flex items-center gap-2 mb-3 select-none">
        <Terminal className="w-4 h-4 text-[#8892B0]" />
        <span className="heading-font font-black text-sm tracking-wider text-white">EVENT LOG</span>
        <span className="text-[10px] font-mono bg-[#1C1F24] text-[#8892B0] px-1.5 py-0.5 border border-[#2F343F]">
          TIMELINE
        </span>
      </div>

      {/* Log Feed */}
      <div className="flex-1 overflow-y-auto space-y-1.5 font-mono text-xs pr-1 max-h-[190px]">
        {events.length === 0 ? (
          <div className="text-[#4C566A] text-center py-8">Awaiting operational events...</div>
        ) : (
          events.map((evt, idx) => (
            <div
              key={idx}
              className="flex items-start gap-2.5 py-1 border-b border-[#2F343F]/40 hover:bg-[#1C1F24]/50 transition-colors"
            >
              <span className="text-[#8892B0] font-bold text-[11px] whitespace-nowrap">
                {evt.timestamp || '00:00'}
              </span>
              <span className="text-[#4C566A]">|</span>
              <span className={`flex-1 font-bold ${getSeverityStyle(evt.severity)}`}>
                {evt.message}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
