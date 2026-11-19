# POST /consentimiento

Registra la aceptación del consentimiento informado y la declaración de mayoría de edad.

- **Estado:** Operativo con persistencia SQL (PostgreSQL; SQLite en pruebas)
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
- La aceptación persiste después de reiniciar la aplicación; el chat consulta este registro, no una marca de consentimiento en memoria.
- Una nueva aceptación actualiza la misma fila y su fecha anterior, sin duplicar registros por usuario. Las primeras aceptaciones concurrentes se resuelven mediante una inserción/actualización atómica.
- La fecha se genera en UTC. También se guardan la mayoría de edad declarada y la versión del texto, actualmente `provisional-1`, pendiente de DOC-01 y revisión legal.
- Una petición rechazada por falta de aceptación o mayoría de edad no escribe el registro. La transacción pertenece a la conexión proporcionada por la aplicación.
