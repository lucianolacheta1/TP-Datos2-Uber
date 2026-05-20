# TP Uber — Datos 2 (UADE)

Sistema de gestión de datos para una plataforma de transporte compartido tipo Uber. Trabajo Práctico de la materia **Datos 2** en UADE, cátedra Mosquera Prada.

El sistema integra **5 bases de datos** (1 relacional + 4 NoSQL) demostrando cómo distintos paradigmas pueden coexistir y cooperar:

| Tipo | Tecnología | Hosting |
|---|---|---|
| Relacional | PostgreSQL | Neon |
| Documental | MongoDB | Atlas |
| Columnar | Cassandra | DataStax Astra |
| Grafo | Neo4j | Aura |
| Cache / sesiones | Redis | Redis Cloud / Upstash |

## Por dónde empezar

1. **`CLAUDE.md`** — memoria del proyecto: stack, estructura del repo, reglas de mantenimiento.
2. **`docs/diseno.md`** — diseño técnico completo: modelo de datos, mapeo de casos de uso, flujo de datos.
3. **`docs/decisiones.md`** — por qué tomamos cada decisión arquitectónica (ADRs).
4. **`docs/tareas.md`** — roadmap del proyecto: qué hicimos, qué falta, qué está en curso.
5. **`docs/justificacion-der.md`** — cambios al DER (documento para mostrar al profesor).
6. **`docs/presentacion.md`** — plan de defensa del TP (guion del demo, slides, checklist).

## Cómo correr el proyecto

> Pendiente — se completará cuando exista la carpeta `src/`. Por ahora el repo contiene solo la documentación y el diseño del sistema.

## Equipo y colaboración

Trabajo grupal. Ver `docs/decisiones.md` (ADR-012) para las convenciones de Git y branches.
