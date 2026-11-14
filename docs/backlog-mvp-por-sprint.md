# Holo: backlog del MVP por sprint y responsable

Nov 14, 2026 · @Maria Zapata

El MVP se reparte entre nueve integrantes en dos sprints de una semana, trabajando en parejas: Erick concentra la inteligencia artificial, María Belén el backend y la IA de seguridad, y los otros siete combinan tareas de front y back en parejas que rotan, para que todos conozcan el código completo.

## Planificación

Se propone el sprint 1 del 16 al 20 de noviembre y el sprint 2 del 23 al 27 de noviembre; las fechas deben confirmarse con la fecha real de la demostración. El MVP original suma 76 puntos; con las tareas técnicas que surgen al dividirlo, el plan llega a 115.

| Integrante | Usuario de GitHub | Área | Sprint 1 | Sprint 2 | Total |
| --- | --- | --- | --- | --- | --- |
| Erick Guerron | ErickGuerron | Inteligencia artificial y una tarea de front | 13 | 12 | 25 |
| María Belén | Mabe-Zapata | Backend, Docker e IA de seguridad | 11 | 14 | 25 |
| Álvaro López | alvarolopezmoya | Front y back | 5 | 4 | 9 |
| Jose Mera | mxrajxse38 | Front y back | 4 | 3 | 7 |
| Damien | Damienq7w | Front y back | 8 | 3 | 11 |
| Justin Alexander | ElJoss09 | Front y back | 5 | 4 | 9 |
| Jampier Camacho | jampiercamacho94-cloud | Front y back | 5 | 3 | 8 |
| Imanol Miranda | Osyanne | Front y back | 6 | 2 | 8 |
| Karol | Sin cuenta todavía | Diseño, documentación y, al unirse, front y back | 10 | 3 | 13 |
| **Total** |  |  | **67** | **48** | **115** |

La carga de los siete integrantes que combinan front y back es baja a propósito (7 a 13 puntos en dos semanas): es el primer proyecto conjunto del equipo, programar en pareja es más lento que hacerlo solo y el margen cubre revisiones y aprendizaje. Quien termine antes toma una historia opcional. Los nombres de pila se infirieron de la cuenta de GitHub o de la invitación y deben confirmarse.

## Parejas y programación en pareja

Cada pareja toma un tema completo (una parte del front y una del back) y lo construye junta. Las parejas cambian en el sprint 2, de modo que cada integrante trabaja con otras personas y toca ambos repositorios.

| Sprint | Pareja | Integrantes | Tema | Tareas |
| --- | --- | --- | --- | --- |
| 1 | N | Erick y María Belén | IA y núcleo del backend | Sus secciones de este documento |
| 1 | A | Álvaro y Jose | Acceso: cuentas y consentimiento | BE-02, BE-03, HU-02, FE-07 |
| 1 | B | Damien y Justin | Conversación | FE-05, FE-06, BE-04, BE-14, BE-16 |
| 1 | C (trío) | Jampier, Imanol y Karol | Base técnica y diseño | FE-01, FE-02, CI-01, CI-02, BE-07a, BE-15, DOC-01, UX-01, UX-02, UX-03 |
| 2 | N | Erick y María Belén | Flujo de chat y resumen | Sus secciones de este documento |
| 2 | D | Álvaro y Damien | Crisis y usabilidad | HU-15, BE-06, UX-04 |
| 2 | E | Jose y Jampier | Vista del tratante y datos | FE-10, FE-12, BE-07b, BE-08 |
| 2 | F (trío) | Justin, Imanol y Karol | Integración y cierre | FE-13, BE-17, BE-19, HU-22 |

Cómo se trabaja en pareja:

