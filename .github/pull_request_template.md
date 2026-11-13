## Descripción

<!-- Qué cambia y por qué, en dos o tres líneas. -->

## Historia relacionada

<!-- Ejemplo: HU-06. Ver docs/product-backlog.md -->
HU-

## Tipo de cambio

- [ ] Nueva funcionalidad (`feat`)
- [ ] Corrección (`fix`)
- [ ] Documentación (`docs`)
- [ ] Refactorización o tarea técnica (`refactor`, `chore`, `test`)

## Cómo se probó

<!-- Pasos para que la persona revisora reproduzca la prueba. -->

## Lista de verificación

- [ ] La rama parte de `develop` y el pull request apunta a `develop`
- [ ] El título sigue el convenio de commits (ver CONTRIBUTING.md)
- [ ] `ruff check .` no reporta errores
- [ ] `pytest` se ejecuta sin fallos y se agregaron pruebas para el cambio
- [ ] Si cambió un endpoint, se actualizó su archivo en `odds/` y se regeneró `odds/openapi.json`
- [ ] No se incluyen claves, archivos `.env` ni datos de personas reales
- [ ] Se cumplen los criterios de aceptación de la historia
