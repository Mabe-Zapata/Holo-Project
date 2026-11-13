# Proyecto Holo: product backlog

Versión 1.0 · 12 de noviembre de 2026

El presente documento contiene el product backlog del proyecto Holo. Reúne 45 historias organizadas en siete épicas: 22 conforman la primera entrega (MVP), distribuidas en dos sprints de una semana; 4 son opcionales dentro del plazo, y 19 corresponden a versiones posteriores.

La numeración de los requerimientos (RF, RNF) corresponde a la especificación de requerimientos de software. El alcance de la primera entrega se describe en `documento-de-trabajo-equipo.md`.

## 1. Convenciones

### 1.1 Formato de las historias

Cada historia de usuario se redacta con la forma «Como [rol], quiero [acción], para [beneficio]» e incluye criterios de aceptación verificables. Las historias técnicas, que no aportan valor directo al usuario pero son necesarias, se identifican con la etiqueta **(Técnica)**.

### 1.2 Prioridad

| Prioridad | Significado |
| --- | --- |
| Imprescindible | Sin esta historia, la demostración no puede presentarse |
| Importante | Aporta valor claro, pero la demostración funciona sin ella |
| Deseable | Se aborda solo si el tiempo lo permite |
| Posterior | Fuera de la primera entrega |

### 1.3 Estimación

Las estimaciones se expresan en puntos de historia con la escala 1, 2, 3, 5, 8. Son una propuesta inicial: el equipo debe revisarlas en la planificación de cada sprint, dado que aún no se conoce su velocidad real.

### 1.4 Repositorios y roles

| Abreviatura | Significado |
| --- | --- |
| Back | Repositorio `Holo-project` (FastAPI) |
| Front | Repositorio `Holo-project-front` (Flutter) |
| R1 | Coordinación y presentación |
| R2 | Aplicación: conversación |
| R3 | Aplicación: crisis y tratante |
| R4 | Backend |
| R5 | Inteligencia artificial: conocimiento |
| R6 | Inteligencia artificial: riesgo y resumen |

### 1.5 Definición de preparado

Una historia puede entrar a un sprint cuando:

- Su redacción y sus criterios de aceptación son comprendidos por todo el equipo.
- Tiene estimación y responsable.
- Sus dependencias están resueltas o planificadas dentro del mismo sprint.
- Si requiere material o textos de la especialista, estos se encuentran disponibles o existe una versión provisional.

### 1.6 Definición de terminado

Una historia se considera terminada cuando:

- Cumple todos sus criterios de aceptación.
- El código fue integrado a `develop` mediante un pull request aprobado por al menos un integrante distinto del autor.
- Las pruebas automáticas y el análisis estático se ejecutan sin errores.
- La documentación afectada fue actualizada (en particular, la carpeta `odds/` cuando cambia un endpoint).
- No contiene claves, datos reales ni material sin identificar como provisional.

## 2. Épicas

| ID | Épica | Objetivo | Requerimientos |
| --- | --- | --- | --- |
| E1 | Acceso y consentimiento | El usuario ingresa de forma informada y con el modo de uso correcto | RF-01 a RF-06 |
| E2 | Conversación de apoyo | El asistente responde desde material aprobado y dentro de sus límites | RF-07 a RF-16 |
| E3 | Seguimiento y resumen | El tratante recibe un resumen útil del periodo | RF-17 a RF-22 |
| E4 | Riesgo y derivación | Ninguna situación de riesgo queda sin respuesta ni registro | RF-23 a RF-29 |
| E5 | Vista del tratante | El tratante consulta alertas y resúmenes de sus pacientes | RF-30 a RF-32 |
| E6 | Conocimiento y auditoría | El material es trazable y cada respuesta queda registrada | RF-33 a RF-35 |
| E7 | Base técnica y entrega | El equipo dispone de entornos, pruebas y una demostración lista | RNF-06, RNF-12, RNF-13 |

## 3. Sprint 1: conversación completa (días 1 a 5)

**Objetivo del sprint:** que un usuario acepte el consentimiento y converse desde la aplicación con un asistente que responde a partir del material y respeta sus límites.

Total estimado: 42 puntos.

