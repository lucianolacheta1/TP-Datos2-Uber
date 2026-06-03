# Plan de construcción del PowerPoint — Defensa del TP

> Plan operativo para armar el `.pptx` que va a usar el equipo durante la defensa frente al profesor.
> El **contenido y la estructura de las 8 slides** ya está definido en [`docs/presentacion.md §5`](presentacion.md). Este doc cubre solo:
> - Qué materiales hay que juntar
> - Quién captura/aporta qué
> - En qué momento del cronograma se obtiene cada cosa
> - Cómo se construye el archivo final
>
> Última actualización: 2026-05-26
> Audiencia: equipo

---

## 1. Objetivo

Producir 1 `presentacion.pptx` + 1 `presentacion.pdf` (backup) para la defensa final del TP de Datos 2 frente al Prof. Mosquera Prada.

**Formato esperado:**
- 8 slides según `docs/presentacion.md §5`.
- Cada slide entendible en ~10 segundos.
- **Mucho diagrama, poco texto.**
- Funciona offline (PDF backup por si PowerPoint falla).

---

## 2. Las 8 slides — recordatorio

| # | Slide | Visual principal | Texto principal |
|---|---|---|---|
| 1 | Portada | Logo UADE / portada simple | TP Uber + integrantes + cátedra + fecha |
| 2 | Contexto | Cita textual del profesor | Qué es el TP + requisito clave |
| 3 | DER + cambios | Captura del DER original | Tabla con cambios E1-E5 (3 columnas: problema / solución / por qué) |
| 4 | Stack tecnológico | Logos de las 5 bases | Tabla tipo / hosting cloud |
| 5 | Arquitectura | Diagrama "Postgres mínimo + NoSQL operativas" | Frase corta del patrón |
| 6 | Mapeo casos → base | Tabla con los 7 casos | Distribución (Mongo 3, Cassandra 2, Neo4j 2, Postgres 0 directos) |
| 7 | Flujo de datos | Diagrama "finalizar viaje" tocando 4 bases | "Una sola acción del usuario → 4 bases en simultáneo" |
| 8 | Cierre | Lecciones aprendidas (3-4 bullets) | Agradecimiento + preguntas |

---

## 3. Inventario de materiales necesarios

### 🟢 A. Logos e imágenes estáticas (descargables de internet — fácil)

| Item | Para qué slide | Fuente sugerida |
|---|---|---|
| Logo UADE | 1 (portada) | https://www.uade.edu.ar |
| Logo Python | 4 (stack) | https://www.python.org |
| Logo PostgreSQL | 4, 5 | https://www.postgresql.org/about/ |
| Logo MongoDB | 4, 5 | https://www.mongodb.com/brand-resources |
| Logo Cassandra | 4, 5 | https://cassandra.apache.org |
| Logo Neo4j | 4, 5 | https://neo4j.com/company/brand/ |
| Logo Redis | 4, 5 | https://redis.io/brand |
| Logo Neon | 4 | https://neon.tech |
| Logo Atlas/MongoDB Cloud | 4 | https://www.mongodb.com |
| Logo DataStax Astra | 4 | https://www.datastax.com |
| Logo Neo4j Aura | 4 | https://neo4j.com/cloud/aura/ |
| Logo Redis Cloud | 4 | https://redis.io/cloud/ |

**Responsable:** cualquiera del equipo. Los podemos juntar en una carpeta `docs/slides/assets/logos/`.

---

### 🟡 B. DER original + diagramas (yo los puedo armar)

| Item | Para qué slide | Cómo se obtiene |
|---|---|---|
| **Imagen del DER original** | 3 | Extraigo la imagen del `Uber/Uber.pdf` con Python (`pdftoppm` o similar) |
| **Diagrama "Postgres mínimo + NoSQL operativas"** | 5 | Yo lo redibujo en PPTX a partir de la descripción en `docs/diseno.md §3` |
| **Diagrama "Finalizar viaje" multi-DB** | 7 | Yo lo redibujo en PPTX a partir de `docs/diseno.md §6.5` |
| **Tabla mapeo casos → base** | 6 | Tabla generada directo desde `docs/diseno.md §5` |
| **Tabla cambios E1-E5** | 3 | Tabla generada directo desde `docs/justificacion-der.md §A` |

