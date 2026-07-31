"""Papéis canônicos de oficiais de uma partida."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class OfficialRole(DomainEnum):
    """Representa a função desempenhada por um oficial da partida."""

    REFEREE = "referee"
    ASSISTANT_REFEREE = "assistant_referee"
    FOURTH_OFFICIAL = "fourth_official"
    VIDEO_ASSISTANT_REFEREE = "video_assistant_referee"
    ASSISTANT_VIDEO_ASSISTANT_REFEREE = (
        "assistant_video_assistant_referee"
    )
    ADDITIONAL_ASSISTANT_REFEREE = "additional_assistant_referee"
    RESERVE_ASSISTANT_REFEREE = "reserve_assistant_referee"
    MATCH_COMMISSIONER = "match_commissioner"