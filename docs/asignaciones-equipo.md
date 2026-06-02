# Asignaciones del equipo — TP Uber

> Quién hace qué, qué leer según tu rol, contratos entre repositories y cómo trabajar con AI tools sin pisarse.
> Audiencia: equipo + asistentes de IA que cada integrante use.
> Última actualización: 2026-05-26

---

## 👥 Tabla de asignaciones

| Integrante | Email | Base de datos | Rol/responsabilidades técnicas |
|---|---|---|---|
| **Luciano Lacheta** | llacheta@uade.edu.ar | 🔴 **Neo4j** | Esquema en Aura + `grafo_repo` + casos de uso 5 y 6 + parte del `vehiculo_service` y `reconciliacion_service` |
| **(a confirmar 1)** | aguarguello@uade.edu.ar | 🟡 **MongoDB** | 4 colecciones + `viaje_repo`, `pago_repo`, `resena_repo`, `login_history_repo` + casos 1, 2, 7 |
| **(a confirmar 2)** | mdelaguardia@uade.edu.ar | 🟡 **Cassandra** | 3 tablas + `ubicacion_repo`, `actividad_repo` + casos 3 y 4 |
| **(a confirmar 3)** | mselles@uade.edu.ar | 🟢 **PostgreSQL + Auth** | 3 tablas + `usuario_repo`, `conductor_repo`, `vehiculo_repo` + `auth_service` |
| **(a confirmar 4)** | jfanarasanchez@uade.edu.ar | 🟢 **Redis + menú + simulador GPS** | `cache_repo` + `outbox` + `main_menu` + 4 submenús + simulador GPS |

> ✏️ **Luciano:** completá los `(a confirmar)` cuando hablés con el equipo. Las asignaciones son sugeridas según complejidad/volumen pero podés intercambiar.

### Tareas transversales (cualquiera + más de uno)

| Tarea | Quién | Cuándo |
|---|---|---|
| Tests de integración multi-DB | El "dueño" de la DB principal + revisión cruzada | Plan 03 |
| `seed_data.py` | Quien tenga más bandwidth al llegar al Plan 05 | Plan 05 |
| Slides + ensayos de presentación | Todo el equipo, dividir 2 slides cada uno | Plan 05 |
| Code review de PRs | Cualquiera del equipo (no el autor) | Continuo |

---

## 📖 Cómo trabajar como dueño de una DB

