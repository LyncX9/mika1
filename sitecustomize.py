# sitecustomize.py
# Ini akan dijalankan otomatis sebelum import lain (built-in feature Python)

import sys
import types

# Buat modul palsu audioop
fake_audioop = types.ModuleType("audioop")

def _b(*args, **kwargs): return b''
def _i(*args, **kwargs): return 0
def _t(*args, **kwargs): return (b'', 0)

# Isi fungsi dasar agar tidak error di discord
fake_audioop.add = fake_audioop.mul = fake_audioop.bias = _b
fake_audioop.getsample = fake_audioop.avg = fake_audioop.max = fake_audioop.rms = _i
fake_audioop.reverse = fake_audioop.tomono = fake_audioop.tostereo = fake_audioop.lin2lin = _b
fake_audioop.lin2ulaw = fake_audioop.ulaw2lin = _b
fake_audioop.lin2adpcm = fake_audioop.adpcm2lin = _t

# Registrasikan ke sys.modules
sys.modules["audioop"] = fake_audioop
