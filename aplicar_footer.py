"""
Aplica el pie de página (footer) a TODAS las páginas de una sola vez.

Uso:
    1. Copia utils_footer.py dentro de tu carpeta utils/  →  utils/footer.py
    2. Ejecuta:  python aplicar_footer.py
       (por defecto busca en la carpeta 'pages/'; si tus módulos están en
        otra carpeta, pásala como argumento: python aplicar_footer.py mi_carpeta)

Qué hace, archivo por archivo:
    - Si el archivo ya tiene el footer aplicado, lo salta (seguro de correr varias veces).
    - Agrega el import 'from utils.footer import show_footer' junto a los demás imports.
    - Agrega la llamada 'show_footer()' al final del archivo.

No borra ni modifica nada más de tus archivos.
"""
import sys
import re
from pathlib import Path

MARCA = "show_footer()"
IMPORT_LINE = "from utils.footer import show_footer\n"


def aplicar_a_archivo(path: Path) -> str:
    texto = path.read_text(encoding="utf-8")

    if MARCA in texto:
        return "ya tenía el footer, sin cambios"

    lineas = texto.splitlines(keepends=True)

    # Insertar el import después del último 'import'/'from' inicial del archivo
    idx_insercion = 0
    for i, linea in enumerate(lineas):
        if linea.startswith("import ") or linea.startswith("from "):
            idx_insercion = i + 1
    lineas.insert(idx_insercion, IMPORT_LINE)

    nuevo_texto = "".join(lineas)
    if not nuevo_texto.endswith("\n"):
        nuevo_texto += "\n"
    nuevo_texto += "\n# Pie de página (autoría), agregado automáticamente\nshow_footer()\n"

    path.write_text(nuevo_texto, encoding="utf-8")
    return "footer agregado"


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("pages")
    if not carpeta.exists():
        print(f"⚠️  No encontré la carpeta '{carpeta}'. Pásala como argumento, ej: python aplicar_footer.py pages")
        return

    archivos = sorted(carpeta.glob("*.py"))
    if not archivos:
        print(f"⚠️  No hay archivos .py en '{carpeta}'.")
        return

    for archivo in archivos:
        resultado = aplicar_a_archivo(archivo)
        print(f"  {archivo.name}: {resultado}")

    print(f"\nListo. Revisado {len(archivos)} archivo(s) en '{carpeta}'.")


if __name__ == "__main__":
    main()