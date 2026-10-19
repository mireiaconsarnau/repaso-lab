"""Baraja las opciones de las preguntas tipo test de web/datos/preguntas.json.

La posición de la opción correcta (A, B, C o D) y el orden de las demás salen de un hash del id de la pregunta,
así que el orden es fijo: volver a ejecutar el script no cambia nada, y una pregunta nueva no mueve las demás.
La sal está elegida para que la correcta quede repartida por igual entre las cuatro letras.

Uso (desde la raíz del repositorio): python -I tools/barajar_opciones.py [ruta/preguntas.json]
Ejecútalo cada vez que añadas preguntas tipo test: al escribirlas, la correcta suele quedar la primera.
"""
import hashlib
import json
import sys
from pathlib import Path

RUTA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'web' / 'datos' / 'preguntas.json'
SAL = 'repaso-lab-1219'


def numero(*partes):
    return int(hashlib.sha256('|'.join((SAL,) + partes).encode('utf-8')).hexdigest(), 16)


def barajar(q):
    correcta = next(o for o in q['opciones'] if o['correcta'])
    otras = sorted((o for o in q['opciones'] if not o['correcta']), key=lambda o: numero(q['id'], o['texto']))
    posicion = numero(q['id']) % len(q['opciones'])
    q['opciones'] = otras[:posicion] + [correcta] + otras[posicion:]


# Mismo formato que el resto del banco: listas cortas en una línea, opciones y filas de tabla en una línea cada una.
def en_linea(v):
    return json.dumps(v, ensure_ascii=False)


def formatear(v, sangria=0, clave=None):
    pad = '  ' * sangria
    if isinstance(v, list):
        if all(not isinstance(x, (list, dict)) for x in v) and len(en_linea(v)) <= 100:
            return en_linea(v)
        # Listas de números o de puntos [x, y] (datos de los gráficos): varias por línea.
        if v and all(isinstance(x, (int, float)) or (isinstance(x, list) and all(isinstance(y, (int, float)) for y in x)) for x in v):
            dentro = '  ' * (sangria + 1)
            lineas, actual = [], ''
            for x in v:
                trozo = en_linea(x)
                if actual and len(actual) + len(trozo) + 2 > 96:
                    lineas.append(actual + ',')
                    actual = ''
                actual = actual + (', ' if actual else '') + trozo
            lineas.append(actual)
            return '[\n' + '\n'.join(dentro + l for l in lineas) + '\n' + pad + ']'
        dentro = '  ' * (sangria + 1)
        el = [dentro + en_linea(x) for x in v] if clave in ('opciones', 'filas') else [dentro + formatear(x, sangria + 1) for x in v]
        return '[\n' + ',\n'.join(el) + '\n' + pad + ']'
    if isinstance(v, dict):
        dentro = '  ' * (sangria + 1)
        return '{\n' + ',\n'.join(f'{dentro}{en_linea(k)}: {formatear(x, sangria + 1, k)}' for k, x in v.items()) + '\n' + pad + '}'
    return en_linea(v)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    banco = json.loads(RUTA.read_text(encoding='utf-8'))
    tests = [q for q in banco if q.get('tipo') == 'test']
    for q in tests:
        barajar(q)
    RUTA.write_text(formatear(banco) + '\n', encoding='utf-8')
    cuenta = [sum(1 for q in tests if q['opciones'][i]['correcta']) for i in range(4)]
    print(f'{len(tests)} preguntas tipo test. Correcta en A, B, C y D: ' + ', '.join(map(str, cuenta)))
