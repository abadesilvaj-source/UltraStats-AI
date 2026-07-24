"""Naturezas canônicas de partidas."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class MatchType(DomainEnum):
    """Representa a natureza esportiva principal da partida."""

    REGULAR = "regular"
    FRIENDLY = "friendly"
    QUALIFIER = "qualifier"
    PLAYOFF = "playoff"
    KNOCKOUT = "knockout"
    GROUP_STAGE = "group_stage"
    LEAGUE = "league"
    CUP = "cup"
    SUPERCUP = "supercup"
    THIRD_PLACE = "third_place"
    FINAL = "final"
    EXHIBITION = "exhibition"
    TRAINING = "training"
    ABANDONED_REPLAY = "abandoned_replay"
    OTHER = "other"
    UNKNOWN = "unknown"
