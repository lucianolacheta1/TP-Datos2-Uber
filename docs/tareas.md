# Tareas del proyecto — TP Uber

> Roadmap completo del proyecto. Marcar `[x]` cuando se complete, `[~]` cuando esté en curso, `[ ]` cuando esté pendiente.
> Última actualización: 2026-05-26

**Leyenda:**
- `[x]` ✅ completado
- `[~]` 🔄 en curso
- `[ ]` ⬜ pendiente
- `[?]` ❓ a decidir / dependiente de algo

---

## 📍 Estado actual (TL;DR para nuevos integrantes)

**Lo que ya está hecho (Fases 0 + 1 + 2):**
- ✅ Diseño completo, 5 documentos en `docs/`, 12 ADRs.
- ✅ Las **5 bases cloud están creadas y conectándose OK** desde Python (`scripts/check_connections.py` devuelve 5/5).
- ✅ Esqueleto Python: `src/config.py`, `src/utils/`, los 5 módulos `src/db/`, `scripts/check_connections.py`.
- ✅ **Invitaciones mandadas a los 4 compañeros** en las 5 plataformas (Neon, Atlas, Astra, Aura, Redis Cloud).
- ✅ Repo GitHub con toda la documentación y código pusheado.

**En qué estamos ahora:**
- 🔄 Esperando que los compañeros acepten invitaciones y armen su entorno local siguiendo `docs/onboarding-equipo.md`.
- ⬜ Próximo paso técnico: **Fase 3 — crear los esquemas (DDL)** en cada base.

**Quién hace qué:**
- Si sos nuevo en el proyecto → arrancá por `docs/onboarding-equipo.md`.
- Cuando tu `check_connections.py` devuelva 5/5, ya estás listo para programar.

---

## Fase 0 — Diseño y planificación

### 0.1 Análisis del enunciado
- [x] Leer `Uber/Uber.docx` (requerimientos y casos de uso)
- [x] Analizar `Uber/Uber.pdf` (DER original)
- [x] Procesar transcripción del video del profesor

### 0.2 Decisiones de stack
- [x] Elegir lenguaje de programación → **Python**
- [x] Elegir tipo de hosting → **Cloud (todo)**
- [x] Elegir interfaz → **Consola con menú**
- [x] Definir bases NoSQL → **MongoDB + Cassandra + Neo4j + Redis**

### 0.3 Diseño del sistema
- [x] Definir patrón arquitectónico (Postgres = catálogo de identidad, NoSQL = operacional)
- [x] Diseñar modelo de datos en cada base
- [x] Mapear los 7 casos de uso a cada base
- [x] Diseñar flujo de datos y consistencia (write-through best-effort + reconciliación)

### 0.4 Documentación inicial
- [x] Crear `docs/diseno.md` (diseño técnico)
- [x] Crear `docs/justificacion-der.md` (para el profesor)
- [x] Crear `docs/decisiones.md` (ADRs)
- [x] Crear `CLAUDE.md` (memoria del proyecto)
- [x] Crear `docs/tareas.md` (este archivo)
- [x] Documentar Sección 4: estructura del proyecto Python (en `docs/diseno.md` §7)
- [x] Documentar Sección 5: plan de presentación (en `docs/presentacion.md`)
- [x] Self-review de los documentos
- [x] Revisión final del usuario antes de pasar a implementación

---

## Fase 1 — Setup de infraestructura cloud ✅ COMPLETADA

> Las credenciales de cada base están en `.env` (no commiteado).
> Para nuevos integrantes: **NO crear cuentas nuevas** — pedirle el `.env` y el bundle de Cassandra a Luciano por canal privado. Ver `docs/onboarding-equipo.md`.

### 1.1 PostgreSQL en Neon — ✅
- [x] Cuenta y proyecto creados en https://neon.tech
- [x] Región: `sa-east-1` (São Paulo)
- [x] Connection string guardado en `.env` como `POSTGRES_URL`
- [x] Conexión probada desde Python con `psycopg` → OK
- [x] **Invitaciones mandadas a los 4 compañeros** (rol Admin) desde Organization → People → Invite member