1. **Pair programming remoto por turnos.** Una persona programa y la otra revisa; después cambian de rol. No hace falta conectarse a la vez durante horas.
2. **Turno de escritura.** Quien programa trabaja en una rama `feature/HU-xx-descripcion`, hace commits pequeños, sube la rama y abre un pull request en borrador con lo que hizo y lo que falta.
3. **Turno de revisión.** La pareja lee el borrador en GitHub, comenta línea por línea, prueba la rama en su equipo y deja sus observaciones en un plazo máximo de medio día.
4. **Cambio de roles.** Quien revisó toma el siguiente turno sobre la misma rama (la parte siguiente de la tarea o la tarea que sigue) y quien escribió pasa a revisar. En cada relevo se recomienda una llamada de 10 a 15 minutos para explicar lo hecho.
5. **Responsable y coautoría.** Cada tarea tiene un responsable, que cierra el pull request; su pareja figura como coautora en los commits con la línea `Co-authored-by:` con su nombre y correo de GitHub.
6. **Front y back juntos.** Antes de pasar el borrador a revisión final, la pareja prueba junta la parte de front y la de back del tema.
7. **Revisión final.** La hace alguien ajeno a la pareja, según `CONTRIBUTING.md`.
8. **Karol.** Hasta que reciba acceso a los repositorios trabaja en diseño y documentación; cuando entre, su pareja puede abrir los pull requests con ella como coautora.

## Reglas para trabajar de forma autónoma

Cada tarea corresponde a un pull request, tiene sus propios archivos y sus propias pruebas, y puede comenzar el primer día de su sprint.

- **Un dueño por archivo.** Cada tarea indica los archivos que crea; nadie más los modifica durante el sprint. El archivo `app/api/routes/chat.py` solo lo modifica Erick (HU-08b): los demás exponen funciones con la firma acordada y él las conecta.
- **Base de datos en Docker.** La base es PostgreSQL con pgvector, ejecutada con Docker Compose (BE-01, María Belén; ver el documento de Docker). Cada repositorio de datos (`app/repositorios/usuarios.py`, `consentimientos.py`, `mensajes.py`, `alertas.py`, `auditoria.py`) usa SQLAlchemy y recibe la conexión como parámetro; sus pruebas usan SQLite en memoria, de modo que no necesitan Docker ni dependen de otra tarea.
- **Front por pantalla.** Cada pantalla vive en `lib/features/<nombre>/`, recibe el cliente de la API por constructor y se prueba con un cliente falso; ninguna espera al backend.
- **Contrato único.** La carpeta `odds/` del backend define lo que la API recibe y devuelve. Un cambio exige un pull request que modifique `odds/` y la aprobación de quien consume ese endpoint.
- **Dos bases el primer día.** Son las únicas tareas que otras usan: BE-01 (Docker y conexión, María Belén) y FE-01 (carpetas de plataforma de Flutter, Jampier). Deben integrarse el día 1; hasta entonces el resto trabaja con pruebas locales.

Las ramas, los commits y los requisitos de pull request siguen `CONTRIBUTING.md` de cada repositorio. Los textos de crisis, consentimiento y material son provisionales hasta la aprobación de la especialista.

## Erick: inteligencia artificial

Erick es dueño de todo lo que alimenta y controla al modelo: el proveedor, los prompts, el material y su recuperación (RAG), las respuestas con fuentes y el resumen. Ninguna tarea espera a la especialista: el material inicial es provisional. Como la base será PostgreSQL con pgvector, puede guardar los vectores del material en ella o usar una solución más simple; la decisión es suya. Tiene también una tarea de front para conocer esa parte del código.

### Sprint 1: modelo, prompt y conocimiento (13 pts)

