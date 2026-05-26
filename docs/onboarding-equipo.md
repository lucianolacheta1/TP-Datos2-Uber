# Guía de onboarding — TP Uber (Datos 2)

> Esta guía es para los integrantes del equipo que se suman al proyecto.
> Te toma **~30 minutos** dejar todo funcionando.

¡Hola! Te sumás al TP de **Datos 2 (UADE)**: un sistema tipo Uber que integra 5 bases de datos en la nube. Acá tenés todo lo que necesitás para empezar a trabajar.

---

## 📋 Lo que vas a hacer

| Paso | Qué | Tiempo |
|---|---|---|
| 1 | Crear 3 cuentas con tu email @uade.edu.ar | 10 min |
| 2 | Aceptar 3 invitaciones que te van a llegar por mail | 5 min |
| 3 | Clonar el repo y armar el proyecto Python en tu máquina | 15 min |
| 4 | Verificar que las 5 bases responden con el health check | 1 min |

---

## Paso 1 — Crear las cuentas con `@uade.edu.ar`

Las **3 plataformas** abajo te van a llegar invitación por mail. Para que la invitación funcione, **tenés que tener una cuenta creada con tu email @uade.edu.ar exacto**.

**Importante:** usá el mismo email en las 3 plataformas, así no te marés.

### 1.1. MongoDB Atlas

- Andá a: https://www.mongodb.com/cloud/atlas/register
- Registrate con tu email **@uade.edu.ar**.
- Te va a pedir un formulario corto ("qué vas a construir"). Respondé cualquier cosa, no importa.
- Cuando llegues al dashboard, **no crees ningún cluster** — vas a recibir invitación al cluster del equipo.

### 1.2. DataStax Astra

- Andá a: https://astra.datastax.com
- Click en **Sign Up** → registrate con email **@uade.edu.ar**.
- Verificá el email si te lo pide.
- Cuando llegues al dashboard, **no crees ninguna DB** — vas a recibir invitación a la del equipo.

### 1.3. Redis Cloud

- Andá a: https://redis.io/try-free
- Click en **Sign Up** → registrate con email **@uade.edu.ar**.
- Cuando llegues al dashboard, **no crees ninguna database** — vas a recibir invitación.

> ⚠️ **NO tenés que crear cuentas en** Neon (Postgres) ni Neo4j Aura. Esas dos plataformas no permiten invitaciones en su tier gratuito. El acceso a esas DBs lo vas a tener vía las credenciales del archivo `.env` (paso 3).

#### Cómo acceder a Neo4j desde la web (sin cuenta de Aura)

Si querés inspeccionar el grafo visualmente:

1. Andá a https://workspace.neo4j.io
2. Login con cualquier cuenta (Google o email — es independiente de Aura).
3. Una vez adentro, **"Connect to instance"** → **"Add connection"**.
4. Pegá:
   - **Connection URL:** el `NEO4J_URI` del `.env`.
   - **Username:** el `NEO4J_USER` del `.env` (importante: es el instance ID, NO `neo4j`).
   - **Password:** el `NEO4J_PASSWORD` del `.env`.
5. Click **Connect**.

Vas a ver la misma DB que el resto del equipo.

#### Cómo acceder a Postgres (Neon) desde un cliente

