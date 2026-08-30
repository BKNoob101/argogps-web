#!/usr/bin/env python3
"""Generate ArgoGPS slideshow - 2 tahap: segment -> concat"""
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
SEG_DIR = "/opt/data/argogps-web/assets/screens/segments"
OUT = "/opt/data/argogps-web/argogps-slideshow.mp4"
os.makedirs(SEG_DIR, exist_ok=True)

# === TAHAP 1: bikin segment per gambar (fps konstan) ===
seg_files = []
for i, img in enumerate(IMAGES):
    seg = f"{SEG_DIR}/seg_{i}.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img,
        "-t", str(DUR), "-r", str(FPS),
        "-filter_complex",
        f"[0:v]scale=2160:4496,setsar=1,"
        f"zoompan=z='min(1.0+0.0008*on,1.12)':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={int(FPS*DUR)}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p,trim=duration={DUR},setpts=PTS-STARTPTS[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        seg
    ]
    print(f"Segment {i+1}/4...")
    subprocess.run(cmd, check=True, capture_output=True)
    seg_files.append(seg)

# === TAHAP 2: concat dengan xfade (input sudah constant fps) ===
inputs = " ".join([f"-i {s}" for s in seg_files])

# xfade chain offsets: after each DUR - XF
xfade_filters = []
for i in range(3):
    off = (i+1)*DUR - (i+1)*XF
    if i == 0:
        xfade_filters.append(f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
    else:
        xfade_filters.append(f"[x{i-1}][{i+1}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
xfade_filters.append(f"[x2]format=yuv420p[vout]")
filter_graph = "; ".join(xfade_filters)

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

print("Concat with crossfade...")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
print("STDERR:", result.stderr[-3000:] if result.stderr else "")
print("Exit code:", result.returncode)

if result.returncode == 0:
    size = os.path.getsize(OUT)
    print(f"SUCCESS: {OUT} ({size/1024:.1f} KB)")
else:
    print("FAILED")

# cleanup
for s in seg_files:
    try: os.remove(s)
    except: pass