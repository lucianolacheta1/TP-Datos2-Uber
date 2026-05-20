# Plan 05 — Seeding de datos + Preparación de la presentación

> **Para agentes:** REQUIRED SUB-SKILL: Usar `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans`. Los pasos usan checkboxes `- [ ]` para tracking.

**Goal:** Llevar el proyecto desde "ejecutable end-to-end" hasta "listo para presentar". Cargar datos realistas para que los 7 casos de uso devuelvan resultados visibles, implementar el simulador GPS, armar las slides, ensayar el demo y resolver todos los riesgos.

**Architecture:** Un script `seed_data.py` que crea un dataset coherente (usuarios, conductores, vehículos, viajes finalizados, pagos, reseñas) usando los services del Plan 03. Un `simulador_gps.py` que en un hilo background reporta posiciones para vehículos activos durante el demo. Un `demo_automatico.py` como fallback ante problemas en vivo. Slides en PowerPoint/Google Slides + checklist de ensayo.

**Tech Stack:** Mismo que Planes 01-04. Sin librerías nuevas (`threading` y `random` del stdlib).

---

## Pre-requisitos

**Planes 01, 02, 03 y 04 completos.** Esto significa:

- ✅ 5 bases cloud + esquemas + 11 repositories + 7 services + 7 casos de uso + menú.
- ✅ `python -m src.main` arranca la app y permite recorrer todo el flujo manualmente.
- ✅ `pytest tests/` corre verde de punta a punta (~140+ tests).
- ✅ Smoke test manual del Plan 04 §5 pasa.

---

## Alcance de este plan

Cubre las **Fases 7 y 8** de `docs/tareas.md`: datos de prueba, simulador GPS, slides, ensayos.

**NO incluye:**
- Nuevas funcionalidades de negocio (las 4 fases anteriores ya cubren todo).
- Cambios al diseño técnico (los planes anteriores son el alcance).

**Entregables al finalizar:**

- ✅ `scripts/seed_data.py`: dataset realista de ~10 usuarios, ~5 conductores, ~7 vehículos, ~50 viajes finalizados, pagos y reseñas distribuidos para que los 7 casos den resultados.
- ✅ `scripts/simulador_gps.py`: thread que reporta posiciones GPS aleatorias para vehículos cada 2 segundos.
- ✅ `scripts/demo_automatico.py`: script de fallback que ejecuta el guión sin interacción manual.
- ✅ Slides exportadas a PPTX y PDF en `docs/slides/`.
- ✅ Checklist del día previo completo.
- ✅ Al menos 2 ensayos completos del demo (~20 min cada uno) registrados como hechos.
- ✅ La carpeta `Uber/` tiene el material original disponible para mostrar el DER al profesor.

---

## File Structure

Archivos que se crean en este plan:

```
scripts/
├── seed_data.py            ← carga ~50 viajes + pagos + reseñas distribuidos
├── simulador_gps.py        ← thread que reporta GPS continuo
└── demo_automatico.py      ← fallback no-interactivo del guion

docs/
└── slides/
    ├── presentacion.pptx   ← 8 slides
    └── presentacion.pdf    ← export para backup
```

Se actualizan:
- `docs/presentacion.md` — agregar resultados esperados del seed y referencia al simulador.
- `docs/tareas.md` — marcar Fases 7 y 8 como completadas.

---

## Sección 1 — Seed de datos

### Task 1.1: Diseño del dataset

> No hay código todavía. Esta tarea define los datos que va a generar el seed para que **los 7 casos de uso devuelvan resultados visibles** durante la presentación.

- [ ] **Step 1: Confirmar la estructura del dataset**

**Usuarios (10):** Juan Pérez, María García, Carlos López, Ana Rodríguez, Pedro Martínez, Laura Fernández, Diego Sánchez, Sofía Romero, Martín Díaz, Valentina Torres.

**Conductores (5):** Ana Gómez, Luis Castro, Beatriz Silva, Roberto Núñez, Carolina Vega.

**Vehículos (7):** distribución por marca y patente para satisfacer el caso 6:

| Conductor | Placa | Marca | Modelo | Tipo |
|---|---|---|---|---|
| Ana Gómez | `ABC123D` | Toyota | Corolla | sedan |
| Ana Gómez | `XYZ888D` | Toyota | Hilux | pickup |
| Luis Castro | `TOY222D` | Toyota | Etios | sedan |
| Luis Castro | `HND111A` | Honda | Civic | sedan |
| Beatriz Silva | `FRD555X` | Ford | Focus | sedan |
| Roberto Núñez | `VWA444B` | Volkswagen | Gol | sedan |
| Carolina Vega | `RNT666D` | Renault | Sandero | sedan |

⇒ **Caso 6** debería devolver **4 Toyota con patente terminada en "D"** (Corolla, Hilux, Etios, y técnicamente solo los 3 primeros son Toyota — Renault termina en D pero no es Toyota). Actualizo el conteo: **3 Toyota con patente terminada en D** (Corolla, Hilux, Etios).

**Viajes (50, con distribución):**
- **Coincidencias para caso 5:** que algunos pares pasajero-conductor tengan ≥2 viajes.
  - Juan ↔ Ana Gómez: 4 viajes
  - María ↔ Luis Castro: 3 viajes
  - Carlos ↔ Beatriz Silva: 2 viajes
  - Resto (~41 viajes): pares únicos sin repetición → no aparecen en caso 5.
- **Distribución temporal para caso 3:**
  - **Carolina Vega**: ningún viaje en los últimos 30 días (todos hace 2+ meses) → aparece como inactiva.
  - **Roberto Núñez**: ningún viaje nunca → aparece como inactivo.
  - El resto: al menos un viaje en el último mes.
- **Duración para caso 4:** valores aleatorios entre 10 y 45 min, distribución media ~22 min.

