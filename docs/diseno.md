# Diseño del Sistema — TP Uber (UADE — Datos 2)

> Documento técnico vivo. Audiencia: equipo de desarrollo.
> Última actualización: 2026-05-19

## Tabla de contenidos

1. [Contexto del proyecto](#1-contexto-del-proyecto)
2. [Stack tecnológico](#2-stack-tecnológico)
3. [Patrón arquitectónico](#3-patrón-arquitectónico)
4. [Modelo de datos por base](#4-modelo-de-datos-por-base)
5. [Mapeo de casos de uso → base](#5-mapeo-de-casos-de-uso--base)
6. [Flujo de datos y consistencia](#6-flujo-de-datos-y-consistencia)
7. [Estructura del proyecto Python](#7-estructura-del-proyecto-python)

> **Plan de presentación:** ver documento separado en [`docs/presentacion.md`](presentacion.md).

---

## 1. Contexto del proyecto

Sistema de gestión de datos para una plataforma de transporte compartido tipo Uber. TP para la materia **Datos 2** de UADE, cátedra Mosquera Prada.

**Requisito clave de la materia:**
> *"Es motivo de desaprobar que las bases de datos no interactúen entre sí."* — Profesor Mosquera (video de presentación)

El proyecto debe usar **1 base relacional + 3 NoSQL** mínimo. Vamos a usar **5 bases en total** (Postgres + 4 NoSQL) como bonus.

**Equipo:** trabajo grupal. Fecha de entrega: más de un mes.

---

## 2. Stack tecnológico

| Capa | Tecnología | Hosting | Tier gratuito |
|---|---|---|---|
| Lenguaje | **Python 3.11+** | Local | — |
| Base relacional | **PostgreSQL** | Neon | Sí, permanente |
| Base documental | **MongoDB** | Atlas | Sí, 512 MB |
| Base columnar | **Cassandra** | Astra DB | Sí |
| Base de grafo | **Neo4j** | Aura | Sí, 1 DB, 200k nodos |
| Cache / sesiones | **Redis** | Redis Cloud / Upstash | Sí, 30 MB |
| Interfaz | Consola con menú numérico | Local | — |

### Drivers Python

```
psycopg[binary]      → PostgreSQL
pymongo              → MongoDB
cassandra-driver     → Cassandra
neo4j                → Neo4j
redis                → Redis
python-dotenv        → variables de entorno
bcrypt               → hash de contraseñas
```

---

## 3. Patrón arquitectónico

**Postgres como catálogo mínimo de identidad; NoSQL como almacén operativo.**

Este patrón replica el ejemplo del profesor en el video:

- **Postgres** mantiene solo las entidades estables que requieren integridad referencial: usuarios, conductores, vehículos.
- **MongoDB** guarda los datos operativos ricos: viajes, pagos, reseñas.
- **Cassandra** guarda series temporales: ubicaciones GPS y agregados de actividad.
- **Neo4j** guarda relaciones derivadas: coincidencias usuario-conductor.
- **Redis** guarda estado efímero: sesiones, última posición, caché de queries.

### Volúmenes esperados

| Base | Volumen relativo | Justificación |
|---|---|---|
| Postgres | 🟢 Bajo | Catálogo estable, ~miles de filas en total |
| Mongo | 🟡 Medio | 1 documento por viaje, 1 por pago, 0-2 por reseña |
| Cassandra | 🔴 Alto | Miles de filas por vehículo activo por día (GPS time-series) |
| Neo4j | 🟡 Medio | 1 nodo por entidad, 1 arista por par usuario-conductor |
| Redis | 🟢 Bajo | Solo claves vivas: sesiones activas + caches |

---

## 4. Modelo de datos por base

### 4.1 PostgreSQL — catálogo de identidad

```sql
CREATE TABLE usuario (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           VARCHAR(255) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  nombre          VARCHAR(255) NOT NULL,
  telefono        VARCHAR(50),
  foto_url        VARCHAR(500),
  rating_promedio FLOAT DEFAULT 0,
  fecha_registro  TIMESTAMP DEFAULT NOW(),
  estado          VARCHAR(20) CHECK (estado IN ('ACTIVO','SUSPENDIDO','BAJA'))
);

CREATE TABLE conductor (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           VARCHAR(255) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  nombre          VARCHAR(255) NOT NULL,
  telefono        VARCHAR(50),
  nro_licencia    VARCHAR(50) UNIQUE NOT NULL,
  rating_promedio FLOAT DEFAULT 0,
  estado          VARCHAR(20) CHECK (estado IN ('ACTIVO','SUSPENDIDO','BAJA')),
  fecha_registro  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vehiculo (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conductor_id UUID REFERENCES conductor(id) ON DELETE CASCADE,
  placa        VARCHAR(20) UNIQUE NOT NULL,
  marca        VARCHAR(50) NOT NULL,
  modelo       VARCHAR(50) NOT NULL,
  anio         INT,
  color        VARCHAR(30),
  tipo         VARCHAR(30)
);

CREATE INDEX idx_vehiculo_conductor ON vehiculo(conductor_id);
```

> **Nota:** `usuario` y `conductor` quedan como entidades separadas (no se unifican en una supertipo PERSONA). Justificación: simplicidad de implementación para el TP.

### 4.2 MongoDB — datos operativos

```javascript
// Colección: viajes
{
  _id: ObjectId,
  usuario_id: "uuid-postgres",
  conductor_id: "uuid-postgres",
  vehiculo_id: "uuid-postgres",
  origen:   { lat: -34.61, lon: -58.38, direccion: "Palermo" },
  destino:  { lat: -34.55, lon: -58.45, direccion: "Belgrano" },
  distancia_km: 8.2,
  duracion_min: 22,
  estado: "FINALIZADO",  // PENDIENTE | EN_CURSO | FINALIZADO | CANCELADO
  ts_solicitud: ISODate("..."),
  ts_inicio:    ISODate("..."),
  ts_fin:       ISODate("..."),
  // snapshots tomados al momento de crear el viaje (consultados desde Postgres)
  usuario_snapshot:   { nombre: "Juan Pérez",   rating: 4.7 },
  conductor_snapshot: { nombre: "Ana Gómez",    rating: 4.9 }
}

// Colección: pagos
{
  _id: ObjectId,
  viaje_id: ObjectId,           // referencia a viajes._id
  monto_total: 2500.50,
  tarifa_base: 500,
  tarifa_distancia: 1200,
  tarifa_tiempo: 600,
  cargos_extra: 200.50,
  metodo_pago: "TARJETA",       // TARJETA | EFECTIVO | BILLETERA_VIRTUAL
  estado: "APROBADO",           // PENDIENTE | APROBADO | RECHAZADO | REEMBOLSADO
  timestamp: ISODate("...")
}

// Colección: resenas
{
  _id: ObjectId,
  viaje_id: ObjectId,
  tipo: "U_A_C",                // U_A_C = Usuario a Conductor | C_A_U = Conductor a Usuario
  autor:        { id: "uuid", nombre: "Juan Pérez" },
  destinatario: { id: "uuid", nombre: "Ana Gómez"  },
  rating: 5,
  comentario: "Excelente viaje, muy amable",
  timestamp: ISODate("..."),
  contexto_viaje: {
    origen: "Palermo",
    destino: "Belgrano",
    duracion_min: 22
  }
}
// Equivalencia con el DER conceptual (ver justificacion-der.md §E1):
//   tipo = 'U_A_C':  autor.id ≡ usuario_id,    destinatario.id ≡ conductor_id
//   tipo = 'C_A_U':  autor.id ≡ conductor_id,  destinatario.id ≡ usuario_id
// El nombre está denormalizado dentro de autor/destinatario para evitar
// joins con Postgres en consultas frecuentes (casos de uso 1 y 7).

// Colección: login_history (auditoría)
{
  _id: ObjectId,
  usuario_id: "uuid",           // o conductor_id
  tipo_cuenta: "USUARIO",
  evento: "LOGIN_OK",           // LOGIN_OK | LOGIN_FAIL | LOGOUT
  ip: "190.x.x.x",
  timestamp: ISODate("...")
}
```

### 4.3 Cassandra — time-series y agregados

```cql
-- Stream de ubicaciones GPS (alta frecuencia de escritura)
CREATE TABLE ubicaciones_por_vehiculo (
  vehiculo_id UUID,
  ts          TIMESTAMP,
  lat         DECIMAL,
  lon         DECIMAL,
  precision_m FLOAT,
  viaje_id    UUID,
  PRIMARY KEY (vehiculo_id, ts)
) WITH CLUSTERING ORDER BY (ts DESC);

-- Última actividad de cada conductor (para caso de uso 3)
CREATE TABLE ultima_actividad_conductor (
  conductor_id    UUID PRIMARY KEY,
  ultimo_viaje_ts TIMESTAMP,
  ultimo_viaje_id UUID
);

-- Viajes finalizados por día (para caso de uso 4 — agregado)
CREATE TABLE viajes_finalizados_por_dia (
  dia          DATE,
  viaje_id     UUID,
  conductor_id UUID,
  usuario_id   UUID,
  duracion_min INT,
  distancia_km FLOAT,
  PRIMARY KEY (dia, viaje_id)
);
```

### 4.4 Neo4j — grafo de coincidencias

```cypher
// Nodos
(:Usuario   { id, nombre, email })
(:Conductor { id, nombre, email, rating })
(:Vehiculo  { id, placa, marca, modelo, anio, color, tipo })

// Relaciones
(:Conductor)-[:MANEJA]->(:Vehiculo)
(:Usuario)-[:VIAJÓ_CON {
    cantidad_viajes: 3,
    ultimo_viaje_ts: datetime("...")
}]->(:Conductor)
```

**Constraints e índices:**

```cypher
CREATE CONSTRAINT usuario_id   IF NOT EXISTS FOR (u:Usuario)   REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT conductor_id IF NOT EXISTS FOR (c:Conductor) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT vehiculo_id  IF NOT EXISTS FOR (v:Vehiculo)  REQUIRE v.id IS UNIQUE;
CREATE INDEX vehiculo_marca    IF NOT EXISTS FOR (v:Vehiculo)  ON (v.marca);
```

### 4.5 Redis — estado efímero

| Patrón de clave | Tipo Redis | TTL | Uso |
|---|---|---|---|
| `session:{token}` | STRING (JSON) | 10 min (configurable) | Sesión de login validada |
| `vehiculo:{id}:pos` | STRING (`"lat,lon"`) | 30 s | Última posición conocida |
| `cache:top3_resenadores` | STRING (JSON) | 5 min | Cache del caso de uso 1 |
| `cache:viajes_promedio` | STRING (JSON) | 5 min | Cache del caso de uso 4 |

---

## 5. Mapeo de casos de uso → base

| # | Caso de uso | Base que resuelve | Estrategia |
|---|---|---|---|
| 1 | Top 3 usuarios con más reseñas | **Mongo** + **Redis** (cache) | `aggregate([{$match:{tipo:'U_A_C'}}, {$group:{_id:"$autor.id", n:{$sum:1}}}, {$sort:{n:-1}}, {$limit:3}])` |
| 2 | Método de pago menos usado | **Mongo** | `aggregate([{$group:{_id:"$metodo_pago", c:{$sum:1}}}, {$sort:{c:1}}, {$limit:1}])` |
| 3 | Conductores inactivos último mes | **Cassandra** | `SELECT conductor_id FROM ultima_actividad_conductor WHERE ultimo_viaje_ts < ?` (con filtro app-side) |
| 4 | Tiempo promedio viajes | **Cassandra** + **Redis** (cache) | `SELECT AVG(duracion_min) FROM viajes_finalizados_por_dia` (o agregado app-side) |
| 5 | Pasajero-conductor con >1 viaje | **Neo4j** | `MATCH (u:Usuario)-[r:VIAJÓ_CON]->(c:Conductor) WHERE r.cantidad_viajes > 1 RETURN u, c, r.cantidad_viajes` |
| 6 | Autos patente "D" + Toyota | **Neo4j** | `MATCH (v:Vehiculo) WHERE v.marca='Toyota' AND v.placa ENDS WITH 'D' RETURN count(v)` |
| 7 | Reseñas con rating 5 o <2 | **Mongo** | `find({$or:[{rating:5},{rating:{$lt:2}}]})` |

**Distribución final:**

```
Mongo    ████████████  3 casos (1, 2, 7)
Cassandra████████      2 casos (3, 4)
Neo4j    ████████      2 casos (5, 6)
Postgres ░░░░░░░░░░░░  0 casos directos — rol: catálogo de identidad
Redis    ░░░░░░░░░░░░  0 casos directos — rol: sesiones + cache transversal
```

Todas las bases tienen rol concreto: las que aparecen con 0 casos directos cumplen funciones transversales sin las cuales el sistema no funciona.

---

## 6. Flujo de datos y consistencia

### 6.1 Matriz de eventos → bases tocadas

| Evento | Postgres | Mongo | Cassandra | Neo4j | Redis |
|---|---|---|---|---|---|
| Registro de usuario | ✏️ INSERT | — | — | ✏️ CREATE `(:Usuario)` | — |
| Registro de conductor | ✏️ INSERT | — | — | ✏️ CREATE `(:Conductor)` | — |
| Registro de vehículo | ✏️ INSERT | — | — | ✏️ CREATE `(:Vehiculo)` + `[:MANEJA]` | — |
| Login | 🔍 SELECT pw | ✏️ INSERT login_history | — | — | ✏️ SETEX session |
| Reporte GPS | — | — | ✏️ INSERT | — | ✏️ SET pos |
| Solicitud de viaje | 🔍 SELECT u + c | ✏️ INSERT viaje + snapshots | — | — | 🔍 GET sesión |
| Inicio de viaje | — | ✏️ UPDATE estado | — | — | — |
| Fin de viaje | — | ✏️ UPDATE estado | ✏️ UPSERT actividad + INSERT viajes_finalizados | ✏️ MERGE arista += 1 | 🗑️ DEL cache |
| Pago | — | ✏️ INSERT pago | — | — | — |
| Reseña | ✏️ UPDATE rating | ✏️ INSERT reseña | — | ✏️ SET rating en nodo | 🗑️ DEL cache top3 |
| Logout | — | — | — | — | 🗑️ DEL session |

### 6.2 Source of truth por dato

| Dato | SOT | Cómo se replica/proyecta |
|---|---|---|
| Identidad de usuarios/conductores/vehículos | **Postgres** | Snapshots en Mongo al crear viaje; nodos en Neo4j al registrarse |
| Viajes | **Mongo** | Proyección a Cassandra y Neo4j al finalizar |
| Pagos | **Mongo** | — |
| Reseñas | **Mongo** | Disparan UPDATE de rating en Postgres |
| Ubicaciones GPS | **Cassandra** | Última posición en Redis |
| Coincidencias usuario-conductor | **Neo4j** (derivado de Mongo viajes) | Se reconstruye desde Mongo |
| Sesiones | **Redis** (efímero, sin SOT) | — |

### 6.3 Patrón de escritura: write-through best-effort

```python
def finalizar_viaje(viaje_id, distancia_km, duracion_min):
    # 1. SOT primero (CRÍTICO — si falla, abortamos)
    res = mongo.viajes.update_one(
        {"_id": viaje_id},
        {"$set": {"estado": "FINALIZADO", "distancia_km": distancia_km,
                  "duracion_min": duracion_min, "ts_fin": now()}}
    )
    if not res.modified_count:
        raise ViajeNoEncontrado(viaje_id)

    v = mongo.viajes.find_one({"_id": viaje_id})

    # 2. Proyecciones a bases derivadas (BEST-EFFORT — loguear si fallan)
    proyecciones = [
        ("cassandra_actividad",
         lambda: cassandra.upsert_actividad(v["conductor_id"], v["ts_fin"], viaje_id)),
        ("cassandra_finalizados",
         lambda: cassandra.insert_viaje_finalizado(viaje_id, v)),
        ("neo4j_arista",
         lambda: neo4j.incrementar_viajo_con(v["usuario_id"], v["conductor_id"])),
    ]
    for nombre, op in proyecciones:
        try:
            op()
        except Exception as e:
            logger.error(f"Proyección {nombre} falló para viaje {viaje_id}: {e}")
            outbox.enqueue(nombre, viaje_id)
```

### 6.4 Reconciliación

Job que corre cada N minutos (o manualmente desde el menú) para garantizar eventual consistency:

```python
def reconciliar_neo4j_desde_mongo():
    pares = mongo.viajes.aggregate([
        {"$match": {"estado": "FINALIZADO"}},
        {"$group": {"_id": {"u": "$usuario_id", "c": "$conductor_id"},
                    "n": {"$sum": 1}}}
    ])
    for par in pares:
        neo4j.run("""
          MERGE (u:Usuario   {id: $u})
          MERGE (c:Conductor {id: $c})
          MERGE (u)-[r:VIAJÓ_CON]->(c)
          SET r.cantidad_viajes = $n
        """, **par["_id"], n=par["n"])
```

### 6.5 Garantías al profesor

1. ✅ **Interacción entre bases**: cada evento toca 2-5 bases (matriz arriba).
2. ✅ **Consistencia eventual**: reconciliación periódica corrige drift.
3. ✅ **Resiliencia**: una base caída no rompe la app; degrada elegantemente.
4. ✅ **Source of truth claro**: nunca hay ambigüedad de qué base "manda".
5. ✅ **Trazabilidad**: outbox registra cada proyección fallida.

---

## 7. Estructura del proyecto Python

### 7.1 Árbol de carpetas

```
TPUber/
├── CLAUDE.md
├── docs/                          (documentación)
├── Uber/                          (material original — NO TOCAR)
│
├── src/                           ◄── código de la aplicación
│   ├── __init__.py
│   ├── main.py                    ◄── entry point: bootstrap + arranca el menú
│   ├── config.py                  ◄── carga variables desde .env
│   │
│   ├── db/                        ◄── CONEXIONES (singletons a cada base)
│   │   ├── postgres.py
│   │   ├── mongo.py
│   │   ├── cassandra.py
│   │   ├── neo4j_db.py
│   │   └── redis_db.py
│   │
│   ├── repositories/              ◄── CRUD básico, 1 archivo = 1 entidad en 1 base
│   │   ├── usuario_repo.py             # → Postgres
│   │   ├── conductor_repo.py           # → Postgres
│   │   ├── vehiculo_repo.py            # → Postgres
│   │   ├── viaje_repo.py               # → Mongo
│   │   ├── pago_repo.py                # → Mongo
│   │   ├── resena_repo.py              # → Mongo
│   │   ├── login_history_repo.py       # → Mongo
│   │   ├── ubicacion_repo.py           # → Cassandra
│   │   ├── actividad_repo.py           # → Cassandra (última activ. + agregados)
│   │   ├── grafo_repo.py               # → Neo4j (nodos + aristas)
│   │   └── cache_repo.py               # → Redis (sesiones + cache + posición)
│   │
│   ├── services/                  ◄── LÓGICA DE NEGOCIO (orquesta repositories)
│   │   ├── auth_service.py             # registro, login, logout, validar sesión
│   │   ├── vehiculo_service.py
│   │   ├── viaje_service.py            # solicitar, iniciar, finalizar
│   │   ├── pago_service.py
│   │   ├── resena_service.py
│   │   ├── ubicacion_service.py        # streaming GPS
│   │   └── reconciliacion_service.py   # sincronización entre bases
│   │
│   ├── casos_uso/                 ◄── LOS 7 CASOS DEL ENUNCIADO (lecturas)
│   │   ├── caso_01_top_resenadores.py
│   │   ├── caso_02_metodo_pago.py
│   │   ├── caso_03_conductores_inactivos.py
│   │   ├── caso_04_promedio_viajes.py
│   │   ├── caso_05_coincidencias.py
│   │   ├── caso_06_toyota_patente_d.py
│   │   └── caso_07_resenas_extremas.py
│   │
│   ├── menu/                      ◄── INTERFAZ DE CONSOLA
│   │   ├── main_menu.py
│   │   ├── submenu_cuentas.py          # registrar, login, logout
│   │   ├── submenu_operacion.py        # solicitar viaje, pagar, reseñar
│   │   ├── submenu_consultas.py        # los 7 casos de uso
│   │   └── submenu_admin.py            # limpiar bases, reconciliar, ver salud
│   │
│   └── utils/
│       ├── logger.py
│       ├── outbox.py                   # cola de proyecciones fallidas
│       └── errors.py                   # excepciones del dominio
│
├── scripts/                       ◄── SCRIPTS AUXILIARES (correr a mano)
│   ├── init_postgres.sql               # DDL de Postgres
│   ├── init_mongo.py                   # crear índices
│   ├── init_cassandra.cql              # DDL de Cassandra
│   ├── init_neo4j.cypher               # constraints + índices
│   ├── reset_all_dbs.py                # ⚠️ limpia las 5 bases
│   ├── check_connections.py            # health-check
│   ├── seed_data.py                    # carga datos de prueba
│   └── simulador_gps.py                # genera ubicaciones aleatorias
│
├── tests/                         (opcional, ad-hoc)
├── requirements.txt
├── .env.example                   ◄── plantilla (sí va a git)
├── .env                           ◄── credenciales reales (gitignored)
├── .gitignore
└── README.md
```

### 7.2 Arquitectura en 5 capas

```
   ┌─────────────────────────────────────────┐
   │  menu/         (consola)                │  ← lo que ve el usuario
   └────┬────────────────────────────────────┘
        │ llama a casos_uso o services
        ▼
   ┌─────────────────────────────────────────┐
   │  casos_uso/    (lecturas)               │  ← responde las 7 preguntas
   └────┬────────────────────────────────────┘
        │ usa repositories
        ▼
   ┌─────────────────────────────────────────┐
   │  services/     (escrituras + orquestación)│  ← orquesta multi-DB
   └────┬────────────────────────────────────┘
        │ usa repositories
        ▼
   ┌─────────────────────────────────────────┐
   │  repositories/ (CRUD por entidad/base)  │  ← saben de UNA sola base
   └────┬────────────────────────────────────┘
        │ usa db
        ▼
   ┌─────────────────────────────────────────┐
   │  db/           (conexiones)             │  ← drivers
   └─────────────────────────────────────────┘
```

### 7.3 Reglas de dependencia

| Capa | Puede llamar a... | NO puede llamar a... |
|---|---|---|
| `menu/` | `casos_uso/`, `services/` | `repositories/`, `db/` directo |
| `casos_uso/` | `repositories/` | `db/` directo, `services/` (los casos son solo lecturas) |
| `services/` | `repositories/`, otros `services/` | `db/` directo |
| `repositories/` | `db/` (solo la suya) | otros `repositories/`, `services/` |
| `db/` | nada (es la capa más baja) | — |

**Regla de oro:** cada `*_repo.py` toca **exactamente UNA base de datos**. Si una operación necesita 3 bases, eso se orquesta en un `service`, no en un repository. Preserva testabilidad y deja claras las responsabilidades.

### 7.4 Patrón de service: write-through best-effort

```python
# src/services/viaje_service.py
from src.repositories import viaje_repo, actividad_repo, grafo_repo, cache_repo
from src.utils.outbox import outbox
from src.utils.logger import logger
from src.utils.errors import ViajeNoEncontrado

def finalizar_viaje(viaje_id: str, distancia_km: float, duracion_min: int):
    # 1. SOT primero (crítico — si falla, abortar)
    if not viaje_repo.finalizar(viaje_id, distancia_km, duracion_min):
        raise ViajeNoEncontrado(viaje_id)

    viaje = viaje_repo.get_by_id(viaje_id)

    # 2. Proyecciones best-effort
    _intentar("cassandra_actividad",
              lambda: actividad_repo.upsert_ultima(viaje["conductor_id"],
                                                  viaje["ts_fin"], viaje_id))
    _intentar("cassandra_finalizados",
              lambda: actividad_repo.insertar_viaje_finalizado(viaje))
    _intentar("neo4j_arista",
              lambda: grafo_repo.incrementar_viajo_con(viaje["usuario_id"],
                                                      viaje["conductor_id"]))
    _intentar("redis_cache_invalidate",
              lambda: cache_repo.invalidar("cache:viajes_promedio"))

def _intentar(nombre, op):
    try:
        op()
    except Exception as e:
        logger.error(f"Proyección {nombre} falló: {e}")
        outbox.enqueue(nombre)
```

### 7.5 Patrón de repository

```python
# src/repositories/viaje_repo.py — solo conoce Mongo
from src.db.mongo import get_db
from datetime import datetime

def insertar(doc: dict) -> str:
    return str(get_db().viajes.insert_one(doc).inserted_id)

def finalizar(viaje_id: str, distancia_km: float, duracion_min: int) -> bool:
    res = get_db().viajes.update_one(
        {"_id": viaje_id, "estado": "EN_CURSO"},
        {"$set": {"estado": "FINALIZADO",
                  "distancia_km": distancia_km,
                  "duracion_min": duracion_min,
                  "ts_fin": datetime.utcnow()}}
    )
    return res.modified_count == 1

def get_by_id(viaje_id: str) -> dict | None:
    return get_db().viajes.find_one({"_id": viaje_id})
```

### 7.6 Patrón de caso de uso (lectura)

```python
# src/casos_uso/caso_05_coincidencias.py
from src.repositories import grafo_repo

def ejecutar(min_viajes: int = 2) -> list[dict]:
    """¿Qué pasajeros y conductores han coincidido en >1 viaje?"""
    return grafo_repo.coincidencias(min_viajes)
```

```python
# src/repositories/grafo_repo.py
def coincidencias(min_viajes: int) -> list[dict]:
    query = """
        MATCH (u:Usuario)-[r:VIAJÓ_CON]->(c:Conductor)
        WHERE r.cantidad_viajes >= $n
        RETURN u.nombre AS pasajero, c.nombre AS conductor,
               r.cantidad_viajes AS viajes
        ORDER BY viajes DESC
    """
    with get_driver().session() as s:
        return [dict(r) for r in s.run(query, n=min_viajes)]
```

### 7.7 División sugerida del trabajo en el grupo

**Equipo de 3 personas:**

| Persona | Responsabilidad principal | Archivos |
|---|---|---|
| **A — Identidad y Operación** | Postgres + Mongo (auth, viaje, pago) | `db/postgres.py`, `db/mongo.py`, `repositories/usuario_repo`, `conductor_repo`, `vehiculo_repo`, `viaje_repo`, `pago_repo`, `services/auth_service`, `vehiculo_service`, `viaje_service`, `pago_service` |
| **B — Eventos y Tiempo Real** | Cassandra + Redis + Reseñas | `db/cassandra.py`, `db/redis_db.py`, `repositories/ubicacion_repo`, `actividad_repo`, `resena_repo`, `cache_repo`, `login_history_repo`, `services/ubicacion_service`, `resena_service`, `scripts/simulador_gps.py` |
| **C — Grafo y Presentación** | Neo4j + Menú + Casos de uso | `db/neo4j_db.py`, `repositories/grafo_repo`, todo `casos_uso/`, todo `menu/`, `services/reconciliacion_service` |

**Equipo de 2 personas:**

- **A:** Postgres + Mongo + auth/viaje/pago/reseña + 3-4 casos de uso.
- **B:** Cassandra + Neo4j + Redis + menú + 3-4 casos de uso.

Las capas tienen contratos claros, así que trabajan en paralelo sin pisarse.

### 7.8 Convenciones específicas de código

- **Imports absolutos:** `from src.repositories import viaje_repo` (no `from ..repositories`).
- **Naming:** `snake_case` para funciones y módulos; `PascalCase` para clases.
- **Errores de dominio:** definidos en `src/utils/errors.py` (`UsuarioNoEncontrado`, `ViajeNoEncontrado`, `SesionExpirada`, etc.). Capas superiores las capturan, inferiores las lanzan.
- **Logging:** todo via `src.utils.logger` (nivel configurable desde `.env`).
- **Cada operación de service multi-DB sigue el patrón `_intentar(...)`** mostrado en 7.4.

---

> 📑 El plan de defensa del TP está en un documento separado: [`docs/presentacion.md`](presentacion.md).
