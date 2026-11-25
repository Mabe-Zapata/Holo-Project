# Análisis de brecha: paráfrasis de riesgo no detectada (HU-21)

Documento para revisión de la especialista. Describe una brecha conocida de la lista de expresiones de riesgo. No modifica la lista ni define niveles de gravedad: esas decisiones son clínicas y quedan a cargo de la especialista.

## 1. Caso

| Campo | Valor |
| --- | --- |
| Texto | "Quisiera no despertarme nunca más." |
| Estado actual | No detectado por `es_riesgo_alto` (prueba marcada `xfail` en `tests/test_sensibilidad.py`) |
| Origen de la prueba | Paráfrasis de riesgo agregada en HU-21 |

## 2. Por qué no se detecta

El detector (`app/services/riesgo.py`) busca coincidencias exactas de cada expresión de `data/expresiones_riesgo.txt`, después de normalizar mayúsculas, acentos, signos y espacios. El texto del caso no contiene ninguna de las expresiones de la lista, aunque expresa una idea cercana.

Expresiones relacionadas que sí están en la lista (líneas 39 a 43 del archivo):

- `ya no quiero vivir`
- `ya no quiero existir`
- `quiero dejar de existir`
- `quiero no existir`
- `no quiero despertar`

La lista contiene `no quiero despertar`, pero no la forma "no despertarme nunca más" ni el condicional "quisiera".

## 3. Qué no sabemos

- No sabemos con qué gravedad clínica debe tratarse este texto frente a "no quiero vivir" o "no quiero despertar". La comparación de gravedad no se hizo en el código ni en este análisis.
- No hay un criterio del equipo sobre niveles de riesgo. El detector es binario: detecta o no detecta, sin niveles.

## 4. Decisiones pendientes

1. **¿Debe este texto activar riesgo alto?**
   - Si sí: agregar variantes a la lista (por ejemplo "no despertarme nunca más" y "quisiera no despertar"), que requiere revisión de falsos positivos.
   - Si no: mantener la brecha documentada y quitar la prueba de la lista de sensibilidad, con la justificación de la especialista.
2. **¿Hace falta una categoría intermedia?** Hoy todo lo que coincide activa la misma respuesta de crisis. Un nivel intermedio cambiaría el flujo del chat y requiere diseño de producto, no solo de lista.
3. **Familia de "quiero morirme":** no se agregó por riesgo de falsos positivos (por ejemplo "quiero morirme de risa"). Sigue como decisión de equipo.

## 5. Estado en el código

- `tests/test_sensibilidad.py`: la prueba de paráfrasis sigue como `xfail` con `strict=True`. Si la expresión se agrega a la lista, la prueba falla como XPASS y debe quitarse del marcador.
- `data/expresiones_riesgo.txt`: sin cambios en esta revisión.
- `docs/resultados-pruebas.md`: sin cambios.

## 6. Qué se pide a la especialista

- Decidir si el caso debe detectarse como riesgo alto (opción 1 o 2 del punto 4).
- Indicar si la lista provisional de HU-21 puede pasar a validada, o qué expresiones debe retirar o agregar.
- Revisar el punto 4.3 con el equipo.
