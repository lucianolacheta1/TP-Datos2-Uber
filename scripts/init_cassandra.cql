-- DDL inicial de Cassandra (Astra) para el TP Uber
-- Ejecutar en CQL Console (usar keyspace uber_tp).

CREATE TABLE IF NOT EXISTS ubicaciones_por_vehiculo (
  vehiculo_id UUID,
  ts          TIMESTAMP,
  lat         DECIMAL,
  lon         DECIMAL,
  precision_m FLOAT,
  viaje_id    UUID,
  PRIMARY KEY (vehiculo_id, ts)
) WITH CLUSTERING ORDER BY (ts DESC);

CREATE TABLE IF NOT EXISTS ultima_actividad_conductor (
  conductor_id    UUID PRIMARY KEY,
  ultimo_viaje_ts TIMESTAMP,
  ultimo_viaje_id UUID
);

CREATE TABLE IF NOT EXISTS viajes_finalizados_por_dia (
  dia          DATE,
  viaje_id     UUID,
  conductor_id UUID,
  usuario_id   UUID,
  duracion_min INT,
  distancia_km FLOAT,
  PRIMARY KEY (dia, viaje_id)
);