| ID | Historia | Criterios de aceptación | Prioridad | Rol | Repo | Ref. | Pts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HU-01 | **(Técnica)** Como equipo, queremos los entornos de desarrollo instalados y los repositorios configurados, para comenzar a trabajar sin bloqueos. | Cada integrante ejecuta el backend y la aplicación en su equipo. La rama `develop` existe en ambos repositorios. La clave gratuita del modelo fue verificada. | Imprescindible | Todos | Ambos | E7 | 2 |
| HU-02 | Como usuario, quiero leer y aceptar el consentimiento informado antes de usar la aplicación, para saber qué es Holo y qué datos se guardan. | Sin aceptar y declarar mayoría de edad no se accede a la conversación. El texto indica que Holo no reemplaza a un profesional ni a un servicio de emergencia. | Imprescindible | R2 | Front | RF-02 | 3 |
| HU-03 | **(Técnica)** Como aplicación, quiero registrar el consentimiento en el backend, para conservar la fecha de aceptación. | `POST /consentimiento` guarda la fecha. Sin consentimiento, `POST /chat` responde 403. | Imprescindible | R4 | Back | RF-02 | 2 |
| HU-04 | **(Técnica)** Como equipo, queremos cuentas de demostración con su modo de uso, para mostrar los dos tipos de usuario sin implementar registro. | Existen las cuentas Ana (usuaria estándar), Luis (paciente) y la tratante. Luis está vinculado a la tratante. Los datos persisten en SQLite. | Imprescindible | R4 | Back | RF-03 | 2 |
| HU-05 | Como usuario, quiero una pantalla de conversación con mi historial, para retomar lo que he escrito. | Los mensajes se muestran en orden. Al reabrir la aplicación aparece el historial. Se indica cuando el asistente está respondiendo. Los recursos de ayuda son accesibles desde la pantalla. | Imprescindible | R2 | Front | RF-07 | 5 |
| HU-06 | **(Técnica)** Como aplicación, quiero enviar mensajes y consultar el historial mediante la API, para que la conversación se conserve. | `POST /chat` y `GET /chat/historial` funcionan según la carpeta `odds/`. Los mensajes persisten en SQLite. | Imprescindible | R4 | Back | RF-07 | 3 |
| HU-07 | Como administrador, quiero cargar el material de la especialista con etiquetas de tema, modo y módulo, para que el asistente pueda consultarlo. | Un script carga entre 5 y 10 textos. Cada fragmento conserva sus etiquetas y su estado (provisional o aprobado). Una búsqueda por tema recupera el documento. | Imprescindible | R5 | Back | RF-33 | 5 |
| HU-08 | Como usuario, quiero que el asistente responda a partir del material aprobado, para recibir orientación confiable. | Cada respuesta registra al menos un fragmento empleado. Sin fragmento pertinente, el asistente indica que no puede ayudar con esa consulta y orienta hacia un profesional. | Imprescindible | R5 | Back | RF-08 | 8 |
| HU-09 | **(Técnica)** Como equipo, queremos el modelo de lenguaje encapsulado en una interfaz, para cambiar de proveedor sin modificar el resto del sistema. | Existe un proveedor real (Gemini o Groq) además del proveedor de prueba. El cambio se realiza con una variable de entorno. La clave se lee del archivo `.env`. | Imprescindible | R5 | Back | RNF-12 | 3 |
| HU-10 | Como usuario, quiero que el asistente no opine sobre diagnósticos ni medicación, para no recibir indicaciones que corresponden a un profesional. | Se rechazan todos los casos del conjunto de prueba. La respuesta orienta hacia un profesional. | Imprescindible | R5 | Back | RF-09 | 3 |
| HU-11 | Como usuario, quiero que el asistente me guíe en una técnica de relajación paso a paso, para calmarme en el momento. | Se dispone de dos técnicas completas: respiración y anclaje al presente. El asistente espera la confirmación del usuario entre pasos. | Imprescindible | R5 | Back | RF-10 | 3 |
| HU-12 | Como paciente con ansiedad, quiero contenido específico de mi módulo, para recibir apoyo acorde a mi tratamiento. | El material del módulo de ansiedad solo se emplea con cuentas en modo paciente. La cuenta de usuaria estándar no lo recibe. | Importante | R5 | Back | RF-11 | 3 |

## 4. Sprint 2: riesgo, resumen y presentación (días 6 a 10)

**Objetivo del sprint:** que una situación de riesgo active la respuesta de crisis y una alerta, que la tratante consulte el resumen semanal, y que la demostración quede ensayada.

Total estimado: 34 puntos.

