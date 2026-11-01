"""Importa las lecciones originales (HTML de pandoc exportado desde Word) a fragmentos limpios.

Uso (una sola vez, ya ejecutado para la v2):
    python tools/importar_lecciones.py <carpeta_con_los_html_originales>

Lee `contenido/lecciones.json` para saber el título, el slug y el archivo de origen de cada
lección, y escribe:
    contenido/lecciones/<slug>.html   fragmento HTML limpio (sin <html>/<head>/<body>)
    media/<slug>/imagenN.webp         capturas convertidas a WebP

Lo que corrige respecto a la exportación de pandoc:
    - Los comandos y scripts venían como un <p> por línea: se agrupan en <pre><code>.
    - «Etiqueta: comando» se convierte en texto + <code>.
    - Los párrafos en negrita que hacían de título pasan a ser <h2>/<h3> reales.
    - Las imágenes pierden el alto/ancho fijo en pulgadas (se deformaban en móvil) y las rutas
      con barras invertidas.
"""
import html
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent

# Primeras palabras que delatan una línea de terminal.
COMANDOS = set("""
adduser alias apt apt-get apt-cache aptitude arp arping at atq atrm awk base64 basename bash bc bg
blkid bmon btop bzip2 bunzip2 cal cat cd chage chattr chgrp chmod chown chpasswd chroot chsh cksum
clamscan clamdscan clear cmatrix cmp comm cowsay cp cpio crontab crunch curl cut date dd deluser
df dhclient diff dig dmesg dmidecode dnf docker docker-compose dpkg du e2fsck echo egrep env
ethtool exit export expr fail2ban-client fail2ban-regex false fdisk fg fgrep figlet file find
finger firewall-cmd fortune free freshclam fsck fuser gdisk getent getfacl git gpasswd gping grep
groupadd groupdel groupmod groups grub-install grub-mkconfig gunzip gzip halt hashcat hdparm
head history host hostname hostnamectl htop hwclock hydra id ifconfig ifdown ifup iftop inxi
ionice iostat ip ip6tables iptables iptables-save iptables-restore iwconfig jobs john journalctl
kill killall last lastb lastlog less ln locate logger login logrotate logout ls lsattr lsblk
lscpu lsmod lspci lsof lsusb lvcreate lvdisplay lynis lolcat mail make man md5sum mkdir mkfs
mkfs.ext4 mkfs.vfat mkfs.xfs mke2fs mkswap modprobe more mount mpstat mv mysql mysql_secure_installation nano nc
ncat neofetch netstat newgrp nice nmap nmcli nmtui nohup nslookup ntpdate openssl parted passwd
paste pgrep php ping pip pip3 pkill poweroff printenv ps pstree pvcreate pwd python python3 rar
read readlink reboot renice resolvectl rm rmdir route rsync runlevel samba scp screen sed seq
service setfacl sftp sh sha256sum shred shutdown sl smbclient smbpasswd sort source split ss ssh
ssh-copy-id ssh-keygen stat strace su sudo swapoff swapon sync sysctl systemctl tail tar tcpdump
tee telnet test tiger time timedatectl timeout tmux top touch tr traceroute tree tshark tty
tune2fs type ufw umask umount uname unalias uniq unrar unzip update-grub updatedb uptime useradd
userdel usermod vi vim vmstat w wall watch wc wget whereis which while who whoami wireshark xargs
xz yes yum zcat zip zgrep arpspoof dsniff urlsnarf msgsnarf mailsnarf filesnarf webspy macof
dnsspoof tcpkill ettercap whois mtr vnstat fping compgen dpkg-query dconf unxz xz tput fmt patch od
dos2unix unix2dos recode iconv rev oneko mesg lsb_release netplan dnsmasq nethogs nload speedtest-cli
bmon iperf iperf3 ab hping3 arp-scan netdiscover masscan rkhunter chkrootkit aide lynis openvpn
wg wg-quick fping6 ping6 tracepath ss host getfacl setfacl chcon restorecon sestatus getenforce
setenforce apparmor_status aa-status visudo vipw vigr pwck grpck faillog pam_tally2 last lastlog
journalctl rsyslogd logwatch apt-mark snap usermod pinky toilet banner boxes asciiview aafire
cmatrix sl fortune cowthink ponysay espeak xeyes bb telnet nyancat hollywood genact pv dialog whiptail
notify-send zenity yad jq yq column numfmt shuf factor expand unexpand fold pr tac nl csplit
truncate fallocate mktemp install mkfifo sha1sum sha512sum b2sum md5 gpg ssh-agent ssh-add
sleep cargo pipx stress glances iotop atop nmon dstat sar npm node dirname exiftool binwalk strings hexdump xxd ldd ldconfig objdump readelf nm uptime lsns nsenter unshare
lxc incus podman kubectl systemd-analyze systemd-run loginctl localectl bootctl networkctl
 linpeas.sh linuxprivchecker.py nagios snap flatpak cubic clonezilla
mysqldump a2enmod a2ensite a2dissite apache2ctl nginx certbot postconf postfix dovecot mailq
newaliases sendmail testparm exportfs showmount ufw nikto gobuster sqlmap aircrack-ng
""".split())

