"""Regras reutilizáveis de qualidade de respostas, sem depender de provedor de IA."""
import re


def response_issues(message: str, *, emergency: bool = False) -> list[str]:
    """Verificações objetivas; não substituem revisão semântica nem clínica."""
    result = []
    text = message.strip()
    if not text:
        return ["empty"]
    if emergency:
        return result
    if len(text.split()) > 65:
        result.append("long")
    if text.count("?") > 1:
        result.append("multiple_questions")
    if len([line for line in text.splitlines() if line.strip()]) > 4:
        result.append("too_many_paragraphs")
    if re.search(r"\b(?:diagnostico voce|diagnóstico você|tenho 50 anos de experiência|sou psicólogo(a)? licenciado(a)?)\b", text, re.I):
        result.append("professional_claim")
    return result
