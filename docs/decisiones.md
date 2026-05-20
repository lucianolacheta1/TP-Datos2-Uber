# Registro de decisiones arquitectónicas (ADRs)

> Cada entrada documenta una decisión clave tomada durante el diseño.
> Formato: contexto → decisión → consecuencias.

---

## ADR-001 — Lenguaje de implementación: Python

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** El profesor explicitó que el lenguaje es libre; no se evalúa la calidad del código sino la interacción entre las bases. Se evaluaron Python, Java, JavaScript y C#.

**Decisión:** Python 3.11+.

**Razones:**
- Drivers oficiales y maduros para las 5 bases (`psycopg`, `pymongo`, `cassandra-driver`, `neo4j`, `redis`).
- Es el lenguaje que el profesor mostró en el video.
- Menos verboso que Java; sin necesidad de tooling pesado.
- Sintaxis legible para todo el equipo independientemente de su nivel.

**Consecuencias:**
- ✅ Productividad alta; setup mínimo.
- ⚠️ Sin verificación de tipos en tiempo de compilación → mitigar con type hints + `mypy` si surge la necesidad.

---

## ADR-002 — Hosting: todas las bases en la nube

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** El profesor recomendó cloud por practicidad ("la pueden interactuar todos, cada uno desde su casa"). Alternativas: Docker local, híbrido, todo cloud.

**Decisión:** Todo cloud:
- PostgreSQL → Neon (free tier permanente).
- MongoDB → Atlas (512 MB free).
- Cassandra → Astra DB (free tier).
- Neo4j → Aura Free (1 DB, 200k nodos).
- Redis → Redis Cloud o Upstash (30 MB free).

**Razones:**
- El equipo es grupal: tres personas pueden conectarse a la misma base sin tener que coordinar Dockers.
- Free tiers permanentes (Neon) o lo suficientemente generosos para un TP.
- Replica exactamente lo que el profesor hizo en el video.

**Consecuencias:**
- ✅ Cero setup local.
- ⚠️ Dependencia de internet para desarrollar.
- ⚠️ Hay que cuidar las credenciales (no commitear `.env`).

---

## ADR-003 — Interfaz: consola con menú numérico

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** El profesor mostró una app de consola con menú numérico tipo `"1. Registrar usuario, 2. Crear viaje..."`. Alternativas: API REST, frontend web.

**Decisión:** Consola con menú numérico, estilo idéntico al ejemplo del profesor.

**Razones:**
- Suficiente para demostrar la interacción entre bases.
- El profesor explicó que no evalúa la calidad de la UI ni el código en sí.
- Tiempo del equipo se enfoca en lo que sí se evalúa: el diseño de datos y la interacción multi-DB.

**Consecuencias:**
- ✅ Avance rápido.
- ⚠️ Menos vistoso visualmente — se compensa con buenas demos durante la presentación.

---

## ADR-004 — Stack NoSQL final: Mongo + Cassandra + Neo4j + Redis

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** El TP requiere 1 relacional + 3 NoSQL como mínimo. Se evaluaron combinaciones distintas.

**Decisión:** Las 4 NoSQL: MongoDB + Cassandra + Neo4j + Redis (junto con PostgreSQL como relacional = **5 bases en total**).

**Razones:**
- **MongoDB**: datos operativos polimórficos (reseñas) y rica metadata (viajes, pagos).
- **Cassandra**: time-series GPS de alta frecuencia (Requerimiento 6 del enunciado).
- **Neo4j**: caso de uso 5 es textbook de grafos (coincidencias usuario-conductor).
- **Redis**: sesiones con TTL (replica el demo del profesor) + cache + última posición vehículo.
- Cada base "brilla" en al menos un rol concreto: ninguna queda decorativa.
- Suma una base por sobre lo requerido → señal de iniciativa positiva.

**Decisión rechazada:** quedarnos solo con 3 NoSQL (Mongo + Cassandra + Neo4j) sin Redis.
- Razón del rechazo: Redis agrega un paradigma adicional con muy bajo costo de implementación y permite replicar el demo de sesiones del profesor.

**Consecuencias:**
- ✅ Diversidad máxima de paradigmas (relacional + documental + columnar + grafo + key-value).
- ⚠️ Hay que sincronizar 5 bases en lugar de 4 → mitigado con patrón write-through best-effort.
- ⚠️ Confirmar con el profesor que está OK ir más allá del mínimo de 4 bases.

---

## ADR-005 — Patrón arquitectónico: Postgres como catálogo mínimo de identidad

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** Se evaluaron tres enfoques para distribuir datos entre las bases:
- **Postgres como SOT completo** con NoSQL como vistas duplicadas → no fiel al video del profesor; subutiliza las NoSQL.
- **Cada entidad en una sola base** → fragmenta queries; consistencia compleja.
- **Postgres catálogo mínimo + NoSQL operativas** → patrón del profesor.

