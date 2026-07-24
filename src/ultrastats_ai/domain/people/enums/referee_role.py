"""Funções profissionais canônicas de arbitragem."""

from ultrastats_ai.domain.shared import DomainEnum


class RefereeRole(DomainEnum):
    """Representa a função predominante na carreira de arbitragem."""

    MAIN_REFEREE = "main_referee"
    ASSISTANT_REFEREE = "assistant_referee"
    FOURTH_OFFICIAL = "fourth_official"
    VIDEO_ASSISTANT_REFEREE = "video_assistant_referee"
    ASSISTANT_VIDEO_ASSISTANT_REFEREE = (
        "assistant_video_assistant_referee"
    )
    ADDITIONAL_ASSISTANT_REFEREE = (
        "additional_assistant_referee"
    )
    RESERVE_ASSISTANT_REFEREE = (
        "reserve_assistant_referee"
    )
    REFEREE_OBSERVER = "referee_observer"
    OTHER = "other"
    UNKNOWN = "unknown"