# Plan 01 — Foundation: Infraestructura cloud + esqueleto Python + esquemas

> **Para agentes:** REQUIRED SUB-SKILL: Usar `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans` para implementar este plan tarea por tarea. Los pasos usan checkboxes `- [ ]` para tracking.

**Goal:** Tener las 5 bases de datos cloud configuradas, conectadas desde Python y con sus esquemas creados, dejando el proyecto listo para empezar a implementar la capa de repositories en el siguiente plan.

**Architecture:** Setup secuencial. Primero se crean las 5 cuentas cloud y se guardan las credenciales en `.env`. Después se arma el esqueleto Python (venv + dependencias + estructura de carpetas + utils). Por último, una conexión por base con su esquema/DDL, validando con un check explícito. Cierra con dos scripts auxiliares: `check_connections.py` (health check) y `reset_all_dbs.py` (limpieza administrativa).

**Tech Stack:** Python 3.11+, `psycopg`, `pymongo`, `cassandra-driver`, `neo4j`, `redis`, `python-dotenv`, `bcrypt`.

---

## Alcance de este plan

Cubre las **Fases 1, 2 y parte de 3** de `docs/tareas.md`. **NO incluye** repositories, services, casos de uso, menú ni seeding — esos van en planes siguientes.

**Entregables al finalizar:**

- ✅ 5 bases de datos cloud activas con credenciales en `.env`: Neon (Postgres), Atlas (Mongo), Astra (Cassandra), Aura (Neo4j), Redis Cloud.
- ✅ Proyecto Python con `venv`, dependencias instaladas y estructura de carpetas establecida.
- ✅ 5 módulos de conexión en `src/db/`, uno por base, todos con función `check()`.
- ✅ DDL/esquemas ejecutados en cada base.
- ✅ `scripts/check_connections.py` que verifica las 5 conexiones simultáneas e imprime un reporte.
- ✅ `scripts/reset_all_dbs.py` que limpia todas las bases (uso administrativo, con confirmación).

**Plan siguiente:** repositories layer + más utils (`outbox`).

---

## File Structure

Archivos que se crean en este plan (ya existentes marcados con ✓):

```
✓ .gitignore
✓ README.md
✓ CLAUDE.md
✓ docs/...

  .env.example                  ◄── plantilla de variables (versionada)
  .env                          ◄── credenciales reales (gitignored)
  requirements.txt              ◄── dependencias Python

  src/
  ├── __init__.py
  ├── config.py                 ◄── carga .env + valida variables
  ├── db/
  │   ├── __init__.py
  │   ├── postgres.py           ◄── conexión PG + check()
  │   ├── mongo.py              ◄── cliente Mongo + check()
  │   ├── cassandra.py          ◄── sesión Cassandra + check()
  │   ├── neo4j_db.py           ◄── driver Neo4j + check()
  │   └── redis_db.py           ◄── cliente Redis + check()
  └── utils/
      ├── __init__.py
      ├── logger.py             ◄── logger configurado
      └── errors.py             ◄── excepciones del dominio

  scripts/
  ├── init_postgres.sql         ◄── DDL Postgres
  ├── init_mongo.py             ◄── crea índices en Mongo
  ├── init_cassandra.cql        ◄── DDL Cassandra
  ├── init_neo4j.cypher         ◄── constraints + índices Neo4j
  ├── check_connections.py      ◄── verifica las 5 conexiones
  └── reset_all_dbs.py          ◄── limpia las 5 bases (admin)

  tests/                        ◄── carpeta lista para próximos planes
  └── __init__.py
```

---

## Sección 1 — Cuentas cloud y credenciales (Fase 1 de tareas.md)

> **Nota:** estas tareas son **manuales** (apuntar y clickear en sitios web). No hay código que escribir. Cada tarea termina con credenciales agregadas al archivo `.env` local. **El `.env` NO se commitea** (ya está en `.gitignore`).
>
> **Importante:** crear `.env` vacío antes de empezar si no existe:
> ```bash
> touch .env
> ```

### Task 1.1: Crear cuenta y DB en Neon (PostgreSQL)

- [ ] **Step 1: Crear cuenta en Neon**

Abrir https://neon.tech y registrarse con GitHub o email.

- [ ] **Step 2: Crear nuevo proyecto**

Click en "Create Project". Nombre: `tp-uber`. Elegir la región más cercana (probablemente `aws-us-east-2` o `aws-sa-east-1` si está disponible).

- [ ] **Step 3: Copiar el connection string**

En el dashboard del proyecto → "Connection Details" → copiar el connection string completo. Formato:
```
postgresql://<usuario>:<password>@<host>/<db>?sslmode=require
```

- [ ] **Step 4: Agregar a .env**

Editar el archivo `.env` y agregar:
```
POSTGRES_URL=postgresql://<usuario>:<password>@<host>/<db>?sslmode=require
```

- [ ] **Step 5: Verificar conexión desde la SQL Editor de Neon**

