"""Tipos canônicos de eventos ocorridos durante uma partida."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class EventType(DomainEnum):
    """Representa a natureza de um evento registrado na partida."""

    GOAL = "goal"
    OWN_GOAL = "own_goal"
    PENALTY_GOAL = "penalty_goal"
    PENALTY_MISSED = "penalty_missed"
    YELLOW_CARD = "yellow_card"
    SECOND_YELLOW_CARD = "second_yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    INJURY = "injury"
    OFFSIDE = "offside"
    FOUL = "foul"
    CORNER = "corner"
    FREE_KICK = "free_kick"
    PENALTY_AWARDED = "penalty_awarded"
    KICKOFF = "kickoff"
    HALF_TIME = "half_time"
    FULL_TIME = "full_time"
    EXTRA_TIME_START = "extra_time_start"
    EXTRA_TIME_END = "extra_time_end"
    PENALTY_SHOOTOUT_START = "penalty_shootout_start"
    PENALTY_SHOOTOUT_END = "penalty_shootout_end"