# Plan 03 — Services: orquestación multi-DB + autenticación

> **Para agentes:** REQUIRED SUB-SKILL: Usar `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans`. Los pasos usan checkboxes `- [ ]` para tracking.

**Goal:** Implementar la capa de services en `src/services/`. Es la capa que **orquesta múltiples repositories en una sola operación de negocio**, materializando el patrón `write-through best-effort + outbox` que el profesor identifica como motivo de aprobar/desaprobar el TP.

**Architecture:** Cada service implementa operaciones de negocio que cruzan 2-5 bases. La escritura al **source of truth** (SOT) es crítica y bloqueante. Las proyecciones a bases derivadas son **best-effort**: si fallan, se loguean al outbox y se reconcilian después, sin abortar la operación principal. Los tests son tests de integración que verifican el estado en todas las bases tocadas.

**Tech Stack:** Mismo que Plan 02 + `bcrypt` (hash de passwords), `secrets` (generación de tokens). Outbox en archivo plano (`outbox.log`).

---

## Pre-requisitos

**Plan 01 (Foundation) y Plan 02 (Repositories) completos.** Esto significa:

- ✅ 5 bases cloud conectadas y con esquemas.
- ✅ 11 repositories implementados con sus ~84 tests verdes.
- ✅ `pytest tests/repositories/` corre verde de punta a punta.
- ✅ Fixtures de limpieza disponibles en `tests/conftest.py`.

---

## Alcance de este plan

Cubre la **Fase 5** de `docs/tareas.md`: la capa de services.

**NO incluye:**
- Casos de uso ni menú (Plan 04).
- Seed de datos ni presentación (Plan 05).

**Entregables al finalizar:**

- ✅ 7 módulos en `src/services/`, uno por dominio operacional.
- ✅ 7 archivos de test en `tests/services/`, todos pasando.
- ✅ `src/utils/outbox.py` para registro de proyecciones fallidas.
- ✅ Cada operación de negocio escribe al SOT primero (bloqueante) y proyecta a bases derivadas con manejo de fallos.
- ✅ Cada service que toca múltiples bases tiene al menos un test que verifica el estado en cada una.

---

## File Structure

Archivos que se crean en este plan:

```
src/
├── services/
│   ├── __init__.py
│   ├── auth_service.py            ← Postgres + Mongo + Redis
│   ├── vehiculo_service.py        ← Postgres + Neo4j
│   ├── viaje_service.py           ← Mongo + Cassandra + Neo4j
│   ├── pago_service.py            ← Mongo
│   ├── resena_service.py          ← Mongo + Postgres + Neo4j + Redis
│   ├── ubicacion_service.py       ← Cassandra + Redis
│   └── reconciliacion_service.py  ← lee Mongo, escribe Neo4j/Cassandra
└── utils/
    └── outbox.py                  ← cola de proyecciones fallidas

tests/services/
├── __init__.py
├── test_auth_service.py
├── test_vehiculo_service.py
├── test_viaje_service.py
├── test_pago_service.py
├── test_resena_service.py
├── test_ubicacion_service.py
└── test_reconciliacion_service.py

.gitignore  → agregar outbox.log
```

---

## Diseño de los services

### Patrón write-through best-effort

Toda función que escribe en múltiples bases sigue este esqueleto:

```python
def operacion(args):
    # 1. SOT (Source of Truth) primero — bloqueante
    sot_id = sot_repo.escribir(...)
    if not sot_id:
        raise DominioError(...)

    # 2. Datos del SOT que necesitan las proyecciones
    sot_data = sot_repo.get_by_id(sot_id)

    # 3. Proyecciones best-effort (no abortan si fallan)
    _intentar("nombre_proyeccion_1",
              lambda: otro_repo.proyectar(sot_data))
    _intentar("nombre_proyeccion_2",
              lambda: tercer_repo.proyectar(sot_data))

    return sot_id


def _intentar(nombre: str, op):
    """Ejecuta op() y, si falla, loguea y mete en outbox."""
    try:
        op()
    except Exception as e:
        logger.error(f"Proyeccion {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})
```

### Convenciones de los services

1. **Validación primero:** verificar pre-condiciones antes de escribir (ej: el `usuario_id` debe existir).
2. **SOT bloqueante:** si falla, lanzar excepción del dominio.
3. **Proyecciones best-effort:** loguear y continuar.
4. **Sin lógica de presentación:** los services devuelven datos crudos (dicts, ids). El formato lo decide el menú/caso de uso.
5. **Errores del dominio** (definidos en `src/utils/errors.py`):
   - `UsuarioInexistente`, `ConductorInexistente`, `VehiculoInexistente`, `ViajeNoEncontrado`
   - `CredencialesInvalidas`, `SesionExpirada`, `EstadoInvalido`

### Convenciones de los tests de services

1. **Tests de integración multi-DB.** Tocan todas las bases involucradas.
2. **Usan múltiples fixtures:** ej. `test_register_usuario(postgres_clean, neo4j_clean, redis_clean)`.
3. **Verifican el estado en cada base tocada**, no solo el resultado del service.
4. **No mockean nada.** Si el código es difícil de testear, hay que refactorizarlo.

---

## Sección 0 — Outbox

### Task 0.1: `src/utils/outbox.py`

**Files:**
- Create: `src/utils/outbox.py`
- Create: `tests/test_outbox.py`
- Modify: `.gitignore` (agregar `outbox.log`)

- [ ] **Step 1: Agregar `outbox.log` al `.gitignore`**

Editar `.gitignore`, en la sección "Logs y archivos temporales", agregar:
```
outbox.log
```

- [ ] **Step 2: Escribir el test (TDD)**

Crear `tests/test_outbox.py`:
```python
"""Tests del outbox (cola simple en archivo para proyecciones fallidas)."""
import pytest
from pathlib import Path


@pytest.fixture
def outbox_clean(tmp_path, monkeypatch):
    """Redirige el outbox a un archivo temporal y lo vacía."""
    from src.utils import outbox
    temp_file = tmp_path / "outbox.log"
    monkeypatch.setattr(outbox, "_OUTBOX_FILE", temp_file)
    yield temp_file


def test_enqueue_y_pending(outbox_clean):
    from src.utils import outbox
    outbox.enqueue("test_op", {"viaje_id": "ABC"})
    pendings = outbox.pending()
    assert len(pendings) == 1
    assert pendings[0]["operation"] == "test_op"
    assert pendings[0]["payload"]["viaje_id"] == "ABC"


def test_pending_vacio(outbox_clean):
    from src.utils import outbox
    assert outbox.pending() == []


def test_enqueue_multiple(outbox_clean):
    from src.utils import outbox
    outbox.enqueue("op1")
    outbox.enqueue("op2", {"x": 1})
    outbox.enqueue("op3")
    pendings = outbox.pending()
    assert len(pendings) == 3
    assert [p["operation"] for p in pendings] == ["op1", "op2", "op3"]


def test_clear_vacia_el_outbox(outbox_clean):
    from src.utils import outbox
    outbox.enqueue("op")
    outbox.clear()
    assert outbox.pending() == []
```

- [ ] **Step 3: Correr el test — debe fallar**

```bash
pytest tests/test_outbox.py -v
```
Expected: 4 FAIL (no existe el módulo).

- [ ] **Step 4: Implementar `src/utils/outbox.py`**