En el dashboard de Neon → "SQL Editor" → ejecutar:
```sql
SELECT 1 AS ok;
```
Expected: una fila con `ok = 1`.

- [ ] **Step 6: (Sin commit, .env está gitignored)**

No hay nada que commitear. Continuar con la siguiente tarea.

---

### Task 1.2: Crear cluster en MongoDB Atlas

- [ ] **Step 1: Crear cuenta**

Abrir https://www.mongodb.com/cloud/atlas/register y registrarse.

- [ ] **Step 2: Crear organización + proyecto**

Aceptar las defaults o nombrar la organización `UADE` y el proyecto `tp-uber`.

- [ ] **Step 3: Crear cluster M0 (Free)**

Click "Build a Database" → elegir **M0 Free** → provider AWS (recomendado) → región más cercana (`sa-east-1` o `us-east-1`). Click "Create Deployment".

- [ ] **Step 4: Crear usuario de DB**

En el wizard "Security Quickstart" → username: `tp_user`, password: generar y **guardar**. Click "Create User".

- [ ] **Step 5: Configurar Network Access**

En el mismo wizard → "Add Your Current IP Address" y también agregar `0.0.0.0/0` (allow from anywhere — solo OK para desarrollo). Click "Finish".

- [ ] **Step 6: Obtener connection string**

En el cluster → botón "Connect" → "Drivers" → Python → copiar el connection string. Reemplazar `<password>` por el password del Step 4.

- [ ] **Step 7: Agregar a .env**

```
MONGO_URL=mongodb+srv://tp_user:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority&appName=...
```

- [ ] **Step 8: Verificar conexión desde Atlas**

En el cluster → "Collections" → debería mostrar "Add My Own Data" sin errores. (No crear collections todavía, lo hace `init_mongo.py`).

---

### Task 1.3: Crear DB en DataStax Astra (Cassandra)

- [ ] **Step 1: Crear cuenta**

Abrir https://astra.datastax.com y registrarse con GitHub o email.

- [ ] **Step 2: Crear nueva Database**

Click "Create Database" → tipo **Serverless** → nombre: `tp-uber` → región más cercana → keyspace: `uber_tp`. Click "Create Database". Esperar ~3 minutos a que esté "Active".

- [ ] **Step 3: Generar Application Token**

En el panel izquierdo → "Settings" → "Token Management" → seleccionar el rol **Database Administrator** → "Generate Token". Aparecen 3 valores:
- Client ID (empieza con un UUID)
- Client Secret
- Token (empieza con `AstraCS:...`)

**Copiar los 3 inmediatamente** — no se muestran de nuevo.

- [ ] **Step 4: Descargar el Secure Connect Bundle**

En la DB → tab "Connect" → "Get Bundle" → descargar el `.zip`. **Guardarlo en una carpeta fuera del repo**, por ejemplo:
```
C:\Users\<vos>\secrets\secure-connect-tp-uber.zip
```

- [ ] **Step 5: Agregar a .env**

```
ASTRA_BUNDLE_PATH=C:\Users\<vos>\secrets\secure-connect-tp-uber.zip
ASTRA_CLIENT_ID=<el client id>
ASTRA_CLIENT_SECRET=<el client secret>
ASTRA_KEYSPACE=uber_tp
```

- [ ] **Step 6: Verificar conexión desde CQL Console**

En la DB → tab "CQL Console" → ejecutar:
```cql
SELECT release_version FROM system.local;
```
Expected: una fila con la versión de Cassandra.

---

### Task 1.4: Crear instancia AuraDB Free (Neo4j)

- [ ] **Step 1: Crear cuenta**

Abrir https://console.neo4j.io y registrarse.

- [ ] **Step 2: Crear instancia AuraDB Free**

Click "Create instance" → tipo **AuraDB Free** → región más cercana → nombre: `tp-uber`. Click "Create".

- [ ] **Step 3: COPIAR EL PASSWORD INMEDIATAMENTE**

Se muestra una vez en pantalla. **Si la cerrás, perdés el password y hay que crear otra instancia.**

- [ ] **Step 4: Anotar el URI**

Formato: `neo4j+s://<id>.databases.neo4j.io`

- [ ] **Step 5: Agregar a .env**

```
NEO4J_URI=neo4j+s://<id>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<el password del Step 3>
```

- [ ] **Step 6: Verificar conexión con Neo4j Browser**

Click "Query" en la UI de Aura → abre Neo4j Browser → ejecutar:
```cypher
RETURN 1 AS ok;
```
Expected: una fila con `ok = 1`.

---

### Task 1.5: Crear DB en Redis Cloud o Upstash

- [ ] **Step 1: Elegir proveedor y crear cuenta**

Opción recomendada: https://redis.com/try-free → registrarse. Alternativa más simple: https://upstash.com.

- [ ] **Step 2: Crear free DB**

En Redis Cloud → "New database" → free tier (30 MB) → región más cercana → nombre: `tp-uber-cache`. Click "Activate".

