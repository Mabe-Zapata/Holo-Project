# Holo: especificación del sprint 1

Nov 14, 2026 · @Maria Zapata

Este documento explica, para quien se incorpora al proyecto, qué se construye en el sprint 1 (del 16 al 20 de noviembre de 2026), por qué se construye así y qué debe hacer cada persona; se puede leer completo sin conocer Holo de antemano.

## Qué es Holo y por qué existe

Holo (nombre provisional) es una aplicación móvil de apoyo emocional con un asistente conversacional. Quien la usa escribe lo que le preocupa y el asistente responde con orientación y técnicas de relajación, siempre a partir de material que una especialista en psicología revisó y aprobó. El asistente no inventa contenido ni reemplaza a un profesional.

Hay dos tipos de usuario:

- **Usuario estándar.** Una persona adulta sin tratante, que usa la aplicación a diario para conversar y practicar técnicas de relajación.
- **Paciente.** Una persona adulta con un psicólogo o psicóloga que la atiende (el tratante). El tratante no lee la conversación por defecto: recibe un resumen semanal con hechos concretos y alertas si hubo situaciones de riesgo.

Holo no diagnostica ni habla de medicación. Si detecta una situación de riesgo, deja de sugerir técnicas, muestra un texto fijo con los números de ayuda (ECU 911 y la línea 171, opción 6) y registra una alerta para el tratante.

El primer módulo especializado es el de ansiedad, y el proyecto se presenta primero como una demostración formal de la idea, no como un producto para usuarios reales.

## Objetivo del sprint 1

Al terminar el sprint, una persona debe poder aceptar el consentimiento informado y conversar desde la aplicación con un asistente que responde a partir del material y respeta sus límites, sobre una base técnica ordenada que el sprint 2 pueda ampliar.

El viernes 20 de noviembre se hace una demostración interna con este recorrido:

1. Ana, usuaria estándar, abre la aplicación y elige su cuenta de demostración.
2. Lee el consentimiento, declara que es mayor de edad y lo acepta.
3. Escribe una consulta de ansiedad y recibe una respuesta basada en un fragmento del material.
4. Cierra y reabre la aplicación: su conversación sigue ahí.
5. Pregunta por un medicamento: el asistente se niega y la orienta hacia un profesional.
6. Escribe algo fuera del material: el asistente reconoce que no puede ayudar con eso.
7. Escribe un mensaje de riesgo: recibe el texto fijo con ECU 911 y la línea 171, opción 6, y se registra una alerta.

Quedan fuera del sprint 1 el resumen semanal, la vista del tratante, la pantalla de crisis completa, el registro con correo y contraseña y la publicación en internet. Todos los datos son ficticios y todos los textos sensibles son provisionales.

El plan suma 67 puntos de historia. Un punto mide la complejidad relativa de una tarea, no las horas que toma: 1 es casi trivial y 8 es la tarea más compleja del plan. Sirve para repartir el trabajo, no para evaluar a nadie.

## Cómo funciona por dentro: el recorrido de un mensaje

Holo tiene tres piezas: la **aplicación** (Flutter, en el celular), el **backend** (FastAPI, un servidor que recibe peticiones) y la **base de datos** (PostgreSQL, en Docker). El backend además se comunica con un **modelo de lenguaje** externo (Gemini o Groq, con plan gratuito). Cuando el usuario envía un mensaje ocurre esto, siempre en este orden:

1. La aplicación envía el mensaje al endpoint `POST /chat` junto con la cuenta que lo escribe (tarea FE-06).
2. El backend valida que el mensaje no esté vacío ni sea excesivo (BE-16) y que el usuario haya aceptado el consentimiento; si no, responde 403 (BE-03).
3. Guarda el mensaje en la base de datos (BE-04).
4. **Revisa el riesgo antes de consultar al modelo** (HU-13). Si hay riesgo alto, el flujo se corta aquí: devuelve el texto fijo de crisis con los números de ayuda (HU-14) y registra una alerta para el tratante (sprint 2). El modelo no interviene.
5. Revisa si el mensaje pide un diagnóstico o habla de medicación (HU-10). Si es así, responde con un texto fijo que orienta hacia un profesional.
6. Busca en el material los fragmentos relacionados con la consulta (HU-08a). Si ninguno es pertinente, responde que no puede ayudar con eso y orienta hacia un profesional, sin llamar al modelo.
7. Si hay fragmentos, arma la petición al modelo con el prompt del sistema (IA-01), los fragmentos y el mensaje, y le pide una respuesta (HU-09).
8. Guarda la respuesta junto con los fragmentos usados y devuelve el resultado a la aplicación, que lo muestra (FE-05 y FE-06).

