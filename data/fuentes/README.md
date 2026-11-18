# Fuentes para el material del asistente (RAG)

Textos completos de fuentes públicas, descargados el 18 de noviembre de 2026. Sirven como
referencia para redactar el material de HU-07 y como base del recuperador (HU-08a). Son fuentes,
no material aprobado: el material que ve el asistente sale de estas fuentes y lo aprueba la especialista.

| Archivo | Fuente | URL | Licencia | Notas |
| --- | --- | --- | --- | --- |
| `oms-mhgap-2023.txt` | OMS, guía mhGAP para trastornos mentales, neurológicos y por consumo de sustancias (2023) | https://iris.who.int/server/api/core/bitstreams/93e56376-0e64-4a08-bdd0-703313be5354/content | CC BY-NC-SA 3.0 IGO | Texto extraído del PDF con `pdftotext -layout`. La recomendación ANX1 (ansiedad generalizada y trastorno de pánico) es fuerza condicional y certeza baja |
| `oms-ficha-ansiedad.txt` | OMS, ficha informativa "Anxiety disorders" | https://www.who.int/news-room/fact-sheets/detail/anxiety-disorders | CC BY-NC-SA 3.0 IGO (verificar en la página) | Texto extraído de la página HTML; puede incluir menús |
| `nhs-respiracion-estres.txt` | NHS, "Breathing exercises for stress" | https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/ | **Pendiente de confirmar** | Página revisada por última vez el 12 de junio |
| `nhs-problemas-sueno.txt` | NHS, Every Mind Matters, "Sleep problems" | https://www.nhs.uk/every-mind-matters/mental-health-issues/sleep/ | **Pendiente de confirmar** | |
| `nhs-dormir-mejor.txt` | NHS, Every Mind Matters, "Fall asleep faster and sleep better" | https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/how-to-fall-asleep-faster-and-sleep-better/ | **Pendiente de confirmar** | |

## Antes de publicar el repositorio

- Confirmar los términos de reutilización del NHS. Si no permiten reproducir el texto, borrar los tres archivos `nhs-*` y dejar solo el enlace y el resumen.
- Mantener la atribución de la OMS en cualquier material derivado y licenciar las adaptaciones con la misma licencia (CC BY-NC-SA 3.0 IGO).
