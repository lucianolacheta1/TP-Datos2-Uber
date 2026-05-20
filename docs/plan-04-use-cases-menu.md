# Plan 04 — Casos de Uso + Menú de Consola

> **Para agentes:** REQUIRED SUB-SKILL: Usar `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans`. Los pasos usan checkboxes `- [ ]` para tracking.

**Goal:** Implementar los 7 casos de uso del enunciado en `src/casos_uso/` y el menú de consola en `src/menu/` para que la aplicación sea **demostrable end-to-end** corriendo `python -m src.main`.

**Architecture:** Los casos de uso son thin layers sobre los repositories que opcionalmente cachean en Redis y enriquecen resultados desde Postgres. El menú está dividido por responsabilidad (cuentas / operación / consultas / admin), cada submenú usa los services del Plan 03 y los casos de uso. El entry point `src/main.py` arma todo.

**Tech Stack:** Mismo que Planes 01-03. Sin librerías nuevas.

---

## Pre-requisitos

**Planes 01, 02 y 03 completos.** Esto significa:

- ✅ 5 bases cloud + esquemas.
- ✅ 11 repositories con tests verdes.
- ✅ 7 services con tests verdes.
- ✅ `pytest tests/` corre verde de punta a punta.

---

## Alcance de este plan

Cubre las **Fases 5-6** de `docs/tareas.md`: casos de uso + menú.

**NO incluye:**
- Seed de datos (Plan 05).
- Slides/preparación de la presentación (Plan 05).

**Entregables al finalizar:**

- ✅ 7 módulos en `src/casos_uso/`, uno por caso del enunciado.
- ✅ Tests para cada caso de uso (con datos de prueba inline).
- ✅ 4 submenús en `src/menu/` (cuentas, operación, consultas, admin).
- ✅ `src/menu/main_menu.py` que orquesta los submenús.
- ✅ `src/main.py` como entry point ejecutable: `python -m src.main`.
- ✅ Demo manual end-to-end: registrar → login → solicitar viaje → finalizar → reseña → consulta caso de uso → ver resultado.

---

## Diseño de los casos de uso

### Convenciones

1. **Una función pública** por caso: `ejecutar(...) → resultado`.
2. **Sin lógica del menú** dentro del caso de uso (el formateo y el `print` va en el submenú).
3. **Cachean en Redis** los que tienen aggregations pesadas (casos 1 y 4).
4. **Enriquecen con nombres** desde Postgres cuando el resultado solo tiene IDs (caso 1).
5. **Devuelven datos estructurados** (list/dict/scalar), no strings formateados.

### Tabla de mapeo

| Caso | Función | Base principal | Cache |
|---|---|---|---|
| 1 | `caso_01_top_resenadores.ejecutar()` | Mongo | ✅ Redis 5 min |
| 2 | `caso_02_metodo_pago.ejecutar()` | Mongo | ❌ |
| 3 | `caso_03_conductores_inactivos.ejecutar()` | Cassandra + Postgres | ❌ |
| 4 | `caso_04_promedio_viajes.ejecutar()` | Cassandra | ✅ Redis 5 min |
| 5 | `caso_05_coincidencias.ejecutar(min_viajes=2)` | Neo4j | ❌ |
| 6 | `caso_06_toyota_patente_d.ejecutar(marca='Toyota', sufijo='D')` | Neo4j | ❌ |
| 7 | `caso_07_resenas_extremas.ejecutar()` | Mongo | ❌ |

---

## File Structure

Archivos que se crean en este plan:

```
src/
├── main.py                              ← entry point
├── casos_uso/
│   ├── __init__.py
│   ├── caso_01_top_resenadores.py
│   ├── caso_02_metodo_pago.py
│   ├── caso_03_conductores_inactivos.py
│   ├── caso_04_promedio_viajes.py
│   ├── caso_05_coincidencias.py
│   ├── caso_06_toyota_patente_d.py
│   └── caso_07_resenas_extremas.py
└── menu/
    ├── __init__.py
    ├── main_menu.py
    ├── submenu_cuentas.py
    ├── submenu_operacion.py
    ├── submenu_consultas.py
    ├── submenu_admin.py
    └── formato.py                       ← helpers de formato/print

tests/casos_uso/
├── __init__.py
├── test_caso_01_top_resenadores.py
├── test_caso_02_metodo_pago.py
├── test_caso_03_conductores_inactivos.py
├── test_caso_04_promedio_viajes.py
├── test_caso_05_coincidencias.py
├── test_caso_06_toyota_patente_d.py
└── test_caso_07_resenas_extremas.py

tests/menu/
├── __init__.py
└── test_imports.py                      ← tests basicos de que los modulos cargan
```

---

## Sección 1 — Casos de uso (TDD)

### Task 1.1: Setup de carpetas

- [ ] **Step 1: Crear las carpetas**

```bash
mkdir -p src/casos_uso src/menu tests/casos_uso tests/menu
touch src/casos_uso/__init__.py src/menu/__init__.py
touch tests/casos_uso/__init__.py tests/menu/__init__.py
```

- [ ] **Step 2: Commit**

```bash
git add src/casos_uso/ src/menu/ tests/casos_uso/ tests/menu/
git commit -m "agregar esqueleto de carpetas para casos_uso y menu"
git push
```

---

### Task 1.2: Caso 1 — Top 3 reseñadores

**Files:**
- Create: `src/casos_uso/caso_01_top_resenadores.py`
- Create: `tests/casos_uso/test_caso_01_top_resenadores.py`

- [ ] **Step 1: Test**