El orden es una decisión de seguridad: lo más delicado (el riesgo) se resuelve con reglas fijas y revisables, antes de que un modelo pueda improvisar. Esta forma de trabajar, donde el modelo solo redacta a partir de material aprobado, se llama RAG y es lo que evita que el asistente invente contenido.

En el sprint 1 se construyen los pasos 1 a 7 de forma separada y probada; la conexión definitiva de todo el flujo en `chat.py` la hace Erick en el sprint 2 (HU-08b), porque hasta entonces el proveedor de prueba, que repite el mensaje, mantiene funcionando la conversación.

## Glosario para quien empieza

| Término | Qué significa | Dónde lo verás |
| --- | --- | --- |
| Repositorio | Carpeta de un proyecto con todo su historial de cambios en Git. Holo tiene dos: `Holo-project` (backend) y `Holo-project-front` (aplicación). | GitHub |
| Rama (branch) | Copia paralela del código donde se trabaja sin afectar la versión estable. | `feature/HU-xx-...` |
| Pull request (PR) | Solicitud para incorporar una rama a `develop`; otra persona la revisa antes. | GitHub |
| CI | Verificación automática (formato, análisis y pruebas) que corre en cada pull request. | CI-01, CI-02 |
| Flutter y widget | Flutter es el marco para construir la aplicación; un widget es cada pieza visual (un botón, una burbuja, una pantalla). | Repositorio del front |
| FastAPI y endpoint | FastAPI es el marco del backend; un endpoint es una dirección a la que la aplicación envía una petición, como `POST /chat`. | Repositorio del back |
| Contrato (`odds/`) | Carpeta con la descripción de cada endpoint: qué recibe y qué devuelve. Front y back se ponen de acuerdo ahí. | `Holo-project/odds/` |
| Cliente simulado | Versión de prueba del cliente de la API que responde con ejemplos, para construir pantallas sin el backend. | FE-02 |
| Docker y Docker Compose | Docker ejecuta programas en contenedores aislados; Compose describe varios contenedores en un archivo. Aquí levanta la base de datos. | BE-01 |
| PostgreSQL y pgvector | Base de datos relacional; pgvector es una extensión para guardar y buscar textos por similitud. | BE-01, HU-07 |
| SQLAlchemy y repositorio de datos | SQLAlchemy permite hablar con la base desde Python; un repositorio de datos es el módulo que lee y escribe un tipo de dato (mensajes, usuarios). | `app/repositorios/` |
| LLM (modelo de lenguaje) | Programa que genera texto a partir de una instrucción; aquí, Gemini o Groq. | HU-09 |
| Prompt | La instrucción que se le da al modelo: su rol, sus límites y la consulta. | IA-01 |
| RAG | Forma de usar el modelo: primero se buscan fragmentos de material aprobado y luego el modelo responde solo con ellos. | HU-07, HU-08 |
| Fragmento | Trozo del material con sus etiquetas de tema, modo y módulo. | HU-07 |
| Modo y módulo | El modo es el tipo de usuario (estándar o paciente); el módulo es la especialidad (ansiedad). | HU-12 |
| Provisional | Texto o dato que aún no aprobó la especialista; debe estar marcado como tal. | Consentimiento, crisis, material |
| Coautor | Persona que contribuyó a un commit sin ser quien lo registró; se indica con `Co-authored-by:`. | Commits de pareja |

## Cómo se trabaja

### Ramas y commits

El código estable vive en `main`; el trabajo integrado, en `develop`. Nadie escribe directamente en ninguna de las dos. Cada tarea se hace en una rama propia que sale de `develop` y se llama `feature/HU-xx-descripcion` (o `fix/`, `docs/`, `chore/` según el caso). Los mensajes de commit siguen el formato de Conventional Commits en español, por ejemplo `feat: agregar pantalla de consentimiento` o `fix: corregir el orden del historial`.

