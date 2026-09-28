import os
import cv2
import numpy as np
import random
import math

def generate_demo_video(output_path: str, duration_sec: int = 15, fps: int = 24):
    """
    Developer Testing Utility:
    Generates a synthetic surveillance video with walking silhouettes,
    crowd density escalation (20 -> 45 -> 70), and a simulated flame event.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    width, height = 720, 480
    total_frames = duration_sec * fps

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Initialize simulated persons
    max_persons = 75
    persons = []
    for _ in range(max_persons):
        persons.append({
            "x": random.uniform(50, width - 50),
            "y": random.uniform(100, height - 60),
            "vx": random.uniform(-1.2, 1.2),
            "vy": random.uniform(-0.8, 0.8),
            "scale": random.uniform(0.8, 1.2),
            "hue": random.randint(15, 35)  # skin/cloth tone
        })

    print(f"Generating test video: {output_path} ({total_frames} frames)...")

    for f in range(total_frames):
        # Progress crowd count over time:
        # 0-30% of video: 20 persons (SAFE)
        # 30-60% of video: 38 persons (MODERATE)
        # 60-80% of video: 52 persons (HIGH)
        # 80-100% of video: 70 persons (CRITICAL)
        progress = f / total_frames
        if progress < 0.30:
            active_count = 20
        elif progress < 0.60:
            active_count = int(20 + (progress - 0.30) / 0.30 * 18)
        elif progress < 0.80:
            active_count = int(38 + (progress - 0.60) / 0.20 * 14)
        else:
            active_count = int(52 + (progress - 0.80) / 0.20 * 18)

        # Draw indoor concourse background (dark surveillance aesthetic)
        frame = np.full((height, width, 3), (35, 38, 44), dtype=np.uint8)

        # Floor grid perspective lines
        for i in range(0, width, 60):
            cv2.line(frame, (i, 120), (int(i * 1.3) - 100, height), (48, 52, 60), 1)
        for j in range(120, height, 40):
            cv2.line(frame, (0, j), (width, j), (48, 52, 60), 1)

        # Overhead hallway light gradients
        cv2.rectangle(frame, (0, 0), (width, 100), (25, 28, 32), -1)
        cv2.putText(frame, "CAM-01 // SECTOR-B CONCOURSE", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 130, 140), 2)
        cv2.putText(frame, "CCTV LIVE RECORDING", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 100), 1)

        # Draw active persons (pedestrian silhouettes with head, torso, legs)
        for i in range(active_count):
            p = persons[i]
            # Update position
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 30 or p["x"] > width - 30:
                p["vx"] *= -1
            if p["y"] < 130 or p["y"] > height - 40:
                p["vy"] *= -1

            x, y = int(p["x"]), int(p["y"])
            s = p["scale"]

            # Head
            head_r = int(7 * s)
            cv2.circle(frame, (x, y - int(24 * s)), head_r, (180, 190, 200), -1)
            # Torso
            cv2.rectangle(frame, (x - int(8 * s), y - int(16 * s)), (x + int(8 * s), y), (90, 100, 115), -1)
            # Legs
            cv2.line(frame, (x - int(4 * s), y), (x - int(5 * s), y + int(16 * s)), (50, 55, 65), int(3 * s))
            cv2.line(frame, (x + int(4 * s), y), (x + int(5 * s), y + int(16 * s)), (50, 55, 65), int(3 * s))

        # In the final 30% of video, simulate flame hazard in top right concourse corner
        if progress > 0.70:
            flame_x, flame_y = width - 120, 170
            # Flickering flame layers
            flicker = random.randint(-4, 4)
            cv2.circle(frame, (flame_x + flicker, flame_y), 28, (0, 140, 255), -1) # Orange outer
            cv2.circle(frame, (flame_x, flame_y - 8 + flicker), 18, (0, 220, 255), -1) # Yellow core
            # Smoke puff rising
            smoke_y = flame_y - int((f % 30) * 2)
            cv2.circle(frame, (flame_x + random.randint(-10, 10), smoke_y - 20), 22, (90, 95, 100), -1)

        out.write(frame)

    out.release()
    print(f"Generated test video successfully at {output_path}")

if __name__ == "__main__":
    import sys
    out_file = sys.argv[1] if len(sys.argv) > 1 else "../backend/uploads/demo_crowd_simulation.mp4"
    generate_demo_video(out_file)