**Pagos (1 por viaje finalizado = ~50):** distribución para caso 2:
- TARJETA: ~30 pagos
- EFECTIVO: ~15 pagos
- BILLETERA_VIRTUAL: ~5 pagos
⇒ **Caso 2** debe devolver **BILLETERA_VIRTUAL**.

**Reseñas (2 por viaje finalizado = ~100, U_A_C y C_A_U):**
- **Caso 1 (top 3 reseñadores):** los usuarios con más viajes deberían liderar.
  - Juan (4 viajes con Ana + algunos más) → ~6 reseñas U_A_C.
  - María → ~5 reseñas U_A_C.
  - Carlos → ~4 reseñas U_A_C.
- **Caso 7 (rating extremo):** asegurar:
  - ~5 reseñas con rating 5.
  - ~3 reseñas con rating 1.
  - El resto: 3 o 4.

- [ ] **Step 2: Verificar que el diseño cubre los 7 casos**

Releer cada caso del enunciado y confirmar que el dataset diseñado da un resultado **no-vacío y demostrable**:

- [ ] Caso 1: top 3 va a tener a Juan, María, Carlos (cantidades distintas).
- [ ] Caso 2: BILLETERA_VIRTUAL es el menos usado.
- [ ] Caso 3: Carolina Vega + Roberto Núñez aparecen como inactivos.
- [ ] Caso 4: promedio ronda los ~22 min.
- [ ] Caso 5: 3 pares con coincidencias (Juan-Ana 4, María-Luis 3, Carlos-Beatriz 2).
- [ ] Caso 6: 3 Toyota con patente terminada en D.
- [ ] Caso 7: ~5 con rating 5, ~3 con rating <2 (los de rating 1).

- [ ] **Step 3: (Sin commit, es solo planificación)**

---

### Task 1.2: Implementar `seed_data.py`

**Files:**
- Create: `scripts/seed_data.py`

- [ ] **Step 1: Implementar**

