"""Genera el sitio estático del curso en _site/ (solo biblioteca estándar de Python).

    python tools/build.py            # construye _site/
    python tools/build.py --salida X # en otra carpeta

Entradas:
    contenido/lecciones.json         bloques y lecciones (orden, títulos, temas LPIC-1)
    contenido/lecciones/<slug>.html  cuerpo de cada lección
    contenido/lpic1/temas.json       temas y pesos del examen LPIC-1
    contenido/lpic1/preguntas.json   banco de preguntas
    assets/, media/                  se copian tal cual
"""
import argparse
import html
import json
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REPO = "https://github.com/unfantasmaenelsistema/Curso-Linux"
WEB = "https://unfantasmaenelsistema.github.io/Curso-Linux/"
URL_BLOG = "https://www.unfantasmaenelsistema.com/"
URL_ACADEMIA = "https://www.ghostacademy.unfantasmaenelsistema.com/"
URL_TIENDA = "https://www.ghostore.unfantasmaenelsistema.com/"

CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
       "connect-src 'self'; font-src 'self'; base-uri 'self'; form-action 'none'; object-src 'none'")

ICONOS = {
    "terminal": '<path d="M4 17l6-6-6-6"/><path d="M12 19h8"/>',
    "engranaje": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    "disco": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
    "reloj": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
    "red": '<rect x="9" y="2" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="16" y="16" width="6" height="6" rx="1"/><path d="M5 16v-3h14v3M12 8v5"/>',
    "servidor": '<rect x="3" y="3" width="18" height="7" rx="1.5"/><rect x="3" y="14" width="18" height="7" rx="1.5"/><path d="M7 6.5h.01M7 17.5h.01"/>',
    "escudo": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
    "objetivo": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "examen": '<path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/>',
}


def icono(nombre, clase="icono"):
    return (f'<svg class="{clase}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONOS[nombre]}</svg>')


def e(texto):
    return html.escape(str(texto), quote=True)


def slug_id(texto, usados):
    import unicodedata
    base = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:60] or "seccion"
    cand, n = base, 2
    while cand in usados:
        cand, n = f"{base}-{n}", n + 1
    usados.add(cand)
    return cand


def texto_plano(fragmento):
    t = re.sub(r"</?(code|strong|em|a)[^>]*>", "", fragmento)  # en línea: sin espacios añadidos
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


