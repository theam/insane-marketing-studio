// From the Shepherdr production (track.swift), unchanged. Compiled by `studio setup` into ~/.local/share/insane-marketing-studio/bin/.
import AppKit
import Vision
// Screen tracking helpers on stills, with Vision.
//   track rect <img> x y w h            rectangles found in the crop (VNDetectRectanglesRequest): one line per rectangle,
//                                        "conf tlx tly trx try brx bry blx bly" in full-image px (origin top-left)
//   track reg <ref> <img> x y w h        homography H (9 numbers, row-major) that maps a point of <img> to <ref>, both
//                                        cropped to the same rect (VNHomographicImageRegistrationRequest); in full-image px
let a = CommandLine.arguments
func load(_ p: String) -> CGImage { NSImage(contentsOfFile: p)!.cgImage(forProposedRect: nil, context: nil, hints: nil)! }
func crop(_ img: CGImage, _ i: Int) -> (CGImage, CGRect) {
  let r = CGRect(x: Int(a[i])!, y: Int(a[i + 1])!, width: Int(a[i + 2])!, height: Int(a[i + 3])!)
  return (img.cropping(to: r)!, r)
}
if a[1] == "rect" {
  let (c, r) = crop(load(a[2]), 3)
  let req = VNDetectRectanglesRequest()
  req.maximumObservations = 8
  req.minimumAspectRatio = 0.3
  req.minimumSize = 0.2
  req.quadratureTolerance = 30
  req.minimumConfidence = 0.3
  try! VNImageRequestHandler(cgImage: c).perform([req])
  // Normalised, origin bottom-left → full-image px, origin top-left.
  func px(_ p: CGPoint) -> String { String(format: "%.2f %.2f", r.minX + p.x * r.width, r.minY + (1 - p.y) * r.height) }
  for o in req.results ?? [] {
    print(String(format: "%.3f", o.confidence), px(o.topLeft), px(o.topRight), px(o.bottomRight), px(o.bottomLeft))
  }
} else if a[1] == "reg" {
  let (ref, r) = crop(load(a[2]), 4)
  let (img, _) = crop(load(a[3]), 4)
  let req = VNHomographicImageRegistrationRequest(targetedCGImage: img)
  try! VNImageRequestHandler(cgImage: ref).perform([req])
  guard let o = req.results?.first as? VNImageHomographicAlignmentObservation else { print("no alignment"); exit(1) }
  // Vision's warp is in the crop's pixel space with a bottom-left origin; convert to full-image px, top-left origin:
  // p_ref = F · W · F⁻¹ · p_img, with F flipping y about the crop and shifting by its origin.
  let m = o.warpTransform // column-major simd_float3x3
  let W = [[Double(m.columns.0.x), Double(m.columns.1.x), Double(m.columns.2.x)],
           [Double(m.columns.0.y), Double(m.columns.1.y), Double(m.columns.2.y)],
           [Double(m.columns.0.z), Double(m.columns.1.z), Double(m.columns.2.z)]]
  let h = Double(r.height), x0 = Double(r.minX), y0 = Double(r.minY)
  // T: full top-left px → crop bottom-left px: (x - x0, h - (y - y0)); Ti its inverse.
  let T = [[1.0, 0, -x0], [0, -1.0, h + y0], [0, 0, 1.0]]
  let Ti = [[1.0, 0, x0], [0, -1.0, h + y0], [0, 0, 1.0]]
  func mul(_ A: [[Double]], _ B: [[Double]]) -> [[Double]] { (0..<3).map { i in (0..<3).map { j in (0..<3).reduce(0) { $0 + A[i][$1] * B[$1][j] } } } }
  let H = mul(Ti, mul(W, T))
  print(H.flatMap { $0 }.map { String(format: "%.8f", $0 / H[2][2]) }.joined(separator: " "))
}
