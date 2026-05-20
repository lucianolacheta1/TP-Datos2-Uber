# Plan de presentación — TP Uber

> Documento específico para la defensa del TP frente al profesor.
> Audiencia: equipo (para preparar y ensayar).
> Última actualización: 2026-05-19

## Base sobre la cual se construye este plan

El profesor explicitó en el video de presentación qué espera ver:

> *"Recuerden que ustedes van a tener que mostrar primero el DER... y qué modificaciones hicieron... segundo, hacer este tipo de presentación... no les voy a evaluar código... lo que sí me interesa ver es esto, cómo interactúan las bases de datos entre sí."*

Todo el plan se ordena alrededor de esa premisa: **demostrar interacción entre bases**.

---

## 1. Estructura general (15-20 min)

| Tiempo | Bloque | Qué mostrar |
|---|---|---|
| 0:00-2:00 | **Apertura** | Contexto del TP + integrantes + alcance |
| 2:00-5:00 | **DER + modificaciones** | DER original (Uber.pdf) + cambios E1-E5 justificados |
| 5:00-7:00 | **Stack y arquitectura** | Las 5 bases + por qué cada una + patrón "Postgres mínimo + NoSQL operativas" |
| 7:00-9:00 | **Mapeo de casos de uso → base** | Tabla de los 7 casos + qué base resuelve cada uno |
| 9:00-15:00 | **🎯 DEMO EN VIVO** | El bloque crítico — interacción entre bases |
| 15:00-17:00 | **Casos de uso ejecutados** | Correr los 7 casos sobre datos cargados durante el demo |
| 17:00-19:00 | **Cierre** | Lecciones aprendidas + preguntas |

---

## 2. Demo en vivo — guion paso a paso

Es **el corazón** de la presentación. Está diseñado para que cada acción del usuario muestre escrituras en múltiples bases en simultáneo.

### 2.1 Setup previo a entrar al aula

- Tener **5 ventanas abiertas en simultáneo** (una por cada cliente de DB):
  - pgAdmin / DBeaver → Postgres
  - MongoDB Compass → Mongo
  - Astra UI → Cassandra
  - Neo4j Browser → Neo4j
  - RedisInsight → Redis
- Consola con la app corriendo en otra ventana.
- Bases recién limpias (correr `scripts/reset_all_dbs.py` antes de empezar).

### 2.2 Guion del demo

`G:` = qué decir / hacer, `Q:` = qué señalar en pantalla, `💡` = comentario clave para el profesor.

```
G1: "Voy a registrar un usuario nuevo, Diego, en la plataforma"
    → Menu opción 1 → diego@mail.com / 1234 / Diego Pérez
Q1: ✅ Postgres muestra fila en `usuario`
    ✅ Neo4j Browser: MATCH (u:Usuario {email:"diego@..."}) RETURN u
        → aparece el nodo

G2: "Ahora hago login con ese usuario"
    → Menu opción 2 → mismas credenciales
Q2: ✅ Redis muestra `session:abc...` con TTL 600 segundos
    ✅ Mongo `login_history` muestra el evento LOGIN_OK
💡 "Acá ya hay tres bases interactuando: Postgres validó el password,
   Redis guardó la sesión con TTL, Mongo registró la auditoría"

G3: "Registro un conductor y un vehículo"
    → conductor: ana@mail.com / Ana Gómez / licencia 12345
    → vehículo: ABC123D / Toyota Corolla 2020 azul sedán
Q3: ✅ Postgres: filas en `conductor` y `vehiculo`
    ✅ Neo4j: nodos + arista (:Conductor)-[:MANEJA]->(:Vehiculo)

G4: "El usuario solicita un viaje al conductor"
    → Menu opción → seleccionar Diego como pasajero, Ana como conductor
Q4: ✅ Mongo `viajes` muestra el documento con snapshots
💡 "Los snapshots se obtuvieron consultando Postgres
   — bases distintas trabajando juntas en una sola operación"

G5: "El viaje se inicia y comienza a reportar ubicaciones"
    → Iniciar viaje + activar simulador de GPS
Q5: ✅ Cassandra `ubicaciones_por_vehiculo` se llena cada 2s
    ✅ Redis `vehiculo:{id}:pos` se actualiza con TTL de 30s
💡 "Cassandra guarda el histórico completo, Redis solo el último latido
   — paradigmas complementarios"

G6: "Se finaliza el viaje"
    → Menu finalizar viaje, distancia 8 km, duración 22 min
Q6: ✅ Mongo `viajes` actualizado: estado=FINALIZADO, ts_fin
    ✅ Cassandra `ultima_actividad_conductor` actualizada
    ✅ Cassandra `viajes_finalizados_por_dia` con entrada nueva
    ✅ Neo4j: MATCH (u)-[r:VIAJÓ_CON]->(c) RETURN r.cantidad_viajes = 1
💡 "Una sola acción del usuario disparó escritura en 4 bases simultáneas"

G7: "Se procesa el pago"
    → Tarjeta, $2500
Q7: ✅ Mongo `pagos` muestra el documento

G8: "El usuario deja una reseña al conductor"
    → 5 estrellas, "excelente viaje"
Q8: ✅ Mongo `resenas` con tipo=U_A_C
    ✅ Postgres: `conductor.rating_promedio` recalculado
    ✅ Neo4j: nodo `:Conductor` con `rating` actualizado
    ✅ Redis: `cache:top3_resenadores` invalidado (DEL)

G9: "Hago logout y muestro que la sesión se cae al expirar"
    → Logout manual o esperar TTL
Q9: ✅ Redis: `session:abc...` desaparece
```