| ID | Historia | Criterios de aceptación | Prioridad | Rol | Repo | Ref. | Pts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HU-13 | Como usuario en una situación de riesgo, quiero que el sistema lo reconozca, para recibir ayuda adecuada de inmediato. | Cada mensaje se revisa antes de consultar al modelo. Se identifican como riesgo alto todos los mensajes de riesgo del conjunto de prueba. La lista de expresiones fue aprobada por la especialista. | Imprescindible | R6 | Back | RF-23 | 3 |
| HU-14 | Como usuario en una situación de riesgo, quiero recibir un mensaje claro con recursos de ayuda, para saber a quién acudir. | Ante riesgo alto, la API devuelve el texto fijo con ECU 911 y línea 171, opción 6. El modelo no interviene en esa respuesta. El texto fue aprobado por la especialista. | Imprescindible | R6 | Back | RF-24 | 2 |
| HU-15 | Como usuario en una situación de riesgo, quiero ver una pantalla de crisis con los recursos de ayuda, para contactarlos fácilmente. | La pantalla muestra el texto fijo y permite llamar a cada recurso. El asistente no propone técnicas. | Imprescindible | R3 | Front | RF-24 | 3 |
| HU-16 | Como tratante, quiero que cada situación de riesgo quede registrada, para conocerla antes de la siguiente sesión. | La alerta guarda fecha, nivel y mensaje de origen. Solo el tratante vinculado puede consultarla. | Imprescindible | R4 | Back | RF-25 | 2 |
| HU-17 | Como tratante, quiero un resumen de la semana de mi paciente con hechos específicos, para preparar la sesión sin reconstruir lo ocurrido. | `POST /resumen` genera el resumen de los últimos siete días. Cada hecho indica el día de la conversación de origen. No contiene diagnósticos ni recomendaciones clínicas. Indica que fue generado por IA. | Imprescindible | R6 | Back | RF-19 | 8 |
| HU-18 | Como tratante, quiero una vista con las alertas y el resumen de mi paciente, para consultarlos desde la aplicación. | La vista muestra las alertas y el último resumen. Permite generar un resumen nuevo. No muestra la conversación. | Imprescindible | R3 | Front | RF-30 | 5 |
| HU-19 | **(Técnica)** Como equipo, queremos registrar cada respuesta con su revisión de riesgo y sus fragmentos, para auditar el comportamiento del asistente. | Por cada respuesta se conserva el resultado de la revisión de riesgo y los fragmentos empleados. | Importante | R4 | Back | RF-35 | 2 |
| HU-20 | **(Técnica)** Como equipo, queremos una semana de conversaciones ficticias cargada para Luis, para que el resumen tenga contenido en la demostración. | Un script carga los datos. Los datos son ficticios y están identificados como tales. | Imprescindible | R1 | Back | E7 | 3 |
| HU-21 | **(Técnica)** Como equipo, queremos un conjunto de mensajes de prueba, para verificar los criterios de aceptación de la entrega. | El conjunto incluye mensajes de riesgo, consultas de diagnóstico y medicación, y mensajes habituales. Fue revisado por la especialista. Los resultados quedan documentados. | Imprescindible | R6 | Back | E7 | 3 |
| HU-22 | Como equipo, queremos la presentación formal y el guion de la demostración, para exponer la idea con claridad. | El guion se ejecuta completo dos veces consecutivas. Existe una grabación de respaldo. La presentación declara que el material es provisional y los datos son ficticios. | Imprescindible | R1 | Ninguno | E7 | 3 |

## 5. Historias opcionales dentro del plazo

Se abordan únicamente si las historias imprescindibles están terminadas.

| ID | Historia | Criterios de aceptación | Rol | Repo | Ref. | Pts |
| --- | --- | --- | --- | --- | --- | --- |
| HU-23 | Como paciente, quiero destacar un mensaje para mi tratante, para asegurarme de que conozca lo que considero importante. | Lo destacado llega al tratante en una sección aparte del resumen. | R2, R4 | Ambos | RF-20 | 3 |
| HU-24 | **(Técnica)** Como equipo, queremos una segunda revisión de riesgo realizada por el modelo, para reducir los casos no detectados. | Si cualquiera de las dos revisiones identifica riesgo alto, se trata como riesgo alto. | R6 | Back | RF-23 | 5 |
| HU-25 | Como usuario, quiero registrar mi estado de ánimo diario, para observar mi evolución. | Se registra un valor de 1 a 5 y una nota opcional. El registro aparece en el resumen. | R2, R4 | Ambos | RF-17 | 3 |
| HU-26 | **(Técnica)** Como equipo, queremos el backend publicado en internet, para presentar la demostración sin depender de la red local. | La aplicación se conecta al backend publicado. Las claves no quedan expuestas. | R4 | Back | E7 | 3 |