**Decisión:** Postgres mantiene **solo** las entidades de identidad (usuario, conductor, vehiculo). El resto de datos operativos vive en las NoSQL, donde cada una se elige por su patrón de acceso.

**Razones:**
- Replica fielmente el patrón demostrado por el profesor.
- Maximiza la "interacción entre bases": cada evento de negocio escribe en 2-5 bases.
- Cada NoSQL almacena datos que realmente le corresponden por paradigma.
- Postgres queda chico y manejable; sirve como "registro civil" inmutable.

**Consecuencias:**
- ✅ Diseño coherente con la materia (NoSQL es protagonista).
- ✅ Justificación clara del rol de cada base.
- ⚠️ Sin ACID nativo en pagos (mitigado: irrelevante para TP escolar; Mongo tiene transacciones desde 4.0).
- ⚠️ Más lógica de sincronización en código → encapsulada en servicios por entidad.

---

## ADR-006 — Modelo de reseña: discriminador `tipo` (Opción 3)

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** El DER original tiene `RESEÑA.autor_id` y `RESEÑA.destinatario_id` como FKs ambiguas (pueden apuntar a USUARIO o a CONDUCTOR). Se evaluaron tres soluciones:

- **Opción 1:** Supertipo PERSONA con subtipos.
- **Opción 2:** Dos entidades separadas (RESEÑA_PASAJERO_A_CONDUCTOR y RESEÑA_CONDUCTOR_A_PASAJERO).
- **Opción 3:** Una entidad con dos FKs explícitas + discriminador `tipo`.

**Decisión:** Opción 3.

**Razones:**
- Mínimo refactor del DER original.
- Encaja naturalmente con un documento Mongo que tiene `autor:{...}`, `destinatario:{...}`, `tipo`.
- Queries simples (`find({tipo: 'U_A_C'})`).

**Consecuencias:**
- ✅ Simplicidad de implementación.
- ⚠️ Las queries deben filtrar por `tipo` para no contar reseñas en el sentido opuesto.

---

## ADR-007 — Cardinalidad CONDUCTOR-VEHICULO: 0..\*

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** El DER original define `CONDUCTOR (1) — (1..*) VEHICULO`, obligando a todo conductor a tener al menos un vehículo.

**Decisión:** Cambiar a `(0..*)`.

**Razones:**
- Realismo: un conductor puede registrarse antes de cargar su vehículo.
- Simplifica el orden de operaciones en el alta.

---

## ADR-008 — Patrón de escritura: write-through best-effort + reconciliación

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** Cada evento de negocio toca múltiples bases. Se evaluaron tres patrones:

- **Transacción distribuida 2PC** → no soportado limpiamente por Mongo + Cassandra + Neo4j.
- **Eventos asíncronos con cola (Kafka/RabbitMQ)** → overkill para un TP.
- **Write-through best-effort + reconciliación** → simple, robusto, ampliamente usado.

**Decisión:** Cada operación escribe primero al SOT (crítico, falla = abort). Luego intenta proyectar a bases derivadas; los fallos se loguean en un outbox y se reintenta en la reconciliación periódica.

**Razones:**
- Implementable con 50-100 líneas de Python.
- Tolerante a fallos parciales: una base caída no rompe la app.
- La reconciliación garantiza consistencia eventual.

---

## ADR-009 — Distribución de casos de uso por base

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** Se decidió que Postgres no resuelva ningún caso de uso directamente, para enfatizar el rol protagónico de las NoSQL (es una materia de NoSQL).

**Decisión:**

| # | Caso | Base |
|---|---|---|
| 1 | Top 3 reseñadores | Mongo (+ cache Redis) |
| 2 | Método pago menos usado | Mongo |
| 3 | Conductores inactivos último mes | Cassandra |
| 4 | Tiempo promedio viajes | Cassandra (+ cache Redis) |
| 5 | Coincidencias pasajero-conductor >1 viaje | Neo4j |
| 6 | Autos Toyota patente "D" | Neo4j |
| 7 | Rating 5 o <2 | Mongo |

**Razones:**
- Mongo, Cassandra y Neo4j resuelven 2+ casos cada una.
- Postgres mantiene rol de soporte (identidad + integridad).
- Redis cumple rol transversal (sesiones, cache, posición actual) — no resuelve casos directamente pero es indispensable.

---

## ADR-010 — Documentación: separar por audiencia y propósito

**Fecha:** 2026-05-19
**Estado:** Aceptada (actualizada 2026-05-19: se sumó `presentacion.md` y `tareas.md`)

**Contexto:** Se evaluó documentar todo en un único archivo grande vs separar por audiencia.

**Decisión:** Múltiples archivos en `docs/` y `CLAUDE.md` en la raíz, cada uno con un propósito y audiencia bien definidos:

| Archivo | Audiencia | Propósito |
|---|---|---|
| `CLAUDE.md` (raíz) | Cualquier persona/asistente entrando al repo | Memoria del proyecto, reglas y pointers |
| `docs/diseno.md` | Equipo | Diseño técnico vivo (modelo de datos, flujos, arquitectura) |
| `docs/justificacion-der.md` | Profesor | Justificación de cambios al DER para la presentación |
| `docs/decisiones.md` | Equipo + profesor | Registro de decisiones arquitectónicas (ADRs — este archivo) |
| `docs/presentacion.md` | Equipo (para ensayar) | Plan de defensa: guion del demo, slides, checklist |
| `docs/tareas.md` | Equipo | Roadmap del proyecto: hecho / en curso / pendiente |

**Razones:**
- Cada audiencia tiene su documento sin ruido innecesario.
- El doc del profesor puede compartirse o imprimirse sin filtrar contenido técnico interno.
- El doc de presentación no contamina al de diseño con guiones, slides y checklists.
- Los ADRs son referenciables desde cualquier otro documento.

---

## ADR-011 — Arquitectura en 5 capas (menu → casos_uso/services → repositories → db)

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** Con 5 bases de datos y múltiples operaciones que tocan varias bases por cada acción de usuario, sin una arquitectura clara el código rápidamente se vuelve un spaghetti de imports. Se evaluaron alternativas:

- **Monolítico (todo en `main.py`)** → inmanejable, sin reuso.
- **MVC clásico (Model-View-Controller)** → no encaja bien con multi-DB.
- **Hexagonal / Ports & Adapters** → demasiado pesado para un TP.
- **5 capas con dependencias unidireccionales** → punto medio.

**Decisión:** Estructura en 5 capas con dependencias estrictamente unidireccionales:

```
menu/ → casos_uso/ → services/ → repositories/ → db/
```

**Reglas clave:**
- Cada repository toca **una sola base** (`viaje_repo.py` solo conoce Mongo).
- Cada service que escribe en múltiples bases usa el patrón `write-through best-effort` con `_intentar(...)`.
- Los casos de uso son solo lecturas; los services hacen escrituras y orquestación.
- El menú nunca llama a repositories o `db/` directamente (saltearía la lógica de negocio).

**Razones:**
- Separación de responsabilidades clara.
- Facilita la división de trabajo en el grupo: cada miembro puede tomar capas verticales (una base + sus repositorios + sus servicios).
- Testeable: cada repository se puede mockear sin afectar a los demás.
- Si mañana hay que cambiar Mongo por DynamoDB, solo se reescribe `viaje_repo.py`.

**Consecuencias:**
- ✅ Código organizado y predecible.
- ✅ El trabajo en paralelo no genera conflictos en los mismos archivos.
- ⚠️ Más archivos que un script monolítico → mitigado con imports absolutos y nombres descriptivos.

---

## ADR-012 — Control de versiones: repositorio en GitHub

**Fecha:** 2026-05-19
**Estado:** Aceptada

**Contexto:** El trabajo es grupal y necesita un mecanismo de sincronización entre los integrantes. Se evaluó:

- **GitHub** (público o privado).
- **GitLab / Bitbucket** (alternativas).
- **Compartir por Drive / pendrive** (descartado obviamente).

**Decisión:** Repositorio en GitHub: https://github.com/lucianolacheta1/TP-Datos2-Uber

**Razones:**
- Estándar de la industria; el equipo está familiarizado.
- Permite colaboración limpia con branches + pull requests.
- Historial completo y revisable durante la presentación si el profesor lo pide.
- Sirve también para mostrar el repo al profesor como entregable.

**Consecuencias:**
- ✅ Sincronización fluida entre los integrantes del grupo.
- ✅ Backup automático del proyecto en la nube.
- ⚠️ Hay que ser estricto con el `.gitignore`: nunca commitear `.env`, secure connect bundles, ni credenciales.
- ⚠️ Cada integrante necesita cuenta de GitHub y permisos en el repo (gestionar via Settings → Collaborators).

**Convenciones acordadas:**
- Branch principal: `main`.
- Branches de feature: `feature/<nombre-corto>` (ej: `feature/setup-cassandra`).
- Commits en español, en imperativo presente (ej: `agregar conexión a Neo4j`).
- Pull requests para integrar a `main` (opcional al inicio; recomendado cuando empiece el código).

**Qué va al repositorio:**

| ✅ Versionado en el repo | ❌ Solo local (no se sube) |
|---|---|
| `CLAUDE.md` | `Uber/` (material original del enunciado) |
| `docs/` completo | `Meeting with MOSQUERA...vtt` (transcripción del video) |
| `README.md` (portada del repo) | `.env` (credenciales reales) |
| `.gitignore` | `*.zip` (secure connect bundles de Cassandra) |
| Futuro código en `src/`, `scripts/`, etc. | `venv/`, `__pycache__/`, `.idea/`, `.vscode/` |

Razón de excluir `Uber/` y el `.vtt`: son materiales que el profesor entregó a todo el grupo; cada integrante ya los tiene en su Drive de la facultad. No tiene sentido versionarlos.