| ID | Tarea | Criterios de aceptación | Archivos | Pts |
| --- | --- | --- | --- | --- |
| HU-09 | **(Técnica)** Como equipo, queremos el modelo encapsulado en una interfaz, para cambiar de proveedor sin tocar el resto. | Existe un proveedor real (Gemini o Groq) además del proveedor de prueba. El cambio se hace con `HOLO_PROVEEDOR_LLM`. La clave se lee de `.env` y `.env.example` queda actualizado. Las pruebas usan el proveedor de prueba y no consumen cuota. | `app/services/proveedor_llm.py`, `.env.example` | 3 |
| IA-01 | **(Técnica)** Como equipo, queremos el prompt del sistema versionado, para que el tono y los límites del asistente sean verificables. | Un archivo indica su versión y define rol, tono y límites: no diagnostica, no habla de medicación, responde solo con los fragmentos entregados y declara ser una IA. Se carga desde archivo, no desde el código. Una prueba confirma que se incluye en cada llamada al modelo. | `data/prompts/prompt_sistema.md`, `app/services/prompts.py` | 2 |
| HU-07 | Como administrador, quiero cargar material con etiquetas de tema, modo y módulo, para que el asistente pueda consultarlo. | Un script carga entre 5 y 10 textos con sus etiquetas y su estado (provisional o aprobado). Los textos iniciales son provisionales, redactados por el equipo a partir de guías públicas citadas. Una búsqueda por tema recupera el documento. | `scripts/cargar_material.py`, `data/material/`, `app/services/material.py` | 5 |
| HU-08a | **(Técnica)** Como equipo, queremos recuperar los fragmentos pertinentes de una consulta, para que el asistente responda desde el material. | `buscar_fragmentos(consulta, modo, modulo)` devuelve hasta tres fragmentos con su identificador y una lista vacía si ninguno supera un umbral configurable. Una prueba con diez consultas documenta los resultados. | `app/services/recuperacion.py` | 3 |

### Sprint 2: respuestas con fuentes, resumen y una tarea de front (12 pts)

| ID | Tarea | Criterios de aceptación | Archivos | Pts |
| --- | --- | --- | --- | --- |
| HU-08b | Como usuario, quiero que el asistente responda a partir del material aprobado, para recibir orientación confiable. | `POST /chat` ejecuta, en orden, la revisión de riesgo, el filtro de diagnóstico (HU-10), la búsqueda de fragmentos y el modelo. Cada respuesta registra al menos un fragmento. Sin fragmento pertinente, el asistente indica que no puede ayudar con esa consulta y orienta hacia un profesional, sin llamar al modelo. `odds/chat.md` incluye los fragmentos. | `app/api/routes/chat.py`, `odds/chat.md` | 5 |
| HU-17a | Como tratante, quiero que el resumen semanal se genere con hechos específicos, para preparar la sesión. | `generar_resumen(mensajes)` devuelve hechos, cada uno con su día de origen, sin diagnósticos ni recomendaciones clínicas, e indica que fue generado por IA. El prompt está versionado. Se prueba con las conversaciones ficticias de BE-07a o con un archivo propio. | `app/services/resumen.py`, `data/prompts/prompt_resumen.md` | 5 |
| FE-11 | Como tratante, quiero ver el resumen semanal de mi paciente, para preparar la sesión. | Widget que muestra cada hecho con su día y la etiqueta "Generado por IA", con un estado sin resumen. Con pruebas de widget y un cliente falso. | `lib/features/tratante/tarjeta_resumen.dart` | 2 |

## María Belén: backend, Docker e IA de seguridad

María Belén es dueña del núcleo del backend (Docker, base de datos, alertas y el resumen como endpoint) y de las reglas que acotan al asistente: detección de riesgo, texto de crisis, filtro clínico, técnicas de relajación y contenido del módulo de ansiedad. El documento "Holo: Docker y Docker Compose" explica cómo hacer BE-01.

### Sprint 1: Docker, base de datos y seguridad (11 pts)

