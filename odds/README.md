# Documentación de endpoints

Esta carpeta describe el contrato de cada endpoint de la API de Holo. Es la referencia para el equipo de la aplicación móvil y debe actualizarse en el mismo pull request que modifica un endpoint.

## Índice

| Endpoint | Documento | Estado | Requerimientos |
| --- | --- | --- | --- |
| `GET /salud` | [salud.md](salud.md) | Operativo | |
| `POST /consentimiento` | [consentimiento.md](consentimiento.md) | Operativo | RF-02 |
| `POST /chat` | [chat.md](chat.md) | Operativo con proveedor de prueba | RF-07, RF-08, RF-09, RF-23, RF-24 |
| `GET /chat/historial` | [chat-historial.md](chat-historial.md) | Operativo | RF-07 |
| `POST /resumen` | [resumen.md](resumen.md) | Pendiente (responde 501) | RF-19 |
| `GET /tratante/paciente` | [tratante-paciente.md](tratante-paciente.md) | Operativo parcial | RF-25, RF-30 |

Para documentar un endpoint nuevo se parte de [_plantilla.md](_plantilla.md).

## Convenciones generales

- **URL base en desarrollo:** `http://127.0.0.1:8000`
- **Formato:** JSON codificado en UTF-8, con la cabecera `Content-Type: application/json`.
- **Fechas:** formato ISO 8601 en UTC, por ejemplo `2026-11-12T15:30:00Z`.
- **Nombres de campos:** en español y en `snake_case`.

### Identificación de la cuenta

En la primera entrega no existe inicio de sesión. Todas las peticiones, excepto `GET /salud`, deben incluir la cabecera `X-Usuario-Id` con una de las cuentas de demostración.

| Valor | Rol |
| --- | --- |
| `ana` | `usuario_estandar` |
| `luis` | `paciente` |
| `tratante` | `tratante` |

### Errores

Todos los errores tienen la misma forma:

```json
{ "detail": "Descripción del error." }
```

| Código | Significado |
| --- | --- |
| 400 | La petición es válida en su forma, pero no cumple una regla del sistema |
| 401 | La cabecera `X-Usuario-Id` no corresponde a una cuenta conocida |
| 403 | La cuenta no tiene permiso para la operación |
| 404 | El recurso solicitado no existe |
| 422 | El cuerpo o las cabeceras no cumplen el esquema; `detail` contiene una lista con el campo y el motivo |
| 501 | El endpoint está definido, pero aún no implementado |

## Especificación OpenAPI

El archivo [openapi.json](openapi.json) contiene la especificación generada a partir del código. Se regenera con:

```bash
python scripts/exportar_openapi.py
```

Con el servidor en ejecución, la documentación interactiva está disponible en `http://127.0.0.1:8000/docs`.
