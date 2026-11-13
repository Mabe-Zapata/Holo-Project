# Holo · Backend

API del proyecto Holo, una aplicación de apoyo conversacional en salud mental. Este repositorio contiene el backend en FastAPI. La aplicación móvil se encuentra en el repositorio `Holo-project-front`.

> **Estado:** demostración en desarrollo. Opera con cuentas ficticias y almacenamiento en memoria. No debe utilizarse con datos de personas reales.

## Requisitos

- Python 3.10 o superior
- Git

## Puesta en marcha

En Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload
```

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000` y la documentación interactiva en `http://127.0.0.1:8000/docs`.

Para probar la aplicación móvil desde un teléfono en la misma red, inicie el servidor con `uvicorn app.main:app --reload --host 0.0.0.0` y utilice la dirección IP del equipo.

## Comprobaciones

```bash
pytest          # pruebas automáticas
ruff check .    # análisis estático
ruff format .   # formato del código
```

## Estructura

```text
app/
  main.py            Punto de entrada de la API
  core/config.py     Configuración por variables de entorno
  api/deps.py        Dependencias compartidas (cuenta, proveedor, expresiones)
  api/routes/        Un archivo por grupo de endpoints
  schemas/           Modelos de entrada y salida
  services/          Lógica: almacenamiento, riesgo y proveedor del modelo
data/                Lista de expresiones de riesgo (pendiente de la especialista)
docs/                Documentación del proyecto y product backlog
odds/                Documentación de los endpoints
scripts/             Utilidades (exportar la especificación OpenAPI)
tests/               Pruebas automáticas
```

## Cuentas de demostración

No existe registro ni inicio de sesión en esta entrega. Cada petición identifica la cuenta mediante la cabecera `X-Usuario-Id`.

| Cuenta | Rol | Descripción |
| --- | --- | --- |
| `ana` | Usuaria estándar | Sin tratante |
| `luis` | Paciente | Vinculado a la tratante de demostración |
| `tratante` | Tratante | Consulta las alertas y el resumen de Luis |

## Estado de los endpoints

| Endpoint | Estado | Historia pendiente |
| --- | --- | --- |
| `GET /salud` | Operativo | |
| `POST /consentimiento` | Operativo, en memoria | HU-04 (persistencia en SQLite) |
| `POST /chat` | Operativo con proveedor de prueba (eco), sin búsqueda en el material | HU-08, HU-09 |
| `GET /chat/historial` | Operativo, en memoria | HU-06 |
| `POST /resumen` | Responde 501 | HU-17 |
| `GET /tratante/paciente` | Devuelve alertas; el resumen aún es nulo | HU-17 |

La revisión de riesgo está implementada, pero la lista `data/expresiones_riesgo.txt` se encuentra vacía hasta contar con las expresiones aprobadas por la especialista. El texto de crisis es provisional.

## Documentación

- [Documento de trabajo del equipo](docs/documento-de-trabajo-equipo.md)
- [Product backlog](docs/product-backlog.md)
- [Documentación de endpoints](odds/README.md)
- [Convenios de desarrollo y requisitos de pull request](CONTRIBUTING.md)

## Consideraciones

- Las claves de los proveedores se guardan únicamente en el archivo `.env`, que no se sube al repositorio.
- Mientras se utilicen proveedores gratuitos de modelos o material sin validar, solo se trabaja con datos ficticios.
- Holo no emite diagnósticos, no indica medicación y no sustituye a un profesional ni a un servicio de emergencia.