PALABRAS_ES = set("""
y o e u a tu mi esto eso ese esa aquí así dentro solo sólo ejemplo archivo archivos comando
comandos usuario usuarios sistema puedes muestra crear ver otro otra cómo qué porque mismo
vez veces luego después antes primero ahora siempre nunca bien mejor forma manera paso
de la el los las que para con por una un del se en es al lo como más mas pero este esta estos
estas sus su si no ya muy también tambien cuando donde puede pueden permite permiten hay
nos te le les sobre entre hasta desde sin según segun cada todo todos toda todas ser está
están son fue hace hacer usar usa utiliza utilizar debe debes vamos podemos tenemos
""".split())

PALABRAS_SHELL = re.compile(
    r"^(if|then|else|elif|fi|for|do|done|while|until|case|esac|function|return|exit|echo|printf|"
    r"read|local|export|alias|source|break|continue|shift|declare|set|unset|trap)\b")


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def sin_comillas(texto):
    return re.sub(r"\"[^\"]*\"|'[^']*'", " ", texto)


def palabras_es(texto):
    n = 0
    for tok in sin_comillas(texto).lower().split():
        if tok.startswith(("-", "/", "$")) or "=" in tok or "/" in tok:
            continue  # opciones, rutas y variables no cuentan
        if tok.strip(".,;:()¿?¡!«»\"'") in PALABRAS_ES:
            n += 1
    return n


def primera_palabra(texto):
    t = texto.strip()
    t = re.sub(r"^(\$|#|\w+@[\w.-]+:\S*[$#])\s+", "", t)  # prompts "$ ", "# ", "user@host:~$ "
    m = re.match(r"[\w./+-]+", t)
    return m.group(0) if m else ""


def es_comando(texto):
    """¿La línea completa es un comando de terminal?"""
    t = texto.strip()
    if not t or len(t) > 400:
        return False
    w = primera_palabra(t)
    base = w.split("/")[-1]
    if base not in COMANDOS and not w.startswith("./"):
        return False
    resto = t[len(w):] if t.startswith(w) else t
    # «ls muestra el contenido de la carpeta» es prosa: comando seguido de una frase.
    n = palabras_es(resto)
    if n >= 4 or (n >= 2 and not re.search(r"\s-{1,2}\w|[|><$]", resto)):
        return False
    if re.match(r"^[A-ZÁÉÍÓÚ][a-záéíóúñ]+\s", t) and base.lower() != base:
        return False
    return True


