#!/bin/sh
# Key a sprite generated on flat green (#00FF00) or magenta (#FF00FF): remove the spill, shave one pixel of fringe off
# the matte and trim the image to its content. From the Shepherdr production (key.sh).
#   studio chroma in.png assets/cutouts/out.png [green|magenta]
# Ask the image model for "isolated on a flat pure green (#00FF00) background, no shadow on the background" (magenta
# for green subjects). For photos, `studio cutout` (macOS Vision) is usually cleaner.
set -e
[ -n "$2" ] || { sed -n '2,6p' "$0"; exit 1; }
tmp=$(mktemp -d)
if [ "$3" = magenta ]; then k="colorkey=0xFF00FF:0.36:0.08"; else k="colorkey=0x00FF00:0.30:0.10,despill=type=green:mix=0.6:expand=0.1"; fi
ffmpeg -hide_banner -loglevel error -y -i "$1" -filter_complex "[0]format=rgba,$k,split[c][m];[m]alphaextract,erosion[a];[c][a]alphamerge" "$tmp/k.png"
# Bounding box of the opaque pixels (alpha > 0.5), so thin objects aren't trimmed away.
box=$(alphabox "$tmp/k.png" 0.5)
mkdir -p "$(dirname "$2")"
ffmpeg -hide_banner -loglevel error -y -i "$tmp/k.png" -vf "$box" "$2"
rm -rf "$tmp"
echo "$2 $box"
