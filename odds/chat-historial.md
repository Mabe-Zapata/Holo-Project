# GET /chat/historial

Devuelve los mensajes anteriores de la cuenta, en orden cronológico.

- **Estado:** Operativo (almacenamiento en memoria)
- **Requerimientos:** RF-07
- **Historias:** HU-05, HU-06
- **Roles permitidos:** usuario_estandar, paciente

## Petición

Cabecera `X-Usuario-Id` obligatoria. No requiere cuerpo.

```bash
curl http://127.0.0.1:8000/chat/historial -H "X-Usuario-Id: ana"
```

## Respuesta

Código `200`. Lista de mensajes; vacía si la cuenta no ha conversado.

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `autor` | texto | `usuario` o `asistente` |
| `texto` | texto | Contenido del mensaje |
| `fecha` | fecha y hora | Momento del mensaje |
| `tipo` | texto | `mensaje` (del usuario), `respuesta` o `crisis` (del asistente) |

```json
[
  { "autor": "usuario", "texto": "Estoy muy estresada", "fecha": "2026-11-12T15:31:00Z", "tipo": "mensaje" },
  { "autor": "asistente", "texto": "[eco] Estoy muy estresada", "fecha": "2026-11-12T15:31:01Z", "tipo": "respuesta" }
]
```

## Errores

| Código | Causa |
| --- | --- |
| 401 | Cuenta desconocida |

## Notas

- Cada cuenta solo accede a su propio historial. El tratante no puede consultar la conversación de su paciente (regla RN-06).
- Pendiente (HU-06): persistencia en SQLite. Actualmente el historial se pierde al reiniciar el servidor.