- [ ] **Step 3: Obtener credenciales**

En la DB → "Configuration" → copiar:
- **Public endpoint** (formato: `<host>:<port>`)
- **Default user password**

- [ ] **Step 4: Agregar a .env**

```
REDIS_HOST=<host>
REDIS_PORT=<port>
REDIS_PASSWORD=<password>
```

- [ ] **Step 5: Verificar conexión con redis-cli web**

En Redis Cloud → "Connect" → "Redis CLI" → ejecutar:
```
PING
```
Expected: `PONG`.

---

## Sección 2 — Esqueleto Python (Fase 2 de tareas.md)

> A partir de acá hay código real. Cada tarea termina con un **commit** al repo.

### Task 2.1: Estructura de carpetas y `__init__.py` files

**Files:**
- Create: `src/__init__.py`, `src/db/__init__.py`, `src/utils/__init__.py`, `tests/__init__.py`
- Create: `scripts/` (carpeta sin `__init__.py`)

- [ ] **Step 1: Crear las carpetas**

```bash
mkdir -p src/db src/utils scripts tests
```

- [ ] **Step 2: Crear `__init__.py` vacíos**

```bash
touch src/__init__.py src/db/__init__.py src/utils/__init__.py tests/__init__.py
```

- [ ] **Step 3: Verificar la estructura**

```bash
ls -la src/ src/db/ src/utils/ scripts/ tests/
```
Expected: cada carpeta existe; las que tienen `__init__.py` lo muestran.

- [ ] **Step 4: Commit**

```bash
git add src/ scripts/ tests/
git commit -m "agregar esqueleto de carpetas src/ scripts/ tests/"
git push
```

---

### Task 2.2: `requirements.txt` y entorno virtual

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Crear `requirements.txt`**

```
psycopg[binary]==3.2.*
pymongo==4.10.*
cassandra-driver==3.29.*
neo4j==5.26.*
redis==5.2.*
python-dotenv==1.0.*
bcrypt==4.2.*
```

- [ ] **Step 2: Crear venv**

```bash
python -m venv venv
```

- [ ] **Step 3: Activar venv**

Windows (Git Bash):
```bash
source venv/Scripts/activate
```

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

- [ ] **Step 4: Instalar dependencias**

```bash
pip install -r requirements.txt
```

- [ ] **Step 5: Verificar instalación**

```bash
pip list
```
Expected: aparecen `psycopg`, `pymongo`, `cassandra-driver`, `neo4j`, `redis`, `python-dotenv`, `bcrypt`.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt
git commit -m "agregar requirements.txt con drivers de las 5 bases"
git push
```

> **Nota:** `venv/` ya está en `.gitignore`, no se commitea.

---

### Task 2.3: `.env.example` y `src/config.py`

**Files:**
- Create: `.env.example`
- Create: `src/config.py`

- [ ] **Step 1: Crear `.env.example` (plantilla con claves vacías)**

```
# PostgreSQL (Neon)
POSTGRES_URL=

# MongoDB (Atlas)
MONGO_URL=

# Cassandra (DataStax Astra)
ASTRA_BUNDLE_PATH=
ASTRA_CLIENT_ID=
ASTRA_CLIENT_SECRET=
ASTRA_KEYSPACE=uber_tp

# Neo4j (Aura)
NEO4J_URI=
NEO4J_USER=neo4j
NEO4J_PASSWORD=

# Redis (Redis Cloud o Upstash)
REDIS_HOST=
REDIS_PORT=6379
REDIS_PASSWORD=

