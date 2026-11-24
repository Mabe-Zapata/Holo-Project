# Backlog del sprint 2 (23 al 27 de noviembre)

Documento de trabajo. Parte de `docs/backlog-mvp-por-sprint.md` y lo actualiza con el estado real del código al 19 de noviembre. Cuando una tarea cambie de estado, actualizar esta tabla en el mismo pull request.

## Objetivo

Que la demostración recorra completa tres casos: la conversación de Ana, la crisis de Luis con alerta visible para la tratante, y el resumen semanal generado por IA. Todo con datos ficticios y material provisional.

## Estado de entrada (fin del sprint 1)

Trabajo del sprint 1 que quedó en revisión y todavía no está en `develop`:

| Tarea | Rama | Pull request | Estado |
| --- | --- | --- | --- |
| DOC-01, texto del consentimiento | `feature/DOC-01-consentimiento` | Holo-Project #18 | Abierto |
| BE-04, chat e historial en la base | `feature/BE-04-conectar-chat` | Holo-Project #19 | Abierto |
| HU-16, alertas en la base | `feature/HU-16-alertas` | Holo-Project #20 | Abierto, apilado sobre #19 |
| HU-16, crisis resiliente y cola de sincronización | `feature/crisis-resiliencia` | Holo-Project #21 | Abierto, apilado sobre #20 |
| FE-07, recursos de ayuda en la conversación | `feature/FE-07-recursos-ayuda` | Holo-Frontend #7 | Abierto |
| HU-16 (cliente), cola de envíos con reintento | `feature/crisis-cola-envios` | Holo-Frontend #8 | Abierto, apilado sobre #7 |

Revisar y fusionar en este orden: #18 y #19, después #20, #21, #7 y #8. Cuando una rama intermedia se fusione, cambiar la base del PR siguiente a `develop`.

Pendientes del sprint 1 que no están en ningún pull request: BE-14 (formato único de errores), UX-01 a UX-03 (guía de estilo y mockups) y CI-01 y CI-02 (verificación de cada pull request, que ya aparecen en `develop` pero conviene confirmar).

## Alcance del sprint

Los puntos y responsables vienen del plan original. El estado se verificó contra `origin/develop` y las ramas abiertas.

### Erick: inteligencia artificial (12 pts)

| ID | Tarea | Pts | Estado | Depende de |
| --- | --- | --- | --- | --- |
| HU-08b | Chat responde con el material aprobado; registra fragmentos | 5 | Sin empezar. `app/api/routes/chat.py` ya tiene la base de la ruta | HU-07, HU-08a (ver riesgos) |
| HU-17a | `generar_resumen` con hechos y su día de origen | 5 | Sin empezar. `app/api/routes/resumen.py` responde 501 | BE-07a en `develop` |
| FE-11 | Widget del resumen con etiqueta "Generado por IA" | 2 | Sin empezar | HU-17b |

### María Belén: backend y seguridad (14 pts)

| ID | Tarea | Pts | Estado | Depende de |
| --- | --- | --- | --- | --- |
| HU-16 | Alertas guardadas y visibles solo al tratante vinculado | 2 | En revisión: #20 y #21 | BE-04 (#19) |
| HU-11 | Relajación paso a paso, respiración y anclaje | 3 | Sin empezar | Ninguna |
| HU-12 | Contenido del módulo de ansiedad solo para cuentas de paciente | 3 | Sin empezar | HU-07 |
| HU-17b | `POST /resumen` guarda el último resumen (solo tratante vinculado) | 3 | Sin empezar | HU-17a |
| HU-21 | Conjunto de mensajes de prueba y script de evaluación | 3 | Sin empezar | Ninguna |

### Parejas (22 pts)

