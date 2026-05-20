# Plan 02 — Repositories: Capa de acceso a datos con TDD estricto

> **Para agentes:** REQUIRED SUB-SKILL: Usar `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans`. Los pasos usan checkboxes `- [ ]` para tracking.

**Goal:** Implementar los 11 repositories en `src/repositories/`, uno por entidad por base, cada uno con tests de integración siguiendo TDD estricto (test que falla → implementación mínima → test pasa → commit).

**Architecture:** Cada repository toca **exactamente UNA base de datos** y expone funciones CRUD + queries específicas. Los tests son **tests de integración** contra las bases cloud reales (no se mockean). Cada test usa fixtures que limpian la base antes de ejecutarse para garantizar aislamiento.

**Tech Stack:** Python 3.11+, pytest, los drivers del Plan 01 (`psycopg`, `pymongo`, `cassandra-driver`, `neo4j`, `redis`).

---

## Pre-requisito

**Plan 01 (Foundation) debe estar completo.** Esto significa:
- ✅ 5 bases cloud activas y conectadas (`scripts/check_connections.py` devuelve OK).
- ✅ Esquemas inicializados en Postgres, Mongo (índices), Cassandra y Neo4j (constraints).
- ✅ Módulos `src/db/*.py` funcionando.
- ✅ `src/config.py`, `src/utils/logger.py`, `src/utils/errors.py` listos.

---

## Alcance de este plan

Cubre la **Fase 4** de `docs/tareas.md`: la capa de repositorios.

**NO incluye:**
- Services (Plan 03)
- Casos de uso ni menú (Plan 04)
- Seed de datos ni presentación (Plan 05)

**Entregables al finalizar:**

- ✅ 11 módulos en `src/repositories/`, uno por entidad/base.
- ✅ 11 archivos de test en `tests/repositories/`, todos pasando.
- ✅ `conftest.py` con fixtures que limpian cada base entre tests.
- ✅ `pytest tests/repositories/` corre verde de punta a punta.
- ✅ Cobertura mental: cada función pública tiene al menos 1 test (caso feliz) + casos de borde relevantes (no encontrado, duplicado, etc.).

---

## Diseño general de la capa

### Convenciones de los repositories

1. **Una sola base por repository.** `viaje_repo.py` solo toca Mongo. Nunca importa `src.db.postgres`.
2. **Singleton de conexión.** Cada repository usa el singleton de `src/db/*.py` del Plan 01.
3. **Sin lógica de negocio.** Los repositories solo hacen CRUD + queries. Validaciones de negocio van en los services (Plan 03).
4. **Funciones, no clases.** Cada repository es un módulo Python con funciones a nivel top-level (más simple que clases para este TP).
5. **Tipos de retorno consistentes:**
   - `crear_*(...)` → `str` (id del nuevo registro)
   - `get_by_*(...)` → `dict | None` (None si no se encuentra)
   - `actualizar_*(...)` → `bool` (True si modificó algo)
   - `listar_*(...)` → `list[dict]`
   - `contar_*(...)` → `int` o `dict`
   - `existe(...)` → `bool`
6. **Errores:** los repositories no lanzan excepciones del dominio (eso es responsabilidad de los services). Solo propagan errores de driver si algo va mal a nivel infraestructura.

### Convenciones de los tests

1. **Tests de integración**, no unitarios. Hablan con las bases reales del cloud.
2. **Una base por test class.** No mezclar bases en un mismo archivo de test.
3. **Aislamiento:** cada test corre con una base limpia gracias a una fixture (`autouse=True` por archivo).
4. **Naming:** `test_<funcion>_<caso>` (ej. `test_crear_usuario_con_email_valido`, `test_get_by_email_no_existente`).
5. **Sin mocks.** Si necesitás aislar lógica, refactorizá la lógica al service.
6. **Tiempo de ejecución:** `pytest tests/repositories/` debería tardar < 60 segundos. Si tarda más, reportar.

---

## File Structure

Archivos que se crean en este plan:

```
src/repositories/
├── __init__.py
├── usuario_repo.py          → Postgres
├── conductor_repo.py        → Postgres
├── vehiculo_repo.py         → Postgres
├── viaje_repo.py            → Mongo
├── pago_repo.py             → Mongo
├── resena_repo.py           → Mongo
├── login_history_repo.py    → Mongo
├── ubicacion_repo.py        → Cassandra
├── actividad_repo.py        → Cassandra
├── grafo_repo.py            → Neo4j
└── cache_repo.py            → Redis

tests/
├── __init__.py              (ya existe del Plan 01)
├── conftest.py              ← fixtures globales
└── repositories/
    ├── __init__.py
    ├── test_usuario_repo.py
    ├── test_conductor_repo.py
    ├── test_vehiculo_repo.py
    ├── test_viaje_repo.py
    ├── test_pago_repo.py
    ├── test_resena_repo.py
    ├── test_login_history_repo.py
    ├── test_ubicacion_repo.py
    ├── test_actividad_repo.py
    ├── test_grafo_repo.py
    └── test_cache_repo.py

requirements.txt             ← agregar pytest
```

---

## Sección 0 — Setup de pytest e infraestructura de tests

### Task 0.1: Agregar pytest a requirements

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Agregar pytest al `requirements.txt`**

Editar `requirements.txt` y agregar al final:
```
pytest==8.3.*
```

- [ ] **Step 2: Reinstalar dependencias**

```bash
pip install -r requirements.txt
```
Expected: `Successfully installed pytest-8.3.x`

- [ ] **Step 3: Verificar instalación**

```bash
pytest --version
```
Expected: `pytest 8.3.x`

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "agregar pytest para tests de integracion de repositories"
git push
```

---

### Task 0.2: Crear `src/repositories/__init__.py` y `tests/repositories/`

**Files:**
- Create: `src/repositories/__init__.py`
- Create: `tests/repositories/__init__.py`

- [ ] **Step 1: Crear las carpetas y archivos**

```bash
mkdir -p src/repositories tests/repositories
touch src/repositories/__init__.py tests/repositories/__init__.py
```

- [ ] **Step 2: Verificar**

```bash
ls -la src/repositories/ tests/repositories/
```
Expected: ambas carpetas con `__init__.py`.

- [ ] **Step 3: Commit**

```bash
git add src/repositories/ tests/repositories/
git commit -m "agregar esqueleto de carpetas para repositories y sus tests"
git push
```

---

### Task 0.3: `tests/conftest.py` con fixtures de limpieza

**Files:**
- Create: `tests/conftest.py`

> Pytest descubre automáticamente `conftest.py` y hace disponibles las fixtures definidas ahí a todos los tests del directorio (y subdirectorios).

- [ ] **Step 1: Escribir `tests/conftest.py`**

```python
"""Fixtures globales para todos los tests del proyecto.

Cada fixture limpia su base de datos antes del test. Esto garantiza
aislamiento entre tests aún cuando ejecutan contra DBs reales en cloud.

Uso en un test:

    def test_algo(postgres_clean):
        # Postgres está vacía acá
        ...
"""
import pytest


@pytest.fixture
def postgres_clean():
    """Trunca todas las tablas de Postgres antes del test."""
    from src.db.postgres import get_conn
    with get_conn().cursor() as cur:
        cur.execute("TRUNCATE vehiculo, conductor, usuario CASCADE;")
    yield


@pytest.fixture
def mongo_clean():
    """Borra todas las colecciones de Mongo antes del test."""
    from src.db.mongo import get_db
    db = get_db()
    for coll in ["viajes", "pagos", "resenas", "login_history"]:
        db[coll].drop()
    # Recrear índices después de drop (los pierde con drop_collection)
    db.viajes.create_index([("usuario_id", 1)])
    db.viajes.create_index([("conductor_id", 1)])
    db.viajes.create_index([("estado", 1), ("ts_inicio", -1)])
    db.pagos.create_index([("viaje_id", 1)])
    db.pagos.create_index([("metodo_pago", 1)])
    db.resenas.create_index([("autor.id", 1)])
    db.resenas.create_index([("destinatario.id", 1)])
    db.resenas.create_index([("tipo", 1), ("rating", 1)])
    yield


@pytest.fixture
def cassandra_clean():
    """Trunca todas las tablas de Cassandra antes del test."""
    from src.db.cassandra import get_session
    session = get_session()
    for table in ["ubicaciones_por_vehiculo", "ultima_actividad_conductor",
                  "viajes_finalizados_por_dia"]:
        session.execute(f"TRUNCATE {table}")
    yield


@pytest.fixture
def neo4j_clean():
    """Borra todos los nodos y aristas de Neo4j antes del test."""
    from src.db.neo4j_db import get_driver
    with get_driver().session() as s:
        s.run("MATCH (n) DETACH DELETE n")
    yield


@pytest.fixture
def redis_clean():
    """FLUSHDB en Redis antes del test."""
    from src.db.redis_db import get_client
    get_client().flushdb()
    yield
```

- [ ] **Step 2: Crear un test smoke para verificar pytest funciona**

Crear `tests/test_smoke.py`:
```python
"""Smoke test — verifica que pytest está configurado correctamente."""


def test_pytest_funciona():
    assert True


def test_imports_basicos():
    from src.config import settings
    from src.utils.logger import logger
    from src.utils.errors import DomainError

    assert settings is not None
    assert logger is not None
    assert issubclass(DomainError, Exception)
```

- [ ] **Step 3: Correr pytest**

```bash
pytest tests/test_smoke.py -v
```
Expected:
```
tests/test_smoke.py::test_pytest_funciona PASSED
tests/test_smoke.py::test_imports_basicos PASSED

