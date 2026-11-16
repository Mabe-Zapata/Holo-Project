import pytest

from app.services.filtros import es_consulta_clinica

CONSULTAS_CLINICAS = [
    "¿Qué diagnóstico tengo según lo que te escribo?",
    "¿Puedo tomar más dosis de mi medicamento?",
    "¿Cuántos miligramos debería tomar?",
    "¿Me recomiendas un antidepresivo?",
    "¿Qué pastillas me conviene tomar para dormir?",
    "¿Es normal que el ansiolítico me dé sueño?",
    "¿Puedes recetarme algo para la ansiedad?",
    "¿Debo dejar de tomar mi medicación?",
    "Creo que tengo bipolaridad, ¿verdad?",
    "¿Qué trastorno tengo?",
]

CONSULTAS_NO_CLINICAS = [
    "Hoy fue un buen día en la universidad.",
    "¿Me das una receta de galletas?",
    "Estoy muy cansada después del examen.",
    "¿Cómo puedo respirar mejor cuando estoy nerviosa?",
    "Quiero hablar de mi relación con mi familia.",
    "Me gustaría practicar la técnica de anclaje.",
    "Ayer salí a caminar con mi perra.",
    "¿Qué puedo hacer para dormir mejor?",
    "Me preocupa el examen de la próxima semana.",
    "Gracias por escucharme.",
]


@pytest.mark.parametrize("texto", CONSULTAS_CLINICAS)
def test_detecta_consultas_clinicas(texto):
    assert es_consulta_clinica(texto)


@pytest.mark.parametrize("texto", CONSULTAS_NO_CLINICAS)
def test_no_marca_conversacion_habitual(texto):
    assert not es_consulta_clinica(texto)
