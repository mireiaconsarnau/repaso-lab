"""Comprueba web/datos/config.json y web/datos/preguntas.json.

Uso (desde la raíz del repositorio):
    python -I tools/validar_banco.py            # valida web/
    python -I tools/validar_banco.py ruta/web   # otra carpeta

Revisa la estructura de cada pregunta, su unidad y lección, los niveles, los temas, los enlaces,
las tablas, los gráficos («figuras», que dibuja web/js/graficos.js), el HTML y que no aparezcan
nombres de los datasets reales de las actividades (lista en tools/prohibidos.txt, que no se publica).
"""
import importlib.util
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

WEB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'web'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')  # acentos legibles en la consola de Windows

# Nombres que no pueden salir en el banco (regla fija: las preguntas usan siempre ejemplos inventados): datasets y
# columnas reales de las actividades y casos de pruebas anteriores. La lista no es pública: está en tools/prohibidos.txt,
# que no se sube al repositorio (.gitignore) y se copia a mano en cada ordenador. Un nombre por línea; # para comentarios.
# Amplíala cada semestre. Sin el archivo, se avisa y no se busca nada.
RUTA_PROHIBIDOS = Path(__file__).resolve().parent / 'prohibidos.txt'
PROHIBIDOS = [l.strip() for l in RUTA_PROHIBIDOS.read_text(encoding='utf-8').splitlines()
              if l.strip() and not l.lstrip().startswith('#')] if RUTA_PROHIBIDOS.exists() else []

ETIQUETAS_HTML = {'strong', 'em', 'code', 'br', 'sub', 'sup'}
VACIAS = {'br'}

errores = []
avisos = []
# Test: posición de la correcta y si es la opción más larga, para detectar patrones que delaten la respuesta.
posiciones_correcta = []
correcta_mas_larga = []
sin_barajar = []
# Misma regla que tools/barajar_opciones.py, para saber dónde debe estar la correcta de cada pregunta.
_spec = importlib.util.spec_from_file_location('barajar_opciones', Path(__file__).resolve().parent / 'barajar_opciones.py')
barajado = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(barajado)
CITA_OPCION = re.compile(r'\b[Oo]pci[oó]n(es)? [A-D]\b|\b(respuesta|letra) [A-D]\b|\b(todas|ninguna) de las anteriores\b|\b(primera|segunda|tercera|última) opción\b')


def error(msg):
    errores.append(msg)


class ComprobadorHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pila = []
        self.problemas = []

    def handle_starttag(self, tag, attrs):
        if tag not in ETIQUETAS_HTML:
            self.problemas.append(f'etiqueta <{tag}> no permitida')
        if tag not in VACIAS:
            self.pila.append(tag)

    def handle_endtag(self, tag):
        if tag in VACIAS:
            return
        if not self.pila or self.pila[-1] != tag:
            self.problemas.append(f'</{tag}> sin abrir o mal anidada')
        else:
            self.pila.pop()


def revisar_html(donde, texto):
    if not isinstance(texto, str):
        error(f'{donde}: debe ser texto')
        return
    c = ComprobadorHTML()
    c.feed(texto)
    c.close()
    if c.pila:
        c.problemas.append('sin cerrar: ' + ', '.join(c.pila))
    for p in c.problemas:
        error(f'{donde}: {p}')


def textos(valor):
    """Todos los textos de un valor JSON (para buscar nombres prohibidos)."""
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, list):
        for v in valor:
            yield from textos(v)
    elif isinstance(valor, dict):
        for v in valor.values():
            yield from textos(v)


def cargar(nombre):
    ruta = WEB / 'datos' / nombre
    try:
        return json.loads(ruta.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f'ERROR: {ruta} no es JSON válido: {e}')
        sys.exit(1)


cfg = cargar('config.json')
banco = cargar('preguntas.json')

temas = cfg.get('temas', {})
lecciones = cfg.get('lecciones', {})
niveles = {n['id']: n['nombre'] for n in cfg.get('niveles', [])}
unidades = {u['codigo']: u for u in cfg.get('unidades', [])}

# ---- configuración ----
for u in cfg.get('unidades', []):
    for campo in ('id', 'codigo', 'nombre'):
        if not u.get(campo):
            error(f'unidad {u}: falta «{campo}»')
for codigo, lec in lecciones.items():
    for campo in ('titulo', 'url'):
        if not lec.get(campo):
            error(f'lección {codigo}: falta «{campo}»')
    if codigo.split('L')[0] not in unidades:
        error(f'lección {codigo}: su unidad no está en config.json → unidades')


