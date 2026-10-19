"""Construye la web completa para GitHub Pages a partir de web/.

web/index.html es un fragmento: el artefacto de Claude le añade el esqueleto del documento (doctype, charset y
viewport). Para GitHub Pages hay que añadírselo aquí; el resto de archivos se copian tal cual.
Lo ejecuta .github/workflows/pages.yml en cada push a main; tools/servir_local.py usa el mismo esqueleto.

Uso (desde la raíz del repositorio): python -I tools/construir_web.py [carpeta_de_salida]   (por defecto, _site)
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / 'web'
ESQUELETO = (
    '<!doctype html><html lang="es"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    '</head><body>{}</body></html>'
)


def documento():
    return ESQUELETO.format((WEB / 'index.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / '_site'
    if salida.exists():
        shutil.rmtree(salida)
    shutil.copytree(WEB, salida)
    (salida / 'index.html').write_text(documento(), encoding='utf-8')
    (salida / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Web construida en {salida}')
