"""Helpers de formato y entrada para el menú de consola."""


def titulo(texto: str) -> None:
    """Imprime un título con separadores."""
    print(f"\n{'=' * 60}")
    print(f"  {texto}")
    print(f"{'=' * 60}\n")


def subtitulo(texto: str) -> None:
    """Imprime un subtítulo."""
    print(f"\n--- {texto} ---\n")


def info(texto: str) -> None:
    """Imprime un mensaje informativo."""
    print(f"[INFO] {texto}")


def error(texto: str) -> None:
    """Imprime un mensaje de error."""
    print(f"[ERROR] {texto}")


def exito(texto: str) -> None:
    """Imprime un mensaje de éxito."""
    print(f"[OK] {texto}")


def tabla(items: list[dict], columnas: list[str]) -> None:
    """Imprime una tabla simple. columnas es una lista de keys del dict."""
    if not items:
        print("(sin resultados)")
        return
    # Headers
    print("  ".join(f"{c:<20}" for c in columnas))
    print("-" * (22 * len(columnas)))
    for it in items:
        print("  ".join(f"{str(it.get(c, '')):<20}" for c in columnas))


def pedir_input(prompt: str, default: str | None = None) -> str:
    """Pide un input al usuario con opcional valor por defecto."""
    if default is not None:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    valor = input(full_prompt).strip()
    return valor or (default or "")


def confirmar(prompt: str) -> bool:
    """Devuelve True si el usuario tipea exactamente 's' o 'S' o 'si'."""
    resp = input(f"{prompt} [s/N]: ").strip().lower()
    return resp in ("s", "si", "sí")


def pausa() -> None:
    """Espera al usuario antes de seguir."""
    input("\nPresioná Enter para continuar...")
