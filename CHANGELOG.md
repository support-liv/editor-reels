# Changelog

Cada mudança com o motivo, para o time entender por que o editor faz o que faz.

## 0.6 (28/09/2026) - cortes pelo áudio e auditorias
- **Cortes pelo áudio:** o Whisper estica o fim da última palavra para o silêncio, e isso aparecia como respiro ou olhada pro lado no fim da frase. Agora o editor mede a voz (energia em dB a cada 20 ms) e corta onde a fala começa e termina, com folga de 0,05s antes e 0,10s depois. Pausas internas acima de 0,25s saem.
- **Pergunta do entrevistador:** limite de voz 8 dB mais sensível, porque sai mais baixa no microfone.
- **Zoom por bloco:** com o corte pelo áudio surgem muitos pedaços curtos. O punch-in passou a alternar por bloco original, senão o zoom pisca.
- **Tom de voz por bloco:** na conversa, medir em pedaços curtos errava quem falava.
- **Detecção de leitura do celular:** o detector de rostos agora devolve a inclinação da cabeça (pitch/yaw). `auditar.py` mostra, por frase do bruto, a % do tempo olhando pra baixo. Takes lidos não entram.
- **`auditar_pronto.py`:** confere pausas e olhar no vídeo final.
- **Legenda 35% menor** (58 → 38 px), aprovada pelo time.
- **Caixa do gancho em selfie:** escolhe a posição que menos cobre olhos e boca.

## 0.5 (28/09/2026) - anúncios
- Modo anúncio: sem caixa de CTA (o Meta põe o botão), legenda a 55% (selfie a 64%).

## 0.4 (28/09/2026) - cor e posição da caixa
- **HDR → SDR:** o iPhone grava em HDR (HLG/Dolby Vision). Sem conversão, a imagem ficava lavada. Conversão com tone mapping pelo VideoToolbox e arquivo marcado como BT.709.
- **Caixa não tapa rosto:** o editor gera o quadro final, procura os rostos e desce a caixa para o lugar da legenda quando precisa (a legenda some enquanto a caixa aparece).
- **Bandeira depois da palavra:** a bandeira sozinha não era entendida de primeira.

## 0.3 (27/09/2026) - conversa e ordem livre
- `--pessoa voz`: fecha em quem fala pelo tom de voz (Julia ~235 Hz, André ~160 Hz; limite 200 Hz) e segue cada pessoa por identidade, frame a frame.
- Trechos em qualquer ordem, `a-b?` para pergunta e `@N` para forçar quem aparece.
- Série "pergunta + resposta": a pergunta abre em quadro aberto.
- Equalização de voz (dynaudnorm) antes do loudnorm.

## 0.2 (27/09/2026) - visual e cortes
- Detector de rostos trocado de OpenCV (Haar) para o Vision do macOS: o Haar falhava com perfil e óculos.
- Gancho em caixa alta e bandeiras (renderizadas pelo macOS, porque o Pillow sem libraqm não junta as letras da bandeira).
- Legenda 25% menor (78 → 58 px). Caixas a 290 px do topo, abaixo da barra do Instagram.
- Removido o CTA falado "segue o perfil".

## 0.1 (27/09/2026) - primeira versão
- Transcrição com Whisper (timestamps por palavra), corte de perguntas e pausas, enquadramento 9:16 seguindo o rosto, legenda palavra a palavra, gancho e CTA, áudio a -14 LUFS.
- Legenda desenhada em Python porque o ffmpeg do Homebrew vem sem libass/drawtext.
