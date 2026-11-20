// From the Shepherdr production (subject.swift), unchanged. Compiled by `studio setup` into ~/.local/share/insane-marketing-studio/bin/.
import AppKit
import Vision
import CoreImage
// Lifts the foreground subjects out of a photo crop with Vision (VNGenerateForegroundInstanceMaskRequest) and writes a
// PNG with alpha. usage: subject in.jpg x y w h out.png [instance indices, e.g. 1,2; default all]
let a = CommandLine.arguments
let src = NSImage(contentsOfFile: a[1])!.cgImage(forProposedRect: nil, context: nil, hints: nil)!
let rect = CGRect(x: Int(a[2])!, y: Int(a[3])!, width: Int(a[4])!, height: Int(a[5])!)
let crop = src.cropping(to: rect)!
let req = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(cgImage: crop)
try! handler.perform([req])
guard let obs = req.results?.first else { print("no subject found"); exit(1) }
print("instances: \(obs.allInstances.map { $0 })")
let pick = a.count > 7 ? IndexSet(a[7].split(separator: ",").map { Int($0)! }) : obs.allInstances
let buf = try! obs.generateMaskedImage(ofInstances: pick, from: handler, croppedToInstancesExtent: false)
let ci = CIImage(cvPixelBuffer: buf)
let ctx = CIContext()
let cg = ctx.createCGImage(ci, from: ci.extent)!
let rep = NSBitmapImageRep(cgImage: cg)
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[6]))
print("wrote \(a[6]) \(cg.width)x\(cg.height)")
