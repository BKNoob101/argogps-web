#!/usr/bin/env bash
set -e
cd /opt/data/argogps-web/assets/screens

OUT="/opt/data/argogps-web/argogps-slideshow.mp4"
W=720
H=1496
FPS=30
DUR=3              # durasi tiap slide (dtk)
XF=0.7             # durasi crossfade
FADE=0.5

# siapkan input 4 gambar
IMGS="home-polished.png tagihan-polished.png riwayat-polished.png setelan-polished.png"

# --- Tahap 1: buat tiap gambar jadi klip .ts (dengan zoompan halus) ---
i=0
segment_files=""
for img in $IMGS; do
  # zoom in pelan dari 1.0 -> 1.12 (Ken Burns), setiap klip DUR detik
  # zoompan butuh scale tinggi dulu biar gerakan mulus
  ffmpeg -y -loop 1 -i "$img" -t $DUR -r $FPS \
    -filter_complex "[0:v]scale=2160:4496,setsar=1,zoompan=z='min(1.0+0.0008*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${FPS}*${DUR}:s=${W}x${H}:fps=${FPS},format=yuv420p,trim=duration=${DUR},setpts=PTS-STARTPTS[v]" \
    -map "[v]" -c:v libx264 -preset medium -crf 20 seg_$i.mp4
  segment_files="$segment_files seg_$i.mp4"
  i=$((i+1))
done

# --- Tahap 2: gabung 4 klip dengan crossfade berantai ---
# xfade chain: c0 -> c1 -> c2 -> c3
# offset = (i+1)*DUR - i*XF
python3 - "$segment_files" > /tmp/filt.txt <<'EOF'
import sys
files = sys.argv[1].split()
n = len(files)
DUR=3.0; XF=0.7; FPS=30
parts=[]
for j in range(n):
    parts.append(f"[{j}:v]")
# build filtergraph
chain=[]
for j in range(n-1):
    off = (j+1)*DUR - (j+1)*XF
    if j==0:
        chain.append(f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x1]")
    else:
        chain.append(f"[x{j}][{j+1}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{j+1}]")
# last = x{n-1}; total duration = n*DUR - (n-1)*XF
total = n*DUR - (n-1)*XF
# audio: generate silent audio with same length
print("; ".join(chain))
print(f"total={total:.3f}")
EOF
cat /tmp/filt.txt
lines=($(cat /tmp/filt.txt))
filts="${lines[0]}"
total="${lines[1]#total=}"

ffmpeg -y \
  -i seg_0.mp4 -i seg_1.mp4 -i seg_2.mp4 -i seg_3.mp4 \
  -filter_complex "$filts; [x3]format=yuv420p,scale=${W}:${H}[vout]" \
  -map "[vout]" -r $FPS -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -movflags +faststart "$OUT"

echo "DONE: $OUT"
ls -la "$OUT"
rm -f seg_*.mp4 /tmp/filt.txt