Crear `tests/casos_uso/test_caso_01_top_resenadores.py`:
```python
"""Tests del caso de uso 1: top 3 reseñadores (Mongo + Redis cache)."""
from datetime import datetime, UTC


def _crear_resenas(autor_id: str, cantidad: int):
    """Helper: inserta N reseñas U_A_C de un autor en Mongo."""
    from src.repositories import resena_repo
    for _ in range(cantidad):
        resena_repo.crear({
            "viaje_id": "v",
            "tipo": "U_A_C",
            "autor":        {"id": autor_id, "nombre": f"Autor {autor_id}"},
            "destinatario": {"id": "c1", "nombre": "Conductor"},
            "rating": 5,
            "comentario": "ok",
            "timestamp": datetime.now(UTC),
        })


def test_devuelve_top_3_ordenado_desc(postgres_clean, mongo_clean, redis_clean):
    from src.repositories import usuario_repo
    from src.casos_uso import caso_01_top_resenadores

    # 3 usuarios reales en Postgres para enriquecer
    a_id = usuario_repo.crear("a@m.com", "h", "Andrea")
    b_id = usuario_repo.crear("b@m.com", "h", "Beto")
    c_id = usuario_repo.crear("c@m.com", "h", "Carla")
    d_id = usuario_repo.crear("d@m.com", "h", "Diana")
    _crear_resenas(a_id, 5)
    _crear_resenas(b_id, 3)
    _crear_resenas(c_id, 2)
    _crear_resenas(d_id, 1)

    top = caso_01_top_resenadores.ejecutar()
    assert len(top) == 3
    assert [t["autor_id"] for t in top] == [a_id, b_id, c_id]
    assert top[0]["cantidad"] == 5
    assert top[0]["nombre"] == "Andrea"


def test_cachea_en_redis(postgres_clean, mongo_clean, redis_clean):
    from src.repositories import usuario_repo, cache_repo
    from src.casos_uso import caso_01_top_resenadores

    uid = usuario_repo.crear("x@m.com", "h", "X")
    _crear_resenas(uid, 1)
    caso_01_top_resenadores.ejecutar()

    cached = cache_repo.get_cache("top3_resenadores")
    assert cached is not None
    assert cached[0]["autor_id"] == uid


def test_segunda_llamada_usa_cache(postgres_clean, mongo_clean, redis_clean):
    """Si hay cache, no toca Mongo."""
    from src.repositories import cache_repo
    from src.casos_uso import caso_01_top_resenadores

    cache_repo.set_cache("top3_resenadores", [{"autor_id": "FAKE", "cantidad": 99, "nombre": "Fake"}])
    top = caso_01_top_resenadores.ejecutar()
    # Devuelve el cache, no datos reales (que están vacíos)
    assert top[0]["autor_id"] == "FAKE"
    assert top[0]["cantidad"] == 99


def test_sin_resenas_devuelve_lista_vacia(postgres_clean, mongo_clean, redis_clean):
    from src.casos_uso import caso_01_top_resenadores
    assert caso_01_top_resenadores.ejecutar() == []
```

- [ ] **Step 2: Tests fallan**

```bash
pytest tests/casos_uso/test_caso_01_top_resenadores.py -v
```
Expected: 4 FAIL.

- [ ] **Step 3: Implementar**

Crear `src/casos_uso/caso_01_top_resenadores.py`:
```python
"""Caso de uso 1: top 3 usuarios con más reseñas.

Base principal: Mongo (resenas) + enriquecimiento desde Postgres (nombres).
Cache: Redis con TTL 5 min.
"""
from src.repositories import resena_repo, cache_repo, usuario_repo

CACHE_KEY = "top3_resenadores"
CACHE_TTL = 300  # 5 min


def ejecutar() -> list[dict]:
    """Devuelve top 3 reseñadores, enriquecido con nombre desde Postgres.

    Formato: [{autor_id, cantidad, nombre}, ...]
    """
    # 1. Cache hit?
    cached = cache_repo.get_cache(CACHE_KEY)
    if cached is not None:
        return cached

    # 2. Aggregation en Mongo
    top = resena_repo.top_autores(n=3, tipo="U_A_C")

    # 3. Enriquecer con nombre desde Postgres
    for item in top:
        user = usuario_repo.get_by_id(item["autor_id"])
        item["nombre"] = user["nombre"] if user else "(desconocido)"

    # 4. Cachear
    cache_repo.set_cache(CACHE_KEY, top, ttl_seconds=CACHE_TTL)
    return top
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/casos_uso/test_caso_01_top_resenadores.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/casos_uso/caso_01_top_resenadores.py tests/casos_uso/test_caso_01_top_resenadores.py
git commit -m "agregar caso de uso 1: top 3 resenadores con cache Redis (4 tests)"
git push
```

---

### Task 1.3: Caso 2 — Método de pago menos usado

**Files:**
- Create: `src/casos_uso/caso_02_metodo_pago.py`
- Create: `tests/casos_uso/test_caso_02_metodo_pago.py`

- [ ] **Step 1: Test**

```python
"""Tests del caso de uso 2: método de pago menos usado (Mongo)."""
from datetime import datetime, UTC


def _crear_pago(metodo: str):
    from src.repositories import pago_repo
    pago_repo.crear({
        "viaje_id": "v",
        "monto_total": 1000, "tarifa_base": 500,
        "tarifa_distancia": 300, "tarifa_tiempo": 200, "cargos_extra": 0,
        "metodo_pago": metodo, "estado": "APROBADO",
        "timestamp": datetime.now(UTC),
    })


def test_devuelve_metodo_con_menos_pagos(mongo_clean):
    from src.casos_uso import caso_02_metodo_pago

    for _ in range(5):
        _crear_pago("TARJETA")
    for _ in range(2):
        _crear_pago("EFECTIVO")
    _crear_pago("BILLETERA_VIRTUAL")
    assert caso_02_metodo_pago.ejecutar() == "BILLETERA_VIRTUAL"


def test_sin_pagos_devuelve_none(mongo_clean):
    from src.casos_uso import caso_02_metodo_pago
    assert caso_02_metodo_pago.ejecutar() is None
```

- [ ] **Step 2: Tests fallan**

```bash
pytest tests/casos_uso/test_caso_02_metodo_pago.py -v
```

- [ ] **Step 3: Implementar**

```python
"""Caso de uso 2: método de pago menos utilizado en la plataforma.

Base: Mongo (agregación sobre pagos).
"""
from src.repositories import pago_repo


def ejecutar() -> str | None:
    """Devuelve el nombre del método de pago menos usado, o None si no hay pagos."""
    return pago_repo.metodo_menos_usado()
```

- [ ] **Step 4: Tests pasan**

```bash
pytest tests/casos_uso/test_caso_02_metodo_pago.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add src/casos_uso/caso_02_metodo_pago.py tests/casos_uso/test_caso_02_metodo_pago.py
git commit -m "agregar caso de uso 2: metodo de pago menos usado (2 tests)"
git push
```

---

### Task 1.4: Caso 3 — Conductores inactivos último mes

**Files:**
- Create: `src/casos_uso/caso_03_conductores_inactivos.py`
- Create: `tests/casos_uso/test_caso_03_conductores_inactivos.py`

- [ ] **Step 1: Test**

```python
"""Tests del caso de uso 3: conductores inactivos último mes (Cassandra + Postgres)."""
import uuid
from datetime import datetime, UTC, timedelta


def test_inactivo_es_quien_no_tuvo_viajes_en_30_dias(postgres_clean, cassandra_clean):
    from src.repositories import conductor_repo, actividad_repo
    from src.casos_uso import caso_03_conductores_inactivos

    activo_id = conductor_repo.crear("a@m.com", "h", "Activo", "LIC-A")
    inactivo_id = conductor_repo.crear("i@m.com", "h", "Inactivo", "LIC-I")
    nunca_id = conductor_repo.crear("n@m.com", "h", "Nunca", "LIC-N")

    ahora = datetime.now(UTC)
    actividad_repo.upsert_ultima(uuid.UUID(activo_id), ahora, uuid.uuid4())
    actividad_repo.upsert_ultima(uuid.UUID(inactivo_id), ahora - timedelta(days=60), uuid.uuid4())
    # nunca_id no tiene actividad

    inactivos = caso_03_conductores_inactivos.ejecutar()
    ids = [c["id"] for c in inactivos]
    assert activo_id not in ids
    assert inactivo_id in ids
    assert nunca_id in ids


def test_sin_conductores_devuelve_lista_vacia(postgres_clean, cassandra_clean):
    from src.casos_uso import caso_03_conductores_inactivos
    assert caso_03_conductores_inactivos.ejecutar() == []
```