def clasificar(texto, en_cita):
    """Devuelve 'C' (código), 'P' (prosa) o '?' (dudoso; lo decide el contexto)."""
    t = texto.strip()
    if not t:
        return "?"
    if t.startswith(("#!", "$ ", "sudo ", "./")) or re.match(r"^\w+@[\w.-]+:\S*[$#]\s", t):
        return "C"
    if re.match(r"^#\s?\S", t) and palabras_es(t) < 6:
        return "C"  # comentario de script
    if (re.match(r"^([\d*/,-]+\s+){5}\S", t)
            or (re.match(r"^@(reboot|daily|hourly|weekly|monthly|yearly|annually)\s", t) and palabras_es(t) < 2)
            or t == "EOF" or re.match(r"^!(\d+|!)$", t)):
        return "C"  # líneas de crontab, fin de heredoc, expansión del historial
    if (re.search(r"\bALL\s?=\s?\(", t) or re.match(r"^(CREATE|INSERT|SELECT|GRANT|FLUSH|DROP|ALTER|UPDATE|DELETE|USE|SHOW)\s+[A-Z*]", t)
            or re.match(r"^\w+\(\s*['\"$]", t)):
        return "C"  # sudoers, SQL, llamadas tipo define( 'X' )
    if (re.match(r"^[-dlcbps][rwxsStT-]{9}[.+@]?\s", t) or re.match(r"^([A-Z%][A-Z0-9%/@:>-]*\s+){3,}[A-Z%]", t)
            or re.match(r"^(●|[|`]-|\[\d+\][+-]?\s|\(\w+\)\s*>|ERROR:)", t) or re.match(r"^\w[\w.-]*@[\w.-]+:\S*[$#]\s*$", t)):
        return "C"  # salida de ls -l, cabeceras de ps/lsof/w, systemctl status, jobs, prompts
    if re.match(r"^-?(ba|z)?sh: ", t) or (" " not in t and t.count(":") >= 3):
        return "C"  # salida de la shell («-bash: cd: …») o líneas tipo /etc/passwd
    if re.match(r"^\[[\w .:/-]+\]$", t):
        return "C"  # sección de .ini / .service
    if re.match(r"^[A-Za-z_][\w.]*\s?=\s?\S", t) and " " not in t.split("=", 1)[0].strip():
        return "C"  # VAR=valor / Clave=Valor
    if PALABRAS_SHELL.match(t) and (palabras_es(t) < 4 or re.search(r"[;$\[\]\"]", t)):
        return "C"
    if re.match(r"^[{}()]\s*;?$", t) or t.endswith(("{", ";;", "; then", "; do")):
        return "C"
    if re.match(r"^</?[a-zA-Z!][\w-]*(\s|>|/>|$)", t) or re.match(r"^[.#]?[\w-][^{}]*\{.*\}$", t):
        return "C"  # HTML y CSS de los ejemplos
    if es_comando(t):
        return "C"
    if re.match(r"^[A-ZÁÉÍÓÚ¿¡][^=|$]{1,60}:$", t):
        return "P"  # «Explicación:», «Activar el timer:»
    if re.match(r"^\(?[A-ZÁÉÍÓÚ¿¡][a-záéíóúñ]+(\s+\S+){2,}[.!?)]$", t) and not re.search(r"[=|<>{}$]", t):
        return "P"  # frase normal: «Introduce varias contraseñas incorrectas.»
    if re.match(r"^https?://\S+$", t):
        return "P"
    n_es = palabras_es(t)
    if n_es >= 3 or (n_es >= 1 and re.search(r"[.:]$", t) and len(t.split()) >= 4):
        return "P"
    if re.match(r"^[A-ZÁÉÍÓÚ¿¡][a-záéíóúñ]", t) and len(t.split()) >= 5 and pinta_codigo(t) < 2:
        return "P"
    return "?"


ETIQUETAS_LENGUAJE = {"html", "bash", "sh", "shell", "python", "yaml", "json", "css", "javascript", "ini",
                      "plaintext", "text", "conf", "código", "copiar código", "php", "sql", "xml"}


def pinta_codigo(texto):
    """Cuántos rasgos de código/salida tiene una línea (0 = parece texto normal)."""
    t = texto.strip()
    n = len(re.findall(r"[/:=<>{}\[\]|*@%$#\\_]", t)) // 2
    n += len(re.findall(r"\b[a-z]+\.[a-z_]+\b|&&", t))  # http.request, a && b
    n += len(re.findall(r"\b\d+(\.\d+){1,3}\b", t))  # IP, versiones, tiempos
    if re.match(r"^[\w.-]+:\s*\S*$", t) or re.match(r"^-\s+\S+$", t):
        n += 2  # YAML
    if re.match(r"^[-=]{3,}", t):
        n += 2
    if re.search(r"\s{2,}\S", texto):
        n += 1  # columnas alineadas
    return n