### 1.2 MongoDB en Atlas — ✅
- [x] Cuenta + organización + proyecto creados en https://www.mongodb.com/cloud/atlas
- [x] Cluster **M0 Free** `UADE-ID2-UBER` activo
- [x] Usuario `llacheta` con password creado
- [x] Network Access con `0.0.0.0/0` para desarrollo
- [x] Connection string guardado en `.env` como `MONGO_URL`
- [x] Conexión probada desde Python con `pymongo` → OK
- [x] **Invitaciones mandadas a los 4 compañeros** (rol Project Owner) desde Access Manager → Project Access

### 1.3 Cassandra en DataStax Astra — ✅
- [x] Cuenta creada en https://astra.datastax.com
- [x] Database serverless `UADE_ID2_UBER` activa
- [x] Keyspace `uber_tp` creado
- [x] Application Token generado con rol `Organization Administrator + Database Administrator`
- [x] Credenciales guardadas en `.env` (`ASTRA_CLIENT_ID`, `ASTRA_CLIENT_SECRET`, `ASTRA_TOKEN`)
- [x] Secure Connect Bundle descargado y guardado fuera del repo
- [x] Path al bundle guardado en `.env` como `ASTRA_BUNDLE_PATH`
- [x] Conexión probada desde Python con `cassandra-driver` → OK
- [x] **Invitaciones mandadas a los 4 compañeros** (Org + DB Admin) desde Organization Settings → User Management

### 1.4 Neo4j en Aura — ✅
- [x] Cuenta creada en https://console.neo4j.io
- [x] Instancia **AuraDB** creada (instance ID: `1b29ebc4`)
- [x] Password copiado y guardado en `.env` como `NEO4J_PASSWORD`
- [x] URI guardado en `.env` como `NEO4J_URI=neo4j+s://1b29ebc4.databases.neo4j.io`
- [x] **⚠️ Importante:** el `NEO4J_USER` es el **instance ID** (`1b29ebc4`), NO la string `neo4j` como era antes. Aura cambió su esquema reciente.
- [x] Conexión probada desde Python con driver `neo4j` → OK
- [x] **Invitaciones mandadas a los 4 compañeros** (3 quedaron como Viewer, alcanza para visualizar; el acceso de escritura va por el `.env`)

### 1.5 Redis en Redis Cloud — ✅
- [x] Cuenta creada en https://app.redislabs.com
- [x] Database free tier `UADE-ID2-UBER` activa
- [x] Host, port, password guardados en `.env` (`REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`)
- [x] Conexión probada desde Python con `redis-py` → OK
- [x] **Invitaciones mandadas a los 4 compañeros** (rol Owner) → 5/5 aceptaron desde Access Management → Team

### 1.6 Verificación end-to-end — ✅
- [x] `scripts/check_connections.py` implementado
- [x] Las 5 bases responden OK desde Python en la máquina principal (Luciano)
- [ ] Que los 4 compañeros corran el check en su máquina y confirmen 5/5 OK (esperando)

---

## Fase 2 — Setup del proyecto Python

### 2.1 Repositorio Git
- [x] `git init -b main` en la raíz del proyecto local
- [x] Crear `.gitignore` (excluye `Uber/`, `*.vtt`, `.env`, `*.zip`, `venv/`, `__pycache__/`, etc.)
- [x] Crear `README.md` (portada del repo apuntando a `CLAUDE.md` y `docs/`)
- [x] Conectar al remoto: `git remote add origin https://github.com/lucianolacheta1/TP-Datos2-Uber.git`
- [x] Primer commit con la documentación (8 archivos, 1742 líneas)
- [x] Push inicial: `git push --force -u origin main` (force-push sobrescribió el commit inicial trivial de GitHub)
- [ ] Invitar a los compañeros del grupo como colaboradores del repo (Settings → Collaborators en GitHub)