- [ ] **Step 2: Tests fallan**

- [ ] **Step 3: Implementar**

```python
"""Caso de uso 3: conductores inactivos en los últimos 30 días.

Inactivo = conductor activo en Postgres que NO tiene viaje finalizado
en los últimos 30 días (Cassandra).
"""
from datetime import datetime, UTC, timedelta

from src.repositories import actividad_repo, conductor_repo


DIAS_INACTIVIDAD = 30


def ejecutar() -> list[dict]:
    """Devuelve la lista de conductores activos que no tuvieron viajes recientes."""
    limite = datetime.now(UTC) - timedelta(days=DIAS_INACTIVIDAD)
    ids_con_actividad_reciente = set(
        str(cid) for cid in actividad_repo.conductores_activos_desde(limite)
    )

    todos_activos = conductor_repo.listar_activos()
    inactivos = [c for c in todos_activos if c["id"] not in ids_con_actividad_reciente]
    return inactivos
```

- [ ] **Step 4: Tests pasan**

```bash
pytest tests/casos_uso/test_caso_03_conductores_inactivos.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add src/casos_uso/caso_03_conductores_inactivos.py tests/casos_uso/test_caso_03_conductores_inactivos.py
git commit -m "agregar caso de uso 3: conductores inactivos ultimo mes (2 tests)"
git push
```

---

### Task 1.5: Caso 4 — Tiempo promedio de viajes

**Files:**
- Create: `src/casos_uso/caso_04_promedio_viajes.py`
- Create: `tests/casos_uso/test_caso_04_promedio_viajes.py`

- [ ] **Step 1: Test**

```python
"""Tests del caso de uso 4: tiempo promedio de viajes (Cassandra + Redis cache)."""
import pytest
import uuid
from datetime import date


def test_promedio_calculado_correctamente(cassandra_clean, redis_clean):
    from src.repositories import actividad_repo
    from src.casos_uso import caso_04_promedio_viajes

    hoy = date.today()
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 10, 5.0)
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 30, 10.0)
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 50, 15.0)

    assert caso_04_promedio_viajes.ejecutar() == pytest.approx(30)


def test_cachea_resultado(cassandra_clean, redis_clean):
    from src.repositories import actividad_repo, cache_repo
    from src.casos_uso import caso_04_promedio_viajes

    actividad_repo.insertar_viaje_finalizado(date.today(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 20, 5.0)
    caso_04_promedio_viajes.ejecutar()
    assert cache_repo.get_cache("viajes_promedio") == 20


def test_segunda_llamada_usa_cache(cassandra_clean, redis_clean):
    from src.repositories import cache_repo
    from src.casos_uso import caso_04_promedio_viajes

    cache_repo.set_cache("viajes_promedio", 99.5)
    assert caso_04_promedio_viajes.ejecutar() == 99.5


def test_sin_viajes_devuelve_cero(cassandra_clean, redis_clean):
    from src.casos_uso import caso_04_promedio_viajes
    assert caso_04_promedio_viajes.ejecutar() == 0
```

- [ ] **Step 2: Tests fallan**

- [ ] **Step 3: Implementar**

```python
"""Caso de uso 4: tiempo promedio de viajes (en minutos).

Base: Cassandra (viajes_finalizados_por_dia).
Cache: Redis con TTL 5 min.
"""
from src.repositories import actividad_repo, cache_repo

CACHE_KEY = "viajes_promedio"
CACHE_TTL = 300  # 5 min


def ejecutar() -> float:
    """Devuelve el promedio de duración (min) de viajes finalizados."""
    cached = cache_repo.get_cache(CACHE_KEY)
    if cached is not None:
        return cached

    promedio = actividad_repo.promedio_duracion()
    cache_repo.set_cache(CACHE_KEY, promedio, ttl_seconds=CACHE_TTL)
    return promedio
```

- [ ] **Step 4: Tests pasan**

```bash
pytest tests/casos_uso/test_caso_04_promedio_viajes.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/casos_uso/caso_04_promedio_viajes.py tests/casos_uso/test_caso_04_promedio_viajes.py
git commit -m "agregar caso de uso 4: tiempo promedio de viajes con cache Redis (4 tests)"
git push
```

---

### Task 1.6: Caso 5 — Coincidencias usuario-conductor

**Files:**
- Create: `src/casos_uso/caso_05_coincidencias.py`
- Create: `tests/casos_uso/test_caso_05_coincidencias.py`

- [ ] **Step 1: Test**

```python
"""Tests del caso de uso 5: coincidencias usuario-conductor (Neo4j)."""


def test_devuelve_parejas_con_mas_de_1_viaje(neo4j_clean):
    from src.repositories import grafo_repo
    from src.casos_uso import caso_05_coincidencias

    # Crear nodos
    grafo_repo.crear_usuario("U1", "U1", "u1@m.com")
    grafo_repo.crear_usuario("U2", "U2", "u2@m.com")
    grafo_repo.crear_conductor("C1", "C1", "c1@m.com")
    grafo_repo.crear_conductor("C2", "C2", "c2@m.com")

    # U1-C1: 3 viajes
    for _ in range(3):
        grafo_repo.incrementar_viajo_con("U1", "C1")
    # U2-C2: 1 viaje (NO debe aparecer)
    grafo_repo.incrementar_viajo_con("U2", "C2")

    coincidencias = caso_05_coincidencias.ejecutar()
    pares = {(c["pasajero_id"], c["conductor_id"]) for c in coincidencias}
    assert ("U1", "C1") in pares
    assert ("U2", "C2") not in pares


def test_acepta_min_viajes_parametro(neo4j_clean):
    from src.repositories import grafo_repo
    from src.casos_uso import caso_05_coincidencias

    grafo_repo.crear_usuario("U", "U", "u@m.com")
    grafo_repo.crear_conductor("C", "C", "c@m.com")
    for _ in range(5):
        grafo_repo.incrementar_viajo_con("U", "C")

    assert len(caso_05_coincidencias.ejecutar(min_viajes=3)) == 1
    assert len(caso_05_coincidencias.ejecutar(min_viajes=10)) == 0


def test_sin_aristas_devuelve_lista_vacia(neo4j_clean):
    from src.casos_uso import caso_05_coincidencias
    assert caso_05_coincidencias.ejecutar() == []
```

- [ ] **Step 2: Tests fallan**

- [ ] **Step 3: Implementar**

