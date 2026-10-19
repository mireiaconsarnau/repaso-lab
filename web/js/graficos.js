/*
 * Gráficos de las preguntas (SVG dibujado en la página a partir de los datos del banco).
 *
 *   Graficos.crear(figura)    → elemento <figure> con título, leyenda, gráfico y «Ver los datos del gráfico».
 *   Graficos.describir(figura) → texto con los datos, para que Claude pueda corregir sin ver la imagen.
 *
 * Tipos (campo «tipo» de cada figura):
 *   lineas      { eje_x, eje_y, series: [{ nombre, puntos: [[x, y], …] }], x_min?, x_max?, y_min?, y_max?, referencia?: [[x, y], [x, y]], referencia_nombre? }
 *   roc         como «lineas», con ejes de 0 a 1 y la diagonal del azar
 *   barras      { eje_y, categorias: […], series: [{ nombre, valores: […] }], y_max? }
 *   histograma  { eje_x, eje_y, limites: [b0, b1, …, bn], series: [{ nombre, conteos: […] }] }
 *   boxplot     { cajas: [{ nombre, min, q1, mediana, q3, max, atipicos: […] }] }   (cada variable con su propia escala)
 *   dispersion  { eje_x, eje_y, grupos: [{ nombre, puntos: [[x, y], …] }], linea?: [[x, y], [x, y]], linea_nombre? }
 *   matriz      { etiquetas: […], valores: [[…], …], titulo_filas?, titulo_columnas? }   (filas: real; columnas: predicho)
 *
 * Colores: paleta categórica fija y validada (azul, naranja, aguamarina; como máximo 3 series), en estilos.css.
 */
