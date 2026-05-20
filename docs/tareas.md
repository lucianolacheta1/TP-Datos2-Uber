# Tareas del proyecto — TP Uber

> Roadmap completo del proyecto. Marcar `[x]` cuando se complete, `[~]` cuando esté en curso, `[ ]` cuando esté pendiente.
> Última actualización: 2026-05-19

**Leyenda:**
- `[x]` ✅ completado
- `[~]` 🔄 en curso
- `[ ]` ⬜ pendiente
- `[?]` ❓ a decidir / dependiente de algo

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

## Fase 1 — Setup de infraestructura cloud

> Las **credenciales** de cada base deben ir a un archivo `.env` que **no se commitee**. Compartir entre el equipo por canal seguro.

### 1.1 PostgreSQL en Neon (`neon.tech`)
- [ ] Crear cuenta en https://neon.tech (con GitHub o email)
- [ ] Crear nuevo proyecto: nombre `tp-uber` (o similar)
- [ ] Elegir región más cercana (probablemente `us-east-2` o `sa-east-1` si está disponible)
- [ ] Anotar el **connection string** (formato `postgresql://user:pass@host/db`)
- [ ] Guardar en `.env` como `POSTGRES_URL=...`
- [ ] Probar conexión con `psql` o desde Python con `psycopg`
- [ ] Habilitar branching si querés tener ramas dev/prod (opcional)

### 1.2 MongoDB en Atlas (`mongodb.com/cloud/atlas`)
- [ ] Crear cuenta en https://www.mongodb.com/cloud/atlas
- [ ] Crear nueva organización + proyecto
- [ ] Crear cluster **M0 (Free)** — elegir provider (AWS recomendado) y región
- [ ] En **Database Access**: crear usuario con password (anotar)
- [ ] En **Network Access**: agregar IP `0.0.0.0/0` (allow from anywhere) — solo para desarrollo
- [ ] Obtener el connection string del botón "Connect" → "Drivers" → Python
- [ ] Guardar en `.env` como `MONGO_URL=mongodb+srv://...`
- [ ] Probar conexión con MongoDB Compass (desktop client) o desde Python con `pymongo`

### 1.3 Cassandra en DataStax Astra (`astra.datastax.com`)
- [ ] Crear cuenta en https://astra.datastax.com (con GitHub o email)
- [ ] Crear nueva **Database** → tipo **Serverless (Vector)** o **Serverless**
- [ ] Asignar nombre `tp-uber` y región
- [ ] Crear **keyspace** llamado `uber_tp` (o el nombre que prefieran)
- [ ] Generar un **Application Token** desde "Settings → Tokens" con rol `Database Administrator`
- [ ] Anotar `Client ID`, `Client Secret` y `Token`
- [ ] Descargar el **Secure Connect Bundle** (.zip) — guardarlo en una carpeta segura
- [ ] Guardar en `.env` las 3 credenciales + el path al bundle
- [ ] Probar conexión con CQL Console (en la UI de Astra) o desde Python con `cassandra-driver`

### 1.4 Neo4j en Aura (`console.neo4j.io`)
- [ ] Crear cuenta en https://console.neo4j.io
- [ ] Crear nueva instancia **AuraDB Free** (1 DB, 200k nodos, gratis para siempre)
- [ ] **⚠️ IMPORTANTE:** copiar el password apenas se genera; **se muestra una sola vez**. Guardarlo de inmediato.
- [ ] Anotar el **URI** (formato `neo4j+s://xxxxxxxx.databases.neo4j.io`)
- [ ] Usuario por defecto: `neo4j`
- [ ] Guardar en `.env` como `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- [ ] Probar conexión con Neo4j Browser (link en la UI) ejecutando `RETURN 1`
- [ ] Probar conexión desde Python con el driver `neo4j`

### 1.5 Redis en Redis Cloud (`redis.com`) o Upstash (`upstash.com`)
- [ ] Elegir proveedor: **Redis Cloud** (30 MB free) o **Upstash** (10 MB free, más simple)
- [ ] Crear cuenta
- [ ] Crear **Database** free tier
- [ ] Anotar `host`, `port`, `password`
- [ ] Guardar en `.env` como `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- [ ] Probar conexión con `redis-cli` o desde Python con `redis`

### 1.6 Verificación end-to-end
- [ ] Crear script `check_connections.py` que abra una conexión a cada base e imprima `OK` o el error.
- [ ] Asegurar que las 5 bases respondan desde la máquina de cada integrante del grupo.

---

## Fase 2 — Setup del proyecto Python

### 2.1 Repositorio Git
- [ ] Hacer `git init` en `C:\Users\lucia\UADE\datos2\TPUber\` (si no está ya)
- [ ] Crear `.gitignore` incluyendo: `.env`, `__pycache__/`, `*.pyc`, `venv/`, `*.zip` (secure connect bundles), `.idea/`, `.vscode/`
- [ ] Conectar al remoto: `git remote add origin https://github.com/lucianolacheta1/TP-Datos2-Uber.git`
- [ ] Primer commit con la documentación: `git add . && git commit -m "agregar documentación inicial del proyecto"`
- [ ] Push inicial: `git push -u origin main`
- [ ] Invitar a los compañeros del grupo como colaboradores del repo (Settings → Collaborators en GitHub)