```python
"""Caso de uso 5: pasajeros y conductores que coincidieron en >1 viaje.

Base: Neo4j (relación VIAJO_CON con propiedad cantidad_viajes).
"""
from src.repositories import grafo_repo


def ejecutar(min_viajes: int = 2) -> list[dict]:
    """Devuelve parejas (pasajero, conductor) que coincidieron en N o más viajes.

    Formato: [{pasajero_id, pasajero, conductor_id, conductor, viajes}, ...]
    """
    return grafo_repo.coincidencias(min_viajes=min_viajes)
```

- [ ] **Step 4: Tests pasan**

```bash
pytest tests/casos_uso/test_caso_05_coincidencias.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/casos_uso/caso_05_coincidencias.py tests/casos_uso/test_caso_05_coincidencias.py
git commit -m "agregar caso de uso 5: coincidencias usuario-conductor en Neo4j (3 tests)"
git push
```

---

### Task 1.7: Caso 6 — Autos Toyota con patente terminada en "D"

**Files:**
- Create: `src/casos_uso/caso_06_toyota_patente_d.py`
- Create: `tests/casos_uso/test_caso_06_toyota_patente_d.py`

- [ ] **Step 1: Test**

```python
"""Tests del caso de uso 6: Toyota patente terminada en D (Neo4j)."""


def test_cuenta_solo_toyota_con_patente_terminada_en_D(neo4j_clean):
    from src.repositories import grafo_repo
    from src.casos_uso import caso_06_toyota_patente_d

    grafo_repo.crear_vehiculo("V1", "ABC123D", "Toyota", "Corolla")
    grafo_repo.crear_vehiculo("V2", "XYZ888D", "Toyota", "Hilux")
    grafo_repo.crear_vehiculo("V3", "AAA111A", "Toyota", "Etios")     # no termina en D
    grafo_repo.crear_vehiculo("V4", "BBB222D", "Honda", "Civic")      # no Toyota

    assert caso_06_toyota_patente_d.ejecutar() == 2


def test_acepta_parametros_marca_y_sufijo(neo4j_clean):
    from src.repositories import grafo_repo
    from src.casos_uso import caso_06_toyota_patente_d

    grafo_repo.crear_vehiculo("V1", "AAA111A", "Honda", "Civic")
    grafo_repo.crear_vehiculo("V2", "BBB222A", "Honda", "Fit")
    assert caso_06_toyota_patente_d.ejecutar(marca="Honda", sufijo="A") == 2


def test_sin_vehiculos_devuelve_cero(neo4j_clean):
    from src.casos_uso import caso_06_toyota_patente_d
    assert caso_06_toyota_patente_d.ejecutar() == 0
```

- [ ] **Step 2: Tests fallan**

- [ ] **Step 3: Implementar**

```python
"""Caso de uso 6: cantidad de autos de cierta marca con patente terminada en X.

Por defecto: Toyota con patente terminada en "D".
Base: Neo4j (nodos Vehiculo).
"""
from src.repositories import grafo_repo


def ejecutar(marca: str = "Toyota", sufijo: str = "D") -> int:
    """Devuelve la cantidad de vehículos que cumplen ambos filtros."""
    return grafo_repo.vehiculos_marca_y_patente_termina(marca, sufijo)
```

- [ ] **Step 4: Tests pasan**

```bash
pytest tests/casos_uso/test_caso_06_toyota_patente_d.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/casos_uso/caso_06_toyota_patente_d.py tests/casos_uso/test_caso_06_toyota_patente_d.py
git commit -m "agregar caso de uso 6: Toyota con patente D en Neo4j (3 tests)"
git push
```

---

### Task 1.8: Caso 7 — Reseñas con rating 5 o <2

**Files:**
- Create: `src/casos_uso/caso_07_resenas_extremas.py`
- Create: `tests/casos_uso/test_caso_07_resenas_extremas.py`

- [ ] **Step 1: Test**

```python
"""Tests del caso de uso 7: reseñas con rating 5 o menor a 2 (Mongo)."""
from datetime import datetime, UTC


def _resena(rating: int):
    return {
        "viaje_id": "v", "tipo": "U_A_C",
        "autor": {"id": "a", "nombre": "A"},
        "destinatario": {"id": "d", "nombre": "D"},
        "rating": rating, "comentario": "x",
        "timestamp": datetime.now(UTC),
    }


def test_devuelve_solo_extremos(mongo_clean):
    from src.repositories import resena_repo
    from src.casos_uso import caso_07_resenas_extremas

    resena_repo.crear(_resena(5))
    resena_repo.crear(_resena(1))
    resena_repo.crear(_resena(3))  # ignorada
    resena_repo.crear(_resena(4))  # ignorada
    resena_repo.crear(_resena(5))

    extremas = caso_07_resenas_extremas.ejecutar()
    ratings = sorted(r["rating"] for r in extremas)
    assert ratings == [1, 5, 5]


def test_sin_resenas_devuelve_lista_vacia(mongo_clean):
    from src.casos_uso import caso_07_resenas_extremas
    assert caso_07_resenas_extremas.ejecutar() == []
```

- [ ] **Step 2: Tests fallan**

- [ ] **Step 3: Implementar**

```python
"""Caso de uso 7: reseñas con rating 5 o menor a 2.

Base: Mongo (resenas).
"""
from src.repositories import resena_repo


def ejecutar() -> list[dict]:
    """Devuelve las reseñas extremas (rating = 5 o rating < 2)."""
    return resena_repo.buscar_por_rating_extremo()
```

- [ ] **Step 4: Tests pasan**

```bash
pytest tests/casos_uso/test_caso_07_resenas_extremas.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add src/casos_uso/caso_07_resenas_extremas.py tests/casos_uso/test_caso_07_resenas_extremas.py
git commit -m "agregar caso de uso 7: resenas con rating extremo (2 tests)"
git push
```

---

## Sección 2 — Helpers de formato

### Task 2.1: `src/menu/formato.py`

**Files:**
- Create: `src/menu/formato.py`

Helpers de print/formato compartidos por todos los submenús. Sin tests automatizados (es presentación pura).

- [ ] **Step 1: Crear el archivo**

```python
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
```

- [ ] **Step 2: Verificar que importa**

```bash
python -c "from src.menu import formato; formato.titulo('Test'); formato.exito('OK')"
```
Expected: imprime el título y el [OK] sin errores.

- [ ] **Step 3: Commit**

```bash
git add src/menu/formato.py
git commit -m "agregar helpers de formato para el menu de consola"
git push
```

---

## Sección 3 — Submenús

> **Para los submenús no hay tests unitarios automatizados** (testear stdin/stdout es complicado y de bajo valor para un TP). El test es manual al final del plan.
>
> Lo único que sí testeamos automáticamente es que los módulos **importen sin errores**, en `tests/menu/test_imports.py`.