# Logging
LOG_LEVEL=INFO
```

- [ ] **Step 2: Crear `src/config.py`**

```python
"""Configuración del proyecto cargada desde .env."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Postgres
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")
    # Mongo
    MONGO_URL: str = os.getenv("MONGO_URL", "")
    # Cassandra (Astra)
    ASTRA_BUNDLE_PATH: str = os.getenv("ASTRA_BUNDLE_PATH", "")
    ASTRA_CLIENT_ID: str = os.getenv("ASTRA_CLIENT_ID", "")
    ASTRA_CLIENT_SECRET: str = os.getenv("ASTRA_CLIENT_SECRET", "")
    ASTRA_KEYSPACE: str = os.getenv("ASTRA_KEYSPACE", "uber_tp")
    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()


def validate():
    """Verifica que las credenciales criticas estén presentes. Lanza RuntimeError si falta alguna."""
    required = [
        "POSTGRES_URL", "MONGO_URL",
        "ASTRA_BUNDLE_PATH", "ASTRA_CLIENT_ID", "ASTRA_CLIENT_SECRET",
        "NEO4J_URI", "NEO4J_PASSWORD",
        "REDIS_HOST", "REDIS_PASSWORD",
    ]
    missing = [f for f in required if not getattr(settings, f)]
    if missing:
        raise RuntimeError(f"Variables de entorno faltantes en .env: {missing}")
```

- [ ] **Step 3: Probar que `validate()` falla sin .env completo**

```bash
python -c "from src.config import validate; validate()"
```
Expected: si tu `.env` no tiene todas las claves, lanza `RuntimeError: Variables de entorno faltantes...`. Si ya completaste todas en la Sección 1, expected: no output (silencio = éxito).

- [ ] **Step 4: Si faltan, completar `.env` con los valores reales** (de las tareas 1.1-1.5)

- [ ] **Step 5: Volver a correr validate**

```bash
python -c "from src.config import validate; validate(); print('OK')"
```
Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add .env.example src/config.py
git commit -m "agregar .env.example y src/config.py con validacion de variables"
git push
```

---

### Task 2.4: `src/utils/logger.py`

**Files:**
- Create: `src/utils/logger.py`

- [ ] **Step 1: Crear el logger**

```python
"""Logger configurado del proyecto."""
import logging
from src.config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("tp_uber")
```

- [ ] **Step 2: Probar que importa y loguea**

```bash
python -c "from src.utils.logger import logger; logger.info('hola mundo')"
```
Expected: una línea con el formato `YYYY-MM-DD HH:MM:SS,mmm [INFO] tp_uber: hola mundo`.

- [ ] **Step 3: Commit**

```bash
git add src/utils/logger.py
git commit -m "agregar logger configurable del proyecto"
git push
```

---

### Task 2.5: `src/utils/errors.py`

**Files:**
- Create: `src/utils/errors.py`

- [ ] **Step 1: Crear las excepciones del dominio**

```python
"""Excepciones del dominio del TP Uber."""


class DomainError(Exception):
    """Error base del dominio. Capturable por las capas superiores."""


class EntidadInexistente(DomainError):
    """Una entidad referenciada no existe."""


class UsuarioInexistente(EntidadInexistente):
    pass


class ConductorInexistente(EntidadInexistente):
    pass


class VehiculoInexistente(EntidadInexistente):
    pass


class ViajeNoEncontrado(EntidadInexistente):
    pass


class CredencialesInvalidas(DomainError):
    """Email o password incorrectos."""


class SesionExpirada(DomainError):
    """La sesión Redis venció o no existe."""


class EstadoInvalido(DomainError):
    """Se intentó una transición de estado no permitida (ej. finalizar un viaje PENDIENTE)."""
```

- [ ] **Step 2: Probar imports**

```bash
python -c "from src.utils.errors import DomainError, ViajeNoEncontrado; raise ViajeNoEncontrado('test')"
```
Expected: traceback con `src.utils.errors.ViajeNoEncontrado: test`.

- [ ] **Step 3: Commit**

```bash
git add src/utils/errors.py
git commit -m "agregar excepciones del dominio en src/utils/errors.py"
git push
```

---

## Sección 3 — Conexiones y esquemas por base (Fase 3 de tareas.md)

> A partir de acá: un módulo de conexión por base, su DDL/init script, y una verificación.

### Task 3.1: `src/db/postgres.py` + DDL

**Files:**
- Create: `src/db/postgres.py`
- Create: `scripts/init_postgres.sql`

- [ ] **Step 1: Escribir `src/db/postgres.py`**

```python
"""Postgres connection — singleton."""
import psycopg
from src.config import settings
from src.utils.logger import logger

_conn = None


def get_conn() -> psycopg.Connection:
    """Devuelve la conexión Postgres (la crea la primera vez)."""
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg.connect(settings.POSTGRES_URL, autocommit=True)
        logger.info("Conexión a Postgres establecida")
    return _conn


def check() -> bool:
    """Devuelve True si la conexión y la query basica funcionan."""
    try:
        with get_conn().cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone() == (1,)
    except Exception as e:
        logger.error(f"Postgres check failed: {e}")
        return False
```

- [ ] **Step 2: Probar la conexión**

```bash
python -c "from src.db.postgres import check; print('OK' if check() else 'FAIL')"
```
Expected: `OK`.

- [ ] **Step 3: Escribir `scripts/init_postgres.sql`**

```sql
-- DDL inicial de Postgres para el TP Uber
-- Ejecutar una sola vez al inicio del proyecto.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS usuario (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           VARCHAR(255) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  nombre          VARCHAR(255) NOT NULL,
  telefono        VARCHAR(50),
  foto_url        VARCHAR(500),
  rating_promedio FLOAT DEFAULT 0,
  fecha_registro  TIMESTAMP DEFAULT NOW(),
  estado          VARCHAR(20) CHECK (estado IN ('ACTIVO','SUSPENDIDO','BAJA'))
                  DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS conductor (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           VARCHAR(255) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  nombre          VARCHAR(255) NOT NULL,
  telefono        VARCHAR(50),
  nro_licencia    VARCHAR(50) UNIQUE NOT NULL,
  rating_promedio FLOAT DEFAULT 0,
  estado          VARCHAR(20) CHECK (estado IN ('ACTIVO','SUSPENDIDO','BAJA'))
                  DEFAULT 'ACTIVO',
  fecha_registro  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehiculo (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conductor_id UUID REFERENCES conductor(id) ON DELETE CASCADE,
  placa        VARCHAR(20) UNIQUE NOT NULL,
  marca        VARCHAR(50) NOT NULL,
  modelo       VARCHAR(50) NOT NULL,
  anio         INT,
  color        VARCHAR(30),
  tipo         VARCHAR(30)
);

CREATE INDEX IF NOT EXISTS idx_vehiculo_conductor ON vehiculo(conductor_id);
CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuario(email);
CREATE INDEX IF NOT EXISTS idx_conductor_email ON conductor(email);
```

- [ ] **Step 4: Ejecutar el DDL desde la SQL Editor de Neon**

Abrir Neon dashboard → SQL Editor → pegar todo el contenido de `init_postgres.sql` → Run. Expected: "Query executed successfully".

- [ ] **Step 5: Verificar que las tablas existen**

En la misma SQL Editor:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;
```
Expected: 3 filas: `conductor`, `usuario`, `vehiculo`.

- [ ] **Step 6: Commit**

```bash
git add src/db/postgres.py scripts/init_postgres.sql
git commit -m "agregar conexion a Postgres y DDL inicial (usuario, conductor, vehiculo)"
git push
```

---

### Task 3.2: `src/db/mongo.py` + indexes

**Files:**
- Create: `src/db/mongo.py`
- Create: `scripts/init_mongo.py`

- [ ] **Step 1: Escribir `src/db/mongo.py`**

```python
"""MongoDB connection — singleton."""
from pymongo import MongoClient
from pymongo.database import Database
from src.config import settings
from src.utils.logger import logger

_client: MongoClient | None = None
_DB_NAME = "uber_tp"


def get_client() -> MongoClient:
    """Devuelve el cliente Mongo (lo crea la primera vez)."""
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URL)
        logger.info("Conexión a MongoDB establecida")
    return _client


def get_db() -> Database:
    """Devuelve la database `uber_tp`."""
    return get_client()[_DB_NAME]


def check() -> bool:
    """Devuelve True si la conexión y el ping funcionan."""
    try:
        get_client().admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"Mongo check failed: {e}")
        return False
```

- [ ] **Step 2: Probar la conexión**

```bash
python -c "from src.db.mongo import check; print('OK' if check() else 'FAIL')"
```
Expected: `OK`.

- [ ] **Step 3: Escribir `scripts/init_mongo.py`**

```python
"""Crea los índices necesarios en las colecciones de Mongo."""
from src.db.mongo import get_db
from src.utils.logger import logger


def main():
    db = get_db()

    # viajes
    db.viajes.create_index([("usuario_id", 1)])
    db.viajes.create_index([("conductor_id", 1)])
    db.viajes.create_index([("estado", 1), ("ts_inicio", -1)])
    db.viajes.create_index([("ts_fin", -1)])

    # pagos
    db.pagos.create_index([("viaje_id", 1)])
    db.pagos.create_index([("metodo_pago", 1)])
    db.pagos.create_index([("estado", 1), ("timestamp", -1)])

    # resenas
    db.resenas.create_index([("autor.id", 1)])
    db.resenas.create_index([("destinatario.id", 1)])
    db.resenas.create_index([("tipo", 1), ("rating", 1)])
    db.resenas.create_index([("rating", 1)])

    # login_history
    db.login_history.create_index([("usuario_id", 1), ("timestamp", -1)])
    db.login_history.create_index([("evento", 1)])

    logger.info("Índices creados en MongoDB")
    print("OK: índices creados en MongoDB")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Ejecutar el script**

```bash
python -m scripts.init_mongo
```
Expected: `OK: índices creados en MongoDB`.

- [ ] **Step 5: Verificar índices desde Atlas UI**

En Atlas → Collections → la database `uber_tp` → cada colección debería tener un tab "Indexes" con los índices creados (además del `_id` default).

- [ ] **Step 6: Commit**

```bash
git add src/db/mongo.py scripts/init_mongo.py
git commit -m "agregar conexion a Mongo y script de inicializacion de indices"
git push
```

---

### Task 3.3: `src/db/cassandra.py` + DDL

**Files:**
- Create: `src/db/cassandra.py`
- Create: `scripts/init_cassandra.cql`

- [ ] **Step 1: Escribir `src/db/cassandra.py`**

```python
"""Cassandra (DataStax Astra) connection — singleton."""
from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from src.config import settings
from src.utils.logger import logger

_session: Session | None = None


def get_session() -> Session:
    """Devuelve la sesión Cassandra (la crea la primera vez)."""
    global _session
    if _session is None:
        cloud_config = {"secure_connect_bundle": settings.ASTRA_BUNDLE_PATH}
        auth = PlainTextAuthProvider(
            settings.ASTRA_CLIENT_ID, settings.ASTRA_CLIENT_SECRET
        )
        cluster = Cluster(cloud=cloud_config, auth_provider=auth)
        _session = cluster.connect(settings.ASTRA_KEYSPACE)
        logger.info("Conexión a Cassandra (Astra) establecida")
    return _session


def check() -> bool:
    """Devuelve True si la sesión y la query basica funcionan."""
    try:
        result = get_session().execute("SELECT release_version FROM system.local")
        return result.one() is not None
    except Exception as e:
        logger.error(f"Cassandra check failed: {e}")
        return False
```

- [ ] **Step 2: Probar la conexión**

```bash
python -c "from src.db.cassandra import check; print('OK' if check() else 'FAIL')"
```
Expected: `OK`. **Si falla**, verificar que `ASTRA_BUNDLE_PATH` apunte al `.zip` correcto (path absoluto, sin comillas).

- [ ] **Step 3: Escribir `scripts/init_cassandra.cql`**

```cql
-- DDL inicial de Cassandra (Astra) para el TP Uber
-- Ejecutar en CQL Console (usar keyspace uber_tp).

CREATE TABLE IF NOT EXISTS ubicaciones_por_vehiculo (
  vehiculo_id UUID,
  ts          TIMESTAMP,
  lat         DECIMAL,
  lon         DECIMAL,
  precision_m FLOAT,
  viaje_id    UUID,
  PRIMARY KEY (vehiculo_id, ts)
) WITH CLUSTERING ORDER BY (ts DESC);

CREATE TABLE IF NOT EXISTS ultima_actividad_conductor (
  conductor_id    UUID PRIMARY KEY,
  ultimo_viaje_ts TIMESTAMP,
  ultimo_viaje_id UUID
);

CREATE TABLE IF NOT EXISTS viajes_finalizados_por_dia (
  dia          DATE,
  viaje_id     UUID,
  conductor_id UUID,
  usuario_id   UUID,
  duracion_min INT,
  distancia_km FLOAT,
  PRIMARY KEY (dia, viaje_id)
);
```

- [ ] **Step 4: Ejecutar el DDL desde la CQL Console de Astra**

En Astra → la DB → tab "CQL Console" → asegurar que estás en el keyspace `uber_tp` (botón "Use Keyspace") → pegar cada CREATE TABLE individualmente y Enter. Expected: tres resultados "OK".

- [ ] **Step 5: Verificar las tablas**

En la CQL Console:
```cql
DESCRIBE TABLES;
```
Expected: las 3 tablas listadas.

- [ ] **Step 6: Commit**

```bash
git add src/db/cassandra.py scripts/init_cassandra.cql
git commit -m "agregar conexion a Cassandra y DDL inicial (ubicaciones, actividad, viajes_finalizados)"
git push
```

---

### Task 3.4: `src/db/neo4j_db.py` + constraints

**Files:**
- Create: `src/db/neo4j_db.py`
- Create: `scripts/init_neo4j.cypher`

- [ ] **Step 1: Escribir `src/db/neo4j_db.py`**

```python
"""Neo4j (Aura) connection — singleton driver."""
from neo4j import GraphDatabase, Driver
from src.config import settings
from src.utils.logger import logger

_driver: Driver | None = None


def get_driver() -> Driver:
    """Devuelve el driver Neo4j (lo crea la primera vez)."""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        logger.info("Conexión a Neo4j (Aura) establecida")
    return _driver


def check() -> bool:
    """Devuelve True si el driver y la query basica funcionan."""
    try:
        with get_driver().session() as s:
            record = s.run("RETURN 1 AS ok").single()
            return record is not None and record["ok"] == 1
    except Exception as e:
        logger.error(f"Neo4j check failed: {e}")
        return False
```

- [ ] **Step 2: Probar la conexión**

```bash
python -c "from src.db.neo4j_db import check; print('OK' if check() else 'FAIL')"
```
Expected: `OK`.

- [ ] **Step 3: Escribir `scripts/init_neo4j.cypher`**

```cypher
// Constraints e índices iniciales para Neo4j (TP Uber)
// Ejecutar en Neo4j Browser, una línea a la vez (o pegar bloques).

CREATE CONSTRAINT usuario_id_unique   IF NOT EXISTS FOR (u:Usuario)   REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT conductor_id_unique IF NOT EXISTS FOR (c:Conductor) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT vehiculo_id_unique  IF NOT EXISTS FOR (v:Vehiculo)  REQUIRE v.id IS UNIQUE;

CREATE INDEX vehiculo_marca IF NOT EXISTS FOR (v:Vehiculo) ON (v.marca);
CREATE INDEX vehiculo_placa IF NOT EXISTS FOR (v:Vehiculo) ON (v.placa);
```

- [ ] **Step 4: Ejecutar las constraints en Neo4j Browser**

Abrir Neo4j Browser desde Aura → pegar cada línea y ejecutar (cada CREATE devuelve OK aunque ya exista).

- [ ] **Step 5: Verificar las constraints**

```cypher
SHOW CONSTRAINTS;
```
Expected: 3 filas con las constraints UNIQUE.

```cypher
SHOW INDEXES;
```
Expected: incluye `vehiculo_marca` y `vehiculo_placa`.

- [ ] **Step 6: Commit**

```bash
git add src/db/neo4j_db.py scripts/init_neo4j.cypher
git commit -m "agregar conexion a Neo4j y constraints/indices iniciales"
git push
```

---

### Task 3.5: `src/db/redis_db.py`

**Files:**
- Create: `src/db/redis_db.py`

> **Nota:** Redis no tiene esquema, así que no hay script de inicialización. Las convenciones de claves se documentan dentro del módulo.

- [ ] **Step 1: Escribir `src/db/redis_db.py`**

```python
"""Redis connection — singleton.

