# POST /resumen

Genera el resumen de los últimos siete días del paciente vinculado al tratante.

- **Estado:** Pendiente. Actualmente responde 501
- **Requerimientos:** RF-19
- **Historia:** HU-17
- **Roles permitidos:** tratante

## Petición

Cabecera `X-Usuario-Id` obligatoria, con una cuenta de rol tratante. No requiere cuerpo: en la primera entrega el tratante tiene un único paciente vinculado.

```bash
curl -X POST http://127.0.0.1:8000/resumen -H "X-Usuario-Id: tratante"
```

## Respuesta propuesta

El siguiente contrato es una propuesta para la historia HU-17 y puede ajustarse durante su implementación. Código `201`.

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `paciente_id` | texto | Paciente al que corresponde el resumen |
| `desde`, `hasta` | fecha | Periodo cubierto |
| `generado_en` | fecha y hora | Momento de la generación |
| `generado_por_ia` | booleano | Siempre `true`; la aplicación debe mostrarlo |
| `temas` | lista de texto | Temas tratados en el periodo |
| `hechos` | lista de objetos | Hechos específicos, cada uno con `fecha` y `descripcion` |
| `patrones` | lista de texto | Patrones observados, redactados de forma descriptiva |
| `alertas` | lista de objetos | Alertas del periodo, con `fecha`, `nivel` y `mensaje` |

```json
{
  "paciente_id": "luis",
  "desde": "2026-11-05",
  "hasta": "2026-11-12",
  "generado_en": "2026-11-12T16:00:00Z",
  "generado_por_ia": true,
  "temas": ["Carga académica", "Dificultad para dormir"],
  "hechos": [
    { "fecha": "2026-11-07", "descripcion": "Relató que no pudo dormir antes de un examen." }
  ],
  "patrones": ["El malestar aumenta en los días previos a una entrega."],
  "alertas": []
}
```

## Errores

| Código | Causa |
| --- | --- |
| 401 | Cuenta desconocida |
| 403 | La cuenta no tiene rol de tratante |
| 501 | Endpoint aún no implementado |

## Notas

- El resumen describe hechos y patrones. No contiene diagnósticos, interpretaciones clínicas ni recomendaciones de intervención (regla RN-08).
- Cada hecho debe indicar el día de la conversación de la que procede.
- El resumen no incluye la conversación literal (regla RN-06).