```python
"""Cola simple en archivo para registrar proyecciones fallidas.

Las funciones de los services llaman a enqueue() cuando una proyección
a una base derivada falla. El job de reconciliación (Plan 03 §7) procesa
estas entradas periódicamente.
"""
import json
from pathlib import Path
from datetime import datetime, UTC

from src.utils.logger import logger

_OUTBOX_FILE = Path("outbox.log")


def enqueue(operation: str, payload: dict | None = None) -> None:
    """Registra una proyección fallida."""
    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "operation": operation,
        "payload": payload or {},
    }
    with _OUTBOX_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    logger.warning(f"Outbox enqueued: {operation}")


def pending() -> list[dict]:
    """Devuelve todas las entradas pendientes en el outbox."""
    if not _OUTBOX_FILE.exists():
        return []
    with _OUTBOX_FILE.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def clear() -> None:
    """Vacía el outbox. Llamar después de reconciliar exitosamente."""
    if _OUTBOX_FILE.exists():
        _OUTBOX_FILE.unlink()
```

- [ ] **Step 5: Correr el test — debe pasar**

```bash
pytest tests/test_outbox.py -v
```
Expected: 4 passed.

- [ ] **Step 6: Crear estructura de `src/services/` y `tests/services/`**

```bash
mkdir -p src/services tests/services
touch src/services/__init__.py tests/services/__init__.py
```

- [ ] **Step 7: Commit**

```bash
git add .gitignore src/utils/outbox.py tests/test_outbox.py src/services/ tests/services/
git commit -m "agregar outbox para proyecciones fallidas + esqueleto src/services/"
git push
```

---

## Sección 1 — `auth_service` (registro + login + sesiones)

### Task 1.1: `auth_service` completo

**Files:**
- Create: `src/services/auth_service.py`
- Create: `tests/services/test_auth_service.py`

**Funciones:**
- `register_usuario(email, password, nombre, telefono=None) → str (id)` — Postgres + Neo4j
- `register_conductor(email, password, nombre, nro_licencia, telefono=None) → str (id)` — Postgres + Neo4j
- `login(email, password, tipo_cuenta: 'USUARIO'|'CONDUCTOR') → str (token)` — Postgres + Redis + Mongo
- `logout(token) → None` — Redis + Mongo
- `validate_session(token) → dict | None` — Redis

**Bases tocadas:** Postgres (cuentas), Neo4j (nodos), Redis (sesiones), Mongo (login_history).

- [ ] **Step 1: Tests completos**

Crear `tests/services/test_auth_service.py`:
```python
"""Tests del auth_service (Postgres + Mongo + Redis + Neo4j)."""
import pytest


# ---- register_usuario ----

def test_register_usuario_persiste_en_postgres(postgres_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import usuario_repo

    uid = auth_service.register_usuario("juan@m.com", "pass1234", "Juan")
    user = usuario_repo.get_by_id(uid)
    assert user is not None
    assert user["email"] == "juan@m.com"
    assert user["nombre"] == "Juan"
    assert user["password_hash"] != "pass1234"  # debe estar hasheado


def test_register_usuario_crea_nodo_neo4j(postgres_clean, neo4j_clean):
    from src.services import auth_service
    from src.db.neo4j_db import get_driver

    uid = auth_service.register_usuario("ana@m.com", "p", "Ana")
    with get_driver().session() as s:
        n = s.run("MATCH (u:Usuario {id:$id}) RETURN u", id=uid).single()
        assert n is not None


def test_register_usuario_email_duplicado_lanza_error(postgres_clean, neo4j_clean):
    from src.services import auth_service
    import psycopg
    auth_service.register_usuario("dup@m.com", "p", "Juan")
    with pytest.raises(psycopg.errors.UniqueViolation):
        auth_service.register_usuario("dup@m.com", "p", "Otro Juan")


# ---- register_conductor ----

def test_register_conductor_persiste_en_postgres_y_neo4j(postgres_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import conductor_repo
    from src.db.neo4j_db import get_driver

    cid = auth_service.register_conductor("ana@m.com", "pass", "Ana", "LIC-001")
    assert conductor_repo.get_by_id(cid) is not None
    with get_driver().session() as s:
        n = s.run("MATCH (c:Conductor {id:$id}) RETURN c", id=cid).single()
        assert n is not None


# ---- login ----

def test_login_usuario_devuelve_token(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service

    auth_service.register_usuario("user@m.com", "secret123", "User")
    token = auth_service.login("user@m.com", "secret123", "USUARIO")
    assert token is not None and len(token) >= 16


def test_login_crea_sesion_en_redis(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import cache_repo

    auth_service.register_usuario("u@m.com", "p", "U")
    token = auth_service.login("u@m.com", "p", "USUARIO")
    sesion = cache_repo.get_session(token)
    assert sesion is not None
    assert sesion["tipo"] == "USUARIO"


def test_login_registra_evento_en_mongo(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import usuario_repo, login_history_repo

    auth_service.register_usuario("u@m.com", "p", "U")
    auth_service.login("u@m.com", "p", "USUARIO")
    uid = usuario_repo.get_by_email("u@m.com")["id"]
    eventos = login_history_repo.listar_por_usuario(uid)
    assert any(e["evento"] == "LOGIN_OK" for e in eventos)


def test_login_password_incorrecto_lanza_credenciales_invalidas(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.utils.errors import CredencialesInvalidas

    auth_service.register_usuario("u@m.com", "secret", "U")
    with pytest.raises(CredencialesInvalidas):
        auth_service.login("u@m.com", "incorrecto", "USUARIO")


def test_login_password_incorrecto_registra_evento_fail(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import usuario_repo, login_history_repo
    from src.utils.errors import CredencialesInvalidas

    auth_service.register_usuario("u@m.com", "secret", "U")
    with pytest.raises(CredencialesInvalidas):
        auth_service.login("u@m.com", "wrong", "USUARIO")
    uid = usuario_repo.get_by_email("u@m.com")["id"]
    eventos = login_history_repo.listar_por_usuario(uid)
    assert any(e["evento"] == "LOGIN_FAIL" for e in eventos)


def test_login_email_inexistente_lanza_error(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.utils.errors import CredencialesInvalidas

    with pytest.raises(CredencialesInvalidas):
        auth_service.login("no@m.com", "p", "USUARIO")


# ---- validate_session ----

def test_validate_session_existente(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service

    auth_service.register_usuario("u@m.com", "p", "U")
    token = auth_service.login("u@m.com", "p", "USUARIO")
    sesion = auth_service.validate_session(token)
    assert sesion is not None
    assert sesion["tipo"] == "USUARIO"


def test_validate_session_inexistente(redis_clean):
    from src.services import auth_service
    assert auth_service.validate_session("token-falso") is None


# ---- logout ----

def test_logout_borra_sesion_en_redis(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import cache_repo

    auth_service.register_usuario("u@m.com", "p", "U")
    token = auth_service.login("u@m.com", "p", "USUARIO")
    assert cache_repo.get_session(token) is not None
    auth_service.logout(token)
    assert cache_repo.get_session(token) is None


def test_logout_registra_evento_en_mongo(postgres_clean, mongo_clean, redis_clean, neo4j_clean):
    from src.services import auth_service
    from src.repositories import usuario_repo, login_history_repo

    auth_service.register_usuario("u@m.com", "p", "U")
    token = auth_service.login("u@m.com", "p", "USUARIO")
    auth_service.logout(token)
    uid = usuario_repo.get_by_email("u@m.com")["id"]
    eventos = login_history_repo.listar_por_usuario(uid)
    assert any(e["evento"] == "LOGOUT" for e in eventos)
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/services/test_auth_service.py -v
```
Expected: 13 FAIL (no existe `auth_service`).

