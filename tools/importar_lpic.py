"""Importa los 15 tests del antiguo repositorio Preparaci-n-LPIC1 al banco de preguntas del curso.

Uso (una sola vez, ya ejecutado para la v2):
    python tools/importar_lpic.py <carpeta_con_Test_(N).html>

Escribe contenido/lpic1/preguntas.json. A partir de ahí ese JSON es la fuente: las correcciones
de la revisión (CORRECCIONES) y las preguntas nuevas (contenido/lpic1/nuevas.json) se aplican aquí
para que quede constancia de qué se cambió y por qué.
"""
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "contenido" / "lpic1"

# Nivel de cada test: 14 y 15 son de nivel Linux Essentials; 8 (herramientas de red) y 13 van más allá de LPIC-1.
NIVEL_TEST = {14: "inicial", 15: "inicial", 8: "ampliacion", 13: "ampliacion"}
TITULO_TEST = {8: "Comandos de red"}

# Tema LPIC-1 por palabras clave (el primero que encaja). Se revisa a mano en CORRECCIONES.
REGLAS_TEMA = [
    ("106", r"\bx11\b|xorg|wayland|\bxdm\b|lightdm|gdm|sddm|\bdisplay\b|\bvnc\b|xdmcp|spice|\brdp\b|accesib|lector de pantalla|teclado en pantalla|escritorio|kde|gnome|xfce|libreoffice"),
    ("108", r"\bntp|chrony|hwclock|timedatectl|zona horaria|\bdate\b.*hora|syslog|rsyslog|journal|logrotate|logger|\bmta\b|sendmail|postfix|exim|mailq|/etc/aliases|newaliases|\.forward|\bcups|\blp\b|\blpr\b|lpq|lprm|lpstat|cupsd|impres"),
    ("110", r"\bsudo|sudoers|visudo|\bsuid\b|setuid|\bsgid\b|ssh|gpg|gnupg|nologin|xinetd|inetd|ulimit|nmap|lsof -i|\bfuser\b|shadow|chage|fail2ban|cifr|contraseñ|firewall|iptables|ufw|seguridad|\bwho\b|\blast\b|passwd -l"),
    ("109", r"\bip (addr|route|link|a\b|r\b)|ifconfig|\bss\b|netstat|\bdig\b|nslookup|\bhost\b|ipv6|ipv4|/etc/hosts|resolv\.conf|nsswitch|\broute\b|\bping|traceroute|tracepath|nmcli|networkmanager|hostnamectl|hostname|puerta de enlace|gateway|subred|máscara|mascara|\bdns\b|\btcp\b|\budp\b|puerto|dhcp|\barp\b|tcpdump|wget|curl|interfaz de red|/etc/services|\bmac\b"),
    ("107", r"useradd|usermod|userdel|groupadd|groupmod|groupdel|/etc/passwd|/etc/group|\bgetent\b|\bid\b|cron|crontab|\bat\b|atq|atrm|anacron|systemd-run|\.timer|locale|\blang\b|lc_all|iconv|utf-8|tzselect|/etc/timezone|/etc/localtime|/etc/skel|\bchsh\b"),
    ("105", r"\bbash|\bshell\b|script|#!|\bif\b|\bfor\b|while|\$\?|alias|\bfunction|\bexport\b|\benv\b|printenv|variable|\bset\b|unset|\bsource\b|\.bashrc|\.profile|/etc/profile|\bread\b|\btest\b|\bseq\b|\bexec\b|\$#|\$@|\$0|\$1"),
    ("102", r"\bapt|dpkg|\brpm\b|\byum\b|\bdnf\b|zypper|paquete|repositorio|\bldd\b|ldconfig|ld\.so|ld_library_path|librer|grub|gestor de arranque|cargador de arranque|partici|\blvm\b|lvcreate|pvcreate|vgcreate|swap|/boot|virtualiz|contenedor|docker|cloud-init|machine-id|d-bus|hipervisor|kvm"),
    ("101", r"lspci|lsusb|lsmod|modprobe|insmod|rmmod|modinfo|depmod|udev|/sys\b|sysfs|/proc|dmesg|runlevel|nivel de ejecuci|target|init\b|systemctl|systemd|arranque|bios|uefi|initramfs|initrd|kernel|apagar|reiniciar|shutdown|reboot|halt|poweroff|wall\b|hardware|dispositivo"),
    ("104", r"mount|umount|fstab|\bdf\b|\bdu\b|fsck|e2fsck|tune2fs|mkfs|mke2fs|xfs|btrfs|ext[234]|vfat|blkid|lsblk|fdisk|gdisk|parted|chmod|chown|chgrp|umask|sticky|permis|\bln\b|enlace|inodo|inode|fhs|/usr|/var|/opt|/srv|whereis|\bwhich\b|\blocate\b|updatedb|\bfind\b|\btype\b|sistema de archivos|sistema de ficheros|cuota|quota"),
    ("103", r".*"),
]

