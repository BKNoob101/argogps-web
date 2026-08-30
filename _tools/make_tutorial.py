#!/usr/bin/env python3
"""Generate ArgoGPS tutorial video - step-by-step walkthrough with annotations"""
import subprocess, os

W, H = 720, 1496
FPS = 30
OUT = "/opt/data/argogps-web/argogps-tutorial.mp4"
SEG_DIR = "/opt/data/argogps-web/assets/screens/segments"
os.makedirs(SEG_DIR, exist_ok=True)

# 4 layar + durasi + teks langkah
SCREENS = [
    {
        "file": "/opt/data/argogps-web/assets/screens/home-polished.png",
        "dur": 5.5,
        "title": "1. Buka ArgoGPS",
        "steps": [
            {"text": "Odometer GPS siap pakai", "y": 0.18},
            {"text": "Kalkulator ongkir otomatis", "y": 0.32},
            {"text": "Geser untuk mulai tracking →", "y": 0.88, "highlight": "slide_right"},
        ],
    },
    {
        "file": "/opt/data/argogps-web/assets/screens/home-polished.png",  # same screen, different focus
        "dur": 5.0,
        "title": "2. Mulai Perjalanan",
        "steps": [
            {"text": "Geser tombol 'Geser untuk mulai'", "y": 0.15},
            {"text": "GPS aktif → jarak & ongkir hitung real-time", "y": 0.30},
            {"text": "Mode Hujan / Malam otomatis", "y": 0.45},
        ],
    },
    {
        "file": "/opt/data/argogps-web/assets/screens/tagihan-polished.png",
        "dur": 5.5,
        "title": "3. Lihat Tagihan Otomatis",
        "steps": [
            {"text": "Ringkasan Trip & Rincian Tagihan", "y": 0.15},
            {"text": "Detail belanja per outlet", "y": 0.35},
            {"text": "+ Tambah Outlet (+Rp2.000)", "y": 0.65, "highlight": "bottom_btn"},
            {"text": "Total Akhir otomatis", "y": 0.88},
        ],
    },
    {
        "file": "/opt/data/argogps-web/assets/screens/riwayat-polished.png",
        "dur": 5.0,
        "title": "4. Cek Riwayat & Pendapatan",
        "steps": [
            {"text": "Total Pendapatan & jumlah trip", "y": 0.15},
            {"text": "Daftar perjalanan lengkap", "y": 0.35},
            {"text": "Reset harian/mingguan/bulanan", "y": 0.60},
        ],
    },
    {
        "file": "/opt/data/argogps-web/assets/screens/setelan-polished.png",
        "dur": 5.0,
        "title": "5. Atur Sesuai Kebutuhan",
        "steps": [
            {"text": "Profil • Tema (20 pilihan) • Tarif", "y": 0.15},
            {"text": "Struk custom (logo/header/footer)", "y": "0.35"},
            {"text": "Riwayat • Aplikasi (versi, bantuan)", "y": "0.55"},
        ],
    },
]