- [ ] **Step 3: Implementar `src/services/auth_service.py`**

```python
"""Auth service: registro, login, logout, validación de sesión.

Toca:
- Postgres → cuentas (usuario, conductor) con password_hash bcrypt.
- Neo4j   → nodos (:Usuario), (:Conductor) (best-effort).
- Redis   → sesiones con TTL (10 min default).
- Mongo   → audit trail (login_history).
"""
import secrets
import bcrypt

from src.repositories import (
    usuario_repo, conductor_repo,
    grafo_repo, cache_repo, login_history_repo,
)
from src.utils import outbox
from src.utils.errors import CredencialesInvalidas
from src.utils.logger import logger


SESSION_TTL_SECONDS = 600  # 10 min


# ----------------- helpers -----------------

def _hash_password(password: str) -> str:
    """Hash bcrypt del password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def _intentar(nombre: str, op) -> None:
    """Ejecuta una proyección best-effort, loguea y encola si falla."""
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


# ----------------- registro -----------------

def register_usuario(email: str, password: str, nombre: str,
                     telefono: str | None = None) -> str:
    """Crea un usuario en Postgres y proyecta a Neo4j."""
    pw_hash = _hash_password(password)
    user_id = usuario_repo.crear(email, pw_hash, nombre, telefono)
    _intentar("neo4j_crear_usuario",
              lambda: grafo_repo.crear_usuario(user_id, nombre, email))
    return user_id


def register_conductor(email: str, password: str, nombre: str,
                       nro_licencia: str, telefono: str | None = None) -> str:
    """Crea un conductor en Postgres y proyecta a Neo4j."""
    pw_hash = _hash_password(password)
    cond_id = conductor_repo.crear(email, pw_hash, nombre, nro_licencia, telefono)
    _intentar("neo4j_crear_conductor",
              lambda: grafo_repo.crear_conductor(cond_id, nombre, email, rating=0))
    return cond_id


# ----------------- login / logout -----------------

def login(email: str, password: str, tipo_cuenta: str) -> str:
    """Valida credenciales, genera token, abre sesión en Redis y audita en Mongo.

    tipo_cuenta: 'USUARIO' o 'CONDUCTOR'.
    Lanza CredencialesInvalidas si email/password no coinciden.
    """
    repo = usuario_repo if tipo_cuenta == "USUARIO" else conductor_repo
    cuenta = repo.get_by_email(email)

    if cuenta is None or not _verify_password(password, cuenta["password_hash"]):
        # Audit del fail (best-effort)
        if cuenta is not None:
            _intentar("mongo_login_fail",
                      lambda: login_history_repo.crear(
                          cuenta["id"], tipo_cuenta, "LOGIN_FAIL"))
        raise CredencialesInvalidas("Email o password incorrectos")

    # Token y sesión
    token = secrets.token_urlsafe(24)
    cache_repo.set_session(
        token,
        {"user_id": cuenta["id"], "tipo": tipo_cuenta, "nombre": cuenta["nombre"]},
        ttl_seconds=SESSION_TTL_SECONDS,
    )
    # Audit OK (best-effort)
    _intentar("mongo_login_ok",
              lambda: login_history_repo.crear(cuenta["id"], tipo_cuenta, "LOGIN_OK"))
    return token


def logout(token: str) -> None:
    """Borra la sesión en Redis y audita en Mongo."""
    sesion = cache_repo.get_session(token)
    cache_repo.delete_session(token)
    if sesion is not None:
        _intentar("mongo_logout",
                  lambda: login_history_repo.crear(
                      sesion["user_id"], sesion["tipo"], "LOGOUT"))


# ----------------- sesión -----------------

def validate_session(token: str) -> dict | None:
    """Devuelve los datos de sesión o None si expiró/no existe."""
    return cache_repo.get_session(token)
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/services/test_auth_service.py -v
```
Expected: 13 passed.

- [ ] **Step 5: Commit**

```bash
git add src/services/auth_service.py tests/services/test_auth_service.py
git commit -m "agregar auth_service con bcrypt + sesion Redis + audit Mongo (13 tests)"
git push
```

---

## Sección 2 — `vehiculo_service`

### Task 2.1: `vehiculo_service`

**Files:**
- Create: `src/services/vehiculo_service.py`
- Create: `tests/services/test_vehiculo_service.py`

**Funciones:**
- `registrar(conductor_id, placa, marca, modelo, anio=None, color=None, tipo=None) → str (vehiculo_id)`
  - Verifica que el conductor existe (Postgres).
  - Inserta en Postgres (SOT).
  - Proyecta a Neo4j: crea nodo `(:Vehiculo)` + relación `(:Conductor)-[:MANEJA]->(:Vehiculo)` (best-effort).

**Bases tocadas:** Postgres + Neo4j.

- [ ] **Step 1: Tests**

Crear `tests/services/test_vehiculo_service.py`:
```python
"""Tests del vehiculo_service (Postgres + Neo4j)."""
import pytest


def _crear_conductor(postgres_clean, neo4j_clean):
    from src.services import auth_service
    return auth_service.register_conductor("c@m.com", "p", "Conductor", "LIC-T")


def test_registrar_persiste_en_postgres(postgres_clean, neo4j_clean):
    from src.services import vehiculo_service
    from src.repositories import vehiculo_repo

    cid = _crear_conductor(postgres_clean, neo4j_clean)
    vid = vehiculo_service.registrar(cid, "ABC123D", "Toyota", "Corolla", 2020)
    v = vehiculo_repo.get_by_id(vid)
    assert v is not None
    assert v["placa"] == "ABC123D"


def test_registrar_crea_nodo_y_relacion_en_neo4j(postgres_clean, neo4j_clean):
    from src.services import vehiculo_service
    from src.db.neo4j_db import get_driver

    cid = _crear_conductor(postgres_clean, neo4j_clean)
    vid = vehiculo_service.registrar(cid, "XYZ999D", "Toyota", "Hilux", 2021)
    with get_driver().session() as s:
        rel = s.run(
            """MATCH (c:Conductor {id:$cid})-[r:MANEJA]->(v:Vehiculo {id:$vid})
               RETURN v.placa AS placa, v.marca AS marca""",
            cid=cid, vid=vid,
        ).single()
        assert rel is not None
        assert rel["placa"] == "XYZ999D"
        assert rel["marca"] == "Toyota"


def test_registrar_con_conductor_inexistente_lanza_error(postgres_clean, neo4j_clean):
    from src.services import vehiculo_service
    from src.utils.errors import ConductorInexistente

    with pytest.raises(ConductorInexistente):
        vehiculo_service.registrar(
            "00000000-0000-0000-0000-000000000000",
            "ABC", "M", "M"
        )
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/services/test_vehiculo_service.py -v
```
Expected: 3 FAIL.

- [ ] **Step 3: Implementar `src/services/vehiculo_service.py`**

