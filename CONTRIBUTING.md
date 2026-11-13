# Convenios de desarrollo

El presente documento establece los convenios de trabajo con Git del proyecto Holo. Su cumplimiento es requisito para integrar cambios al repositorio.

## 1. Ramas

| Rama | Propósito | Reglas |
| --- | --- | --- |
| `main` | Versión estable, la que se presenta | Solo recibe cambios desde `develop` mediante pull request. No se permite el envío directo |
| `develop` | Integración del trabajo en curso | Solo recibe cambios mediante pull request aprobado. No se permite el envío directo |
| `feature/...` | Una historia del backlog | Parte de `develop` y vuelve a `develop` |
| `fix/...` | Corrección de un defecto | Parte de `develop` y vuelve a `develop` |
| `docs/...` | Cambios exclusivos de documentación | Parte de `develop` y vuelve a `develop` |
| `chore/...` | Configuración, dependencias y tareas técnicas | Parte de `develop` y vuelve a `develop` |

### Nombre de las ramas

Formato: `tipo/HU-XX-descripcion-breve`, en minúsculas, sin tildes y con guiones.

```text
feature/HU-06-endpoint-chat
fix/HU-13-normalizacion-tildes
docs/odds-resumen
chore/actualizar-dependencias
```

### Flujo de trabajo

```bash
git checkout develop
git pull
git checkout -b feature/HU-06-endpoint-chat
# ... cambios y commits ...
git push -u origin feature/HU-06-endpoint-chat
# Abrir el pull request hacia develop
```

Antes de abrir el pull request, la rama debe actualizarse con los últimos cambios de `develop`.

## 2. Commits

Se emplea el convenio Conventional Commits, con la descripción en español.

Formato: `tipo(alcance): descripción`

| Tipo | Uso |
| --- | --- |
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de un defecto |
| `docs` | Cambios en la documentación |
| `test` | Pruebas nuevas o modificadas |
| `refactor` | Cambio interno que no altera el comportamiento |
| `style` | Formato del código, sin cambios de lógica |
| `chore` | Configuración, dependencias o tareas de mantenimiento |

Reglas:

- La descripción se escribe en infinitivo o en presente, en minúsculas y sin punto final.
- La primera línea no supera los 72 caracteres.
- Cada commit contiene un solo cambio lógico.
- El alcance es opcional e indica el módulo afectado.
- Cuando corresponde, el cuerpo del commit hace referencia a la historia.

```text
feat(chat): agregar endpoint de historial
fix(riesgo): ignorar tildes al comparar expresiones
docs(odds): documentar el endpoint de resumen
test(consentimiento): cubrir el rechazo sin aceptación
```

## 3. Pull requests

### Requisitos para abrir un pull request

- Apunta a `develop`. Únicamente la integración de una entrega apunta a `main`.
- Su título sigue el convenio de commits.
- Corresponde a una sola historia o corrección, e indica su identificador (HU-XX).
- Se completa la plantilla del repositorio, incluida la sección de pruebas.
- Su tamaño es acotado: como referencia, menos de 400 líneas modificadas. Un cambio mayor se divide.
- No contiene claves, archivos `.env`, datos de personas reales ni material sin identificar como provisional.

### Requisitos para integrarlo

- Cuenta con la aprobación de al menos un integrante distinto del autor.
- Todas las conversaciones de la revisión están resueltas.
- Las comprobaciones automáticas del repositorio se ejecutan sin errores (sección 4).
- La documentación afectada fue actualizada.
- No presenta conflictos con `develop`.

La integración se realiza mediante *squash and merge*, de modo que cada historia quede como un único commit en `develop`. La rama se elimina después de integrarla.

### Revisión

- La revisión se realiza dentro de las 24 horas siguientes a la solicitud.
- Los comentarios se refieren al código y proponen una alternativa concreta.
- La persona autora es quien integra el pull request una vez aprobado.

## 4. Comprobaciones antes del pull request

En este repositorio deben ejecutarse sin errores:

```bash
ruff format .
ruff check .
pytest
```

Además:

- Toda funcionalidad nueva incluye al menos una prueba automática.
- Si se agrega o modifica un endpoint, se actualiza su archivo en `odds/` y se regenera la especificación con `python scripts/exportar_openapi.py`.
- Las dependencias nuevas se agregan a `requirements.txt` o `requirements-dev.txt` y se justifican en el pull request.

## 5. Seguridad y datos

- Las claves se guardan exclusivamente en el archivo `.env`, que está excluido del repositorio. Si una clave se publica por error, se revoca de inmediato y se informa al equipo.
- No se utilizan datos de personas reales en el código, las pruebas ni los ejemplos.
- La lista de expresiones de riesgo y el texto de crisis solo se modifican con la aprobación de la especialista, y el pull request debe indicarlo.