Convenciones de claves usadas en el proyecto:

    session:{token}             → JSON con datos de la sesión (TTL 10 min)
    vehiculo:{id}:pos           → "lat,lon" (TTL 30 s)
    cache:top3_resenadores      → JSON (TTL 5 min)
    cache:viajes_promedio       → JSON (TTL 5 min)
"""
import redis
from src.config import settings
from src.utils.logger import logger

_client: redis.Redis | None = None


def get_client() -> redis.Redis:
    """Devuelve el cliente Redis (lo crea la primera vez)."""
    global _client
    if _client is None:
        _client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        logger.info("Conexión a Redis establecida")
    return _client


def check() -> bool:
    """Devuelve True si el ping funciona."""
    try:
        return bool(get_client().ping())
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        return False
```

- [ ] **Step 2: Probar la conexión**

```bash
python -c "from src.db.redis_db import check; print('OK' if check() else 'FAIL')"
```
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add src/db/redis_db.py
git commit -m "agregar conexion a Redis con convenciones de claves documentadas"
git push
```

---

### Task 3.6: `scripts/check_connections.py`

**Files:**
- Create: `scripts/check_connections.py`

- [ ] **Step 1: Escribir el script**

```python
"""Verifica que las 5 conexiones a las bases de datos funcionan.