```python
"""Vehiculo service: registro con proyección al grafo.

Toca:
- Postgres → vehiculo (SOT).
- Neo4j   → nodo (:Vehiculo) + relación [:MANEJA] desde el Conductor (best-effort).
"""
from src.repositories import conductor_repo, vehiculo_repo, grafo_repo
from src.utils import outbox
from src.utils.errors import ConductorInexistente
from src.utils.logger import logger


def _intentar(nombre: str, op) -> None:
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


def registrar(conductor_id: str, placa: str, marca: str, modelo: str,
              anio: int | None = None, color: str | None = None,
              tipo: str | None = None) -> str:
    """Registra un vehiculo en Postgres y proyecta al grafo."""
    if not conductor_repo.existe(conductor_id):
        raise ConductorInexistente(conductor_id)

    vehiculo_id = vehiculo_repo.crear(conductor_id, placa, marca, modelo, anio, color, tipo)

    _intentar("neo4j_crear_vehiculo",
              lambda: grafo_repo.crear_vehiculo(vehiculo_id, placa, marca, modelo, anio))
    _intentar("neo4j_relacion_maneja",
              lambda: grafo_repo.crear_relacion_maneja(conductor_id, vehiculo_id))

    return vehiculo_id
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/services/test_vehiculo_service.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/services/vehiculo_service.py tests/services/test_vehiculo_service.py
git commit -m "agregar vehiculo_service con proyeccion a Neo4j (3 tests)"
git push
```

---

## Sección 3 — `viaje_service`

### Task 3.1: `viaje_service` (solicitar + iniciar + finalizar)

**Files:**
- Create: `src/services/viaje_service.py`
- Create: `tests/services/test_viaje_service.py`

**Funciones:**
- `solicitar(usuario_id, conductor_id, vehiculo_id, origen, destino) → str (viaje_id)`
  - Verifica usuario, conductor y vehiculo en Postgres.
  - Crea documento en Mongo con snapshots tomados de Postgres.
- `iniciar(viaje_id) → bool`
  - Update en Mongo (PENDIENTE → EN_CURSO).
- `finalizar(viaje_id, distancia_km, duracion_min) → None`
  - Update en Mongo (EN_CURSO → FINALIZADO).
  - Proyectar a Cassandra (`ultima_actividad_conductor` + `viajes_finalizados_por_dia`).
  - Proyectar a Neo4j (incrementar arista `VIAJO_CON`).
  - Invalidar cache de Redis (`cache:viajes_promedio`).

**Bases tocadas:** Postgres (lectura), Mongo (SOT), Cassandra (proyección), Neo4j (proyección), Redis (invalidación).

- [ ] **Step 1: Tests**

Crear `tests/services/test_viaje_service.py`:
```python
"""Tests del viaje_service (Mongo + Cassandra + Neo4j + Redis)."""
import pytest
import uuid
from datetime import datetime, UTC


def _setup_entidades(postgres_clean, neo4j_clean):
    """Crea un usuario, conductor y vehiculo de prueba. Devuelve sus ids."""
    from src.services import auth_service, vehiculo_service
    uid = auth_service.register_usuario("user@m.com", "p", "User")
    cid = auth_service.register_conductor("driver@m.com", "p", "Driver", "LIC-V")
    vid = vehiculo_service.registrar(cid, "ABC123D", "Toyota", "Corolla")
    return uid, cid, vid


# ---- solicitar ----

def test_solicitar_crea_documento_en_mongo(postgres_clean, mongo_clean, neo4j_clean):
    from src.services import viaje_service
    from src.repositories import viaje_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(
        uid, cid, vid,
        origen={"lat": -34.6, "lon": -58.4, "direccion": "Palermo"},
        destino={"lat": -34.55, "lon": -58.45, "direccion": "Belgrano"},
    )
    v = viaje_repo.get_by_id(viaje_id)
    assert v is not None
    assert v["estado"] == "PENDIENTE"
    assert v["usuario_id"] == uid
    assert v["conductor_id"] == cid


def test_solicitar_incluye_snapshots(postgres_clean, mongo_clean, neo4j_clean):
    from src.services import viaje_service
    from src.repositories import viaje_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(
        uid, cid, vid,
        {"lat": -34.6, "lon": -58.4}, {"lat": -34.5, "lon": -58.5},
    )
    v = viaje_repo.get_by_id(viaje_id)
    assert v["usuario_snapshot"]["nombre"] == "User"
    assert v["conductor_snapshot"]["nombre"] == "Driver"


def test_solicitar_con_usuario_inexistente_lanza_error(postgres_clean, mongo_clean, neo4j_clean):
    from src.services import viaje_service
    from src.utils.errors import UsuarioInexistente

    _, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    with pytest.raises(UsuarioInexistente):
        viaje_service.solicitar(
            "00000000-0000-0000-0000-000000000000", cid, vid,
            {"lat": 0, "lon": 0}, {"lat": 0, "lon": 0},
        )


# ---- iniciar ----

def test_iniciar_cambia_estado(postgres_clean, mongo_clean, neo4j_clean):
    from src.services import viaje_service
    from src.repositories import viaje_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    ok = viaje_service.iniciar(viaje_id)
    assert ok is True
    assert viaje_repo.get_by_id(viaje_id)["estado"] == "EN_CURSO"


# ---- finalizar ----

def test_finalizar_actualiza_mongo(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import viaje_service
    from src.repositories import viaje_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, distancia_km=8.5, duracion_min=22)

    v = viaje_repo.get_by_id(viaje_id)
    assert v["estado"] == "FINALIZADO"
    assert v["distancia_km"] == 8.5
    assert v["duracion_min"] == 22


def test_finalizar_proyecta_a_cassandra(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import viaje_service
    from src.repositories import actividad_repo
    from src.repositories import conductor_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, 5, 15)

    ultima = actividad_repo.get_ultima(uuid.UUID(cid))
    assert ultima is not None
    assert ultima["ultimo_viaje_id"] == uuid.UUID(viaje_id)


def test_finalizar_incrementa_arista_neo4j(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import viaje_service
    from src.repositories import grafo_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, 5, 15)

    coincidencias = grafo_repo.coincidencias(min_viajes=1)
    assert len(coincidencias) == 1
    assert coincidencias[0]["pasajero_id"] == uid
    assert coincidencias[0]["conductor_id"] == cid
    assert coincidencias[0]["viajes"] == 1


def test_finalizar_dos_viajes_misma_pareja_incrementa_arista(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import viaje_service
    from src.repositories import grafo_repo

    uid, cid, vid = _setup_entidades(postgres_clean, neo4j_clean)
    for _ in range(3):
        viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
        viaje_service.iniciar(viaje_id)
        viaje_service.finalizar(viaje_id, 5, 15)
    coincidencias = grafo_repo.coincidencias(min_viajes=2)
    assert coincidencias[0]["viajes"] == 3
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/services/test_viaje_service.py -v
```
Expected: 8 FAIL.

- [ ] **Step 3: Implementar `src/services/viaje_service.py`**

