"""Comprueba el sitio generado y el banco de preguntas (lo ejecuta el workflow antes de publicar).

    python tools/comprobar.py [carpeta_del_sitio]   # por defecto _site/
"""
import html.parser
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

RAIZ = Path(__file__).resolve().parent.parent
errores = []


def error(msg):
    errores.append(msg)


class Enlaces(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.h1, self.scripts_inline, self.estilos = [], set(), 0, 0, 0
        self._en_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        if "style" in a:
            self.estilos += 1
        if tag == "script":
            if "src" in a:
                self.refs.append(a["src"])
            else:
                self._en_script = True
        for attr in ("href", "src"):
            if attr in a and tag != "script":
                self.refs.append(a[attr])

    def handle_endtag(self, tag):
        if tag == "script":
            self._en_script = False

    def handle_data(self, data):
        if self._en_script and data.strip():
            self.scripts_inline += 1


def comprobar_sitio(sitio):
    paginas = sorted(sitio.rglob("*.html"))
    if len(paginas) < 50:
        error(f"Solo hay {len(paginas)} páginas en {sitio}")
    ids_por_pagina = {}
    analisis = {}
    for p in paginas:
        a = Enlaces()
        a.feed(p.read_text(encoding="utf-8"))
        analisis[p] = a
        ids_por_pagina[p.resolve()] = a.ids
    for p, a in analisis.items():
        rel = p.relative_to(sitio)
        if a.h1 != 1 and p.name != "404.html":
            error(f"{rel}: {a.h1} encabezados h1")
        if a.scripts_inline:
            error(f"{rel}: script en línea (lo bloquea la CSP)")
        if a.estilos:
            error(f"{rel}: atributo style (lo bloquea la CSP)")
        for ref in a.refs:
            u = urlparse(ref)
            if u.scheme in ("http", "https", "mailto") or ref.startswith("data:"):
                continue
            if p.name == "404.html":
                continue  # usa rutas absolutas /Curso-Linux/
            ruta = unquote(u.path)
            destino = (p.parent / ruta).resolve() if ruta else p.resolve()
            if ruta.endswith("/"):
                destino = destino / "index.html"
            if not destino.exists():
                error(f"{rel}: enlace roto → {ref}")
            elif u.fragment and destino.suffix == ".html" and u.fragment not in ids_por_pagina.get(destino, set()):
                if not re.match(r"^(tema-\d{3}|test-\d+|fallos|progreso|simulacro-\d{3})$", u.fragment):
                    error(f"{rel}: ancla inexistente → {ref}")
    for nombre in ("buscar.json", "lpic1/preguntas.json", "sitemap.xml", ".nojekyll"):
        if not (sitio / nombre).exists():
            error(f"Falta {nombre}")


def comprobar_preguntas():
    datos = json.loads((RAIZ / "contenido" / "lpic1" / "preguntas.json").read_text(encoding="utf-8"))
    temas = {t["id"] for t in json.loads((RAIZ / "contenido" / "lpic1" / "temas.json").read_text(encoding="utf-8"))["temas"]}
    ids = set()
    for q in datos["preguntas"]:
        pid = q["id"]
        if pid in ids:
            error(f"Pregunta repetida: {pid}")
        ids.add(pid)
        corr = q["correcta"] if isinstance(q["correcta"], list) else [q["correcta"]]
        if not corr or any(not isinstance(c, int) or c < 0 or c >= len(q["opciones"]) for c in corr):
            error(f"{pid}: respuesta correcta fuera de rango")
        if len(set(q["opciones"])) != len(q["opciones"]):
            error(f"{pid}: opciones repetidas")
        if len(q["opciones"]) < 2:
            error(f"{pid}: menos de dos opciones")
        if q["tema"] not in temas:
            error(f"{pid}: tema desconocido {q['tema']}")
        if q.get("nivel") not in ("inicial", "lpic1", "ampliacion"):
            error(f"{pid}: nivel desconocido")
        if re.search(r"\*\*|\[cite", q["texto"] + q["explicacion"]):
            error(f"{pid}: restos de markdown o citas")
    for t in datos["tests"]:
        for pid in t["preguntas"]:
            if pid not in ids:
                error(f"Test {t['n']}: pregunta inexistente {pid}")
    return len(datos["preguntas"])


def main():
    sitio = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "_site"
    n = comprobar_preguntas()
    comprobar_sitio(sitio)
    if errores:
        print("\n".join(errores))
        print(f"{len(errores)} errores")
        sys.exit(1)
    print(f"OK: {len(list(sitio.rglob('*.html')))} páginas y {n} preguntas sin errores")


if __name__ == "__main__":
    main()