2 passed in 0.5s
```

- [ ] **Step 4: Probar que las fixtures de limpieza funcionan**

Agregar al final de `tests/test_smoke.py`:
```python
def test_postgres_clean_fixture(postgres_clean):
    """Verifica que la fixture limpia Postgres sin errores."""
    from src.db.postgres import get_conn
    with get_conn().cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM usuario")
        assert cur.fetchone()[0] == 0


def test_mongo_clean_fixture(mongo_clean):
    """Verifica que la fixture limpia Mongo sin errores."""
    from src.db.mongo import get_db
    assert get_db().viajes.count_documents({}) == 0


def test_cassandra_clean_fixture(cassandra_clean):
    """Verifica que la fixture limpia Cassandra sin errores."""
    from src.db.cassandra import get_session
    rows = list(get_session().execute("SELECT * FROM ultima_actividad_conductor LIMIT 1"))
    assert rows == []


def test_neo4j_clean_fixture(neo4j_clean):
    """Verifica que la fixture limpia Neo4j sin errores."""
    from src.db.neo4j_db import get_driver
    with get_driver().session() as s:
        count = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        assert count == 0


def test_redis_clean_fixture(redis_clean):
    """Verifica que la fixture limpia Redis sin errores."""
    from src.db.redis_db import get_client
    assert get_client().dbsize() == 0
```

- [ ] **Step 5: Correr de nuevo**

```bash
pytest tests/test_smoke.py -v
```
Expected: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add tests/conftest.py tests/test_smoke.py
git commit -m "agregar conftest.py con fixtures de limpieza para las 5 bases + smoke tests"
git push
```

---

## Sección 1 — Repositories de Postgres

> **Patrón general** para cada función dentro de un repository:
> 1. Escribir test que falla (la función no existe todavía).
> 2. Correr el test, verificar que falla con `AttributeError` o `NameError`.
> 3. Implementar la función mínima para que pase.
> 4. Correr el test, verificar que pasa.
> 5. Repetir para la siguiente función.
> 6. Al final del repository, **un solo commit** con todo el archivo + sus tests.

### Task 1.1: `usuario_repo` (Postgres)

**Files:**
- Create: `src/repositories/usuario_repo.py`
- Create: `tests/repositories/test_usuario_repo.py`

**Funciones a implementar:**
- `crear(email, password_hash, nombre, telefono=None, foto_url=None) → str` (id)
- `get_by_id(id) → dict | None`
- `get_by_email(email) → dict | None`
- `actualizar_rating(id, nuevo_rating) → bool`
- `listar_todos() → list[dict]`
- `existe(id) → bool`

- [ ] **Step 1: Escribir el archivo de tests completo**

Crear `tests/repositories/test_usuario_repo.py`:
```python
"""Tests del usuario_repo (Postgres)."""
import pytest


# ---- crear ----

def test_crear_devuelve_id(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("juan@mail.com", "hash123", "Juan Pérez")
    assert id is not None
    assert len(id) == 36  # UUID


def test_crear_persiste_los_datos(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("ana@mail.com", "hash456", "Ana Gómez", "+541112345678")
    user = usuario_repo.get_by_id(id)
    assert user["email"] == "ana@mail.com"
    assert user["nombre"] == "Ana Gómez"
    assert user["telefono"] == "+541112345678"


def test_crear_email_duplicado_lanza_error(postgres_clean):
    from src.repositories import usuario_repo
    import psycopg
    usuario_repo.crear("dup@mail.com", "hash", "Primer Juan")
    with pytest.raises(psycopg.errors.UniqueViolation):
        usuario_repo.crear("dup@mail.com", "hash2", "Segundo Juan")


# ---- get_by_id ----

def test_get_by_id_no_existente_devuelve_none(postgres_clean):
    from src.repositories import usuario_repo
    assert usuario_repo.get_by_id("00000000-0000-0000-0000-000000000000") is None


def test_get_by_id_existente_devuelve_dict(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("test@mail.com", "h", "Test")
    user = usuario_repo.get_by_id(id)
    assert user is not None
    assert user["id"] == id
    assert user["email"] == "test@mail.com"


# ---- get_by_email ----

def test_get_by_email_existente(postgres_clean):
    from src.repositories import usuario_repo
    usuario_repo.crear("mail@mail.com", "h", "Mail")
    user = usuario_repo.get_by_email("mail@mail.com")
    assert user["nombre"] == "Mail"


def test_get_by_email_no_existente(postgres_clean):
    from src.repositories import usuario_repo
    assert usuario_repo.get_by_email("inexistente@mail.com") is None


# ---- actualizar_rating ----

def test_actualizar_rating_existente(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("rate@mail.com", "h", "Rate")
    ok = usuario_repo.actualizar_rating(id, 4.5)
    assert ok is True
    assert usuario_repo.get_by_id(id)["rating_promedio"] == pytest.approx(4.5)


def test_actualizar_rating_no_existente(postgres_clean):
    from src.repositories import usuario_repo
    ok = usuario_repo.actualizar_rating("00000000-0000-0000-0000-000000000000", 5)
    assert ok is False


# ---- listar_todos ----

def test_listar_todos_vacio(postgres_clean):
    from src.repositories import usuario_repo
    assert usuario_repo.listar_todos() == []


def test_listar_todos_con_varios(postgres_clean):
    from src.repositories import usuario_repo
    usuario_repo.crear("a@mail.com", "h", "A")
    usuario_repo.crear("b@mail.com", "h", "B")
    usuario_repo.crear("c@mail.com", "h", "C")
    todos = usuario_repo.listar_todos()
    assert len(todos) == 3
    emails = sorted(u["email"] for u in todos)
    assert emails == ["a@mail.com", "b@mail.com", "c@mail.com"]


# ---- existe ----

def test_existe_true(postgres_clean):
    from src.repositories import usuario_repo
    id = usuario_repo.crear("e@mail.com", "h", "E")
    assert usuario_repo.existe(id) is True


def test_existe_false(postgres_clean):
    from src.repositories import usuario_repo
    assert usuario_repo.existe("00000000-0000-0000-0000-000000000000") is False
```

- [ ] **Step 2: Correr los tests — verificar que TODOS fallan**

```bash
pytest tests/repositories/test_usuario_repo.py -v
```
Expected: 13 tests, todos FAIL con `AttributeError: module 'src.repositories' has no attribute 'usuario_repo'`.

- [ ] **Step 3: Implementar `src/repositories/usuario_repo.py`**

```python
"""Repository de Usuario (Postgres).

Solo CRUD y queries. Sin lógica de negocio.
"""
from src.db.postgres import get_conn


def crear(email: str, password_hash: str, nombre: str,
          telefono: str | None = None, foto_url: str | None = None) -> str:
    """Inserta un nuevo usuario y devuelve su id (UUID como str)."""
    sql = """
        INSERT INTO usuario (email, password_hash, nombre, telefono, foto_url)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id::text
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (email, password_hash, nombre, telefono, foto_url))
        return cur.fetchone()[0]


def get_by_id(id: str) -> dict | None:
    """Devuelve el usuario o None."""
    sql = """
        SELECT id::text, email, password_hash, nombre, telefono, foto_url,
               rating_promedio, fecha_registro, estado
        FROM usuario WHERE id = %s
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def get_by_email(email: str) -> dict | None:
    """Devuelve el usuario por email o None."""
    sql = """
        SELECT id::text, email, password_hash, nombre, telefono, foto_url,
               rating_promedio, fecha_registro, estado
        FROM usuario WHERE email = %s
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (email,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def actualizar_rating(id: str, nuevo_rating: float) -> bool:
    """Actualiza rating_promedio. Devuelve True si modificó una fila."""
    sql = "UPDATE usuario SET rating_promedio = %s WHERE id = %s"
    with get_conn().cursor() as cur:
        cur.execute(sql, (nuevo_rating, id))
        return cur.rowcount == 1


def listar_todos() -> list[dict]:
    """Devuelve todos los usuarios (lista vacía si no hay)."""
    sql = """
        SELECT id::text, email, nombre, telefono, rating_promedio, estado
        FROM usuario ORDER BY fecha_registro
    """
    with get_conn().cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def existe(id: str) -> bool:
    """Devuelve True si existe un usuario con ese id."""
    sql = "SELECT 1 FROM usuario WHERE id = %s"
    with get_conn().cursor() as cur:
        cur.execute(sql, (id,))
        return cur.fetchone() is not None
```

- [ ] **Step 4: Correr los tests — verificar que TODOS pasan**

```bash
pytest tests/repositories/test_usuario_repo.py -v
```
Expected: 13 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/usuario_repo.py tests/repositories/test_usuario_repo.py
git commit -m "agregar usuario_repo con CRUD basico + tests de integracion (13 tests)"
git push
```

---

### Task 1.2: `conductor_repo` (Postgres)

**Files:**
- Create: `src/repositories/conductor_repo.py`
- Create: `tests/repositories/test_conductor_repo.py`

**Funciones a implementar:**
- `crear(email, password_hash, nombre, nro_licencia, telefono=None) → str` (id)
- `get_by_id(id) → dict | None`
- `get_by_email(email) → dict | None`
- `actualizar_rating(id, nuevo_rating) → bool`
- `listar_todos() → list[dict]`
- `listar_activos() → list[dict]`
- `existe(id) → bool`

- [ ] **Step 1: Escribir el archivo de tests**

Crear `tests/repositories/test_conductor_repo.py`:
```python
"""Tests del conductor_repo (Postgres)."""
import pytest


def test_crear_devuelve_id(postgres_clean):
    from src.repositories import conductor_repo
    id = conductor_repo.crear("ana@mail.com", "h", "Ana", "LIC-001")
    assert id is not None and len(id) == 36


