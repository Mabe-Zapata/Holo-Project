# Holo: Docker y Docker Compose

Nov 14, 2026 · @Maria Zapata

Guía para María Belén, responsable de la tarea BE-01, que explica qué es Docker y cómo crear el archivo `docker-compose.yml` que levanta la base de datos PostgreSQL de Holo para todo el equipo.

## Qué es Docker y por qué Holo lo usa

Docker permite ejecutar un programa, junto con todo lo que necesita, dentro de un contenedor aislado del resto del computador. Con él, los nueve integrantes del equipo usan exactamente la misma base de datos, sin instalarla ni configurarla a mano, y sin el clásico problema de que "en mi máquina funciona".

En Holo, Docker se usa solo para la base de datos: PostgreSQL 16 con la extensión pgvector, que además servirá para guardar y buscar el material del asistente. El backend (FastAPI) y la aplicación (Flutter) se siguen ejecutando directamente en cada computador.

Esto implica un cambio respecto al plan inicial, que usaba SQLite: se adelanta PostgreSQL, que estaba previsto para la versión 1. A cambio, todos aprenden la herramienta que el proyecto usará después, y borrar o recrear la base es cuestión de un comando.

## Conceptos básicos

| Concepto | Qué es | En Holo |
| --- | --- | --- |
| Imagen | Plantilla de solo lectura con un programa y sus dependencias. | `pgvector/pgvector:pg16`: PostgreSQL 16 con pgvector ya instalado |
| Contenedor | Una imagen en ejecución; es desechable. | El contenedor `holo-db` |
| Volumen | Espacio de disco que Docker conserva aunque el contenedor se borre. | `holo_datos`, donde viven los datos de la base |
| Puerto | Puerta por la que el computador se comunica con el contenedor. | `5432` de PostgreSQL, publicado solo en `127.0.0.1` |
| Variable de entorno | Valor de configuración que se entrega al contenedor al iniciarlo. | Usuario, clave y nombre de la base |
| Docker Compose | Herramienta que describe en un archivo YAML uno o varios contenedores y los levanta con un comando. | `docker-compose.yml` |
| Docker Hub | Sitio público del que se descargan las imágenes. | De allí baja `pgvector/pgvector:pg16` |

La idea clave es que **el contenedor es desechable y el volumen no**: se puede borrar el contenedor sin perder datos, pero borrar el volumen elimina la base completa.

## Instalación y verificación

- **Windows 10 u 11.** Se instala Docker Desktop con el motor WSL 2 (el instalador lo propone). Requiere que la virtualización esté activada en la BIOS, algo que casi siempre ya lo está.
- **macOS.** Se instala Docker Desktop, eligiendo la versión para Apple Silicon o Intel según el equipo.
- **Linux.** Se instalan Docker Engine y el complemento de Compose desde la documentación oficial de la distribución; luego se agrega el usuario al grupo `docker` y se vuelve a iniciar sesión.

Docker Desktop es gratuito para uso personal y educativo; conviene confirmar las condiciones vigentes en su sitio oficial antes de instalarlo. Con la aplicación abierta, se verifica la instalación en una terminal:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

Si el último comando imprime un mensaje que comienza con "Hello from Docker!", todo funciona. Si dice que no puede conectarse al servicio de Docker, falta abrir Docker Desktop y esperar a que indique que está en ejecución.

## Creación del docker-compose.yml paso a paso

Todo se hace en la raíz del repositorio `Holo-project`, sobre una rama propia.

### 1. Crear la rama

```bash
git checkout develop
git pull
git checkout -b feature/BE-01-docker-base-datos
```

### 2. Crear el script de inicio

PostgreSQL ejecuta los archivos de la carpeta `/docker-entrypoint-initdb.d` la primera vez que arranca con un volumen vacío. Se usa para activar pgvector. Archivo `docker/init/01-extensiones.sql`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Crear el archivo docker-compose.yml

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: holo-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${HOLO_DB_USUARIO}
      POSTGRES_PASSWORD: ${HOLO_DB_CLAVE}
      POSTGRES_DB: ${HOLO_DB_NOMBRE}
    ports:
      - "127.0.0.1:${HOLO_DB_PUERTO:-5432}:5432"
    volumes:
      - holo_datos:/var/lib/postgresql/data
      - ./docker/init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  holo_datos:
```

Qué hace cada parte:

- `image` indica qué imagen descargar: PostgreSQL 16 con pgvector.
- `container_name` da un nombre fijo y fácil de recordar al contenedor.
- `restart: unless-stopped` lo reinicia si el computador se reinicia, salvo que se haya detenido a propósito.
- `environment` entrega usuario, clave y nombre de la base. Los valores se leen del archivo `.env`; no se escriben aquí.
- `ports` publica el puerto 5432 solo en `127.0.0.1`, es decir, solo accesible desde el propio computador y no desde la red. `${HOLO_DB_PUERTO:-5432}` usa 5432 salvo que se defina otro puerto.
- `volumes` conecta el volumen `holo_datos`, que conserva los datos, y la carpeta con el script de inicio, en modo de solo lectura (`ro`).
- `healthcheck` pregunta cada 5 segundos si la base está lista (`pg_isready`). El doble signo `$$` evita que Compose interprete la variable, de modo que la lea el contenedor.
- `volumes:` al final declara el volumen con nombre.

### 4. Validar el archivo

Los pasos 4 a 6 necesitan el archivo `.env` de la sección siguiente: créalo primero. Este comando verifica la sintaxis y muestra cómo quedan las variables ya sustituidas:

```bash
docker compose config
```

### 5. Levantar la base

```bash
docker compose up -d db
docker compose ps
```

La primera vez descarga la imagen, lo que puede tardar unos minutos. Cuando el estado del servicio dice `healthy`, la base está lista.

### 6. Comprobar que pgvector está activo

```bash
docker compose exec db psql -U holo -d holo -c "\dx"
```

La lista de extensiones debe incluir `vector`. Si usaste otro usuario o nombre en el `.env`, cámbialos en el comando.

## Variables de entorno y credenciales

La clave de la base no se escribe en `docker-compose.yml`, que se sube a GitHub. Se guarda en un archivo `.env` que **nunca** se sube. El repositorio incluye en cambio `.env.example`, una plantilla sin secretos que sí se sube y que cada integrante copia.

Archivo `.env.example` (se agregan estas líneas a las que ya existen):

```bash
HOLO_DB_USUARIO=holo
HOLO_DB_CLAVE=cambiar_esta_clave
HOLO_DB_NOMBRE=holo
HOLO_DB_PUERTO=5432
HOLO_URL_BASE_DATOS=postgresql+psycopg://holo:cambiar_esta_clave@localhost:5432/holo
```

Cada integrante lo copia y cambia la clave:

```bash
cp .env.example .env
```

En Windows PowerShell, el comando equivalente es `Copy-Item .env.example .env`.

Tres cuidados:

- Se confirma que `.env` está en `.gitignore` y que `git status` no lo muestra antes de hacer commit.
- Si se cambia la clave en `HOLO_DB_CLAVE`, también se cambia en `HOLO_URL_BASE_DATOS`: son el mismo dato escrito dos veces.
- Las variables de usuario, clave y nombre solo se aplican la primera vez que se crea el volumen. Para cambiarlas después hay que borrar el volumen (ver problemas frecuentes), lo que elimina los datos.

## Comandos del día a día

Todos se ejecutan en la raíz del repositorio `Holo-project`.

| Comando | Qué hace | Riesgo |
| --- | --- | --- |
| `docker compose up -d db` | Levanta la base en segundo plano. | Ninguno |
| `docker compose ps` | Muestra el estado del servicio. | Ninguno |
| `docker compose logs -f db` | Muestra el registro de la base en vivo; se sale con Ctrl+C. | Ninguno |
| `docker compose stop` | Detiene la base sin borrar nada. | Ninguno |
| `docker compose restart db` | Reinicia la base. | Ninguno |
| `docker compose down` | Detiene y elimina el contenedor, pero conserva el volumen con los datos. | Bajo |
| `docker compose down -v` | Elimina el contenedor y **el volumen: se pierden todos los datos**. | Alto |
| `docker compose exec db psql -U holo -d holo` | Abre una consola SQL dentro de la base. Se sale con `\q`. | Bajo |

Para hacer un respaldo de la base:

```bash
docker compose exec db pg_dump -U holo -d holo -f /tmp/respaldo.sql
docker compose cp db:/tmp/respaldo.sql ./respaldo.sql
```

El respaldo contiene datos y no se sube a GitHub: debe estar en `.gitignore`. Se hace en dos pasos porque la redirección `>` de PowerShell cambia la codificación del archivo.

## Conectar el backend con SQLAlchemy

El backend se conecta a la base con SQLAlchemy, una biblioteca que permite escribir consultas en Python y funciona igual con PostgreSQL y con SQLite. Esa compatibilidad es lo que permite que las pruebas automáticas usen una base en memoria sin Docker.

### 1. Agregar las dependencias

En `requirements.txt`:

```text
sqlalchemy>=2.0
psycopg[binary]>=3.2
```

### 2. Agregar la URL a la configuración

En la clase `Configuracion` de `app/core/config.py` se agrega un campo; el prefijo `HOLO_` hace que lea la variable `HOLO_URL_BASE_DATOS`:

```python
url_base_datos: str = "postgresql+psycopg://holo:cambiar_esta_clave@localhost:5432/holo"
```

### 3. Crear app/db.py

```python
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import Configuracion