| ID | Tarea | Criterios de aceptación | Archivos | Pts |
| --- | --- | --- | --- | --- |
| BE-01 | **(Técnica)** Como equipo, queremos la base de datos en Docker y su conexión, para que todos trabajen con el mismo entorno. | `docker compose up -d db` levanta PostgreSQL 16 con pgvector con datos persistentes en un volumen. `app/db.py` crea el motor con SQLAlchemy desde `HOLO_URL_BASE_DATOS` y las tablas se crean al iniciar. `almacen.py` queda como fachada con un método por repositorio. `.env.example` y el README explican el arranque. Se integra el día 1. | `docker-compose.yml`, `app/db.py`, `app/services/almacen.py`, `.env.example` | 3 |
| HU-10 | Como usuario, quiero que el asistente no opine sobre diagnósticos ni medicación, para no recibir indicaciones que corresponden a un profesional. | `es_consulta_clinica(texto)` identifica los veinte casos del conjunto de prueba. La respuesta fija orienta hacia un profesional. Erick la conecta al flujo en HU-08b. | `app/services/filtros.py`, `tests/test_filtros.py` | 3 |
| HU-13 | Como usuario en una situación de riesgo, quiero que el sistema lo reconozca, para recibir ayuda adecuada de inmediato. | La revisión normaliza el texto (mayúsculas, tildes) y usa la lista de `data/expresiones_riesgo.txt`. Se agrega una lista de prueba de al menos quince expresiones, marcada como provisional, que detecta todos los casos de riesgo del conjunto de prueba. La aprobación de la especialista sigue pendiente. | `app/services/riesgo.py`, `data/expresiones_riesgo.txt` | 3 |
| HU-14 | Como usuario en una situación de riesgo, quiero un mensaje claro con recursos de ayuda, para saber a quién acudir. | El texto fijo y los recursos (ECU 911 y línea 171, opción 6) se leen de `data/texto_crisis.md`. La API devuelve ese texto sin intervención del modelo. Marcado como provisional. | `data/texto_crisis.md`, `app/services/riesgo.py` | 2 |

### Sprint 2: alertas, relajación, resumen, módulo y pruebas (14 pts)

| ID | Tarea | Criterios de aceptación | Archivos | Pts |
| --- | --- | --- | --- | --- |
| HU-16 | Como tratante, quiero que cada situación de riesgo quede registrada, para conocerla antes de la siguiente sesión. | La alerta guarda fecha, nivel y mensaje de origen. Solo el tratante vinculado puede consultarla; otro usuario recibe 403. `GET /tratante/paciente` devuelve las alertas guardadas. | `app/repositorios/alertas.py`, `app/api/routes/tratante.py` | 2 |
| HU-11 | Como usuario, quiero que el asistente me guíe en una técnica de relajación paso a paso, para calmarme en el momento. | Hay dos técnicas completas, respiración y anclaje al presente. `siguiente_paso(tecnica, paso, confirmacion)` avanza solo cuando el usuario confirma. Pruebas de ambas secuencias. El cambio mínimo en `chat.py` se acuerda con Erick. | `app/services/relajacion.py`, `tests/test_relajacion.py` | 3 |
| HU-12 | Como paciente con ansiedad, quiero contenido específico de mi módulo, para recibir apoyo acorde a mi tratamiento. | Hay al menos tres textos del módulo de ansiedad, con el material y las etiquetas de HU-07. Solo se usan con cuentas en modo paciente; la cuenta de usuaria estándar no los recibe. Una prueba lo verifica con ambas cuentas. | `data/material/ansiedad_*.md`, filtro en `recuperacion.py` (acordado con Erick) | 3 |
| HU-17b | Como tratante, quiero solicitar el resumen de mi paciente desde la API, para consultarlo en la aplicación. | `POST /resumen` toma los mensajes de los últimos siete días, invoca `generar_resumen` y guarda el último resumen. Solo el tratante vinculado puede solicitarlo (403 en otro caso). Hasta que exista la función de Erick, se usa un doble de prueba. `odds/resumen.md` actualizado. | `app/api/routes/resumen.py`, `app/repositorios/resumenes.py` | 3 |
| HU-21 | **(Técnica)** Como equipo, queremos un conjunto de mensajes de prueba, para verificar los criterios de aceptación de la entrega. | El conjunto incluye al menos cuarenta mensajes de riesgo, de diagnóstico o medicación y habituales. Un script los evalúa y deja los resultados en `docs/resultados-pruebas.md`. La revisión de la especialista queda pendiente. | `tests/datos/mensajes_prueba.json`, `scripts/evaluar_mensajes.py` | 3 |