```python
"""Seed de datos realista para la demo y testing manual.

Genera un dataset coherente que cubre los 7 casos de uso del enunciado:
- 10 usuarios, 5 conductores, 7 vehículos.
- ~50 viajes finalizados (con coincidencias específicas para el caso 5).
- ~50 pagos (distribución de métodos para el caso 2).
- ~100 reseñas (ratings distribuidos para el caso 7, autores variados para el caso 1).
- Distribución temporal para el caso 3 (algunos conductores inactivos).

Uso:
    python -m scripts.seed_data
"""
import random
import uuid
from datetime import datetime, UTC, timedelta

from src.config import validate
from src.services import (
    auth_service, vehiculo_service,
    viaje_service, pago_service, resena_service,
)
from src.utils.logger import logger

# ---- datos base ----

USUARIOS = [
    ("juan@m.com",     "Juan Pérez"),
    ("maria@m.com",    "María García"),
    ("carlos@m.com",   "Carlos López"),
    ("ana@m.com",      "Ana Rodríguez"),
    ("pedro@m.com",    "Pedro Martínez"),
    ("laura@m.com",    "Laura Fernández"),
    ("diego@m.com",    "Diego Sánchez"),
    ("sofia@m.com",    "Sofía Romero"),
    ("martin@m.com",   "Martín Díaz"),
    ("valentina@m.com","Valentina Torres"),
]

CONDUCTORES = [
    # (email, nombre, licencia)
    ("anag@m.com",     "Ana Gómez",       "LIC-001"),
    ("luis@m.com",     "Luis Castro",     "LIC-002"),
    ("beatriz@m.com",  "Beatriz Silva",   "LIC-003"),
    ("roberto@m.com",  "Roberto Núñez",   "LIC-004"),
    ("carolina@m.com", "Carolina Vega",   "LIC-005"),
]

VEHICULOS = [
    # (idx_conductor, placa, marca, modelo, anio, color, tipo)
    (0, "ABC123D", "Toyota",     "Corolla", 2020, "Blanco", "sedan"),
    (0, "XYZ888D", "Toyota",     "Hilux",   2021, "Negro",  "pickup"),
    (1, "TOY222D", "Toyota",     "Etios",   2019, "Gris",   "sedan"),
    (1, "HND111A", "Honda",      "Civic",   2022, "Azul",   "sedan"),
    (2, "FRD555X", "Ford",       "Focus",   2018, "Rojo",   "sedan"),
    (3, "VWA444B", "Volkswagen", "Gol",     2020, "Blanco", "sedan"),
    (4, "RNT666D", "Renault",    "Sandero", 2019, "Plata",  "sedan"),
]

LUGARES = [
    ({"lat": -34.6087, "lon": -58.3716, "direccion": "Microcentro"}, {"lat": -34.5876, "lon": -58.3934, "direccion": "Recoleta"}),
    ({"lat": -34.5778, "lon": -58.4226, "direccion": "Palermo"},     {"lat": -34.5631, "lon": -58.4587, "direccion": "Belgrano"}),
    ({"lat": -34.6443, "lon": -58.4116, "direccion": "Caballito"},   {"lat": -34.6037, "lon": -58.3816, "direccion": "Monserrat"}),
    ({"lat": -34.5499, "lon": -58.4632, "direccion": "Núñez"},       {"lat": -34.5878, "lon": -58.4174, "direccion": "Las Heras"}),
    ({"lat": -34.6178, "lon": -58.3645, "direccion": "Puerto Madero"}, {"lat": -34.6010, "lon": -58.3819, "direccion": "Once"}),
]

COMENTARIOS_5 = ["Excelente viaje", "Muy amable y puntual", "10/10 lo recomiendo", "Perfecto, sin quejas", "Auto impecable"]
COMENTARIOS_4 = ["Buen viaje", "Todo bien", "Sin novedades", "Cumplió", "Conforme"]
COMENTARIOS_3 = ["Aceptable", "Normal", "Ni bueno ni malo"]
COMENTARIOS_1 = ["Muy mal trato", "Llegó tarde y de mal humor", "No vuelvo a usarlo"]


# ---- helpers ----

def _crear_usuarios(usuarios_data: list) -> list[tuple[str, str]]:
    """Registra usuarios. Devuelve [(id, nombre), ...]."""
    out = []
    for email, nombre in usuarios_data:
        try:
            uid = auth_service.register_usuario(email, "demo1234", nombre)
            out.append((uid, nombre))
            logger.info(f"Usuario creado: {nombre}")
        except Exception as e:
            logger.warning(f"Skipping {nombre}: {e}")
    return out


def _crear_conductores(conductores_data: list) -> list[tuple[str, str]]:
    out = []
    for email, nombre, licencia in conductores_data:
        try:
            cid = auth_service.register_conductor(email, "demo1234", nombre, licencia)
            out.append((cid, nombre))
            logger.info(f"Conductor creado: {nombre}")
        except Exception as e:
            logger.warning(f"Skipping {nombre}: {e}")
    return out


def _crear_vehiculos(vehiculos_data: list, conductores: list) -> list[tuple[str, str, str]]:
    """Devuelve [(vehiculo_id, conductor_id, conductor_nombre), ...]."""
    out = []
    for idx_cond, placa, marca, modelo, anio, color, tipo in vehiculos_data:
        cid, cnombre = conductores[idx_cond]
        try:
            vid = vehiculo_service.registrar(cid, placa, marca, modelo, anio, color, tipo)
            out.append((vid, cid, cnombre))
            logger.info(f"Vehículo {placa} ({marca}) creado para {cnombre}")
        except Exception as e:
            logger.warning(f"Skipping vehículo {placa}: {e}")
    return out


def _crear_viaje_finalizado(
    usuario: tuple[str, str],
    conductor: tuple[str, str],
    vehiculo: tuple[str, str, str],
    fecha_fin: datetime,
    duracion_min: int,
    distancia_km: float,
) -> str:
    """Crea un viaje y lo finaliza con la fecha indicada."""
    uid, _ = usuario
    cid, _ = conductor
    vid, _, _ = vehiculo
    origen, destino = random.choice(LUGARES)

    viaje_id = viaje_service.solicitar(uid, cid, vid, origen, destino)
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, distancia_km, duracion_min)

    # Sobreescribir ts_fin manualmente para simular fechas pasadas (caso 3)
    from src.db.mongo import get_db
    get_db().viajes.update_one(
        {"_id": viaje_id},
        {"$set": {"ts_fin": fecha_fin}},
    )
    return viaje_id


def _crear_pago(viaje_id: str, monto: float, metodo: str) -> None:
    pago_service.procesar(
        viaje_id, monto,
        tarifa_base=500,
        tarifa_distancia=monto * 0.5,
        tarifa_tiempo=monto * 0.3,
        cargos_extra=monto * 0.05,
        metodo_pago=metodo,
    )


def _crear_resena(viaje_id: str, usuario: tuple, conductor: tuple,
                  tipo: str, rating: int) -> None:
    if tipo == "U_A_C":
        autor_id, autor_nombre = usuario
        dest_id, dest_nombre = conductor
    else:
        autor_id, autor_nombre = conductor
        dest_id, dest_nombre = usuario

    comentario = {
        5: random.choice(COMENTARIOS_5),
        4: random.choice(COMENTARIOS_4),
        3: random.choice(COMENTARIOS_3),
        1: random.choice(COMENTARIOS_1),
    }.get(rating, "Sin comentario")

    resena_service.crear(
        viaje_id, tipo,
        autor_id, autor_nombre,
        dest_id, dest_nombre,
        rating, comentario,
    )


# ---- main ----

def main() -> int:
    random.seed(42)  # reproducible
    validate()

    logger.info("=== Seed iniciado ===")

    # 1. Usuarios y conductores
    usuarios = _crear_usuarios(USUARIOS)
    conductores = _crear_conductores(CONDUCTORES)
    vehiculos = _crear_vehiculos(VEHICULOS, conductores)

    if not usuarios or not conductores or not vehiculos:
        logger.error("No se pudieron crear entidades base. Abortando.")
        return 1

    # 2. Construir el plan de viajes
    # Estructura: lista de (idx_usuario, idx_conductor, dias_atras)
    plan_viajes: list[tuple[int, int, int]] = []

    # Coincidencias para caso 5
    for _ in range(4):  # Juan ↔ Ana Gómez (idx 0 user, idx 0 cond)
        plan_viajes.append((0, 0, random.randint(0, 20)))
    for _ in range(3):  # María ↔ Luis Castro (idx 1, idx 1)
        plan_viajes.append((1, 1, random.randint(0, 20)))
    for _ in range(2):  # Carlos ↔ Beatriz Silva (idx 2, idx 2)
        plan_viajes.append((2, 2, random.randint(0, 20)))

    # Resto de viajes (~41), excluyendo Carolina Vega (idx 4 cond) y Roberto Núñez (idx 3)
    # como conductores recientes
    conductores_activos = [0, 1, 2]  # Ana, Luis, Beatriz
    for _ in range(40):
        idx_user = random.randint(0, len(usuarios) - 1)
        idx_cond = random.choice(conductores_activos)
        # Evitar duplicar coincidencias (no queremos más Juan-Ana)
        if (idx_user, idx_cond) in [(0, 0), (1, 1), (2, 2)]:
            continue
        plan_viajes.append((idx_user, idx_cond, random.randint(0, 25)))

    # 1 viaje viejo de Carolina (idx 4 cond): hace 60 días → caso 3 la marca inactiva
    plan_viajes.append((5, 4, 60))
    # Roberto (idx 3) no aparece nunca → también inactivo

    # 3. Ejecutar el plan
    viajes_creados: list[tuple[str, int, int]] = []  # (viaje_id, idx_user, idx_cond)
    ahora = datetime.now(UTC)
    for idx_user, idx_cond, dias_atras in plan_viajes:
        usuario = usuarios[idx_user]
        conductor = conductores[idx_cond]
        # Vehículo del conductor: tomar el primero suyo
        vehiculo = next(v for v in vehiculos if v[1] == conductor[0])
        duracion = random.randint(10, 45)
        distancia = round(random.uniform(2.0, 25.0), 1)
        fecha_fin = ahora - timedelta(days=dias_atras, hours=random.randint(0, 23))
        viaje_id = _crear_viaje_finalizado(
            usuario, conductor, vehiculo, fecha_fin, duracion, distancia,
        )
        viajes_creados.append((viaje_id, idx_user, idx_cond))
    logger.info(f"{len(viajes_creados)} viajes creados")

    # 4. Pagos con distribución 30/15/5 (TARJETA/EFECTIVO/BILLETERA)
    metodos = ["TARJETA"] * 30 + ["EFECTIVO"] * 15 + ["BILLETERA_VIRTUAL"] * 5
    random.shuffle(metodos)
    metodos = metodos[:len(viajes_creados)]
    for (viaje_id, _, _), metodo in zip(viajes_creados, metodos):
        monto = round(random.uniform(800, 5000), 2)
        _crear_pago(viaje_id, monto, metodo)
    logger.info(f"{len(viajes_creados)} pagos creados")

    # 5. Reseñas con distribución de ratings
    # Caso 7: queremos ~5 con rating 5, ~3 con rating 1, resto 3-4.
    ratings_pool = [5] * 5 + [1] * 3 + [4] * 20 + [3] * 22
    random.shuffle(ratings_pool)
    for i, (viaje_id, idx_user, idx_cond) in enumerate(viajes_creados):
        usuario = usuarios[idx_user]
        conductor = conductores[idx_cond]
        rating_user = ratings_pool[i % len(ratings_pool)]
        rating_cond = ratings_pool[(i + 7) % len(ratings_pool)]
        try:
            _crear_resena(viaje_id, usuario, conductor, "U_A_C", rating_user)
            _crear_resena(viaje_id, usuario, conductor, "C_A_U", rating_cond)
        except Exception as e:
            logger.warning(f"No se pudo reseñar viaje {viaje_id}: {e}")
    logger.info("Reseñas creadas")

    print("\nSeed completo. Resumen:")
    print(f"  Usuarios:     {len(usuarios)}")
    print(f"  Conductores:  {len(conductores)}")
    print(f"  Vehículos:    {len(vehiculos)}")
    print(f"  Viajes:       {len(viajes_creados)}")
    print(f"  Pagos:        {len(viajes_creados)}")
    print(f"  Reseñas:      ~{2 * len(viajes_creados)}")
    print("\nResultados esperados por caso de uso:")
    print("  Caso 1 (top 3):           Juan, María y Carlos")
    print("  Caso 2 (pago menos usado): BILLETERA_VIRTUAL")
    print("  Caso 3 (inactivos):       Carolina Vega + Roberto Núñez")
    print("  Caso 4 (tiempo promedio): ~22 min")
    print("  Caso 5 (coincidencias):   Juan-Ana(4), María-Luis(3), Carlos-Beatriz(2)")
    print("  Caso 6 (Toyota patente D): 3 vehículos")
    print("  Caso 7 (rating extremo):  ~10 reseñas (5 con rating=5, 3 con rating=1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Limpiar las bases antes del primer seed**

```bash
python -m scripts.reset_all_dbs
# Confirmar con BORRAR
python -m scripts.init_mongo
```

- [ ] **Step 3: Ejecutar el seed**

```bash
python -m scripts.seed_data
```
Expected: tarda 30-60 segundos (latencia cloud × ~250 escrituras). Termina con el resumen y los resultados esperados.

- [ ] **Step 4: Verificar el seed corriendo los 7 casos en la app**

```bash
python -m src.main
```

Ir a **Consultas** y correr los 7 casos. Verificar contra los "Resultados esperados" del seed:
- Caso 1: top 3 = Juan, María, Carlos (algún orden cercano).
- Caso 2: BILLETERA_VIRTUAL.
- Caso 3: Carolina Vega y Roberto Núñez en la lista.
- Caso 4: tiempo promedio cerca de 22 min (puede variar 18-27).
- Caso 5: 3 pares (Juan-Ana 4, María-Luis 3, Carlos-Beatriz 2).
- Caso 6: 3.
- Caso 7: ~10 reseñas (5 rating=5 y 3 rating=1 + posibles ratings ya en distribución).

- [ ] **Step 5: Si algún caso devuelve un resultado raro, ajustar las constantes en `seed_data.py` y volver a correr**

Por ejemplo: si el caso 6 da 2 en vez de 3, revisar las placas de los Toyota.

- [ ] **Step 6: Commit**

```bash
git add scripts/seed_data.py
git commit -m "agregar seed_data.py con dataset cubriendo los 7 casos de uso"
git push
```

---

## Sección 2 — Simulador GPS

### Task 2.1: Implementar `simulador_gps.py`

**Files:**
- Create: `scripts/simulador_gps.py`

> Este script genera GPS pings continuos en background mientras la app corre, simulando vehículos en movimiento. Es opcional para el demo pero refuerza visualmente el "Cassandra se está llenando ahora" en la presentación.

- [ ] **Step 1: Implementar**

```python
"""Simulador de GPS: reporta posiciones aleatorias para los vehiculos en background.

Uso standalone:
    python -m scripts.simulador_gps

Uso programatico (ej. desde el menu admin):
    from scripts.simulador_gps import iniciar_simulador, detener_simulador
    iniciar_simulador()
    ...
    detener_simulador()

El thread reporta una posicion aleatoria cerca de CABA para cada vehiculo
registrado en Postgres, cada INTERVALO_SEG segundos.
"""
import random
import signal
import sys
import threading
import time