**Responsable:** yo cuando armemos el `.pptx`.

---

### 🔴 C. Screenshots de las cloud consoles (TU TAREA — capturar AHORA)

> Estos los podés sacar **YA** sin esperar a que esté el código terminado. Lo único que necesitan es que las DBs existan, y ya existen.

Capturá pantallas tipo "todas las DBs activas" para mostrar al profesor que **el setup cloud realmente funciona**:

| # | Captura | Plataforma | Qué mostrar |
|---|---|---|---|
| C1 | Dashboard Neon | console.neon.tech | El proyecto `tp-uber` activo con stats |
| C2 | Dashboard Atlas | cloud.mongodb.com | El cluster `UADE-ID2-UBER` running |
| C3 | Dashboard Astra | astra.datastax.com | La DB `UADE_ID2_UBER` con keyspace `uber_tp` |
| C4 | Dashboard Aura | console.neo4j.io | La instance running |
| C5 | Dashboard Redis Cloud | app.redislabs.com | La DB `UADE-ID2-UBER` running |

**Formato sugerido:**
- PNG, resolución mínima 1920×1080.
- Sin información confidencial visible (cubrí credenciales si aparecen).
- Nombre del archivo: `dashboard-neon.png`, `dashboard-atlas.png`, etc.

**Dónde guardarlas:** `docs/slides/assets/screenshots-cloud/` (creamos la carpeta cuando estés listo).

---

### 🔴 D. Screenshots de queries y resultados (CUANDO HAYA DATOS — Fase 5+ del Plan 05)

> Estos van **después** de que `seed_data.py` corra y los 7 casos devuelvan datos reales. Los capturamos cerca del día del demo.

| # | Captura | Cliente / Tool | Qué mostrar |
|---|---|---|---|
| Q1 | Output `check_connections` | Terminal | `5/5 OK` con timestamps |
| Q2 | Tablas Postgres con datos | DBeaver o SQL Editor de Neon | `SELECT * FROM usuario LIMIT 5;` con datos del seed |
| Q3 | Colección Mongo viajes | MongoDB Compass | 50 viajes con `usuario_snapshot` y `conductor_snapshot` visibles |
| Q4 | Aggregate caso 1 ejecutado | Mongo Compass o consola | Top 3 reseñadores con sus cantidades |
| Q5 | Cassandra ubicaciones | CQL Console de Astra | `SELECT * FROM ubicaciones_por_vehiculo LIMIT 10;` lleno |
| Q6 | ⭐ Grafo Neo4j caso 5 | Neo4j Workspace | Visualización del grafo con nodos y aristas VIAJO_CON — **el "wow moment"** |
| Q7 | Cypher caso 6 ejecutado | Neo4j Workspace | Resultado de Toyota patente D |
| Q8 | Redis sessions con TTL | RedisInsight | Lista de claves `session:*` con sus tiempos vivos |

**Formato sugerido:** PNG, ≥1920×1080. Carpeta: `docs/slides/assets/screenshots-queries/`.

---

### 🟢 E. Datos del proyecto que ya tengo (yo aporto)

- ✅ Lista de los 12 ADRs (de `docs/decisiones.md`).
- ✅ Texto del patrón arquitectónico (de `docs/diseno.md §3`).
- ✅ Tabla de modificaciones al DER (E1-E5) (de `docs/justificacion-der.md §A`).
- ✅ Tabla de mapeo casos → base (de `docs/diseno.md §5`).
- ✅ Matriz de eventos → bases tocadas (de `docs/diseno.md §6.1`).
- ✅ Lista de "lecciones aprendidas" (de `docs/presentacion.md §8`).

---

## 4. Cronograma sugerido