```python
"""Viaje service: solicitar, iniciar, finalizar.

Toca:
- Postgres → lectura de usuario/conductor para snapshots.
- Mongo    → viajes (SOT).
- Cassandra → ultima_actividad_conductor + viajes_finalizados_por_dia (proyección).
- Neo4j    → incremento de arista VIAJO_CON (proyección).
- Redis    → invalidación de cache de queries pesadas (proyección).
"""
import uuid
from datetime import datetime, UTC, date

from src.repositories import (
    usuario_repo, conductor_repo, vehiculo_repo,
    viaje_repo, actividad_repo, grafo_repo, cache_repo,
)
from src.utils import outbox
from src.utils.errors import (
    UsuarioInexistente, ConductorInexistente,
    VehiculoInexistente, ViajeNoEncontrado, EstadoInvalido,
)
from src.utils.logger import logger


def _intentar(nombre: str, op) -> None:
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


# ----------------- solicitar -----------------

def solicitar(usuario_id: str, conductor_id: str, vehiculo_id: str,
              origen: dict, destino: dict) -> str:
    """Crea un viaje en estado PENDIENTE en Mongo con snapshots de Postgres."""
    usuario = usuario_repo.get_by_id(usuario_id)
    if usuario is None:
        raise UsuarioInexistente(usuario_id)
    conductor = conductor_repo.get_by_id(conductor_id)
    if conductor is None:
        raise ConductorInexistente(conductor_id)
    if not vehiculo_repo.existe(vehiculo_id):
        raise VehiculoInexistente(vehiculo_id)

    doc = {
        "usuario_id":   usuario_id,
        "conductor_id": conductor_id,
        "vehiculo_id":  vehiculo_id,
        "origen":  origen,
        "destino": destino,
        "estado":  "PENDIENTE",
        "ts_solicitud": datetime.now(UTC),
        "usuario_snapshot": {
            "nombre": usuario["nombre"],
            "rating": usuario["rating_promedio"],
        },
        "conductor_snapshot": {
            "nombre": conductor["nombre"],
            "rating": conductor["rating_promedio"],
        },
    }
    return viaje_repo.crear(doc)


# ----------------- iniciar -----------------

def iniciar(viaje_id: str) -> bool:
    """Transición PENDIENTE → EN_CURSO."""
    return viaje_repo.iniciar(viaje_id)


# ----------------- finalizar -----------------

def finalizar(viaje_id: str, distancia_km: float, duracion_min: int) -> None:
    """Transición EN_CURSO → FINALIZADO + proyecciones a Cassandra/Neo4j/Redis."""
    ok = viaje_repo.finalizar(viaje_id, distancia_km, duracion_min)
    if not ok:
        # O no existe o no estaba EN_CURSO
        viaje = viaje_repo.get_by_id(viaje_id)
        if viaje is None:
            raise ViajeNoEncontrado(viaje_id)
        raise EstadoInvalido(f"Viaje {viaje_id} no está EN_CURSO")

    viaje = viaje_repo.get_by_id(viaje_id)
    cid_uuid = uuid.UUID(viaje["conductor_id"])
    uid_uuid = uuid.UUID(viaje["usuario_id"])
    vid_uuid = uuid.UUID(viaje_id)
    ts_fin = viaje["ts_fin"]
    if ts_fin.tzinfo is None:
        ts_fin = ts_fin.replace(tzinfo=UTC)

    # Proyección 1: última actividad del conductor (Cassandra)
    _intentar(
        "cassandra_ultima_actividad",
        lambda: actividad_repo.upsert_ultima(cid_uuid, ts_fin, vid_uuid),
    )

    # Proyección 2: viajes finalizados por día (Cassandra)
    _intentar(
        "cassandra_viajes_finalizados",
        lambda: actividad_repo.insertar_viaje_finalizado(
            ts_fin.date(), vid_uuid, cid_uuid, uid_uuid, duracion_min, distancia_km
        ),
    )

    # Proyección 3: arista VIAJO_CON en Neo4j
    _intentar(
        "neo4j_arista_viajo_con",
        lambda: grafo_repo.incrementar_viajo_con(viaje["usuario_id"], viaje["conductor_id"]),
    )

    # Proyección 4: invalidación de caches relacionados
    _intentar("redis_invalidar_viajes_promedio",
              lambda: cache_repo.invalidar("viajes_promedio"))
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/services/test_viaje_service.py -v
```
Expected: 8 passed.

> Si algún test de Cassandra falla con `KeyError: 'ultimo_viaje_id'`, revisar que `actividad_repo.get_ultima` devuelva todas las columnas correctamente.

- [ ] **Step 5: Commit**

```bash
git add src/services/viaje_service.py tests/services/test_viaje_service.py
git commit -m "agregar viaje_service con proyeccion multi-DB al finalizar (8 tests)"
git push
```

---

## Sección 4 — `pago_service`

### Task 4.1: `pago_service`

**Files:**
- Create: `src/services/pago_service.py`
- Create: `tests/services/test_pago_service.py`

**Funciones:**
- `procesar(viaje_id, monto_total, tarifa_base, tarifa_distancia, tarifa_tiempo, cargos_extra, metodo_pago) → str (pago_id)`
  - Verifica que el viaje existe en Mongo.
  - Inserta el pago en Mongo.

**Bases tocadas:** Mongo (lectura + escritura).

- [ ] **Step 1: Tests**

Crear `tests/services/test_pago_service.py`:
```python
"""Tests del pago_service (Mongo)."""
import pytest


def _setup_viaje_finalizado(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import auth_service, vehiculo_service, viaje_service
    uid = auth_service.register_usuario("u@m.com", "p", "U")
    cid = auth_service.register_conductor("c@m.com", "p", "C", "L1")
    vid = vehiculo_service.registrar(cid, "P1", "M", "M")
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, 5, 15)
    return viaje_id


def test_procesar_inserta_pago_en_mongo(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import pago_service
    from src.repositories import pago_repo

    viaje_id = _setup_viaje_finalizado(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    pago_id = pago_service.procesar(
        viaje_id, monto_total=2500, tarifa_base=500,
        tarifa_distancia=1200, tarifa_tiempo=600,
        cargos_extra=200, metodo_pago="TARJETA",
    )
    p = pago_repo.get_by_id(pago_id)
    assert p["monto_total"] == 2500
    assert p["metodo_pago"] == "TARJETA"
    assert p["viaje_id"] == viaje_id


def test_procesar_estado_aprobado(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import pago_service
    from src.repositories import pago_repo

    viaje_id = _setup_viaje_finalizado(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    pago_id = pago_service.procesar(viaje_id, 1000, 500, 300, 200, 0, "EFECTIVO")
    p = pago_repo.get_by_id(pago_id)
    assert p["estado"] == "APROBADO"


def test_procesar_viaje_inexistente_lanza_error(mongo_clean):
    from src.services import pago_service
    from src.utils.errors import ViajeNoEncontrado

    with pytest.raises(ViajeNoEncontrado):
        pago_service.procesar(
            "507f1f77bcf86cd799439011",
            1000, 500, 300, 200, 0, "TARJETA",
        )
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/services/test_pago_service.py -v
```
Expected: 3 FAIL.

- [ ] **Step 3: Implementar `src/services/pago_service.py`**