def es_titulo(p):
    """Párrafo entero en negrita y corto → título."""
    hijos = [h for h in p.contents if not (isinstance(h, NavigableString) and not h.strip())]
    if len(hijos) != 1 or not isinstance(hijos[0], Tag) or hijos[0].name != "strong":
        return False
    texto = p.get_text(" ", strip=True)
    return 0 < len(texto) <= 110 and (not texto.endswith((".", ",")) or bool(re.match(r"^\d+\s*[.)-]", texto)))


def texto_plano(nodo):
    return re.sub(r"\s+", " ", nodo.get_text(" ")).strip()


def lineas(p):
    """Texto de un <p> separado por los <br>."""
    partes, actual = [], []
    for n in p.descendants:
        if isinstance(n, Tag) and n.name == "br":
            partes.append("".join(actual))
            actual = []
        elif isinstance(n, NavigableString):
            actual.append(str(n))
    partes.append("".join(actual))
    return [re.sub(r"[ \t\r\n]+", " ", x).strip() for x in partes]


def envolver_rutas(fragmento):
    """En prosa, marca como <code> las rutas absolutas (/etc/fstab, ~/.bashrc)."""
    def sub(m):
        return f"{m.group(1)}<code>{m.group(2)}</code>"
    trozos = re.split(r"(https?://(?:(?!&lt;|&gt;)[^\s<>\"»”)])+[^\s<>\"»”).,;:&])", fragmento)
    if len(trozos) > 1:  # las URL sueltas pasan a ser enlaces
        def url(t):
            if re.match(r"https?://(localhost|127\.|10\.|192\.168\.|ejemplo\.|example\.|tu-?)", t):
                return f"<code>{t}</code>"  # direcciones de laboratorio: no son enlaces reales
            return f'<a href="{t}" target="_blank" rel="noopener">{t}</a>'
        return "".join(url(t) if i % 2 else envolver_rutas(t) for i, t in enumerate(trozos))
    return re.sub(r"(^|[\s(«“])((?:~/|/)(?:[\w.*+-]+/)*[\w.*+-][\w.*+-]*?/?)(?=[.,;:]?(?:[\s)»”]|$))", sub, fragmento)


def limpiar_codigo(texto):
    """Deshace la autocorrección de Word dentro del código: comillas tipográficas y guiones largos."""
    texto = texto.replace("“", '"').replace("”", '"').replace("„", '"').replace("‘", "'").replace("’", "'")
    texto = re.sub(r"(^|\s)[–—](?=\w)", r"\1--", texto)
    return texto.replace(" ", " ")


def comillas_equilibradas(texto):
    return texto.count('"') % 2 == 0 and texto.count("'") % 2 == 0


def es_prosa(texto):
    t = texto.strip()
    return bool(t) and (palabras_es(t) >= 2 or (re.match(r"^[A-ZÁÉÍÓÚ¿¡(]", t) and len(t.split()) >= 2))


def es_codigo(texto):
    t = texto.strip()
    return clasificar(t, False) == "C" or bool(re.match(r"^-{1,2}\w[\w-]*(\s+(\S+|\"[^\"]*\"))?$", t))


def partir_mixto(texto):
    """Línea que mezcla prosa y un comando. Devuelve HTML o None.

    «Versión del kernel: uname -r»          → Versión del kernel: <code>uname -r</code>
    «sudo ufw enable: Habilita el firewall.» → <code>sudo ufw enable</code>: Habilita el firewall.
    «sudo mv a b (para activarla)»           → <code>sudo mv a b</code> (para activarla)
    """
    if re.match(r"^(#|\$ |\w+@[\w.-]+:|-?(ba|z)?sh: )", texto.strip()):
        return None  # comentario o prompt: es código entero
    t = texto.strip()
    e = lambda x: html.escape(x, quote=False)
    entero = clasificar(t, False) == "C" and not es_comando(t)  # sudoers, SQL, crontab…
    m = re.match(r"^(.{2,120}?):\s+(\S.*?)\.?$", t)
    if m and not entero and not es_comando(m.group(1)) and es_comando(m.group(2)) and comillas_equilibradas(m.group(2)):
        return f"{envolver_rutas(e(m.group(1)))}: <code>{e(limpiar_codigo(m.group(2)))}</code>"
    m = re.match(r"^(.+?):\s+(\S.*)$", t)
    if m and not entero and es_codigo(m.group(1)) and comillas_equilibradas(m.group(1)) and es_prosa(m.group(2)):
        return f"<code>{e(limpiar_codigo(m.group(1)))}</code>: {envolver_rutas(e(m.group(2)))}"
    m = re.match(r"^(.+?)\s+\(([^()]*)\)\.?$", t)
    if m and es_codigo(m.group(1)) and es_prosa(m.group(2)):
        return f"<code>{e(limpiar_codigo(m.group(1)))}</code> ({envolver_rutas(e(m.group(2)))})"
    m = re.match(r"^(.+?)\s+(?:→|->|=>)\s+(\S.*)$", t)
    if m and es_codigo(m.group(1)) and es_prosa(m.group(2)):
        return f"<code>{e(limpiar_codigo(m.group(1)))}</code> → {envolver_rutas(e(m.group(2)))}"
    return None