## 6. Versión 1 (posterior a la primera entrega)

Estas historias se refinarán cuando se apruebe la continuidad del proyecto. No tienen estimación.

| ID | Historia | Épica | Ref. |
| --- | --- | --- | --- |
| HU-27 | Como usuario, quiero registrarme e iniciar sesión con correo y contraseña, para proteger mi información. | E1 | RF-01 |
| HU-28 | Como paciente, quiero vincularme con mi tratante mediante un código, para compartirle mis resúmenes. | E1 | RF-04 |
| HU-29 | Como usuario, quiero responder un cuestionario inicial breve, para que el asistente se adapte a mí. | E1 | RF-05 |
| HU-30 | Como usuario, quiero eliminar mi cuenta y mis datos, para ejercer control sobre mi información. | E1 | RF-06 |
| HU-31 | Como usuario, quiero ajustar cuánto me sugiere el asistente, para que me escuche sin proponerme técnicas cuando no las deseo. | E2 | RF-12 |
| HU-32 | Como usuario, quiero que el asistente recuerde lo relevante de sesiones anteriores, para no repetir mi situación. | E2 | RF-13 |
| HU-33 | Como usuario de largo plazo, quiero que el asistente me sugiera atención profesional ante un malestar sostenido, para no depender únicamente de la aplicación. | E2 | RF-14 |
| HU-34 | Como tratante, quiero definir la fecha de la próxima sesión, para que el resumen cubra exactamente el periodo. | E3 | RF-18 |
| HU-35 | Como paciente, quiero poder solicitar el envío de la conversación completa a mi tratante, para decidir qué comparto. | E3 | RF-21 |
| HU-36 | Como usuario con malestar intenso, quiero que el asistente reduzca las sugerencias y priorice la contención, para sentirme acompañado. | E4 | RF-26 |
| HU-37 | Como tratante, quiero recibir un aviso cuando se registra una alerta, para enterarme sin abrir la aplicación. | E4 | RF-27 |
| HU-38 | Como tratante, quiero configurar el módulo, el nivel de sugerencia y las técnicas permitidas de cada paciente, para alinear el asistente con el tratamiento. | E5 | RF-31 |
| HU-39 | Como especialista, quiero aprobar cada documento antes de que el asistente lo utilice, para garantizar su validez. | E6 | RF-34 |
| HU-40 | **(Técnica)** Como equipo, queremos migrar a PostgreSQL con pgvector, para soportar múltiples usuarios. | E7 | RNF-13 |

## 7. Futuro

| ID | Historia | Épica | Ref. |
| --- | --- | --- | --- |
| HU-41 | Como usuario, quiero conversar por voz, para expresarme con mayor comodidad. | E2 | RF-15 |
| HU-42 | Como paciente con otro diagnóstico, quiero un módulo especializado para mi trastorno, para recibir apoyo específico. | E2 | RF-16 |
| HU-43 | Como tratante, quiero anotar el resumen y exportarlo a PDF, para incorporarlo a mis registros. | E3 | RF-22 |
| HU-44 | Como usuario, quiero ser derivado a psicólogos reales registrados en el sistema, para iniciar una atención profesional. | E4, E5 | RF-28, RF-32 |
| HU-45 | Como usuario, quiero registrar un contacto de confianza, para que se me ofrezca llamarlo ante una situación de riesgo. | E4 | RF-29 |

## 8. Dependencias externas

| Dependencia | Historias afectadas | Estado |
| --- | --- | --- |
| Material de la especialista sobre ansiedad y estrés | HU-07, HU-08, HU-11, HU-12 | Pendiente; se trabaja con material provisional |
| Lista de expresiones de riesgo y texto de crisis | HU-13, HU-14, HU-15, HU-21 | Pendiente de redacción y aprobación |
| Protocolo de actuación del tratante ante una alerta | HU-16, HU-18 | Pendiente |
| Elección del proveedor gratuito del modelo | HU-09 | Pendiente; se decide el día 1 |
| Asignación nominal de los seis roles | Todas | Pendiente; se define en la primera reunión |