```python
"""Pago service: procesar pagos asociados a viajes finalizados.

Toca:
- Mongo → viajes (lectura para validar) + pagos (escritura).
"""
from datetime import datetime, UTC

from src.repositories import viaje_repo, pago_repo
from src.utils.errors import ViajeNoEncontrado


def procesar(viaje_id: str,
             monto_total: float,
             tarifa_base: float,
             tarifa_distancia: float,
             tarifa_tiempo: float,
             cargos_extra: float,
             metodo_pago: str) -> str:
    """Procesa un pago para un viaje. Estado siempre APROBADO en el TP."""
    if viaje_repo.get_by_id(viaje_id) is None:
        raise ViajeNoEncontrado(viaje_id)

    pago_doc = {
        "viaje_id":         viaje_id,
        "monto_total":      monto_total,
        "tarifa_base":      tarifa_base,
        "tarifa_distancia": tarifa_distancia,
        "tarifa_tiempo":    tarifa_tiempo,
        "cargos_extra":     cargos_extra,
        "metodo_pago":      metodo_pago,
        "estado":           "APROBADO",
        "timestamp":        datetime.now(UTC),
    }
    return pago_repo.crear(pago_doc)
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/services/test_pago_service.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/services/pago_service.py tests/services/test_pago_service.py
git commit -m "agregar pago_service con validacion de viaje + insert en Mongo (3 tests)"
git push
```

---

## Sección 5 — `resena_service`

### Task 5.1: `resena_service`

**Files:**
- Create: `src/services/resena_service.py`
- Create: `tests/services/test_resena_service.py`

**Funciones:**
- `crear(viaje_id, tipo, autor_id, autor_nombre, destinatario_id, destinatario_nombre, rating, comentario) → str`
  - Verifica que el viaje existe y está FINALIZADO (Mongo).
  - Inserta la reseña en Mongo (SOT).
  - Recalcula `rating_promedio` del destinatario y lo actualiza en Postgres.
  - Si el destinatario es conductor, actualiza también el nodo en Neo4j.
  - Invalida `cache:top3_resenadores` en Redis.

**Bases tocadas:** Mongo (lectura + SOT), Postgres (update), Neo4j (update), Redis (invalidación).

- [ ] **Step 1: Tests**

Crear `tests/services/test_resena_service.py`:
```python
"""Tests del resena_service (Mongo + Postgres + Neo4j + Redis)."""
import pytest


def _setup_viaje_finalizado_y_personas(postgres_clean, mongo_clean, cassandra_clean,
                                        neo4j_clean, redis_clean):
    """Setup completo: usuario, conductor, vehiculo, viaje finalizado."""
    from src.services import auth_service, vehiculo_service, viaje_service
    uid = auth_service.register_usuario("u@m.com", "p", "Juan Pérez")
    cid = auth_service.register_conductor("c@m.com", "p", "Ana Gómez", "LIC-R")
    vid = vehiculo_service.registrar(cid, "R1", "Toyota", "Corolla")
    viaje_id = viaje_service.solicitar(uid, cid, vid,
                                        {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    viaje_service.iniciar(viaje_id)
    viaje_service.finalizar(viaje_id, 5, 20)
    return uid, cid, viaje_id


def test_crear_inserta_resena_en_mongo(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import resena_service
    from src.repositories import resena_repo

    uid, cid, viaje_id = _setup_viaje_finalizado_y_personas(
        postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    rid = resena_service.crear(
        viaje_id=viaje_id, tipo="U_A_C",
        autor_id=uid, autor_nombre="Juan Pérez",
        destinatario_id=cid, destinatario_nombre="Ana Gómez",
        rating=5, comentario="Excelente",
    )
    r = resena_repo.get_by_id(rid)
    assert r["rating"] == 5
    assert r["tipo"] == "U_A_C"
    assert r["autor"]["id"] == uid


def test_crear_actualiza_rating_promedio_postgres(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import resena_service
    from src.repositories import conductor_repo

    uid, cid, viaje_id = _setup_viaje_finalizado_y_personas(
        postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    resena_service.crear(
        viaje_id, "U_A_C", uid, "Juan", cid, "Ana", 5, "ok",
    )
    cond = conductor_repo.get_by_id(cid)
    assert cond["rating_promedio"] == pytest.approx(5.0)


def test_crear_promedia_varias_resenas(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    """Si vienen 2 reseñas con ratings 4 y 5, el promedio del destinatario debe ser 4.5."""
    from src.services import resena_service, auth_service, vehiculo_service, viaje_service
    from src.repositories import conductor_repo

    cid = auth_service.register_conductor("c@m.com", "p", "Ana", "LIC-R")
    vid = vehiculo_service.registrar(cid, "R1", "M", "M")

    for i, rating in enumerate([4, 5]):
        uid = auth_service.register_usuario(f"u{i}@m.com", "p", f"U{i}")
        viaje_id = viaje_service.solicitar(uid, cid, vid,
                                            {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
        viaje_service.iniciar(viaje_id)
        viaje_service.finalizar(viaje_id, 5, 20)
        resena_service.crear(viaje_id, "U_A_C", uid, f"U{i}", cid, "Ana", rating, "ok")

    assert conductor_repo.get_by_id(cid)["rating_promedio"] == pytest.approx(4.5)


def test_crear_invalida_cache_top3(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import resena_service
    from src.repositories import cache_repo

    cache_repo.set_cache("top3_resenadores", [{"x": 1}])
    assert cache_repo.get_cache("top3_resenadores") is not None

    uid, cid, viaje_id = _setup_viaje_finalizado_y_personas(
        postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean)
    resena_service.crear(viaje_id, "U_A_C", uid, "U", cid, "C", 5, "ok")

    assert cache_repo.get_cache("top3_resenadores") is None


def test_crear_sobre_viaje_no_finalizado_lanza_error(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    from src.services import resena_service, auth_service, vehiculo_service, viaje_service
    from src.utils.errors import EstadoInvalido

    uid = auth_service.register_usuario("u@m.com", "p", "U")
    cid = auth_service.register_conductor("c@m.com", "p", "C", "LIC")
    vid = vehiculo_service.registrar(cid, "P", "M", "M")
    # No finalizamos el viaje: queda en PENDIENTE
    viaje_id = viaje_service.solicitar(uid, cid, vid, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
    with pytest.raises(EstadoInvalido):
        resena_service.crear(viaje_id, "U_A_C", uid, "U", cid, "C", 5, "ok")
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/services/test_resena_service.py -v
```
Expected: 5 FAIL.

- [ ] **Step 3: Implementar `src/services/resena_service.py`**