### Pull requests

La rama se incorpora a `develop` mediante un pull request que llena la plantilla del repositorio. Se integra solo cuando: la verificación automática pasa, al menos una persona distinta del autor lo aprobó, y se actualizó la documentación afectada (en especial `odds/` si cambió un endpoint). La integración se hace con *squash and merge*. El archivo `CONTRIBUTING.md` de cada repositorio detalla todo esto.

### Pair programming remoto por turnos

Cada pareja trabaja a distancia, sin necesidad de estar conectada todo el tiempo:

1. Una persona programa y la otra revisa; después cambian.
2. Quien programa trabaja en la rama, hace commits pequeños, la sube y abre un pull request en borrador con lo hecho y lo pendiente.
3. La pareja lee el borrador, comenta en GitHub, prueba la rama en su equipo y responde en medio día como máximo.
4. Quien revisó toma el siguiente turno sobre la misma rama y quien escribió pasa a revisar. En cada relevo conviene una llamada de 10 a 15 minutos para explicar lo hecho.
5. Cada tarea tiene un responsable que cierra el pull request; su pareja aparece como coautora con la línea `Co-authored-by:` en los commits.

El objetivo no es ir más rápido, sino que dos personas conozcan cada parte del código y que se detecten errores a tiempo.

### Definición de terminado

Una tarea está terminada cuando cumple sus criterios de aceptación, está integrada en `develop` con su pull request aprobado, la verificación automática pasa, la documentación quedó al día y no contiene claves ni datos reales. Un texto que aún no aprobó la especialista debe estar marcado como provisional.

### Autonomía

Cada tarea tiene sus propios archivos y sus propias pruebas, para que nadie espere a otro. Dos tareas de un punto sí las necesitan los demás y deben integrarse el lunes: BE-01 (Docker y conexión, María Belén) y FE-01 (carpetas de Flutter, Jampier). Si algo te bloquea más de medio día, avísalo en la reunión diaria o al canal del equipo; no es un fracaso, es parte del trabajo.

## Qué hace cada pareja

Cada tarea indica qué se construye, por qué importa y cómo sabrás que está lista. Los criterios completos y los archivos están en el documento "Holo: backlog del MVP por sprint y responsable".

### Pareja N: Erick y María Belén (IA y núcleo del backend)

**María Belén**

- **BE-01, base de datos en Docker (3 pts).** Levanta PostgreSQL en un contenedor y conecta el backend a él. Importa porque así todo el equipo comparte el mismo entorno y nadie instala la base a mano. Está lista cuando cualquier integrante ejecuta `docker compose up -d db` y el backend se conecta. Se integra el lunes porque otras tareas la usan; el documento "Holo: Docker y Docker Compose" la explica paso a paso.
- **HU-13, detección de riesgo (3 pts).** Mejora la revisión que corre antes del modelo para que detecte las expresiones de riesgo aunque cambien las mayúsculas o las tildes. Importa porque es la defensa más importante de la aplicación. La lista que se usa en el sprint es de prueba y está marcada como provisional: no es una detección validada por una especialista.
- **HU-14, texto de crisis (2 pts).** Mueve el texto fijo de crisis y los números de ayuda a un archivo editable. Así la especialista puede cambiarlo sin tocar código. Está lista cuando la API devuelve ese texto sin pasar por el modelo.
- **HU-10, rechazo clínico (3 pts).** Crea la función que reconoce consultas sobre diagnósticos o medicación. Importa porque dar esa orientación corresponde a un profesional. Está lista cuando reconoce los veinte casos de prueba.

**Erick**

