"""Genera web/datos/apuntes/U1.json … U5.json, los apuntes que usa el tutor de «Resuelve tus dudas».

Lee una copia del repositorio público del curso (https://github.com/mireiaconsarnau/machine_learning):
- las fichas de resumen de cada lección (resumenes/unidadN.md), en texto, con las figuras descritas por su texto alternativo;
- la teoría de cada lección (unidadN/lM.pdf), partida en fragmentos de unos 1.200 caracteres para que la página
  pueda enviar a Claude solo los que tienen que ver con cada duda;
- los cuadernos (unidadN/cuadernos/UnLmm.ipynb): su texto y su código, sin las salidas, en fragmentos de unos
  1.500 caracteres, para explicar el código que pegue el alumno con los ejemplos del curso.

Uso (desde la raíz del repositorio; necesita pdftotext):
    git clone --depth 1 https://github.com/mireiaconsarnau/machine_learning.git <carpeta>
    python -I tools/generar_apuntes.py <carpeta>
Vuelve a generarlos si cambian los apuntes del curso.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CURSO = Path(sys.argv[1])
SALIDA = RAIZ / 'web' / 'datos' / 'apuntes'
TAM_FRAGMENTO = 1200
TAM_CUADERNO = 1500
LICENCIA = re.compile(r'^Este trabajo est[áa] licenciado', re.I)

# Discrepancias conocidas entre el material y la buena práctica (docs/material_teorico.md §4).
# El tutor explica la buena práctica sin penalizar a quien haya seguido el material.
NOTAS = {
    1: [],
    2: ['Algunos cuadernos imputan, escalan o eliminan atípicos con todo el dataset antes de dividir; lo recomendable es dividir primero y ajustar las transformaciones solo con el entrenamiento.',
        'Algunos cuadernos usan LabelEncoder en variables nominales, lo que inventa un orden; en las nominales es mejor One-Hot y en las ordinales, una codificación ordinal que respete el orden.',
        'No se imputa la variable objetivo: las filas sin objetivo se eliminan del entrenamiento.',
        'Spearman detecta relaciones monótonas, no cualquier relación no lineal.'],
    3: ['En el ejemplo del VIH la clase positiva es «Sano», por eso el material vigila la precisión; con la convención habitual (positivo = enfermo) esos errores serían falsos negativos y se vigilaría la sensibilidad. Las dos lecturas son válidas si el razonamiento es coherente.',
        'En ese mismo ejemplo, el Kappa correcto es aproximadamente 0,59 (no 0,55) y el F1, aproximadamente 0,88.',
        'En la teoría las filas de la matriz de confusión son la predicción; en scikit-learn, las filas son la clase real.',
        'Los umbrales orientativos del error porcentual son 10 % / 25 % en la teoría y 10 % / 30 % en los cuadernos.',
        'Lo recomendable es elegir el modelo con validación (o validación cruzada) y reservar el test para la evaluación final; joblib guarda solo el modelo, así que conviene guardar también el preprocesado (mejor, en un Pipeline).'],
    4: ['Al calcular las métricas de clustering o el PCA hay que excluir la columna con la etiqueta del grupo (fe de erratas del curso).',
        'Las componentes del PCA son incorreladas, no «independientes».'],
    5: ['No se debe usar el conjunto de test como validation_data al entrenar una red: para eso está la validación.',
        'Al predecir con un modelo preentrenado hay que aplicar el mismo preprocess_input que al entrenar.',
        'Las pérdidas MSE y entropía cruzada binaria no se pueden comparar entre sí.'],
}


def texto_html(s):
    """Convierte el HTML de una ficha en texto: las figuras se quedan con su descripción y las listas, con guiones."""
    s = re.sub(r'<svg[^>]*aria-label="([^"]*)"[^>]*>.*?</svg>', lambda m: '\n[Figura: ' + m.group(1) + ']\n', s, flags=re.S)
    s = re.sub(r'<svg.*?</svg>', '', s, flags=re.S)
    s = re.sub(r'<span class="num">\d+</span>', '', s)
    s = re.sub(r'<(div|li) class="(idea|paso|error|item|termino|par|fila|tarjeta)[^"]*"[^>]*>', '\n- ', s)
    s = re.sub(r'<(li)[^>]*>', '\n- ', s)
    s = re.sub(r'</?(strong|b|em|i|code|a|abbr|sub|sup)\b[^>]*>', '', s)
    s = re.sub(r'<(p|div|tr|h\d|br)[^>]*>', '\n', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'\{[:#][^}]*\}', '', s)          # atributos de Kramdown: {#leccion-1}, {: .btn}
    s = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s)  # enlaces Markdown: solo el texto
    lineas = [re.sub(r'\s+', ' ', l).strip() for l in s.split('\n')]
    salida, previa = [], None
    for l in lineas:
        if l in ('', '-') and previa in ('', None):
            continue
        if l == '-':
            continue
        salida.append(l)
        previa = l
    return '\n'.join(salida).strip()


def fichas(unidad):
    md = (CURSO / 'resumenes' / f'unidad{unidad}.md').read_text(encoding='utf-8')
    md = re.sub(r'^---.*?---', '', md, count=1, flags=re.S)
    partes = re.split(r'^## ', md, flags=re.M)[1:]
    out, sintesis = {}, ''
    for p in partes:
        titulo, _, cuerpo = p.partition('\n')
        m = re.match(r'Lecci[oó]n (\d+)', titulo)
        if m:
            out[f'U{unidad}L{m.group(1)}'] = texto_html(cuerpo)
        elif 'ntesis' in titulo:
            sintesis = texto_html(cuerpo)
    return out, sintesis


def teoria(pdf):
    crudo = subprocess.run(['pdftotext', '-enc', 'UTF-8', str(pdf), '-'], capture_output=True, check=True).stdout.decode('utf-8')
    crudo = crudo.replace('‬‭', ' ').replace('‭', '').replace('‬', '').replace('\f', '\n')
    crudo = crudo.replace('', '-').replace('●', '-').replace('•', '-')
    parrafos = []
    for l in crudo.split('\n'):
        l = re.sub(r'\s+', ' ', l).strip()
        if not l or LICENCIA.match(l) or re.fullmatch(r'\d{1,3}', l):
            continue
        parrafos.append(l)
    # Un párrafo corto sin punto final se toma como título de apartado.
    fragmentos, actual, seccion, seccion_actual = [], [], '', ''
    for l in parrafos:
        es_titulo = len(l) < 90 and not l.endswith(('.', ':', ';', ','))
        if es_titulo:
            seccion = l
        if actual and (sum(len(x) for x in actual) + len(l) > TAM_FRAGMENTO or (es_titulo and sum(len(x) for x in actual) > TAM_FRAGMENTO / 2)):
            fragmentos.append({'s': seccion_actual, 'x': '\n'.join(actual)})
            actual = []
        if not actual:
            seccion_actual = seccion
        actual.append(l)
    if actual:
        fragmentos.append({'s': seccion_actual, 'x': '\n'.join(actual)})
    return fragmentos


def cuaderno(ruta):
    """Texto y código de un cuaderno, sin salidas ni imágenes, en fragmentos con el título del apartado."""
    nb = json.loads(ruta.read_text(encoding='utf-8'))
    bloques, seccion = [], ''
    for celda in nb.get('cells', []):
        t = ''.join(celda.get('source', [])).strip()
        if not t:
            continue
        if celda['cell_type'] == 'markdown':
            t = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', t)           # imágenes
            t = re.sub(r'<img[^>]*>', '', t)
            t = re.sub(r'\(data:[^)]*\)|data:[\w/+.-]+;base64,[\w+/=]+', '', t)
            t = re.sub(r'<[^>]+>', ' ', html.unescape(t))
            t = re.sub(r'[ \t]+', ' ', t).strip()
            titulos = re.findall(r'^#+\s*(.+)$', t, flags=re.M)
            if titulos:
                seccion = titulos[-1].replace('*', '').strip()
            if t:
                bloques.append((seccion, 'texto', t))
        elif celda['cell_type'] == 'code':
            # Una celda muy larga se parte por líneas para que quepa en un fragmento.
            trozo = []
            for linea in t.split('\n'):
                if trozo and sum(len(x) + 1 for x in trozo) + len(linea) > TAM_CUADERNO - 40:
                    bloques.append((seccion, 'codigo', '\n'.join(trozo)))
                    trozo = []
                trozo.append(linea)
            bloques.append((seccion, 'codigo', '\n'.join(trozo)))

    # Las celdas de código seguidas van juntas en un solo bloque ```python.
    def unir(partes):
        salida = []
        for tipo, t in partes:
            if tipo == 'codigo' and salida and salida[-1][0] == 'codigo':
                salida[-1] = ('codigo', salida[-1][1] + '\n\n' + t)
            else:
                salida.append((tipo, t))
        return '\n\n'.join('```python\n' + t + '\n```' if tipo == 'codigo' else t for tipo, t in salida)

    fragmentos, actual, seccion_actual = [], [], ''
    for seccion, tipo, t in bloques:
        if actual and sum(len(x) for _, x in actual) + len(t) > TAM_CUADERNO:
            fragmentos.append({'s': seccion_actual, 'x': unir(actual)})
            actual = []
        if not actual:
            seccion_actual = seccion
        actual.append((tipo, t))
    if actual:
        fragmentos.append({'s': seccion_actual, 'x': unir(actual)})
    return fragmentos


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    SALIDA.mkdir(parents=True, exist_ok=True)
    for u in range(1, 6):
        fich, sintesis = fichas(u)
        frags = []
        for pdf in sorted((CURSO / f'unidad{u}').glob('l*.pdf'), key=lambda p: int(re.sub(r'\D', '', p.stem))):
            leccion = f'U{u}L{int(re.sub(r"[^0-9]", "", pdf.stem))}'
            frags += [dict(l=leccion, **f) for f in teoria(pdf)]
        # UnLmm.ipynb es el cuaderno mm de la lección m (p. ej. U3L29 → lección U3L2).
        cuads = []
        for nb in sorted((CURSO / f'unidad{u}' / 'cuadernos').glob('U*L*.ipynb')):
            m = re.fullmatch(rf'U{u}L(\d)\d+', nb.stem)
            if m:
                cuads += [dict(c=nb.stem, l=f'U{u}L{m.group(1)}', **f) for f in cuaderno(nb)]
        datos = {'unidad': f'U{u}', 'notas': NOTAS[u], 'fichas': fich, 'sintesis': sintesis, 'fragmentos': frags, 'cuadernos': cuads}
        ruta = SALIDA / f'U{u}.json'
        ruta.write_text(json.dumps(datos, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        print(f'U{u}: {len(fich)} fichas ({sum(len(t) for t in fich.values())} caracteres), síntesis {len(sintesis)}, '
              f'{len(frags)} fragmentos de teoría ({sum(len(f["x"]) for f in frags)} caracteres), '
              f'{len(cuads)} de cuadernos ({sum(len(f["x"]) for f in cuads)} caracteres) → {ruta.stat().st_size // 1024} KB')
