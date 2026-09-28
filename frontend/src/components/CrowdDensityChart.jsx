import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
} from 'recharts';
import { TrendingUp } from 'lucide-react';

export default function CrowdDensityChart({ data = [] }) {
  // Chart data format: { time: "00:12", occupancy: 65, persons: 32 }
  return (
    <div className="brutal-panel p-4 bg-[#131518] border-2 border-black flex flex-col h-full">
      {/* Chart Title & Legend */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3 select-none">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-[#2D27FF]" />
          <span className="heading-font font-black text-sm tracking-wider text-white">
            CROWD DENSITY // TIMELINE
          </span>
        </div>

        {/* Threshold Indicators */}
        <div className="flex items-center gap-3 text-[10px] font-mono">
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 bg-[#00FF5B]" />
            <span className="text-[#8892B0]">SAFE (&lt;50%)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 bg-[#2D27FF]" />
            <span className="text-[#8892B0]">MOD (50-75%)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 bg-[#FFE53B]" />
            <span className="text-[#8892B0]">HIGH (75-90%)</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 bg-[#FF005B]" />
            <span className="text-[#8892B0]">CRITICAL (90%+)</span>
          </div>
        </div>
      </div>

      {/* Chart Container */}
      <div className="flex-1 min-h-[190px] w-full">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-[#4C566A] font-mono text-xs">
            Awaiting telemetry data...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="occupancyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2D27FF" stopOpacity={0.5} />
                  <stop offset="95%" stopColor="#2D27FF" stopOpacity={0.0} />
                </linearGradient>
              </defs>

              <XAxis
                dataKey="time"
                stroke="#4C566A"
                fontSize={10}
                tickLine={false}
                fontFamily="JetBrains Mono"
              />
              <YAxis
                domain={[0, 100]}
                stroke="#4C566A"
                fontSize={10}
                tickLine={false}
                fontFamily="JetBrains Mono"
                unit="%"
              />

              {/* Threshold Guidelines */}
              <ReferenceLine y={50} stroke="#00FF5B" strokeDasharray="3 3" opacity={0.4} />
              <ReferenceLine y={75} stroke="#FFE53B" strokeDasharray="3 3" opacity={0.4} />
              <ReferenceLine y={90} stroke="#FF005B" strokeDasharray="3 3" opacity={0.5} />

              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload;
                    return (
                      <div className="bg-[#1C1F24] border border-[#2F343F] p-2 text-xs font-mono shadow-[2px_2px_0px_#000]">
                        <div className="text-[#8892B0] text-[10px]">TIME: {d.time}</div>
                        <div className="text-white font-bold">
                          OCCUPANCY: <span className="text-[#00FF5B]">{d.occupancy}%</span>
                        </div>
                        <div className="text-white">
                          PERSONS: <span className="text-[#2D27FF] font-bold">{d.persons}</span>
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />

              <Area
                type="monotone"
                dataKey="occupancy"
                stroke="#2D27FF"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#occupancyGradient)"
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
