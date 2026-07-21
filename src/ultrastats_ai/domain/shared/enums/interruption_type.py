"""Tipos canônicos de interrupção de uma partida."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class InterruptionType(DomainEnum):
    """Representa o motivo de uma interrupção de partida."""

    INJURY = "injury"
    WEATHER = "weather"
    CROWD_TROUBLE = "crowd_trouble"
    PITCH_INVASION = "pitch_invasion"
    TECHNICAL_ISSUE = "technical_issue"
    LIGHTING_FAILURE = "lighting_failure"
    SECURITY_ISSUE = "security_issue"
    REFEREE_DECISION = "referee_decision"
    VAR_CHECK = "var_check"
    MEDICAL_EMERGENCY = "medical_emergency"
    EQUIPMENT_FAILURE = "equipment_failure"
    OTHER = "other"