def crear_motor(url: str | None = None) -> Engine:
    """Crea el motor de SQLAlchemy.

    En las pruebas se le pasa "sqlite:///:memory:" para no necesitar Docker.
    """
    if url is None:
        url = Configuracion().url_base_datos
    return create_engine(url, pool_pre_ping=True)


def verificar_conexion(motor: Engine) -> bool:
    """Devuelve True si la base responde."""
    with motor.connect() as conexion:
        return conexion.execute(text("SELECT 1")).scalar() == 1
```

### 4. Probar la conexión

Una prueba automática, que no necesita Docker, en `tests/test_db.py`:

```python
from app.db import crear_motor, verificar_conexion


def test_conexion_en_memoria():
    motor = crear_motor("sqlite:///:memory:")
    assert verificar_conexion(motor)
```

Y una verificación manual contra la base real, con el contenedor encendido y el entorno virtual activo:

```bash
python -c "from app.db import crear_motor, verificar_conexion; print(verificar_conexion(crear_motor()))"
```

Debe imprimir `True`. Si aparece un error de conexión, se revisa la sección de problemas frecuentes.

### 5. Lo que sigue en BE-01

El criterio de la tarea también pide que las tablas se creen al iniciar y que `almacen.py` sea una fachada con un método por repositorio. Eso se hace después de lo anterior, con las tablas del primer sprint (usuarios, consentimientos y mensajes), y se coordina con Damien, Álvaro y Jose, que escriben esos repositorios. El código de esta sección es una base de partida: debe revisarse y adaptarse al código existente del repositorio.

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| "Cannot connect to the Docker daemon" | Docker Desktop está cerrado o aún arrancando. | Abrir Docker Desktop y esperar a que indique que está en ejecución. |
| "WSL 2 installation is incomplete" (Windows) | Falta el componente de WSL 2. | Ejecutar `wsl --update` en una terminal como administrador y reiniciar. |
| Docker no inicia por virtualización | La virtualización está desactivada en la BIOS. | Activarla (suele llamarse Intel VT-x o SVM) y reiniciar. |
| "port is already allocated" o "address already in use" | Otro programa usa el puerto 5432, por ejemplo un PostgreSQL instalado antes. | Poner otro valor en `HOLO_DB_PUERTO` (por ejemplo 5433), ajustar el puerto en `HOLO_URL_BASE_DATOS` y volver a levantar. |
| "permission denied" al usar Docker (Linux) | El usuario no está en el grupo `docker`. | `sudo usermod -aG docker $USER` y volver a iniciar sesión. |
| "password authentication failed" | La clave del `.env` no coincide con la del volumen ya creado. | Usar la clave original, o borrar el volumen con `docker compose down -v` si no importa perder los datos, y volver a levantar. |
| "extension vector is not available" | Se usa una imagen sin pgvector, o el script de inicio no se ejecutó porque el volumen ya existía. | Verificar que la imagen es `pgvector/pgvector:pg16`; para activarla a mano: `docker compose exec db psql -U holo -d holo -c "CREATE EXTENSION IF NOT EXISTS vector;"`. |
| El backend dice "connection refused" | La base no está lista o el puerto de la URL no coincide con el publicado. | `docker compose ps` debe mostrar `healthy`; revisar el puerto en `HOLO_URL_BASE_DATOS`. |
| Docker consume mucha memoria | Docker Desktop reserva memoria para su máquina virtual. | Limitarla en Settings, Resources; con 4 GB alcanza para la base. |

Si un error no aparece aquí, se copia el mensaje completo y se busca junto con la palabra Docker; casi siempre es un problema que alguien ya resolvió. Si persiste, se pide ayuda al equipo con el mensaje y los comandos ejecutados.

## Lista de verificación para cerrar BE-01

- [ ] `docker compose config` no muestra errores.
- [ ] `docker compose up -d db` levanta el servicio y `docker compose ps` lo muestra como `healthy`.
- [ ] La extensión `vector` aparece en la lista de extensiones.
- [ ] `.env` está en `.gitignore` y no aparece en `git status`; `.env.example` sí está en el repositorio.
- [ ] `app/db.py` y `tests/test_db.py` existen y la prueba pasa sin Docker.
- [ ] La verificación manual contra la base real imprime `True`.
- [ ] El README explica en pocas líneas cómo levantar la base y a qué documento recurrir.
- [ ] `almacen.py` es una fachada con un método por repositorio, y el cambio se integró a `develop` el lunes.
- [ ] Al menos un integrante, distinto de la autora, levantó la base siguiendo el README y le funcionó.

Cuando esté integrada, el resto del equipo puede empezar a escribir sus repositorios de datos (BE-02, BE-03 y BE-04) sobre esta base. Las pruebas de cada repositorio usan SQLite en memoria, así que no dependen de que el contenedor esté encendido.