| ID | Resp. | Pareja | Tarea | Pts | Estado | Depende de |
| --- | --- | --- | --- | --- | --- | --- |
| HU-15 | Damien | D | Pantalla de crisis con recursos, sin técnicas ni campo de escritura | 3 | Parcial: `crisis_screen.dart` existe; revisar criterios y pruebas | Ninguna |
| BE-06 | Álvaro | D | `registrar_respuesta` en `app/repositorios/auditoria.py` | 2 | Sin empezar | HU-08b |
| UX-04 | Álvaro | D | Prueba de usabilidad con tres personas ajenas al equipo | 2 | Sin empezar | Flujo de consentimiento y conversación estable |
| FE-10 | Jampier | E | Widget `ListaAlertas` con estado vacío | 2 | Sin empezar | HU-16 (#20) |
| BE-07b | Jampier | E | Script que carga `conversaciones_luis.json` sin duplicar | 1 | Sin empezar | BE-04 (#19) |
| FE-12 | Jose | E | Vista del tratante con alertas, resumen y botón de resumen nuevo | 2 | Sin empezar | FE-10, FE-11, HU-17b |
| BE-08 | Jose | E | Prueba que falla si `odds/openapi.json` está desactualizado | 1 | Sin empezar. Existe `scripts/exportar_openapi.py` | Ninguna |
| FE-13 | Justin | F | Recorrido contra el backend real, con diferencias registradas en `odds/` | 2 | Sin empezar | HU-08b, HU-17b |
| BE-19 | Justin | F | Revisión de seguridad básica, en `docs/seguridad.md` | 2 | Sin empezar | Ninguna |
| BE-17 | Imanol | F | Prueba de extremo a extremo: consentimiento, mensaje, crisis, alerta y resumen | 2 | En revisión: `tests/test_flujo_completo.py` | HU-08b, HU-17b |
| HU-22 | Karol | F | Guion de la demostración, presentación y grabación de respaldo | 3 | Sin empezar | Todo lo anterior para el ensayo final |

Total del sprint: 48 pts (Erick 12, María Belén 14, parejas 22).

## Orden de trabajo

1. **Día 1 (lunes 23):** revisar y fusionar #18 y #19. Sin esto, BE-07b y el resto de la cadena de chat no pueden empezar.
2. **Día 1 a 2:** HU-07 y HU-08a (de Erick) desbloquean HU-08b, que es la tarea más larga del sprint.
3. **Trabajo en paralelo:** HU-11, HU-21, BE-08, BE-19, HU-15 y UX-04 no tienen dependencias.
4. **Día 3 a 4:** HU-17a y HU-17b, después FE-11 y FE-12.
5. **Día 4 a 5:** FE-13 y BE-17 cuando HU-08b y HU-17b estén integradas.
6. **Viernes 27:** ensayo de HU-22 dos veces seguidas, con grabación de respaldo.

## Definición de terminado

Lo de `CONTRIBUTING.md` y la plantilla de pull request, más:

- Cada tarea tiene al menos una prueba automática. Las tareas de front, con prueba de widget.
- `ruff check .`, `ruff format --check .`, `pytest`, `flutter analyze` y `flutter test` en verde.
- Cambios de endpoint actualizan `odds/` y regeneran `odds/openapi.json`.
- Ningún dato real, clave ni archivo `.env` en el repositorio. La cola de crisis (`data/cola/`) queda fuera del repositorio.

## Riesgos

- **HU-07 y HU-08a no existen en `develop`.** Son de Erick en el sprint 1. Si no están, HU-08b no puede cerrarse en el sprint. Confirmar el estado con Erick el lunes.
- **Migración de la base.** Las columnas nuevas de HU-16 (`id_evento`) requieren `ALTER TABLE` en cada base existente. Está documentado en el PR #21. Cada integrante debe aplicarlo en su entorno.
- **Lista de riesgo y texto de crisis provisionales.** La demostración muestra el aviso, no una detección validada.
- **Flutter nunca se había compilado en el equipo.** Ya se generó `web/` y pasan las pruebas, pero falta probar en teléfono.
- **Cadena de pull requests.** Varias tareas dependen de PRs que aún no se fusionaron. Un retraso en #18 o #19 atrasa la mitad del sprint.
- **Personas sin acceso.** Las invitaciones al repositorio pueden seguir pendientes; sin ellas nadie puede subir código.

## Fuera de este sprint

Historias opcionales (BE-12, FE-14, BE-13, FE-15, HU-24, HU-26) y las épicas E1 a E7 del product backlog.
