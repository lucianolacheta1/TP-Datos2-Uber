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


def pedir_entero(prompt: str, minimo: int | None = None,
                 maximo: int | None = None) -> int:
    """Pide un entero con reintento hasta que sea valido (y dentro del rango)."""
    while True:
        crudo = input(f"{prompt}: ").strip()
        try:
            valor = int(crudo)
        except ValueError:
            error("Ingresá un número entero.")
            continue
        if minimo is not None and valor < minimo:
            error(f"El valor debe ser mayor o igual a {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            error(f"El valor debe ser menor o igual a {maximo}.")
            continue
        return valor


def pedir_decimal(prompt: str, minimo: float | None = None) -> float:
    """Pide un número decimal con reintento hasta que sea valido."""
    while True:
        crudo = input(f"{prompt}: ").strip().replace(",", ".")
        try:
            valor = float(crudo)
        except ValueError:
            error("Ingresá un número (ej: 8.5).")
            continue
        if minimo is not None and valor < minimo:
            error(f"El valor debe ser mayor o igual a {minimo}.")
            continue
        return valor


def elegir_de_lista(items: list, etiqueta) -> object | None:
    """Muestra los items numerados y devuelve el elegido (None si cancela).

    etiqueta es una funcion item -> str para renderizar cada opcion.
    El usuario elige por numero; 0 cancela.
    """
    if not items:
        return None
    for i, item in enumerate(items, 1):
        print(f"  {i}. {etiqueta(item)}")
    print("  0. Cancelar")
    while True:
        crudo = input("\nElegí una opción: ").strip()
        if crudo == "0":
            return None
        if crudo.isdigit() and 1 <= int(crudo) <= len(items):
            return items[int(crudo) - 1]
        error("Opción inválida.")


def confirmar(prompt: str) -> bool:
    """Devuelve True si el usuario tipea exactamente 's' o 'S' o 'si'."""
    resp = input(f"{prompt} [s/N]: ").strip().lower()
    return resp in ("s", "si", "sí")


def pausa() -> None:
    """Espera al usuario antes de seguir."""
    input("\nPresioná Enter para continuar...")
