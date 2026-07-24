"""Funções técnicas canônicas de treinadores."""

from ultrastats_ai.domain.shared import DomainEnum


class CoachRole(DomainEnum):
    """Representa a função técnica predominante de um treinador."""

    HEAD_COACH = "head_coach"
    ASSISTANT_COACH = "assistant_coach"
    GOALKEEPER_COACH = "goalkeeper_coach"
    FITNESS_COACH = "fitness_coach"
    TECHNICAL_DIRECTOR = "technical_director"
    INTERIM_COACH = "interim_coach"
    YOUTH_COACH = "youth_coach"
    OTHER = "other"
    UNKNOWN = "unknown"