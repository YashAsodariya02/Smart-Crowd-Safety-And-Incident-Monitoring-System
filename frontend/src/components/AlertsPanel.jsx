import React, { useState } from 'react';
import { AlertTriangle, Flame, Users, ShieldAlert, CheckCircle2, Eye } from 'lucide-react';

export default function AlertsPanel({
  incidents = [],
  onAcknowledge,
  onResolve
}) {
  const [filter, setFilter] = useState('ALL');

  const filteredIncidents = incidents.filter((inc) => {
    if (filter === 'ACTIVE') return inc.status === 'ACTIVE';
    if (filter === 'ACKNOWLEDGED') return inc.status === 'ACKNOWLEDGED';
    if (filter === 'RESOLVED') return inc.status === 'RESOLVED';
    return true;
  });

  const activeCount = incidents.filter((i) => i.status === 'ACTIVE').length;

  const getIncidentIcon = (type) => {
    if (type?.includes('FIRE')) return <Flame className="w-4 h-4 text-[#FF005B]" />;
    if (type?.includes('SMOKE')) return <AlertTriangle className="w-4 h-4 text-[#FFE53B]" />;
    if (type?.includes('CROWD')) return <Users className="w-4 h-4 text-[#FFE53B]" />;
    return <ShieldAlert className="w-4 h-4 text-[#2D27FF]" />;
  };

  return (
    <div className="brutal-panel bg-[#131518] flex flex-col h-full overflow-hidden border-2 border-black">
      {/* Header */}
      <div className="bg-[#1C1F24] px-4 py-2 border-b-2 border-black flex items-center justify-between select-none">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-[#FF005B]" />
          <span className="heading-font font-black text-sm tracking-wider text-white">ACTIVE ALERTS</span>
          {activeCount > 0 && (
            <span className="bg-[#FF005B] text-white font-mono text-[10px] px-1.5 py-0.2 font-black border border-black animate-pulse">
              {activeCount} ACTIVE
            </span>
          )}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="bg-[#181A1E] px-3 py-1.5 border-b border-[#2F343F] flex gap-1 text-[11px] font-mono">
        {['ALL', 'ACTIVE', 'ACKNOWLEDGED', 'RESOLVED'].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-2 py-0.5 border ${
              filter === tab
                ? 'bg-[#22252A] border-black text-white font-bold'
                : 'border-transparent text-[#8892B0] hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Alert List */}
      <div className="flex-1 p-3 overflow-y-auto space-y-2.5 max-h-[500px]">
        {filteredIncidents.length === 0 ? (
          <div className="text-center py-12 text-[#4C566A] font-mono text-xs">
            <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-[#2F343F]" />
            NO {filter !== 'ALL' ? filter : ''} ALERTS RECORDED
          </div>
        ) : (
          filteredIncidents.map((incident) => {
            const isCritical = incident.severity === 'CRITICAL';
            const isActive = incident.status === 'ACTIVE';
            const isAck = incident.status === 'ACKNOWLEDGED';
            const isResolved = incident.status === 'RESOLVED';

            return (
              <div
                key={incident.id}
                className={`brutal-card p-3 border-l-4 ${
                  isCritical ? 'border-l-[#FF005B]' : 'border-l-[#FFE53B]'
                } ${isActive ? 'bg-[#1C1F24]' : 'bg-[#16181C] opacity-80'}`}
              >
                {/* Alert Card Header */}
                <div className="flex items-center justify-between gap-2 mb-1.5 font-mono text-xs">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`font-black px-1.5 py-0.5 text-[10px] border border-black ${
                        isCritical ? 'bg-[#FF005B] text-white' : 'bg-[#FFE53B] text-black'
                      }`}
                    >
                      {incident.severity}
                    </span>
                    <span className="text-white font-bold text-[11px]">
                      {incident.type?.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <span className="text-[#8892B0] font-mono text-[11px] font-bold">
                    {incident.timestamp}
                  </span>
                </div>

                {/* Details / Confidence */}
                <div className="text-xs text-[#ECEFF4] font-mono mb-2">
                  {incident.details || incident.type}
                </div>

                {incident.confidence && (
                  <div className="text-[11px] font-mono text-[#8892B0] mb-2">
                    CONFIDENCE: <strong className="text-white">{incident.confidence}%</strong>
                  </div>
                )}

                {/* Card Footer: Status & Actions */}
                <div className="flex items-center justify-between pt-1 border-t border-[#2F343F]/60 text-[11px] font-mono">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`dot-indicator ${
                        isActive ? (isCritical ? 'dot-critical' : 'dot-warning') : isAck ? 'dot-warning' : 'dot-safe'
                      }`}
                    />
                    <span className="text-[#8892B0] font-bold">{incident.status}</span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {isActive && (
                      <button
                        onClick={() => onAcknowledge(incident.id)}
                        className="brutal-btn brutal-btn-dark px-2 py-0.5 text-[10px] text-[#FFE53B] border border-[#FFE53B]/50 hover:border-[#FFE53B]"
                      >
                        ACKNOWLEDGE
                      </button>
                    )}
                    {(isActive || isAck) && (
                      <button
                        onClick={() => onResolve(incident.id)}
                        className="brutal-btn brutal-btn-safe px-2 py-0.5 text-[10px]"
                      >
                        RESOLVE
                      </button>
                    )}
                    {isResolved && (
                      <span className="text-[#00FF5B] text-[10px] font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> RESOLVED
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