Uso:
    python -m scripts.check_connections

Exit code 0 si todas OK, 1 si alguna falla.
"""
import sys
from src.config import validate
from src.db import postgres, mongo, cassandra, neo4j_db, redis_db


def main() -> int:
    print("Validando .env...")
    validate()
    print("OK\n")

    bases = [
        ("Postgres   (Neon)",   postgres.check),
        ("MongoDB    (Atlas)",  mongo.check),
        ("Cassandra  (Astra)",  cassandra.check),
        ("Neo4j      (Aura)",   neo4j_db.check),
        ("Redis      (Cloud)",  redis_db.check),
    ]

    print("Verificando conexiones a las bases:")
    todos_ok = True
    for nombre, check_fn in bases:
        ok = check_fn()
        estado = "OK  " if ok else "FAIL"
        print(f"  [{estado}] {nombre}")
        if not ok:
            todos_ok = False

    print()
    if todos_ok:
        print("Todas las bases respondieron correctamente.")
        return 0
    else:
        print("Hay bases con problemas. Revisar logs y credenciales.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Ejecutar el script**

```bash
python -m scripts.check_connections
```
Expected:
```
Validando .env...
OK

Verificando conexiones a las bases:
  [OK  ] Postgres   (Neon)
  [OK  ] MongoDB    (Atlas)
  [OK  ] Cassandra  (Astra)
  [OK  ] Neo4j      (Aura)
  [OK  ] Redis      (Cloud)

Todas las bases respondieron correctamente.
```

Y exit code 0 (verificar con `echo $?`).

- [ ] **Step 3: Commit**

```bash
git add scripts/check_connections.py
git commit -m "agregar script de health-check de las 5 conexiones"
git push
```

---

### Task 3.7: `scripts/reset_all_dbs.py`

**Files:**
- Create: `scripts/reset_all_dbs.py`

> **⚠️ Este script borra todos los datos de las 5 bases.** Solo se usa en desarrollo o como parte del demo en la presentación.

- [ ] **Step 1: Escribir el script**

```python
"""Limpia (vacía) las 5 bases de datos del proyecto. SOLO PARA DESARROLLO.