### Task 3.1: `submenu_cuentas.py`

**Files:**
- Create: `src/menu/submenu_cuentas.py`

Operaciones: registrar usuario, registrar conductor, login, logout.

- [ ] **Step 1: Implementar**

```python
"""Submenu de gestion de cuentas: registro, login, logout."""
from src.services import auth_service
from src.utils.errors import CredencialesInvalidas
from src.menu import formato


def loop(sesion: dict) -> None:
    """Loop del submenu. sesion es un dict mutable con token/data actuales."""
    while True:
        formato.subtitulo("Cuentas")
        _imprimir_estado_sesion(sesion)
        print("1. Registrar como usuario (pasajero)")
        print("2. Registrar como conductor")
        print("3. Iniciar sesión")
        print("4. Cerrar sesión")
        print("5. Volver")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            _registrar_usuario()
        elif op == "2":
            _registrar_conductor()
        elif op == "3":
            _login(sesion)
        elif op == "4":
            _logout(sesion)
        elif op == "5":
            return
        else:
            formato.error("Opción inválida.")


def _imprimir_estado_sesion(sesion: dict) -> None:
    if sesion.get("data"):
        formato.info(f"Sesión activa: {sesion['data']['nombre']} ({sesion['data']['tipo']})")
    else:
        formato.info("Sin sesión")


def _registrar_usuario() -> None:
    email = formato.pedir_input("Email")
    password = formato.pedir_input("Password")
    nombre = formato.pedir_input("Nombre completo")
    telefono = formato.pedir_input("Teléfono (opcional)", default="")
    try:
        uid = auth_service.register_usuario(email, password, nombre, telefono or None)
        formato.exito(f"Usuario registrado con id {uid}")
    except Exception as e:
        formato.error(f"No se pudo registrar: {e}")
    formato.pausa()


def _registrar_conductor() -> None:
    email = formato.pedir_input("Email")
    password = formato.pedir_input("Password")
    nombre = formato.pedir_input("Nombre completo")
    licencia = formato.pedir_input("Nro. de licencia")
    telefono = formato.pedir_input("Teléfono (opcional)", default="")
    try:
        cid = auth_service.register_conductor(email, password, nombre, licencia, telefono or None)
        formato.exito(f"Conductor registrado con id {cid}")
    except Exception as e:
        formato.error(f"No se pudo registrar: {e}")
    formato.pausa()


def _login(sesion: dict) -> None:
    if sesion.get("data"):
        formato.error("Ya hay una sesión activa. Cerrá sesión primero.")
        formato.pausa()
        return
    email = formato.pedir_input("Email")
    password = formato.pedir_input("Password")
    tipo = formato.pedir_input("Tipo de cuenta (USUARIO/CONDUCTOR)", default="USUARIO")
    if tipo not in ("USUARIO", "CONDUCTOR"):
        formato.error("Tipo de cuenta inválido.")
        formato.pausa()
        return
    try:
        token = auth_service.login(email, password, tipo)
        data = auth_service.validate_session(token)
        sesion["token"] = token
        sesion["data"] = data
        formato.exito(f"Sesión iniciada como {data['nombre']} ({data['tipo']})")
    except CredencialesInvalidas:
        formato.error("Email o password incorrectos.")
    except Exception as e:
        formato.error(f"Error al iniciar sesión: {e}")
    formato.pausa()


def _logout(sesion: dict) -> None:
    if not sesion.get("token"):
        formato.error("No hay sesión activa.")
        formato.pausa()
        return
    auth_service.logout(sesion["token"])
    sesion["token"] = None
    sesion["data"] = None
    formato.exito("Sesión cerrada.")
    formato.pausa()
```

- [ ] **Step 2: Verificar import**

```bash
python -c "from src.menu import submenu_cuentas; print('OK')"
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add src/menu/submenu_cuentas.py
git commit -m "agregar submenu de cuentas (registro/login/logout)"
git push
```

---

### Task 3.2: `submenu_operacion.py`

**Files:**
- Create: `src/menu/submenu_operacion.py`

Operaciones que requieren sesión: registrar vehículo, solicitar/iniciar/finalizar viaje, pago, reseña, reportar GPS.

- [ ] **Step 1: Implementar**

