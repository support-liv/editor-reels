import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from editor_reels import transcrever
for v in sys.argv[1:]:
    base = os.path.splitext(os.path.basename(v))[0]
    transcrever(v, os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcricoes", base + ".json"))
    print("ok", base, flush=True)
