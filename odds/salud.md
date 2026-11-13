# GET /salud

Comprueba que la API se encuentra en funcionamiento.

- **Estado:** Operativo
- **Roles permitidos:** no requiere identificación

## Petición

No requiere cabeceras ni cuerpo.

```bash
curl http://127.0.0.1:8000/salud
```

## Respuesta

Código `200`.

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `estado` | texto | Siempre `ok` cuando la API responde |
| `version` | texto | Versión de la API |

```json
{ "estado": "ok", "version": "0.1.0" }
```

## Notas

La aplicación móvil puede emplear este endpoint para verificar la conexión antes de mostrar la conversación.
