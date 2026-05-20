# CLAUDE.md — TP Uber (Datos 2 — UADE)

> Memoria del proyecto. Este archivo le da contexto a Claude (u otro asistente) cuando entre nuevo al repositorio.

## Qué es este proyecto

Sistema de gestión de datos para una plataforma de transporte compartido tipo Uber. Trabajo Práctico de la materia **Datos 2** (UADE), cátedra Mosquera Prada. Trabajo grupal.

**Repositorio remoto:** https://github.com/lucianolacheta1/TP-Datos2-Uber

El TP requiere integrar **1 base relacional + 3 NoSQL como mínimo** demostrando interacción y consistencia entre todas. Nuestra implementación usa **5 bases** (Postgres + 4 NoSQL).

> *"Es motivo de desaprobar que las bases de datos no interactúen entre sí."* — Prof. Mosquera (video de presentación del TP)

## Stack

| Componente | Tecnología | Hosting cloud |
|---|---|---|
| Lenguaje | Python 3.11+ | — |
| Base relacional | PostgreSQL | Neon |
| Base documental | MongoDB | Atlas |
| Base columnar | Cassandra | DataStax Astra |
| Base de grafo | Neo4j | Aura |
| Cache / sesiones | Redis | Redis Cloud / Upstash |
| Interfaz | Consola con menú | Local |

**Todo corre en la nube.** No hay Docker ni instalaciones locales.

## Estructura del repositorio

```
TPUber/
├── CLAUDE.md                                  ← este archivo (memoria del proyecto)
├── docs/
│   ├── diseno.md                              ← diseño técnico completo (LEER PRIMERO)
│   ├── justificacion-der.md                   ← justificación de cambios al DER (para el profesor)
│   ├── decisiones.md                          ← ADRs: cada decisión con su rationale
│   ├── presentacion.md                        ← plan de defensa del TP (guion + slides + checklist)
│   └── tareas.md                              ← roadmap del proyecto (hecho / en curso / pendiente)
├── Uber/                                      ← material original del enunciado (NO MODIFICAR)
│   ├── Uber.pdf                               ← DER del sistema
│   └── Uber.docx                              ← requerimientos + 7 casos de uso
├── Meeting with MOSQUERA...vtt                ← transcripción del video del profesor
└── (src/  — la carpeta de código vendrá cuando empiece la implementación)
```

## Por dónde empezar a leer

Si entrás nuevo al proyecto, leé en este orden:

1. **`docs/diseno.md`** — diseño técnico completo: stack, modelo de datos en cada base, mapeo de casos de uso, flujo de datos y consistencia.
2. **`docs/decisiones.md`** — por qué tomamos cada decisión clave (ADRs).
3. **`docs/tareas.md`** — qué se hizo, qué está en curso, qué falta.
4. **`docs/justificacion-der.md`** — cambios al DER (para mostrar al profesor).
5. **`docs/presentacion.md`** — plan de defensa del TP (cuando se acerque la fecha).
6. **`Uber/Uber.docx`** — enunciado original del TP.
7. **`Uber/Uber.pdf`** — DER original del sistema.

## Reglas de mantenimiento de la documentación

**Cada vez que se tome una decisión arquitectónica o se haga un cambio relevante al proyecto, hay que documentarlo en los archivos correspondientes.** Esto vale para cualquier persona o asistente que toque el proyecto.

| Tipo de cambio | Dónde documentarlo |
|---|---|
| Decisión arquitectónica nueva (elección de tecnología, patrón, etc.) | Nuevo ADR en `docs/decisiones.md` |
| Cambio en el modelo de datos, esquema o flujo | Actualizar `docs/diseno.md` |
| Modificación al DER o cambio en su justificación | Actualizar `docs/justificacion-der.md` |
| Avance en las tareas del proyecto | Marcar/agregar en `docs/tareas.md` |
| Cambio en el plan de defensa del TP (guion, slides, demo) | Actualizar `docs/presentacion.md` |
| Cambio que afecta a quien lea el repo | Actualizar `CLAUDE.md` (este archivo) |

**Qué NO requiere documentación:** fixes de typos, refactors triviales, ajustes menores de formato, renombres de variables sin impacto. Usar criterio.

**Cómo documentar:**
- Ser **conciso**: contexto → decisión → consecuencias.
- Incluir **fecha** y **estado** (Aceptada / Rechazada / Reemplazada por X).
- Si una decisión se cambia, **no borrar la vieja**: marcarla como "Reemplazada" y crear una nueva entrada. Trazabilidad.

## Reglas con el material original

- **Nunca modificar** archivos en `Uber/` ni la transcripción `.vtt`. Son entrada inmutable.
- Si hay que extraer info, copiar a `docs/` y trabajar sobre la copia.

## Convenciones

- **Idioma:** español para documentación; código mixto (nombres de funciones/variables en español están OK).
- **Nombres de archivos:** sin acentos ni ñ (portabilidad con git / shells).
- **Credenciales:** todas en `.env` (gitignored). Nunca commitear connection strings, tokens ni passwords.
- **Sin emojis** en código y mensajes de commit. Sí permitido en documentación cuando ayudan a la legibilidad.
- **Commits:** mensajes en español, en imperativo presente. Ej: `agregar conexión a Neo4j`, `documentar decisión sobre Redis`.

## Patrón arquitectónico clave (recordatorio)

**Postgres mantiene solo el catálogo de identidad** (usuarios, conductores, vehículos). El resto vive en NoSQL:

- Viajes, pagos, reseñas → **MongoDB**
- Ubicaciones GPS + agregados time-series → **Cassandra**
- Coincidencias usuario-conductor + vehículos como nodos → **Neo4j**
- Sesiones con TTL, última posición vehículo, cache → **Redis**

Cada operación de negocio toca varias bases (write-through best-effort + reconciliación periódica). Ver `docs/diseno.md` sección 6 para el detalle.

## Cómo correr el proyecto

> Pendiente — se completará cuando exista la carpeta `src/`.

## Equipo

Trabajo grupal. La estructura del proyecto y los servicios se diseñan para permitir trabajo en paralelo: cada miembro puede tomar una base y sus servicios asociados.

---

**Última actualización:** 2026-05-19