def test_crear_persiste_los_datos(postgres_clean):
    from src.repositories import conductor_repo
    id = conductor_repo.crear("p@mail.com", "h", "Pedro", "LIC-002", "+54999")
    c = conductor_repo.get_by_id(id)
    assert c["email"] == "p@mail.com"
    assert c["nro_licencia"] == "LIC-002"
    assert c["telefono"] == "+54999"


def test_crear_licencia_duplicada_lanza_error(postgres_clean):
    from src.repositories import conductor_repo
    import psycopg
    conductor_repo.crear("c1@mail.com", "h", "C1", "LIC-DUP")
    with pytest.raises(psycopg.errors.UniqueViolation):
        conductor_repo.crear("c2@mail.com", "h", "C2", "LIC-DUP")


def test_get_by_id_no_existente(postgres_clean):
    from src.repositories import conductor_repo
    assert conductor_repo.get_by_id("00000000-0000-0000-0000-000000000000") is None


def test_get_by_email_existente(postgres_clean):
    from src.repositories import conductor_repo
    conductor_repo.crear("e@mail.com", "h", "E", "LIC-E")
    c = conductor_repo.get_by_email("e@mail.com")
    assert c["nro_licencia"] == "LIC-E"


def test_actualizar_rating_existente(postgres_clean):
    from src.repositories import conductor_repo
    id = conductor_repo.crear("r@mail.com", "h", "R", "LIC-R")
    ok = conductor_repo.actualizar_rating(id, 4.8)
    assert ok is True
    assert conductor_repo.get_by_id(id)["rating_promedio"] == pytest.approx(4.8)


def test_listar_todos_vacio(postgres_clean):
    from src.repositories import conductor_repo
    assert conductor_repo.listar_todos() == []


def test_listar_todos_con_varios(postgres_clean):
    from src.repositories import conductor_repo
    conductor_repo.crear("a@m.com", "h", "A", "L1")
    conductor_repo.crear("b@m.com", "h", "B", "L2")
    assert len(conductor_repo.listar_todos()) == 2


def test_listar_activos_excluye_baja(postgres_clean):
    from src.repositories import conductor_repo
    from src.db.postgres import get_conn
    id1 = conductor_repo.crear("act@m.com", "h", "Act", "L-ACT")
    id2 = conductor_repo.crear("baj@m.com", "h", "Baj", "L-BAJ")
    with get_conn().cursor() as cur:
        cur.execute("UPDATE conductor SET estado = 'BAJA' WHERE id = %s", (id2,))
    activos = conductor_repo.listar_activos()
    ids = [c["id"] for c in activos]
    assert id1 in ids
    assert id2 not in ids


def test_existe_true_y_false(postgres_clean):
    from src.repositories import conductor_repo
    id = conductor_repo.crear("e@m.com", "h", "E", "L-E")
    assert conductor_repo.existe(id) is True
    assert conductor_repo.existe("00000000-0000-0000-0000-000000000000") is False
```

- [ ] **Step 2: Correr los tests — todos deben fallar**

```bash
pytest tests/repositories/test_conductor_repo.py -v
```
Expected: 10 tests, todos FAIL.

- [ ] **Step 3: Implementar `src/repositories/conductor_repo.py`**

```python
"""Repository de Conductor (Postgres)."""
from src.db.postgres import get_conn

_COLS_FULL = """
    id::text, email, password_hash, nombre, telefono, nro_licencia,
    rating_promedio, estado, fecha_registro
"""


def crear(email: str, password_hash: str, nombre: str, nro_licencia: str,
          telefono: str | None = None) -> str:
    sql = """
        INSERT INTO conductor (email, password_hash, nombre, nro_licencia, telefono)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id::text
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (email, password_hash, nombre, nro_licencia, telefono))
        return cur.fetchone()[0]


def get_by_id(id: str) -> dict | None:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS_FULL} FROM conductor WHERE id = %s", (id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def get_by_email(email: str) -> dict | None:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS_FULL} FROM conductor WHERE email = %s", (email,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def actualizar_rating(id: str, nuevo_rating: float) -> bool:
    sql = "UPDATE conductor SET rating_promedio = %s WHERE id = %s"
    with get_conn().cursor() as cur:
        cur.execute(sql, (nuevo_rating, id))
        return cur.rowcount == 1


def listar_todos() -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS_FULL} FROM conductor ORDER BY fecha_registro")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def listar_activos() -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS_FULL} FROM conductor WHERE estado = 'ACTIVO' ORDER BY fecha_registro")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def existe(id: str) -> bool:
    with get_conn().cursor() as cur:
        cur.execute("SELECT 1 FROM conductor WHERE id = %s", (id,))
        return cur.fetchone() is not None
```

- [ ] **Step 4: Correr los tests — deben pasar todos**

```bash
pytest tests/repositories/test_conductor_repo.py -v
```
Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/conductor_repo.py tests/repositories/test_conductor_repo.py
git commit -m "agregar conductor_repo con CRUD + listar_activos + tests (10 tests)"
git push
```

---

### Task 1.3: `vehiculo_repo` (Postgres)

**Files:**
- Create: `src/repositories/vehiculo_repo.py`
- Create: `tests/repositories/test_vehiculo_repo.py`

**Funciones:**
- `crear(conductor_id, placa, marca, modelo, anio=None, color=None, tipo=None) → str`
- `get_by_id(id) → dict | None`
- `get_by_placa(placa) → dict | None`
- `listar_por_conductor(conductor_id) → list[dict]`
- `listar_todos() → list[dict]`
- `existe(id) → bool`

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_vehiculo_repo.py`:
```python
"""Tests del vehiculo_repo (Postgres)."""
import pytest


def _crear_conductor():
    from src.repositories import conductor_repo
    return conductor_repo.crear("c@mail.com", "h", "Conductor Test", f"LIC-{id(object())}")


def test_crear_devuelve_id(postgres_clean):
    from src.repositories import vehiculo_repo
    cid = _crear_conductor()
    vid = vehiculo_repo.crear(cid, "ABC123D", "Toyota", "Corolla", 2020, "azul", "sedan")
    assert vid is not None and len(vid) == 36


def test_crear_sin_conductor_lanza_error(postgres_clean):
    from src.repositories import vehiculo_repo
    import psycopg
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        vehiculo_repo.crear("00000000-0000-0000-0000-000000000000", "XYZ", "Marca", "Modelo")


def test_crear_placa_duplicada_lanza_error(postgres_clean):
    from src.repositories import vehiculo_repo
    import psycopg
    cid = _crear_conductor()
    vehiculo_repo.crear(cid, "DUP123", "M", "M1")
    with pytest.raises(psycopg.errors.UniqueViolation):
        vehiculo_repo.crear(cid, "DUP123", "M", "M2")


def test_get_by_id(postgres_clean):
    from src.repositories import vehiculo_repo
    cid = _crear_conductor()
    vid = vehiculo_repo.crear(cid, "PLT001", "Honda", "Civic", 2021)
    v = vehiculo_repo.get_by_id(vid)
    assert v["placa"] == "PLT001"
    assert v["marca"] == "Honda"
    assert v["anio"] == 2021


def test_get_by_placa(postgres_clean):
    from src.repositories import vehiculo_repo
    cid = _crear_conductor()
    vehiculo_repo.crear(cid, "BUSCAR1", "M", "M")
    v = vehiculo_repo.get_by_placa("BUSCAR1")
    assert v is not None
    assert v["placa"] == "BUSCAR1"


def test_get_by_placa_no_existente(postgres_clean):
    from src.repositories import vehiculo_repo
    assert vehiculo_repo.get_by_placa("NOEXISTE") is None


def test_listar_por_conductor(postgres_clean):
    from src.repositories import vehiculo_repo
    cid_a = _crear_conductor()
    cid_b = _crear_conductor()
    vehiculo_repo.crear(cid_a, "A1", "M", "M")
    vehiculo_repo.crear(cid_a, "A2", "M", "M")
    vehiculo_repo.crear(cid_b, "B1", "M", "M")
    vehiculos_a = vehiculo_repo.listar_por_conductor(cid_a)
    assert len(vehiculos_a) == 2
    assert all(v["conductor_id"] == cid_a for v in vehiculos_a)


def test_existe(postgres_clean):
    from src.repositories import vehiculo_repo
    cid = _crear_conductor()
    vid = vehiculo_repo.crear(cid, "EXISTE", "M", "M")
    assert vehiculo_repo.existe(vid) is True
    assert vehiculo_repo.existe("00000000-0000-0000-0000-000000000000") is False
```

- [ ] **Step 2: Correr tests — deben fallar**

```bash
pytest tests/repositories/test_vehiculo_repo.py -v
```
Expected: 8 tests, todos FAIL.

- [ ] **Step 3: Implementar `src/repositories/vehiculo_repo.py`**

```python
"""Repository de Vehiculo (Postgres)."""
from src.db.postgres import get_conn

_COLS = """
    id::text, conductor_id::text, placa, marca, modelo,
    anio, color, tipo
