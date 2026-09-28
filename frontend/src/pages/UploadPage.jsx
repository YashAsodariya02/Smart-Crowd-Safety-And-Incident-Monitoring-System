import React, { useState, useRef } from 'react';
import { Upload, Video, ShieldAlert, CheckCircle2, ArrowRight, Play, FileVideo } from 'lucide-react';
import { uploadVideo, loadDemoVideo, startSession } from '../services/api';

export default function UploadPage({ onSessionReady, systemStatus }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [safeCapacity, setSafeCapacity] = useState(50);
  const [isUploading, setIsUploading] = useState(false);
  const [initStep, setInitStep] = useState(0); // 0: idle, 1: init, 2: yolo, 3: video, 4: ready
  const [errorMessage, setErrorMessage] = useState('');

  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = (file) => {
    if (!file.name.toLowerCase().match(/\.(mp4|avi|mov|mkv)$/)) {
      setErrorMessage('Please select a valid MP4/AVI/MOV video file.');
      return;
    }
    setErrorMessage('');
    setSelectedFile(file);
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const runInitializationSequence = async (uploadPromise) => {
    setIsUploading(true);
    setErrorMessage('');
    setInitStep(1); // INITIALIZING MONITORING SESSION

    try {
      const session = await uploadPromise;
      await new Promise((r) => setTimeout(r, 600));

      setInitStep(2); // LOADING YOLOv8...
      await new Promise((r) => setTimeout(r, 700));

      setInitStep(3); // PREPARING VIDEO...
      await startSession(session.id);
      await new Promise((r) => setTimeout(r, 600));

      setInitStep(4); // AI SYSTEM READY
      await new Promise((r) => setTimeout(r, 500));

      onSessionReady(session);
    } catch (err) {
      console.error('Session start failed:', err);
      setErrorMessage(err.message || 'Failed to initialize session');
      setIsUploading(false);
      setInitStep(0);
    }
  };

  const handleStartAnalysis = () => {
    if (!selectedFile) return;
    runInitializationSequence(uploadVideo(selectedFile, safeCapacity));
  };

  const handleUseDemo = () => {
    runInitializationSequence(loadDemoVideo(safeCapacity));
  };

  return (
    <div className="min-h-screen bg-[#181A1E] flex flex-col items-center justify-center p-4 select-none">
      {/* Container */}
      <div className="w-full max-w-2xl">
        {/* Branding Header */}
        <div className="brutal-panel bg-[#22252A] p-6 mb-6 border-2 border-black flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-[#FF005B] border-2 border-black flex items-center justify-center text-white shadow-[2px_2px_0px_#000]">
              <ShieldAlert className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="heading-font font-black text-2xl text-white tracking-tight">
                  CROWD//MONITOR
                </h1>
                <span className="bg-[#2D27FF] text-white text-[10px] font-mono px-2 py-0.5 border border-black font-bold">
                  SURVEILLANCE AI
                </span>
              </div>
              <p className="text-xs font-mono text-[#8892B0] tracking-wide mt-0.5">
                SMART CROWD SAFETY & INCIDENT MONITORING SYSTEM
              </p>
            </div>
          </div>

          <div className="hidden sm:flex flex-col items-end font-mono text-xs text-[#8892B0]">
            <span>SYSTEM STATUS</span>
            <div className="flex items-center gap-1.5 font-bold text-[#00FF5B] mt-1">
              <span className="dot-indicator dot-safe" />
              <span>ONLINE</span>
            </div>
          </div>
        </div>

        {/* Upload Card / Dropzone */}
        <div className="brutal-panel bg-[#1C1F24] p-6 border-2 border-black">
          <div className="mb-4">
            <h2 className="heading-font font-bold text-lg text-white mb-1">
              VIDEO FEED INGESTION
            </h2>
            <p className="font-mono text-xs text-[#8892B0]">
              Select or drop an MP4 surveillance video, Blender crowd simulation, or CCTV feed for real-time AI incident analysis.
            </p>
          </div>

          {/* Drag & Drop Area */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={`border-2 border-dashed p-8 text-center cursor-pointer transition-colors ${
              dragActive
                ? 'border-[#00FF5B] bg-[#00FF5B]/10'
                : selectedFile
                ? 'border-[#2D27FF] bg-[#2D27FF]/10'
                : 'border-[#2F343F] hover:border-[#8892B0] bg-[#121417]'
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".mp4,.avi,.mov,.mkv"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              className="hidden"
            />

            <Upload className="w-10 h-10 text-[#8892B0] mx-auto mb-3" />
            <p className="font-mono text-xs text-white font-bold mb-1">
              {selectedFile ? 'CLICK TO CHANGE VIDEO FILE' : 'DRAG & DROP VIDEO FEED (MP4)'}
            </p>
            <p className="font-mono text-[11px] text-[#4C566A]">
              or click to browse from local computer
            </p>
          </div>

          {/* Selected File Details */}
          {selectedFile && (
            <div className="mt-4 p-3 bg-[#121417] border border-[#2F343F] flex items-center justify-between font-mono text-xs">
              <div className="flex items-center gap-2">
                <FileVideo className="w-5 h-5 text-[#2D27FF]" />
                <div>
                  <div className="text-white font-bold truncate max-w-[280px]">
                    {selectedFile.name}
                  </div>
                  <div className="text-[#8892B0] text-[11px]">
                    SIZE: {formatFileSize(selectedFile.size)}
                  </div>
                </div>
              </div>
              <span className="text-[#00FF5B] text-[10px] font-bold border border-[#00FF5B]/30 px-2 py-0.5">
                READY FOR ANALYSIS
              </span>
            </div>
          )}

          {/* Safe Capacity Setting */}
          <div className="mt-4 pt-4 border-t border-[#2F343F] flex flex-wrap items-center justify-between gap-3 font-mono text-xs">
            <div>
              <span className="font-bold text-white block">SAFE CROWD CAPACITY</span>
              <span className="text-[11px] text-[#8892B0]">Baseline limit for occupancy threshold calculation</span>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="10"
                max="500"
                value={safeCapacity}
                onChange={(e) => setSafeCapacity(Number(e.target.value))}
                className="bg-[#121417] border-2 border-black text-white px-3 py-1.5 w-24 text-center font-bold focus:outline-none focus:border-[#2D27FF]"
              />
              <span className="text-[#8892B0] text-xs">PERSONS</span>
            </div>
          </div>

          {errorMessage && (
            <div className="mt-4 p-2.5 bg-[#FF005B]/15 border border-[#FF005B] text-[#FF005B] font-mono text-xs">
              ERROR: {errorMessage}
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleStartAnalysis}
              disabled={!selectedFile || isUploading}
              className={`brutal-btn flex-1 py-3 px-6 text-sm flex items-center justify-center gap-2 ${
                selectedFile && !isUploading
                  ? 'brutal-btn-primary'
                  : 'bg-[#2F343F] text-[#8892B0] border-[#4C566A] cursor-not-allowed'
              }`}
            >
              <span>START ANALYSIS</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={handleUseDemo}
              disabled={isUploading}
              className="brutal-btn brutal-btn-dark py-3 px-5 text-xs flex items-center justify-center gap-2 border border-[#2F343F]"
              title="Load developer testing crowd simulation MP4"
            >
              <Play className="w-3.5 h-3.5 text-[#00FF5B]" />
              <span>USE DEMO SIMULATION</span>
            </button>
          </div>
        </div>

        {/* Footer info */}
        <div className="mt-4 text-center font-mono text-[11px] text-[#4C566A]">
          POWERED BY ULTRALYTICS YOLOV8 &bull; REAL-TIME TEMPORAL STABILIZATION &bull; FASTAPI
        </div>
      </div>

      {/* Initialization Sequence Modal */}
      {isUploading && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="brutal-panel bg-[#181A1E] w-full max-w-md p-6 border-2 border-black shadow-[4px_4px_0px_#000]">
            <div className="flex items-center gap-3 mb-6 pb-3 border-b-2 border-black">
              <div className="w-8 h-8 bg-[#2D27FF] border-2 border-black flex items-center justify-center text-white font-bold">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <h3 className="heading-font font-black text-white text-base">
                  STARTING MONITORING SESSION
                </h3>
                <p className="font-mono text-[11px] text-[#8892B0]">INITIALIZING PIPELINE</p>
              </div>
            </div>

            {/* Sequence Steps */}
            <div className="space-y-3 font-mono text-xs">
              {/* Step 1 */}
              <div className="flex items-center justify-between p-2.5 bg-[#121417] border border-[#2F343F]">
                <span className="text-white font-bold">INITIALIZING MONITORING SESSION</span>
                {initStep > 1 ? (
                  <CheckCircle2 className="w-4 h-4 text-[#00FF5B]" />
                ) : (
                  <span className="text-[#2D27FF] font-bold animate-pulse">PROCESSING...</span>
                )}
              </div>

              {/* Step 2 */}
              <div className="flex items-center justify-between p-2.5 bg-[#121417] border border-[#2F343F]">
                <span className="text-white font-bold">LOADING YOLOv8...</span>
                {initStep > 2 ? (
                  <CheckCircle2 className="w-4 h-4 text-[#00FF5B]" />
                ) : initStep === 2 ? (
                  <span className="text-[#2D27FF] font-bold animate-pulse">WARMING UP...</span>
                ) : (
                  <span className="text-[#4C566A]">PENDING</span>
                )}
              </div>

              {/* Step 3 */}
              <div className="flex items-center justify-between p-2.5 bg-[#121417] border border-[#2F343F]">
                <span className="text-white font-bold">PREPARING VIDEO...</span>
                {initStep > 3 ? (
                  <CheckCircle2 className="w-4 h-4 text-[#00FF5B]" />
                ) : initStep === 3 ? (
                  <span className="text-[#2D27FF] font-bold animate-pulse">PROBING...</span>
                ) : (
                  <span className="text-[#4C566A]">PENDING</span>
                )}
              </div>

              {/* Step 4 */}
              <div className="flex items-center justify-between p-2.5 bg-[#121417] border border-[#2F343F]">
                <span className="text-white font-bold">AI SYSTEM READY</span>
                {initStep >= 4 ? (
                  <CheckCircle2 className="w-4 h-4 text-[#00FF5B]" />
                ) : (
                  <span className="text-[#4C566A]">PENDING</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
