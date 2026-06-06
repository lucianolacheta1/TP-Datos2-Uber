# TP Uber — Datos 2 (UADE)

Sistema de gestión de datos para una plataforma de transporte compartido tipo Uber.
Trabajo Práctico de la materia **Datos 2** (UADE, cátedra Mosquera Prada).

El sistema integra **5 bases de datos** (1 relacional + 4 NoSQL) demostrando cómo
distintos paradigmas coexisten y, sobre todo, **interactúan entre sí**: cada acción
del usuario escribe en varias bases a la vez y se mantiene consistencia entre ellas.

## Stack

| Tipo | Tecnología | Hosting | Rol en el sistema |
|---|---|---|---|
| Relacional | PostgreSQL | Neon | Catálogo de identidad: usuario, conductor, vehículo |
| Documental | MongoDB | Atlas | Datos operativos: viajes, pagos, reseñas, auditoría |
| Columnar / time-series | Cassandra | DataStax Astra | Ubicaciones GPS + agregados por día |
| Grafo | Neo4j | Aura | Coincidencias pasajero-conductor + vehículos como nodos |
| Cache / sesiones | Redis | Redis Cloud | Sesiones con TTL, última posición, cache de consultas |

Lenguaje: **Python 3.11+**. Interfaz: consola con menú numérico. Todo corre en la nube.

## Arquitectura

Cinco capas con dependencias unidireccionales:

```
menu/                     interfaz de consola
   v
casos_uso/  +  services/  lecturas (7 casos) / escrituras multi-base
   v
repositories/             CRUD, cada repo toca UNA sola base
   v
db/                       conexiones (drivers, singletons)
```

**Regla de oro:** cada `*_repo.py` conoce una sola base. Si una operación necesita
varias bases, se orquesta en un *service*, nunca en un repository.

### Patrón de identidad

PostgreSQL mantiene solo el **catálogo de identidad** (entidades estables que
requieren integridad referencial). Todo lo operativo, de alto volumen o relacional
vive en las NoSQL. Cada base hace lo que mejor sabe.

### Consistencia entre bases

Patrón **write-through best-effort + outbox + reconciliación**:

1. Se escribe primero en la *source of truth* del dato (crítico; si falla, se aborta).
2. Se proyecta a las bases derivadas en *best-effort*; si una falla, no rompe la app:
   se registra en un *outbox*.
3. Un proceso de **reconciliación** (manual desde el menú o periódico) reconstruye
   las bases derivadas desde la *source of truth*, garantizando consistencia eventual.

Ejemplo: **finalizar un viaje** actualiza MongoDB (estado), Cassandra (actividad +
agregados), Neo4j (arista de coincidencia) y Redis (invalida cache) — una sola acción
del usuario tocando cuatro bases.

## Los 7 casos de uso

| # | Consulta | Base(s) |
|---|---|---|
| 1 | Top 3 usuarios con más reseñas | MongoDB (aggregate) + Redis (cache) |
| 2 | Método de pago menos usado | MongoDB (aggregate) |
| 3 | Conductores inactivos en el último mes | Cassandra + PostgreSQL (join app-side) |
| 4 | Tiempo promedio de viajes | Cassandra + Redis (cache) |
| 5 | Pasajero-conductor con más de un viaje en común | Neo4j |
| 6 | Vehículos Toyota con patente terminada en "D" | Neo4j |
| 7 | Reseñas con rating 5 o menor a 2 | MongoDB (find) |

## Estructura del proyecto

```
src/
  main.py            entry point: bootstrap + arranca el menú
  config.py          carga de variables de entorno
  db/                conexiones a las 5 bases
  repositories/      CRUD por entidad (cada uno toca una sola base)
  services/          lógica de negocio y orquestación multi-base
  casos_uso/         los 7 casos del enunciado (lecturas)
  menu/              interfaz de consola
  utils/             errores de dominio, logger, outbox
scripts/
  check_connections.py   health-check de las 5 bases
  init_mongo.py          crea índices en Mongo
  seed_data.py           carga datos de prueba
  reset_all_dbs.py       limpia las 5 bases
  simulador_gps.py       genera ubicaciones GPS
  demo_automatico.py     corre el flujo completo + los 7 casos sin interacción
tests/                  suite de pruebas (contra las bases cloud reales)
```

## Cómo correr el proyecto

### Requisitos

- Python 3.11+ y Git.
- Archivo `.env` con las credenciales de las 5 bases (ver `.env.example`).
- Bundle de conexión segura de Cassandra/Astra (`.zip`); apuntar a él con
  `ASTRA_BUNDLE_PATH` en el `.env`.

### Setup

```bash
git clone https://github.com/lucianolacheta1/TP-Datos2-Uber.git
cd TP-Datos2-Uber

python -m venv venv
# PowerShell:   .\venv\Scripts\Activate.ps1
# Git Bash:     source venv/Scripts/activate
# Mac/Linux:    source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env   # luego completar las credenciales reales
```

### Verificar que las 5 bases responden

```bash
python -m scripts.check_connections
```

Esperado: `5/5 [OK]` y exit code 0.

### Correr la app

```bash
python -m src.main
```

### Demo automático (sin interacción)

Corre el flujo completo (registro, viaje, GPS, pago, reseña) y luego los 7 casos:

```bash
python -m scripts.demo_automatico
```

### Cargar datos de prueba

```bash
python -m scripts.reset_all_dbs    # limpia las 5 bases
python -m scripts.init_mongo       # recrea índices en Mongo
python -m scripts.seed_data        # carga el dataset de prueba
```

> Nota: correr la suite de tests trunca las tablas de Cassandra. Si necesitás los
> datos del seed, ejecutá el seed **después** de los tests, no antes.

### Tests

```bash
pytest -q
```

## Equipo

Trabajo grupal. La arquitectura en capas con contratos claros permite que cada
integrante tome una base y sus servicios asociados, trabajando en paralelo.