class Sitio:
    def __init__(self, salida):
        self.salida = salida
        self.indice = json.loads((RAIZ / "contenido" / "lecciones.json").read_text(encoding="utf-8"))
        self.temas = json.loads((RAIZ / "contenido" / "lpic1" / "temas.json").read_text(encoding="utf-8"))
        self.nombre_tema = {t["id"]: t for t in self.temas["temas"]}
        self.lecciones = []
        for b in self.indice["bloques"]:
            for lec in b["lecciones"]:
                lec = dict(lec, bloque=b)
                lec["cuerpo"] = (RAIZ / "contenido" / "lecciones" / f"{lec['slug']}.html").read_text(encoding="utf-8")
                self.lecciones.append(lec)
        ruta_preg = RAIZ / "contenido" / "lpic1" / "preguntas.json"
        self.preguntas = json.loads(ruta_preg.read_text(encoding="utf-8")) if ruta_preg.exists() else {"preguntas": []}

    # --- piezas comunes ----------------------------------------------------------------------
    def lateral(self, raiz, activa=None):
        partes = ['<nav class="lateral-nav" aria-label="Temario">']
        for b in self.indice["bloques"]:
            abierto = " open" if activa and activa["bloque"]["id"] == b["id"] else ""
            partes.append(f'<details class="bloque-nav"{abierto}><summary>{icono(b["icono"])}'
                          f'<span data-es="{e(b["titulo"])}" data-en="{e(b["titulo_en"])}">{e(b["titulo"])}</span>'
                          f'<span class="cuenta">{len(b["lecciones"])}</span></summary><ol>')
            for lec in b["lecciones"]:
                actual = ' aria-current="page"' if activa and activa["slug"] == lec["slug"] else ""
                partes.append(f'<li><a href="{raiz}lecciones/{lec["slug"]}.html" data-slug="{lec["slug"]}"{actual}>'
                              f'{e(lec["titulo"])}</a></li>')
            partes.append("</ol></details>")
        partes.append(f'<a class="lateral-lpic" href="{raiz}lpic1/index.html">{icono("examen")}'
                      f'<span data-i18n="lpic_titulo">Preparación LPIC-1</span></a></nav>')
        return "".join(partes)

    def pagina(self, ruta, titulo, descripcion, cuerpo, raiz, activa=None, clase="", lateral=True):
        titulo_completo = f"{titulo} · Curso de Linux" if titulo != "Curso de Linux" else "Curso de Linux · Ghost Academy"
        url = WEB + ruta.replace("index.html", "")
        doc = f"""<!doctype html>
<html lang="es" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{e(titulo_completo)}</title>
<meta name="description" content="{e(descripcion)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(titulo_completo)}">
<meta property="og:description" content="{e(descripcion)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{WEB}assets/img/logo.png">
<meta name="theme-color" content="#0d1117">
<link rel="icon" type="image/png" href="{raiz}assets/img/favicon.png">
<link rel="stylesheet" href="{raiz}assets/css/curso.css">
<script src="{raiz}assets/js/tema.js"></script>
</head>
<body class="{clase}" data-raiz="{raiz}">
<a class="saltar" href="#contenido" data-i18n="saltar">Saltar al contenido</a>
<header class="barra">
  <button class="boton-icono menu-btn" type="button" aria-controls="lateral" aria-expanded="false" data-i18n-aria="menu" aria-label="Abrir el temario">
    <svg class="icono" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
  </button>
  <a class="marca" href="{raiz}index.html">
    <img src="{raiz}assets/img/logo.png" width="40" height="40" alt="Logo de Un Fantasma en el Sistema">
    <span><small>Ghost Academy</small><strong>Curso de Linux</strong></span>
  </a>
  <div class="buscador" role="search">
    <svg class="icono" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
    <input id="buscar" type="search" autocomplete="off" placeholder="Buscar en el curso…" data-i18n-placeholder="buscar" aria-label="Buscar en el curso" aria-controls="resultados" aria-expanded="false">
    <div id="resultados" class="resultados" role="listbox" hidden></div>
  </div>
  <nav class="barra-enlaces" aria-label="Secciones">
    <a href="{raiz}index.html#temario" data-i18n="temario">Temario</a>
    <a href="{raiz}lpic1/index.html" data-i18n="lpic_corto">LPIC-1</a>
  </nav>
  <button class="boton-texto" id="idioma" type="button" aria-label="Switch to English">EN</button>
  <button class="boton-icono" id="tema" type="button" data-i18n-aria="tema" aria-label="Cambiar entre tema claro y oscuro">
    <svg class="icono sol" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
    <svg class="icono luna" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
  </button>
</header>
<div class="marco{' sin-lateral' if not lateral else ''}">
{f'<aside id="lateral" class="lateral">{self.lateral(raiz, activa)}</aside><div class="velo" hidden></div>' if lateral else ''}
<main id="contenido" tabindex="-1">
{cuerpo}
</main>
</div>
<footer class="pie">
  <div class="pie-marca">
    <img src="{raiz}assets/img/logo.png" width="32" height="32" alt="">
    <p><strong>Curso de Linux</strong> · <span data-i18n="pie_parte">parte de</span> <a href="{URL_ACADEMIA}" target="_blank" rel="noopener">Ghost Academy</a>,
    <span data-i18n="pie_gratis">la academia gratuita de</span> <a href="{URL_BLOG}" target="_blank" rel="noopener">Un Fantasma en el Sistema</a>.</p>
  </div>
  <nav class="pie-enlaces" aria-label="Enlaces de la casa">
    <a href="{URL_BLOG}" target="_blank" rel="noopener">unfantasmaenelsistema.com</a>
    <a href="{URL_ACADEMIA}" target="_blank" rel="noopener">Ghost Academy</a>
    <a href="{URL_TIENDA}" target="_blank" rel="noopener">GhoStore</a>
    <a href="{REPO}" target="_blank" rel="noopener" data-i18n="codigo">Código (MIT)</a>
  </nav>
</footer>
<script src="{raiz}assets/js/curso.js" defer></script>
{'<script src="' + raiz + 'assets/js/lpic.js" defer></script>' if 'pagina-lpic' in clase else ''}
</body>
</html>
"""
        destino = self.salida / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(doc, encoding="utf-8")

    # --- lecciones ---------------------------------------------------------------------------
    def leccion(self, i, lec):
        usados = set()
        indice = []

        def poner_id(m):
            nivel, texto = m.group(1), m.group(2)
            ident = slug_id(html.unescape(re.sub(r"<[^>]+>", "", texto)), usados)
            if nivel == "2":
                indice.append((ident, re.sub(r"<[^>]+>", "", texto)))
            return f'<h{nivel} id="{ident}">{texto}</h{nivel}>'

        cuerpo = re.sub(r"<h([2-4])>(.*?)</h\1>", poner_id, lec["cuerpo"])
        # las tablas anchas y los bloques de código ya vienen envueltos; las imágenes llevan ruta ../media
        palabras = len(texto_plano(cuerpo).split())
        minutos = max(3, round(palabras / 180))
        n_codigo = cuerpo.count("<pre>")
        b = lec["bloque"]
        aviso = ""
        if b.get("aviso"):
            aviso = ('<div class="aviso aviso-rojo" role="note"><strong data-i18n="aviso_titulo">Solo en tu laboratorio.</strong> '
                     '<span data-i18n="aviso_texto">Estas técnicas se practican en máquinas virtuales propias o con autorización '
                     'por escrito. Usarlas contra equipos o redes ajenas es delito.</span></div>')
        chips = ""
        if lec["lpic"]:
            enlaces = "".join(
                f'<a class="chip" href="../lpic1/index.html#tema-{t}">{t} · <span data-es="{e(self.nombre_tema[t]["es"])}" '
                f'data-en="{e(self.nombre_tema[t]["en"])}">{e(self.nombre_tema[t]["es"])}</span></a>' for t in lec["lpic"])
            chips = f'<div class="chips"><span class="chips-titulo" data-i18n="practica_lpic">Practica con preguntas LPIC-1:</span>{enlaces}</div>'
        anterior = self.lecciones[i - 1] if i > 0 else None
        siguiente = self.lecciones[i + 1] if i + 1 < len(self.lecciones) else None
        pag = '<nav class="paginacion" aria-label="Lecciones vecinas">'
        if anterior:
            pag += (f'<a class="pag-ant" href="{anterior["slug"]}.html" rel="prev"><small data-i18n="anterior">Anterior</small>'
                    f'<span>{e(anterior["titulo"])}</span></a>')
        if siguiente:
            pag += (f'<a class="pag-sig" href="{siguiente["slug"]}.html" rel="next"><small data-i18n="siguiente">Siguiente</small>'
                    f'<span>{e(siguiente["titulo"])}</span></a>')
        pag += "</nav>"
        toc = ""
        if len(indice) >= 3:
            toc = ('<nav class="toc" aria-label="En esta lección"><p data-i18n="en_esta_leccion">En esta lección</p><ol>'
                   + "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in indice) + "</ol></nav>")
        articulo = f"""<div class="leccion-rejilla">
<article class="leccion" data-slug="{lec['slug']}">
  <nav class="migas" aria-label="Ruta"><a href="../index.html" data-i18n="inicio">Inicio</a><span aria-hidden="true">›</span>
    <a href="../index.html#bloque-{b['id']}" data-es="{e(b['titulo'])}" data-en="{e(b['titulo_en'])}">{e(b['titulo'])}</a></nav>
  <h1>{e(lec['titulo'])}</h1>
  <p class="meta"><span><span data-i18n="leccion">Lección</span> {i + 1} / {len(self.lecciones)}</span>
    <span>~{minutos} min</span><span>{n_codigo} <span data-i18n="{'bloque_codigo' if n_codigo == 1 else 'bloques_codigo'}">{'bloque de código' if n_codigo == 1 else 'bloques de código'}</span></span></p>
  <p class="aviso-idioma" data-solo-en hidden>This lesson is written in Spanish.</p>
  {aviso}
  {chips}
  <div class="cuerpo">
{cuerpo}
  </div>
  <div class="acciones-leccion">
    <button class="boton marcar" type="button" data-slug="{lec['slug']}" aria-pressed="false">
      <span data-i18n="marcar">Marcar como completada</span></button>
  </div>
  {pag}
</article>
{toc}
</div>"""
        resumen = texto_plano(re.sub(r"<pre>.*?</pre>", "", cuerpo, flags=re.S))[:155]
        self.pagina(f"lecciones/{lec['slug']}.html", lec["titulo"], resumen, articulo, "../", activa=lec, clase="pagina-leccion")
        return {"t": lec["titulo"], "b": b["titulo"], "u": f"lecciones/{lec['slug']}.html", "x": texto_plano(lec["cuerpo"])}

    # --- portada -----------------------------------------------------------------------------
    def portada(self):
        n_lec = len(self.lecciones)
        n_cod = sum(l["cuerpo"].count("<pre>") for l in self.lecciones)
        n_preg = len(self.preguntas["preguntas"])
        bloques = []
        for b in self.indice["bloques"]:
            lis = "".join(f'<li><a href="lecciones/{l["slug"]}.html" data-slug="{l["slug"]}">{e(l["titulo"])}</a></li>'
                          for l in b["lecciones"])
            extra = ' <span class="etiqueta-roja" data-i18n="solo_lab">solo laboratorio</span>' if b.get("aviso") else ""
            bloques.append(f"""<section class="tarjeta-bloque" id="bloque-{b['id']}">
  <h3>{icono(b['icono'])}<span data-es="{e(b['titulo'])}" data-en="{e(b['titulo_en'])}">{e(b['titulo'])}</span>{extra}</h3>
  <div class="progreso-bloque" data-bloque="{b['id']}" data-total="{len(b['lecciones'])}"><span></span></div>
  <ol>{lis}</ol>
</section>""")
        primera = self.lecciones[0]["slug"]
        cuerpo = f"""<section class="portada">
  <div class="portada-texto">
    <p class="antetitulo">Ghost Academy · <span data-i18n="gratis">gratis y en español</span></p>
    <h1 data-i18n="portada_titulo">Curso de Linux: de la terminal a la seguridad</h1>
    <p class="entradilla" data-i18n="portada_entradilla">Administración de sistemas Linux paso a paso: comandos, usuarios, procesos, discos, redes, servidores y bastionado, con ejemplos que puedes copiar y probar en tu máquina virtual. Y cuando quieras medirte, un banco de preguntas para preparar la certificación LPIC‑1.</p>
    <div class="portada-botones">
      <a class="boton boton-primario" href="lecciones/{primera}.html" id="empezar" data-i18n="empezar">Empezar por la primera lección</a>
      <a class="boton" href="lpic1/index.html" data-i18n="ir_lpic">Ponerme a prueba con LPIC-1</a>
    </div>
  </div>
  <div class="terminal-deco" aria-hidden="true">
    <div class="terminal-barra"><span></span><span></span><span></span></div>
<pre>alumno@ghost:~$ whoami
alumno
alumno@ghost:~$ ls curso-linux/
<b>terminal</b>  <b>sistema</b>  <b>discos</b>  <b>redes</b>
<b>servidores</b>  <b>seguridad</b>  <b>lpic1</b>
alumno@ghost:~$ <i>▌</i></pre>
  </div>
</section>
<ul class="cifras" aria-label="El curso en cifras">
  <li><strong>{n_lec}</strong><span data-i18n="cifra_lecciones">lecciones</span></li>
  <li><strong>{len(self.indice['bloques'])}</strong><span data-i18n="cifra_bloques">bloques</span></li>
  <li><strong>{n_cod}</strong><span data-i18n="cifra_codigo">ejemplos de terminal</span></li>
  <li><strong>{n_preg}</strong><span data-i18n="cifra_preguntas">preguntas LPIC-1</span></li>
</ul>
<p class="continuar" id="continuar" hidden><a class="boton" href="#"><span data-i18n="continuar">Continuar donde lo dejaste:</span> <strong></strong></a></p>
<h2 id="temario" data-i18n="temario">Temario</h2>
<p class="nota" data-i18n="temario_nota">Las lecciones se pueden leer en orden o sueltas. Las que marques como completadas se guardan en este navegador.</p>
<p class="aviso-idioma" data-solo-en hidden>Lessons and questions are written in Spanish; only the interface is translated.</p>
<div class="rejilla-bloques">
{''.join(bloques)}
</div>
<section class="banda-lpic">
  {icono('examen', 'icono icono-grande')}
  <div>
    <h2 data-i18n="lpic_titulo">Preparación LPIC-1</h2>
    <p data-i18n="lpic_banda">{n_preg} preguntas revisadas y clasificadas por los temas oficiales del examen: practica por tema, repite los 15 tests de siempre, repasa tus fallos o haz un simulacro cronometrado de 60 preguntas en 90 minutos.</p>
  </div>
  <a class="boton boton-primario" href="lpic1/index.html" data-i18n="abrir_lpic">Abrir la preparación</a>
</section>"""
        self.pagina("index.html", "Curso de Linux",
                    "Curso gratuito de administración de sistemas Linux en español: 53 lecciones prácticas y preparación de la certificación LPIC‑1.",
                    cuerpo, "", clase="pagina-portada")

    # --- LPIC-1 -------------------------------------------------------------------------------
    def lpic(self):
        cuerpo = """<section class="lpic" id="lpic">
  <h1 data-i18n="lpic_titulo">Preparación LPIC-1</h1>
  <p class="entradilla" data-i18n="lpic_entradilla">Preguntas tipo test para preparar los dos exámenes de la certificación LPIC‑1 (101-500 y 102-500). Tus resultados y fallos se guardan solo en este navegador.</p>
  <p class="aviso-idioma" data-solo-en hidden>Questions are written in Spanish.</p>
  <div id="lpic-app" class="lpic-app" aria-live="polite"><p class="cargando" data-i18n="cargando">Cargando preguntas…</p></div>
  <noscript><p class="aviso">Esta sección necesita JavaScript.</p></noscript>
</section>"""
        self.pagina("lpic1/index.html", "Preparación LPIC-1",
                    "Banco de preguntas LPIC-1 en español: tests, práctica por temas oficiales, repaso de fallos y simulacro cronometrado.",
                    cuerpo, "../", clase="pagina-lpic")
        datos = dict(self.preguntas)
        datos["temas"] = self.temas["temas"]
        datos["examenes"] = self.temas["examenes"]
        datos["lecciones"] = {t: [{"t": l["titulo"], "u": f"../lecciones/{l['slug']}.html"} for l in self.lecciones if t in l["lpic"]]
                              for t in self.nombre_tema}
        (self.salida / "lpic1" / "preguntas.json").write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")),
                                                               encoding="utf-8")

    def no_encontrada(self):
        cuerpo = """<section class="vacia"><h1 data-i18n="no_encontrada">Esta página no existe</h1>
<p data-i18n="no_encontrada_texto">Puede que la lección haya cambiado de nombre en la nueva versión del curso. Búscala arriba o vuelve al temario.</p>
<p><a class="boton boton-primario" href="/Curso-Linux/index.html#temario" data-i18n="volver_temario">Volver al temario</a></p></section>"""
        self.pagina("404.html", "Página no encontrada", "Página no encontrada", cuerpo, "/Curso-Linux/", lateral=False)

    def construir(self):
        if self.salida.exists():
            shutil.rmtree(self.salida)
        self.salida.mkdir(parents=True)
        shutil.copytree(RAIZ / "assets", self.salida / "assets")
        shutil.copytree(RAIZ / "media", self.salida / "media")
        buscar = [self.leccion(i, l) for i, l in enumerate(self.lecciones)]
        self.portada()
        self.lpic()
        self.no_encontrada()
        (self.salida / "buscar.json").write_text(json.dumps(buscar, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        (self.salida / ".nojekyll").write_text("", encoding="utf-8")
        mapa = [WEB, WEB + "lpic1/"] + [f"{WEB}lecciones/{l['slug']}.html" for l in self.lecciones]
        (self.salida / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{u}</loc></url>\n" for u in mapa) + "</urlset>\n", encoding="utf-8")
        (self.salida / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {WEB}sitemap.xml\n", encoding="utf-8")
        print(f"{len(self.lecciones)} lecciones, {len(self.preguntas['preguntas'])} preguntas -> {self.salida}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=str(RAIZ / "_site"))
    Sitio(Path(ap.parse_args().salida)).construir()