### 2.2 Estructura del proyecto — ✅
- [x] Carpetas creadas: `src/`, `src/db/`, `src/utils/`, `scripts/`, `tests/` (todas con `__init__.py`)
- [x] `requirements.txt` creado con: `psycopg[binary]`, `pymongo`, `cassandra-driver`, `pyasyncore` (necesario para Python 3.12+), `neo4j`, `redis`, `python-dotenv`, `bcrypt`, `pytest`
- [x] `.env.example` creado como plantilla del `.env` real (que está gitignored)

### 2.3 Entorno virtual y dependencias — ✅
- [x] `python -m venv venv` creado
- [x] Activar venv: `.\venv\Scripts\Activate.ps1` (PS) o `source venv/Scripts/activate` (Git Bash)
- [x] `pip install -r requirements.txt` ejecutado, todas las dependencias instaladas
- [x] `pip list` muestra los 9 paquetes esperados

### 2.4 Capa de configuración — ✅
- [x] `src/config.py` implementado con `python-dotenv` y dataclass `Settings`
- [x] Función `validate()` que verifica que las variables críticas estén presentes
- [x] `src/utils/logger.py` y `src/utils/errors.py` también implementados

### 2.5 Conexiones a las bases — ✅
- [x] `src/db/postgres.py` con `get_conn()` singleton + `check()` → OK
- [x] `src/db/mongo.py` con `get_client()` + `get_db()` + `check()` → OK
- [x] `src/db/cassandra.py` con `get_session()` + `check()` → OK
- [x] `src/db/neo4j_db.py` con `get_driver()` + `check()` → OK
- [x] `src/db/redis_db.py` con `get_client()` + `check()` → OK
- [x] `scripts/check_connections.py` corre las 5 verificaciones, devuelve 5/5 OK

---

## Fase 3 — Creación de esquemas (DDL)

### 3.1 PostgreSQL — `init_postgres.sql` — ✅
- [x] Crear extensión `pgcrypto` para `gen_random_uuid()`
- [x] Crear tabla `usuario` con CHECK en `estado`
- [x] Crear tabla `conductor` con CHECK en `estado`
- [x] Crear tabla `vehiculo` con FK a `conductor`
- [x] Crear índices (`idx_vehiculo_conductor`, etc.)
- [x] Ejecutar el script — aplicado y verificado en Neon (3 tablas)

### 3.2 MongoDB — `init_mongo.py` — ✅ (aplicado en Atlas, 4 colecciones con índices)
- [x] Crear índices en `viajes` (`usuario_id`, `conductor_id`, `estado`, `ts_inicio`)
- [x] Crear índices en `pagos` (`viaje_id`, `metodo_pago`)
- [x] Crear índices en `resenas` (`autor.id`, `destinatario.id`, `tipo`, `rating`)
- [ ] Validar esquemas con JSON Schema validators (opcional)

### 3.3 Cassandra — `init_cassandra.cql` — ✅ (aplicado en Astra, keyspace `uber_tp`)
- [x] Crear tabla `ubicaciones_por_vehiculo` con PK compuesta `(vehiculo_id, ts)`
- [x] Crear tabla `ultima_actividad_conductor`
- [x] Crear tabla `viajes_finalizados_por_dia`

### 3.4 Neo4j — `init_neo4j.cypher` — ✅
- [x] Crear constraints UNIQUE en `Usuario.id`, `Conductor.id`, `Vehiculo.id`
- [x] Crear índice en `Vehiculo.marca` (+ `Vehiculo.placa`) — ejecutado y verificado en Aura

### 3.5 Redis
- [ ] No hay esquema; documentar en el código las **convenciones de claves** que se van a usar

