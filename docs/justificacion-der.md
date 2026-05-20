# Justificación de modificaciones al DER

> Documento para la presentación. Audiencia: **profesor**.
> Fecha: 2026-05-19

## Resumen ejecutivo

El DER original recibido se respeta en su modelo **conceptual** (entidades y relaciones de negocio). Las modificaciones se dividen en dos categorías:

| Categoría | Cantidad | Naturaleza |
|---|---|---|
| **Correcciones al DER conceptual** | 5 cambios (E1-E5) | Resuelven ambigüedades, restricciones faltantes o errores de modelado |
| **Decisiones de implementación física** | 4 mapeos a bases | El DER conceptual se "reparte" entre las 5 bases según el patrón de acceso |

> **Nota conceptual:** Un DER es un modelo conceptual de entidades y relaciones, **independiente** del motor de almacenamiento. Que una entidad del DER se materialice en MongoDB o en PostgreSQL es una decisión de **modelado físico**, no una modificación al DER. Sin embargo, se documentan ambas categorías por completitud.

---

## A. Correcciones al DER conceptual

### E1 — Polimorfismo en `RESEÑA.autor` / `RESEÑA.destinatario` (ERROR DE MODELADO)

**Problema:** El DER original define `RESEÑA.autor_id` y `RESEÑA.destinatario_id` como claves foráneas que pueden apuntar **indistintamente** a `USUARIO` o a `CONDUCTOR`. Esto es **estructuralmente incorrecto** en un DER: una FK no puede ser polimórfica.

**Solución adoptada (Opción 3):** Una sola entidad `RESEÑA` con:
- Dos FKs explícitas: `usuario_id` (apunta a USUARIO) + `conductor_id` (apunta a CONDUCTOR)
- Un atributo discriminador `tipo` ∈ {`U_A_C`, `C_A_U`} que indica el sentido de la reseña

> **Nota de implementación física (Mongo):** el documento almacena la entidad como `autor: {id, nombre}` y `destinatario: {id, nombre}` (denormalizado para acceso rápido). El mapping es: si `tipo = 'U_A_C'`, entonces `autor.id ≡ usuario_id` y `destinatario.id ≡ conductor_id`; y al revés cuando `tipo = 'C_A_U'`. Ver `diseno.md §4.2` para el detalle.

**Alternativas descartadas:**
- *Opción 1 (supertipo PERSONA con subtipos USUARIO/CONDUCTOR):* más elegante pero implica un refactor mayor del DER y la pérdida del modelo simple original.
- *Opción 2 (dos entidades separadas RESEÑA_PASAJERO_A_CONDUCTOR y RESEÑA_CONDUCTOR_A_PASAJERO):* duplica esquema y complica las queries del caso de uso 1 y 7.

### E2 — Cardinalidad `CONDUCTOR (1) — (1..*) VEHICULO`

**Problema:** La cardinalidad mínima de `1..*` obliga a que todo conductor tenga **al menos un** vehículo. En la práctica, un conductor puede registrarse antes de cargar su auto, dejando un estado inválido transitorio.

**Solución:** cambiar a `CONDUCTOR (1) — (0..*) VEHICULO`.

### E3 — Restricción `UNIQUE` en `email` no expresada

**Problema:** El DER no marca `email` como único, lo que permitiría dos cuentas con el mismo email.

**Solución:** agregar la restricción de unicidad explícita en `USUARIO.email` y `CONDUCTOR.email`. También en `CONDUCTOR.nro_licencia` y `VEHICULO.placa`.

### E4 — Atributos `estado` sin dominio definido

**Problema:** Los atributos `estado` en `USUARIO`, `CONDUCTOR`, `VIAJE` y `PAGO` están tipados como `VARCHAR` libre, lo que permite cualquier string y es propenso a errores de tipeo.

**Solución:** definir dominios enumerados explícitos:

| Entidad | Dominio de `estado` |
|---|---|
| USUARIO | { ACTIVO, SUSPENDIDO, BAJA } |
| CONDUCTOR | { ACTIVO, SUSPENDIDO, BAJA } |
| VIAJE | { PENDIENTE, EN_CURSO, FINALIZADO, CANCELADO } |
| PAGO | { PENDIENTE, APROBADO, RECHAZADO, REEMBOLSADO } |

