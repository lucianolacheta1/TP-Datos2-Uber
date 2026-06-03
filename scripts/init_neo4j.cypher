// ============================================================================
// init_neo4j.cypher  -  Constraints e indices iniciales del grafo (TP Uber)
// ============================================================================
//
// Base: Neo4j Aura (capa de grafo de coincidencias).
// Ejecutar UNA sola vez al inicializar la base, desde Neo4j Workspace (Query)
// o Neo4j Browser. Cada sentencia se corre de a una; todas usan IF NOT EXISTS,
// asi que volver a correrlas es idempotente (no falla si ya existen).
//
// Modelo de datos (ver docs/diseno.md S4.4):
//   (:Usuario   {id, nombre, email})
//   (:Conductor {id, nombre, email, rating})
//   (:Vehiculo  {id, placa, marca, modelo, anio, color, tipo})
//   (:Conductor)-[:MANEJA]->(:Vehiculo)
//   (:Usuario)-[:VIAJO_CON {cantidad_viajes, ultimo_viaje_ts}]->(:Conductor)
// ============================================================================


// --- Constraints de unicidad sobre los ids -------------------------------- //
//
// El id de cada nodo es el MISMO UUID que genera Postgres (source of truth de
// la identidad, ADR-005). grafo_repo crea/actualiza nodos con MERGE por id
// (ej: MERGE (u:Usuario {id: $id})). Una constraint UNIQUE cumple dos roles:
//   1) Garantiza idempotencia: el write-through best-effort y el job de
//      reconciliacion (docs/diseno.md S6.3 y S6.4) corren MERGE muchas veces;
//      la unicidad evita nodos duplicados para un mismo id.
//   2) Performance: la constraint crea por debajo un indice de respaldo, asi
//      el MERGE por id resuelve con index seek en vez de un full label scan.

CREATE CONSTRAINT usuario_id_unique   IF NOT EXISTS FOR (u:Usuario)   REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT conductor_id_unique IF NOT EXISTS FOR (c:Conductor) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT vehiculo_id_unique  IF NOT EXISTS FOR (v:Vehiculo)  REQUIRE v.id IS UNIQUE;


// --- Indices para el caso de uso 6 ---------------------------------------- //
//
// Caso 6 (grafo_repo.vehiculos_marca_y_patente_termina): cuenta los vehiculos
// de una marca cuya patente termina en un sufijo dado. La query es:
//     MATCH (v:Vehiculo)
//     WHERE v.marca = $marca AND v.placa ENDS WITH $sufijo
//     RETURN count(v)
//
// vehiculo_marca: el predicado v.marca = $marca es una igualdad exacta, asi
//   que este indice lo resuelve con un seek y reduce el conjunto candidato
//   ANTES de evaluar el sufijo de la patente. Es el indice que mas acelera el
//   caso 6 (filtra por "Toyota" primero, despues chequea la patente).
//
// vehiculo_placa: sirve para busquedas por patente exacta y por prefijo
//   (= y STARTS WITH). Nota honesta: un indice de rango NO acelera el
//   "ENDS WITH" (sufijo) del caso 6 -- ese matcheo se evalua sobre los nodos
//   que ya filtro vehiculo_marca. Se incluye igual porque la patente es un
//   identificador natural del vehiculo (UNIQUE en Postgres) y habilita
//   lookups eficientes por placa a futuro.

CREATE INDEX vehiculo_marca IF NOT EXISTS FOR (v:Vehiculo) ON (v.marca);
CREATE INDEX vehiculo_placa IF NOT EXISTS FOR (v:Vehiculo) ON (v.placa);
