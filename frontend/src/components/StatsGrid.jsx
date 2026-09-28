import React from 'react';
import { Users, Activity, Flame, Cpu } from 'lucide-react';

export default function StatsGrid({ telemetry }) {
  const personCount = telemetry?.person_count ?? 0;
  const peakPeople = telemetry?.peak_people ?? 0;
  const occupancy = telemetry?.occupancy ?? 0;
  const crowdLevel = telemetry?.crowd_level ?? 'SAFE';
  const hazardsCount = telemetry?.hazards_count ?? 0;
  const avgConfidence = telemetry?.avg_confidence ?? 0;

  // Occupancy color based on crowd status
  const getOccupancyColor = (level) => {
    if (level === 'CRITICAL') return 'bg-[#FF005B] text-white';
    if (level === 'HIGH') return 'bg-[#FFE53B] text-black';
    if (level === 'MODERATE') return 'bg-[#2D27FF] text-white';
    return 'bg-[#00FF5B] text-black';
  };

  const getBarColor = (level) => {
    if (level === 'CRITICAL') return '#FF005B';
    if (level === 'HIGH') return '#FFE53B';
    if (level === 'MODERATE') return '#2D27FF';
    return '#00FF5B';
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 my-4">
      {/* CARD 1: PEOPLE */}
      <div className="brutal-panel p-4 bg-[#181A1E] flex flex-col justify-between border-2 border-black">
        <div className="flex items-center justify-between text-xs font-mono text-[#8892B0] mb-1">
          <span className="font-bold tracking-wider">PEOPLE</span>
          <Users className="w-4 h-4 text-[#8892B0]" />
        </div>
        <div className="my-1">
          <span className="heading-font font-black text-4xl lg:text-5xl text-white tracking-tight">
            {String(personCount).padStart(3, '0')}
          </span>
        </div>
        <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-[#2F343F]">
          <span className="text-[#8892B0]">CURRENT COUNT</span>
          <span className="text-white font-bold">PEAK: {peakPeople}</span>
        </div>
      </div>

      {/* CARD 2: CROWD OCCUPANCY */}
      <div className="brutal-panel p-4 bg-[#181A1E] flex flex-col justify-between border-2 border-black">
        <div className="flex items-center justify-between text-xs font-mono text-[#8892B0] mb-1">
          <span className="font-bold tracking-wider">CROWD OCCUPANCY</span>
          <span className={`px-2 py-0.5 font-bold font-mono text-[10px] border border-black ${getOccupancyColor(crowdLevel)}`}>
            {crowdLevel}
          </span>
        </div>
        <div className="my-1 flex items-baseline gap-2">
          <span className="heading-font font-black text-4xl lg:text-5xl text-white tracking-tight">
            {Math.round(occupancy)}%
          </span>
        </div>
        {/* Simple Occupancy Progress Bar */}
        <div className="pt-2 border-t border-[#2F343F]">
          <div className="w-full bg-[#121417] h-2 border border-black overflow-hidden flex">
            <div
              className="h-full transition-all duration-300"
              style={{
                width: `${Math.min(100, occupancy)}%`,
                backgroundColor: getBarColor(crowdLevel)
              }}
            />
          </div>
        </div>
      </div>

      {/* CARD 3: HAZARDS */}
      <div className="brutal-panel p-4 bg-[#181A1E] flex flex-col justify-between border-2 border-black">
        <div className="flex items-center justify-between text-xs font-mono text-[#8892B0] mb-1">
          <span className="font-bold tracking-wider">HAZARDS</span>
          <Flame className={`w-4 h-4 ${hazardsCount > 0 ? 'text-[#FF005B] animate-pulse' : 'text-[#8892B0]'}`} />
        </div>
        <div className="my-1">
          <span
            className={`heading-font font-black text-4xl lg:text-5xl tracking-tight ${
              hazardsCount > 0 ? 'text-[#FF005B]' : 'text-white'
            }`}
          >
            {String(hazardsCount).padStart(2, '0')}
          </span>
        </div>
        <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-[#2F343F]">
          <span className="text-[#8892B0]">STATUS</span>
          <span className={`font-bold ${hazardsCount > 0 ? 'text-[#FF005B]' : 'text-[#00FF5B]'}`}>
            {hazardsCount > 0 ? 'ACTIVE DETECTIONS' : 'CLEAR'}
          </span>
        </div>
      </div>

      {/* CARD 4: MODEL */}
      <div className="brutal-panel p-4 bg-[#181A1E] flex flex-col justify-between border-2 border-black">
        <div className="flex items-center justify-between text-xs font-mono text-[#8892B0] mb-1">
          <span className="font-bold tracking-wider">MODEL</span>
          <Cpu className="w-4 h-4 text-[#8892B0]" />
        </div>
        <div className="my-1">
          <span className="heading-font font-black text-4xl lg:text-5xl text-white tracking-tight">
            {avgConfidence > 0 ? `${avgConfidence}%` : '—'}
          </span>
        </div>
        <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-[#2F343F]">
          <span className="text-[#8892B0]">AVG CONFIDENCE</span>
          <span className="text-[#00FF5B] font-bold">YOLOv8n</span>
        </div>
      </div>
    </div>
  );
}