Implementación: `CHECK constraints` en Postgres y validación en la capa de aplicación.

### E5 — `VIAJE.duracion_min` es atributo derivado

**Problema:** `duracion_min` puede calcularse como `ts_fin - ts_inicio`, por lo que es un atributo **derivado** y no almacenado primario.

**Solución:** mantenerlo almacenado por razones de performance (acelera el caso de uso 4 "tiempo promedio de viajes") pero **marcarlo en el DER con el prefijo `/`** (notación estándar para atributos derivados).

---

## B. Decisiones de implementación física

Las siguientes son decisiones de **modelado físico**: el DER conceptual se materializa en distintos motores de almacenamiento según el patrón de acceso de cada entidad.

### M1 — Reseñas se almacenan en **MongoDB**

**Justificación:**
- La entidad RESEÑA tiene relaciones polimórficas (autor/destinatario pueden ser USUARIO o CONDUCTOR). MongoDB modela esto naturalmente con documentos flexibles.
- Permite enriquecer cada reseña con contexto del viaje (snapshot de origen, destino, duración) sin joins ni migraciones.
- Los casos de uso 1 (top 3 reseñadores) y 7 (rating extremo) son agregaciones que MongoDB resuelve eficientemente.

### M2 — Ubicaciones GPS se almacenan en **Cassandra**

**Justificación:**
- Las ubicaciones son **time-series de alta frecuencia**: cada vehículo activo escribe coordenadas cada N segundos.
- Cassandra está diseñada exactamente para este patrón (write-heavy, particionado por entidad).
- Postgres se vuelve un cuello de botella para este volumen de escrituras.
- La clave de partición `(vehiculo_id, ts)` permite consultas eficientes del histórico de un vehículo.

### M3 — Relaciones usuario-conductor se proyectan en **Neo4j**

**Justificación:**
- El caso de uso 5 ("pasajero-conductor con más de 1 viaje en común") es un problema clásico de **relaciones N:M con peso**.
- En Postgres se resuelve con `GROUP BY ... HAVING COUNT(*) > 1`, que tiene complejidad O(viajes).
- En Neo4j se modela como una arista `[:VIAJO_CON]` con propiedad `cantidad_viajes`, lectura en O(1).
- Los vehículos también se modelan como nodos para resolver el caso de uso 6 (filtro por marca + patrón en placa).

### M4 — Sesiones, posiciones actuales y caché en **Redis**

**Justificación:**
- Las sesiones de login con expiración automática son el caso de uso textbook de Redis con TTL (idéntico al ejemplo mostrado por el profesor en el video).
- La última posición conocida de cada vehículo se mantiene en Redis para lecturas sub-milisegundo en el matching de viajes (Cassandra retiene el histórico completo).
- Las queries pesadas (caso de uso 1 con `aggregate` en Mongo) se cachean en Redis con TTL corto.

---

## C. Síntesis: distribución final de entidades por base

| Entidad del DER | Materialización física | Rol |
|---|---|---|
| `USUARIO` | PostgreSQL (`usuario`) + nodo `(:Usuario)` en Neo4j | Identidad |
| `CONDUCTOR` | PostgreSQL (`conductor`) + nodo `(:Conductor)` en Neo4j | Identidad |
| `VEHICULO` | PostgreSQL (`vehiculo`) + nodo `(:Vehiculo)` en Neo4j | Catálogo de activos |
| `VIAJE` | MongoDB (`viajes`) + proyección en Cassandra (`viajes_finalizados_por_dia`) | Operacional |
| `PAGO` | MongoDB (`pagos`) | Operacional |
| `RESEÑA` | MongoDB (`resenas`) | Operacional |
| `UBICACION` | Cassandra (`ubicaciones_por_vehiculo`) + última en Redis | Time-series |

---

## D. Garantía de consistencia entre bases

Cuestión central de la materia: **las bases deben interactuar y mantener consistencia**.

- **Source of truth** definido por dato (sección 6.2 del documento de diseño).
- **Patrón write-through best-effort**: cada escritura se propaga a las bases derivadas; los fallos se loguean en un outbox.
- **Reconciliación periódica**: un job compara conteos entre bases (ej. cantidad de viajes en Mongo vs aristas en Neo4j) y reconstruye las derivadas desde el SOT si hay drift.
- Detalle en el documento de diseño técnico, sección 6.