## Sprint 1: tareas de las parejas (43 pts)

Cada integrante tiene al menos una tarea de front y una de back, con la excepción de Karol, que se incorpora a los repositorios más adelante. Los mockups se entregan en Figma (o la herramienta que el equipo elija) con vínculo en el pull request. Las pantallas no esperan a los mockups: parten del tema ya definido en `lib/app.dart` y se ajustan después.

| ID | Resp. | Pareja | Tarea | Criterios de aceptación | Archivos o entregable | Pts |
| --- | --- | --- | --- | --- | --- | --- |
| BE-02 | Álvaro | A | Como equipo, queremos las cuentas de demostración guardadas, para mostrar los dos tipos de usuario sin implementar registro (HU-04). | Existen Ana (usuaria estándar), Luis (paciente vinculado a la tratante) y la tratante, creadas al iniciar si no existen. Persisten en la base de datos. Pruebas con SQLite en memoria. | `app/repositorios/usuarios.py` | 2 |
| BE-03 | Jose | A | Como aplicación, quiero registrar el consentimiento en el backend, para conservar la fecha de aceptación (HU-03). | `POST /consentimiento` guarda la fecha y se conserva tras reiniciar. Sin consentimiento, `POST /chat` responde 403. Pruebas con SQLite en memoria. | `app/repositorios/consentimientos.py`, `app/api/routes/consentimiento.py` | 2 |
| HU-02 | Álvaro | A | Como usuario, quiero leer y aceptar el consentimiento informado, para saber qué es Holo y qué datos se guardan. | El botón de continuar está desactivado hasta aceptar el texto y declarar mayoría de edad. Al continuar llama a `POST /consentimiento`. Sin aceptar no se llega al chat. El texto indica que Holo no reemplaza a un profesional ni a un servicio de emergencia y se marca como provisional. | `lib/features/consentimiento/` | 3 |
| FE-07 | Jose | A | Como usuario, quiero acceder a los recursos de ayuda desde la conversación, para contactarlos en cualquier momento. | El widget `RecursosAyuda` muestra ECU 911 y la línea 171, opción 6, y permite llamar a cada uno. Se abre desde un botón de la pantalla de conversación. Con pruebas. | `lib/features/crisis/recursos_ayuda.dart` | 2 |
| FE-05 | Damien | B | Como usuario, quiero ver los mensajes de la conversación con claridad, para distinguir lo que escribí de lo que respondió el asistente. | Widgets `BurbujaMensaje` (usuario y asistente), `ListaMensajes` e `IndicadorEscribiendo`, sin llamadas a la API y con pruebas de widget. | `lib/features/chat/widgets/` | 3 |
| BE-04 | Damien | B | Como usuario, quiero que mi conversación se conserve, para retomarla después (HU-06). | `POST /chat` y `GET /chat/historial` guardan y devuelven los mensajes en orden según `odds/`. Los mensajes sobreviven al reinicio del servidor. Pruebas con SQLite en memoria. | `app/repositorios/mensajes.py` | 3 |
| BE-16 | Damien | B | Como equipo, queremos validar los mensajes del chat, para evitar entradas vacías o excesivas. | Un mensaje vacío o de más de 2000 caracteres devuelve 422 con un mensaje claro. Pruebas de ambos límites. | `app/schemas/chat.py`, `tests/test_validacion.py` | 2 |
| FE-06 | Justin | B | Como usuario, quiero una pantalla de conversación con mi historial, para retomar lo que he escrito (HU-05). | Ensambla FE-05 y un campo de envío. Al abrirla carga el historial; al enviar muestra el indicador hasta recibir respuesta. Un error de red muestra un mensaje y permite reintentar. Prueba con cliente falso. | `lib/features/chat/chat_screen.dart` | 3 |
| BE-14 | Justin | B | Como aplicación, quiero errores con un formato único, para mostrarlos sin tratar cada caso. | Los errores 401, 403, 422 y 500 devuelven `{"error": {"codigo", "mensaje"}}`. El formato queda descrito en `odds/README.md`. Con pruebas. | `app/core/errores.py`, `app/main.py` | 2 |
| FE-01 | Jampier | C | Como equipo, queremos las carpetas de plataforma de Flutter, para ejecutar la aplicación. | Se ejecuta `flutter create --org com.holo --project-name holo_app --platforms android,web .`; luego `flutter pub get`, `flutter analyze` y `flutter test` sin errores. Se integra el día 1. | `android/`, `web/` | 1 |
| FE-02 | Jampier | C | Como equipo, queremos un cliente de la API con modo simulado, para construir las pantallas sin el backend. | Una interfaz con implementación real y otra simulada que responde con los ejemplos de `odds/` (incluida una respuesta de crisis). Se elige con `--dart-define=USAR_SIMULACION=true`. Con pruebas. | `lib/core/api_client.dart`, `lib/core/api_simulado.dart` | 2 |
| CI-01 | Jampier | C | Como equipo, queremos verificación automática en cada pull request del backend, para cumplir la definición de terminado. | Un flujo de GitHub Actions ejecuta `ruff format --check .`, `ruff check .` y `pytest` en cada pull request hacia `develop`. | `.github/workflows/ci.yml` (backend) | 2 |
| BE-07a | Imanol | C | Como equipo, queremos siete días de conversaciones ficticias de Luis, para que el resumen tenga contenido. | Un archivo con al menos tres mensajes por día, un episodio de ansiedad, uno de sueño y un mensaje de riesgo. Cada registro está identificado como ficticio. Se entrega hacia el día 3 porque HU-17a lo usa. | `data/conversaciones_luis.json` | 2 |
| CI-02 | Imanol | C | Como equipo, queremos verificación automática en cada pull request del front, para cumplir la definición de terminado. | Un flujo de GitHub Actions ejecuta `dart format --set-exit-if-changed .`, `flutter analyze` y `flutter test` en cada pull request hacia `develop`. | `.github/workflows/ci.yml` (front) | 2 |
| BE-15 | Imanol | C | Como equipo, queremos registros sin datos personales, para cumplir con la protección de datos de salud. | La configuración de logs nunca escribe el texto de los mensajes. El nivel se define por variable de entorno. Una prueba confirma que el texto de un mensaje no aparece en los registros. | `app/core/logging.py` | 2 |
| UX-01 | Karol | C | Como equipo, queremos una guía de estilo, para que todas las pantallas se vean coherentes. | Define paleta (parte de `#25706A`), tipografías, espaciados, botones, campos y burbujas de mensaje. Los pares de color de texto y fondo cumplen un contraste mínimo de 4.5 a 1. Textos legibles en móvil. | Archivo de diseño y `docs/guia-estilo.md` | 2 |
| UX-02 | Karol | C | Como equipo, queremos los mockups de consentimiento y conversación, para construir esas pantallas con un diseño definido. | Incluyen el estado normal, vacío, cargando y de error de la conversación, y el acceso a los recursos de ayuda. Se entregan hacia el día 2. | Archivo de diseño | 3 |
| UX-03 | Karol | C | Como equipo, queremos los mockups de la pantalla de crisis y de la vista del tratante, para construirlas en el sprint 2. | La pantalla de crisis es sobria, sin elementos distractores y con los dos recursos visibles. La vista del tratante muestra alertas, resumen y el botón de nuevo resumen. El tono de la pantalla de crisis queda pendiente de revisión por la especialista. | Archivo de diseño | 3 |
| DOC-01 | Karol | C | Como equipo, queremos el texto del consentimiento y del aviso de privacidad, para que HU-02 lo muestre. | Texto en español formal que explica qué es Holo, qué datos se guardan, quién los ve, la mayoría de edad y que no reemplaza a un profesional ni a un servicio de emergencia. Cita la LOPDP. Marcado como provisional hasta una revisión legal. | `docs/consentimiento.md` | 2 |