- **HU-09, proveedor del modelo (3 pts).** Encapsula al modelo detrás de una interfaz para poder cambiar entre Gemini, Groq u otro con una variable de entorno. Importa porque los planes gratuitos tienen límites y el equipo no debe quedar atado a uno. La clave va en `.env`, que nunca se sube a GitHub.
- **IA-01, prompt del sistema (2 pts).** Escribe, en un archivo versionado, el rol y los límites del asistente: no diagnostica, no habla de medicación, responde solo con el material y dice que es una IA.
- **HU-07, carga del material (5 pts).** Un script que lee entre 5 y 10 textos con sus etiquetas y los deja listos para consultar. Hasta que la especialista entregue su material, los textos son provisionales y se redactan a partir de guías públicas citadas.
- **HU-08a, búsqueda de fragmentos (3 pts).** Dada una consulta, devuelve hasta tres fragmentos pertinentes o ninguno. El "ninguno" es tan importante como el resultado: permite que el asistente reconozca lo que no sabe.

### Pareja A: Álvaro y Jose (acceso, cuentas y consentimiento)

- **BE-02, cuentas de demostración (2 pts, Álvaro).** Guarda en la base las tres cuentas con las que se mostrará el proyecto: Ana (usuaria estándar), Luis (paciente) y la tratante. No hay registro con correo todavía; las cuentas se eligen en la pantalla inicial. Está lista cuando existen al iniciar y sus pruebas pasan con una base en memoria.
- **BE-03, consentimiento en el backend (2 pts, Jose).** `POST /consentimiento` guarda la fecha de aceptación; sin ella, el chat responde 403. Importa por una razón legal y ética: nadie debe conversar sin haber aceptado qué es Holo y qué datos se guardan.
- **HU-02, pantalla de consentimiento (3 pts, Álvaro).** Muestra el texto, pide aceptar y declarar mayoría de edad, y no deja avanzar sin ambos. El texto lo redacta Karol en DOC-01; hasta que esté se usa uno provisional.
- **FE-07, recursos de ayuda (2 pts, Jose).** Un widget reutilizable con ECU 911 y la línea 171, opción 6, con un botón para llamar. Se reutiliza en la pantalla de crisis del sprint 2, así que debe quedar bien hecho y probado.

### Pareja B: Damien y Justin (conversación)

- **FE-05, componentes de la conversación (3 pts, Damien).** Las burbujas de mensaje, la lista y el indicador de que el asistente está respondiendo. Son piezas sin conexión a la API, para probarlas fácilmente.
- **FE-06, pantalla de conversación (3 pts, Justin).** Junta esas piezas con un campo de envío, carga el historial al abrir y maneja los errores de red con un mensaje y un botón de reintento. Depende de FE-05: se coordinan entre ambos para que el relevo sea fluido.
- **BE-04, conversación guardada (3 pts, Damien).** Guarda cada mensaje en la base y devuelve el historial en orden. Importa para que la persona retome lo que escribió y para que el resumen del sprint 2 tenga de dónde leer.
- **BE-16, validación de mensajes (2 pts, Damien).** Rechaza mensajes vacíos o de más de 2000 caracteres con un error claro. Evita errores y abusos desde el inicio.
- **BE-14, errores con formato único (2 pts, Justin).** Todos los errores de la API tienen la misma forma, para que la aplicación los muestre sin casos especiales.

### Pareja C: Jampier, Imanol y Karol (base técnica y diseño)

- **FE-01, carpetas de plataforma (1 pt, Jampier).** Ejecuta `flutter create` en el repositorio del front para generar las carpetas de Android y web, y verifica que `flutter pub get`, `flutter analyze` y `flutter test` pasan. Es la primera tarea del sprint: sin ella nadie puede ejecutar la aplicación. El código Dart nunca se compiló, así que pueden aparecer errores que hay que corregir.
- **FE-02, cliente de la API con modo simulado (2 pts, Jampier).** Un cliente que puede hablar con el backend real o responder con los ejemplos de `odds/`, según un parámetro. Permite construir las pantallas sin esperar al backend.
- **CI-01 y CI-02, verificación automática (2 pts cada una, Jampier el backend e Imanol el front).** Configuran GitHub Actions para que, en cada pull request, se revise el formato, se analice el código y se ejecuten las pruebas. Así ninguna rama rota llega a `develop`.
- **BE-07a, conversaciones ficticias de Luis (2 pts, Imanol).** Siete días de conversaciones inventadas, con un episodio de ansiedad, uno de sueño y un mensaje de riesgo, para que el resumen del sprint 2 tenga contenido. Cada registro debe estar identificado como ficticio. Erick las necesita hacia el miércoles.
- **BE-15, registros sin datos personales (2 pts, Imanol).** Configura los logs del backend para que nunca escriban el texto de los mensajes. Importa porque en una aplicación de salud emocional un registro de servidor es un riesgo de privacidad.
- **UX-01, guía de estilo (2 pts, Karol).** Define colores, tipografías, botones y burbujas, con contraste suficiente para leerse bien en el celular.
- **UX-02 y UX-03, mockups (3 pts cada uno, Karol).** UX-02 cubre el consentimiento y la conversación, con sus estados vacío, cargando y error; UX-03, la pantalla de crisis y la vista del tratante. La pantalla de crisis debe ser sobria y su tono lo revisa luego la especialista.
- **DOC-01, texto del consentimiento (2 pts, Karol).** Redacta, en español formal, qué es Holo, qué datos se guardan, quién los ve, la mayoría de edad y que no reemplaza a un profesional ni a un servicio de emergencia, con referencia a la LOPDP. Es provisional hasta una revisión legal.