from src.config import validate
from src.repositories import vehiculo_repo
from src.services import ubicacion_service
from src.utils.logger import logger

INTERVALO_SEG = 2.0
# Centro CABA y un margen aleatorio
CENTRO_LAT, CENTRO_LON = -34.6037, -58.3816
MARGEN = 0.15

_thread: threading.Thread | None = None
_stop_event = threading.Event()


def _loop(intervalo: float) -> None:
    """Loop del simulador, corre hasta que _stop_event se setea."""
    while not _stop_event.is_set():
        vehiculos = vehiculo_repo.listar_todos()
        if not vehiculos:
            logger.info("Simulador GPS: no hay vehículos registrados")
        for v in vehiculos:
            lat = CENTRO_LAT + random.uniform(-MARGEN, MARGEN)
            lon = CENTRO_LON + random.uniform(-MARGEN, MARGEN)
            try:
                ubicacion_service.reportar(v["id"], lat, lon)
            except Exception as e:
                logger.warning(f"Reporte GPS falló para {v['id']}: {e}")
        _stop_event.wait(intervalo)


def iniciar_simulador(intervalo: float = INTERVALO_SEG) -> None:
    """Inicia el simulador en un thread daemon. Idempotente."""
    global _thread
    if _thread is not None and _thread.is_alive():
        logger.info("Simulador GPS ya está corriendo")
        return
    _stop_event.clear()
    _thread = threading.Thread(target=_loop, args=(intervalo,), daemon=True)
    _thread.start()
    logger.info(f"Simulador GPS arrancado (intervalo={intervalo}s)")