### 3.6 Script de "limpiar todo" — `reset_dbs.py`
- [ ] DROP/TRUNCATE en Postgres
- [ ] `drop_collection` en Mongo
- [ ] `TRUNCATE` en Cassandra
- [ ] `MATCH (n) DETACH DELETE n` en Neo4j
- [ ] `FLUSHDB` en Redis (cuidado!)

---

## Fase 4 — Implementación de servicios de negocio

> Cada servicio orquesta escrituras a múltiples bases siguiendo el patrón write-through best-effort.

### 4.1 Autenticación
- [ ] `auth_service.register_usuario(email, password, nombre, ...)`
- [ ] `auth_service.register_conductor(email, password, nombre, nro_licencia, ...)`
- [ ] `auth_service.login(email, password, tipo_cuenta)` → escribe `login_history` en Mongo, crea sesión Redis
- [ ] `auth_service.logout(token)` → borra sesión Redis
- [ ] `auth_service.validate_session(token)` → consulta Redis con TTL

### 4.2 Gestión de vehículos — ✅
- [x] `vehiculo_service.registrar(conductor_id, placa, marca, modelo, anio, color, tipo)` → escribe Postgres (SOT) + nodo Vehiculo y relación MANEJA en Neo4j (best-effort) — 3 tests

### 4.3 Gestión de viajes
- [ ] `viaje_service.solicitar(usuario_id, conductor_id, origen, destino)` → escribe Mongo con snapshots desde Postgres
- [ ] `viaje_service.iniciar(viaje_id)` → update en Mongo
- [ ] `viaje_service.finalizar(viaje_id, distancia, duracion)` → update Mongo + actualizar Cassandra + actualizar Neo4j

### 4.4 Pagos
- [ ] `pago_service.procesar(viaje_id, monto, metodo_pago)` → escribe Mongo

### 4.5 Reseñas
- [ ] `resena_service.crear(viaje_id, autor, destinatario, rating, comentario)` → escribe Mongo + recalcula rating en Postgres + actualiza nodo Neo4j + invalida cache Redis

### 4.6 Ubicaciones (streaming)
- [x] `ubicacion_service.reportar(vehiculo_id, lat, lon)` → escribe Cassandra + setea Redis con TTL corto — 3 tests
- [ ] Simulador de GPS: thread que cada N segundos genera ubicaciones aleatorias para vehículos activos

### 4.7 Reconciliación
- [x] `reconciliacion_service.sync_neo4j_desde_mongo()` (rebuild aristas) — hecho con TDD (3 tests + `outbox`)
- [ ] `reconciliacion.sync_cassandra_actividad()` (rebuild ultima_actividad_conductor)
- [ ] Endpoint del menú para correr la reconciliación manualmente

---

## Fase 5 — Implementación de los 7 casos de uso

- [ ] **Caso 1:** Top 3 reseñadores → Mongo aggregate + cache Redis
- [ ] **Caso 2:** Método de pago menos usado → Mongo aggregate
- [x] **Caso 3:** Conductores inactivos último mes → Cassandra query + JOIN app-side con Postgres — `caso_03` (2 tests)
- [x] **Caso 4:** Tiempo promedio viajes → Cassandra agregado + cache Redis — `caso_04` + `cache_repo` (4 tests)
- [x] **Caso 5:** Pasajero-conductor con >1 viaje → Neo4j cypher — `grafo_repo` + `caso_05` (3 tests)
- [x] **Caso 6:** Autos Toyota patente "D" → Neo4j cypher — `grafo_repo` + `caso_06` (3 tests)
- [ ] **Caso 7:** Reseñas rating 5 o <2 → Mongo find

---

## Fase 6 — Menú de consola

- [ ] Estructura general del menú principal
- [ ] Submenú: **Gestión de cuentas** (registrar, login, logout)
- [ ] Submenú: **Gestión de vehículos** (registrar)
- [ ] Submenú: **Operación** (solicitar viaje, iniciar, finalizar, pagar, reseñar)
- [ ] Submenú: **Consultas — los 7 casos de uso**
- [ ] Submenú: **Administración** (limpiar bases, reconciliar, ver salud de conexiones)
- [ ] Loop principal con manejo de errores