Karol aún no tiene acceso a los repositorios: sus tareas de este sprint no lo necesitan. Mientras tanto, su pareja sube los archivos al repositorio con ella como coautora.

## Calendario del sprint

Las reuniones propuestas son breves. Los horarios deben acordarse con el equipo.

| Día | Qué ocurre | Se entrega |
| --- | --- | --- |
| Lunes 16 | Reunión de inicio (45 minutos). Se aceptan las invitaciones de GitHub, se instalan Git, Docker Desktop, Python, Flutter y un editor, y se consiguen la clave gratuita del modelo y el acceso de Karol. Las parejas leen sus tareas. | BE-01 y FE-01 integradas; todos ejecutan el proyecto |
| Martes 17 | Las parejas comienzan sus primeros turnos. Reunión diaria de 10 minutos. | UX-02 (mockups de consentimiento y conversación) |
| Miércoles 18 | Primeros relevos entre las parejas. Las tareas de base ya están integradas. | BE-07a (conversaciones ficticias); FE-02 y CI integradas |
| Jueves 19 | Pull requests en revisión; se corrigen observaciones. Se prueba la aplicación contra el backend con el proveedor de prueba. | La mayoría de las tareas en `develop` |
| Viernes 20 | Demostración interna del recorrido descrito arriba, retrospectiva de 30 minutos y planificación del sprint 2. | Sprint cerrado |

Si una tarea no termina el viernes, no se fuerza: se explica por qué y se pasa al sprint 2. Los 67 puntos son una propuesta; la planificación del lunes es el momento de ajustarlos.

## Implicaciones y precauciones

Holo trata un tema sensible, y eso cambia cómo se trabaja incluso en un sprint de demostración.

- **No es terapia ni emergencia.** El asistente no diagnostica, no habla de medicación y no sustituye a un profesional. Ningún texto, pantalla ni presentación debe sugerir lo contrario.
- **Lo provisional se marca.** La lista de expresiones de riesgo, el texto de crisis, el consentimiento y el material de consulta fueron redactados por el equipo, no por la especialista. Deben estar marcados como provisionales y no pueden presentarse como validados. Antes de que lo use una persona real hace falta su aprobación y una revisión legal.
- **Solo datos ficticios.** Los planes gratuitos de los modelos pueden usar lo que se les envía para mejorar sus productos, y la ley ecuatoriana de protección de datos personales (LOPDP) trata los datos de salud como una categoría especial. Por eso nunca se prueba con conversaciones ni datos de personas reales, incluidos los propios.
- **Cuidado con los mensajes de prueba.** Para verificar la detección de riesgo hay que escribir mensajes que expresan sufrimiento. Si a alguien le resulta difícil escribirlos o leerlos, puede pedir que otra persona de la pareja los redacte, sin necesidad de explicar por qué.
- **Privacidad en el código.** Las claves y contraseñas van solo en `.env`, que está en `.gitignore`; los registros del servidor no guardan el texto de los mensajes; el archivo de Docker Compose no contiene credenciales reales. Un secreto subido por error a GitHub se considera filtrado aunque se borre después: se avisa y se cambia.
- **Cambio de base de datos.** Se usa PostgreSQL en Docker en lugar de SQLite, por lo que quien aprende lo hace con la herramienta que tendrá el proyecto después. A cambio, Docker Desktop es un requisito para todos y consume memoria; Windows necesita WSL 2.
- **Contrato compartido.** Un cambio en la carpeta `odds/` afecta al front y al back a la vez. Nunca se cambia sin avisar a la otra parte.
- **Límites de los modelos gratuitos.** Gemini y Groq tienen límites de peticiones por minuto y por día. Las pruebas automáticas usan el proveedor de prueba para no gastar la cuota.

