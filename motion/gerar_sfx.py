#!/usr/bin/env python3
"""Gera a biblioteca de efeitos sonoros do motion (motion/sfx/*.wav), sintetizados do zero:
sem licença de terceiros. 48 kHz, estéreo, pico -3 dBFS. Rode de novo para recriar."""
import math, os, wave
import numpy as np

SR = 48000
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "sfx")
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(d * SR)) / SR


def bandpass_sweep(x, f0, f1, q=1.2):
    """biquad passa-banda com frequência central variando (exponencial) de f0 a f1."""
    n = len(x)
    fs = f0 * (f1 / f0) ** (np.arange(n) / max(1, n - 1))
    y = np.zeros(n)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(n):
        w = 2 * math.pi * fs[i] / SR
        a = math.sin(w) / (2 * q)
        b0, b2, a0, a1, a2 = a, -a, 1 + a, -2 * math.cos(w), 1 - a
        yi = (b0 * x[i] + b2 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1, y2, y1 = x1, x[i], y1, yi
        y[i] = yi
    return y


def lowpass(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def env(n, ataque, queda, forma=2.0):
    """envelope: sobe em `ataque` (fração) e cai até o fim."""
    k = np.arange(n) / n
    e = np.where(k < ataque, (k / ataque) ** 1.5, ((1 - k) / (1 - ataque)) ** forma)
    return e


def pan(m, de=-0.6, ate=0.6):
    p = np.linspace(de, ate, len(m))
    l, r = np.cos((p + 1) * math.pi / 4), np.sin((p + 1) * math.pi / 4)
    return np.stack([m * l, m * r], 1)


def estereo(m):
    return np.stack([m, m], 1)


def normalizar(s, pico_db=-3.0):
    return s / (np.max(np.abs(s)) + 1e-9) * 10 ** (pico_db / 20)


def salvar(nome, s):
    s = normalizar(s)
    with wave.open(os.path.join(SAIDA, nome + ".wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(s, -1, 1) * 32767).astype("<i2").tobytes())


def whoosh(d=0.5, f0=250, f1=3200, q=0.9, de=-0.7, ate=0.7):
    n = int(d * SR)
    ruido = rng.standard_normal(n)
    m = bandpass_sweep(ruido, f0, f1, q) * env(n, 0.55, n, 2.2)
    return pan(m, de, ate)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    # passagem rápida (entrada de cena)
    salvar("whoosh", whoosh())
    # passagem grave e mais longa (troca de cena grande)
    salvar("whoosh_grave", whoosh(0.8, 120, 1400, 0.7, 0.6, -0.6))
    # pop: bolha curta subindo (elemento aparecendo)
    x = t(0.09)
    f = 380 + 820 * (x / x[-1])
    pop = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-x * 38)
    salvar("pop", estereo(pop))
    # tick: clique seco (contador, lista)
    x = t(0.03)
    tick = (np.sin(2 * math.pi * 3100 * x) + 0.4 * rng.standard_normal(len(x))) * np.exp(-x * 220)
    salvar("tick", estereo(tick))
    # impacto: grave com queda de afinação + ruído abafado (texto batendo)
    x = t(0.9)
    f = 90 * np.exp(-x * 3.5) + 38
    corpo = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-x * 5.5)
    estalo = lowpass(rng.standard_normal(len(x)), 900) * np.exp(-x * 30) * 3
    salvar("impacto", estereo(corpo + estalo))
    # riscar: arranhão curto (algo sendo cortado/negado)
    n = int(0.22 * SR)
    risco = bandpass_sweep(rng.standard_normal(n), 1800, 5200, 2.5) * env(n, 0.15, n, 1.4)
    salvar("riscar", pan(risco, -0.3, 0.5))
    # subida: tensão crescendo (antes da virada)
    x = t(1.3)
    n = len(x)
    ruido = bandpass_sweep(rng.standard_normal(n), 400, 6000, 0.8)
    f = 180 + 700 * (x / x[-1]) ** 2
    tom = np.sin(2 * math.pi * np.cumsum(f) / SR) * 0.35
    salvar("subida", estereo((ruido + tom) * (x / x[-1]) ** 2.2 * np.exp(-np.maximum(0, x - 1.22) * 60)))
    # sino: resolução positiva (resposta, CTA)
    x = t(1.4)
    sino = sum(a * np.sin(2 * math.pi * f * x) * np.exp(-x * k)
               for f, a, k in [(1318.5, 1.0, 3.2), (2637, 0.45, 5.0), (3951, 0.25, 7.5), (659.3, 0.3, 2.5)])
    salvar("sino", estereo(sino * (1 - np.exp(-x * 400))))
    print("sfx gerados em", SAIDA, ":", ", ".join(sorted(os.listdir(SAIDA))))


if __name__ == "__main__":
    main()