---

## 3. Ejecución de los 7 casos de uso

Después del flujo principal, correr los 7 casos en el orden del enunciado. Para cada uno:

1. **Decir cuál es** el caso de uso.
2. **Decir qué base lo resuelve** y por qué.
3. **Ejecutar** la opción del menú.
4. **Mostrar el resultado**.
5. **Mostrar la query** en el cliente nativo de la base (Mongo Compass, Neo4j Browser, etc.) para que vean que efectivamente vino de ahí.

| # | Caso | Base | Tip de demo |
|---|---|---|---|
| 1 | Top 3 reseñadores | Mongo aggregate | — |
| 2 | Método de pago menos usado | Mongo aggregate | — |
| 3 | Conductores inactivos | Cassandra query | — |
| 4 | Tiempo promedio viajes | Cassandra | — |
| 5 | Coincidencias >1 viaje | Neo4j Cypher | ⭐ **Mostrar el grafo visual en Neo4j Browser** — es el "wow moment" |
| 6 | Toyota patente D | Neo4j Cypher | — |
| 7 | Rating 5 o <2 | Mongo find | — |

---

## 4. Bloque opcional: resiliencia (si sobra tiempo o si el profesor pregunta)

Demuestra el patrón **write-through best-effort + consistencia eventual** descrito en `docs/diseno.md` sección 6.

- **Cortar manualmente la conexión a Neo4j** y crear un viaje → la app no se rompe, se loguea el fallo en el outbox.
- **Volver a conectar Neo4j** y correr la **reconciliación** → la arista se reconstruye desde Mongo.
- **Mostrar el log** del outbox con los fallos parciales recuperados.

---

## 5. Slides (estructura sugerida — 8 slides)

| # | Slide | Contenido |
|---|---|---|
| 1 | Portada | Título + integrantes + cátedra + fecha |
| 2 | Contexto | Qué es el TP + requisito clave (interacción entre bases) |
| 3 | DER original + cambios | Captura del Uber.pdf + tabla con E1-E5 |
| 4 | Stack tecnológico | Logo/nombre de las 5 bases + tipo + hosting cloud |
| 5 | Arquitectura | Diagrama del patrón "Postgres mínimo + NoSQL operativas" |
| 6 | Mapeo casos → base | Tabla con los 7 casos y la base que los resuelve |
| 7 | Flujo de datos | Diagrama del "finalizar viaje" tocando 4 bases (de `diseno.md` sección 6.5) |
| 8 | Cierre | Aprendizajes + agradecimiento + preguntas |

**Formato:** simple, mucho diagrama, poco texto. Cada slide debe entenderse en 10 segundos.

---

## 6. Mitigación de riesgos durante la presentación

| Riesgo | Mitigación |
|---|---|
| **Cae internet en la facultad** | Tener videos cortos pre-grabados del demo como respaldo |
| **Una base cloud está caída** | Tener Docker local de respaldo o screenshots con timestamps reales |
| **Algún caso de uso devuelve vacío por mala distribución de datos** | Correr `seed_data.py` previamente y verificar manualmente cada caso |
| **Demo en vivo se traba o crashea** | Tener un script `demo_automatico.py` que ejecuta el guion sin interacción |
| **Profesor pide ver código** | Tener el repo abierto en otra pestaña, navegable, con README claro |

---

## 7. Checklist el día anterior

- [ ] Las 5 bases cloud están accesibles desde la laptop que se va a usar.
- [ ] `seed_data.py` corrió y los 7 casos devuelven resultados no-vacíos.
- [ ] Slides exportadas a PDF (por si PowerPoint falla).
- [ ] `docs/justificacion-der.md` impreso o accesible offline.
- [ ] Demo ensayado completo al menos 2 veces de principio a fin.
- [ ] Cargador, mouse, adaptador HDMI/VGA, agua.

---

## 8. Lecciones aprendidas (para el cierre)

Bullets que pueden cerrar la presentación:

- La **diversidad de paradigmas** (relacional + documental + columnar + grafo + key-value) permite que cada base resuelva lo que mejor sabe.
- **Mantener consistencia entre bases sin transacciones distribuidas** requiere un patrón explícito (write-through + reconciliación).
- **Postgres no debe forzarse a hacer lo que las NoSQL hacen mejor**, ni viceversa.
- La **flexibilidad de Mongo** resolvió naturalmente el polimorfismo de Reseña que era ambiguo en SQL.
- El caso de uso 5 (coincidencias) ilustra cómo un problema "feo" en SQL se vuelve **trivial en un grafo**.

---

## 9. Pendientes de preparación

Ver `docs/tareas.md`, Fase 8.