Igual que con Neo4j, no necesitás una cuenta de Neon. Usá un cliente local como **DBeaver** (https://dbeaver.io, gratis) o **pgAdmin**:

1. Instalá DBeaver.
2. Nueva conexión → **PostgreSQL**.
3. Pegá el `POSTGRES_URL` del `.env` o partilo en sus componentes (host, port, database, user, password).
4. Conectá.

---

## Paso 2 — Aceptar las invitaciones

En los próximos minutos te van a llegar **3 emails** con invitaciones de los siguientes remitentes:

- MongoDB Atlas: `noreply@mongodb.com`
- DataStax Astra: `noreply@datastax.com`
- Redis Cloud: `noreply@redis.com` (o similar)

Para cada uno:
1. Abrí el mail.
2. Click en el botón de aceptar invitación.
3. Te lleva a la plataforma → confirma con tu cuenta ya creada.
4. Listo.

Una vez aceptadas, vas a ver en tu dashboard de cada plataforma:
- Atlas: cluster **`UADE-ID2-UBER`**.
- Astra: database **`UADE_ID2_UBER`** con keyspace `uber_tp`.
- Redis Cloud: subscription con la database **`UADE-ID2-UBER`**.

---

## Paso 3 — Setup local del proyecto

### 3.1. Pre-requisitos

- **Python 3.11+** instalado. Verificá con: `python --version` (en algunos sistemas es `python3`).
  - Si no lo tenés: https://www.python.org/downloads/ → descargá la última versión.
  - En la instalación, marcá la opción **"Add Python to PATH"**.
- **Git** instalado. Verificá con: `git --version`.
  - Si no lo tenés: https://git-scm.com/downloads.

### 3.2. Clonar el repo

Elegí una carpeta donde quieras tener el proyecto (ej: `Documents/proyectos/`) y abrí una terminal ahí:

```bash
git clone https://github.com/lucianolacheta1/TP-Datos2-Uber.git
cd TP-Datos2-Uber
```

### 3.3. Pedir el `.env` y el bundle de Cassandra

Estos 2 archivos **no están en el repo** (tienen credenciales sensibles). Pedíselos a Luciano (o al integrante que te invitó) por canal privado (WhatsApp, Drive con permiso restringido, etc.):

| Archivo | Dónde ponerlo |
|---|---|
| `.env` | En la raíz del repo clonado (al lado de `README.md`) |
| `secure-connect-uade-id2-uber.zip` | Una carpeta tuya **fuera del repo**, ej: `C:\Users\<vos>\secrets\` |

### 3.4. Editar el path del bundle en tu `.env`

Una vez que tengas el `.env`, abrilo con un editor y buscá esta línea:

```
ASTRA_BUNDLE_PATH=C:\Users\lucia\UADE\datos2\secure-connect-uade-id2-uber.zip
```

**Cambiala** por el path donde guardaste el `.zip` en TU máquina. Ejemplos:

- Windows: `ASTRA_BUNDLE_PATH=C:\Users\juan\secrets\secure-connect-uade-id2-uber.zip`
- Mac/Linux: `ASTRA_BUNDLE_PATH=/home/juan/secrets/secure-connect-uade-id2-uber.zip`

### 3.5. Crear el entorno virtual e instalar dependencias

Desde la raíz del repo (con la terminal):

```bash
python -m venv venv
```

**Activar el venv** (depende de tu shell):

- **Windows PowerShell:** `.\venv\Scripts\Activate.ps1`
- **Windows Git Bash:** `source venv/Scripts/activate`
- **Mac/Linux:** `source venv/bin/activate`

> Si en PowerShell te da error de execution policy, corré una sola vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

Después de activado vas a ver `(venv)` al inicio del prompt. Ahora:

```bash
pip install -r requirements.txt
```

Tarda ~1-2 minutos.

---

## Paso 4 — Verificar conexiones

```bash
python -m scripts.check_connections
```

**Resultado esperado:**

```
Validando .env...
OK

Verificando conexiones a las bases:
  [OK  ] Postgres   (Neon)
  [OK  ] MongoDB    (Atlas)
  [OK  ] Cassandra  (Astra)
  [OK  ] Neo4j      (Aura)
  [OK  ] Redis      (Cloud)

Todas las bases respondieron correctamente.
```

Si las 5 dan OK, ya estás listo para programar. 🎉

---

## 🆘 Si algo no funciona

### "Variables de entorno faltantes en .env"

Tu `.env` no tiene todas las variables. Comparalo con `.env.example` (que sí está en el repo) y completá las que faltan con los valores que te pasó Luciano.

### "Could not open secure connect bundle" (Cassandra)

El path en `ASTRA_BUNDLE_PATH` no apunta a tu `.zip`. Verificá:
- Que el `.zip` exista en esa ubicación exacta (sin typos).
- Que sea el path absoluto, no relativo.

### "Authentication failed" en Neo4j

⚠️ **Conocido:** en AuraDB Free reciente, el `NEO4J_USER` **NO es** `"neo4j"` sino el **instance ID** (los 8 caracteres del subdominio del URI). El `.env` que te pasaron ya debería tenerlo correcto, pero si te lo configuraste vos por error, verificá.

### "Unable to load a default connection class" (Cassandra)

Si estás en Python 3.12+, instalá:
```bash
pip install pyasyncore
```
(Ya está en `requirements.txt`, pero por si te lo salteaste).

### Algún FAIL que no entiendo

Copiá el output completo y pasáselo a Luciano por el canal del grupo. Lo debugueamos juntos.

---

## 📚 ¿Y ahora qué?

Una vez que tengas las 5 OK:

1. Leé el **`CLAUDE.md`** en la raíz del repo — es la memoria del proyecto.
2. Leé **`docs/diseno.md`** — diseño técnico completo (modelo de datos, flujos, arquitectura).
3. Mirá **`docs/tareas.md`** — el roadmap del proyecto por fases. Las fases ya completadas están con `[x]`.
4. Mirá los **planes de implementación** (`docs/plan-XX-*.md`) según en qué fase estemos trabajando.
5. Coordiná con el equipo qué parte vas a tomar.

¡Bienvenido al proyecto! 🚖