def leccion_principal(q):
    """Primer enlace con código de lección: decide la unidad y la lección que se muestran."""
    return next((e for e in q.get('enlaces', []) if isinstance(e, str) and re.fullmatch(r'U\d+L\d+', e)), None)


# Gráficos: los tipos y campos que sabe dibujar web/js/graficos.js. Como máximo 3 series con color.
MAX_SERIES = 3


def es_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def es_punto(p):
    return isinstance(p, list) and len(p) == 2 and all(es_num(x) for x in p)


def revisar_figura(donde, fig):
    if not isinstance(fig, dict):
        error(f'{donde}: debe ser un objeto')
        return
    tipo = fig.get('tipo')
    series = fig.get('series') or fig.get('grupos') or []
    if tipo in ('lineas', 'roc'):
        if not series:
            error(f'{donde}: «{tipo}» necesita «series»')
        for k, se in enumerate(series):
            pts = se.get('puntos') or []
            if not se.get('nombre') or len(pts) < 2 or not all(es_punto(x) for x in pts):
                error(f'{donde} serie {k + 1}: necesita «nombre» y al menos 2 «puntos» [x, y]')
        if 'referencia' in fig and not (len(fig['referencia']) == 2 and all(es_punto(x) for x in fig['referencia'])):
            error(f'{donde}: «referencia» debe ser [[x, y], [x, y]]')
    elif tipo == 'barras':
        cats = fig.get('categorias') or []
        if not cats or not series:
            error(f'{donde}: «barras» necesita «categorias» y «series»')
        for k, se in enumerate(series):
            vals = se.get('valores') or []
            if not se.get('nombre') or len(vals) != len(cats) or not all(es_num(x) for x in vals):
                error(f'{donde} serie {k + 1}: necesita «nombre» y un valor numérico por categoría ({len(cats)})')
    elif tipo == 'histograma':
        lim = fig.get('limites') or []
        if len(lim) < 2 or not all(es_num(x) for x in lim) or any(b <= a for a, b in zip(lim, lim[1:])):
            error(f'{donde}: «limites» debe ser una lista creciente de números')
        if not series:
            error(f'{donde}: «histograma» necesita «series»')
        for k, se in enumerate(series):
            cs = se.get('conteos') or []
            if not se.get('nombre') or len(cs) != len(lim) - 1 or not all(es_num(x) for x in cs):
                error(f'{donde} serie {k + 1}: necesita «nombre» y {len(lim) - 1} «conteos» (uno por intervalo)')
    elif tipo == 'boxplot':
        cajas = fig.get('cajas') or []
        if not cajas:
            error(f'{donde}: «boxplot» necesita «cajas»')
        for k, c in enumerate(cajas):
            orden = [c.get(x) for x in ('min', 'q1', 'mediana', 'q3', 'max')]
            if not c.get('nombre') or not all(es_num(x) for x in orden) or orden != sorted(orden):
                error(f'{donde} caja {k + 1}: necesita «nombre» y min ≤ q1 ≤ mediana ≤ q3 ≤ max')
            if not all(es_num(x) for x in c.get('atipicos', [])):
                error(f'{donde} caja {k + 1}: «atipicos» debe ser una lista de números')
    elif tipo == 'dispersion':
        if not series:
            error(f'{donde}: «dispersion» necesita «grupos»')
        for k, g in enumerate(series):
            pts = g.get('puntos') or []
            if not g.get('nombre') or not pts or not all(es_punto(x) for x in pts):
                error(f'{donde} grupo {k + 1}: necesita «nombre» y «puntos» [x, y]')
        if 'linea' in fig and not (len(fig['linea']) == 2 and all(es_punto(x) for x in fig['linea'])):
            error(f'{donde}: «linea» debe ser [[x, y], [x, y]]')
    elif tipo == 'matriz':
        et = fig.get('etiquetas') or []
        vals = fig.get('valores') or []
        if len(et) < 2 or len(vals) != len(et) or any(len(f) != len(et) or not all(es_num(x) for x in f) for f in vals):
            error(f'{donde}: «matriz» necesita n «etiquetas» y una matriz n × n de números en «valores»')
    else:
        error(f'{donde}: tipo de gráfico «{tipo}» (usa lineas, roc, barras, histograma, boxplot, dispersion o matriz)')
        return
    if tipo in ('lineas', 'roc', 'barras', 'histograma', 'dispersion') and len(series) > MAX_SERIES:
        error(f'{donde}: {len(series)} series; como máximo {MAX_SERIES} (pártelo en varios gráficos)')
    for campo in ('titulo', 'nota'):
        if campo in fig and not isinstance(fig[campo], str):
            error(f'{donde}: «{campo}» debe ser texto')


