// Detector de rostos com o Vision do macOS (lida bem com perfil e óculos).
// Uso: rostos img1.jpg img2.jpg ...
// Saída: uma linha JSON por imagem: [[cx, cy, w, h, pitch, yaw], ...]
// cx, cy, w, h normalizados 0-1 (origem no topo); pitch/yaw em radianos (pitch > 0 = cabeça pra baixo).
import Foundation
import Vision
import AppKit

for path in CommandLine.arguments.dropFirst() {
    var caixas: [[Double]] = []
    if let img = NSImage(contentsOfFile: path),
       let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) {
        let req = VNDetectFaceRectanglesRequest()
        req.revision = VNDetectFaceRectanglesRequestRevision3
        let handler = VNImageRequestHandler(cgImage: cg, options: [:])
        try? handler.perform([req])
        for obs in req.results ?? [] {
            let b = obs.boundingBox
            let pitch = obs.pitch?.doubleValue ?? 0
            let yaw = obs.yaw?.doubleValue ?? 0
            caixas.append([Double(b.midX), Double(1 - b.midY), Double(b.width), Double(b.height), pitch, yaw])
        }
    }
    let data = try! JSONSerialization.data(withJSONObject: caixas)
    print(String(data: data, encoding: .utf8)!)
}