### 2.2 Estructura del proyecto
- [ ] Definir estructura de carpetas (`src/`, `tests/`, `scripts/`, `config/`, etc.) — ver `docs/diseno.md` §7
- [ ] Crear `requirements.txt` con las dependencias:
  - `psycopg[binary]`
  - `pymongo`
  - `cassandra-driver`
  - `neo4j`
  - `redis`
  - `python-dotenv`
  - `bcrypt`
- [ ] Crear archivo `.env.example` (con las claves vacías, para el equipo)

### 2.3 Entorno virtual y dependencias
- [ ] Crear virtualenv: `python -m venv venv`
- [ ] Activar venv: `source venv/Scripts/activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Verificar que `pip list` muestre todo

### 2.4 Capa de configuración
- [ ] Implementar `src/config.py` que cargue variables desde `.env` con `python-dotenv`
- [ ] Validar al arrancar que todas las variables críticas estén presentes

### 2.5 Conexiones a las bases
- [ ] Implementar `src/db/postgres.py` (singleton de conexión `psycopg`)
- [ ] Implementar `src/db/mongo.py` (cliente `pymongo`)
- [ ] Implementar `src/db/cassandra.py` (cluster `cassandra-driver` con bundle)
- [ ] Implementar `src/db/neo4j_db.py` (driver `neo4j`)
- [ ] Implementar `src/db/redis_db.py` (cliente `redis`)

---

## Fase 3 — Creación de esquemas (DDL)

### 3.1 PostgreSQL — `init_postgres.sql`
- [ ] Crear extensión `pgcrypto` para `gen_random_uuid()`
- [ ] Crear tabla `usuario` con CHECK en `estado`
- [ ] Crear tabla `conductor` con CHECK en `estado`
- [ ] Crear tabla `vehiculo` con FK a `conductor`
- [ ] Crear índices (`idx_vehiculo_conductor`, etc.)
- [ ] Ejecutar el script desde Python o desde la consola SQL de Neon

### 3.2 MongoDB — `init_mongo.py`
- [ ] Crear índices en `viajes` (`usuario_id`, `conductor_id`, `estado`, `ts_inicio`)
- [ ] Crear índices en `pagos` (`viaje_id`, `metodo_pago`)
- [ ] Crear índices en `resenas` (`autor.id`, `destinatario.id`, `tipo`, `rating`)
- [ ] Validar esquemas con JSON Schema validators (opcional)

### 3.3 Cassandra — `init_cassandra.cql`
- [ ] Crear tabla `ubicaciones_por_vehiculo` con PK compuesta `(vehiculo_id, ts)`
- [ ] Crear tabla `ultima_actividad_conductor`
- [ ] Crear tabla `viajes_finalizados_por_dia`

### 3.4 Neo4j — `init_neo4j.cypher`
- [ ] Crear constraints UNIQUE en `Usuario.id`, `Conductor.id`, `Vehiculo.id`
- [ ] Crear índice en `Vehiculo.marca`

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

### 4.2 Gestión de vehículos
- [ ] `vehiculo_service.registrar(conductor_id, placa, marca, modelo, anio, color, tipo)` → escribe Postgres + crea nodo en Neo4j

### 4.3 Gestión de viajes
- [ ] `viaje_service.solicitar(usuario_id, conductor_id, origen, destino)` → escribe Mongo con snapshots desde Postgres
- [ ] `viaje_service.iniciar(viaje_id)` → update en Mongo
- [ ] `viaje_service.finalizar(viaje_id, distancia, duracion)` → update Mongo + actualizar Cassandra + actualizar Neo4j

### 4.4 Pagos
- [ ] `pago_service.procesar(viaje_id, monto, metodo_pago)` → escribe Mongo

### 4.5 Reseñas
- [ ] `resena_service.crear(viaje_id, autor, destinatario, rating, comentario)` → escribe Mongo + recalcula rating en Postgres + actualiza nodo Neo4j + invalida cache Redis

### 4.6 Ubicaciones (streaming)
- [ ] `ubicacion_service.reportar(vehiculo_id, lat, lon)` → escribe Cassandra + setea Redis con TTL corto
- [ ] Simulador de GPS: thread que cada N segundos genera ubicaciones aleatorias para vehículos activos

### 4.7 Reconciliación
- [ ] `reconciliacion.sync_neo4j_desde_mongo()` (rebuild aristas)
- [ ] `reconciliacion.sync_cassandra_actividad()` (rebuild ultima_actividad_conductor)
- [ ] Endpoint del menú para correr la reconciliación manualmente

---

## Fase 5 — Implementación de los 7 casos de uso

- [ ] **Caso 1:** Top 3 reseñadores → Mongo aggregate + cache Redis
- [ ] **Caso 2:** Método de pago menos usado → Mongo aggregate
- [ ] **Caso 3:** Conductores inactivos último mes → Cassandra query + JOIN app-side con Postgres
- [ ] **Caso 4:** Tiempo promedio viajes → Cassandra agregado + cache Redis
- [ ] **Caso 5:** Pasajero-conductor con >1 viaje → Neo4j cypher
- [ ] **Caso 6:** Autos Toyota patente "D" → Neo4j cypher
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
- [ ] **Confirmar con el profesor** que está OK usar 5 bases en lugar de 4 (1 relacional + 4 NoSQL en vez de 1+3).
- [x] Repositorio remoto: https://github.com/lucianolacheta1/TP-Datos2-Uber (decidido 2026-05-19).
