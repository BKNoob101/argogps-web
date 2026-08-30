#!/usr/bin/env python3
"""Generate ArgoGPS slideshow video with ffmpeg - single pass filter graph"""
import subprocess, os

W, H = 720, 1496
FPS = 30
DUR = 3.0      # per slide
XF = 0.7       # crossfade duration
IMAGES = [
    "/opt/data/argogps-web/assets/screens/home-polished.png",
    "/opt/data/argogps-web/assets/screens/tagihan-polished.png",
    "/opt/data/argogps-web/assets/screens/riwayat-polished.png",
    "/opt/data/argogps-web/assets/screens/setelan-polished.png",
]
OUT = "/opt/data/argogps-web/argogps-slideshow.mp4"

# Build filter graph:
# Each input: loop, scale up, zoompan (Ken Burns), trim to DUR
# Then xfade chain: [0][1] -> x1, [x1][2] -> x2, [x2][3] -> x3
# Total duration = 4*DUR - 3*XF = 9.9s

inputs = " ".join([f"-loop 1 -i {img}" for img in IMAGES])

# Per-input zoompan filter (indexed 0-3)
zoom_filters = []
for i in range(4):
    zoom_filters.append(
        f"[{i}:v]scale=2160:4496,setsar=1,"
        f"zoompan=z='min(1.0+0.0008*on,1.12)':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={int(FPS*DUR)}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p,trim=duration={DUR},setpts=PTS-STARTPTS[v{i}]"
    )

# xfade chain
xfade_filters = []
for i in range(3):
    off = (i+1)*DUR - (i+1)*XF
    if i == 0:
        xfade_filters.append(f"[v0][v1]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
    else:
        xfade_filters.append(f"[x{i-1}][v{i+1}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
# final output label
xfade_filters.append(f"[x2]format=yuv420p[vout]")

filter_graph = "; ".join(zoom_filters + xfade_filters)

cmd = [
    "ffmpeg", "-y",
    *inputs.split(),
    "-filter_complex", filter_graph,
    "-map", "[vout]",
    "-r", str(FPS),
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    OUT
]

print("Running ffmpeg...")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
print("STDOUT:", result.stdout[-2000:] if result.stdout else "")
print("STDERR:", result.stderr[-2000:] if result.stderr else "")
print("Exit code:", result.returncode)

if result.returncode == 0:
    size = os.path.getsize(OUT)
    print(f"SUCCESS: {OUT} ({size/1024:.1f} KB)")
else:
    print("FAILED")