```python
"""Submenu de operaciones de negocio. Requiere sesión activa."""
import random
from src.services import (
    vehiculo_service, viaje_service, pago_service,
    resena_service, ubicacion_service,
)
from src.utils.errors import DomainError
from src.menu import formato


def loop(sesion: dict) -> None:
    if not sesion.get("data"):
        formato.error("Necesitás iniciar sesión primero.")
        formato.pausa()
        return

    while True:
        formato.subtitulo(f"Operación — {sesion['data']['nombre']} ({sesion['data']['tipo']})")
        print("1. Registrar vehículo (solo CONDUCTOR)")
        print("2. Solicitar viaje (solo USUARIO)")
        print("3. Iniciar viaje (solo CONDUCTOR)")
        print("4. Finalizar viaje (solo CONDUCTOR)")
        print("5. Reportar GPS de un vehículo")
        print("6. Procesar pago de un viaje")
        print("7. Crear reseña")
        print("8. Volver")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            _registrar_vehiculo(sesion)
        elif op == "2":
            _solicitar_viaje(sesion)
        elif op == "3":
            _iniciar_viaje()
        elif op == "4":
            _finalizar_viaje()
        elif op == "5":
            _reportar_gps()
        elif op == "6":
            _procesar_pago(sesion)
        elif op == "7":
            _crear_resena(sesion)
        elif op == "8":
            return
        else:
            formato.error("Opción inválida.")


def _registrar_vehiculo(sesion: dict) -> None:
    if sesion["data"]["tipo"] != "CONDUCTOR":
        formato.error("Solo los CONDUCTORES pueden registrar vehículos.")
        formato.pausa()
        return
    cid = sesion["data"]["user_id"]
    placa = formato.pedir_input("Placa")
    marca = formato.pedir_input("Marca")
    modelo = formato.pedir_input("Modelo")
    anio = formato.pedir_input("Año (opcional)", default="")
    color = formato.pedir_input("Color (opcional)", default="")
    tipo = formato.pedir_input("Tipo (sedan/SUV/moto/...) (opcional)", default="")
    try:
        vid = vehiculo_service.registrar(
            cid, placa, marca, modelo,
            anio=int(anio) if anio else None,
            color=color or None,
            tipo=tipo or None,
        )
        formato.exito(f"Vehículo registrado con id {vid}")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"No se pudo registrar: {e}")
    formato.pausa()


def _solicitar_viaje(sesion: dict) -> None:
    if sesion["data"]["tipo"] != "USUARIO":
        formato.error("Solo los USUARIOS pueden solicitar viajes.")
        formato.pausa()
        return
    uid = sesion["data"]["user_id"]
    cid = formato.pedir_input("ID del conductor")
    vid = formato.pedir_input("ID del vehículo")
    origen = formato.pedir_input("Origen (descripción)")
    destino = formato.pedir_input("Destino (descripción)")
    try:
        viaje_id = viaje_service.solicitar(
            uid, cid, vid,
            origen={"lat": -34.6, "lon": -58.4, "direccion": origen},
            destino={"lat": -34.55, "lon": -58.45, "direccion": destino},
        )
        formato.exito(f"Viaje solicitado con id {viaje_id} (estado PENDIENTE)")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _iniciar_viaje() -> None:
    viaje_id = formato.pedir_input("ID del viaje a iniciar")
    try:
        ok = viaje_service.iniciar(viaje_id)
        if ok:
            formato.exito("Viaje iniciado (EN_CURSO).")
        else:
            formato.error("No se pudo iniciar (¿no estaba PENDIENTE?).")
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _finalizar_viaje() -> None:
    viaje_id = formato.pedir_input("ID del viaje a finalizar")
    try:
        distancia = float(formato.pedir_input("Distancia (km)"))
        duracion = int(formato.pedir_input("Duración (min)"))
        viaje_service.finalizar(viaje_id, distancia, duracion)
        formato.exito("Viaje finalizado.")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _reportar_gps() -> None:
    vid = formato.pedir_input("ID del vehículo")
    try:
        # Para la demo: lat/lon aleatorios cerca de CABA
        lat = -34.6 + random.uniform(-0.1, 0.1)
        lon = -58.4 + random.uniform(-0.1, 0.1)
        ubicacion_service.reportar(vid, lat, lon)
        formato.exito(f"GPS reportado: ({lat:.4f}, {lon:.4f})")
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _procesar_pago(sesion: dict) -> None:
    viaje_id = formato.pedir_input("ID del viaje")
    try:
        monto = float(formato.pedir_input("Monto total"))
        metodo = formato.pedir_input("Método (TARJETA/EFECTIVO/BILLETERA_VIRTUAL)", default="TARJETA")
        pago_id = pago_service.procesar(
            viaje_id, monto, tarifa_base=500,
            tarifa_distancia=monto * 0.5, tarifa_tiempo=monto * 0.3,
            cargos_extra=0, metodo_pago=metodo,
        )
        formato.exito(f"Pago procesado con id {pago_id}")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()


def _crear_resena(sesion: dict) -> None:
    viaje_id = formato.pedir_input("ID del viaje")
    autor_id = sesion["data"]["user_id"]
    autor_nombre = sesion["data"]["nombre"]
    destinatario_id = formato.pedir_input("ID del destinatario (el otro participante)")
    destinatario_nombre = formato.pedir_input("Nombre del destinatario")
    tipo = "U_A_C" if sesion["data"]["tipo"] == "USUARIO" else "C_A_U"
    try:
        rating = int(formato.pedir_input("Rating (1-5)"))
        comentario = formato.pedir_input("Comentario")
        rid = resena_service.crear(
            viaje_id, tipo, autor_id, autor_nombre,
            destinatario_id, destinatario_nombre,
            rating, comentario,
        )
        formato.exito(f"Reseña creada con id {rid}")
    except DomainError as e:
        formato.error(str(e))
    except Exception as e:
        formato.error(f"Error: {e}")
    formato.pausa()
```

- [ ] **Step 2: Verificar import**

```bash
python -c "from src.menu import submenu_operacion; print('OK')"
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add src/menu/submenu_operacion.py
git commit -m "agregar submenu de operacion (vehiculo/viaje/pago/resena/GPS)"
git push
```

---

### Task 3.3: `submenu_consultas.py`

**Files:**
- Create: `src/menu/submenu_consultas.py`

Los 7 casos de uso.

- [ ] **Step 1: Implementar**

```python
"""Submenu de consultas: los 7 casos de uso del enunciado."""
from src.casos_uso import (
    caso_01_top_resenadores,
    caso_02_metodo_pago,
    caso_03_conductores_inactivos,
    caso_04_promedio_viajes,
    caso_05_coincidencias,
    caso_06_toyota_patente_d,
    caso_07_resenas_extremas,
)
from src.menu import formato


def loop() -> None:
    while True:
        formato.subtitulo("Consultas — los 7 casos de uso")
        print("1. Top 3 reseñadores")
        print("2. Método de pago menos usado")
        print("3. Conductores inactivos último mes")
        print("4. Tiempo promedio de viajes")
        print("5. Pasajero-conductor con >1 viaje")
        print("6. Toyota con patente terminada en 'D'")
        print("7. Reseñas con rating 5 o <2")
        print("8. Volver")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            _ejecutar_caso_1()
        elif op == "2":
            _ejecutar_caso_2()
        elif op == "3":
            _ejecutar_caso_3()
        elif op == "4":
            _ejecutar_caso_4()
        elif op == "5":
            _ejecutar_caso_5()
        elif op == "6":
            _ejecutar_caso_6()
        elif op == "7":
            _ejecutar_caso_7()
        elif op == "8":
            return
        else:
            formato.error("Opción inválida.")


def _ejecutar_caso_1() -> None:
    formato.info("Consultando Mongo (con cache Redis)...")
    top = caso_01_top_resenadores.ejecutar()
    if not top:
        formato.info("Sin reseñas aún.")
    else:
        formato.tabla(top, columnas=["nombre", "autor_id", "cantidad"])
    formato.pausa()


def _ejecutar_caso_2() -> None:
    formato.info("Consultando Mongo...")
    metodo = caso_02_metodo_pago.ejecutar()
    if metodo is None:
        formato.info("Sin pagos en la plataforma todavía.")
    else:
        formato.exito(f"Método menos usado: {metodo}")
    formato.pausa()


def _ejecutar_caso_3() -> None:
    formato.info("Consultando Cassandra + Postgres...")
    inactivos = caso_03_conductores_inactivos.ejecutar()
    if not inactivos:
        formato.info("Todos los conductores activos tuvieron viajes en el último mes.")
    else:
        formato.tabla(inactivos, columnas=["nombre", "email", "rating_promedio"])
    formato.pausa()


def _ejecutar_caso_4() -> None:
    formato.info("Consultando Cassandra (con cache Redis)...")
    promedio = caso_04_promedio_viajes.ejecutar()
    formato.exito(f"Tiempo promedio de viaje: {promedio:.2f} min")
    formato.pausa()


def _ejecutar_caso_5() -> None:
    formato.info("Consultando Neo4j...")
    coincidencias = caso_05_coincidencias.ejecutar()
    if not coincidencias:
        formato.info("Nadie coincidió en más de 1 viaje aún.")
    else:
        formato.tabla(coincidencias, columnas=["pasajero", "conductor", "viajes"])
    formato.pausa()


def _ejecutar_caso_6() -> None:
    marca = formato.pedir_input("Marca", default="Toyota")
    sufijo = formato.pedir_input("Patente termina en", default="D")
    formato.info("Consultando Neo4j...")
    cantidad = caso_06_toyota_patente_d.ejecutar(marca, sufijo)
    formato.exito(f"Hay {cantidad} vehículos {marca} con patente terminada en '{sufijo}'.")
    formato.pausa()


def _ejecutar_caso_7() -> None:
    formato.info("Consultando Mongo...")
    extremas = caso_07_resenas_extremas.ejecutar()
    if not extremas:
        formato.info("Sin reseñas extremas todavía.")
    else:
        # Aplanar autor/destinatario para mostrarlo en tabla
        for r in extremas:
            r["autor_nombre"] = r["autor"]["nombre"]
            r["destinatario_nombre"] = r["destinatario"]["nombre"]
        formato.tabla(extremas, columnas=["rating", "autor_nombre", "destinatario_nombre", "comentario"])
    formato.pausa()
```