```python
"""Resena service: crear reseñas con propagación a Postgres/Neo4j/Redis.

Toca:
- Mongo    → viajes (lectura), resenas (SOT).
- Postgres → update rating_promedio del destinatario.
- Neo4j    → update rating en nodo Conductor (si aplica).
- Redis    → invalida cache:top3_resenadores.
"""
from datetime import datetime, UTC

from src.repositories import (
    viaje_repo, resena_repo,
    usuario_repo, conductor_repo, grafo_repo, cache_repo,
)
from src.utils import outbox
from src.utils.errors import ViajeNoEncontrado, EstadoInvalido
from src.utils.logger import logger
from src.db.neo4j_db import get_driver


def _intentar(nombre: str, op) -> None:
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


def crear(viaje_id: str, tipo: str,
          autor_id: str, autor_nombre: str,
          destinatario_id: str, destinatario_nombre: str,
          rating: int, comentario: str) -> str:
    """Crea una reseña y propaga el nuevo rating al destinatario.

    tipo: 'U_A_C' (Usuario a Conductor) o 'C_A_U' (Conductor a Usuario).
    rating: 1 a 5.
    """
    viaje = viaje_repo.get_by_id(viaje_id)
    if viaje is None:
        raise ViajeNoEncontrado(viaje_id)
    if viaje["estado"] != "FINALIZADO":
        raise EstadoInvalido(f"Solo se puede reseñar viajes FINALIZADOS (actual: {viaje['estado']})")

    # 1. SOT: insertar reseña en Mongo
    doc = {
        "viaje_id": viaje_id,
        "tipo": tipo,
        "autor":        {"id": autor_id,        "nombre": autor_nombre},
        "destinatario": {"id": destinatario_id, "nombre": destinatario_nombre},
        "rating": rating,
        "comentario": comentario,
        "timestamp": datetime.now(UTC),
        "contexto_viaje": {
            "origen": viaje["origen"].get("direccion", ""),
            "destino": viaje["destino"].get("direccion", ""),
            "duracion_min": viaje.get("duracion_min"),
        },
    }
    rid = resena_repo.crear(doc)

    # 2. Recalcular promedio del destinatario
    ratings = resena_repo.ratings_de_destinatario(destinatario_id)
    nuevo_promedio = sum(ratings) / len(ratings) if ratings else 0

    # 3. Actualizar Postgres (rating_promedio)
    if tipo == "U_A_C":
        # destinatario es conductor
        _intentar("postgres_update_rating_conductor",
                  lambda: conductor_repo.actualizar_rating(destinatario_id, nuevo_promedio))
        # 4. Actualizar Neo4j (rating en nodo Conductor)
        _intentar("neo4j_update_rating_conductor",
                  lambda: _actualizar_rating_neo4j_conductor(destinatario_id, nuevo_promedio))
    else:
        # destinatario es usuario
        _intentar("postgres_update_rating_usuario",
                  lambda: usuario_repo.actualizar_rating(destinatario_id, nuevo_promedio))

    # 5. Invalidar cache top3
    _intentar("redis_invalidar_top3_resenadores",
              lambda: cache_repo.invalidar("top3_resenadores"))

    return rid


def _actualizar_rating_neo4j_conductor(conductor_id: str, rating: float) -> None:
    """Helper interno: SET rating en el nodo (:Conductor) de Neo4j."""
    cypher = "MATCH (c:Conductor {id: $id}) SET c.rating = $rating"
    with get_driver().session() as s:
        s.run(cypher, id=conductor_id, rating=rating)
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/services/test_resena_service.py -v
```
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/services/resena_service.py tests/services/test_resena_service.py
git commit -m "agregar resena_service con propagacion de rating a Postgres y Neo4j (5 tests)"
git push
```

---

## Sección 6 — `ubicacion_service`

### Task 6.1: `ubicacion_service`

**Files:**
- Create: `src/services/ubicacion_service.py`
- Create: `tests/services/test_ubicacion_service.py`

**Funciones:**
- `reportar(vehiculo_id, lat, lon, viaje_id=None) → None`
  - Inserta en Cassandra (histórico).
  - Setea última posición en Redis (TTL 30s).

**Bases tocadas:** Cassandra + Redis.

- [ ] **Step 1: Tests**

Crear `tests/services/test_ubicacion_service.py`:
```python
"""Tests del ubicacion_service (Cassandra + Redis)."""
import uuid
import time


def test_reportar_inserta_en_cassandra(cassandra_clean, redis_clean):
    from src.services import ubicacion_service
    from src.repositories import ubicacion_repo

    vid = uuid.uuid4()
    ubicacion_service.reportar(str(vid), -34.6, -58.4)
    historial = ubicacion_repo.historial(vid)
    assert len(historial) == 1


def test_reportar_setea_redis_con_ttl(cassandra_clean, redis_clean):
    from src.services import ubicacion_service
    from src.repositories import cache_repo

    vid = str(uuid.uuid4())
    ubicacion_service.reportar(vid, -34.6, -58.4)
    pos = cache_repo.get_ultima_pos(vid)
    assert pos == (-34.6, -58.4)


def test_reportar_varios_acumula_historial(cassandra_clean, redis_clean):
    from src.services import ubicacion_service
    from src.repositories import ubicacion_repo

    vid = uuid.uuid4()
    for i in range(5):
        ubicacion_service.reportar(str(vid), -34.6 + i * 0.01, -58.4)
        time.sleep(0.01)  # asegurar timestamps distintos
    historial = ubicacion_repo.historial(vid)
    assert len(historial) == 5
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/services/test_ubicacion_service.py -v
```
Expected: 3 FAIL.

- [ ] **Step 3: Implementar `src/services/ubicacion_service.py`**

```python
"""Ubicacion service: streaming GPS de vehiculos.

Toca:
- Cassandra → ubicaciones_por_vehiculo (histórico completo).
- Redis    → última posición con TTL corto (matching de viajes).
"""
import uuid
from datetime import datetime, UTC

from src.repositories import ubicacion_repo, cache_repo
from src.utils import outbox
from src.utils.logger import logger


def _intentar(nombre: str, op) -> None:
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} fallo: {e}")
        outbox.enqueue(nombre, {"error": str(e)})


def reportar(vehiculo_id: str, lat: float, lon: float,
             viaje_id: str | None = None) -> None:
    """Registra una posición GPS del vehículo en histórico y última posición."""
    vid_uuid = uuid.UUID(vehiculo_id)
    vj_uuid = uuid.UUID(viaje_id) if viaje_id else None
    ts = datetime.now(UTC)

    # 1. SOT: histórico en Cassandra
    ubicacion_repo.insertar(vid_uuid, ts, lat, lon, viaje_id=vj_uuid)

    # 2. Proyección: última posición en Redis (best-effort)
    _intentar("redis_ultima_pos",
              lambda: cache_repo.set_ultima_pos(vehiculo_id, lat, lon))
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/services/test_ubicacion_service.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/services/ubicacion_service.py tests/services/test_ubicacion_service.py
git commit -m "agregar ubicacion_service para streaming GPS (3 tests)"
git push
```

---

## Sección 7 — `reconciliacion_service`

### Task 7.1: `reconciliacion_service`

**Files:**
- Create: `src/services/reconciliacion_service.py`
- Create: `tests/services/test_reconciliacion_service.py`

**Funciones:**
- `sync_neo4j_desde_mongo() → dict (stats)`
  - Lee todos los viajes FINALIZADOS de Mongo.
  - Reconstruye las aristas `VIAJO_CON` en Neo4j desde cero (`MATCH... DELETE` + `MERGE`).
  - Devuelve estadísticas de la sincronización.

- `procesar_outbox() → dict (stats)`
  - Lee `outbox.log` y reporta cuántas entradas hay pendientes.
  - Para el TP no implementamos retries automáticos (el reset_all_dbs.py + reconcile es suficiente).

**Bases tocadas:** Mongo (lectura), Neo4j (escritura).

- [ ] **Step 1: Tests**

Crear `tests/services/test_reconciliacion_service.py`:
```python
"""Tests del reconciliacion_service."""
import pytest


