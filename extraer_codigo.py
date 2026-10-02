from __future__ import annotations

import argparse
import os
from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "env",
    "node_modules",
    "uploads",
    "venv",
}
IGNORED_SUFFIXES = {
    ".7z",
    ".avi",
    ".db",
    ".dll",
    ".doc",
    ".docx",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".pyc",
    ".rar",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".webm",
    ".webp",
    ".woff",
    ".woff2",
    ".xls",
    ".xlsx",
    ".zip",
}
def is_sensitive_file(path: Path) -> bool:
    name = path.name.lower()
    if name == ".env.example":
        return False
    return name == ".env" or name.startswith(".env.")


def read_text_file(path: Path) -> str | None:
    if path.suffix.lower() in IGNORED_SUFFIXES or is_sensitive_file(path):
        return None
    try:
        content = path.read_bytes()
        if b"\0" in content[:8192]:
            return None
        try:
            return content.decode("utf-8-sig")
        except UnicodeDecodeError:
            return content.decode("cp1252")
    except (OSError, UnicodeDecodeError):
        return None


def collect_files(root: Path, output: Path) -> list[tuple[Path, str]]:
    collected: list[tuple[Path, str]] = []
    output_resolved = output.resolve()

    for current, directories, filenames in os.walk(root, topdown=True):
        current_path = Path(current)
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
            and not (current_path / directory).is_symlink()
        )

        for filename in sorted(filenames):
            path = current_path / filename
            if path.resolve() == output_resolved or path.is_symlink():
                continue
            text = read_text_file(path)
            if text is not None:
                collected.append((path, text))

    return collected


def write_extraction(root: Path, output: Path) -> int:
    files = collect_files(root, output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="\n") as document:
        document.write(f"EXTRACCION DE CODIGO: {root.resolve()}\n")
        document.write(f"ARCHIVOS INCLUIDOS: {len(files)}\n")
        document.write("=" * 88 + "\n\n")

        for path, text in files:
            relative_path = path.relative_to(root).as_posix()
            document.write("=" * 88 + "\n")
            document.write(f"ARCHIVO: {relative_path}\n")
            document.write("=" * 88 + "\n\n")
            document.write(text)
            if not text.endswith("\n"):
                document.write("\n")
            document.write("\n")

    return len(files)


def parse_args() -> argparse.Namespace:
    script_directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Une archivos de texto y codigo del proyecto en un solo documento."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=script_directory,
        help="Carpeta a recorrer (por defecto, la carpeta donde esta este script).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=script_directory / "codigo_extraido.txt",
        help="Documento de salida (por defecto, codigo_extraido.txt en la carpeta del script).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    output = args.output.resolve()

    if not root.is_dir():
        raise SystemExit(f"La carpeta indicada no existe: {root}")

    total = write_extraction(root, output)
    print(f"Extraccion completa: {total} archivos guardados en {output}")


if __name__ == "__main__":
    main()
