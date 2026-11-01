// Preparación LPIC-1: simulacro cronometrado, práctica por tema, tests originales y repaso de fallos.
(function () {
  'use strict';

  var app = document.getElementById('lpic-app');
  if (!app) return;

  var almacen = window.CursoAlmacen || { leer: function (k, d) { return d; }, guardar: function () {} };
  var idioma = function () { return window.CursoIdioma ? window.CursoIdioma.actual() : 'es'; };

  var T = {
    es: {
      pest_simulacro: 'Simulacro de examen', pest_temas: 'Practicar por tema', pest_tests: 'Tests originales',
      pest_fallos: 'Mis fallos', pest_progreso: 'Mi progreso',
      sim_intro: 'Como el examen real: 60 preguntas repartidas según el peso oficial de cada tema y 90 minutos. No verás si aciertas hasta el final.',
      sim_empezar: 'Empezar', preguntas: 'preguntas', minutos: 'minutos',
      temas_intro: 'Elige un tema del examen. Verás si aciertas al momento, con la explicación y la lección del curso que lo trata.',
      tests_intro: 'Los 15 tests del repositorio original, revisados. Los marcados como «nivel inicial» son de Linux Essentials y los de «ampliación» van más allá de LPIC-1.',
      fallos_intro: 'Aquí se acumulan las preguntas que fallas en cualquier modo. Cuando aciertes una aquí, sale de la lista.',
      fallos_vacio: 'No tienes fallos guardados. ¡Buen trabajo!', fallos_practicar: 'Repasar mis fallos', fallos_borrar: 'Vaciar la lista',
      cuantas: 'Número de preguntas', todas: 'Todas', incluir_ampliacion: 'Incluir preguntas de ampliación',
      nivel_inicial: 'nivel inicial', nivel_ampliacion: 'ampliación', mejor: 'Mejor nota', sin_hacer: 'Sin hacer',
      acierto: 'acierto', respondidas: 'respondidas', pregunta: 'Pregunta', de: 'de',
      comprobar: 'Comprobar', siguiente: 'Siguiente', anterior: 'Anterior', terminar: 'Terminar', terminar_examen: 'Terminar el examen',
      salir: 'Salir', confirmar_salir: '¿Salir? Se perderá el progreso de esta prueba.',
      confirmar_terminar: 'Quedan preguntas sin responder. ¿Terminar de todos modos?',
      correcto: '¡Correcto!', incorrecto: 'Incorrecto.', la_correcta: 'Respuesta correcta:', las_correctas: 'Respuestas correctas:',
      elige_varias: 'Elige {n} respuestas.', repasa: 'Repasa en el curso:', revisada: 'Corregida en la revisión:',
      resultado: 'Resultado', aciertos: 'aciertos', apto: 'Superarías el corte orientativo (65 %)', no_apto: 'Por debajo del corte orientativo (65 %)',
      nota_corte: 'El examen real se puntúa de 200 a 800 y se aprueba con 500; el 65 % es solo una referencia.',
      por_tema: 'Por tema', tema: 'Tema', revisar_fallos: 'Preguntas falladas', volver: 'Volver al inicio', repetir: 'Repetir',
      sin_responder: 'Sin responder', tu_respuesta: 'Tu respuesta:', tiempo_agotado: 'Se acabó el tiempo.',
      prog_respondidas: 'preguntas respondidas', prog_acierto: 'de acierto global', prog_examenes: 'simulacros hechos', prog_fallos: 'fallos pendientes',
      historial: 'Últimos simulacros', fecha: 'Fecha', examen: 'Examen', nota: 'Nota', nada_aun: 'Aún no has hecho ningún simulacro.',
      borrar_todo: 'Borrar mi progreso', confirmar_borrar: '¿Borrar todas tus estadísticas, fallos y simulacros guardados en este navegador?',
      error_carga: 'No se pudieron cargar las preguntas.', peso: 'peso'
    },
    en: {
      pest_simulacro: 'Mock exam', pest_temas: 'Practise by topic', pest_tests: 'Original tests',
      pest_fallos: 'My mistakes', pest_progreso: 'My progress',
      sim_intro: 'Like the real exam: 60 questions weighted by the official topic weights, and 90 minutes. You will only see your answers at the end.',
      sim_empezar: 'Start', preguntas: 'questions', minutos: 'minutes',
      temas_intro: 'Pick an exam topic. You get instant feedback, with the explanation and the course lesson that covers it.',
      tests_intro: 'The 15 tests from the original repository, reviewed. “Beginner” ones are Linux Essentials level; “extension” ones go beyond LPIC-1.',
      fallos_intro: 'Questions you get wrong in any mode are collected here. Answer one correctly here and it leaves the list.',
      fallos_vacio: 'No saved mistakes. Well done!', fallos_practicar: 'Review my mistakes', fallos_borrar: 'Clear the list',
      cuantas: 'Number of questions', todas: 'All', incluir_ampliacion: 'Include extension questions',
      nivel_inicial: 'beginner', nivel_ampliacion: 'extension', mejor: 'Best score', sin_hacer: 'Not taken',
      acierto: 'correct', respondidas: 'answered', pregunta: 'Question', de: 'of',
      comprobar: 'Check', siguiente: 'Next', anterior: 'Previous', terminar: 'Finish', terminar_examen: 'Finish the exam',
      salir: 'Exit', confirmar_salir: 'Exit? Progress on this test will be lost.',
      confirmar_terminar: 'Some questions are unanswered. Finish anyway?',
      correcto: 'Correct!', incorrecto: 'Incorrect.', la_correcta: 'Correct answer:', las_correctas: 'Correct answers:',
      elige_varias: 'Choose {n} answers.', repasa: 'Review in the course:', revisada: 'Fixed during the review:',
      resultado: 'Result', aciertos: 'correct', apto: 'Above the reference cut-off (65%)', no_apto: 'Below the reference cut-off (65%)',
      nota_corte: 'The real exam is scored from 200 to 800 and the pass mark is 500; 65% is only a reference.',
      por_tema: 'By topic', tema: 'Topic', revisar_fallos: 'Questions you missed', volver: 'Back to start', repetir: 'Try again',
      sin_responder: 'Unanswered', tu_respuesta: 'Your answer:', tiempo_agotado: 'Time is up.',
      prog_respondidas: 'questions answered', prog_acierto: 'overall accuracy', prog_examenes: 'mock exams taken', prog_fallos: 'pending mistakes',
      historial: 'Latest mock exams', fecha: 'Date', examen: 'Exam', nota: 'Score', nada_aun: 'You have not taken any mock exam yet.',
      borrar_todo: 'Delete my progress', confirmar_borrar: 'Delete all your stats, mistakes and mock exams stored in this browser?',
      error_carga: 'The questions could not be loaded.', peso: 'weight'
    }
  };
  function t(k, vars) {
    var s = (T[idioma()] && T[idioma()][k]) || T.es[k] || k;
    if (vars) Object.keys(vars).forEach(function (v) { s = s.replace('{' + v + '}', vars[v]); });
    return s;
  }

  // --- estado guardado --------------------------------------------------------------------
  var CLAVE = 'cl_lpic';
  function estado() {
    var e = almacen.leer(CLAVE, null);
    if (!e || typeof e !== 'object') e = {};
    e.stats = e.stats && typeof e.stats === 'object' ? e.stats : {};
    e.fallos = Array.isArray(e.fallos) ? e.fallos : [];
    e.examenes = Array.isArray(e.examenes) ? e.examenes : [];
    e.tests = e.tests && typeof e.tests === 'object' ? e.tests : {};
    return e;
  }
  function guardarEstado(e) { almacen.guardar(CLAVE, e); }

  // --- datos ---------------------------------------------------------------------------------
  var D = null, porId = {}, pestana = 'simulacro', sesion = null, reloj = null;

  fetch('preguntas.json').then(function (r) {
    if (!r.ok) throw new Error(r.status);
    return r.json();
  }).then(function (datos) {
    D = datos;
    D.preguntas.forEach(function (q) { porId[q.id] = q; });
    D.nombreTema = {};
    D.temas.forEach(function (tm) { D.nombreTema[tm.id] = tm; });
    rutaInicial();
  }).catch(function () {
    app.innerHTML = '';
    app.appendChild(el('p', { className: 'aviso aviso-rojo' }, t('error_carga')));
  });

  document.addEventListener('curso:idioma', function () {
    if (!D) return;
    if (sesion) pintarPregunta(); else if (app.querySelector('.resultado')) return; else pintarInicio();
  });
  window.addEventListener('hashchange', function () {
    if (!D || !location.hash) return;
    if (sesion && Object.keys(sesion.respuestas).length && !window.confirm(t('confirmar_salir'))) return;
    rutaInicial();
  });

  function rutaInicial() {
    var h = decodeURIComponent(location.hash.slice(1));
    var m;
    if ((m = /^tema-(\d{3})$/.exec(h)) && D.nombreTema[m[1]]) { pestana = 'temas'; pintarInicio(); empezarTema(m[1], 20, false); return; }
    if ((m = /^test-(\d{1,2})$/.exec(h))) { pestana = 'tests'; pintarInicio(); empezarTest(+m[1]); return; }
    if ((m = /^simulacro-(101|102)$/.exec(h))) { pestana = 'simulacro'; pintarInicio(); return; }
    if (h === 'fallos') pestana = 'fallos';
    if (h === 'progreso') pestana = 'progreso';
    pintarInicio();
  }

  // --- utilidades ----------------------------------------------------------------------------
  function el(tag, props, hijos) {
    var n = document.createElement(tag);
    if (props) Object.keys(props).forEach(function (k) {
      if (k === 'html') n.innerHTML = props[k];
      else if (k in n && k !== 'role') n[k] = props[k];
      else n.setAttribute(k, props[k]);
    });
    (Array.isArray(hijos) ? hijos : hijos == null ? [] : [hijos]).forEach(function (h) {
      if (h == null) return;
      n.appendChild(typeof h === 'string' ? document.createTextNode(h) : h);
    });
    return n;
  }
  function barajar(a) {
    a = a.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var x = a[i]; a[i] = a[j]; a[j] = x;
    }
    return a;
  }
  function correctas(q) { return Array.isArray(q.correcta) ? q.correcta : [q.correcta]; }
  function letra(i) { return String.fromCharCode(97 + i); }
  function pct(a, b) { return b ? Math.round(100 * a / b) : 0; }
  function nombreTema(id) { var tm = D.nombreTema[id]; return tm ? tm[idioma()] || tm.es : id; }
  function pool(incluirAmpliacion) {
    return D.preguntas.filter(function (q) { return incluirAmpliacion || q.nivel !== 'ampliacion'; });
  }
  function aciertoTema(e, tema) {
    var ok = 0, tot = 0;
    Object.keys(e.stats).forEach(function (id) {
      var q = porId[id];
      if (q && q.tema === tema) { ok += e.stats[id][0]; tot += e.stats[id][1]; }
    });
    return { ok: ok, tot: tot };
  }
  function irArriba() {
    var dest = document.getElementById('lpic');
    if (dest) dest.scrollIntoView({ block: 'start' });
  }

  // --- pantalla inicial ----------------------------------------------------------------------
  function pintarInicio() {
    sesion = null;
    pararReloj();
    var e = estado();
    app.innerHTML = '';
    var pest = el('div', { className: 'pestanas', role: 'tablist' });
    [['simulacro', 'pest_simulacro'], ['temas', 'pest_temas'], ['tests', 'pest_tests'], ['fallos', 'pest_fallos'], ['progreso', 'pest_progreso']].forEach(function (p) {
      var b = el('button', { type: 'button', role: 'tab', id: 'pest-' + p[0] }, t(p[1]) + (p[0] === 'fallos' && e.fallos.length ? ' (' + e.fallos.length + ')' : ''));
      b.setAttribute('aria-selected', pestana === p[0] ? 'true' : 'false');
      b.addEventListener('click', function () { pestana = p[0]; history.replaceState(null, '', '#' + (p[0] === 'simulacro' ? '' : p[0])); pintarInicio(); });
      pest.appendChild(b);
    });
    app.appendChild(pest);
    var panel = el('div', { role: 'tabpanel' });
    panel.setAttribute('aria-labelledby', 'pest-' + pestana);
    app.appendChild(panel);
    ({ simulacro: pintarSimulacros, temas: pintarTemas, tests: pintarTests, fallos: pintarFallos, progreso: pintarProgreso })[pestana](panel, e);
  }

  function pintarSimulacros(panel, e) {
    panel.appendChild(el('p', { className: 'nota' }, t('sim_intro')));
    var rej = el('div', { className: 'rejilla-tarjetas' });
    D.examenes.forEach(function (ex) {
      var hechos = e.examenes.filter(function (r) { return r.examen === ex.id; });
      var mejor = hechos.reduce(function (m, r) { return Math.max(m, r.nota); }, -1);
      var temas = ex.temas.map(function (id) { return id + ' ' + nombreTema(id); }).join(' · ');
      var b = el('button', { type: 'button', className: 'tarjeta-modo' }, [
        el('strong', null, ex.titulo),
        el('small', null, ex.preguntas + ' ' + t('preguntas') + ' · ' + ex.minutos + ' ' + t('minutos')),
        el('small', null, temas),
        el('small', null, t('mejor') + ': ' + (mejor >= 0 ? mejor + ' %' : t('sin_hacer'))),
        el('span', { className: 'boton boton-primario' }, t('sim_empezar'))
      ]);
      b.addEventListener('click', function () { empezarSimulacro(ex); });
      rej.appendChild(b);
    });
    panel.appendChild(rej);
  }

  function selectorCantidad(id) {
    var s = el('select', { id: id });
    [10, 20, 40, 0].forEach(function (n) { s.appendChild(el('option', { value: String(n) }, n ? String(n) : t('todas'))); });
    s.value = '20';
    return s;
  }

  function pintarTemas(panel, e) {
    panel.appendChild(el('p', { className: 'nota' }, t('temas_intro')));
    var sel = selectorCantidad('lpic-cantidad');
    var amp = el('input', { type: 'checkbox', id: 'lpic-amp' });
    panel.appendChild(el('div', { className: 'selector' }, [
      el('label', { htmlFor: 'lpic-cantidad' }, t('cuantas')), sel,
      el('label', null, [amp, ' ' + t('incluir_ampliacion')])
    ]));
    D.examenes.forEach(function (ex) {
      var bloque = el('section', { className: 'bloque-lpic' });
      bloque.appendChild(el('h2', null, ex.titulo));
      var rej = el('div', { className: 'rejilla-tarjetas' });
      ex.temas.forEach(function (id) {
        var n = D.preguntas.filter(function (q) { return q.tema === id && q.nivel !== 'ampliacion'; }).length;
        var a = aciertoTema(e, id);
        var barra = el('div', { className: 'barra-mini' }, el('span'));
        barra.firstChild.style.width = pct(a.ok, a.tot) + '%';
        var b = el('button', { type: 'button', className: 'tarjeta-modo', id: 'tema-' + id }, [
          el('strong', null, id + ' · ' + nombreTema(id)),
          el('small', null, n + ' ' + t('preguntas') + ' · ' + t('peso') + ' ' + D.nombreTema[id].peso),
          el('small', null, a.tot ? pct(a.ok, a.tot) + ' % ' + t('acierto') + ' (' + a.tot + ' ' + t('respondidas') + ')' : t('sin_hacer')),
          barra
        ]);
        b.addEventListener('click', function () { empezarTema(id, +sel.value, amp.checked); });
        rej.appendChild(b);
      });
      bloque.appendChild(rej);
      panel.appendChild(bloque);
    });
  }

  function pintarTests(panel, e) {
    panel.appendChild(el('p', { className: 'nota' }, t('tests_intro')));
    var rej = el('div', { className: 'rejilla-tarjetas' });
    D.tests.forEach(function (ts) {
      var mejor = e.tests[ts.n];
      var hijos = [el('strong', null, 'Test ' + ts.n + (ts.titulo ? ' · ' + ts.titulo : ''))];
      if (ts.nivel !== 'lpic1') hijos.push(el('span', { className: 'nivel ' + ts.nivel }, t('nivel_' + ts.nivel)));
      hijos.push(el('small', null, ts.preguntas.length + ' ' + t('preguntas')));
      hijos.push(el('small', null, t('mejor') + ': ' + (mejor != null ? mejor + ' %' : t('sin_hacer'))));
      var b = el('button', { type: 'button', className: 'tarjeta-modo' }, hijos);
      b.addEventListener('click', function () { empezarTest(ts.n); });
      rej.appendChild(b);
    });
    panel.appendChild(rej);
  }

  function pintarFallos(panel, e) {
    panel.appendChild(el('p', { className: 'nota' }, t('fallos_intro')));
    var ids = e.fallos.filter(function (id) { return porId[id]; });
    if (!ids.length) { panel.appendChild(el('p', null, t('fallos_vacio'))); return; }
    var porTema = {};
    ids.forEach(function (id) { var tm = porId[id].tema; porTema[tm] = (porTema[tm] || 0) + 1; });
    var tabla = el('table', { className: 'desglose' });
    tabla.appendChild(el('thead', null, el('tr', null, [el('th', null, t('tema')), el('th', null, t('preguntas'))])));
    var cuerpo = el('tbody');
    Object.keys(porTema).sort().forEach(function (tm) {
      cuerpo.appendChild(el('tr', null, [el('td', null, tm + ' · ' + nombreTema(tm)), el('td', null, String(porTema[tm]))]));
    });
    tabla.appendChild(cuerpo);
    var practicar = el('button', { type: 'button', className: 'boton boton-primario' }, t('fallos_practicar') + ' (' + ids.length + ')');
    practicar.addEventListener('click', function () {
      iniciar({ modo: 'fallos', titulo: t('pest_fallos'), ids: barajar(ids), corregirAlMomento: true });
    });
    var borrar = el('button', { type: 'button', className: 'boton' }, t('fallos_borrar'));
    borrar.addEventListener('click', function () {
      var est = estado(); est.fallos = []; guardarEstado(est); pintarInicio();
    });
    panel.appendChild(el('div', { className: 'botonera' }, [practicar, borrar]));
    panel.appendChild(tabla);
  }

  function pintarProgreso(panel, e) {
    var ok = 0, tot = 0;
    Object.keys(e.stats).forEach(function (id) { ok += e.stats[id][0]; tot += e.stats[id][1]; });
    var resp = Object.keys(e.stats).length;
    panel.appendChild(el('div', { className: 'estadisticas' }, [
      el('div', null, [el('strong', null, String(resp)), el('span', null, t('prog_respondidas'))]),
      el('div', null, [el('strong', null, pct(ok, tot) + ' %'), el('span', null, t('prog_acierto'))]),
      el('div', null, [el('strong', null, String(e.examenes.length)), el('span', null, t('prog_examenes'))]),
      el('div', null, [el('strong', null, String(e.fallos.length)), el('span', null, t('prog_fallos'))])
    ]));
    panel.appendChild(el('h2', null, t('historial')));
    if (!e.examenes.length) panel.appendChild(el('p', { className: 'nota' }, t('nada_aun')));
    else {
      var tabla = el('table', { className: 'desglose' });
      tabla.appendChild(el('thead', null, el('tr', null, [el('th', null, t('fecha')), el('th', null, t('examen')), el('th', null, t('nota'))])));
      var cuerpo = el('tbody');
      e.examenes.slice(-10).reverse().forEach(function (r) {
        var f = new Date(r.fecha);
        cuerpo.appendChild(el('tr', null, [
          el('td', null, isNaN(f) ? '' : f.toLocaleString(idioma() === 'en' ? 'en-GB' : 'es-ES', { dateStyle: 'short', timeStyle: 'short' })),
          el('td', null, r.examen), el('td', null, r.nota + ' %')
        ]));
      });
      tabla.appendChild(cuerpo);
      panel.appendChild(tabla);
    }
    var borrar = el('button', { type: 'button', className: 'boton' }, t('borrar_todo'));
    borrar.addEventListener('click', function () {
      if (window.confirm(t('confirmar_borrar'))) { guardarEstado({}); pintarInicio(); }
    });
    panel.appendChild(el('div', { className: 'botonera' }, borrar));
  }

  // --- comienzo de una prueba ----------------------------------------------------------------
  function empezarSimulacro(ex) {
    var disponibles = pool(false);
    var total = ex.temas.reduce(function (s, id) { return s + D.nombreTema[id].peso; }, 0);
    var elegidas = [];
    ex.temas.forEach(function (id) {
      var n = Math.round(ex.preguntas * D.nombreTema[id].peso / total);
      var delTema = barajar(disponibles.filter(function (q) { return q.tema === id && q.nivel === 'lpic1'; }));
      if (delTema.length < n) delTema = delTema.concat(barajar(disponibles.filter(function (q) { return q.tema === id && q.nivel === 'inicial'; })));
      elegidas = elegidas.concat(delTema.slice(0, n));
    });
    iniciar({ modo: 'simulacro', examen: ex.id, titulo: ex.titulo, ids: barajar(elegidas).map(function (q) { return q.id; }),
      corregirAlMomento: false, segundos: ex.minutos * 60 });
  }

  function empezarTema(tema, cantidad, ampliacion) {
    var qs = barajar(pool(ampliacion).filter(function (q) { return q.tema === tema; }));
    if (cantidad) qs = qs.slice(0, cantidad);
    iniciar({ modo: 'tema', titulo: tema + ' · ' + nombreTema(tema), ids: qs.map(function (q) { return q.id; }), corregirAlMomento: true });
  }

  function empezarTest(n) {
    var ts = D.tests.filter(function (x) { return x.n === n; })[0];
    if (!ts) return;
    iniciar({ modo: 'test', test: n, titulo: 'Test ' + n + (ts.titulo ? ' · ' + ts.titulo : ''), ids: ts.preguntas.slice(), corregirAlMomento: true });
  }

  function iniciar(cfg) {
    if (!cfg.ids.length) return;
    sesion = cfg;
    sesion.i = 0;
    sesion.respuestas = {};   // id → array de índices elegidos
    sesion.corregidas = {};   // id → true cuando ya se ha mostrado la solución
    if (cfg.segundos) {
      sesion.fin = Date.now() + cfg.segundos * 1000;
      arrancarReloj();
    }
    pintarPregunta();
    irArriba();
  }

  // --- reloj del simulacro -------------------------------------------------------------------
  function arrancarReloj() {
    pararReloj();
    reloj = setInterval(function () {
      var nodo = document.getElementById('lpic-reloj');
      var resta = Math.max(0, Math.round((sesion.fin - Date.now()) / 1000));
      if (nodo) {
        nodo.textContent = formatoTiempo(resta);
        nodo.classList.toggle('poco', resta <= 300);
      }
      if (resta <= 0) { pararReloj(); terminar(true); }
    }, 1000);
  }
  function pararReloj() { if (reloj) clearInterval(reloj); reloj = null; }
  function formatoTiempo(s) {
    var m = Math.floor(s / 60), x = s % 60;
    return (m < 10 ? '0' : '') + m + ':' + (x < 10 ? '0' : '') + x;
  }

  // --- pregunta ------------------------------------------------------------------------------
  function pintarPregunta() {
    var s = sesion, id = s.ids[s.i], q = porId[id];
    var corr = correctas(q), multiple = corr.length > 1;
    var elegidas = s.respuestas[id] || [];
    var corregida = !!s.corregidas[id];
    app.innerHTML = '';

    var cab = el('div', { className: 'cabecera-test' }, [el('h2', null, s.titulo)]);
    if (s.segundos) cab.appendChild(el('span', { className: 'reloj', id: 'lpic-reloj', role: 'timer', 'aria-live': 'off' },
      formatoTiempo(Math.max(0, Math.round((s.fin - Date.now()) / 1000)))));
    var salir = el('button', { type: 'button', className: 'boton' }, t('salir'));
    salir.addEventListener('click', function () {
      if (Object.keys(s.respuestas).length === 0 || window.confirm(t('confirmar_salir'))) {
        history.replaceState(null, '', location.pathname);
        pintarInicio();
      }
    });
    cab.appendChild(salir);
    app.appendChild(cab);

    var hechas = Object.keys(s.respuestas).length;
    var prog = el('div', { className: 'progreso-test', role: 'progressbar', 'aria-valuemin': '0', 'aria-valuemax': String(s.ids.length), 'aria-valuenow': String(hechas) }, el('span'));
    prog.firstChild.style.width = pct(hechas, s.ids.length) + '%';
    app.appendChild(prog);

    var caja = el('div', { className: 'pregunta' });
    var meta = [t('pregunta') + ' ' + (s.i + 1) + ' ' + t('de') + ' ' + s.ids.length, q.tema + ' · ' + nombreTema(q.tema)];
    if (q.test) meta.push('Test ' + q.test);
    caja.appendChild(el('div', { className: 'pregunta-num' }, meta.map(function (m) { return el('span', null, m); })));
    caja.appendChild(el('p', { className: 'pregunta-texto', id: 'texto-pregunta', html: q.texto }));
    if (multiple) caja.appendChild(el('p', { className: 'nota' }, t('elige_varias', { n: corr.length })));

    var lista = el('ul', { className: 'opciones', 'aria-labelledby': 'texto-pregunta' });
    q.opciones.forEach(function (op, i) {
      var b = el('button', { type: 'button', className: 'opcion' }, [el('span', { className: 'letra' }, letra(i)), el('span', { html: op })]);
      b.setAttribute('aria-pressed', elegidas.indexOf(i) !== -1 ? 'true' : 'false');
      if (corregida) {
        b.disabled = true;
        if (corr.indexOf(i) !== -1) b.classList.add('correcta');
        else if (elegidas.indexOf(i) !== -1) b.classList.add('incorrecta');
      }
      b.addEventListener('click', function () { elegir(i); });
      lista.appendChild(el('li', null, b));
    });
    caja.appendChild(lista);

    if (corregida) caja.appendChild(explicacion(q, elegidas));
    app.appendChild(caja);

    // botonera
    var bot = el('div', { className: 'botonera' });
    var ant = el('button', { type: 'button', className: 'boton' }, t('anterior'));
    ant.disabled = s.i === 0;
    ant.addEventListener('click', function () { s.i--; pintarPregunta(); });
    bot.appendChild(ant);
    var der = el('div', { className: 'derecha' });
    if (s.corregirAlMomento && multiple && !corregida) {
      var comp = el('button', { type: 'button', className: 'boton' }, t('comprobar'));
      comp.disabled = elegidas.length !== corr.length;
      comp.addEventListener('click', function () { corregir(id); });
      der.appendChild(comp);
    }
    if (s.i < s.ids.length - 1) {
      var sig = el('button', { type: 'button', className: 'boton boton-primario' }, t('siguiente'));
      sig.addEventListener('click', function () { s.i++; pintarPregunta(); });
      der.appendChild(sig);
    }
    var fin = el('button', { type: 'button', className: 'boton' + (s.i === s.ids.length - 1 ? ' boton-primario' : '') },
      s.modo === 'simulacro' ? t('terminar_examen') : t('terminar'));
    fin.addEventListener('click', function () {
      var faltan = s.ids.length - Object.keys(s.respuestas).length;
      if (!faltan || window.confirm(t('confirmar_terminar'))) terminar(false);
    });
    der.appendChild(fin);
    bot.appendChild(der);
    app.appendChild(bot);

    // navegador de preguntas
    var nav = el('nav', { className: 'navegador-preguntas', 'aria-label': t('pregunta') });
    s.ids.forEach(function (qid, i) {
      var b = el('button', { type: 'button' }, String(i + 1));
      if (s.respuestas[qid]) b.classList.add('respondida');
      if (s.corregidas[qid]) b.classList.add(esCorrecta(porId[qid], s.respuestas[qid]) ? 'ok' : 'ko');
      if (i === s.i) b.setAttribute('aria-current', 'true');
      b.setAttribute('aria-label', t('pregunta') + ' ' + (i + 1));
      b.addEventListener('click', function () { s.i = i; pintarPregunta(); });
      nav.appendChild(b);
    });
    app.appendChild(nav);
  }

  function elegir(i) {
    var s = sesion, id = s.ids[s.i], q = porId[id];
    if (s.corregidas[id]) return;
    var corr = correctas(q);
    var actual = (s.respuestas[id] || []).slice();
    if (corr.length > 1) {
      var pos = actual.indexOf(i);
      if (pos === -1) { if (actual.length < corr.length) actual.push(i); } else actual.splice(pos, 1);
    } else actual = [i];
    if (actual.length) s.respuestas[id] = actual; else delete s.respuestas[id];
    if (s.corregirAlMomento && corr.length === 1) corregir(id);
    else pintarPregunta();
  }

  function esCorrecta(q, elegidas) {
    var corr = correctas(q);
    return !!elegidas && elegidas.length === corr.length && corr.every(function (c) { return elegidas.indexOf(c) !== -1; });
  }

  function anotar(id, bien) {
    var e = estado();
    var st = e.stats[id] || [0, 0];
    e.stats[id] = [st[0] + (bien ? 1 : 0), st[1] + 1];
    var pos = e.fallos.indexOf(id);
    if (!bien && pos === -1) e.fallos.push(id);
    if (bien && pos !== -1 && sesion && sesion.modo === 'fallos') e.fallos.splice(pos, 1);
    guardarEstado(e);
  }

  function corregir(id) {
    sesion.corregidas[id] = true;
    anotar(id, esCorrecta(porId[id], sesion.respuestas[id]));
    pintarPregunta();
    var exp = app.querySelector('.explicacion');
    if (exp) exp.focus();
  }

  function explicacion(q, elegidas) {
    var bien = esCorrecta(q, elegidas);
    var corr = correctas(q);
    var caja = el('div', { className: 'explicacion' + (bien ? '' : ' mal'), tabIndex: -1 });
    caja.appendChild(el('p', null, el('strong', null, bien ? t('correcto') : t('incorrecto'))));
    if (!bien) {
      caja.appendChild(el('p', { html: '<strong>' + (corr.length > 1 ? t('las_correctas') : t('la_correcta')) + '</strong> ' +
        corr.map(function (c) { return letra(c) + ') ' + q.opciones[c]; }).join(' · ') }));
    }
    if (q.explicacion) caja.appendChild(el('p', { html: q.explicacion }));
    if (q.revision) caja.appendChild(el('p', { className: 'nota' }, t('revisada') + ' ' + q.revision));
    var lecs = (D.lecciones[q.tema] || []).slice(0, 3);
    if (lecs.length) {
      var p = el('p', { className: 'repasa' }, t('repasa') + ' ');
      lecs.forEach(function (l, i) {
        if (i) p.appendChild(document.createTextNode(' · '));
        p.appendChild(el('a', { href: l.u }, l.t));
      });
      caja.appendChild(p);
    }
    return caja;
  }

  // --- resultado -----------------------------------------------------------------------------
  function terminar(porTiempo) {
    var s = sesion;
    pararReloj();
    var ok = 0, porTema = {};
    s.ids.forEach(function (id) {
      var q = porId[id], bien = esCorrecta(q, s.respuestas[id]);
      if (!s.corregidas[id] && s.respuestas[id]) anotar(id, bien);
      else if (!s.corregidas[id] && !s.respuestas[id] && s.modo === 'simulacro') anotar(id, false);
      if (bien) ok++;
      var pt = porTema[q.tema] || (porTema[q.tema] = [0, 0]);
      pt[1]++;
      if (bien) pt[0]++;
    });
    var nota = pct(ok, s.ids.length);
    var e = estado();
    if (s.modo === 'simulacro') {
      e.examenes.push({ examen: s.examen, nota: nota, fecha: new Date().toISOString() });
      e.examenes = e.examenes.slice(-50);
    }
    if (s.modo === 'test') e.tests[s.test] = Math.max(e.tests[s.test] || 0, nota);
    guardarEstado(e);

    app.innerHTML = '';
    var res = el('section', { className: 'resultado', tabIndex: -1 });
    if (porTiempo) res.appendChild(el('p', { className: 'aviso aviso-rojo' }, t('tiempo_agotado')));
    res.appendChild(el('h2', null, t('resultado') + ' · ' + s.titulo));
    res.appendChild(el('p', { className: 'nota-grande ' + (nota >= 65 ? 'apto' : 'no-apto') }, nota + ' %'));
    res.appendChild(el('p', null, ok + ' / ' + s.ids.length + ' ' + t('aciertos')));
    if (s.modo === 'simulacro') {
      res.appendChild(el('p', null, el('strong', null, nota >= 65 ? t('apto') : t('no_apto'))));
      res.appendChild(el('p', { className: 'nota' }, t('nota_corte')));
    }
    var tabla = el('table', { className: 'desglose' });
    tabla.appendChild(el('caption', { className: 'nota' }, t('por_tema')));
    var cuerpo = el('tbody');
    Object.keys(porTema).sort().forEach(function (tm) {
      cuerpo.appendChild(el('tr', null, [el('td', null, tm + ' · ' + nombreTema(tm)),
        el('td', null, porTema[tm][0] + ' / ' + porTema[tm][1] + ' (' + pct(porTema[tm][0], porTema[tm][1]) + ' %)')]));
    });
    tabla.appendChild(cuerpo);
    res.appendChild(tabla);

    var botones = el('div', { className: 'botonera' });
    var volver = el('button', { type: 'button', className: 'boton' }, t('volver'));
    volver.addEventListener('click', function () { history.replaceState(null, '', location.pathname); pintarInicio(); });
    var repetir = el('button', { type: 'button', className: 'boton boton-primario' }, t('repetir'));
    repetir.addEventListener('click', function () {
      var cfg = { modo: s.modo, examen: s.examen, test: s.test, titulo: s.titulo, corregirAlMomento: s.corregirAlMomento, segundos: s.segundos };
      if (s.modo === 'simulacro') { empezarSimulacro(D.examenes.filter(function (x) { return x.id === s.examen; })[0]); return; }
      cfg.ids = s.modo === 'test' ? s.ids.slice() : barajar(s.ids);
      iniciar(cfg);
    });
    botones.appendChild(volver);
    botones.appendChild(repetir);
    res.appendChild(botones);

    var falladas = s.ids.filter(function (id) { return !esCorrecta(porId[id], s.respuestas[id]); });
    if (falladas.length) {
      res.appendChild(el('h3', null, t('revisar_fallos') + ' (' + falladas.length + ')'));
      var lista = el('div', { className: 'repaso-lista' });
      falladas.forEach(function (id) {
        var q = porId[id];
        var caja = el('div', { className: 'pregunta' });
        caja.appendChild(el('div', { className: 'pregunta-num' }, el('span', null, q.tema + ' · ' + nombreTema(q.tema))));
        caja.appendChild(el('p', { className: 'pregunta-texto', html: q.texto }));
        var mia = s.respuestas[id];
        caja.appendChild(el('p', { html: '<strong>' + t('tu_respuesta') + '</strong> ' +
          (mia ? mia.map(function (c) { return letra(c) + ') ' + q.opciones[c]; }).join(' · ') : t('sin_responder')) }));
        caja.appendChild(explicacion(q, mia));
        lista.appendChild(caja);
      });
      res.appendChild(lista);
    }
    app.appendChild(res);
    sesion = null;
    irArriba();
    res.focus();
  }
})();