# ---- preguntas ----
ids = set()
for i, q in enumerate(banco):
    qid = q.get('id') or f'(pregunta {i + 1})'
    if qid in ids:
        error(f'{qid}: id repetido')
    ids.add(qid)

    tipo = q.get('tipo')
    if tipo not in ('abierta', 'test'):
        error(f'{qid}: tipo «{tipo}» (usa «abierta» o «test»)')

    if q.get('pruebas'):
        avisos.append(f'{qid}: el campo «pruebas» ya no se usa (la web se organiza por unidades)')
    leccion = leccion_principal(q)
    if not leccion:
        error(f'{qid}: el primer enlace con código de lección (UnLm) decide su unidad y su lección, y no tiene ninguno')
    elif leccion.split('L')[0] not in unidades:
        error(f'{qid}: la lección {leccion} no es de ninguna unidad de config.json')

    if q.get('tema') not in temas:
        error(f'{qid}: tema desconocido «{q.get("tema")}»')
    if niveles and q.get('nivel') not in niveles:
        error(f'{qid}: nivel «{q.get("nivel")}» (usa uno de {sorted(niveles)})')

    if not q.get('enunciado'):
        error(f'{qid}: falta el enunciado')
    for k, t in enumerate(q.get('enunciado', [])):
        revisar_html(f'{qid} enunciado[{k}]', t)

    for k, tabla in enumerate(q.get('datos', [])):
        cols = tabla.get('columnas', [])
        for f, fila in enumerate(tabla.get('filas', [])):
            if len(fila) != len(cols):
                error(f'{qid} datos[{k}]: la fila {f + 1} tiene {len(fila)} celdas y hay {len(cols)} columnas')
    for k, fig in enumerate(q.get('figuras', [])):
        revisar_figura(f'{qid} figuras[{k}]', fig)

    if tipo == 'abierta':
        uso = q.get('uso')
        if uso not in ('repaso', 'practica'):
            error(f'{qid}: uso «{uso}» (usa «repaso» o «practica»)')
        obligatorios = ('solucion', 'criterios', 'apartados') if uso == 'practica' else ('solucion',)
        for campo in obligatorios:
            if not q.get(campo):
                error(f'{qid}: falta «{campo}»')
        for campo in ('apartados', 'solucion', 'criterios', 'explicacion'):
            for k, t in enumerate(q.get(campo, [])):
                revisar_html(f'{qid} {campo}[{k}]', t)
    elif tipo == 'test':
        ops = q.get('opciones', [])
        if len(ops) < 3:
            error(f'{qid}: tiene {len(ops)} opciones (mínimo 3)')
        correctas = sum(1 for o in ops if o.get('correcta'))
        if correctas != 1:
            error(f'{qid}: tiene {correctas} opciones correctas (debe ser 1)')
        for k, o in enumerate(ops):
            if not o.get('explicacion'):
                error(f'{qid}: la opción {"ABCDEFGHIJ"[k]} no tiene explicación')
            revisar_html(f'{qid} opción {"ABCDEFGHIJ"[k]}', o.get('texto', ''))
            revisar_html(f'{qid} explicación {"ABCDEFGHIJ"[k]}', o.get('explicacion', ''))
            # Las opciones se barajan (tools/barajar_opciones.py): ningún texto puede citar otra por su letra o su posición.
            for campo in ('texto', 'explicacion'):
                if CITA_OPCION.search(o.get(campo, '')):
                    error(f'{qid}: la opción {"ABCDEFGHIJ"[k]} cita otra opción por su letra o su posición ({campo})')
        if correctas == 1 and len(ops) > 1:
            largos = [len(re.sub(r'<[^>]+>', '', o.get('texto', ''))) for o in ops]
            c = next(k for k, o in enumerate(ops) if o.get('correcta'))
            otro = max(l for k, l in enumerate(largos) if k != c)
            posiciones_correcta.append(c)
            if c != barajado.numero(qid) % len(ops):
                sin_barajar.append(qid)
            correcta_mas_larga.append(largos[c] > otro)
            if largos[c] > 1.25 * otro and largos[c] - otro > 8:
                avisos.append(f'{qid}: la opción correcta es mucho más larga que las demás (se adivina sin saber); pasa el porqué a su explicación')
        for k, t in enumerate(q.get('explicacion', [])):
            revisar_html(f'{qid} explicacion[{k}]', t)

    if q.get('aviso'):
        revisar_html(f'{qid} aviso', q['aviso'])

    if not q.get('enlaces'):
        error(f'{qid}: falta al menos un enlace a la web del curso')
    for e in q.get('enlaces', []):
        if isinstance(e, str):
            if e not in lecciones:
                error(f'{qid}: enlace «{e}» no está en config.json → lecciones')
        elif not (isinstance(e, dict) and e.get('texto') and e.get('url')):
            error(f'{qid}: enlace mal formado (usa un código de lección o {{"texto", "url"}})')

    todo = ' '.join(textos(q))
    for nombre in PROHIBIDOS:
        if re.search(re.escape(nombre), todo, re.IGNORECASE):
            error(f'{qid}: contiene «{nombre}», del dataset real de una actividad o de una prueba anterior')