- [ ] **Step 2: Verificar import**

```bash
python -c "from src.menu import submenu_consultas; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add src/menu/submenu_consultas.py
git commit -m "agregar submenu de consultas con los 7 casos de uso"
git push
```

---

### Task 3.4: `submenu_admin.py`

**Files:**
- Create: `src/menu/submenu_admin.py`

Administración: verificar conexiones, reconciliar, ver outbox, limpiar bases.

- [ ] **Step 1: Implementar**

```python
"""Submenu de administracion: health check, reconciliacion, outbox, reset."""
from src.db import postgres, mongo, cassandra, neo4j_db, redis_db
from src.services import reconciliacion_service
from src.utils import outbox
from src.menu import formato


def loop() -> None:
    while True:
        formato.subtitulo("Administración")
        print("1. Verificar conexiones a las 5 bases")
        print("2. Reconciliar Neo4j desde Mongo")
        print("3. Ver outbox (proyecciones fallidas)")
        print("4. Limpiar el outbox")
        print("5. Limpiar TODAS las bases (peligroso)")
        print("6. Volver")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            _health_check()
        elif op == "2":
            _reconciliar()
        elif op == "3":
            _ver_outbox()
        elif op == "4":
            _limpiar_outbox()
        elif op == "5":
            _reset_dbs()
        elif op == "6":
            return
        else:
            formato.error("Opción inválida.")


def _health_check() -> None:
    bases = [
        ("Postgres   (Neon)",   postgres.check),
        ("MongoDB    (Atlas)",  mongo.check),
        ("Cassandra  (Astra)",  cassandra.check),
        ("Neo4j      (Aura)",   neo4j_db.check),
        ("Redis      (Cloud)",  redis_db.check),
    ]
    for nombre, fn in bases:
        ok = fn()
        if ok:
            formato.exito(f"{nombre}: OK")
        else:
            formato.error(f"{nombre}: FAIL")
    formato.pausa()


def _reconciliar() -> None:
    formato.info("Reconstruyendo aristas VIAJO_CON en Neo4j desde Mongo...")
    stats = reconciliacion_service.sync_neo4j_desde_mongo()
    formato.exito(
        f"Listo. Pares reconstruidos: {stats['pares_reconstruidos']}, "
        f"viajes procesados: {stats['viajes_procesados']}."
    )
    formato.pausa()


def _ver_outbox() -> None:
    stats = reconciliacion_service.procesar_outbox()
    formato.info(f"Outbox tiene {stats['pendientes']} entradas pendientes.")
    if stats["pendientes"] > 0:
        formato.tabla(stats["entradas"], columnas=["ts", "operation"])
    formato.pausa()


def _limpiar_outbox() -> None:
    if formato.confirmar("¿Seguro que querés limpiar el outbox?"):
        outbox.clear()
        formato.exito("Outbox limpio.")
    formato.pausa()


def _reset_dbs() -> None:
    formato.error("ATENCIÓN: esto borra TODOS los datos de las 5 bases.")
    if not formato.confirmar('Escribí "s" para confirmar'):
        formato.info("Cancelado.")
        formato.pausa()
        return

    # Reusar la lógica de scripts/reset_all_dbs.py
    from scripts import reset_all_dbs
    reset_all_dbs.reset_postgres()
    reset_all_dbs.reset_mongo()
    reset_all_dbs.reset_cassandra()
    reset_all_dbs.reset_neo4j()
    reset_all_dbs.reset_redis()
    formato.exito("Todas las bases fueron limpiadas.")
    formato.info("Recordá correr `python -m scripts.init_mongo` para recrear índices.")
    formato.pausa()
```

> **Nota:** importar `scripts.reset_all_dbs` requiere que `scripts/` tenga un `__init__.py` o que se ejecute como módulo. Si la importación falla, agregar `scripts/__init__.py` vacío.

- [ ] **Step 2: Asegurar que `scripts/` es importable**

```bash
touch scripts/__init__.py
```

- [ ] **Step 3: Verificar import**

```bash
python -c "from src.menu import submenu_admin; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add src/menu/submenu_admin.py scripts/__init__.py
git commit -m "agregar submenu de administracion (health, reconcile, outbox, reset)"
git push
```

---

## Sección 4 — Main menu + entry point

### Task 4.1: `src/menu/main_menu.py`

**Files:**
- Create: `src/menu/main_menu.py`

- [ ] **Step 1: Implementar**

```python
"""Menu principal — orquesta los 4 submenus."""
from src.menu import (
    submenu_cuentas,
    submenu_operacion,
    submenu_consultas,
    submenu_admin,
    formato,
)

# Sesion actual del usuario, mutable y compartida con los submenus
_sesion = {"token": None, "data": None}


def loop() -> None:
    """Loop infinito del menu principal hasta que el usuario salga."""
    formato.titulo("TP UBER — Datos 2 (UADE)")

    while True:
        _imprimir_estado_sesion()
        print("\n1. Cuentas")
        print("2. Operación")
        print("3. Consultas (7 casos de uso)")
        print("4. Administración")
        print("5. Salir")

        op = input("\nElegí una opción: ").strip()
        if op == "1":
            submenu_cuentas.loop(_sesion)
        elif op == "2":
            submenu_operacion.loop(_sesion)
        elif op == "3":
            submenu_consultas.loop()
        elif op == "4":
            submenu_admin.loop()
        elif op == "5":
            formato.info("Hasta luego.")
            return
        else:
            formato.error("Opción inválida.")


def _imprimir_estado_sesion() -> None:
    if _sesion.get("data"):
        formato.info(f"Sesión activa: {_sesion['data']['nombre']} ({_sesion['data']['tipo']})")
    else:
        formato.info("Sin sesión activa")
```

- [ ] **Step 2: Verificar import**

```bash
python -c "from src.menu import main_menu; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add src/menu/main_menu.py
git commit -m "agregar main_menu que orquesta los 4 submenus"
git push
```

---

### Task 4.2: `src/main.py` (entry point)

**Files:**
- Create: `src/main.py`