# Correcciones de la revisión manual: id → cambios (texto, opciones, correcta, explicacion, tema o
# eliminar) y motivo, que se guarda en la pregunta como «revision».
_ruta_corr = DESTINO / "correcciones.json"
CORRECCIONES = json.loads(_ruta_corr.read_text(encoding="utf-8")) if _ruta_corr.exists() else {}
CORRECCIONES.pop("_nota", None)


def limpiar(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"(^|\s)[–—](?=\w)", r"\1-", html.unescape(s))  # «tar –czf»: guion largo de Word en opciones
    return re.sub(r"\s+", " ", s).strip()


def markdown(s):
    """Convierte el **negrita** y `código` que se colaron en los tests 6-15 a HTML."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = s.replace("**", "")
    return s


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def bloques(s, apertura):
    idx = [m.start() for m in re.finditer(apertura, s)]
    fin = s.find("<script", idx[-1]) if idx else -1
    idx.append(fin if fin != -1 else len(s))
    return [s[idx[i]:idx[i + 1]] for i in range(len(idx) - 1)]


def quitar_letra(op):
    return re.sub(r"^\s*[a-fA-F]\)\s*", "", op).strip()


def explicacion_formato_a(resp, opcion):
    t = limpiar(resp)
    t = re.sub(r"^(la\s+)?respuesta correcta( es)?\s*:?\s*", "", t, flags=re.I)
    t = re.sub(r"^(opci[oó]n\s+)?[a-fA-F](\)\s*|\.|,|\s|$)", "", t).strip()
    if opcion and t.lower().startswith(opcion.lower()):
        t = t[len(opcion):].strip()
    t = t.lstrip(".").strip()
    m = re.match(r"^\((.*)\)\.?$", t, re.S)
    if m:
        t = m.group(1).strip()
    t = re.sub(r"^\.\s*", "", t)
    return t


def leer_test(ruta, n):
    s = ruta.read_text(encoding="utf-8")
    preguntas = []
    if 'class="pregunta-container"' in s:
        for i, b in enumerate(bloques(s, r'<div class="pregunta-container">'), 1):
            texto = limpiar(re.search(r'class="pregunta-texto">(.*?)</p>', b, re.S).group(1))
            ops = [limpiar(o) for o in re.findall(r"<li>(.*?)</li>", b, re.S)]
            resp = re.search(r'class="respuesta">(.*?)</div>', b, re.S).group(1)
            fuerte = limpiar(re.search(r"<strong>(.*?)</strong>", resp, re.S).group(1)) if "<strong>" in resp else limpiar(resp)
            fuerte = re.sub(r"^(la\s+)?respuesta correcta( es)?\s*:?\s*", "", fuerte, flags=re.I)
            m = re.match(r"^(?:opci[oó]n\s+)?([a-fA-F])(?:\)|\.|,|\s|$)", fuerte)
            letras = [o[:1].lower() for o in ops]
            if m:
                correcta = letras.index(m.group(1).lower())
            else:  # test 7, pregunta 14: la respuesta es el texto de la opción («O»)
                correcta = [quitar_letra(o) for o in ops].index(fuerte)
            opciones = [quitar_letra(o) for o in ops]
            preguntas.append(dict(n=i, texto=texto, opciones=opciones, correcta=correcta,
                                  explicacion=explicacion_formato_a(resp, opciones[correcta])))
    else:
        for i, b in enumerate(bloques(s, r'<div class="pregunta-contenedor">'), 1):
            texto = limpiar(re.search(r'class="pregunta">(.*?)</div>', b, re.S).group(1))
            ops = [limpiar(o) for o in re.findall(r'class="opcion">(.*?)</div>', b, re.S)]
            r = limpiar(re.search(r'class="respuesta-correcta">.*?</span>(.*?)</p>', b, re.S).group(1))
            e = re.search(r"Explicaci[oó]n:</strong>(.*?)</p>", b, re.S)
            if r in ops:
                correcta = ops.index(r)
            else:
                cands = [k for k, o in enumerate(ops) if r in o or o in r]
                correcta = cands[0] if cands else -1
            preguntas.append(dict(n=i, texto=texto, opciones=ops, correcta=correcta, explicacion=limpiar(e.group(1)) if e else ""))
    for p in preguntas:
        p["texto"] = re.sub(r"^\d+\s*[.\-)]+\s*-?\s*", "", p["texto"])
        # restos de un generador de texto en el test 9: «[cite_start](…) [cite: 3]»
        e = re.sub(r"\[cite_start\]|\[cite:\s*[\d,\s]+\]", "", p["explicacion"]).strip()
        e = re.sub(r"^Respuesta correcta:\s*[A-Fa-f]\.\s*", "", e)
        e = re.sub(r"^\((.*)\)\.?$", r"\1", e).strip()
        if p["correcta"] >= 0 and norm(e) == norm(quitar_letra(p["opciones"][p["correcta"]])):
            e = ""  # la «explicación» solo repetía la respuesta
        p["explicacion"] = e
    return preguntas


def tema(p):
    # solo el enunciado, la opción correcta y la explicación: las opciones falsas despistan
    correcta = p["opciones"][p["correcta"]] if p["correcta"] >= 0 else ""
    blob = (p["texto"] + " " + correcta + " " + p["explicacion"]).lower().replace("copia de seguridad", "respaldo")
    for t, r in REGLAS_TEMA:
        if re.search(r, blob):
            return t
    return "103"


def main():
    origen = Path(sys.argv[1])
    banco, vistos = [], {}
    tests = []
    for n in range(1, 16):
        ps = leer_test(origen / f"Test ({n}).html", n)
        ids = []
        for p in ps:
            pid = f"t{n:02d}-{p['n']:03d}"
            q = dict(id=pid, test=n, texto=p["texto"], opciones=p["opciones"], correcta=p["correcta"],
                     explicacion=p["explicacion"], tema=tema(p), nivel=NIVEL_TEST.get(n, "lpic1"))
            c = CORRECCIONES.get(pid)
            if c:
                if c.get("eliminar"):
                    continue
                q.update({k: v for k, v in c.items() if k != "motivo"})
                if c.get("motivo"):
                    q["revision"] = c["motivo"]
            # «correcta» es un índice o, en las preguntas de «escoge dos/tres», una lista de índices
            corr = q["correcta"] if isinstance(q["correcta"], list) else [q["correcta"]]
            clave = norm(q["texto"]) + "|" + "|".join(norm(q["opciones"][c]) for c in corr if c >= 0)
            if clave in vistos:
                q["repetida_de"] = vistos[clave]
            else:
                vistos[clave] = pid
            ids.append(pid)
            banco.append(q)
        tests.append({"n": n, "titulo": TITULO_TEST.get(n, ""), "nivel": NIVEL_TEST.get(n, "lpic1"), "preguntas": ids})
    nuevas_ruta = DESTINO / "nuevas.json"
    if nuevas_ruta.exists():
        for q in json.loads(nuevas_ruta.read_text(encoding="utf-8")):
            q.setdefault("nivel", "lpic1")
            q["nueva"] = True
            banco.append(q)
    for q in banco:  # el texto se publica como HTML: escapar y convertir el markdown colado
        q["texto"] = markdown(q["texto"])
        q["opciones"] = [markdown(o) for o in q["opciones"]]
        q["explicacion"] = markdown(q["explicacion"])
    salida = {"version": 2, "tests": tests, "preguntas": banco}
    DESTINO.mkdir(parents=True, exist_ok=True)
    (DESTINO / "preguntas.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(len(banco), "preguntas;", sum(1 for q in banco if "repetida_de" in q), "repetidas;",
          dict(sorted(Counter(q["tema"] for q in banco).items())))


if __name__ == "__main__":
    main()
