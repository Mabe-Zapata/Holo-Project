# GET /tratante/paciente

Devuelve las alertas y el último resumen del paciente vinculado al tratante.

- **Estado:** Operativo parcial. Devuelve las alertas; el campo `resumen` es nulo hasta implementar HU-17
- **Requerimientos:** RF-25, RF-30
- **Historias:** HU-16, HU-18
- **Roles permitidos:** tratante

## Petición

Cabecera `X-Usuario-Id` obligatoria, con una cuenta de rol tratante. No requiere cuerpo.

```bash
curl http://127.0.0.1:8000/tratante/paciente -H "X-Usuario-Id: tratante"
```

## Respuesta

Código `200`.

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `paciente_id` | texto | Identificador del paciente vinculado |
| `nombre` | texto | Nombre del paciente |
| `alertas` | lista de objetos | Alertas registradas, cada una con `nivel`, `mensaje` y `fecha` |
| `resumen` | texto o nulo | Último resumen generado. Su forma definitiva se establecerá en HU-17 |

```json
{
  "paciente_id": "luis",
  "nombre": "Luis",
  "alertas": [
    { "nivel": "alto", "mensaje": "Texto del mensaje que originó la alerta", "fecha": "2026-11-12T15:40:00Z" }
  ],
  "resumen": null
}
```

## Errores

| Código | Causa |
| --- | --- |
| 401 | Cuenta desconocida |
| 403 | La cuenta no tiene rol de tratante |
| 404 | El tratante no tiene pacientes vinculados |

## Notas

- El tratante solo accede a los datos de su paciente vinculado y nunca a la conversación completa.
- El campo `mensaje` de la alerta contiene el texto que la originó, a fin de que el tratante conozca el contexto.
- Pendiente (HU-16): persistencia de las alertas en SQLite.
