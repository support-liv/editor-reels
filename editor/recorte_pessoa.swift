// Recorte da pessoa (máscara) com o Vision do macOS, no próprio Mac: pra pôr texto ATRÁS da pessoa.
// Uso: swift recorte_pessoa.swift PASTA_QUADROS PASTA_MASCARAS   (lê *.png, grava máscaras PNG com o mesmo nome)
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
let entrada = URL(fileURLWithPath: args[1]), saida = URL(fileURLWithPath: args[2])
try? FileManager.default.createDirectory(at: saida, withIntermediateDirectories: true)
let ctx = CIContext()
let req = VNGeneratePersonSegmentationRequest()
req.qualityLevel = .accurate
req.outputPixelFormat = kCVPixelFormatType_OneComponent8

let nomes = (try! FileManager.default.contentsOfDirectory(atPath: entrada.path)).filter { $0.hasSuffix(".png") }.sorted()
for nome in nomes {
    autoreleasepool {
        let ci = CIImage(contentsOf: entrada.appendingPathComponent(nome))!
        try! VNImageRequestHandler(ciImage: ci).perform([req])
        guard let buf = req.results?.first?.pixelBuffer else { return }
        let m = CIImage(cvPixelBuffer: buf)
        let esc = m.transformed(by: CGAffineTransform(scaleX: ci.extent.width / m.extent.width,
                                                      y: ci.extent.height / m.extent.height))
        let cg = ctx.createCGImage(esc, from: ci.extent)!
        let png = NSBitmapImageRep(cgImage: cg).representation(using: .png, properties: [:])!
        try! png.write(to: saida.appendingPathComponent(nome))
    }
}
print("\(nomes.count) máscaras")