def detener_simulador() -> None:
    """Frena el simulador limpiamente."""
    _stop_event.set()
    if _thread is not None:
        _thread.join(timeout=5)
    logger.info("Simulador GPS detenido")


def main() -> int:
    validate()
    iniciar_simulador()

    def _sigint(_signum, _frame):
        print("\nDeteniendo simulador...")
        detener_simulador()
        sys.exit(0)

    signal.signal(signal.SIGINT, _sigint)
    print("Simulador GPS corriendo. Ctrl-C para detener.")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Probarlo standalone (con seed cargado)**

```bash
python -m scripts.simulador_gps
```
Expected: queda corriendo. En otra terminal, verificar Cassandra:
- Astra UI → CQL Console → `SELECT COUNT(*) FROM ubicaciones_por_vehiculo;`
- El número debe crecer cada 2 segundos.

Detener con Ctrl-C.

- [ ] **Step 3: Agregar opción al `submenu_admin.py` para iniciar/detener el simulador desde la app**

Editar `src/menu/submenu_admin.py`. Agregar opciones 6 y 7 al menú:

```python
# Agregar a las opciones del menú impreso
print("6. Iniciar simulador GPS")
print("7. Detener simulador GPS")
print("8. Volver")  # antes era 6
```

Y en el dispatch del `if/elif`:

```python
elif op == "6":
    _iniciar_simulador()
elif op == "7":
    _detener_simulador()
elif op == "8":
    return
```

Y agregar las funciones:

```python
def _iniciar_simulador() -> None:
    from scripts.simulador_gps import iniciar_simulador
    iniciar_simulador()
    formato.exito("Simulador GPS arrancado en background (cada 2s).")
    formato.pausa()


def _detener_simulador() -> None:
    from scripts.simulador_gps import detener_simulador
    detener_simulador()
    formato.exito("Simulador GPS detenido.")
    formato.pausa()
```

- [ ] **Step 4: Probar desde la app**

```bash
python -m src.main
```
Ir a **Administración → 6. Iniciar simulador**. Volver al menú principal, esperar 10 segundos, verificar Astra UI. Detener con opción 7 cuando termine.

- [ ] **Step 5: Commit**

```bash
git add scripts/simulador_gps.py src/menu/submenu_admin.py
git commit -m "agregar simulador GPS con integracion en submenu admin"
git push
```

---

## Sección 3 — Demo automático (fallback)

### Task 3.1: Implementar `demo_automatico.py`

**Files:**
- Create: `scripts/demo_automatico.py`

> Mitigación de riesgo: si el demo en vivo se traba, este script ejecuta el guion sin interacción manual. Imprime cada paso narrado y hace pausas para que el profesor pueda ver lo que pasa en cada base.

- [ ] **Step 1: Implementar**