def test_sync_neo4j_desde_mongo_reconstruye_aristas(postgres_clean, mongo_clean, cassandra_clean, neo4j_clean, redis_clean):
    """Después de borrar las aristas en Neo4j, sync_neo4j_desde_mongo las recrea."""
    from src.services import auth_service, vehiculo_service, viaje_service
    from src.services import reconciliacion_service
    from src.repositories import grafo_repo
    from src.db.neo4j_db import get_driver

    # Crear 3 viajes finalizados de una pareja (U1-C1) y 1 de otra (U2-C1)
    u1 = auth_service.register_usuario("u1@m.com", "p", "U1")
    u2 = auth_service.register_usuario("u2@m.com", "p", "U2")
    c1 = auth_service.register_conductor("c1@m.com", "p", "C1", "LIC")
    v1 = vehiculo_service.registrar(c1, "P1", "M", "M")
    for u in [u1, u1, u1, u2]:
        vid = viaje_service.solicitar(u, c1, v1, {"lat": 0, "lon": 0}, {"lat": 1, "lon": 1})
        viaje_service.iniciar(vid)
        viaje_service.finalizar(vid, 5, 15)

    # Borrar todas las aristas VIAJO_CON en Neo4j (simulando drift)
    with get_driver().session() as s:
        s.run("MATCH ()-[r:VIAJO_CON]->() DELETE r")
    coincidencias_antes = grafo_repo.coincidencias(min_viajes=1)
    assert len(coincidencias_antes) == 0

    # Reconciliar
    stats = reconciliacion_service.sync_neo4j_desde_mongo()
    assert stats["pares_reconstruidos"] == 2

    # Verificar que las aristas están de nuevo
    coincidencias_despues = grafo_repo.coincidencias(min_viajes=1)
    assert len(coincidencias_despues) == 2
    cantidades = sorted(c["viajes"] for c in coincidencias_despues)
    assert cantidades == [1, 3]


def test_sync_sin_viajes_devuelve_cero(mongo_clean, neo4j_clean):
    from src.services import reconciliacion_service
    stats = reconciliacion_service.sync_neo4j_desde_mongo()
    assert stats["pares_reconstruidos"] == 0


def test_procesar_outbox_cuenta_pendientes(tmp_path, monkeypatch):
    from src.utils import outbox
    from src.services import reconciliacion_service

    monkeypatch.setattr(outbox, "_OUTBOX_FILE", tmp_path / "outbox.log")
    outbox.enqueue("op1")
    outbox.enqueue("op2")
    stats = reconciliacion_service.procesar_outbox()
    assert stats["pendientes"] == 2
```

- [ ] **Step 2: Tests deben fallar**

```bash
pytest tests/services/test_reconciliacion_service.py -v
```
Expected: 3 FAIL.

- [ ] **Step 3: Implementar `src/services/reconciliacion_service.py`**

```python
"""Reconciliation service: rebuild de proyecciones desde el SOT.

Garantiza eventual consistency entre Mongo (SOT de viajes) y las bases
derivadas (Neo4j para el caso 5, principalmente).

Modos de uso:
- Manual desde el menú admin del Plan 04.
- Periódico (no implementado en el TP — el menú alcanza).
"""
from src.db.mongo import get_db
from src.db.neo4j_db import get_driver
from src.utils import outbox
from src.utils.logger import logger


def sync_neo4j_desde_mongo() -> dict:
    """Reconstruye las aristas VIAJO_CON en Neo4j desde Mongo.

    Devuelve {'pares_reconstruidos': N, 'viajes_procesados': M}.
    """
    # 1. Agregar viajes finalizados por pareja en Mongo
    pipeline = [
        {"$match": {"estado": "FINALIZADO"}},
        {"$group": {
            "_id": {"u": "$usuario_id", "c": "$conductor_id"},
            "n":   {"$sum": 1},
        }},
    ]
    pares = list(get_db().viajes.aggregate(pipeline))
    total_viajes = sum(p["n"] for p in pares)

    # 2. Aplicar a Neo4j (borra + recrea aristas)
    with get_driver().session() as s:
        # Borrar todas las aristas VIAJO_CON (deja los nodos)
        s.run("MATCH ()-[r:VIAJO_CON]->() DELETE r")
        # Recrear con los conteos correctos
        for par in pares:
            s.run(
                """
                MERGE (u:Usuario   {id: $uid})
                MERGE (c:Conductor {id: $cid})
                MERGE (u)-[r:VIAJO_CON]->(c)
                SET r.cantidad_viajes = $n
                """,
                uid=par["_id"]["u"],
                cid=par["_id"]["c"],
                n=par["n"],
            )

    logger.info(f"Reconciliación: {len(pares)} pares, {total_viajes} viajes")
    return {"pares_reconstruidos": len(pares), "viajes_procesados": total_viajes}


def procesar_outbox() -> dict:
    """Reporta cuántas entradas hay pendientes en el outbox.

    Para el TP no implementamos retries automáticos — el flujo es:
    ver pendientes → correr sync_neo4j_desde_mongo() → outbox.clear().
    """
    pendientes = outbox.pending()
    return {"pendientes": len(pendientes), "entradas": pendientes}
```

- [ ] **Step 4: Tests deben pasar**

```bash
pytest tests/services/test_reconciliacion_service.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/services/reconciliacion_service.py tests/services/test_reconciliacion_service.py
git commit -m "agregar reconciliacion_service para rebuild de Neo4j desde Mongo (3 tests)"
git push
```

---

## Sección 8 — Verificación final

### Task 8.1: Corrida completa

- [ ] **Step 1: Correr todos los tests**

```bash
pytest tests/ -v
```
Expected: **120+ tests passed** (7 smoke + 4 outbox + ~84 repositories + ~35 services). Tiempo total estimado: 2-3 minutos por la latencia cloud.

- [ ] **Step 2: Verificar que el outbox.log existe y se puede limpiar**

```bash
ls -la outbox.log 2>/dev/null || echo "(no hubo proyecciones fallidas)"
# Si existe, limpiar:
rm -f outbox.log
```

- [ ] **Step 3: Marcar Fase 5 completa en `docs/tareas.md`**

Marcar la **Fase 5** (sub-fases 5.1-5.7) como completa.

- [ ] **Step 4: Actualizar nota de seguimiento**

Agregar a `docs/tareas.md`:
```
- 2026-MM-DD: Plan 03 completo. Los 7 services están implementados con tests
  de integración multi-DB verdes. El patrón write-through best-effort + outbox
  funciona end-to-end. Listo para empezar Plan 04 (casos de uso + menú).
```

- [ ] **Step 5: Commit final**

```bash
git add docs/tareas.md
git commit -m "marcar Fase 5 (services) como completada en docs/tareas.md"
git push
```

---

## Cierre del plan

Estado esperado al finalizar:

```
✅ src/utils/outbox.py funcional (cola en archivo)
✅ src/services/ con 7 modulos
✅ tests/services/ con 7 archivos de tests
✅ ~35 tests de integracion multi-DB verdes
✅ Patron write-through best-effort funcionando en todas las operaciones multi-DB
✅ Reconciliación implementada y testeada
✅ Todo versionado en GitHub
```

**Trazabilidad de "interacción entre bases" (lo que más le interesa al profesor):**

| Operación de negocio | Bases tocadas |
|---|---|
| Registrar usuario | Postgres + Neo4j |
| Registrar conductor | Postgres + Neo4j |
| Login | Postgres + Redis + Mongo |
| Logout | Redis + Mongo |
| Registrar vehículo | Postgres + Neo4j |
| Solicitar viaje | Postgres + Mongo (snapshots) |
| Finalizar viaje | Mongo + Cassandra + Neo4j + Redis |
| Procesar pago | Mongo |
| Crear reseña | Mongo + Postgres + Neo4j + Redis |
| Reportar GPS | Cassandra + Redis |
| Reconciliar | Mongo + Neo4j |

**Siguiente paso:** escribir `docs/plan-04-use-cases-menu.md` para implementar los 7 casos de uso y el menú interactivo de consola.
