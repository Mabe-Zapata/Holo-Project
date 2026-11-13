# POST /consentimiento

Registra la aceptación del consentimiento informado y la declaración de mayoría de edad.

- **Estado:** Operativo (almacenamiento en memoria)
- **Requerimientos:** RF-02
- **Historias:** HU-02, HU-03
- **Roles permitidos:** usuario_estandar, paciente, tratante

## Petición

Cabecera `X-Usuario-Id` obligatoria.

| Campo | Tipo | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `mayor_de_edad` | booleano | Sí | El usuario declara tener 18 años o más |
| `acepta` | booleano | Sí | El usuario acepta el consentimiento informado |

```bash
curl -X POST http://127.0.0.1:8000/consentimiento \
  -H "Content-Type: application/json" \
  -H "X-Usuario-Id: ana" \
  -d '{"mayor_de_edad": true, "acepta": true}'
```

## Respuesta

Código `201`.

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `usuario_id` | texto | Cuenta que aceptó |
| `aceptado_en` | fecha y hora | Momento de la aceptación |

```json
{ "usuario_id": "ana", "aceptado_en": "2026-11-12T15:30:00Z" }
```

## Errores

| Código | Causa |
| --- | --- |
| 400 | `mayor_de_edad` o `acepta` tienen el valor `false` |
| 401 | Cuenta desconocida |
| 422 | Falta un campo o su tipo es incorrecto |

## Notas

- Sin un consentimiento registrado, `POST /chat` responde 403.
- Una nueva aceptación reemplaza la fecha anterior.
- Pendiente (HU-04): persistir el registro en SQLite.
