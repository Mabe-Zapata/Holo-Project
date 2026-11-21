# POST /chat

Recibe un mensaje del usuario, revisa el riesgo y devuelve la respuesta del asistente o el texto fijo de crisis.

- **Estado:** Operativo con proveedor de prueba (eco); aún sin búsqueda en el material
- **Requerimientos:** RF-07, RF-08, RF-09, RF-23, RF-24, RF-25
- **Historias:** HU-06, HU-08, HU-09, HU-10, HU-13, HU-14
- **Roles permitidos:** usuario_estandar, paciente

## Petición

Cabecera `X-Usuario-Id` obligatoria.

| Campo | Tipo | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `texto` | texto | Sí | Mensaje del usuario, de 1 a 2000 caracteres |

Un texto vacío, solo con espacios o de más de 2000 caracteres devuelve 422 con un mensaje en español (BE-16).

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-Usuario-Id: ana" \
  -d '{"texto": "Estoy muy estresada por mis entregas"}'
```

## Respuesta

Código `200` en ambos casos. La aplicación decide qué pantalla mostrar según el campo `tipo`.

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `tipo` | texto | `respuesta` o `crisis` |
| `texto` | texto | Respuesta del asistente o texto fijo de crisis |
| `riesgo` | texto | `sin_riesgo` o `alto` |
| `fragmentos` | lista de texto | Identificadores de los fragmentos del material empleados. Vacía mientras no se implemente HU-08 |
| `recursos` | lista de objetos | Recursos de ayuda; solo se incluye cuando `tipo` es `crisis` |

Cada elemento de `recursos` contiene `nombre`, `telefono` y `descripcion`.

Respuesta habitual:

```json
{
  "tipo": "respuesta",
  "texto": "[eco] Estoy muy estresada por mis entregas",
  "riesgo": "sin_riesgo",
  "fragmentos": [],
  "recursos": []
}
```

Respuesta ante riesgo alto:

```json
{
  "tipo": "crisis",
  "texto": "[Texto provisional, pendiente de aprobación de la especialista] ...",
  "riesgo": "alto",
  "fragmentos": [],
  "recursos": [
    { "nombre": "ECU 911", "telefono": "911", "descripcion": "Emergencias" },
    { "nombre": "Línea 171, opción 6", "telefono": "171", "descripcion": "Salud mental, Ministerio de Salud Pública" }
  ]
}
```

## Errores

| Código | Causa |
| --- | --- |
| 401 | Cuenta desconocida |
| 403 | La cuenta no ha aceptado el consentimiento, o es una cuenta que no conversa (tratante) |
| 422 | `texto` vacío, ausente o de más de 2000 caracteres |
| 503 | El proveedor no está configurado, no respondió o devolvió contenido inválido. El detalle técnico no se muestra |

## Notas

- La revisión de riesgo se ejecuta siempre antes de consultar al modelo. Ante riesgo alto, el modelo no interviene y se registra una alerta para el tratante.
- La lista de expresiones de riesgo (`data/expresiones_riesgo.txt`) está vacía hasta recibir la versión aprobada por la especialista; mientras tanto, ningún mensaje activa la respuesta de crisis.
- Cuando `tipo` es `crisis`, la aplicación debe mostrar la pantalla de crisis y no ofrecer técnicas.
- Pendiente: búsqueda en el material aprobado (HU-08) y rechazo de diagnóstico y medicación en el flujo (HU-10).
- La restricción por rol ya está aplicada: la cuenta tratante recibe 403 en el chat y su historial.
- El proveedor real (HU-09) es una API compatible con OpenAI configurada con `HOLO_PROVEEDOR_LLM=groq`, `HOLO_LLM_API_KEY`, `HOLO_LLM_MODELO` y `HOLO_LLM_URL_BASE`. El prompt del sistema (`data/prompts/prompt_sistema.md`) se envía en cada llamada.
- La construcción del proveedor real se difiere hasta la respuesta normal: una configuración incompleta no impide rechazar una cuenta sin consentimiento ni devolver la respuesta de crisis y registrar su alerta. En una respuesta normal, la falta de configuración produce el mismo 503 genérico que un error del proveedor. Una respuesta del modelo debe ser una cadena no vacía; no se convierten objetos ni valores nulos en mensajes.

## Reintentos y caídas de la base

- **`id_evento`** (opcional, 8 a 64 caracteres `A-Z a-z 0-9 _ -`): identificador que el cliente asigna a cada mensaje. Reenviar el mismo `id_evento` no duplica el mensaje ni la alerta, y devuelve la misma respuesta sin llamar al modelo. Sin `id_evento`, el servidor asigna uno propio.
- **Crisis con la base caída:** la respuesta de crisis (`tipo: "crisis"`) se entrega igual. El evento queda en una cola local y se guarda en la base cuando vuelve. El tratante ve esas alertas en `alertas_pendientes` de `GET /tratante/paciente`.
- **Crisis sin consentimiento:** se muestran los recursos de ayuda, pero no se guarda nada.
- **Mensaje normal con la base caída:** responde `500`. El cliente debe reintentar con el mismo `id_evento`.

