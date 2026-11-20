// From the Shepherdr production (alphabox.swift), unchanged. Compiled by `studio setup` into ~/.local/share/insane-marketing-studio/bin/.
import AppKit
// Prints ffmpeg "crop=w:h:x:y" for the bounding box of pixels with alpha above a threshold (default 0.5).
let a = CommandLine.arguments
let rep = NSBitmapImageRep(cgImage: NSImage(contentsOfFile: a[1])!.cgImage(forProposedRect: nil, context: nil, hints: nil)!)
let th = a.count > 2 ? Double(a[2])! : 0.5
let w = rep.pixelsWide, h = rep.pixelsHigh
var x0 = w, y0 = h, x1 = -1, y1 = -1
for y in stride(from: 0, to: h, by: 1) { for x in stride(from: 0, to: w, by: 1) where rep.colorAt(x: x, y: y)!.alphaComponent > th { x0 = min(x0, x); x1 = max(x1, x); y0 = min(y0, y); y1 = max(y1, y) } }
let pad = 4
x0 = max(0, x0 - pad); y0 = max(0, y0 - pad); x1 = min(w - 1, x1 + pad); y1 = min(h - 1, y1 + pad)
print("crop=\(x1 - x0 + 1):\(y1 - y0 + 1):\(x0):\(y0)")
