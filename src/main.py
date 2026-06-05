"""Entry point del TP Uber.

Uso:
    python -m src.main
"""
from src.config import validate
from src.menu.main_menu import loop
from src.menu import formato
from src.utils.logger import logger


def main() -> int:
    print("\nIniciando TP Uber...")
    print("Validando .env...", end=" ")
    validate()
    print("OK")

    logger.info("Aplicación iniciada")
    try:
        loop()
        return 0
    except KeyboardInterrupt:
        formato.info("\nInterrumpido por el usuario.")
        return 0
    except Exception as e:
        logger.exception("Error no manejado en el loop principal")
        formato.error(f"Error fatal: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
