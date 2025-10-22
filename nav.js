document.addEventListener("DOMContentLoaded", function() {
  // Lista de capítulos en orden exacto
  const files = [
    "00 Crear y administrar usuarios.html",
    "01 Redirección y procesamiento de texto I.html",
    "02 Redirección y procesamiento de texto II.html",
    "03 Redirección y procesamiento de texto III.html",
    "04 Archivos y compresión.html",
    "05 Comandos de navegación y gestión de archivos.html",
    "06 Comandos divertidos.html",
    "07 Montaje de sistemas de archivos.html",
    "08 Cubic.html",
    "09 Clonar un disco en Linux.html",
    "10 Clonar un pendrive booteable en Linux.html",
    "11 Creando una imagen de tu sistema con distroshare.html",
    "12 Clonado.html",
    "13 Clonezilla.html",
    "14 Procesos y gestión del sistema.html",
    "15 Administración de Procesos y Servicios.html",
    "16 Systemd.html",
    "17 Monitorización básica.html",
    "18 Comandos_Varios I.html",
    "19 Comandos_Varios II.html",
    "20 Compartir estructuras con tree.html",
    "21 Comandos de red I.html",
    "22 Comandos de red II.html",
    "23 gping.html",
    "24 Cron.html",
    "25 Crontab programando tareas en Linux.html",
    "26 Personalizacion Server.html",
    "27 Ubuntu Mini.html",
    "28 Escaneo y Enumeración de una red local con Nmap en Kali Linux.html",
    "29 Comandos para administrar y monitorear Servers.html",
    "30 Auditoria.html",
    "31 Seguridad.html",
    "32 Webmin.html",
    "33 Wordpress.html",
    "34 ANTIVIRUS CLAMAV.html",
    "35 docker.html",
    "36 Automatización de Auditorías de Seguridad con Bash.html",
    "37 Linuxprivchecker.html",
    "38 System-Monitor.html",
    "39 Tiger.html",
    "40 Bypass login Linux.html",
    "41 HTTP Inseguro.html",
    "42 tshark.html",
    "43 Configuración de red.html",
    "44 Nagios.html",
    "45 Cómo configurar el firewall.html",
    "46 UFW.html",
    "47 Compartir archivos en red.html",
    "48 Dsniff.html",
    "49 Fail2Ban.html",
    "50 Servidor de correo.html",
    "51 LinPwn.html",
    "52 Escalada de Privilegios.html"
  ];

  // Nombre del archivo actual
  const currentFile = decodeURIComponent(window.location.pathname.split("/").pop());
  const index = files.indexOf(currentFile);
  if (index === -1) return; // si no está en la lista, no hacemos nada

  // Crear contenedor
  const nav = document.createElement("div");
  nav.className = "nav-buttons";

  // Botón anterior
  if (index > 0) {
    const prev = document.createElement("a");
    prev.href = files[index - 1];
    prev.textContent = "⬅️ " + files[index - 1].replace(/^\d+\s/, "");
    nav.appendChild(prev);
  }

  // Botón siguiente
  if (index < files.length - 1) {
    const next = document.createElement("a");
    next.href = files[index + 1];
    next.textContent = files[index + 1].replace(/^\d+\s/, "") + " ➡️";
    nav.appendChild(next);
  }

  // Insertar al final del body
  document.body.appendChild(nav);
});
