"""Vista local de la web de repaso, igual que cuando se publica (artefacto de Claude o GitHub Pages).

web/index.html es un fragmento: al publicarlo se le añade el esqueleto del documento (doctype, charset
y viewport). Este servidor hace lo mismo, con el esqueleto de tools/construir_web.py, y sirve el resto
de archivos de web/ en UTF-8.

Uso (desde la raíz del repositorio): python -I tools/servir_local.py [puerto]
Después abre http://localhost:8000 (o el puerto indicado).
"""
import functools
import http.server
import importlib.util
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / 'web'
PUERTO = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

_spec = importlib.util.spec_from_file_location('construir_web', Path(__file__).resolve().parent / 'construir_web.py')
construir_web = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(construir_web)


class Manejador(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.js': 'text/javascript; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
    }

    def do_GET(self):
        ruta = self.path.split('?', 1)[0].split('#', 1)[0]
        if ruta in ('/', '/index.html'):
            cuerpo = construir_web.documento().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(cuerpo)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(cuerpo)
            return
        super().do_GET()


if __name__ == '__main__':
    servidor = http.server.ThreadingHTTPServer(('127.0.0.1', PUERTO), functools.partial(Manejador, directory=str(WEB)))
    print(f'Web de repaso en http://localhost:{PUERTO} (Ctrl+C para parar)')
    servidor.serve_forever()