---

## Fase 7 — Datos de prueba y testing

### 7.1 Seeding
- [ ] Script `seed.py` que cree datos realistas: ~20 usuarios, ~10 conductores, ~15 vehículos, ~50 viajes finalizados, pagos, reseñas
- [ ] Asegurar que la distribución de datos permita demostrar los 7 casos de uso

### 7.2 Verificación
- [ ] Ejecutar manualmente los 7 casos de uso y validar resultados
- [ ] Verificar que los conteos coinciden entre bases (consistencia)
- [ ] Validar que ningún viaje queda huérfano (sin usuario/conductor existente)

### 7.3 Edge cases
- [ ] Reseña sobre un viaje no finalizado → debe rechazar
- [ ] Login con password incorrecto → debe escribir `LOGIN_FAIL` en Mongo
- [ ] Sesión expirada → debe forzar relogin

---

## Fase 8 — Preparación de la presentación

> El plan completo está en [`docs/presentacion.md`](presentacion.md). Acá solo las tareas para trackear.

- [ ] Preparar las 8 slides (ver estructura en `presentacion.md` §5)
- [ ] Ensayar el guion del demo en vivo al menos 2 veces (ver `presentacion.md` §2)
- [ ] Correr `seed_data.py` y verificar que los 7 casos devuelven resultados no-vacíos
- [ ] Imprimir / tener a mano `docs/justificacion-der.md` (lo que el profesor pidió)
- [ ] Grabar video de respaldo del demo (mitigación de riesgo si cae internet)
- [ ] Implementar `scripts/demo_automatico.py` (backup si el demo en vivo se traba)
- [ ] Exportar slides a PDF
- [ ] Asegurar que las 5 bases cloud tienen datos antes del día de la presentación
- [ ] Verificar checklist del día anterior (ver `presentacion.md` §7)

---

## Notas de seguimiento

> Acá podemos ir anotando bloqueos, dudas pendientes, items a discutir en próximas reuniones.

- **2026-05-19:** Documentación inicial completada — 6 documentos: `CLAUDE.md`, `docs/diseno.md`, `docs/justificacion-der.md`, `docs/decisiones.md` (12 ADRs), `docs/presentacion.md`, `docs/tareas.md`. Próximo paso: arrancar **Fase 1** (creación de cuentas en las 5 plataformas cloud).
- **2026-05-26:** Fases 1 y 2 completadas:
  - Las 5 cuentas cloud creadas (Neon, Atlas, Astra, Aura, Redis Cloud) con credenciales en `.env`.
  - Esqueleto Python listo: `src/config.py`, `src/utils/{logger,errors}.py`, los 5 módulos `src/db/`, y `scripts/check_connections.py`.
  - `python -m scripts.check_connections` devuelve 5/5 OK desde la máquina principal.
  - **20 invitaciones mandadas** (4 compañeros × 5 plataformas) — esperando aceptación.
  - `docs/onboarding-equipo.md` creado para guiar el setup de los nuevos integrantes.
  - **Quirks documentados:** `pyasyncore` necesario para Python 3.12+; Neo4j Aura ahora usa el instance ID como username (no `neo4j`).
  - Próximo paso: **Fase 3 — crear los esquemas (DDL)** en cada base.
- [ ] **Confirmar con el profesor** que está OK usar 5 bases en lugar de 4 (1 relacional + 4 NoSQL en vez de 1+3).
- [x] Repositorio remoto: https://github.com/lucianolacheta1/TP-Datos2-Uber (decidido 2026-05-19).
- [ ] **Invitar al equipo como colaboradores del repo en GitHub** (Settings → Collaborators) si queremos que puedan hacer push directo a `main`. Hoy el repo es público, así que pueden clonar sin invitación, pero solo Luciano puede pushear.
