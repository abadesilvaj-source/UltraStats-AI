"""Ações registráveis no histórico do People Context."""

from ultrastats_ai.domain.shared import DomainEnum


class PeopleHistoryAction(DomainEnum):
    """Identifica uma alteração relevante envolvendo uma pessoa."""

    PERSON_CREATED = "person_created"
    PERSON_RENAMED = "person_renamed"

    DISPLAY_NAME_CHANGED = "display_name_changed"
    BIRTH_DATE_CHANGED = "birth_date_changed"

    ALIAS_ADDED = "alias_added"
    ALIAS_REMOVED = "alias_removed"

    PLAYER_PROFILE_ADDED = "player_profile_added"
    PLAYER_PROFILE_REMOVED = "player_profile_removed"

    COACH_PROFILE_ADDED = "coach_profile_added"
    COACH_PROFILE_REMOVED = "coach_profile_removed"

    REFEREE_PROFILE_ADDED = "referee_profile_added"
    REFEREE_PROFILE_REMOVED = "referee_profile_removed"

    PERSON_ACTIVATED = "person_activated"
    PERSON_DEACTIVATED = "person_deactivated"