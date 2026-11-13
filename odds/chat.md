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
| 403 | La cuenta no ha aceptado el consentimiento |
| 422 | `texto` vacío, ausente o de más de 2000 caracteres |

## Notas

- La revisión de riesgo se ejecuta siempre antes de consultar al modelo. Ante riesgo alto, el modelo no interviene y se registra una alerta para el tratante.
- La lista de expresiones de riesgo (`data/expresiones_riesgo.txt`) está vacía hasta recibir la versión aprobada por la especialista; mientras tanto, ningún mensaje activa la respuesta de crisis.
- Cuando `tipo` es `crisis`, la aplicación debe mostrar la pantalla de crisis y no ofrecer técnicas.
- Pendiente: búsqueda en el material aprobado (HU-08), proveedor real del modelo (HU-09), rechazo de diagnóstico y medicación (HU-10), y restricción del endpoint a los roles indicados.
