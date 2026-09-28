import React, { useState } from 'react';
import { X, Settings, Download, Cpu, CheckCircle } from 'lucide-react';

export default function ConfigModal({
  isOpen,
  onClose,
  safeCapacity,
  onSaveCapacity,
  systemStatus,
  onDownloadFireModel
}) {
  const [capacityInput, setCapacityInput] = useState(safeCapacity || 50);
  const [isDownloading, setIsDownloading] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveCapacity(Number(capacityInput));
    onClose();
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      await onDownloadFireModel();
    } finally {
      setIsDownloading(false);
    }
  };

  const fireModelStatus = systemStatus?.models?.fire_smoke_model?.status;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="brutal-panel bg-[#181A1E] w-full max-w-md border-2 border-black p-6 relative">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b-2 border-black mb-4">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-[#2D27FF]" />
            <h3 className="heading-font font-black text-lg text-white">SYSTEM CONFIGURATION</h3>
          </div>
          <button
            onClick={onClose}
            className="text-[#8892B0] hover:text-white p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Capacity Input */}
        <div className="space-y-4 font-mono text-xs">
          <div>
            <label className="block text-[#8892B0] mb-1 font-bold">
              SAFE CROWD CAPACITY (PERSONS)
            </label>
            <p className="text-[11px] text-[#4C566A] mb-2">
              Crowd occupancy % is dynamically computed as (Person Count / Safe Capacity) * 100.
            </p>
            <div className="flex gap-2">
              <input
                type="number"
                min="5"
                max="500"
                value={capacityInput}
                onChange={(e) => setCapacityInput(e.target.value)}
                className="bg-[#121417] border-2 border-black text-white px-3 py-2 text-sm font-mono w-32 focus:outline-none focus:border-[#2D27FF]"
              />
              <button
                onClick={handleSave}
                className="brutal-btn brutal-btn-info px-4 py-2 text-xs font-bold"
              >
                APPLY CAPACITY
              </button>
            </div>
          </div>

          {/* AI Model Status */}
          <div className="pt-3 border-t border-[#2F343F]">
            <span className="block text-[#8892B0] mb-2 font-bold">AI INFERENCE ENGINES</span>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-[#121417] border border-[#2F343F]">
                <div>
                  <div className="font-bold text-white">PERSON / CROWD MODEL</div>
                  <div className="text-[10px] text-[#8892B0]">YOLOv8n (COCO Pretrained)</div>
                </div>
                <span className="text-[#00FF5B] font-bold text-[11px]">ACTIVE</span>
              </div>

              <div className="flex items-center justify-between p-2 bg-[#121417] border border-[#2F343F]">
                <div>
                  <div className="font-bold text-white">FIRE / SMOKE MODEL</div>
                  <div className="text-[10px] text-[#8892B0]">YOLOv8n (D-Fire Dataset, AGPL-3.0)</div>
                </div>
                <div>
                  {fireModelStatus === 'ACTIVE' ? (
                    <span className="text-[#00FF5B] font-bold text-[11px] flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" /> ACTIVE
                    </span>
                  ) : (
                    <button
                      onClick={handleDownload}
                      disabled={isDownloading}
                      className="brutal-btn brutal-btn-primary px-2.5 py-1 text-[10px] flex items-center gap-1"
                    >
                      <Download className="w-3 h-3" />
                      <span>{isDownloading ? 'INSTALLING...' : 'INSTALL WEIGHTS'}</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Hardware status */}
          <div className="pt-3 border-t border-[#2F343F] flex items-center justify-between text-[11px] text-[#8892B0]">
            <span>COMPUTE DEVICE: <strong className="text-white">{systemStatus?.device || 'CPU'}</strong></span>
            <span>MEMORY USAGE: <strong className="text-white">{systemStatus?.memory_percent || 0}%</strong></span>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-5 pt-3 border-t-2 border-black flex justify-end">
          <button
            onClick={onClose}
            className="brutal-btn brutal-btn-dark px-4 py-1.5 text-xs font-bold"
          >
            CLOSE
          </button>
        </div>
      </div>
    </div>
  );
}
