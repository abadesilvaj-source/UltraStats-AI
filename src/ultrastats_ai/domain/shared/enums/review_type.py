"""Tipos canônicos de revisão esportiva ou administrativa."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class ReviewType(DomainEnum):
    """Representa o objeto principal de uma revisão."""

    GOAL = "goal"
    PENALTY = "penalty"
    RED_CARD = "red_card"
    MISTAKEN_IDENTITY = "mistaken_identity"
    OFFSIDE = "offside"
    HANDBALL = "handball"
    FOUL = "foul"
    BALL_OUT_OF_PLAY = "ball_out_of_play"
    DISCIPLINARY_ACTION = "disciplinary_action"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"