```
HOY (2026-05-26)
├── Vos: capturás los 5 screenshots de cloud consoles (sección C)
├── Vos: descargás los logos (sección A) — ~10 minutos
└── Cualquiera del equipo: crea la carpeta docs/slides/assets/ en el repo

CUANDO TERMINEMOS FASE 3 (esquemas creados)
├── Capturar screenshots de las DBs con sus tablas/colecciones vacías
└── (opcional — no es crítico para la defensa)

CUANDO TERMINEMOS FASE 7 (seed corrió + 7 casos OK)
├── Capturar los 8 screenshots de queries con datos reales (sección D)
└── El grafo Neo4j Q6 es el más importante — sacalo nítido

24-48 HS ANTES DE LA DEFENSA
├── Vos me pasás todos los materiales agrupados
├── Yo armo el .pptx en una sola sesión (~1-2 horas)
├── Vos lo revisás y pedís ajustes
├── Iteramos hasta que esté OK
└── Exportamos a PDF y commiteamos al repo

DÍA DE LA DEFENSA
├── Slides cargadas en la laptop + USB de backup
├── PDF abierto en una pestaña por si PowerPoint falla
└── Ver `docs/presentacion.md §7` (checklist del día anterior)
```

---

## 5. Cómo me pasás los materiales

Cuando juntes una tanda (no hace falta esperar a tener todo):

**Opción A — Commit al repo (recomendado):**
```bash
mkdir -p docs/slides/assets/{logos,screenshots-cloud,screenshots-queries}
# guardás los archivos con nombres descriptivos
git add docs/slides/assets/
git commit -m "agregar screenshots de cloud consoles para slides"
git push
```

Ventaja: queda versionado y los compañeros lo pueden ver.

**Opción B — Drive con permiso de lectura:**
- Subís a una carpeta compartida.
- Me pasás el link.

**Opción C — Pegar imágenes en una conversación conmigo:**
- Funciona para 1-2 imágenes.
- Para varias, usá Opción A.

---

## 6. Cómo construyo el `.pptx`

Cuando me pases los materiales:

1. Activo la skill `pptx` (es una capability que tengo).
2. Genero `docs/slides/presentacion.pptx` con la estructura de 8 slides.
3. Inserto las imágenes/screenshots en sus slides correspondientes.
4. Dibujo los diagramas faltantes (sección B) directo en PPTX.
5. Exporto a PDF (`docs/slides/presentacion.pdf`).
6. Commit + push al repo.

**Tiempo estimado:** 1-2 horas la primera versión, más iteraciones según tus comentarios.

---

## 7. Estética / convenciones

- **Paleta:** sobria, profesional. Sugiero **azul oscuro + blanco + acentos en naranja** (los colores de PostgreSQL y de un Uber genérico).
- **Tipografía:** sans-serif (Helvetica / Arial / Calibri — algo seguro y legible desde el fondo del aula).
- **Tamaños:** títulos ~36pt, contenido ~22pt mínimo (para que se lea proyectado).
- **Sin emojis** en las slides finales (para tono formal).
- **Footer en cada slide:** nombre del TP + nombre del integrante que presenta esa slide (opcional, ayuda a no olvidar el turno).

---

## 8. Mitigación de riesgos

Ya está en `docs/presentacion.md §6`. Resumido para el contexto del pptx:

| Riesgo | Mitigación |
|---|---|
| El `.pptx` no abre en la laptop del aula | Llevar el PDF + acceso al repo desde el navegador |
| Las imágenes se ven pixeladas en el proyector | Capturar todas en ≥1920×1080 |
| Falta alguna captura el día del demo | Tener el doc `docs/justificacion-der.md` impreso como backup |
| Los logos descargados son baja resolución | Buscar versiones SVG cuando sea posible |

---

## 9. Checklist final (a marcar antes de la defensa)

- [ ] Las 8 slides están armadas y revisadas por el equipo.
- [ ] La imagen del DER original es nítida (no pixelada).
- [ ] Los 5 screenshots de cloud consoles están en las slides correspondientes.
- [ ] El screenshot del grafo Neo4j (Q6) está en la slide 7 o como parte de la sección de casos.
- [ ] Los diagramas redibujados (patrón arquitectónico + finalizar viaje) están claros y se entienden a 3 metros.
- [ ] La tabla de cambios E1-E5 cabe en una sola slide y se lee.
- [ ] Cada integrante sabe qué slides le toca presentar.
- [ ] El `.pptx` se cargó en la laptop principal + USB backup.
- [ ] El `.pdf` está en una pestaña abierta del navegador.
- [ ] La carpeta `docs/slides/assets/` está commiteada al repo para que cualquiera tenga las fuentes.
