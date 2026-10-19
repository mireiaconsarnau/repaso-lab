"""Genera web/css/fuentes.css con las tipografías de web/fuentes/ incrustadas en base64.

El artefacto de Claude solo carga tipografías de Google Fonts o incrustadas como data: URI,
así que las fuentes locales (licencia OFL) se incrustan en este CSS.

Uso (desde la raíz del repositorio): python -I tools/generar_fuentes_css.py
"""
import base64
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / 'web' / 'fuentes'
SALIDA = RAIZ / 'web' / 'css' / 'fuentes.css'

# archivo → (familia, estilo, peso)
CARAS = [
    ('plexsans-300-normal.woff2', 'IBM Plex Sans', 'normal', '300'),
    ('plexsans-400-normal.woff2', 'IBM Plex Sans', 'normal', '400'),
    ('plexsans-400-italic.woff2', 'IBM Plex Sans', 'italic', '400'),
    ('plexsans-600-normal.woff2', 'IBM Plex Sans', 'normal', '600'),
    ('plexmono-400.woff2', 'IBM Plex Mono', 'normal', '400'),
    ('plexmono-500.woff2', 'IBM Plex Mono', 'normal', '500'),
]

partes = ['/* Generado por tools/generar_fuentes_css.py: no lo edites a mano. Licencias en web/fuentes/LICENCIAS.md. */\n']
for archivo, familia, estilo, peso in CARAS:
    datos = base64.b64encode((FUENTES / archivo).read_bytes()).decode('ascii')
    partes.append(
        f"@font-face {{ font-family: '{familia}'; font-style: {estilo}; font-weight: {peso}; font-display: swap; "
        f"src: url(data:font/woff2;base64,{datos}) format('woff2'); }}\n"
    )

SALIDA.write_text(''.join(partes), encoding='utf-8')
print(f'{SALIDA.relative_to(RAIZ)}: {SALIDA.stat().st_size / 1024:.0f} KB')