1. **Lee las secciones que te corresponden** (ver "Lectura curada por rol" abajo).
2. **Trabajá en un branch feature/** específico de tu DB (ver "Workflow Git").
3. **No modifiques archivos de otras DBs** (otras carpetas/módulos). Si necesitás algo de otra DB, abrí un issue o coordiná en el chat del grupo.
4. **Respetá los contratos de los repositories** (ver "Contratos entre repositories"). Si necesitás cambiar la firma de una función pública, **avisá al equipo primero** — esos cambios rompen el código de otros.
5. **Hacé pull request a `main`** cuando termines algo testeado. Otro del equipo revisa y mergea.
6. **Actualizá `docs/tareas.md`** marcando lo que completaste con `[x]`.

---

## 📚 Lectura curada por rol

> Todos deben leer **`CLAUDE.md` + `docs/onboarding-equipo.md`** primero. Después, solo las secciones específicas de su rol.

### Si te tocó 🟢 PostgreSQL + Auth

**Tu archivo más importante:** `docs/diseno.md` §4.1 (esquema Postgres).

| Doc | Secciones a leer |
|---|---|
| `docs/diseno.md` | §1, §2, §3, **§4.1**, §6.1-§6.3, **§7** |
| `docs/decisiones.md` | ADR-005 (patrón Postgres mínimo), ADR-008 (write-through), ADR-011 (5 capas) |
| `docs/plan-01-foundation.md` | §1.1 (cuenta Neon, ya hecho), **§3.1** (DDL Postgres) |
| `docs/plan-02-repositories.md` | Secciones de **`usuario_repo`**, **`conductor_repo`**, **`vehiculo_repo`** |
| `docs/plan-03-services.md` | **§1 `auth_service`** (es el más complejo del proyecto) |
| `docs/plan-05-seeding-presentacion.md` | §1.2 (parte de seed que crea usuarios/conductores/vehículos) |

### Si te tocó 🟡 MongoDB

**Tu archivo más importante:** `docs/diseno.md` §4.2 (colecciones Mongo).

| Doc | Secciones a leer |
|---|---|
| `docs/diseno.md` | §1, §2, §3, **§4.2**, **§5** (casos 1, 2, 7), §6, §7 |
| `docs/decisiones.md` | ADR-006 (modelo de reseña con discriminador), ADR-008 (write-through), ADR-009 (distribución de casos) |
| `docs/plan-01-foundation.md` | §1.2 (cuenta Atlas, ya hecho), **§3.2** (init_mongo.py) |
| `docs/plan-02-repositories.md` | Secciones de **`viaje_repo`**, **`pago_repo`**, **`resena_repo`**, **`login_history_repo`** |
| `docs/plan-03-services.md` | Las partes Mongo de `auth_service`, **`viaje_service`**, `pago_service`, **`resena_service`** |
| `docs/plan-04-use-cases-menu.md` | **Casos 1, 2, 7** (Task 1.2, 1.3, 1.8) |

### Si te tocó 🟡 Cassandra

**Tu archivo más importante:** `docs/diseno.md` §4.3 (tablas Cassandra) y **§6** (flujo de datos).

| Doc | Secciones a leer |
|---|---|
| `docs/diseno.md` | §1, §2, §3, **§4.3**, **§5** (casos 3, 4), **§6**, §7 |
| `docs/decisiones.md` | ADR-005 (por qué Cassandra para time-series), ADR-008 (write-through), ADR-009 |
| `docs/plan-01-foundation.md` | §1.3 (cuenta Astra, ya hecho), **§3.3** (DDL Cassandra) |
| `docs/plan-02-repositories.md` | Secciones de **`ubicacion_repo`**, **`actividad_repo`** |
| `docs/plan-03-services.md` | **`ubicacion_service`** + las partes Cassandra de `viaje_service.finalizar()` |
| `docs/plan-04-use-cases-menu.md` | **Casos 3 y 4** (Task 1.4, 1.5) |

> 💡 **Atención:** Cassandra no soporta joins ni filtros arbitrarios. El **modelado** (clave de partición + clustering) es lo más importante. Si te trabás, leé la guía de DataStax sobre data modeling antes de codear.

### Si te tocó 🔴 Neo4j (Luciano)

**Tu archivo más importante:** `docs/diseno.md` §4.4 (grafo) + §5 casos 5 y 6.

| Doc | Secciones a leer |
|---|---|
| `docs/diseno.md` | §1, §2, §3, **§4.4**, **§5** (casos 5, 6), §6, §7 |
| `docs/decisiones.md` | ADR-004 (Stack — por qué Neo4j), ADR-005, ADR-006, ADR-009 |
| `docs/plan-01-foundation.md` | §1.4 (cuenta Aura, ya hecho), **§3.4** (constraints + índices) |
| `docs/plan-02-repositories.md` | Sección de **`grafo_repo`** completa |
| `docs/plan-03-services.md` | Las partes Neo4j de `auth_service`, `vehiculo_service`, `viaje_service.finalizar()`, `resena_service`, **`reconciliacion_service`** |
| `docs/plan-04-use-cases-menu.md` | **Casos 5 y 6** (Task 1.6, 1.7) — el caso 5 es el "wow moment" del demo |

### Si te tocó 🟢 Redis + Menú + Simulador GPS

**Tu archivo más importante:** `docs/diseno.md` §4.5 + **§7 (toda la arquitectura del menú)**.

| Doc | Secciones a leer |
|---|---|
| `docs/diseno.md` | §1, §2, §3, **§4.5**, §6, **§7** |
| `docs/decisiones.md` | ADR-004, ADR-008 (outbox), ADR-011 (arquitectura 5 capas) |
| `docs/plan-01-foundation.md` | §1.5 (cuenta Redis, ya hecho) |
| `docs/plan-02-repositories.md` | Sección de **`cache_repo`** |
| `docs/plan-03-services.md` | **§0 outbox** + partes Redis de `auth_service`, `ubicacion_service`, `resena_service` |
| `docs/plan-04-use-cases-menu.md` | **§2 formato**, **§3 los 4 submenús**, **§4 main_menu + main.py** |
| `docs/plan-05-seeding-presentacion.md` | **§2 simulador GPS**, **§3 demo automático** |

> 💡 Tu rol es el "pegamento" del proyecto: cache transversal + UI + simulador. Si bien Redis es trivial, el menú y el simulador son críticos para que el demo funcione.

---

## 🔌 Contratos entre repositories

Cada repository expone un set de funciones públicas que los **services** llaman. **Estas firmas no se pueden cambiar sin coordinar con el equipo**, porque los services dependen de ellas.

> 📌 Si necesitás cambiar una firma, abrí un issue en GitHub o avisá por el chat del grupo.

### Postgres (rol PostgreSQL+Auth)

```python
# src/repositories/usuario_repo.py
def crear(email: str, password_hash: str, nombre: str, telefono: str | None = None) -> str  # devuelve id
def get_by_id(id: str) -> dict | None
def get_by_email(email: str) -> dict | None
def existe(id: str) -> bool
def actualizar_rating(id: str, rating: float) -> None

# src/repositories/conductor_repo.py
def crear(email, password_hash, nombre, nro_licencia, telefono=None) -> str
def get_by_id(id) -> dict | None
def get_by_email(email) -> dict | None
def existe(id) -> bool
def listar_activos() -> list[dict]
def actualizar_rating(id, rating) -> None

# src/repositories/vehiculo_repo.py
def crear(conductor_id, placa, marca, modelo, anio=None, color=None, tipo=None) -> str
def get_by_id(id) -> dict | None
def existe(id) -> bool
def listar_todos() -> list[dict]
```

### Mongo (rol MongoDB)

```python
# src/repositories/viaje_repo.py
def crear(doc: dict) -> str
def get_by_id(id: str) -> dict | None
def iniciar(id: str) -> bool       # PENDIENTE -> EN_CURSO
def finalizar(id, distancia_km, duracion_min) -> bool   # EN_CURSO -> FINALIZADO

# src/repositories/pago_repo.py
def crear(doc: dict) -> str
def get_by_id(id) -> dict | None
def metodo_menos_usado() -> str | None    # caso de uso 2

# src/repositories/resena_repo.py
def crear(doc: dict) -> str
def get_by_id(id) -> dict | None
def top_autores(n: int, tipo: str) -> list[dict]   # caso 1
def ratings_de_destinatario(id: str) -> list[int]  # para recalcular avg
def buscar_por_rating_extremo() -> list[dict]      # caso 7

# src/repositories/login_history_repo.py
def crear(usuario_id, tipo_cuenta, evento) -> None
def listar_por_usuario(id) -> list[dict]
```

### Cassandra (rol Cassandra)

```python
# src/repositories/ubicacion_repo.py
def insertar(vehiculo_id: UUID, ts: datetime, lat: Decimal, lon: Decimal,
             viaje_id: UUID | None = None) -> None
def historial(vehiculo_id: UUID) -> list[dict]

# src/repositories/actividad_repo.py
def upsert_ultima(conductor_id: UUID, ts: datetime, viaje_id: UUID) -> None
def get_ultima(conductor_id: UUID) -> dict | None
def insertar_viaje_finalizado(dia: date, viaje_id, conductor_id, usuario_id,
                              duracion_min: int, distancia_km: float) -> None
def conductores_activos_desde(limite: datetime) -> list[UUID]    # caso 3
def promedio_duracion() -> float                                  # caso 4
```

### Neo4j (rol Neo4j)

```python
# src/repositories/grafo_repo.py
def crear_usuario(id: str, nombre: str, email: str) -> None
def crear_conductor(id: str, nombre: str, email: str, rating: float = 0) -> None
def crear_vehiculo(id, placa, marca, modelo, anio=None) -> None
def crear_relacion_maneja(conductor_id: str, vehiculo_id: str) -> None
def incrementar_viajo_con(usuario_id: str, conductor_id: str) -> None
def coincidencias(min_viajes: int) -> list[dict]                       # caso 5
def vehiculos_marca_y_patente_termina(marca: str, sufijo: str) -> int  # caso 6
```

### Redis (rol Redis+Menú)

```python
# src/repositories/cache_repo.py
# Sesiones
def set_session(token: str, data: dict, ttl_seconds: int) -> None
def get_session(token: str) -> dict | None
def delete_session(token: str) -> None

# Última posición de vehículo (TTL 30s)
def set_ultima_pos(vehiculo_id: str, lat: float, lon: float) -> None
def get_ultima_pos(vehiculo_id: str) -> tuple[float, float] | None

# Cache genérico (TTL configurable)
def set_cache(key: str, value, ttl_seconds: int = 300) -> None
def get_cache(key: str) -> any | None
def invalidar(key: str) -> None
```

---

## 🌿 Workflow Git

### Branches

- **`main`** — siempre estable, code review obligatorio antes de mergear.
- **`feature/<descripcion-corta>`** — branches de trabajo. Ejemplos:
  - `feature/postgres-usuario-repo`
  - `feature/mongo-resenas-aggregation`
  - `feature/neo4j-grafo-repo-coincidencias`
  - `feature/redis-cache-session`
  - `feature/menu-submenu-cuentas`
- **`fix/<descripcion-corta>`** — para bugfixes.

### Workflow típico

```bash
# Arrancás una tarea
git checkout main
git pull
git checkout -b feature/mongo-pago-repo

# Trabajás, hacés commits chicos
git add src/repositories/pago_repo.py tests/repositories/test_pago_repo.py
git commit -m "agregar pago_repo con CRUD basico"

git add src/repositories/pago_repo.py
git commit -m "agregar pago_repo.metodo_menos_usado() con aggregation"

# Cuando terminás, push y abrís PR
git push -u origin feature/mongo-pago-repo
# Andá a github.com → te ofrece "Compare & pull request" → click → mensaje descriptivo
```

### Convenciones de commits

- **Idioma:** español.
- **Modo:** imperativo presente.
- **Ejemplos buenos:**
  - `agregar viaje_repo.iniciar() + 3 tests`
  - `fix: actividad_repo no devolvia ultimo_viaje_id`
  - `refactor: simplificar query de coincidencias en Neo4j`
- **Ejemplos malos:**
  - `cambios` (vago)
  - `arreglos varios` (mezclar contextos)
  - `i added the function` (inglés + tono narrativo)

### Code review

- **Mínimo 1 reviewer** que NO sea el autor.
- Mirá: tests verdes, contratos respetados (no cambia firmas públicas sin avisar), naming consistente, sin secrets commiteados.
- Si todo OK, mergeá con **"Squash and merge"** (mantiene `main` limpio).

---

## 🤖 Starter prompt para AI tools

Copia-pegá esto al inicio de cada conversación con tu AI (Claude, ChatGPT, Cursor, etc.) — **personaliza solo las líneas con `[ ... ]`**:

```
Soy [TU NOMBRE], integrante del equipo del TP de Datos 2 (UADE).

Repo: https://github.com/lucianolacheta1/TP-Datos2-Uber

Mi asignación es: [TU DB — ver tabla en docs/asignaciones-equipo.md]

Antes de ayudarme, leé estos archivos del repo (en este orden):
1. CLAUDE.md (memoria del proyecto)
2. docs/asignaciones-equipo.md (mi rol específico y mi lista de lectura)
3. docs/diseno.md (las secciones que mi rol indica leer)
4. docs/decisiones.md (los ADRs relevantes para mi rol)
5. Los planes de implementación que mi rol indica: docs/plan-XX-*.md

Reglas:
- NO toques archivos de otras DBs / otros módulos.
- RESPETÁ los contratos de mis repositories y los de otros (sección
  "Contratos entre repositories" del doc de asignaciones).
- Hablame en español argentino.
- Si tenés dudas sobre el contexto, ANTES preguntá — no inventes.
- Asumí que las variables de entorno del .env están cargadas; nunca me
  pidas credenciales reales.
- Cuando edites código, mostrame el código completo del archivo después
  del cambio (no fragmentos).

Estoy arrancando con la tarea: [DESCRIBÍ LA TAREA, EJ: "implementar viaje_repo.crear() y su test"].
```

> 💡 **Tip:** si tu AI tiene función de "Custom Instructions" o "System Prompt" (ChatGPT, Cursor), pegá las primeras 4 líneas como instrucción persistente y solo cambiás la tarea por mensaje.

---

## ❓ FAQ rápida para el equipo

**P: ¿Qué hago si necesito modificar el código de otra DB?**
R: NO lo hagas directamente. Avisá al "dueño" de esa DB por el chat o abrí un issue. Si es urgente y el dueño no está, hacé el cambio en un branch separado y mencionalo en el PR para que el dueño revise.

**P: Mi AI me sugiere cambiar una firma de un repository — ¿lo hago?**
R: NO sin consultar. Las firmas son **contratos** que otros services usan. Si la firma actual no te alcanza, abrí un issue para que el equipo discuta.

**P: ¿Puedo agregar nuevas funciones a mi repository?**
R: Sí, siempre. **Agregar** no rompe nada. Solo cuidado con **modificar/eliminar** lo que ya existe.

**P: ¿Cómo sé si mi tarea está terminada?**
R: Tres condiciones:
1. Los tests del Plan correspondiente pasan (`pytest tests/...`).
2. `python -m scripts.check_connections` sigue devolviendo 5/5 OK (no rompiste nada).
3. Pasaste code review en el PR.

**P: ¿Y si me trabo?**
R: Postealo en el chat del grupo. Si Luciano está disponible, preguntale directo. Si no, otro del equipo con menos carga puede ayudar (especialmente si ya pasó por algo similar en su propia DB).

**P: ¿Tengo que entender las 5 bases o solo la mía?**
R: La tuya en profundidad. De las otras alcanza con que entiendas **qué hacen** (suficiente con leer `docs/diseno.md` §4 entero, ~10 min). Eso es lo que vamos a defender frente al profesor — todos tienen que poder hablar del sistema completo.

---

## 🔗 Recursos rápidos

| Tu rol | Recurso clave | Tiempo de lectura |
|---|---|---|
| Postgres | https://neon.tech/docs + https://www.postgresql.org/docs/current/ddl.html | 30 min |
| Mongo | https://www.mongodb.com/docs/manual/aggregation/ | 1 h |
| Cassandra | https://cassandra.apache.org/doc/latest/cassandra/data_modeling/intro.html | 1.5 h |
| Neo4j | https://neo4j.com/docs/getting-started/cypher-intro/ | 1-2 h |
| Redis | https://redis.io/docs/latest/develop/get-started/ | 20 min |