Uso:
    python -m scripts.reset_all_dbs

Pide confirmación interactiva antes de borrar.
"""
import sys
from src.config import settings, validate
from src.db import postgres, mongo, cassandra, neo4j_db, redis_db
from src.utils.logger import logger


def reset_postgres():
    with postgres.get_conn().cursor() as cur:
        cur.execute("TRUNCATE vehiculo, conductor, usuario CASCADE;")
    logger.info("Postgres: tablas truncadas")


def reset_mongo():
    db = mongo.get_db()
    for coll in ["viajes", "pagos", "resenas", "login_history"]:
        db[coll].drop()
    logger.info("Mongo: colecciones dropeadas")


def reset_cassandra():
    session = cassandra.get_session()
    for table in ["ubicaciones_por_vehiculo", "ultima_actividad_conductor", "viajes_finalizados_por_dia"]:
        session.execute(f"TRUNCATE {table}")
    logger.info("Cassandra: tablas truncadas")


def reset_neo4j():
    with neo4j_db.get_driver().session() as s:
        s.run("MATCH (n) DETACH DELETE n")
    logger.info("Neo4j: nodos y aristas borrados")


def reset_redis():
    redis_db.get_client().flushdb()
    logger.info("Redis: FLUSHDB ejecutado")


def main() -> int:
    validate()

    print("⚠️  ATENCIÓN: este script va a borrar TODOS los datos de las 5 bases:")
    print(f"   Postgres ({settings.POSTGRES_URL[:40]}...)")
    print(f"   Mongo    ({settings.MONGO_URL[:40]}...)")
    print(f"   Cassandra keyspace: {settings.ASTRA_KEYSPACE}")
    print(f"   Neo4j    ({settings.NEO4J_URI})")
    print(f"   Redis    ({settings.REDIS_HOST})")
    print()
    confirm = input('Escribí exactamente "BORRAR" para confirmar: ')
    if confirm != "BORRAR":
        print("Cancelado.")
        return 1

    reset_postgres()
    reset_mongo()
    reset_cassandra()
    reset_neo4j()
    reset_redis()

    print("\nLimpieza completa.")
    print("Recordá correr `python -m scripts.init_mongo` para recrear los índices de Mongo (los demás esquemas se preservan).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: NO ejecutarlo todavía (todavía no hay datos que borrar, pero igual está OK probarlo)**

Si querés probarlo:
```bash
python -m scripts.reset_all_dbs
```
Escribir `BORRAR` cuando pida confirmación. Expected: 5 mensajes "Limpieza" y exit 0.

- [ ] **Step 3: Recrear índices de Mongo después del reset**

```bash
python -m scripts.init_mongo
```

- [ ] **Step 4: Volver a correr el health check**

```bash
python -m scripts.check_connections
```
Expected: las 5 bases siguen respondiendo OK (truncate no rompe la conexión).

- [ ] **Step 5: Commit**

```bash
git add scripts/reset_all_dbs.py
git commit -m "agregar script administrativo para resetear las 5 bases con confirmacion"
git push
```

---

## Sección 4 — Verificación final

### Task 4.1: Health check end-to-end

- [ ] **Step 1: Correr el health check una última vez**

```bash
python -m scripts.check_connections
```
Expected: las 5 bases responden OK.

- [ ] **Step 2: Verificar tablas/colecciones existentes**

```bash
# Postgres (desde la SQL Editor de Neon)
SELECT table_name FROM information_schema.tables WHERE table_schema='public';
# Expected: usuario, conductor, vehiculo

# Cassandra (desde CQL Console)
DESCRIBE TABLES;
# Expected: ubicaciones_por_vehiculo, ultima_actividad_conductor, viajes_finalizados_por_dia

# Neo4j (desde Neo4j Browser)
SHOW CONSTRAINTS;
# Expected: 3 constraints UNIQUE
```

- [ ] **Step 3: Marcar tareas completadas en `docs/tareas.md`**

Marcar como `[x]` en `docs/tareas.md`:
- Toda la Fase 1 (las 5 sub-fases 1.1-1.5 + verificación end-to-end 1.6).
- Las sub-fases 2.2-2.5 de la Fase 2.
- Toda la Fase 3.

- [ ] **Step 4: Actualizar la nota de seguimiento en `tareas.md`**

Agregar al final de la sección "Notas de seguimiento":
```
- 2026-MM-DD: Fundación completa. Las 5 bases cloud están activas, conectadas desde Python y con esquemas inicializados. `check_connections.py` devuelve OK para las 5. Listo para empezar Plan 02 (repositories).
```

- [ ] **Step 5: Commit final del plan**

```bash
git add docs/tareas.md
git commit -m "marcar Fases 1-3 como completadas en docs/tareas.md"
git push
```

- [ ] **Step 6: Verificar el repo en GitHub**

Abrir https://github.com/lucianolacheta1/TP-Datos2-Uber y confirmar que aparece toda la estructura nueva (`src/`, `scripts/`, `requirements.txt`, `.env.example`, etc.).

---

## Cierre del plan

Cuando todas las tareas estén con `[x]`, este plan está completo. Estado esperado:

```
✅ 5 cuentas cloud creadas con credenciales en .env (local)
✅ Proyecto Python con venv, dependencias, estructura modular
✅ src/config.py con validación de .env
✅ src/utils/{logger,errors}.py
✅ src/db/{postgres,mongo,cassandra,neo4j_db,redis_db}.py
✅ Esquemas en Postgres, Mongo (índices), Cassandra y Neo4j
✅ scripts/check_connections.py funcionando
✅ scripts/reset_all_dbs.py funcionando
✅ Todo versionado en GitHub
```

**Siguiente paso:** escribir `docs/plan-02-repositories.md` para implementar la capa de repositorios sobre estos cimientos.