"""


def crear(conductor_id: str, placa: str, marca: str, modelo: str,
          anio: int | None = None, color: str | None = None,
          tipo: str | None = None) -> str:
    sql = """
        INSERT INTO vehiculo (conductor_id, placa, marca, modelo, anio, color, tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id::text
    """
    with get_conn().cursor() as cur:
        cur.execute(sql, (conductor_id, placa, marca, modelo, anio, color, tipo))
        return cur.fetchone()[0]


def get_by_id(id: str) -> dict | None:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS} FROM vehiculo WHERE id = %s", (id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def get_by_placa(placa: str) -> dict | None:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS} FROM vehiculo WHERE placa = %s", (placa,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def listar_por_conductor(conductor_id: str) -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS} FROM vehiculo WHERE conductor_id = %s", (conductor_id,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def listar_todos() -> list[dict]:
    with get_conn().cursor() as cur:
        cur.execute(f"SELECT {_COLS} FROM vehiculo")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def existe(id: str) -> bool:
    with get_conn().cursor() as cur:
        cur.execute("SELECT 1 FROM vehiculo WHERE id = %s", (id,))
        return cur.fetchone() is not None
```

- [ ] **Step 4: Correr tests — deben pasar todos**

```bash
pytest tests/repositories/test_vehiculo_repo.py -v
```
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/vehiculo_repo.py tests/repositories/test_vehiculo_repo.py
git commit -m "agregar vehiculo_repo con CRUD + listar_por_conductor + tests (8 tests)"
git push
```

---

## Sección 2 — Repositories de MongoDB

### Task 2.1: `viaje_repo` (Mongo)

**Files:**
- Create: `src/repositories/viaje_repo.py`
- Create: `tests/repositories/test_viaje_repo.py`

**Funciones:**
- `crear(viaje_doc) → str` (ObjectId como str)
- `get_by_id(id) → dict | None`
- `iniciar(id) → bool` (PENDIENTE → EN_CURSO)
- `finalizar(id, distancia_km, duracion_min) → bool` (EN_CURSO → FINALIZADO)
- `listar_finalizados_por_conductor(conductor_id) → list[dict]`
- `contar_por_pareja(usuario_id, conductor_id) → int`
- `listar_finalizados() → list[dict]`

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_viaje_repo.py`:
```python
"""Tests del viaje_repo (Mongo)."""
import pytest
from datetime import datetime, UTC


def _viaje_template(usuario_id="u1", conductor_id="c1", vehiculo_id="v1",
                    estado="PENDIENTE"):
    return {
        "usuario_id": usuario_id,
        "conductor_id": conductor_id,
        "vehiculo_id": vehiculo_id,
        "origen": {"lat": -34.6, "lon": -58.4, "direccion": "Palermo"},
        "destino": {"lat": -34.55, "lon": -58.45, "direccion": "Belgrano"},
        "estado": estado,
        "ts_solicitud": datetime.now(UTC),
        "usuario_snapshot": {"nombre": "Test User", "rating": 0},
        "conductor_snapshot": {"nombre": "Test Driver", "rating": 0},
    }


def test_crear_devuelve_id(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template())
    assert vid is not None
    assert len(vid) == 24  # ObjectId hex string


def test_get_by_id_existente(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(usuario_id="UID-123"))
    v = viaje_repo.get_by_id(vid)
    assert v["usuario_id"] == "UID-123"


def test_get_by_id_no_existente(mongo_clean):
    from src.repositories import viaje_repo
    assert viaje_repo.get_by_id("507f1f77bcf86cd799439011") is None


def test_iniciar_viaje_pendiente(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(estado="PENDIENTE"))
    ok = viaje_repo.iniciar(vid)
    assert ok is True
    assert viaje_repo.get_by_id(vid)["estado"] == "EN_CURSO"


def test_iniciar_viaje_ya_iniciado_falla(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(estado="EN_CURSO"))
    ok = viaje_repo.iniciar(vid)
    assert ok is False


def test_finalizar_viaje_en_curso(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(estado="EN_CURSO"))
    ok = viaje_repo.finalizar(vid, distancia_km=8.5, duracion_min=22)
    assert ok is True
    v = viaje_repo.get_by_id(vid)
    assert v["estado"] == "FINALIZADO"
    assert v["distancia_km"] == 8.5
    assert v["duracion_min"] == 22
    assert v["ts_fin"] is not None


def test_finalizar_viaje_pendiente_falla(mongo_clean):
    from src.repositories import viaje_repo
    vid = viaje_repo.crear(_viaje_template(estado="PENDIENTE"))
    ok = viaje_repo.finalizar(vid, 5, 10)
    assert ok is False


def test_listar_finalizados_por_conductor(mongo_clean):
    from src.repositories import viaje_repo
    vid1 = viaje_repo.crear(_viaje_template(conductor_id="CON-X", estado="EN_CURSO"))
    viaje_repo.finalizar(vid1, 5, 10)
    vid2 = viaje_repo.crear(_viaje_template(conductor_id="CON-X", estado="EN_CURSO"))
    viaje_repo.finalizar(vid2, 5, 10)
    viaje_repo.crear(_viaje_template(conductor_id="CON-Y", estado="EN_CURSO"))
    viajes_x = viaje_repo.listar_finalizados_por_conductor("CON-X")
    assert len(viajes_x) == 2


def test_contar_por_pareja(mongo_clean):
    from src.repositories import viaje_repo
    for _ in range(3):
        vid = viaje_repo.crear(_viaje_template(usuario_id="U", conductor_id="C", estado="EN_CURSO"))
        viaje_repo.finalizar(vid, 5, 10)
    viaje_repo.crear(_viaje_template(usuario_id="U", conductor_id="OTRO", estado="PENDIENTE"))
    assert viaje_repo.contar_por_pareja("U", "C") == 3
    assert viaje_repo.contar_por_pareja("U", "OTRO") == 0  # no finalizados
```

- [ ] **Step 2: Correr tests — deben fallar**

```bash
pytest tests/repositories/test_viaje_repo.py -v
```
Expected: 9 FAIL.

- [ ] **Step 3: Implementar `src/repositories/viaje_repo.py`**

```python
"""Repository de Viaje (Mongo)."""
from datetime import datetime, UTC
from bson import ObjectId
from src.db.mongo import get_db


def _coll():
    return get_db().viajes


def crear(viaje_doc: dict) -> str:
    """Inserta el documento y devuelve el _id como str."""
    return str(_coll().insert_one(viaje_doc).inserted_id)


def get_by_id(id: str) -> dict | None:
    """Devuelve el viaje por id (ObjectId str) o None."""
    try:
        oid = ObjectId(id)
    except Exception:
        return None
    doc = _coll().find_one({"_id": oid})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def iniciar(id: str) -> bool:
    """Transición PENDIENTE → EN_CURSO. True si modificó."""
    res = _coll().update_one(
        {"_id": ObjectId(id), "estado": "PENDIENTE"},
        {"$set": {"estado": "EN_CURSO", "ts_inicio": datetime.now(UTC)}}
    )
    return res.modified_count == 1


def finalizar(id: str, distancia_km: float, duracion_min: int) -> bool:
    """Transición EN_CURSO → FINALIZADO. True si modificó."""
    res = _coll().update_one(
        {"_id": ObjectId(id), "estado": "EN_CURSO"},
        {"$set": {
            "estado": "FINALIZADO",
            "distancia_km": distancia_km,
            "duracion_min": duracion_min,
            "ts_fin": datetime.now(UTC),
        }}
    )
    return res.modified_count == 1


def listar_finalizados_por_conductor(conductor_id: str) -> list[dict]:
    docs = _coll().find({"conductor_id": conductor_id, "estado": "FINALIZADO"})
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result


def contar_por_pareja(usuario_id: str, conductor_id: str) -> int:
    return _coll().count_documents({
        "usuario_id": usuario_id,
        "conductor_id": conductor_id,
        "estado": "FINALIZADO",
    })


def listar_finalizados() -> list[dict]:
    docs = _coll().find({"estado": "FINALIZADO"})
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result
```

- [ ] **Step 4: Correr tests**

```bash
pytest tests/repositories/test_viaje_repo.py -v
```
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/viaje_repo.py tests/repositories/test_viaje_repo.py
git commit -m "agregar viaje_repo con transiciones de estado y queries + tests (9 tests)"
git push
```

---

### Task 2.2: `pago_repo` (Mongo)

**Files:**
- Create: `src/repositories/pago_repo.py`
- Create: `tests/repositories/test_pago_repo.py`

**Funciones:**
- `crear(pago_doc) → str`
- `get_by_id(id) → dict | None`
- `get_by_viaje_id(viaje_id) → dict | None`
- `contar_por_metodo() → dict` (ej. `{"TARJETA": 5, "EFECTIVO": 3}`)
- `metodo_menos_usado() → str | None` (devuelve el nombre del método con menos pagos)

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_pago_repo.py`:
```python
"""Tests del pago_repo (Mongo)."""
from datetime import datetime, UTC


def _pago_template(viaje_id="v1", metodo="TARJETA", monto=2500):
    return {
        "viaje_id": viaje_id,
        "monto_total": monto,
        "tarifa_base": 500,
        "tarifa_distancia": 1200,
        "tarifa_tiempo": 600,
        "cargos_extra": monto - 2300,
        "metodo_pago": metodo,
        "estado": "APROBADO",
        "timestamp": datetime.now(UTC),
    }


def test_crear_devuelve_id(mongo_clean):
    from src.repositories import pago_repo
    pid = pago_repo.crear(_pago_template())
    assert pid is not None and len(pid) == 24


def test_get_by_id(mongo_clean):
    from src.repositories import pago_repo
    pid = pago_repo.crear(_pago_template(monto=3000))
    p = pago_repo.get_by_id(pid)
    assert p["monto_total"] == 3000


def test_get_by_viaje_id(mongo_clean):
    from src.repositories import pago_repo
    pago_repo.crear(_pago_template(viaje_id="VIAJE-X"))
    p = pago_repo.get_by_viaje_id("VIAJE-X")
    assert p is not None
    assert p["viaje_id"] == "VIAJE-X"


def test_get_by_viaje_id_no_existente(mongo_clean):
    from src.repositories import pago_repo
    assert pago_repo.get_by_viaje_id("NO-EXISTE") is None


def test_contar_por_metodo(mongo_clean):
    from src.repositories import pago_repo
    for _ in range(3):
        pago_repo.crear(_pago_template(metodo="TARJETA"))
    for _ in range(2):
        pago_repo.crear(_pago_template(metodo="EFECTIVO"))
    pago_repo.crear(_pago_template(metodo="BILLETERA_VIRTUAL"))
    counts = pago_repo.contar_por_metodo()
    assert counts == {"TARJETA": 3, "EFECTIVO": 2, "BILLETERA_VIRTUAL": 1}


def test_metodo_menos_usado(mongo_clean):
    from src.repositories import pago_repo
    for _ in range(3):
        pago_repo.crear(_pago_template(metodo="TARJETA"))
    pago_repo.crear(_pago_template(metodo="EFECTIVO"))
    assert pago_repo.metodo_menos_usado() == "EFECTIVO"


def test_metodo_menos_usado_sin_pagos(mongo_clean):
    from src.repositories import pago_repo
    assert pago_repo.metodo_menos_usado() is None
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/repositories/test_pago_repo.py -v
```
Expected: 7 FAIL.

- [ ] **Step 3: Implementar `src/repositories/pago_repo.py`**

```python
"""Repository de Pago (Mongo)."""
from bson import ObjectId
from src.db.mongo import get_db


def _coll():
    return get_db().pagos


def crear(pago_doc: dict) -> str:
    return str(_coll().insert_one(pago_doc).inserted_id)


def get_by_id(id: str) -> dict | None:
    try:
        oid = ObjectId(id)
    except Exception:
        return None
    doc = _coll().find_one({"_id": oid})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def get_by_viaje_id(viaje_id: str) -> dict | None:
    doc = _coll().find_one({"viaje_id": viaje_id})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def contar_por_metodo() -> dict:
    """Devuelve {metodo_pago: cantidad}."""
    pipeline = [
        {"$group": {"_id": "$metodo_pago", "c": {"$sum": 1}}},
    ]
    return {doc["_id"]: doc["c"] for doc in _coll().aggregate(pipeline)}


def metodo_menos_usado() -> str | None:
    """Caso de uso 2: método con menos pagos."""
    pipeline = [
        {"$group": {"_id": "$metodo_pago", "c": {"$sum": 1}}},
        {"$sort": {"c": 1}},
        {"$limit": 1},
    ]
    result = list(_coll().aggregate(pipeline))
    return result[0]["_id"] if result else None
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/repositories/test_pago_repo.py -v
```
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/pago_repo.py tests/repositories/test_pago_repo.py
git commit -m "agregar pago_repo con CRUD + agregaciones para caso de uso 2 (7 tests)"
git push
```

---

### Task 2.3: `resena_repo` (Mongo)

**Files:**
- Create: `src/repositories/resena_repo.py`
- Create: `tests/repositories/test_resena_repo.py`

**Funciones:**
- `crear(resena_doc) → str`
- `get_by_id(id) → dict | None`
- `top_autores(n=3, tipo='U_A_C') → list[dict]` (caso de uso 1)
- `buscar_por_rating(rating_5_o_menor_a=2) → list[dict]` (caso de uso 7)
- `ratings_de_destinatario(destinatario_id) → list[int]` (para recalcular promedio)

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_resena_repo.py`:
```python
"""Tests del resena_repo (Mongo)."""
from datetime import datetime, UTC


def _resena_template(autor_id="A1", destinatario_id="D1", rating=5,
                     tipo="U_A_C", viaje_id="V1"):
    return {
        "viaje_id": viaje_id,
        "tipo": tipo,
        "autor": {"id": autor_id, "nombre": f"Autor {autor_id}"},
        "destinatario": {"id": destinatario_id, "nombre": f"Dest {destinatario_id}"},
        "rating": rating,
        "comentario": "Comentario de prueba",
        "timestamp": datetime.now(UTC),
        "contexto_viaje": {"origen": "A", "destino": "B", "duracion_min": 20},
    }


def test_crear_devuelve_id(mongo_clean):
    from src.repositories import resena_repo
    rid = resena_repo.crear(_resena_template())
    assert rid is not None and len(rid) == 24


def test_get_by_id(mongo_clean):
    from src.repositories import resena_repo
    rid = resena_repo.crear(_resena_template(rating=4))
    r = resena_repo.get_by_id(rid)
    assert r["rating"] == 4


def test_top_autores_devuelve_top_3(mongo_clean):
    from src.repositories import resena_repo
    # Autor A: 5 reseñas; Autor B: 3; Autor C: 2; Autor D: 1
    for _ in range(5):
        resena_repo.crear(_resena_template(autor_id="A"))
    for _ in range(3):
        resena_repo.crear(_resena_template(autor_id="B"))
    for _ in range(2):
        resena_repo.crear(_resena_template(autor_id="C"))
    resena_repo.crear(_resena_template(autor_id="D"))
    top = resena_repo.top_autores(n=3, tipo="U_A_C")
    assert [t["autor_id"] for t in top] == ["A", "B", "C"]
    assert top[0]["cantidad"] == 5


def test_top_autores_filtra_por_tipo(mongo_clean):
    from src.repositories import resena_repo
    for _ in range(5):
        resena_repo.crear(_resena_template(autor_id="A", tipo="U_A_C"))
    for _ in range(10):
        resena_repo.crear(_resena_template(autor_id="X", tipo="C_A_U"))
    top = resena_repo.top_autores(n=3, tipo="U_A_C")
    assert top[0]["autor_id"] == "A"
    assert all(t["autor_id"] != "X" for t in top)


def test_buscar_por_rating_5_o_menor_2(mongo_clean):
    from src.repositories import resena_repo
    resena_repo.crear(_resena_template(rating=5))
    resena_repo.crear(_resena_template(rating=1))
    resena_repo.crear(_resena_template(rating=3))  # excluido
    resena_repo.crear(_resena_template(rating=4))  # excluido
    extremos = resena_repo.buscar_por_rating_extremo()
    assert len(extremos) == 2
    ratings = sorted(r["rating"] for r in extremos)
    assert ratings == [1, 5]


def test_ratings_de_destinatario(mongo_clean):
    from src.repositories import resena_repo
    resena_repo.crear(_resena_template(destinatario_id="DEST", rating=5))
    resena_repo.crear(_resena_template(destinatario_id="DEST", rating=4))
    resena_repo.crear(_resena_template(destinatario_id="DEST", rating=3))
    resena_repo.crear(_resena_template(destinatario_id="OTRO", rating=1))
    ratings = resena_repo.ratings_de_destinatario("DEST")
    assert sorted(ratings) == [3, 4, 5]
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/repositories/test_resena_repo.py -v
```
Expected: 6 FAIL.

- [ ] **Step 3: Implementar `src/repositories/resena_repo.py`**

```python
"""Repository de Resena (Mongo)."""
from bson import ObjectId
from src.db.mongo import get_db


def _coll():
    return get_db().resenas


def crear(resena_doc: dict) -> str:
    return str(_coll().insert_one(resena_doc).inserted_id)


def get_by_id(id: str) -> dict | None:
    try:
        oid = ObjectId(id)
    except Exception:
        return None
    doc = _coll().find_one({"_id": oid})
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


def top_autores(n: int = 3, tipo: str = "U_A_C") -> list[dict]:
    """Caso de uso 1: top N autores con más reseñas del tipo dado."""
    pipeline = [
        {"$match": {"tipo": tipo}},
        {"$group": {"_id": "$autor.id", "cantidad": {"$sum": 1}}},
        {"$sort": {"cantidad": -1}},
        {"$limit": n},
    ]
    return [
        {"autor_id": doc["_id"], "cantidad": doc["cantidad"]}
        for doc in _coll().aggregate(pipeline)
    ]


def buscar_por_rating_extremo() -> list[dict]:
    """Caso de uso 7: reseñas con rating = 5 o rating < 2."""
    docs = _coll().find({"$or": [{"rating": 5}, {"rating": {"$lt": 2}}]})
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result


def ratings_de_destinatario(destinatario_id: str) -> list[int]:
    """Devuelve la lista de ratings de un destinatario (para recalcular promedio)."""
    cursor = _coll().find(
        {"destinatario.id": destinatario_id},
        projection={"_id": 0, "rating": 1}
    )
    return [d["rating"] for d in cursor]
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/repositories/test_resena_repo.py -v
```
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/resena_repo.py tests/repositories/test_resena_repo.py
git commit -m "agregar resena_repo con queries para casos de uso 1 y 7 (6 tests)"
git push
```

---

### Task 2.4: `login_history_repo` (Mongo)

**Files:**
- Create: `src/repositories/login_history_repo.py`
- Create: `tests/repositories/test_login_history_repo.py`

**Funciones:**
- `crear(usuario_id, tipo_cuenta, evento, ip=None) → str`
- `listar_por_usuario(usuario_id, limit=10) → list[dict]`

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_login_history_repo.py`:
```python
"""Tests del login_history_repo (Mongo)."""


def test_crear_devuelve_id(mongo_clean):
    from src.repositories import login_history_repo
    rid = login_history_repo.crear("U1", "USUARIO", "LOGIN_OK", "190.x.x.x")
    assert rid is not None and len(rid) == 24


def test_listar_por_usuario(mongo_clean):
    from src.repositories import login_history_repo
    login_history_repo.crear("U1", "USUARIO", "LOGIN_OK")
    login_history_repo.crear("U1", "USUARIO", "LOGOUT")
    login_history_repo.crear("U2", "USUARIO", "LOGIN_OK")
    eventos = login_history_repo.listar_por_usuario("U1")
    assert len(eventos) == 2


def test_listar_por_usuario_orden_desc(mongo_clean):
    from src.repositories import login_history_repo
    import time
    login_history_repo.crear("U", "USUARIO", "LOGIN_OK")
    time.sleep(0.01)
    login_history_repo.crear("U", "USUARIO", "LOGOUT")
    eventos = login_history_repo.listar_por_usuario("U")
    # El más reciente primero
    assert eventos[0]["evento"] == "LOGOUT"


def test_listar_respeta_limit(mongo_clean):
    from src.repositories import login_history_repo
    for i in range(15):
        login_history_repo.crear("U", "USUARIO", "LOGIN_OK")
    eventos = login_history_repo.listar_por_usuario("U", limit=5)
    assert len(eventos) == 5
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/repositories/test_login_history_repo.py -v
```
Expected: 4 FAIL.

- [ ] **Step 3: Implementar `src/repositories/login_history_repo.py`**

```python
"""Repository de Login History (Mongo). Auditoría de logins/logouts."""
from datetime import datetime, UTC
from src.db.mongo import get_db


def _coll():
    return get_db().login_history


def crear(usuario_id: str, tipo_cuenta: str, evento: str,
          ip: str | None = None) -> str:
    """Registra un evento de login/logout/fail."""
    doc = {
        "usuario_id": usuario_id,
        "tipo_cuenta": tipo_cuenta,
        "evento": evento,
        "ip": ip,
        "timestamp": datetime.now(UTC),
    }
    return str(_coll().insert_one(doc).inserted_id)


def listar_por_usuario(usuario_id: str, limit: int = 10) -> list[dict]:
    """Devuelve los últimos N eventos de un usuario, más reciente primero."""
    docs = _coll().find({"usuario_id": usuario_id}).sort("timestamp", -1).limit(limit)
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/repositories/test_login_history_repo.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/login_history_repo.py tests/repositories/test_login_history_repo.py
git commit -m "agregar login_history_repo para auditoria de eventos de cuenta (4 tests)"
git push
```

---

## Sección 3 — Repositories de Cassandra

### Task 3.1: `ubicacion_repo` (Cassandra)

**Files:**
- Create: `src/repositories/ubicacion_repo.py`
- Create: `tests/repositories/test_ubicacion_repo.py`

**Funciones:**
- `insertar(vehiculo_id, ts, lat, lon, precision_m=None, viaje_id=None) → None`
- `historial(vehiculo_id, limit=100) → list[dict]`
- `ultima_posicion(vehiculo_id) → dict | None`

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_ubicacion_repo.py`:
```python
"""Tests del ubicacion_repo (Cassandra)."""
import uuid
from datetime import datetime, UTC, timedelta


def test_insertar_sin_error(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    ubicacion_repo.insertar(vid, datetime.now(UTC), -34.6, -58.4)
    # Sin error → OK


def test_historial_devuelve_inserts(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    base_ts = datetime.now(UTC)
    for i in range(5):
        ubicacion_repo.insertar(vid, base_ts + timedelta(seconds=i), -34.6 + i * 0.001, -58.4)
    historial = ubicacion_repo.historial(vid)
    assert len(historial) == 5


def test_historial_orden_descendente(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    base_ts = datetime.now(UTC)
    for i in range(3):
        ubicacion_repo.insertar(vid, base_ts + timedelta(seconds=i), -34.6, -58.4)
    historial = ubicacion_repo.historial(vid)
    # CLUSTERING ORDER BY (ts DESC) → primero el más reciente
    assert historial[0]["ts"] > historial[-1]["ts"]


def test_historial_vehiculo_sin_ubicaciones(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    assert ubicacion_repo.historial(vid) == []


def test_ultima_posicion_devuelve_la_mas_reciente(cassandra_clean):
    from src.repositories import ubicacion_repo
    vid = uuid.uuid4()
    base_ts = datetime.now(UTC)
    ubicacion_repo.insertar(vid, base_ts, -34.6, -58.4)
    ubicacion_repo.insertar(vid, base_ts + timedelta(seconds=10), -34.7, -58.5)
    ultima = ubicacion_repo.ultima_posicion(vid)
    assert ultima is not None
    assert float(ultima["lat"]) == pytest.approx(-34.7)


def test_ultima_posicion_sin_datos(cassandra_clean):
    from src.repositories import ubicacion_repo
    assert ubicacion_repo.ultima_posicion(uuid.uuid4()) is None


# La línea anterior usa pytest.approx, hace falta importar pytest:
import pytest  # noqa: E402
```

> **Nota:** el `import pytest` al final es deliberado para que el test de `ultima_posicion` lo tenga. Mover al top del archivo si pytest da warning.

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/repositories/test_ubicacion_repo.py -v
```
Expected: 6 FAIL.

- [ ] **Step 3: Implementar `src/repositories/ubicacion_repo.py`**

```python
"""Repository de Ubicacion (Cassandra). Time-series de posiciones GPS."""
from datetime import datetime
from uuid import UUID
from src.db.cassandra import get_session


def insertar(vehiculo_id: UUID, ts: datetime, lat: float, lon: float,
             precision_m: float | None = None, viaje_id: UUID | None = None) -> None:
    """Inserta una nueva posición GPS."""
    cql = """
        INSERT INTO ubicaciones_por_vehiculo
            (vehiculo_id, ts, lat, lon, precision_m, viaje_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    get_session().execute(cql, (vehiculo_id, ts, lat, lon, precision_m, viaje_id))


def historial(vehiculo_id: UUID, limit: int = 100) -> list[dict]:
    """Devuelve el historial GPS de un vehículo, más reciente primero."""
    cql = """
        SELECT vehiculo_id, ts, lat, lon, precision_m, viaje_id
        FROM ubicaciones_por_vehiculo
        WHERE vehiculo_id = %s
        LIMIT %s
    """
    rows = get_session().execute(cql, (vehiculo_id, limit))
    return [
        {
            "vehiculo_id": r.vehiculo_id, "ts": r.ts,
            "lat": r.lat, "lon": r.lon,
            "precision_m": r.precision_m, "viaje_id": r.viaje_id,
        }
        for r in rows
    ]


def ultima_posicion(vehiculo_id: UUID) -> dict | None:
    """Devuelve la posición más reciente o None."""
    cql = """
        SELECT vehiculo_id, ts, lat, lon, precision_m, viaje_id
        FROM ubicaciones_por_vehiculo
        WHERE vehiculo_id = %s LIMIT 1
    """
    row = get_session().execute(cql, (vehiculo_id,)).one()
    if row is None:
        return None
    return {
        "vehiculo_id": row.vehiculo_id, "ts": row.ts,
        "lat": row.lat, "lon": row.lon,
        "precision_m": row.precision_m, "viaje_id": row.viaje_id,
    }
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/repositories/test_ubicacion_repo.py -v
```
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/ubicacion_repo.py tests/repositories/test_ubicacion_repo.py
git commit -m "agregar ubicacion_repo para time-series de GPS en Cassandra (6 tests)"
git push
```

---

### Task 3.2: `actividad_repo` (Cassandra)

**Files:**
- Create: `src/repositories/actividad_repo.py`
- Create: `tests/repositories/test_actividad_repo.py`

**Funciones:**
- `upsert_ultima(conductor_id, ts, viaje_id) → None`
- `get_ultima(conductor_id) → dict | None`
- `conductores_activos_desde(fecha_limite) → list[UUID]` (conductores con `ultimo_viaje_ts >= fecha_limite`)
- `insertar_viaje_finalizado(dia, viaje_id, conductor_id, usuario_id, duracion_min, distancia_km) → None`
- `promedio_duracion() → float` (caso de uso 4)
- `viajes_finalizados_en_rango(dia) → list[dict]`

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_actividad_repo.py`:
```python
"""Tests del actividad_repo (Cassandra)."""
import pytest
import uuid
from datetime import datetime, UTC, timedelta, date


def test_upsert_ultima_inserta(cassandra_clean):
    from src.repositories import actividad_repo
    cid = uuid.uuid4()
    vid = uuid.uuid4()
    ts = datetime.now(UTC)
    actividad_repo.upsert_ultima(cid, ts, vid)
    ultima = actividad_repo.get_ultima(cid)
    assert ultima is not None
    assert ultima["ultimo_viaje_id"] == vid


def test_upsert_ultima_sobrescribe(cassandra_clean):
    from src.repositories import actividad_repo
    cid = uuid.uuid4()
    v1, v2 = uuid.uuid4(), uuid.uuid4()
    ts1 = datetime.now(UTC)
    ts2 = ts1 + timedelta(hours=1)
    actividad_repo.upsert_ultima(cid, ts1, v1)
    actividad_repo.upsert_ultima(cid, ts2, v2)
    ultima = actividad_repo.get_ultima(cid)
    assert ultima["ultimo_viaje_id"] == v2


def test_get_ultima_no_existente(cassandra_clean):
    from src.repositories import actividad_repo
    assert actividad_repo.get_ultima(uuid.uuid4()) is None


def test_conductores_activos_desde(cassandra_clean):
    from src.repositories import actividad_repo
    activo = uuid.uuid4()
    inactivo = uuid.uuid4()
    ahora = datetime.now(UTC)
    actividad_repo.upsert_ultima(activo, ahora, uuid.uuid4())
    actividad_repo.upsert_ultima(inactivo, ahora - timedelta(days=60), uuid.uuid4())
    activos = actividad_repo.conductores_activos_desde(ahora - timedelta(days=30))
    assert activo in activos
    assert inactivo not in activos


def test_insertar_viaje_finalizado_y_promedio(cassandra_clean):
    from src.repositories import actividad_repo
    hoy = date.today()
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 20, 5.0)
    actividad_repo.insertar_viaje_finalizado(hoy, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), 40, 10.0)
    promedio = actividad_repo.promedio_duracion()
    assert promedio == pytest.approx(30)