## Sprint 2: tareas de las parejas (22 pts)

Las parejas rotan: cada integrante trabaja con personas distintas a las del sprint 1 y vuelve a tocar front y back.

| ID | Resp. | Pareja | Tarea | Criterios de aceptación | Archivos o entregable | Pts |
| --- | --- | --- | --- | --- | --- | --- |
| HU-15 | Damien | D | Como usuario en una situación de riesgo, quiero ver una pantalla de crisis con los recursos de ayuda, para contactarlos fácilmente. | Aparece cuando la respuesta del chat es de tipo `crisis`. Muestra el texto fijo recibido y reutiliza `RecursosAyuda`. No ofrece técnicas ni campo de escritura. Con pruebas. | `lib/features/crisis/crisis_screen.dart` | 3 |
| BE-06 | Álvaro | D | Como equipo, queremos registrar cada respuesta con su revisión de riesgo y sus fragmentos, para auditar al asistente (HU-19). | `registrar_respuesta(usuario, riesgo, fragmentos)` guarda los tres datos. Erick la invoca desde HU-08b. Pruebas con SQLite en memoria. | `app/repositorios/auditoria.py` | 2 |
| UX-04 | Álvaro | D | Como equipo, queremos una prueba de usabilidad breve, para detectar confusiones antes de la demostración. | Tres personas adultas ajenas al equipo recorren consentimiento y conversación con datos ficticios. Se registran las dificultades y las correcciones acordadas en un documento de una página. | `docs/prueba-usabilidad.md` | 2 |
| FE-10 | Jampier | E | Como tratante, quiero ver las alertas de mi paciente, para conocerlas antes de la sesión. | Widget `ListaAlertas` con fecha, nivel y mensaje de origen, y un estado vacío. Con pruebas. | `lib/features/tratante/lista_alertas.dart` | 2 |
| BE-07b | Jampier | E | Como equipo, queremos cargar las conversaciones ficticias en la base, para la demostración (HU-20). | El script carga `conversaciones_luis.json` mediante el repositorio de mensajes y puede ejecutarse varias veces sin duplicar. Requiere BE-04. | `scripts/cargar_datos_ficticios.py` | 1 |
| FE-12 | Jose | E | Como tratante, quiero una vista con las alertas y el resumen, para consultarlos desde la aplicación (HU-18). | Ensambla FE-10 y FE-11 y agrega el botón para generar un resumen nuevo (`POST /resumen`) con indicador de carga. No muestra la conversación. Prueba con cliente falso. | `lib/features/tratante/tratante_screen.dart` | 2 |
| BE-08 | Jose | E | Como equipo, queremos que `odds/openapi.json` no quede desactualizado, para que sea confiable. | Una prueba falla si el archivo difiere del que genera la aplicación. | `tests/test_openapi.py` | 1 |
| FE-13 | Justin | F | Como equipo, queremos la aplicación probada contra el backend real, para confirmar que ambos respetan el contrato. | Con el backend de `develop` en local y la base en Docker se recorren tres casos: conversación de Ana, mensaje de riesgo de Luis y vista de la tratante. Cada diferencia con `odds/` se registra como incidencia. Requiere HU-08b y HU-17b integradas. | Incidencias | 2 |
| BE-19 | Justin | F | Como equipo, queremos una revisión de seguridad básica, para no exponer claves ni datos. | Se revisa `.gitignore`, `.env.example`, las credenciales de Docker Compose, CORS por variable de entorno y la ausencia de datos reales. Los hallazgos y correcciones quedan en `docs/seguridad.md`. | `docs/seguridad.md` | 2 |
| BE-17 | Imanol | F | Como equipo, queremos una prueba de extremo a extremo, para detectar roturas entre módulos. | Con el proveedor de prueba: consentimiento, mensaje habitual, mensaje de riesgo, alerta visible para la tratante y resumen. Se escribe al final del sprint. | `tests/test_flujo_completo.py` | 2 |
| HU-22 | Karol | F | Como equipo, queremos la presentación formal y el guion de la demostración, para exponer la idea con claridad. | El guion cubre a Ana (conversación), Luis (crisis) y la tratante (resumen). Se ejecuta completo dos veces seguidas y existe una grabación de respaldo. Declara que el material es provisional y los datos ficticios. El guion y la presentación pueden comenzar ya; la grabación va al final. | `docs/guion-demostracion.md` | 3 |

