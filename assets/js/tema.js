// Aplica el tema y el idioma guardados antes de pintar la página (evita el parpadeo).
(function () {
  var tema = null, idioma = null;
  try { tema = localStorage.getItem('cl_tema'); idioma = localStorage.getItem('cl_idioma'); } catch (e) { /* sin almacenamiento */ }
  if (tema !== 'light' && tema !== 'dark') {
    tema = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }
  document.documentElement.setAttribute('data-theme', tema);
  if (idioma === 'en') document.documentElement.setAttribute('lang', 'en');
})();
