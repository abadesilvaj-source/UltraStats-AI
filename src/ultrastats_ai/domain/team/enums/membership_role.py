"""Funções exercidas por pessoas em equipes."""

from ultrastats_ai.domain.shared import DomainEnum


class MembershipRole(DomainEnum):
    """Identifica a função de uma pessoa dentro da equipe."""

    PLAYER = "player"

    HEAD_COACH = "head_coach"
    ASSISTANT_COACH = "assistant_coach"
    GOALKEEPER_COACH = "goalkeeper_coach"
    FITNESS_COACH = "fitness_coach"
    TECHNICAL_DIRECTOR = "technical_director"

    TEAM_MANAGER = "team_manager"
    DIRECTOR = "director"
    PRESIDENT = "president"

    DOCTOR = "doctor"
    PHYSIOTHERAPIST = "physiotherapist"
    NUTRITIONIST = "nutritionist"
    ANALYST = "analyst"

    STAFF = "staff"
    OTHER = "other"
    UNKNOWN = "unknown"