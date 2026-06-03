-- DDL inicial de Postgres para el TP Uber
-- Ejecutar una sola vez al inicio del proyecto.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS usuario (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           VARCHAR(255) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  nombre          VARCHAR(255) NOT NULL,
  telefono        VARCHAR(50),
  foto_url        VARCHAR(500),
  rating_promedio FLOAT DEFAULT 0,
  fecha_registro  TIMESTAMP DEFAULT NOW(),
  estado          VARCHAR(20) CHECK (estado IN ('ACTIVO','SUSPENDIDO','BAJA'))
                  DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS conductor (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           VARCHAR(255) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  nombre          VARCHAR(255) NOT NULL,
  telefono        VARCHAR(50),
  nro_licencia    VARCHAR(50) UNIQUE NOT NULL,
  rating_promedio FLOAT DEFAULT 0,
  estado          VARCHAR(20) CHECK (estado IN ('ACTIVO','SUSPENDIDO','BAJA'))
                  DEFAULT 'ACTIVO',
  fecha_registro  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehiculo (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conductor_id UUID REFERENCES conductor(id) ON DELETE CASCADE,
  placa        VARCHAR(20) UNIQUE NOT NULL,
  marca        VARCHAR(50) NOT NULL,
  modelo       VARCHAR(50) NOT NULL,
  anio         INT,
  color        VARCHAR(30),
  tipo         VARCHAR(30)
);

CREATE INDEX IF NOT EXISTS idx_vehiculo_conductor ON vehiculo(conductor_id);
CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuario(email);
CREATE INDEX IF NOT EXISTS idx_conductor_email ON conductor(email);
