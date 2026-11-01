// Curso de Linux · interacción común: menú, buscador, tema, idioma, copiar código y progreso.
(function () {
  'use strict';

  var RAIZ = document.body.getAttribute('data-raiz') || '';

  // --- almacenamiento seguro ---------------------------------------------------------------
  function leer(clave, defecto) {
    try { var v = localStorage.getItem(clave); return v === null ? defecto : JSON.parse(v); } catch (e) { return defecto; }
  }
  function guardar(clave, valor) {
    try { localStorage.setItem(clave, JSON.stringify(valor)); } catch (e) { /* modo privado */ }
  }
  window.CursoAlmacen = { leer: leer, guardar: guardar };

  // --- textos de la interfaz (ES/EN) -------------------------------------------------------
  var TEXTOS = {
    es: {
      saltar: 'Saltar al contenido', menu: 'Abrir el temario', buscar: 'Buscar en el curso…', temario: 'Temario',
      lpic_corto: 'LPIC-1', tema: 'Cambiar entre tema claro y oscuro', pie_parte: 'parte de', pie_gratis: 'la academia gratuita de',
      codigo: 'Código (MIT)', inicio: 'Inicio', leccion: 'Lección', bloques_codigo: 'bloques de código', bloque_codigo: 'bloque de código',
      aviso_titulo: 'Solo en tu laboratorio.',
      aviso_texto: 'Estas técnicas se practican en máquinas virtuales propias o con autorización por escrito. Usarlas contra equipos o redes ajenas es delito.',
      practica_lpic: 'Practica con preguntas LPIC-1:', marcar: 'Marcar como completada', marcada: 'Completada',
      anterior: 'Anterior', siguiente: 'Siguiente', en_esta_leccion: 'En esta lección', gratis: 'gratis y en español',
      portada_titulo: 'Curso de Linux: de la terminal a la seguridad',
      portada_entradilla: 'Administración de sistemas Linux paso a paso: comandos, usuarios, procesos, discos, redes, servidores y bastionado, con ejemplos que puedes copiar y probar en tu máquina virtual. Y cuando quieras medirte, un banco de preguntas para preparar la certificación LPIC‑1.',
      empezar: 'Empezar por la primera lección', ir_lpic: 'Ponerme a prueba con LPIC-1', cifra_lecciones: 'lecciones',
      cifra_bloques: 'bloques', cifra_codigo: 'ejemplos de terminal', cifra_preguntas: 'preguntas LPIC-1',
      continuar: 'Continuar donde lo dejaste:',
      temario_nota: 'Las lecciones se pueden leer en orden o sueltas. Las que marques como completadas se guardan en este navegador.',
      solo_lab: 'solo laboratorio', lpic_titulo: 'Preparación LPIC-1',
      lpic_banda: 'Preguntas revisadas y clasificadas por los temas oficiales del examen: practica por tema, repite los 15 tests de siempre, repasa tus fallos o haz un simulacro cronometrado de 60 preguntas en 90 minutos.',
      abrir_lpic: 'Abrir la preparación',
      lpic_entradilla: 'Preguntas tipo test para preparar los dos exámenes de la certificación LPIC‑1 (101-500 y 102-500). Tus resultados y fallos se guardan solo en este navegador.',
      cargando: 'Cargando preguntas…', no_encontrada: 'Esta página no existe',
      no_encontrada_texto: 'Puede que la lección haya cambiado de nombre en la nueva versión del curso. Búscala arriba o vuelve al temario.',
      volver_temario: 'Volver al temario', copiar: 'Copiar', copiado: 'Copiado', sin_resultados: 'Sin resultados para',
      cambiar_idioma: 'Switch to English'
    },
    en: {
      saltar: 'Skip to content', menu: 'Open the syllabus', buscar: 'Search the course…', temario: 'Syllabus',
      lpic_corto: 'LPIC-1', tema: 'Toggle light and dark theme', pie_parte: 'part of', pie_gratis: 'the free academy by',
      codigo: 'Source (MIT)', inicio: 'Home', leccion: 'Lesson', bloques_codigo: 'code blocks', bloque_codigo: 'code block',
      aviso_titulo: 'Lab use only.',
      aviso_texto: 'Practise these techniques on your own virtual machines or with written permission. Using them against other people’s systems or networks is a crime.',
      practica_lpic: 'Practise with LPIC-1 questions:', marcar: 'Mark as completed', marcada: 'Completed',
      anterior: 'Previous', siguiente: 'Next', en_esta_leccion: 'In this lesson', gratis: 'free, in Spanish',
      portada_titulo: 'Linux course: from the terminal to security',
      portada_entradilla: 'Step-by-step Linux system administration: commands, users, processes, disks, networking, servers and hardening, with examples you can copy and try in your virtual machine. And when you want to test yourself, a question bank to prepare the LPIC‑1 certification.',
      empezar: 'Start with the first lesson', ir_lpic: 'Test myself with LPIC-1', cifra_lecciones: 'lessons',
      cifra_bloques: 'sections', cifra_codigo: 'terminal examples', cifra_preguntas: 'LPIC-1 questions',
      continuar: 'Continue where you left off:',
      temario_nota: 'Read the lessons in order or pick any of them. The ones you mark as completed are saved in this browser.',
      solo_lab: 'lab only', lpic_titulo: 'LPIC-1 preparation',
      lpic_banda: 'Reviewed questions, sorted by the official exam topics: practise by topic, retake the 15 classic tests, review your mistakes or sit a timed 60-question, 90-minute mock exam.',
      abrir_lpic: 'Open the preparation',
      lpic_entradilla: 'Multiple-choice questions to prepare both LPIC‑1 exams (101-500 and 102-500). Your results and mistakes are stored only in this browser.',
      cargando: 'Loading questions…', no_encontrada: 'This page does not exist',
      no_encontrada_texto: 'The lesson may have been renamed in the new version of the course. Search for it above or go back to the syllabus.',
      volver_temario: 'Back to the syllabus', copiar: 'Copy', copiado: 'Copied', sin_resultados: 'No results for',
      cambiar_idioma: 'Cambiar a español'
    }
  };
  var idioma = leer('cl_idioma', 'es') === 'en' ? 'en' : 'es';

  function t(clave) { return (TEXTOS[idioma] && TEXTOS[idioma][clave]) || TEXTOS.es[clave] || clave; }

  function aplicarIdioma() {
    document.documentElement.setAttribute('lang', idioma);
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var k = el.getAttribute('data-i18n');
      if (!el.hasAttribute('data-i18n-orig')) el.setAttribute('data-i18n-orig', el.textContent);
      el.textContent = idioma === 'es' ? (TEXTOS.es[k] ? el.getAttribute('data-i18n-orig') : el.textContent) : t(k);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) { el.placeholder = t(el.getAttribute('data-i18n-placeholder')); });
    document.querySelectorAll('[data-i18n-aria]').forEach(function (el) { el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria'))); });
    document.querySelectorAll('[data-es][data-en]').forEach(function (el) { el.textContent = el.getAttribute('data-' + idioma); });
    document.querySelectorAll('[data-solo-en]').forEach(function (el) { el.hidden = idioma !== 'en'; });
    var b = document.getElementById('idioma');
    if (b) { b.textContent = idioma === 'es' ? 'EN' : 'ES'; b.setAttribute('aria-label', t('cambiar_idioma')); }
    document.querySelectorAll('.copiar:not(.hecho)').forEach(function (el) { el.textContent = t('copiar'); });
    actualizarMarcar();
    document.dispatchEvent(new CustomEvent('curso:idioma', { detail: idioma }));
  }
  window.CursoIdioma = { actual: function () { return idioma; }, t: t, textos: TEXTOS };

  var botonIdioma = document.getElementById('idioma');
  if (botonIdioma) botonIdioma.addEventListener('click', function () {
    idioma = idioma === 'es' ? 'en' : 'es';
    guardar('cl_idioma', idioma);
    aplicarIdioma();
  });

  // --- tema ---------------------------------------------------------------------------------
  var botonTema = document.getElementById('tema');
  if (botonTema) botonTema.addEventListener('click', function () {
    var nuevo = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nuevo);
    try { localStorage.setItem('cl_tema', nuevo); } catch (e) { /* sin almacenamiento */ }
  });

  // --- menú lateral en móvil ----------------------------------------------------------------
  var lateral = document.getElementById('lateral');
  var velo = document.querySelector('.velo');
  var botonMenu = document.querySelector('.menu-btn');
  function menu(abrir) {
    if (!lateral) return;
    lateral.classList.toggle('abierto', abrir);
    if (velo) velo.hidden = !abrir;
    if (botonMenu) botonMenu.setAttribute('aria-expanded', abrir ? 'true' : 'false');
  }
  if (botonMenu) botonMenu.addEventListener('click', function () { menu(!lateral.classList.contains('abierto')); });
  if (velo) velo.addEventListener('click', function () { menu(false); });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') menu(false); });
  var actual = lateral && lateral.querySelector('[aria-current="page"]');
  if (actual) actual.scrollIntoView({ block: 'center' });
  if (lateral) lateral.scrollTop = Math.max(0, (actual ? actual.offsetTop : 0) - lateral.clientHeight / 2);

  // --- progreso (lecciones vistas) ----------------------------------------------------------
  var vistas = leer('cl_vistas', []);
  if (!Array.isArray(vistas)) vistas = [];
  function pintarProgreso() {
    document.querySelectorAll('a[data-slug]').forEach(function (a) {
      a.classList.toggle('vista', vistas.indexOf(a.getAttribute('data-slug')) !== -1);
    });
    document.querySelectorAll('.progreso-bloque').forEach(function (p) {
      var tarjeta = p.parentElement;
      var total = +p.getAttribute('data-total');
      var hechas = tarjeta.querySelectorAll('a.vista').length;
      p.firstElementChild.style.width = (total ? (100 * hechas / total) : 0) + '%';
      p.setAttribute('title', hechas + ' / ' + total);
    });
  }
  var botonMarcar = document.querySelector('.marcar');
  function actualizarMarcar() {
    if (!botonMarcar) return;
    var hecha = vistas.indexOf(botonMarcar.getAttribute('data-slug')) !== -1;
    botonMarcar.setAttribute('aria-pressed', hecha ? 'true' : 'false');
    botonMarcar.firstElementChild.textContent = hecha ? t('marcada') : t('marcar');
  }
  if (botonMarcar) botonMarcar.addEventListener('click', function () {
    var slug = botonMarcar.getAttribute('data-slug');
    var i = vistas.indexOf(slug);
    if (i === -1) vistas.push(slug); else vistas.splice(i, 1);
    guardar('cl_vistas', vistas);
    actualizarMarcar();
    pintarProgreso();
  });
  var articulo = document.querySelector('.leccion[data-slug]');
  if (articulo) {
    var h1 = articulo.querySelector('h1');
    guardar('cl_ultima', { slug: articulo.getAttribute('data-slug'), titulo: h1 ? h1.textContent : '' });
  }
  var continuar = document.getElementById('continuar');
  var ultima = leer('cl_ultima', null);
  if (continuar && ultima && ultima.slug && /^[a-z0-9-]+$/.test(ultima.slug)) {
    var enlace = continuar.querySelector('a');
    enlace.href = RAIZ + 'lecciones/' + ultima.slug + '.html';
    enlace.querySelector('strong').textContent = ultima.titulo || ultima.slug;
    continuar.hidden = false;
  }
  pintarProgreso();

  // --- botones de copiar en los bloques de código -------------------------------------------
  document.querySelectorAll('.cuerpo pre').forEach(function (pre) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'copiar';
    b.textContent = t('copiar');
    b.addEventListener('click', function () {
      var texto = pre.querySelector('code') ? pre.querySelector('code').innerText : pre.innerText;
      var hecho = function () {
        b.textContent = t('copiado');
        b.classList.add('hecho');
        setTimeout(function () { b.textContent = t('copiar'); b.classList.remove('hecho'); }, 1600);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(texto).then(hecho, function () { copiarViejo(texto); hecho(); });
      } else { copiarViejo(texto); hecho(); }
    });
    pre.appendChild(b);
  });
  function copiarViejo(texto) {
    var ta = document.createElement('textarea');
    ta.value = texto;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) { /* nada */ }
    document.body.removeChild(ta);
  }

  // --- ampliar capturas ---------------------------------------------------------------------
  document.querySelectorAll('.cuerpo figure img').forEach(function (img) {
    img.addEventListener('click', function () {
      var visor = document.createElement('div');
      visor.className = 'visor';
      visor.setAttribute('role', 'dialog');
      visor.setAttribute('aria-label', img.alt);
      var grande = document.createElement('img');
      grande.src = img.currentSrc || img.src;
      grande.alt = img.alt;
      visor.appendChild(grande);
      var cerrar = function () { visor.remove(); document.removeEventListener('keydown', tecla); };
      var tecla = function (ev) { if (ev.key === 'Escape') cerrar(); };
      visor.addEventListener('click', cerrar);
      document.addEventListener('keydown', tecla);
      document.body.appendChild(visor);
    });
  });

  // --- índice lateral: resaltar la sección visible ------------------------------------------
  var tocEnlaces = document.querySelectorAll('.toc a');
  if (tocEnlaces.length && 'IntersectionObserver' in window) {
    var porId = {};
    tocEnlaces.forEach(function (a) { porId[a.getAttribute('href').slice(1)] = a; });
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting && porId[en.target.id]) {
          tocEnlaces.forEach(function (a) { a.classList.remove('activo'); });
          porId[en.target.id].classList.add('activo');
        }
      });
    }, { rootMargin: '-70px 0px -70% 0px' });
    Object.keys(porId).forEach(function (id) { var h = document.getElementById(id); if (h) obs.observe(h); });
  }

  // --- buscador -----------------------------------------------------------------------------
  var entrada = document.getElementById('buscar');
  var caja = document.getElementById('resultados');
  var indice = null, cargando = null, seleccion = -1;

  function normalizar(s) {
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }
  function cargarIndice() {
    if (indice || cargando) return cargando;
    cargando = fetch(RAIZ + 'buscar.json').then(function (r) { return r.json(); }).then(function (datos) {
      indice = datos.map(function (d) { d.nt = normalizar(d.t); d.nx = normalizar(d.x); return d; });
      return indice;
    }).catch(function () { indice = []; });
    return cargando;
  }
  function escapar(s) {
    return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }
  function resaltar(texto, terminos) {
    var html = escapar(texto);
    terminos.forEach(function (term) {
      if (term.length < 2) return;
      var re = new RegExp('(' + term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig');
      html = html.replace(re, '<mark>$1</mark>');
    });
    return html;
  }
  function buscar() {
    var q = entrada.value.trim();
    if (q.length < 2) { cerrarResultados(); return; }
    cargarIndice().then(function () {
      var terms = normalizar(q).split(/\s+/).filter(Boolean);
      var res = [];
      indice.forEach(function (d) {
        var punt = 0;
        for (var i = 0; i < terms.length; i++) {
          var enT = d.nt.indexOf(terms[i]) !== -1;
          var pos = d.nx.indexOf(terms[i]);
          if (!enT && pos === -1) return;
          punt += enT ? 10 : 1;
          if (pos !== -1) punt += Math.min(5, d.nx.split(terms[i]).length - 1);
        }
        var p0 = d.nx.indexOf(terms[0]);
        var ini = Math.max(0, p0 - 50);
        var frag = p0 === -1 ? d.x.slice(0, 110) : (ini > 0 ? '…' : '') + d.x.slice(ini, ini + 130) + '…';
        res.push({ d: d, p: punt, f: frag });
      });
      res.sort(function (a, b) { return b.p - a.p; });
      res = res.slice(0, 8);
      caja.innerHTML = '';
      if (!res.length) {
        var vacio = document.createElement('p');
        vacio.className = 'vacio';
        vacio.textContent = t('sin_resultados') + ' «' + q + '»';
        caja.appendChild(vacio);
      }
      var crudos = q.split(/\s+/);
      res.forEach(function (r, i) {
        var a = document.createElement('a');
        a.href = RAIZ + r.d.u;
        a.id = 'res-' + i;
        a.setAttribute('role', 'option');
        a.innerHTML = '<small>' + escapar(r.d.b) + '</small><strong>' + resaltar(r.d.t, crudos) + '</strong><span>' + resaltar(r.f, crudos) + '</span>';
        caja.appendChild(a);
      });
      seleccion = -1;
      caja.hidden = false;
      entrada.setAttribute('aria-expanded', 'true');
    });
  }
  function cerrarResultados() {
    if (!caja) return;
    caja.hidden = true;
    entrada.setAttribute('aria-expanded', 'false');
  }
  if (entrada && caja) {
    var temporizador;
    entrada.addEventListener('focus', cargarIndice);
    entrada.addEventListener('input', function () { clearTimeout(temporizador); temporizador = setTimeout(buscar, 120); });
    entrada.addEventListener('keydown', function (ev) {
      var opciones = caja.querySelectorAll('a');
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
        if (!opciones.length) return;
        ev.preventDefault();
        seleccion = (seleccion + (ev.key === 'ArrowDown' ? 1 : -1) + opciones.length) % opciones.length;
        opciones.forEach(function (o, i) { o.setAttribute('aria-selected', i === seleccion ? 'true' : 'false'); });
        entrada.setAttribute('aria-activedescendant', opciones[seleccion].id);
      } else if (ev.key === 'Enter' && opciones.length) {
        ev.preventDefault();
        window.location.href = opciones[Math.max(0, seleccion)].href;
      } else if (ev.key === 'Escape') {
        cerrarResultados();
      }
    });
    document.addEventListener('click', function (ev) {
      if (!ev.target.closest('.buscador')) cerrarResultados();
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === '/' && !/input|textarea|select/i.test(document.activeElement.tagName)) {
        ev.preventDefault();
        entrada.focus();
      }
    });
  }

  aplicarIdioma();
})();
