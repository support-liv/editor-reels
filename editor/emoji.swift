// Gera um PNG com um emoji na fonte do macOS. Uso: emoji "🇺🇸" saida.png
import AppKit
let args = CommandLine.arguments
let texto = args[1] as NSString
let attrs: [NSAttributedString.Key: Any] = [.font: NSFont(name: "Apple Color Emoji", size: 160)!]
let tam = texto.size(withAttributes: attrs)
let img = NSImage(size: tam)
img.lockFocus()
texto.draw(at: .zero, withAttributes: attrs)
img.unlockFocus()
let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[2]))