## Cómo saber que el sprint terminó bien

El sprint se considera cumplido si, el viernes 20, se verifica lo siguiente:

- [ ] Cada integrante ejecuta el backend, la base en Docker y la aplicación en su equipo.
- [ ] La aplicación muestra el consentimiento y no deja avanzar sin aceptarlo.
- [ ] Un mensaje enviado desde la aplicación queda guardado y se ve al reabrir.
- [ ] Un mensaje de riesgo devuelve el texto de crisis sin pasar por el modelo.
- [ ] Una consulta sobre medicación es rechazada y orienta hacia un profesional.
- [ ] Una consulta fuera del material recibe la respuesta de que no puede ayudar.
- [ ] Existen los mockups de consentimiento y conversación, y la guía de estilo.
- [ ] La verificación automática corre en ambos repositorios.
- [ ] Los textos provisionales están marcados como tales y no hay claves ni datos reales en los repositorios.
- [ ] La carpeta `odds/` refleja lo que hace cada endpoint.

Lo que no alcance a terminarse se anota, con su motivo, para el sprint 2.

## Preguntas frecuentes

**¿Y si no conozco la herramienta de mi tarea?** Para eso está la pareja: una persona escribe y la otra revisa, y ambas aprenden. Cada tarea es pequeña a propósito. Si algo te bloquea más de medio día, avísalo.

**¿Qué hago si mi pareja no responde?** Los turnos de revisión tienen un plazo de medio día. Si se vence, lo mencionas en la reunión diaria o en el canal del equipo; nadie queda bloqueado por la ausencia de otra persona.

**¿Puedo cambiar lo que devuelve un endpoint?** Sí, pero en un pull request que también actualice la carpeta `odds/` y con la aprobación de quien usa ese endpoint, porque el front y el back dependen de él.

**¿Puedo usar asistentes de IA para programar?** Es una decisión que debe tomar el equipo. Si se usan, quien abre el pull request responde por cada línea como si la hubiera escrito él, y la revisión de la pareja y de un tercero se hace igual.

**¿Qué hago si termino antes?** Revisas pull requests de otras parejas y, si queda tiempo, tomas una historia opcional del documento de backlog.

**¿Puedo probar la aplicación con mis propios problemas reales?** No. Todo se prueba con mensajes y datos ficticios, por privacidad y porque el asistente aún no está validado por una especialista.

**¿Por qué hay tantos textos "provisionales"?** Porque el contenido de salud mental debe aprobarlo una especialista y aún no lo ha hecho. Marcarlo evita que una versión de prueba se confunda con una versión validada.

**¿Qué hago si algo del proyecto me afecta personalmente?** Lo dices a la persona que coordina o a tu pareja; trabajar con estos temas puede resultar difícil y se puede cambiar de tarea sin dar explicaciones.

## Documentos relacionados

- [Holo: backlog del MVP por sprint y responsable](https://claude.ai/artifact/1hUGDz6CNG44xEiZomcUDu): todas las tareas, con sus criterios de aceptación y archivos.
- [Holo: Docker y Docker Compose](https://claude.ai/artifact/C8HhBEg3GUMJh9PLoztjes): guía para la tarea BE-01.
- [Proyecto Holo: documento de trabajo para el equipo](https://claude.ai/artifact/XDmFFWdXymfJnS4AaDZr1A): visión general, alcance y riesgos del proyecto.
- En los repositorios: `README.md`, `CONTRIBUTING.md` y la carpeta `odds/` del backend, con la documentación de cada endpoint.

Para que el equipo pueda abrir estos documentos, hay que compartirlos desde el menú Compartir de cada uno: por ahora solo los ve quien los creó.