def etiqueta_y_comando(nodo):
    """«<strong>Instalación:</strong> sudo apt install x» → etiqueta en negrita + <code>."""
    hijos = [h for h in nodo.children if not (isinstance(h, NavigableString) and not h.strip())]
    if len(hijos) < 2 or not isinstance(hijos[0], Tag) or hijos[0].name != "strong":
        return None
    etiqueta = texto_plano(hijos[0])
    if es_codigo(etiqueta) and not etiqueta.endswith(":") and " " in etiqueta:
        # «<strong>home_mailbox = Maildir/</strong> → Define…»: la negrita era código
        return html_inline(nodo).replace(f"<strong>{html_inline(hijos[0])}</strong>",
                                         f"<code>{html.escape(limpiar_codigo(etiqueta), quote=False)}</code>", 1)
    resto = re.sub(r"\s+", " ", "".join(h.get_text(" ") if isinstance(h, Tag) else str(h) for h in hijos[1:])).strip()
    resto_cmd = re.sub(r"\.$", "", resto)
    if es_comando(resto_cmd) and not any(isinstance(h, Tag) and h.name in ("strong", "em") for h in hijos[1:]):
        return f"<strong>{html_inline(hijos[0])}</strong> <code>{html.escape(limpiar_codigo(resto_cmd), quote=False)}</code>"
    mixto = partir_mixto(resto)
    if mixto:
        return f"<strong>{html_inline(hijos[0])}</strong> {mixto}"
    return None


def html_inline(nodo, en_enlace=False):
    """HTML interior de un nodo, simplificado (solo strong/em/a/code)."""
    salida = []
    for n in nodo.children:
        if isinstance(n, NavigableString):
            texto = html.escape(str(n), quote=False)
            salida.append(texto if en_enlace else envolver_rutas(texto))
        elif isinstance(n, Tag):
            if n.name in ("strong", "b"):
                salida.append(f"<strong>{html_inline(n)}</strong>")
            elif n.name in ("em", "i"):
                salida.append(f"<em>{html_inline(n)}</em>")
            elif n.name == "a" and n.get("href"):
                href = html.escape(n["href"])
                ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
                salida.append(f'<a href="{href}"{ext}>{html_inline(n, True)}</a>')
            elif n.name == "br":
                salida.append("<br>")
            elif n.name == "img":
                continue
            else:
                salida.append(html_inline(n))
    return re.sub(r"\s+", " ", "".join(salida)).strip()