## Historias opcionales

Se toman solo cuando el responsable terminó sus tareas imprescindibles. No están incluidas en los 115 puntos.

| ID | Tarea | Resp. | Pts |
| --- | --- | --- | --- |
| BE-12 | Endpoint para destacar un mensaje y mostrarlo aparte en el resumen (HU-23, parte de backend) | Jampier | 2 |
| FE-14 | Acción para destacar un mensaje en la conversación (HU-23, parte de front) | Damien | 2 |
| BE-13 | Endpoint de registro de ánimo diario del 1 al 5 con nota opcional (HU-25, parte de backend) | Álvaro | 2 |
| FE-15 | Pantalla de registro de ánimo diario (HU-25, parte de front) | Justin | 2 |
| HU-24 | Segunda revisión de riesgo realizada por el modelo; si cualquiera de las dos revisiones detecta riesgo alto, se trata como tal | María Belén | 5 |
| HU-26 | Backend publicado en internet, sin exponer claves | Imanol | 3 |

## Supuestos y puntos por confirmar

- **Base de datos.** Al usar Docker para la base, se reemplaza SQLite por PostgreSQL con pgvector y SQLAlchemy desde el sprint 1. Esto adelanta la migración que estaba prevista para la versión 1 (HU-40) y es la razón de que BE-01 pase de 1 a 3 puntos. El README, el diagrama de arquitectura y el documento de trabajo deben actualizarse.
- **GitHub.** Las siete invitaciones de la lista (alvarolopezmoya, Damienq7w, ElJoss09, ErickGuerron, jampiercamacho94-cloud, mxrajxse38 y Osyanne) figuran como pendientes de respuesta: nadie puede subir código hasta aceptarlas. Falta la invitación de Karol. María Belén es Mabe-Zapata, propietaria de ambos repositorios.
- **Nombres.** Los nombres de pila se tomaron de la cuenta o de la invitación; conviene confirmarlos.
- **Reparto.** Toda la IA queda con Erick y María Belén, por eso su carga (25 puntos cada uno) es mayor que la del resto (7 a 13). María Belén no tiene tareas de front en este plan; revisa pull requests de front como parte de su rol.
- **Coordinación.** Se asume que María Belén, como propietaria de los repositorios, coordina el proyecto además de sus tareas y aprueba las integraciones a \`main\`; si otra persona coordina, conviene indicarlo.
- **Lista de riesgo.** La lista de expresiones de HU-13 es de prueba, redactada por el equipo y marcada como provisional. Hasta que la especialista la apruebe, no debe presentarse como detección validada. Esto cambia lo acordado antes, cuando la lista quedaba vacía.
- **Estimaciones.** Provienen del product backlog; las tareas con prefijos BE, FE, UX, CI y DOC son nuevas o divididas y deben revisarse en la planificación de cada sprint.
- **Flutter.** El código nunca se compiló: FE-01 puede revelar errores que habrá que corregir.
- **Pendientes externos.** La clave gratuita de Gemini o Groq (el día 1), el material de la especialista, el texto de crisis aprobado y el protocolo del tratante.
