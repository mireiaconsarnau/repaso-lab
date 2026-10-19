# Repaso Lab · Machine Learning

**[Abrir Repaso Lab](https://mireiaconsarnau.github.io/repaso-lab/)**

Web para poner a prueba tus conocimientos del [curso de Machine Learning](https://mireiaconsarnau.github.io/machine_learning/) de Mireia Consarnau, organizada por las unidades del curso.

- **Repaso**: preguntas tipo test y abiertas de cada unidad, en cuatro niveles (Primeros pasos, Aplica, Comprende y Reto), con la solución explicada y el enlace a la lección y a su infografía. No hace falta cuenta.
- **Practica con casos**: escribes tu respuesta a un caso práctico y Claude te dice qué está bien, qué está mal y qué te falta.
- **Resuelve tus dudas**: un tutor con IA que responde dudas del curso a partir de los apuntes, con un ejemplo, y te dice dónde repasarlo.

La práctica con casos y el tutor usan Claude, así que solo funcionan al abrir la web [en Claude](https://claude.ai/artifact/YA1YZLvVcurULMRZGnsK5c), con una cuenta (sirve la gratuita). Nunca se pone nota.

## Para el profesorado

- Las preguntas están en [`web/datos/preguntas.json`](web/datos/preguntas.json) y la configuración (unidades, niveles, lecciones), en [`web/datos/config.json`](web/datos/config.json).
- Antes de publicar un cambio: `python -I tools/validar_banco.py`. Vista local: `python -I tools/servir_local.py` y abre http://localhost:8000.
- Cada push a `main` publica la web en GitHub Pages (`.github/workflows/pages.yml`).
- Todo el contexto del proyecto, para quien lo mantenga, está en [`CLAUDE.md`](CLAUDE.md).

## Licencia

[CC BY-NC-SA 4.0](LICENSE.md), «Repaso Lab: Machine Learning», de Mireia Consarnau. Las tipografías IBM Plex tienen su propia licencia (SIL OFL 1.1).