def test_promedio_sin_viajes(cassandra_clean):
    from src.repositories import actividad_repo
    assert actividad_repo.promedio_duracion() == 0
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/repositories/test_actividad_repo.py -v
```
Expected: 6 FAIL.

- [ ] **Step 3: Implementar `src/repositories/actividad_repo.py`**

```python
"""Repository de actividad (Cassandra).

Mantiene ultima_actividad_conductor (para caso 3) y
viajes_finalizados_por_dia (para caso 4).
"""
from datetime import datetime, date
from uuid import UUID
from src.db.cassandra import get_session


def upsert_ultima(conductor_id: UUID, ts: datetime, viaje_id: UUID) -> None:
    """Inserta o actualiza la última actividad del conductor."""
    cql = """
        INSERT INTO ultima_actividad_conductor
            (conductor_id, ultimo_viaje_ts, ultimo_viaje_id)
        VALUES (%s, %s, %s)
    """
    get_session().execute(cql, (conductor_id, ts, viaje_id))


def get_ultima(conductor_id: UUID) -> dict | None:
    cql = """
        SELECT conductor_id, ultimo_viaje_ts, ultimo_viaje_id
        FROM ultima_actividad_conductor WHERE conductor_id = %s
    """
    row = get_session().execute(cql, (conductor_id,)).one()
    if row is None:
        return None
    return {
        "conductor_id": row.conductor_id,
        "ultimo_viaje_ts": row.ultimo_viaje_ts,
        "ultimo_viaje_id": row.ultimo_viaje_id,
    }