class Importador:
    def __init__(self, origen, leccion):
        self.origen = origen
        self.lec = leccion
        self.slug = leccion["slug"]
        self.n_img = 0
        self.salida = []
        self.codigo = []  # líneas pendientes de volcar en <pre>
        self.dudosas = []  # líneas «?» a la espera de contexto
        self.hay_titulos = False

    # --- código ---------------------------------------------------------------------------
    def volcar_codigo(self):
        if self.codigo:
            while self.codigo and not self.codigo[-1].strip():
                self.codigo.pop()
            lineas_cod = []
            for i, l in enumerate(self.codigo):
                lineas_cod.append(l)
                # «sudo nano archivo» seguido del contenido del archivo: se separan con una línea en blanco
                if re.match(r"^(sudo\s+)?(nano|vim?|gedit)\s+\S", l) and i + 1 < len(self.codigo):
                    lineas_cod.append("")
            texto = limpiar_codigo("\n".join(lineas_cod))
            self.salida.append(f'<pre><code>{html.escape(texto, quote=False)}</code></pre>')
            self.codigo = []

    def volcar_dudosas(self, como_codigo):
        if not self.dudosas:
            return
        if como_codigo:
            self.codigo.extend(t for t, _, _ in self.dudosas)
        else:
            self.volcar_codigo()
            for _, nodo_html, _ in self.dudosas:
                self.salida.append(nodo_html)
        self.dudosas = []

    def dudosas_son_codigo(self):
        """Sin código alrededor: un grupo de líneas sin prosa y con pinta de salida/configuración."""
        if any(cita for _, _, cita in self.dudosas):
            return True
        pintas = [pinta_codigo(t) for t, _, _ in self.dudosas]
        sin_prosa = all((palabras_es(t) == 0 or (palabras_es(t) <= 1 and pinta_codigo(t) >= 2))
                        and not re.match(r"^https?://\S+$", t) for t, _, _ in self.dudosas)
        if len(self.dudosas) >= 2:
            return sin_prosa and sum(p >= 1 for p in pintas) * 2 >= len(pintas)
        return sin_prosa and pintas[0] >= 2

    def linea(self, texto, tipo, nodo_html, en_cita):
        if tipo == "C":
            # «HTML», «Bash»… sueltos justo antes del código son la cabecera de un bloque copiado: fuera
            if self.dudosas and self.dudosas[-1][0].strip().lower() in ETIQUETAS_LENGUAJE:
                self.dudosas.pop()
            self.volcar_dudosas(bool(self.codigo) or en_cita or (bool(self.dudosas) and self.dudosas_son_codigo()))
            if not en_cita and es_comando(texto) and re.search(r"[^.\s]\.$", texto):
                texto = texto[:-1]  # «sudo apt install htop.»: el punto era de la frase
            self.codigo.append(texto)
        elif tipo == "?":
            self.dudosas.append((texto, nodo_html, en_cita))
        else:
            self.volcar_dudosas(bool(self.codigo) or (bool(self.dudosas) and self.dudosas_son_codigo()))
            self.volcar_codigo()
            self.salida.append(nodo_html)

    def cerrar_bloque(self, en_cita):
        self.volcar_dudosas(bool(self.codigo) or (bool(self.dudosas) and self.dudosas_son_codigo()))
        self.volcar_codigo()

    # --- imágenes -------------------------------------------------------------------------
    def imagen(self, img):
        src = img.get("src", "").replace("\\\\", "/").replace("\\", "/").lstrip("./")
        ruta = self.origen / src
        if not ruta.exists():
            raise FileNotFoundError(f"{self.lec['origen']}: {src}")
        self.n_img += 1
        destino = RAIZ / "media" / self.slug / f"imagen{self.n_img}.webp"
        destino.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(ruta)
        im = im.convert("RGBA" if im.mode in ("P", "LA", "RGBA") else "RGB")
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        if destino.exists() and destino.stat().st_mtime > ruta.stat().st_mtime:
            pass  # ya convertida en una pasada anterior
        elif ruta.suffix.lower() == ".png":
            im.save(destino, "WEBP", lossless=True, method=6)
            perdida = io.BytesIO()
            im.save(perdida, "WEBP", quality=90, method=6)
            if perdida.tell() < destino.stat().st_size * 0.6:
                destino.write_bytes(perdida.getvalue())
        else:
            im.save(destino, "WEBP", quality=82, method=6)
        alt = (img.get("alt") or "").strip()
        if not alt or re.match(r"^[\w\s.-]*\.(png|jpe?g|gif)$", alt, re.I) or alt.lower().startswith("image"):
            alt = f"Captura {self.n_img} de la lección «{self.lec['titulo']}»"
        return (f'<figure><img src="../media/{self.slug}/imagen{self.n_img}.webp" '
                f'width="{im.width}" height="{im.height}" alt="{html.escape(alt)}" loading="lazy" '
                f'decoding="async"></figure>')

    # --- recorrido --------------------------------------------------------------------------
    def parrafo(self, p, en_cita):
        imgs = p.find_all("img")
        if imgs:
            self.cerrar_bloque(en_cita)
            for img in imgs:
                self.salida.append(self.imagen(img))
            resto = p.get_text(" ", strip=True)
            if resto:
                self.salida.append(f"<p>{html_inline(p)}</p>")
            return
        plano = texto_plano(p)
        if (not p.find("a") and len(plano.split()) >= 2 and len(lineas(p)) == 1
                and clasificar(plano, en_cita) == "C" and partir_mixto(plano) is None):
            self.linea(plano, "C", "", en_cita)  # comando entero aunque Word lo pusiera en negrita
            return
        if es_titulo(p):
            self.cerrar_bloque(en_cita)
            nivel = "h3" if self.hay_titulos else "h2"
            self.salida.append(f"<{nivel}>{html.escape(texto_plano(p))}</{nivel}>")
            return
        ls = lineas(p)
        if len(ls) > 1:
            for t in ls:
                mixto = partir_mixto(t)
                if mixto:
                    self.linea(t, "P", f"<p>{mixto}</p>", en_cita)
                else:
                    self.linea(t, clasificar(t, en_cita), f"<p>{envolver_rutas(html.escape(t, quote=False))}</p>", en_cita)
            return
        texto = texto_plano(p)
        especial = etiqueta_y_comando(p) or (None if p.find(["strong", "em", "a"]) else partir_mixto(texto))
        if especial:
            self.linea(texto, "P", f"<p>{especial}</p>", en_cita)
            return
        self.linea(texto, clasificar(texto, en_cita), f"<p>{html_inline(p)}</p>", en_cita)

    @staticmethod
    def contenido_inline(nodo):
        """HTML de un párrafo corto (ítem de lista, celda): detecta comandos sueltos o mezclados."""
        t = texto_plano(nodo)
        if not t:
            return ""
        especial = etiqueta_y_comando(nodo)
        if especial:
            return especial
        if not nodo.find(["strong", "em", "a"]):
            mixto = partir_mixto(t)
            if mixto:
                return mixto
            if clasificar(t, False) == "C":
                return f"<code>{html.escape(limpiar_codigo(t), quote=False)}</code>"
        h = html_inline(nodo)
        # «Se navega a la carpeta <em>home</em>: cd /home.» → el comando final va en <code>
        if ": " in h:
            izq, der = h.rsplit(": ", 1)
            der_txt = html.unescape(re.sub(r"</?code>", "", der)).strip().rstrip(".")
            if "<" not in re.sub(r"</?code>", "", der) and es_comando(der_txt) and comillas_equilibradas(der_txt):
                return f"{izq}: <code>{html.escape(limpiar_codigo(der_txt), quote=False)}</code>"
        return h

    def lista(self, nodo):
        self.cerrar_bloque(False)
        partes = [f"<{nodo.name}>"]
        for li in nodo.find_all("li", recursive=False):
            dentro, suelto = [], []

            def volcar_suelto():
                if suelto:
                    tmp = Tag(name="p")
                    for x in suelto:
                        tmp.append(x)
                    dentro.append(self.contenido_inline(tmp))
                    suelto.clear()

            for h in list(li.children):
                if isinstance(h, Tag) and h.name in ("ul", "ol"):
                    volcar_suelto()
                    sub = Importador(self.origen, self.lec)
                    sub.n_img = self.n_img
                    sub.lista(h)
                    self.n_img = sub.n_img
                    dentro.append("".join(sub.salida))
                elif isinstance(h, Tag) and h.name == "p":
                    volcar_suelto()
                    if h.find("img"):
                        dentro.extend(self.imagen(i) for i in h.find_all("img"))
                    dentro.append(self.contenido_inline(h))
                elif isinstance(h, Tag) and h.name == "img":
                    volcar_suelto()
                    dentro.append(self.imagen(h))
                elif isinstance(h, Tag) and h.name in ("blockquote", "table", "div", "figure"):
                    volcar_suelto()
                    sub = Importador(self.origen, self.lec)
                    sub.n_img = self.n_img
                    sub.nodo(h)
                    sub.cerrar_bloque(False)
                    self.n_img = sub.n_img
                    dentro.append("".join(sub.salida))
                else:
                    suelto.append(h)
            volcar_suelto()
            dentro = [d for d in dentro if d]
            html_li = ""
            for i, d in enumerate(dentro):
                bloque = d.startswith(("<ul", "<ol", "<pre", "<div", "<figure", "<p>"))
                if i and not bloque and not html_li.endswith(("</ul>", "</ol>", "</pre>", "</div>", "</figure>", "</p>")):
                    html_li += "<br>"
                html_li += d
            partes.append("<li>" + html_li + "</li>")
        partes.append(f"</{nodo.name}>")
        self.salida.append("".join(partes))

    def tabla(self, nodo):
        self.cerrar_bloque(False)
        filas = []
        for tr in nodo.find_all("tr"):
            celdas = []
            for c in tr.find_all(["th", "td"]):
                ps = c.find_all("p")
                contenido = "<br>".join(self.contenido_inline(p) for p in ps) if ps else self.contenido_inline(c)
                celdas.append(f"<{c.name}>{contenido}</{c.name}>")
            filas.append("<tr>" + "".join(celdas) + "</tr>")
        cab = ""
        if nodo.find("thead"):
            cab = "<thead>" + filas.pop(0) + "</thead>"
        self.salida.append(f'<div class="tabla"><table>{cab}<tbody>{"".join(filas)}</tbody></table></div>')

    def nodo(self, n, en_cita=False):
        if isinstance(n, NavigableString):
            return
        if n.name == "p":
            self.parrafo(n, en_cita)
        elif n.name == "blockquote":
            self.cerrar_bloque(False)
            for h in n.children:
                self.nodo(h, en_cita=True)
            self.cerrar_bloque(True)
        elif n.name in ("h1", "h2", "h3", "h4", "h5"):
            texto = texto_plano(n)
            tras_dos_puntos = bool(self.salida) and self.salida[-1].endswith(":</p>") and not self.codigo
            if len(texto.split()) >= 2 and (es_comando(texto) or (tras_dos_puntos and primera_palabra(texto) in COMANDOS)):
                self.linea(texto, "C", "", en_cita)  # «Síntesis:» + título con el comando: era código
                return
            self.cerrar_bloque(en_cita)
            nivel = min(int(n.name[1]) + 1, 5)
            self.salida.append(f"<h{nivel}>{html.escape(texto_plano(n))}</h{nivel}>")
        elif n.name in ("ul", "ol"):
            self.lista(n)
        elif n.name == "table":
            self.tabla(n)
        elif n.name == "figure":
            self.cerrar_bloque(en_cita)
            for img in n.find_all("img"):
                self.salida.append(self.imagen(img))
        elif n.name in ("div", "section"):
            for h in n.children:
                self.nodo(h, en_cita)
        elif n.name == "script":
            return
        else:
            texto = n.get_text(" ", strip=True)
            if texto:
                self.linea(texto, clasificar(texto, en_cita), f"<p>{html_inline(n)}</p>", en_cita)

    def importar(self):
        sopa = BeautifulSoup((self.origen / self.lec["origen"]).read_text(encoding="utf-8"), "lxml")
        self.hay_titulos = bool(sopa.body.find(["h1", "h2", "h3"]))
        for n in sopa.body.children:
            self.nodo(n)
        self.cerrar_bloque(False)
        self.quitar_titulo_repetido()
        return "\n".join(self.salida) + "\n"

    def quitar_titulo_repetido(self):
        """El primer párrafo/título suele repetir el nombre de la lección (ya va en el <h1>)."""
        claves = {slug(self.lec["titulo"]), slug(re.sub(r"^\d+\s+|\.html$", "", self.lec["origen"]))}
        for i, bloque in enumerate(self.salida[:3]):
            if bloque.startswith("<figure"):
                continue
            texto = slug(re.sub(r"<[^>]+>", "", bloque))
            if texto and len(texto) < 120 and any(texto == c or texto in c or c in texto for c in claves):
                del self.salida[i]
            break


def main():
    origen = Path(sys.argv[1]).resolve()
    indice = json.loads((RAIZ / "contenido" / "lecciones.json").read_text(encoding="utf-8"))
    (RAIZ / "contenido" / "lecciones").mkdir(parents=True, exist_ok=True)
    for bloque in indice["bloques"]:
        for lec in bloque["lecciones"]:
            frag = Importador(origen, lec).importar()
            (RAIZ / "contenido" / "lecciones" / f"{lec['slug']}.html").write_text(frag, encoding="utf-8")
            print(f"{lec['slug']:55} {frag.count('<pre>'):3} bloques de código")


if __name__ == "__main__":
    main()
