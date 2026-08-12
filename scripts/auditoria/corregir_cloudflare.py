#!/usr/bin/env python3
"""Restituye los literales que Cloudflare destruyo en los modulos 8 y 9 (B5, B6).

Los dos archivos se guardaron desde una pagina servida por Cloudflare, que reescribe
cualquier cadena con '@' como `<a class="__cf_email__" data-cfemail="HEX">[email
protected]</a>` e inyecta un `<script>` que la descifra en el navegador. Fuera de
Cloudflare ese script da 404 y el literal nunca se recupera: el estudiante lee
`[email protected]` donde deberia haber un correo o una cadena de conexion.

El valor original va cifrado en `data-cfemail` (XOR con el primer byte), asi que la
reparacion es exacta: se sustituye el ancla por su texto y se borra el script muerto.

Uso:
    python3 scripts/auditoria/corregir_cloudflare.py --simular   # muestra sin escribir
    python3 scripts/auditoria/corregir_cloudflare.py             # aplica
"""
from __future__ import annotations

import argparse
import html as htmllib
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

RE_ANCLA = re.compile(r'<a\b[^>]*data-cfemail="([0-9a-f]+)"[^>]*>.*?</a>', re.S | re.I)
RE_SCRIPT = re.compile(r'<script[^>]*email-decode[^>]*>\s*</script>')


def descifrar(hexa: str) -> str:
    b = bytes.fromhex(hexa)
    return "".join(chr(c ^ b[0]) for c in b[1:])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true", help="no escribe, solo informa")
    args = ap.parse_args()

    total = 0
    for ruta in sorted(RAIZ.glob("*.html")):
        texto = ruta.read_text(encoding="utf-8")
        if "__cf_email__" not in texto and not RE_SCRIPT.search(texto):
            continue

        anclas = RE_ANCLA.findall(texto)
        scripts = len(RE_SCRIPT.findall(texto))
        print(f"--- {ruta.name}: {len(anclas)} literales, {scripts} script(s) muerto(s)")
        for h in anclas:
            print(f"      [email protected]  ->  {descifrar(h)}")

        nuevo = RE_ANCLA.sub(lambda m: htmllib.escape(descifrar(m.group(1)), quote=False), texto)
        nuevo = RE_SCRIPT.sub("", nuevo)

        if args.simular:
            print("      (simulacion: no se escribio nada)")
        else:
            ruta.write_text(nuevo, encoding="utf-8")
            print(f"      escrito. quedan __cf_email__: {nuevo.count('__cf_email__')}, "
                  f"cdn-cgi: {nuevo.count('cdn-cgi')}")
        total += len(anclas)

    print(f"\n{total} literales restituidos" + (" (simulado)" if args.simular else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