(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';
  var W = 440, H = 260;
  var M = { izq: 50, der: 14, arr: 14, aba: 44 };

  function svg(tag, attrs, hijos) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { if (attrs[k] !== null && attrs[k] !== undefined) n.setAttribute(k, attrs[k]); });
    (hijos || []).forEach(function (h) { if (h) n.appendChild(h); });
    return n;
  }
  function texto(x, y, contenido, clase, ancla) {
    var t = svg('text', { x: x, y: y, class: clase || 'g-texto', 'text-anchor': ancla || 'middle' });
    t.textContent = contenido;
    return t;
  }
  function tooltip(nodo, contenido) {
    var t = document.createElementNS(NS, 'title');
    t.textContent = contenido;
    nodo.appendChild(t);
    return nodo;
  }
  function html(tag, clase, hijos) {
    var n = document.createElement(tag);
    if (clase) n.className = clase;
    (hijos || []).forEach(function (h) { if (h !== null && h !== undefined) n.appendChild(typeof h === 'string' ? document.createTextNode(h) : h); });
    return n;
  }
  function num(v) {
    if (typeof v !== 'number') return String(v);
    return v.toLocaleString('es-ES', { maximumFractionDigits: Math.abs(v) < 10 ? 3 : 1 });
  }
  function pasoBonito(rango, n) {
    var bruto = rango / n;
    var e = Math.pow(10, Math.floor(Math.log(bruto) / Math.LN10));
    var f = bruto / e;
    return (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * e;
  }
  function marcas(min, max, n) {
    if (max === min) max = min + 1;
    var paso = pasoBonito(max - min, n || 4);
    var lista = [];
    for (var v = Math.ceil(min / paso - 1e-9) * paso; v <= max + paso * 1e-6; v += paso) lista.push(+v.toFixed(10));
    return lista;
  }
  // Como marcas(), pero la primera y la última quedan fuera de los datos: así ningún valor se sale del eje.
  function marcasQueCubren(min, max, n) {
    if (max === min) max = min + 1;
    var paso = pasoBonito(max - min, n || 4);
    var lista = [];
    for (var v = Math.floor(min / paso + 1e-9) * paso; v <= Math.ceil(max / paso - 1e-9) * paso + paso * 1e-6; v += paso) lista.push(+v.toFixed(10));
    return lista;
  }
  function escala(d0, d1, r0, r1) { return function (v) { return r0 + (v - d0) / ((d1 - d0) || 1) * (r1 - r0); }; }
  function claseSerie(i) { return 'g-serie-' + (Math.min(i, 2) + 1); }

  // Ejes, rejilla horizontal y títulos de eje (compartido por líneas, dispersión e histograma).
  function ejes(g, x, y, xs, ys, fig, formatoX) {
    ys.forEach(function (v) {
      g.appendChild(svg('line', { x1: M.izq, x2: W - M.der, y1: y(v), y2: y(v), class: 'g-rejilla' }));
      g.appendChild(texto(M.izq - 6, y(v) + 4, num(v), 'g-marca', 'end'));
    });
    xs.forEach(function (v) { g.appendChild(texto(x(v), H - M.aba + 16, formatoX ? formatoX(v) : num(v), 'g-marca')); });
    g.appendChild(svg('line', { x1: M.izq, x2: W - M.der, y1: H - M.aba, y2: H - M.aba, class: 'g-eje' }));
    if (fig.eje_x) g.appendChild(texto((M.izq + W - M.der) / 2, H - 6, fig.eje_x, 'g-titulo-eje'));
    if (fig.eje_y) {
      var t = texto(0, 0, fig.eje_y, 'g-titulo-eje');
      t.setAttribute('transform', 'translate(12,' + ((M.arr + H - M.aba) / 2) + ') rotate(-90)');
      g.appendChild(t);
    }
  }

  function rangoPuntos(listas, eje) {
    var vals = [];
    listas.forEach(function (l) { l.forEach(function (p) { vals.push(p[eje]); }); });
    return [Math.min.apply(null, vals), Math.max.apply(null, vals)];
  }

  // ---------- líneas (curvas de aprendizaje, de pérdida, codo, k-distancias, ROC…) ----------
  function lineas(fig, esRoc) {
    var series = fig.series || [];
    var rx = rangoPuntos(series.map(function (s) { return s.puntos; }), 0);
    var ry = rangoPuntos(series.map(function (s) { return s.puntos; }), 1);
    var x0 = esRoc ? 0 : (fig.x_min !== undefined ? fig.x_min : rx[0]);
    var x1 = esRoc ? 1 : (fig.x_max !== undefined ? fig.x_max : rx[1]);
    var y0 = esRoc ? 0 : (fig.y_min !== undefined ? fig.y_min : Math.min(0, ry[0]));
    var ys = marcas(y0, esRoc ? 1 : (fig.y_max !== undefined ? fig.y_max : ry[1]), 4);
    var y1 = esRoc ? 1 : Math.max(ys[ys.length - 1], fig.y_max !== undefined ? fig.y_max : ry[1]);
    var x = escala(x0, x1, M.izq, W - M.der), y = escala(y0, y1, H - M.aba, M.arr);
    var g = svg('g');
    ejes(g, x, y, marcas(x0, x1, 5), esRoc ? [0, 0.25, 0.5, 0.75, 1] : ys, fig);
    var ref = esRoc ? [[0, 0], [1, 1]] : fig.referencia;
    if (ref) g.appendChild(tooltip(svg('line', { x1: x(ref[0][0]), y1: y(ref[0][1]), x2: x(ref[1][0]), y2: y(ref[1][1]), class: 'g-referencia' }),
      esRoc ? 'Diagonal: un modelo que decide al azar' : (fig.referencia_nombre || 'Referencia')));
    series.forEach(function (s, i) {
      var d = s.puntos.map(function (p, k) { return (k ? 'L' : 'M') + x(p[0]).toFixed(1) + ' ' + y(p[1]).toFixed(1); }).join('');
      g.appendChild(svg('path', { d: d, class: 'g-linea ' + claseSerie(i) }));
      if (s.puntos.length <= 24) {
        s.puntos.forEach(function (p) {
          g.appendChild(tooltip(svg('circle', { cx: x(p[0]), cy: y(p[1]), r: 4, class: 'g-marcador ' + claseSerie(i) }),
            s.nombre + ': ' + (fig.eje_x || 'x') + ' ' + num(p[0]) + ' → ' + num(p[1])));
        });
      }
    });
    return g;
  }

  // ---------- barras (agrupadas si hay varias series) ----------
  function barras(fig) {
    var cats = fig.categorias, series = fig.series;
    var maxV = fig.y_max || Math.max.apply(null, series.map(function (s) { return Math.max.apply(null, s.valores); }));
    var ys = marcas(0, maxV, 4);
    var y1 = Math.max(ys[ys.length - 1], maxV);
    var y = escala(0, y1, H - M.aba, M.arr);
    var banda = (W - M.izq - M.der) / cats.length;
    var ancho = Math.min(24, (banda * 0.7) / series.length);
    var g = svg('g');
    ys.forEach(function (v) {
      g.appendChild(svg('line', { x1: M.izq, x2: W - M.der, y1: y(v), y2: y(v), class: 'g-rejilla' }));
      g.appendChild(texto(M.izq - 6, y(v) + 4, num(v), 'g-marca', 'end'));
    });
    g.appendChild(svg('line', { x1: M.izq, x2: W - M.der, y1: H - M.aba, y2: H - M.aba, class: 'g-eje' }));
    cats.forEach(function (c, ci) {
      var centro = M.izq + banda * (ci + 0.5);
      var etiqueta = texto(centro, H - M.aba + 16, c, 'g-marca');
      g.appendChild(etiqueta);
      series.forEach(function (s, si) {
        var v = s.valores[ci];
        var bx = centro - (ancho * series.length + 2 * (series.length - 1)) / 2 + si * (ancho + 2);
        var by = y(v), base = H - M.aba, r = Math.min(4, (base - by) / 2);
        var d = 'M' + bx + ' ' + base + 'V' + (by + r) + 'Q' + bx + ' ' + by + ' ' + (bx + r) + ' ' + by +
          'H' + (bx + ancho - r) + 'Q' + (bx + ancho) + ' ' + by + ' ' + (bx + ancho) + ' ' + (by + r) + 'V' + base + 'Z';
        g.appendChild(tooltip(svg('path', { d: d, class: 'g-barra ' + claseSerie(si) }), (series.length > 1 ? s.nombre + ' · ' : '') + c + ': ' + num(v)));
        if (series.length === 1 && cats.length <= 10) g.appendChild(texto(bx + ancho / 2, by - 5, num(v), 'g-valor'));
      });
    });
    if (fig.eje_y) {
      var t = texto(0, 0, fig.eje_y, 'g-titulo-eje');
      t.setAttribute('transform', 'translate(12,' + ((M.arr + H - M.aba) / 2) + ') rotate(-90)');
      g.appendChild(t);
    }
    if (fig.eje_x) g.appendChild(texto((M.izq + W - M.der) / 2, H - 6, fig.eje_x, 'g-titulo-eje'));
    return g;
  }

  // ---------- histograma (intervalos contiguos, con 2 px de separación) ----------
  function histograma(fig) {
    var lim = fig.limites, series = fig.series;
    var maxV = Math.max.apply(null, series.map(function (s) { return Math.max.apply(null, s.conteos); }));
    var ys = marcas(0, maxV, 4), y1 = Math.max(ys[ys.length - 1], maxV);
    var x = escala(lim[0], lim[lim.length - 1], M.izq, W - M.der), y = escala(0, y1, H - M.aba, M.arr);
    var g = svg('g');
    ejes(g, x, y, marcas(lim[0], lim[lim.length - 1], 6), ys, fig);
    series.forEach(function (s, si) {
      s.conteos.forEach(function (c, i) {
        if (!c) return;
        var a = x(lim[i]) + 1, b = x(lim[i + 1]) - 1;
        var w = (b - a) / series.length;
        var bx = a + si * w;
        g.appendChild(tooltip(svg('rect', { x: bx, y: y(c), width: Math.max(w, 1), height: (H - M.aba) - y(c), class: 'g-barra ' + claseSerie(si) }),
          (series.length > 1 ? s.nombre + ' · ' : '') + 'de ' + num(lim[i]) + ' a ' + num(lim[i + 1]) + ': ' + num(c)));
      });
    });
    return g;
  }

  // ---------- boxplot (una caja por variable, cada una con su escala: no se comparten ejes) ----------
  function boxplot(fig) {
    var cajas = fig.cajas;
    var g = svg('g');
    var ancho = (W - 8) / cajas.length;
    cajas.forEach(function (c, i) {
      var izq = 8 + i * ancho + 38, der = 8 + (i + 1) * ancho - 10;
      var valores = [c.min, c.max].concat(c.atipicos || []);
      var ys = marcasQueCubren(Math.min.apply(null, valores), Math.max.apply(null, valores), 4);
      var y = escala(ys[0], ys[ys.length - 1], H - M.aba, M.arr);
      ys.forEach(function (v) {
        g.appendChild(svg('line', { x1: izq, x2: der, y1: y(v), y2: y(v), class: 'g-rejilla' }));
        g.appendChild(texto(izq - 5, y(v) + 4, num(v), 'g-marca', 'end'));
      });
      var cx = (izq + der) / 2, bw = Math.min(30, (der - izq) * 0.5);
      g.appendChild(svg('line', { x1: cx, x2: cx, y1: y(c.max), y2: y(c.q3), class: 'g-bigote' }));
      g.appendChild(svg('line', { x1: cx, x2: cx, y1: y(c.q1), y2: y(c.min), class: 'g-bigote' }));
      g.appendChild(svg('line', { x1: cx - bw / 4, x2: cx + bw / 4, y1: y(c.max), y2: y(c.max), class: 'g-bigote' }));
      g.appendChild(svg('line', { x1: cx - bw / 4, x2: cx + bw / 4, y1: y(c.min), y2: y(c.min), class: 'g-bigote' }));
      g.appendChild(tooltip(svg('rect', { x: cx - bw / 2, y: y(c.q3), width: bw, height: Math.max(1, y(c.q1) - y(c.q3)), rx: 3, class: 'g-caja' }),
        c.nombre + ': Q1 ' + num(c.q1) + ', mediana ' + num(c.mediana) + ', Q3 ' + num(c.q3)));
      g.appendChild(svg('line', { x1: cx - bw / 2, x2: cx + bw / 2, y1: y(c.mediana), y2: y(c.mediana), class: 'g-mediana' }));
      (c.atipicos || []).forEach(function (v) {
        g.appendChild(tooltip(svg('circle', { cx: cx, cy: y(v), r: 4, class: 'g-atipico' }), c.nombre + ': valor atípico ' + num(v)));
      });
      g.appendChild(texto(cx, H - M.aba + 18, c.nombre, 'g-titulo-eje'));
    });
    return g;
  }

  // ---------- dispersión (grupos y, opcionalmente, una recta de referencia) ----------
  function dispersion(fig) {
    var grupos = fig.grupos;
    var todos = grupos.map(function (gr) { return gr.puntos; });
    if (fig.linea) todos.push(fig.linea);
    var rx = rangoPuntos(todos, 0), ry = rangoPuntos(todos, 1);
    var xs = marcasQueCubren(fig.x_min !== undefined ? fig.x_min : rx[0], fig.x_max !== undefined ? fig.x_max : rx[1], 5);
    var ys = marcasQueCubren(fig.y_min !== undefined ? fig.y_min : ry[0], fig.y_max !== undefined ? fig.y_max : ry[1], 4);
    var x = escala(xs[0], xs[xs.length - 1], M.izq, W - M.der), y = escala(ys[0], ys[ys.length - 1], H - M.aba, M.arr);
    var g = svg('g');
    ejes(g, x, y, xs, ys, fig);
    if (fig.linea) g.appendChild(tooltip(svg('line', { x1: x(fig.linea[0][0]), y1: y(fig.linea[0][1]), x2: x(fig.linea[1][0]), y2: y(fig.linea[1][1]), class: 'g-referencia' }), fig.linea_nombre || 'Referencia'));
    grupos.forEach(function (gr, i) {
      gr.puntos.forEach(function (p) {
        g.appendChild(tooltip(svg('circle', { cx: x(p[0]), cy: y(p[1]), r: 4.5, class: 'g-punto ' + (gr.sin_color ? 'g-serie-neutra' : claseSerie(i)) }),
          gr.nombre + ': (' + num(p[0]) + '; ' + num(p[1]) + ')'));
      });
    });
    return g;
  }

  // ---------- matriz de confusión (filas: real; columnas: predicho; intensidad según el valor) ----------
  function matriz(fig) {
    var et = fig.etiquetas, v = fig.valores, n = et.length;
    var max = Math.max.apply(null, v.map(function (f) { return Math.max.apply(null, f); }));
    var izq = 118, arr = 46, lado = Math.min((W - izq - 10) / n, (H - arr - 10) / n);
    var g = svg('g');
    g.appendChild(texto(izq + lado * n / 2, 14, fig.titulo_columnas || 'Predicho', 'g-titulo-eje'));
    var t = texto(0, 0, fig.titulo_filas || 'Real', 'g-titulo-eje');
    t.setAttribute('transform', 'translate(14,' + (arr + lado * n / 2) + ') rotate(-90)');
    g.appendChild(t);
    et.forEach(function (e, j) { g.appendChild(texto(izq + lado * (j + 0.5), arr - 10, e, 'g-marca')); });
    et.forEach(function (e, i) {
      g.appendChild(texto(izq - 8, arr + lado * (i + 0.5) + 4, e, 'g-marca', 'end'));
      et.forEach(function (_, j) {
        var val = v[i][j], intensidad = max ? val / max : 0;
        var celda = svg('rect', { x: izq + lado * j + 1, y: arr + lado * i + 1, width: lado - 2, height: lado - 2, rx: 4, class: 'g-celda' });
        celda.style.fill = 'color-mix(in srgb, var(--serie-1) ' + Math.round(8 + intensidad * 82) + '%, var(--hoja))';
        g.appendChild(tooltip(celda, 'Real ' + e + ', predicho ' + et[j] + ': ' + num(val)));
        g.appendChild(texto(izq + lado * (j + 0.5), arr + lado * (i + 0.5) + 5, num(val), intensidad > 0.55 ? 'g-valor-celda g-valor-claro' : 'g-valor-celda'));
      });
    });
    return g;
  }

  // ---------- leyenda, tabla de datos y descripción ----------
  function nombresSeries(fig) {
    if (fig.tipo === 'lineas' || fig.tipo === 'roc' || fig.tipo === 'barras' || fig.tipo === 'histograma') return fig.series.map(function (s) { return s.nombre; });
    if (fig.tipo === 'dispersion') return fig.grupos.map(function (g) { return g.nombre; });
    return [];
  }
  function leyenda(fig) {
    var nombres = nombresSeries(fig);
    var extra = [];
    if (fig.tipo === 'roc') extra.push(['g-clave-referencia', 'Azar (diagonal)']);
    else if (fig.referencia && fig.referencia_nombre) extra.push(['g-clave-referencia', fig.referencia_nombre]);
    if (fig.tipo === 'dispersion' && fig.linea && fig.linea_nombre) extra.push(['g-clave-referencia', fig.linea_nombre]);
    // Con una sola serie no hace falta leyenda (el título ya dice qué se dibuja); sí se explica la línea de referencia.
    var series = nombres.length >= 2 ? nombres.map(function (nm, i) {
      var neutro = fig.tipo === 'dispersion' && fig.grupos[i].sin_color;
      return html('li', null, [html('span', 'g-clave ' + (neutro ? 'g-serie-neutra' : claseSerie(i))), nm]);
    }) : [];
    var items = series.concat(extra.map(function (e) { return html('li', null, [html('span', 'g-clave ' + e[0]), e[1]]); }));
    return items.length ? html('ul', 'g-leyenda', items) : null;
  }
  function filasTabla(fig) {
    switch (fig.tipo) {
      case 'lineas':
      case 'roc':
        return [['Serie', fig.eje_x || 'x', fig.eje_y || 'y']].concat([].concat.apply([], fig.series.map(function (s) {
          return s.puntos.map(function (p) { return [s.nombre, num(p[0]), num(p[1])]; });
        })));
      case 'barras':
        return [['Categoría'].concat(fig.series.map(function (s) { return s.nombre; }))].concat(fig.categorias.map(function (c, i) {
          return [c].concat(fig.series.map(function (s) { return num(s.valores[i]); }));
        }));
      case 'histograma':
        return [['Intervalo'].concat(fig.series.map(function (s) { return s.nombre; }))].concat(fig.limites.slice(0, -1).map(function (b, i) {
          return ['de ' + num(b) + ' a ' + num(fig.limites[i + 1])].concat(fig.series.map(function (s) { return num(s.conteos[i]); }));
        }));
      case 'boxplot':
        return [['Variable', 'Mín.', 'Q1', 'Mediana', 'Q3', 'Máx.', 'Atípicos']].concat(fig.cajas.map(function (c) {
          return [c.nombre, num(c.min), num(c.q1), num(c.mediana), num(c.q3), num(c.max), (c.atipicos || []).map(num).join(', ') || '—'];
        }));
      case 'dispersion':
        return [['Grupo', fig.eje_x || 'x', fig.eje_y || 'y']].concat([].concat.apply([], fig.grupos.map(function (g) {
          return g.puntos.map(function (p) { return [g.nombre, num(p[0]), num(p[1])]; });
        })));
      case 'matriz':
        return [[(fig.titulo_filas || 'Real') + ' \\ ' + (fig.titulo_columnas || 'Predicho')].concat(fig.etiquetas)].concat(fig.etiquetas.map(function (e, i) {
          return [e].concat(fig.valores[i].map(num));
        }));
    }
    return [];
  }
  function tablaDatos(fig) {
    var filas = filasTabla(fig);
    if (!filas.length) return null;
    var tabla = html('table', null, [
      html('thead', null, [html('tr', null, filas[0].map(function (c) { var th = html('th', null, [c]); th.setAttribute('scope', 'col'); return th; }))]),
      html('tbody', null, filas.slice(1).map(function (f) { return html('tr', null, f.map(function (c) { return html('td', null, [c]); })); }))
    ]);
    var caja = html('div', 'tabla-caja', [tabla]);
    caja.setAttribute('tabindex', '0');
    return html('details', 'g-datos', [html('summary', null, ['Ver los datos del gráfico']), caja]);
  }

  function crear(fig) {
    var dibujo;
    switch (fig.tipo) {
      case 'lineas': dibujo = lineas(fig, false); break;
      case 'roc': dibujo = lineas(fig, true); break;
      case 'barras': dibujo = barras(fig); break;
      case 'histograma': dibujo = histograma(fig); break;
      case 'boxplot': dibujo = boxplot(fig); break;
      case 'dispersion': dibujo = dispersion(fig); break;
      case 'matriz': dibujo = matriz(fig); break;
      default: return html('p', 'g-error', ['Tipo de gráfico desconocido: ' + fig.tipo]);
    }
    var lienzo = svg('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': (fig.titulo || 'Gráfico') + '. Los datos están en la tabla «Ver los datos del gráfico».', class: 'g-svg' }, [dibujo]);
    return html('figure', 'grafico', [
      fig.titulo ? html('figcaption', 'g-titulo', [fig.titulo]) : null,
      leyenda(fig),
      html('div', 'g-lienzo', [lienzo]),
      fig.nota ? html('p', 'tabla-nota', [fig.nota]) : null,
      tablaDatos(fig)
    ]);
  }

  var NOMBRE_TIPO = { lineas: 'Gráfico de líneas', roc: 'Curva ROC', barras: 'Gráfico de barras', histograma: 'Histograma', boxplot: 'Diagramas de caja (boxplot)', dispersion: 'Gráfico de dispersión', matriz: 'Matriz de confusión' };
  function describir(fig) {
    var filas = filasTabla(fig);
    var partes = [(NOMBRE_TIPO[fig.tipo] || 'Gráfico') + (fig.titulo ? ' «' + fig.titulo + '»' : '') + '.'];
    if (fig.tipo === 'roc') partes.push('La diagonal representa un modelo que decide al azar.');
    if (fig.referencia && fig.referencia_nombre) partes.push('Línea de referencia: ' + fig.referencia_nombre + '.');
    if (fig.linea && fig.linea_nombre) partes.push('Línea de referencia: ' + fig.linea_nombre + '.');
    if (fig.nota) partes.push(fig.nota);
    partes.push('Datos (' + filas[0].join(' | ') + '):');
    filas.slice(1).forEach(function (f) { partes.push('  ' + f.join(' | ')); });
    return partes.join('\n');
  }

  window.Graficos = { crear: crear, describir: describir };
})();