def conductores_activos_desde(fecha_limite: datetime) -> list[UUID]:
    """Devuelve los conductor_ids con ultimo_viaje_ts >= fecha_limite.

    OJO: usa ALLOW FILTERING porque no hay índice secundario en ultimo_viaje_ts.
    Para el TP es aceptable; en producción se usaría una tabla denormalizada.
    """
    cql = """
        SELECT conductor_id, ultimo_viaje_ts
        FROM ultima_actividad_conductor
        WHERE ultimo_viaje_ts >= %s
        ALLOW FILTERING
    """
    rows = get_session().execute(cql, (fecha_limite,))
    return [r.conductor_id for r in rows]


def insertar_viaje_finalizado(dia: date, viaje_id: UUID, conductor_id: UUID,
                              usuario_id: UUID, duracion_min: int,
                              distancia_km: float) -> None:
    cql = """
        INSERT INTO viajes_finalizados_por_dia
            (dia, viaje_id, conductor_id, usuario_id, duracion_min, distancia_km)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    get_session().execute(cql, (dia, viaje_id, conductor_id, usuario_id,
                                duracion_min, distancia_km))


def promedio_duracion() -> float:
    """Caso de uso 4: tiempo promedio de viajes finalizados.

    Cassandra no tiene AVG nativo eficiente; se calcula en app
    (recorrido completo, OK para el volumen de un TP).
    """
    cql = "SELECT duracion_min FROM viajes_finalizados_por_dia"
    rows = list(get_session().execute(cql))
    if not rows:
        return 0
    total = sum(r.duracion_min for r in rows)
    return total / len(rows)
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/repositories/test_actividad_repo.py -v
```
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/actividad_repo.py tests/repositories/test_actividad_repo.py
git commit -m "agregar actividad_repo para casos de uso 3 y 4 en Cassandra (6 tests)"
git push
```

---

## Sección 4 — Repository de Neo4j

### Task 4.1: `grafo_repo` (Neo4j)

**Files:**
- Create: `src/repositories/grafo_repo.py`
- Create: `tests/repositories/test_grafo_repo.py`

**Funciones:**
- `crear_usuario(id, nombre, email) → None`
- `crear_conductor(id, nombre, email, rating=0) → None`
- `crear_vehiculo(id, placa, marca, modelo, anio=None) → None`
- `crear_relacion_maneja(conductor_id, vehiculo_id) → None`
- `incrementar_viajo_con(usuario_id, conductor_id) → None`
- `coincidencias(min_viajes=2) → list[dict]` (caso de uso 5)
- `vehiculos_marca_y_patente_termina(marca, sufijo) → int` (caso de uso 6)

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_grafo_repo.py`:
```python
"""Tests del grafo_repo (Neo4j)."""


def test_crear_usuario_y_existe(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_usuario("U1", "Juan", "j@m.com")
    with get_driver().session() as s:
        n = s.run("MATCH (u:Usuario {id:'U1'}) RETURN u").single()
        assert n is not None
        assert n["u"]["nombre"] == "Juan"


def test_crear_conductor_idempotente(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_conductor("C1", "Ana", "a@m.com", rating=4.5)
    # Crear de nuevo no debe duplicar (MERGE)
    grafo_repo.crear_conductor("C1", "Ana", "a@m.com", rating=4.5)
    with get_driver().session() as s:
        count = s.run("MATCH (c:Conductor {id:'C1'}) RETURN count(c) AS c").single()["c"]
        assert count == 1


def test_crear_vehiculo_con_relacion_maneja(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_conductor("C1", "Ana", "a@m.com")
    grafo_repo.crear_vehiculo("V1", "ABC123D", "Toyota", "Corolla", 2020)
    grafo_repo.crear_relacion_maneja("C1", "V1")
    with get_driver().session() as s:
        rel = s.run("MATCH (c:Conductor {id:'C1'})-[r:MANEJA]->(v:Vehiculo {id:'V1'}) RETURN r").single()
        assert rel is not None


def test_incrementar_viajo_con_primera_vez(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_usuario("U", "U", "u@m.com")
    grafo_repo.crear_conductor("C", "C", "c@m.com")
    grafo_repo.incrementar_viajo_con("U", "C")
    with get_driver().session() as s:
        rel = s.run("MATCH (:Usuario {id:'U'})-[r:VIAJO_CON]->(:Conductor {id:'C'}) RETURN r.cantidad_viajes AS n").single()
        assert rel["n"] == 1


def test_incrementar_viajo_con_repetido(neo4j_clean):
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver
    grafo_repo.crear_usuario("U", "U", "u@m.com")
    grafo_repo.crear_conductor("C", "C", "c@m.com")
    for _ in range(3):
        grafo_repo.incrementar_viajo_con("U", "C")
    with get_driver().session() as s:
        rel = s.run("MATCH (:Usuario {id:'U'})-[r:VIAJO_CON]->(:Conductor {id:'C'}) RETURN r.cantidad_viajes AS n").single()
        assert rel["n"] == 3


def test_coincidencias_devuelve_solo_min_viajes(neo4j_clean):
    from src.repositories import grafo_repo
    grafo_repo.crear_usuario("U1", "U1", "u1@m.com")
    grafo_repo.crear_usuario("U2", "U2", "u2@m.com")
    grafo_repo.crear_conductor("C1", "C1", "c1@m.com")
    grafo_repo.crear_conductor("C2", "C2", "c2@m.com")
    # U1-C1: 3 viajes
    for _ in range(3):
        grafo_repo.incrementar_viajo_con("U1", "C1")
    # U2-C2: 1 viaje (no debe aparecer)
    grafo_repo.incrementar_viajo_con("U2", "C2")
    # U1-C2: 2 viajes
    for _ in range(2):
        grafo_repo.incrementar_viajo_con("U1", "C2")
    coincidencias = grafo_repo.coincidencias(min_viajes=2)
    assert len(coincidencias) == 2
    # U1-C1 debe estar (3 viajes) y U1-C2 (2 viajes)
    pares = {(c["pasajero_id"], c["conductor_id"]) for c in coincidencias}
    assert ("U1", "C1") in pares
    assert ("U1", "C2") in pares
    assert ("U2", "C2") not in pares


def test_vehiculos_marca_y_patente_termina(neo4j_clean):
    from src.repositories import grafo_repo
    grafo_repo.crear_vehiculo("V1", "ABC123D", "Toyota", "Corolla")
    grafo_repo.crear_vehiculo("V2", "XYZ999D", "Toyota", "Hilux")
    grafo_repo.crear_vehiculo("V3", "AAA111A", "Toyota", "Etios")  # no termina en D
    grafo_repo.crear_vehiculo("V4", "BBB222D", "Honda", "Civic")   # no Toyota
    cantidad = grafo_repo.vehiculos_marca_y_patente_termina("Toyota", "D")
    assert cantidad == 2
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/repositories/test_grafo_repo.py -v
```
Expected: 7 FAIL.

- [ ] **Step 3: Implementar `src/repositories/grafo_repo.py`**

```python
"""Repository de grafo (Neo4j). Nodos y relaciones de Usuario/Conductor/Vehiculo."""
from src.db.neo4j_db import get_driver


def crear_usuario(id: str, nombre: str, email: str) -> None:
    cypher = """
        MERGE (u:Usuario {id: $id})
        SET u.nombre = $nombre, u.email = $email
    """
    with get_driver().session() as s:
        s.run(cypher, id=id, nombre=nombre, email=email)


def crear_conductor(id: str, nombre: str, email: str, rating: float = 0) -> None:
    cypher = """
        MERGE (c:Conductor {id: $id})
        SET c.nombre = $nombre, c.email = $email, c.rating = $rating
    """
    with get_driver().session() as s:
        s.run(cypher, id=id, nombre=nombre, email=email, rating=rating)


def crear_vehiculo(id: str, placa: str, marca: str, modelo: str,
                   anio: int | None = None) -> None:
    cypher = """
        MERGE (v:Vehiculo {id: $id})
        SET v.placa = $placa, v.marca = $marca, v.modelo = $modelo, v.anio = $anio
    """
    with get_driver().session() as s:
        s.run(cypher, id=id, placa=placa, marca=marca, modelo=modelo, anio=anio)


def crear_relacion_maneja(conductor_id: str, vehiculo_id: str) -> None:
    cypher = """
        MATCH (c:Conductor {id: $cid}), (v:Vehiculo {id: $vid})
        MERGE (c)-[:MANEJA]->(v)
    """
    with get_driver().session() as s:
        s.run(cypher, cid=conductor_id, vid=vehiculo_id)


def incrementar_viajo_con(usuario_id: str, conductor_id: str) -> None:
    """Crea o incrementa la relación VIAJO_CON entre usuario y conductor."""
    cypher = """
        MATCH (u:Usuario {id: $uid}), (c:Conductor {id: $cid})
        MERGE (u)-[r:VIAJO_CON]->(c)
        ON CREATE SET r.cantidad_viajes = 1
        ON MATCH  SET r.cantidad_viajes = r.cantidad_viajes + 1
        SET r.ultimo_viaje_ts = datetime()
    """
    with get_driver().session() as s:
        s.run(cypher, uid=usuario_id, cid=conductor_id)


def coincidencias(min_viajes: int = 2) -> list[dict]:
    """Caso de uso 5: parejas usuario-conductor con N o más viajes en común."""
    cypher = """
        MATCH (u:Usuario)-[r:VIAJO_CON]->(c:Conductor)
        WHERE r.cantidad_viajes >= $n
        RETURN u.id AS pasajero_id, u.nombre AS pasajero,
               c.id AS conductor_id, c.nombre AS conductor,
               r.cantidad_viajes AS viajes
        ORDER BY viajes DESC
    """
    with get_driver().session() as s:
        return [dict(r) for r in s.run(cypher, n=min_viajes)]


def vehiculos_marca_y_patente_termina(marca: str, sufijo: str) -> int:
    """Caso de uso 6: cuántos vehículos de marca X tienen patente terminada en Y."""
    cypher = """
        MATCH (v:Vehiculo)
        WHERE v.marca = $marca AND v.placa ENDS WITH $sufijo
        RETURN count(v) AS c
    """
    with get_driver().session() as s:
        return s.run(cypher, marca=marca, sufijo=sufijo).single()["c"]
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/repositories/test_grafo_repo.py -v
```
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/grafo_repo.py tests/repositories/test_grafo_repo.py
git commit -m "agregar grafo_repo con MERGE/MATCH para casos de uso 5 y 6 (7 tests)"
git push
```

---

## Sección 5 — Repository de Redis

### Task 5.1: `cache_repo` (Redis)

**Files:**
- Create: `src/repositories/cache_repo.py`
- Create: `tests/repositories/test_cache_repo.py`

**Funciones:**
- `set_session(token, data: dict, ttl_seconds=600) → None`
- `get_session(token) → dict | None`
- `delete_session(token) → None`
- `set_ultima_pos(vehiculo_id, lat, lon, ttl_seconds=30) → None`
- `get_ultima_pos(vehiculo_id) → tuple[float, float] | None`
- `set_cache(key, data, ttl_seconds=300) → None`
- `get_cache(key) → any | None`
- `invalidar(key) → None`

- [ ] **Step 1: Tests**

Crear `tests/repositories/test_cache_repo.py`:
```python
"""Tests del cache_repo (Redis)."""
import time


def test_set_y_get_session(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_session("token-abc", {"user_id": "U1", "tipo": "USUARIO"})
    data = cache_repo.get_session("token-abc")
    assert data == {"user_id": "U1", "tipo": "USUARIO"}


def test_get_session_no_existente(redis_clean):
    from src.repositories import cache_repo
    assert cache_repo.get_session("no-existe") is None


def test_session_expira_con_ttl(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_session("token", {"u": "x"}, ttl_seconds=1)
    assert cache_repo.get_session("token") is not None
    time.sleep(1.2)
    assert cache_repo.get_session("token") is None


def test_delete_session(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_session("t", {"u": "x"})
    cache_repo.delete_session("t")
    assert cache_repo.get_session("t") is None


def test_set_y_get_ultima_pos(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_ultima_pos("V1", -34.6, -58.4)
    pos = cache_repo.get_ultima_pos("V1")
    assert pos == (-34.6, -58.4)


def test_get_ultima_pos_no_existente(redis_clean):
    from src.repositories import cache_repo
    assert cache_repo.get_ultima_pos("V-no") is None


def test_set_y_get_cache(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_cache("top3", [{"autor": "A"}, {"autor": "B"}])
    assert cache_repo.get_cache("top3") == [{"autor": "A"}, {"autor": "B"}]


def test_invalidar_cache(redis_clean):
    from src.repositories import cache_repo
    cache_repo.set_cache("k", "v")
    cache_repo.invalidar("k")
    assert cache_repo.get_cache("k") is None
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/repositories/test_cache_repo.py -v
```
Expected: 8 FAIL.

- [ ] **Step 3: Implementar `src/repositories/cache_repo.py`**

```python
"""Repository de cache (Redis). Sesiones, ultima posicion y cache de queries."""
import json
from src.db.redis_db import get_client


def _k_session(token: str) -> str:
    return f"session:{token}"


def _k_pos(vehiculo_id: str) -> str:
    return f"vehiculo:{vehiculo_id}:pos"


def _k_cache(key: str) -> str:
    return f"cache:{key}"


# ---- Sesiones ----

def set_session(token: str, data: dict, ttl_seconds: int = 600) -> None:
    """Guarda una sesión con TTL."""
    get_client().setex(_k_session(token), ttl_seconds, json.dumps(data))


def get_session(token: str) -> dict | None:
    val = get_client().get(_k_session(token))
    return json.loads(val) if val else None


def delete_session(token: str) -> None:
    get_client().delete(_k_session(token))


# ---- Ultima posicion del vehiculo ----

def set_ultima_pos(vehiculo_id: str, lat: float, lon: float,
                   ttl_seconds: int = 30) -> None:
    get_client().setex(_k_pos(vehiculo_id), ttl_seconds, f"{lat},{lon}")


def get_ultima_pos(vehiculo_id: str) -> tuple[float, float] | None:
    val = get_client().get(_k_pos(vehiculo_id))
    if val is None:
        return None
    lat_s, lon_s = val.split(",")
    return (float(lat_s), float(lon_s))


# ---- Cache de queries pesadas ----

def set_cache(key: str, data, ttl_seconds: int = 300) -> None:
    """Cachea cualquier objeto serializable JSON."""
    get_client().setex(_k_cache(key), ttl_seconds, json.dumps(data))


def get_cache(key: str):
    val = get_client().get(_k_cache(key))
    return json.loads(val) if val else None


def invalidar(key: str) -> None:
    """Elimina una entrada del cache."""
    get_client().delete(_k_cache(key))
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/repositories/test_cache_repo.py -v
```
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add src/repositories/cache_repo.py tests/repositories/test_cache_repo.py
git commit -m "agregar cache_repo con sesiones TTL, ultima posicion y cache (8 tests)"
git push
```

---

## Sección 6 — Verificación final

### Task 6.1: Corrida completa del test suite

- [ ] **Step 1: Correr todos los tests de repositories**

```bash
pytest tests/repositories/ -v
```
Expected: **78 passed** (13 + 10 + 8 + 9 + 7 + 6 + 4 + 6 + 6 + 7 + 8 = 84 tests aprox), todos green. Si algún número es ligeramente distinto al esperado, no es problema mientras no haya FAILs.

- [ ] **Step 2: Tiempo total**

Anotar el tiempo total de ejecución. Debería ser < 90 segundos para los ~84 tests (cada uno limpia su base, lo que toma tiempo). Si tarda > 3 minutos, es esperable porque hablamos con 5 bases cloud y la latencia se acumula.

- [ ] **Step 3: Marcar tareas completadas en `docs/tareas.md`**

Marcar la **Fase 4** (sub-fases 4.1-4.7) como completas en `docs/tareas.md`.

- [ ] **Step 4: Actualizar nota de seguimiento**

Agregar al final de "Notas de seguimiento" en `tareas.md`:
```
- 2026-MM-DD: Plan 02 completo. Los 11 repositories están implementados con TDD. `pytest tests/repositories/` corre verde con ~84 tests. Listo para empezar Plan 03 (services).
```

- [ ] **Step 5: Commit final**

```bash
git add docs/tareas.md
git commit -m "marcar Fase 4 (repositories) como completada en docs/tareas.md"
git push
```

---

## Cierre del plan

Estado esperado al finalizar:

```
✅ pytest agregado a requirements.txt
✅ src/repositories/ con 11 modulos (uno por entidad/base)
✅ tests/repositories/ con 11 archivos de tests
✅ tests/conftest.py con 5 fixtures de limpieza
✅ ~84 tests de integracion verdes
✅ Todas las funciones requeridas por los casos de uso disponibles
✅ Todo versionado en GitHub
```

**Funciones críticas listas para los casos de uso del TP:**
- Caso 1 → `resena_repo.top_autores()`
- Caso 2 → `pago_repo.metodo_menos_usado()`
- Caso 3 → `actividad_repo.conductores_activos_desde()` (invertir → inactivos)
- Caso 4 → `actividad_repo.promedio_duracion()`
- Caso 5 → `grafo_repo.coincidencias()`
- Caso 6 → `grafo_repo.vehiculos_marca_y_patente_termina()`
- Caso 7 → `resena_repo.buscar_por_rating_extremo()`

**Siguiente paso:** escribir `docs/plan-03-services.md` para implementar la capa de services que orquesta los repositories.
