# Teste piloto — Darwin 25.5.0 (arm64)

01/10/2026 22:52 · Python 3.14.4 · 12/12 ok

| Teste | Resultado | Tempo | Detalhe |
|---|---|---|---|
| ambiente | ✅ | 0s | Python 3.14.4 / ffmpeg version 8.1 Copyright (c) 2000-20 / node v26.7.0 / UTF-8 sim / ffmpeg SEM zscale (HDR sem tone mapping) |
| arquivos grandes (Git LFS) | ✅ | 0s | estoque, trilhas e transições baixados |
| codificador de vídeo | ✅ | 0s | h264_videotoolbox |
| HDR do iPhone → cor padrão | ✅ | 1s | tone mapping ok |
| detector de rostos | ✅ | 0s | rosto em 3/3 quadros, centro [0.58, 0.32] |
| recorte da pessoa (texto atrás) | ✅ | 0s | pessoa ocupa ['47%', '48%', '46%'] do quadro |
| emoji e bandeiras | ✅ | 0s | emoji e bandeiras ok |
| login guardado (Chaveiro / Gerenciador de Credenciais) | ✅ | 0s | guardou, leu e apagou |
| short completo (Whisper + enquadramento + legenda + gancho + CTA animado) | ✅ | 16s | 17.6 MB (motion/HyperFrames incluído no CTA) |
| anúncio dinâmico (texto atrás, film burn, legenda LIV) | ✅ | 2s | quadro de prévia gerado (veja /Users/lucastoledo/Library/Caches/editor-reels/ads/previas/piloto_ads_A_texto_atras/00.80s.png) |
| trilha por baixo da fala | ✅ | 0s | fala -20.2 LUFS, ganho da trilha -24.9 dB |
| Chrome + Playwright (base do envio pelo YouTube Studio) | ✅ | 5s | abriu o Studio (pede login: normal) — https://accounts.google.com/v3/signin/identifier?continue=ht |

Arquivos de teste: `/Users/lucastoledo/Library/Caches/editor-reels/piloto`