# === Helper: buat segment dengan overlay teks & highlight ===
def make_segment(idx, screen):
    dur = screen["dur"]
    seg = f"{SEG_DIR}/tut_{idx}.mp4"
    
    # Build drawtext filters for each step (appear sequentially within segment)
    # We'll use enable='between(t,X,Y)' to show each line at different times
    drawtexts = []
    title = screen["title"]
    # Title at top
    drawtexts.append(
        f"drawtext=text='{title}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"fontsize=36:fontcolor=white:box=1:boxcolor=0x0F7A4E@0.9:boxborderw=16:"
        f"x=(w-text_w)/2:y=60"
    )
    
    # Steps appear staggered
    step_start = 0.8
    for i, step in enumerate(screen["steps"]):
        t0 = step_start + i * 1.0
        t1 = t0 + 3.5
        y_pos = int(step["y"] * H) if isinstance(step["y"], float) else int(float(step["y"]) * H)
        drawtexts.append(
            f"drawtext=text='{step['text']}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            f"fontsize=28:fontcolor=white:box=1:boxcolor=0x15241C@0.85:boxborderw=12:"
            f"x=(w-text_w)/2:y={y_pos}:enable='between(t,{t0:.1f},{t1:.1f})'"
        )
    
    # Highlight circle/arrow for specific UI elements
    # slide_right: arrow pointing right at slide button area (bottom center)
    # bottom_btn: highlight circle at bottom button area
    overlays = []
    for i, step in enumerate(screen["steps"]):
        if step.get("highlight") == "slide_right":
            t0 = step_start + i * 1.0
            t1 = t0 + 3.5
            # Arrow pointing right at slide button (approx x=85%, y=82%)
            cx, cy = int(W * 0.72), int(H * 0.78)
            overlays.append(
                f"drawbox=x={cx-40}:y={cy-25}:w=80:h=50:color=0x169B62@0.3:t=4:enable='between(t,{t0:.1f},{t1:.1f})',"
                f"drawtext=text='▶':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                f"fontsize=48:fontcolor=0x169B62:x={cx}:y={cy}:enable='between(t,{t0:.1f},{t1:.1f})'"
            )
        elif step.get("highlight") == "bottom_btn":
            t0 = step_start + i * 1.0
            t1 = t0 + 3.5
            cx, cy = int(W * 0.5), int(H * 0.62)
            overlays.append(
                f"drawbox=x={cx-80}:y={cy-20}:w=160:h=40:color=0xD97706@0.3:t=4:enable='between(t,{t0:.1f},{t1:.1f})',"
                f"drawtext=text='+':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"fontsize=36:fontcolor=0xD97706:x={cx}:y={cy}:enable='between(t,{t0:.1f},{t1:.1f})'"
            )
    
    all_filters = []
    # Base: scale up + zoompan (Ken Burns slow)
    all_filters.append(
        f"[0:v]scale=2160:4496,setsar=1,"
        f"zoompan=z='min(1.0+0.0004*on,1.08)':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={int(FPS*dur)}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p[vbase]"
    )
    # Apply drawtexts sequentially
    cur = "vbase"
    for j, dt in enumerate(drawtexts):
        nxt = f"vtxt{j}"
        all_filters.append(f"[{cur}]{dt}[{nxt}]")
        cur = nxt
    # Apply overlays
    for j, ov in enumerate(overlays):
        nxt = f"vov{j}"
        all_filters.append(f"[{cur}]{ov}[{nxt}]")
        cur = nxt
    # Final trim
    all_filters.append(f"[{cur}]trim=duration={dur},setpts=PTS-STARTPTS[vout{idx}]")
    
    filter_graph = "; ".join(all_filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", screen["file"],
        "-filter_complex", filter_graph,
        "-map", f"[vout{idx}]",
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        seg
    ]
    print(f"  Segment {idx+1}/{len(SCREENS)}: {screen['title']} ({dur}s)")
    subprocess.run(cmd, check=True, capture_output=True)
    return seg

# === MAIN ===
print("=== TAHAP 1: Buat segment tutorial ===")
segments = []
for i, s in enumerate(SCREENS):
    segments.append(make_segment(i, s))

# === TAHAP 2: Concat dengan crossfade ===
print("\n=== TAHAP 2: Gabung dengan crossfade ===")
inputs = " ".join([f"-i {s}" for s in segments])

XF = 0.8  # crossfade duration
xfade_filters = []
for i in range(len(segments)-1):
    # offset: after previous segment - XF
    off = sum(SCREENS[j]["dur"] for j in range(i+1)) - (i+1)*XF
    if i == 0:
        xfade_filters.append(f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
    else:
        xfade_filters.append(f"[x{i-1}][{i+1}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
xfade_filters.append(f"[x{len(segments)-2}]format=yuv420p[vout]")
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
result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
print(result.stderr[-3000:] if result.stderr else "")
print("Exit:", result.returncode)

if result.returncode == 0:
    size = os.path.getsize(OUT)
    print(f"\n✅ SUCCESS: {OUT} ({size/1024/1024:.1f} MB)")
else:
    print("❌ FAILED")

# cleanup segments
for s in segments:
    try: os.remove(s)
    except: pass