- [ ] **Step 1: Implementar**

```python
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
```

- [ ] **Step 2: Probar que arranca**

```bash
python -m src.main
```
Expected: imprime el banner, muestra el menú principal y espera input. Presionar `5` para salir limpiamente.

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "agregar entry point src/main.py — la app ya es ejecutable"
git push
```

---

### Task 4.3: `tests/menu/test_imports.py`

**Files:**
- Create: `tests/menu/test_imports.py`

Tests minimalistas que solo verifican que los módulos cargan sin errores.

- [ ] **Step 1: Crear**

```python
"""Tests minimalistas del menu: verifican que los modulos importan."""


def test_main_menu_importa():
    from src.menu import main_menu
    assert main_menu.loop is not None


def test_submenu_cuentas_importa():
    from src.menu import submenu_cuentas
    assert submenu_cuentas.loop is not None


def test_submenu_operacion_importa():
    from src.menu import submenu_operacion
    assert submenu_operacion.loop is not None


def test_submenu_consultas_importa():
    from src.menu import submenu_consultas
    assert submenu_consultas.loop is not None


def test_submenu_admin_importa():
    from src.menu import submenu_admin
    assert submenu_admin.loop is not None


def test_formato_helpers_existen():
    from src.menu import formato
    assert formato.titulo is not None
    assert formato.error is not None
    assert formato.exito is not None
    assert formato.tabla is not None
    assert formato.confirmar is not None
```

- [ ] **Step 2: Correr**

```bash
pytest tests/menu/test_imports.py -v
```
Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/menu/test_imports.py
git commit -m "agregar tests minimalistas de imports de modulos del menu (6 tests)"
git push
```

---

## Sección 5 — Verificación end-to-end

### Task 5.1: Smoke test manual de la app

> Este es un test **manual**. El objetivo es asegurarse de que el flujo completo funciona antes de pasar al Plan 05 (seeding + presentación).

- [ ] **Step 1: Limpiar las bases para empezar de cero**

```bash
python -m scripts.reset_all_dbs
```
Escribir `BORRAR` para confirmar.

```bash
python -m scripts.init_mongo
```

- [ ] **Step 2: Arrancar la app**

```bash
python -m src.main
```

- [ ] **Step 3: Flujo manual a verificar**

Hacer este flujo y verificar que cada paso devuelve `[OK]`:

1. **Cuentas → 1. Registrar usuario:** `juan@m.com / 1234 / Juan Pérez`
2. **Cuentas → 2. Registrar conductor:** `ana@m.com / 1234 / Ana Gómez / LIC-001`
3. **Cuentas → 3. Login** como `ana@m.com / 1234 / CONDUCTOR`
4. **Operación → 1. Registrar vehículo:** anotar el `vehiculo_id`. Usar placa `ABC123D` marca `Toyota`.
5. **Cuentas → 4. Logout**
6. **Cuentas → 3. Login** como `juan@m.com / 1234 / USUARIO`
7. **Operación → 2. Solicitar viaje:** pegar el `conductor_id` (de Ana) y el `vehiculo_id` registrado. Anotar el `viaje_id`.
8. **Cuentas → 4. Logout**
9. **Cuentas → 3. Login** como `ana@m.com / 1234 / CONDUCTOR`
10. **Operación → 3. Iniciar viaje:** pegar el `viaje_id`.
11. **Operación → 5. Reportar GPS:** pegar el `vehiculo_id`.
12. **Operación → 4. Finalizar viaje:** pegar el `viaje_id`, distancia `8`, duración `22`.
13. **Cuentas → 4. Logout**
14. **Cuentas → 3. Login** como `juan@m.com` (USUARIO)
15. **Operación → 6. Procesar pago:** pegar `viaje_id`, monto `2500`, método `TARJETA`.
16. **Operación → 7. Crear reseña:** pegar `viaje_id` y `conductor_id`, rating `5`, comentario `Excelente`.
17. **Cuentas → 5. Volver al menú principal**
18. **Consultas → 1. Top 3 reseñadores** → debe aparecer Juan con `cantidad: 1`.
19. **Consultas → 2. Método de pago menos usado** → debe aparecer `TARJETA` (único pago).
20. **Consultas → 4. Tiempo promedio** → debe aparecer `22.00 min`.
21. **Consultas → 5. Coincidencias** → debe aparecer Juan-Ana con `viajes: 1`. (Para que aparezca con `>1`, repetir el flujo de viaje al menos una vez más.)
22. **Consultas → 6. Toyota patente D** → debe aparecer `1 vehículo`.
23. **Consultas → 7. Reseñas extremas** → debe aparecer la reseña rating 5.
24. **Administración → 1. Verificar conexiones** → 5 OK.
25. **Administración → 2. Reconciliar Neo4j desde Mongo** → "Pares reconstruidos: 1".
26. **Salir → 5**

- [ ] **Step 4: Si algún paso falla, debuggear el service correspondiente y arreglar antes de continuar**

- [ ] **Step 5: Correr el test suite completo**

```bash
pytest tests/ -v
```
Expected: **140+ tests passed** (~120 anteriores + ~26 de casos de uso + 6 de menu_imports).

- [ ] **Step 6: Marcar Fases 5 y 6 completas en `docs/tareas.md`**

Marcar todas las sub-fases de:
- **Fase 5** (casos de uso 1-7).
- **Fase 6** (los 4 submenús, loop principal).

- [ ] **Step 7: Actualizar nota de seguimiento**

Agregar a `docs/tareas.md`:
```
- 2026-MM-DD: Plan 04 completo. Los 7 casos de uso están implementados y testeados.
  El menú interactivo funciona end-to-end (registrar → operar → consultar). La app
  ya es ejecutable con `python -m src.main`. Listo para empezar Plan 05 (seeding + presentación).
```

- [ ] **Step 8: Commit final**

```bash
git add docs/tareas.md
git commit -m "marcar Fases 5 y 6 (casos de uso + menu) como completadas"
git push
```

---

## Cierre del plan

Estado esperado al finalizar:

```
✅ src/casos_uso/ con 7 modulos + tests
✅ src/menu/ con 5 modulos (main + 4 submenus + formato)
✅ src/main.py — entry point ejecutable
✅ ~26 tests nuevos de casos de uso + 6 de imports = 32 tests
✅ Total test suite ~140 tests verdes
✅ Demo end-to-end manual exitoso
✅ python -m src.main funciona y permite recorrer todo el flujo
✅ Todo versionado en GitHub
```

**Hito alcanzado:** la aplicación es **demo-able**. Se puede ejecutar la presentación del profesor con datos creados manualmente. El Plan 05 agrega seed data para tener un dataset realista al demo y prepara las slides.

**Siguiente paso:** escribir `docs/plan-05-seeding-presentacion.md` para `seed_data.py` con ~50 viajes realistas + simulador GPS + checklist de presentación.