# ---- resumen por unidad ----
print(f'{"":<52} {"test":>5} {"abiertas":>9} {"práctica":>9}')
for codigo, u in unidades.items():
    qs = [q for q in banco if (leccion_principal(q) or '').split('L')[0] == codigo]
    s = sum(1 for q in qs if q.get('tipo') == 'test')
    a = sum(1 for q in qs if q.get('tipo') == 'abierta' and q.get('uso') == 'repaso')
    c = sum(1 for q in qs if q.get('uso') == 'practica')
    print(f'{u["nombre"]:<52} {s:>5} {a:>9} {c:>9}')
    for tipo, nombre in (('test', 'test'), ('abierta', 'abiertas')):
        cuenta = {n: sum(1 for q in qs if q.get('tipo') == tipo and q.get('uso') != 'practica' and q.get('nivel') == n) for n in niveles}
        print(f'   niveles ({nombre}): ' + ', '.join(f'{niveles[n]}: {cuenta[n]}' for n in niveles))
        for n in niveles:
            if cuenta[n] < 3:
                avisos.append(f'{u["nombre"]}, {nombre}, {niveles[n]}: solo {cuenta[n]} preguntas (mínimo 3)')
    cuenta = {n: sum(1 for q in qs if q.get('uso') == 'practica' and q.get('nivel') == n) for n in niveles}
    print('   niveles (práctica): ' + ', '.join(f'{niveles[n]}: {cuenta[n]}' for n in niveles))
    for n in niveles:
        # En la práctica, 5 casos por nivel; en Primeros pasos (el nivel 0), 3.
        minimo = 3 if n == 0 else 5
        if cuenta[n] < minimo:
            avisos.append(f'{u["nombre"]}, práctica, {niveles[n]}: solo {cuenta[n]} casos (mínimo {minimo})')
print(f'Total: {len(banco)} preguntas, {sum(1 for q in banco if q.get("figuras"))} con gráficos')
if posiciones_correcta:
    n = len(posiciones_correcta)
    letras = [posiciones_correcta.count(k) for k in range(4)]
    print(f'Test: correcta en A, B, C y D: {", ".join(map(str, letras))}; es la opción más larga en {sum(correcta_mas_larga)} de {n}')
    if sin_barajar:
        avisos.append(f'{len(sin_barajar)} pregunta(s) tipo test sin barajar ({", ".join(sin_barajar[:5])}{"…" if len(sin_barajar) > 5 else ""}): '
                      'ejecuta python -I tools/barajar_opciones.py')
    if max(letras) > 0.35 * n:
        avisos.append('la opción correcta se concentra en una letra: ejecuta python -I tools/barajar_opciones.py')
    if sum(correcta_mas_larga) > 0.35 * n:
        avisos.append('la opción correcta es demasiadas veces la más larga: iguala la longitud de las opciones')

if not RUTA_PROHIBIDOS.exists():
    avisos.append('no está tools/prohibidos.txt: no se han buscado nombres de datasets reales ni de casos de pruebas')
for a in avisos:
    print('AVISO:', a)
for e in errores:
    print('ERROR:', e)
print(f'{len(errores)} error(es).' if errores else 'Sin errores.')
sys.exit(1 if errores else 0)