```python
"""Demo automatica del flujo completo del TP, sin interaccion manual.

Util como fallback durante la presentacion si el menu interactivo se traba.

Uso:
    python -m scripts.demo_automatico

Cada paso imprime una narracion y pausa unos segundos antes del siguiente,
asi el profesor puede mirar lo que pasa en las ventanas de las bases.
"""
import time
import uuid

from src.config import validate
from src.services import (
    auth_service, vehiculo_service,
    viaje_service, pago_service, resena_service, ubicacion_service,
)
from src.casos_uso import (
    caso_01_top_resenadores, caso_02_metodo_pago,
    caso_03_conductores_inactivos, caso_04_promedio_viajes,
    caso_05_coincidencias, caso_06_toyota_patente_d,
    caso_07_resenas_extremas,
)

PAUSA = 4  # segundos entre pasos para que el profesor mire


def _narrar(mensaje: str) -> None:
    print(f"\n{'-' * 60}")
    print(f"  {mensaje}")
    print(f"{'-' * 60}\n")
    time.sleep(PAUSA)


def main() -> int:
    validate()

    # Sufijos únicos para no colisionar con datos previos
    suf = uuid.uuid4().hex[:6]

    _narrar(f"Paso 1: Registrar usuario Diego (sufijo {suf})")
    print(f"  Email: diego_{suf}@m.com")
    uid = auth_service.register_usuario(f"diego_{suf}@m.com", "demo", f"Diego {suf}")
    print(f"  Usuario id: {uid}")
    print("  Verificar en Postgres (tabla usuario) y Neo4j (nodo Usuario).")

    _narrar(f"Paso 2: Registrar conductor Ana (sufijo {suf})")
    cid = auth_service.register_conductor(
        f"ana_{suf}@m.com", "demo", f"Ana {suf}", f"LIC-{suf}",
    )
    print(f"  Conductor id: {cid}")
    print("  Verificar en Postgres (tabla conductor) y Neo4j (nodo Conductor).")

    _narrar("Paso 3: Login del usuario → genera sesion Redis con TTL 600s")
    token = auth_service.login(f"diego_{suf}@m.com", "demo", "USUARIO")
    print(f"  Token: {token[:20]}...")
    print("  Verificar en Redis (clave session:...) y Mongo (login_history).")

    _narrar("Paso 4: Registrar un vehiculo Toyota Corolla con patente terminada en D")
    vid = vehiculo_service.registrar(
        cid, f"ZZZ{suf[:3].upper()}D", "Toyota", "Corolla", 2022, "Blanco", "sedan",
    )
    print(f"  Vehiculo id: {vid}")
    print("  Verificar en Postgres (tabla vehiculo) y Neo4j (Conductor)-[:MANEJA]->(Vehiculo).")

    _narrar("Paso 5: Solicitar un viaje (Mongo con snapshots desde Postgres)")
    origen = {"lat": -34.6037, "lon": -58.3816, "direccion": "Microcentro"}
    destino = {"lat": -34.5876, "lon": -58.3934, "direccion": "Recoleta"}
    viaje_id = viaje_service.solicitar(uid, cid, vid, origen, destino)
    print(f"  Viaje id: {viaje_id}")
    print("  Verificar en Mongo (coleccion viajes) — notar el snapshot del usuario y conductor.")

    _narrar("Paso 6: Iniciar el viaje y reportar 3 posiciones GPS")
    viaje_service.iniciar(viaje_id)
    for i, (lat, lon) in enumerate([(-34.6037, -58.3816), (-34.5955, -58.3870), (-34.5876, -58.3934)]):
        ubicacion_service.reportar(vid, lat, lon, viaje_id)
        print(f"  GPS #{i + 1}: ({lat}, {lon})")
        time.sleep(1)
    print("  Verificar en Cassandra (ubicaciones_por_vehiculo) y Redis (vehiculo:{id}:pos).")

    _narrar("Paso 7: Finalizar el viaje (toca 4 bases en simultaneo)")
    viaje_service.finalizar(viaje_id, distancia_km=8.5, duracion_min=22)
    print("  Mongo:     viaje.estado = FINALIZADO")
    print("  Cassandra: ultima_actividad_conductor + viajes_finalizados_por_dia")
    print("  Neo4j:     arista (:Usuario)-[:VIAJO_CON {cantidad_viajes: 1}]->(:Conductor)")
    print("  Redis:     cache:viajes_promedio invalidado")

    _narrar("Paso 8: Procesar pago con TARJETA por $2500")
    pago_service.procesar(viaje_id, 2500, 500, 1250, 750, 0, "TARJETA")
    print("  Verificar en Mongo (coleccion pagos).")

    _narrar("Paso 9: El usuario deja una resena con rating 5 (toca 4 bases)")
    resena_service.crear(
        viaje_id, "U_A_C", uid, f"Diego {suf}", cid, f"Ana {suf}",
        rating=5, comentario="Excelente viaje",
    )
    print("  Mongo:     coleccion resenas")
    print("  Postgres:  conductor.rating_promedio recalculado")
    print("  Neo4j:     nodo Conductor con rating actualizado")
    print("  Redis:     cache:top3_resenadores invalidado")

    _narrar("Paso 10: Logout — borra sesion en Redis y audita en Mongo")
    auth_service.logout(token)
    print("  Verificar en Redis (clave session ya no existe).")

    _narrar("Ahora ejecuto los 7 casos de uso del enunciado:")

    print("\nCaso 1 — Top 3 resenadores (Mongo aggregate + cache Redis):")
    for item in caso_01_top_resenadores.ejecutar():
        print(f"  {item['nombre']:30s} {item['cantidad']:>5} resenas")

    print("\nCaso 2 — Metodo de pago menos usado (Mongo):")
    print(f"  → {caso_02_metodo_pago.ejecutar()}")

    print("\nCaso 3 — Conductores inactivos ultimo mes (Cassandra + Postgres):")
    for c in caso_03_conductores_inactivos.ejecutar():
        print(f"  {c['nombre']:30s} ({c['email']})")

    print("\nCaso 4 — Tiempo promedio de viajes (Cassandra + cache Redis):")
    print(f"  → {caso_04_promedio_viajes.ejecutar():.2f} min")

    print("\nCaso 5 — Coincidencias pasajero-conductor en >1 viaje (Neo4j):")
    for c in caso_05_coincidencias.ejecutar():
        print(f"  {c['pasajero']:20s} ↔ {c['conductor']:20s} ({c['viajes']} viajes)")

    print("\nCaso 6 — Toyota con patente terminada en D (Neo4j):")
    print(f"  → {caso_06_toyota_patente_d.ejecutar()} vehiculos")

    print("\nCaso 7 — Resenas con rating 5 o <2 (Mongo):")
    for r in caso_07_resenas_extremas.ejecutar()[:5]:
        print(f"  rating {r['rating']} — {r['autor']['nombre']:20s} → {r['destinatario']['nombre']:20s}")

    print("\n" + "=" * 60)
    print("  FIN DE LA DEMO AUTOMATICA")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Ejecutarlo con datos del seed**

```bash
python -m scripts.demo_automatico
```
Expected: la demo corre paso a paso (~1 min total), narrando cada acción y mostrando los 7 casos al final.

- [ ] **Step 3: Commit**

```bash
git add scripts/demo_automatico.py
git commit -m "agregar demo_automatico.py como fallback no-interactivo de la presentacion"
git push
```

---

## Sección 4 — Slides

### Task 4.1: Armar las 8 slides

**Files:**
- Create: `docs/slides/presentacion.pptx` (manualmente, en PowerPoint o Google Slides)
- Create: `docs/slides/presentacion.pdf` (export)

> Esta tarea es **manual** — no hay código. Seguir el guion ya definido en `docs/presentacion.md §5`.

- [ ] **Step 1: Crear carpeta**

```bash
mkdir -p docs/slides
```

- [ ] **Step 2: Crear el archivo .pptx con 8 slides**

Usar la estructura ya documentada en `docs/presentacion.md §5`:

| # | Slide | Contenido |
|---|---|---|
| 1 | Portada | Título, integrantes, cátedra, fecha |
| 2 | Contexto | Qué es el TP + requisito clave del profesor (cita textual) |
| 3 | DER original + cambios | Captura del Uber.pdf + tabla con E1-E5 |
| 4 | Stack tecnológico | Las 5 bases con logos + tipo + hosting cloud |
| 5 | Arquitectura | Diagrama "Postgres mínimo + NoSQL operativas" (de diseno.md §3) |
| 6 | Mapeo casos → base | Tabla con los 7 casos (de diseno.md §5) |
| 7 | Flujo "finalizar viaje" | Diagrama del flujo cruzando 4 bases (de diseno.md §6.5) |
| 8 | Cierre | Aprendizajes + preguntas |

**Reglas:**
- Mucho diagrama, poco texto.
- Cada slide se entiende en 10 segundos.
- Usar el DER original del PDF para la slide 3 (screenshot directo).
- Para el diagrama de la slide 7, capturar el ASCII de `diseno.md §6.5` o redibujarlo en PowerPoint.

- [ ] **Step 3: Exportar a PDF como backup**

En PowerPoint: Archivo → Exportar → PDF. Guardar como `docs/slides/presentacion.pdf`.

- [ ] **Step 4: Commit ambos archivos**

> **Atención al `.gitignore`:** la regla `*.zip` no afecta `.pptx` ni `.pdf`. Verificar con `git status` que aparezcan.

```bash
git add docs/slides/
git commit -m "agregar slides de la presentacion (pptx + pdf)"
git push
```

---

## Sección 5 — Ensayo del demo

### Task 5.1: Primer ensayo completo

> Este es un **ensayo manual** del guion completo de `docs/presentacion.md §2`. El objetivo es detectar fricciones, cosas que tardan demasiado, o puntos donde la narración no fluye.

- [ ] **Step 1: Setup previo al ensayo**

- [ ] Limpiar todas las bases: `python -m scripts.reset_all_dbs` → `BORRAR`.
- [ ] Reinicializar índices: `python -m scripts.init_mongo`.
- [ ] Cargar el seed: `python -m scripts.seed_data`.
- [ ] Abrir las 5 ventanas de clientes de DB (pgAdmin, Compass, Astra UI, Neo4j Browser, RedisInsight).
- [ ] Tener `python -m src.main` listo para arrancar.
- [ ] Cronómetro / temporizador encendido.

- [ ] **Step 2: Correr el guion de `presentacion.md §2.2` completo**

Hacer los 9 pasos (`G1` a `G9`) hablando en voz alta como si el profesor estuviera presente. Cronometrar cada paso.

Apuntar:
- ¿Algún paso tarda más de 1 min? → reescribir o automatizar.
- ¿Algún cliente de DB no refresca rápido? → buscar el botón de refresh manual.
- ¿La narración suena natural? → ajustar el texto si no.
- ¿Las queries en los clientes están preparadas o las tipeás cada vez? → guardarlas en archivos `.cql`, `.cypher`, etc. en `docs/slides/queries_demo/`.

- [ ] **Step 3: Correr los 7 casos de uso (presentacion.md §3)**

Para cada caso, decir el caso → ejecutar opción del menú → mostrar resultado → abrir el cliente de DB y mostrar la query que se usó.

- [ ] **Step 4: Anotar problemas encontrados**

Crear `docs/slides/notas_ensayo.md` con los hallazgos del primer ensayo.

- [ ] **Step 5: Commit las correcciones**

```bash
git add docs/slides/queries_demo/ docs/slides/notas_ensayo.md
git commit -m "agregar queries listas para el demo + notas del primer ensayo"
git push
```

---

### Task 5.2: Segundo ensayo (refinado)

- [ ] **Step 1: Resetear y resem-seedear**

```bash
python -m scripts.reset_all_dbs   # BORRAR
python -m scripts.init_mongo
python -m scripts.seed_data
```

- [ ] **Step 2: Correr el guion completo nuevamente**

Esta vez sin pausar, **cronometrar el total**. Objetivo: ≤17 minutos para demo + 7 casos.

- [ ] **Step 3: Si el tiempo está bien, marcar ensayo OK**

Agregar a `docs/slides/notas_ensayo.md`:
```
- [x] Ensayo 2 completo en X minutos
```

- [ ] **Step 4: Commit**

```bash
git add docs/slides/notas_ensayo.md
git commit -m "marcar segundo ensayo del demo como completado"
git push
```

---

## Sección 6 — Checklist del día previo

### Task 6.1: Pre-flight check 24 hs antes de la presentación

> Esta tarea es **el día anterior** a la presentación. Asegura que nada falla en vivo.

- [ ] **Step 1: Verificar conexiones a las 5 bases**

```bash
python -m scripts.check_connections
```
Expected: 5 OK.

- [ ] **Step 2: Reset + seed + verificación de los 7 casos**

```bash
python -m scripts.reset_all_dbs   # BORRAR
python -m scripts.init_mongo
python -m scripts.seed_data
python -m src.main
# Manualmente: ir a Consultas y correr los 7 casos. Verificar que ninguno devuelve vacío.
```

- [ ] **Step 3: Tener accesible offline `docs/justificacion-der.md`**

```bash
# Opcion 1: imprimirlo
# Opcion 2: tenerlo abierto en una pestana del navegador
```

- [ ] **Step 4: Slides en PPTX y PDF a mano**

- [ ] `docs/slides/presentacion.pptx` cargada en la laptop.
- [ ] `docs/slides/presentacion.pdf` también, como fallback.
- [ ] Si vas a presentar desde Google Slides, tener un link compartido.

- [ ] **Step 5: Backup de internet**

- [ ] Verificar que tu celular tiene datos para hacer hotspot si falla el WiFi de la facu.

- [ ] **Step 6: Cargar y probar el equipo físico**

- [ ] Cargador de la laptop.
- [ ] Mouse externo (opcional).
- [ ] Adaptador HDMI/VGA según el proyector de la facu.
- [ ] Agua / café.

- [ ] **Step 7: Practicar la apertura una vez más (sin la demo)**

Solo los primeros 5 min (apertura + DER + stack). Es el momento donde más nervios pueden traicionar.

- [ ] **Step 8: Marcar Fases 7 y 8 completas en `docs/tareas.md`**

Marcar todas las sub-fases de:
- Fase 7 (seed + simulador + verificación).
- Fase 8 (slides + ensayos).

- [ ] **Step 9: Nota final de seguimiento**

Agregar a `docs/tareas.md`:
```
- 2026-MM-DD: Plan 05 completo. Seed corriendo con dataset que cubre los 7
  casos. Simulador GPS funcional. Demo automatico de fallback. Slides listas.
  Ensayados 2 veces. LISTOS PARA LA PRESENTACION.
```

- [ ] **Step 10: Commit final del proyecto**

```bash
git add docs/tareas.md
git commit -m "marcar Fases 7 y 8 completadas — proyecto listo para presentacion"
git push
```

---

## Cierre del plan y del proyecto

Estado esperado al finalizar:

```
✅ scripts/seed_data.py — 50 viajes, 50 pagos, ~100 reseñas, distribución para los 7 casos
✅ scripts/simulador_gps.py — thread background reportando GPS cada 2s
✅ scripts/demo_automatico.py — fallback no-interactivo del guion
✅ docs/slides/presentacion.pptx + presentacion.pdf — 8 slides listas
✅ docs/slides/queries_demo/ — queries CQL/Cypher/SQL pre-cargadas
✅ Ensayos: 2 corridas completas del guion ≤17 min cada una
✅ Todo versionado en GitHub
✅ Checklist del día previo verificado
✅ Carolina Vega y Roberto Núñez son inactivos
✅ BILLETERA_VIRTUAL es el método menos usado
✅ Juan, María, Carlos son top 3 reseñadores
✅ 3 Toyota con patente terminada en D
```

**Estado final del repo después del proyecto completo:**

```
TP-Datos2-Uber/
├── CLAUDE.md
├── README.md
├── .gitignore
├── requirements.txt
├── .env.example
├── docs/
│   ├── diseno.md             ← diseño técnico completo
│   ├── justificacion-der.md  ← para el profesor
│   ├── decisiones.md         ← 12 ADRs
│   ├── presentacion.md       ← plan de defensa
│   ├── tareas.md             ← roadmap 100% completado
│   ├── plan-01-foundation.md
│   ├── plan-02-repositories.md
│   ├── plan-03-services.md
│   ├── plan-04-use-cases-menu.md
│   ├── plan-05-seeding-presentacion.md   ← este plan
│   └── slides/
│       ├── presentacion.pptx
│       ├── presentacion.pdf
│       ├── notas_ensayo.md
│       └── queries_demo/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── db/                   (5 módulos)
│   ├── repositories/         (11 módulos)
│   ├── services/             (7 módulos)
│   ├── casos_uso/            (7 módulos)
│   ├── menu/                 (5 módulos)
│   └── utils/                (logger, errors, outbox)
├── scripts/
│   ├── init_postgres.sql
│   ├── init_mongo.py
│   ├── init_cassandra.cql
│   ├── init_neo4j.cypher
│   ├── check_connections.py
│   ├── reset_all_dbs.py
│   ├── seed_data.py
│   ├── simulador_gps.py
│   └── demo_automatico.py
└── tests/
    ├── repositories/         (~84 tests)
    ├── services/             (~35 tests)
    ├── casos_uso/            (~26 tests)
    └── menu/                 (~6 tests)
```

**Total: ~150 tests verdes + 5 planes documentados + dataset realista + slides + ensayos = TP listo para presentar.**

---

## Lecciones aprendidas (cierre del brainstorming completo)

Cuando termine el proyecto entero, agregar al final de `docs/presentacion.md §8` (o a un `docs/lecciones-aprendidas.md` nuevo) las observaciones empíricas que surjan, por ejemplo:

- Qué tan caro/barato fue cada servicio cloud después de un mes.
- Qué patrones de write-through funcionaron mejor que otros.
- Qué casos de uso fueron triviales y cuáles requirieron reformular.
- Qué sugerencias darían a otro grupo que hace este TP el próximo cuatrimestre.

Este último documento sirve como retrospectiva y aporta valor al curriculum personal del equipo.
