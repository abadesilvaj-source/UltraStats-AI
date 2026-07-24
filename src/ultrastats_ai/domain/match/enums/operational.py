"""Enums operacionais das entidades internas do Match."""

from ultrastats_ai.domain.shared.enums import DomainEnum


class AppointmentStatus(DomainEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REPLACED = "replaced"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PeriodType(DomainEnum):
    PRE_MATCH = "pre_match"
    FIRST_HALF = "first_half"
    HALF_TIME = "half_time"
    SECOND_HALF = "second_half"
    EXTRA_TIME_FIRST_HALF = "extra_time_first_half"
    EXTRA_TIME_SECOND_HALF = "extra_time_second_half"
    PENALTY_SHOOTOUT = "penalty_shootout"
    POST_MATCH = "post_match"


class PeriodStatus(DomainEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    INTERRUPTED = "interrupted"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SquadType(DomainEnum):
    PROVISIONAL = "provisional"
    OFFICIAL = "official"
    MATCHDAY = "matchday"


class SquadStatus(DomainEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CONFIRMED = "confirmed"
    SUPERSEDED = "superseded"
    COMPLETED = "completed"


class LineupType(DomainEnum):
    PROBABLE = "probable"
    OFFICIAL = "official"
    STARTING = "starting"
    IN_PLAY = "in_play"
    FINAL = "final"


class LineupStatus(DomainEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CONFIRMED = "confirmed"
    SUPERSEDED = "superseded"
    COMPLETED = "completed"


class LineupRole(DomainEnum):
    STARTER = "starter"
    SUBSTITUTE = "substitute"
    UNUSED_SUBSTITUTE = "unused_substitute"
    COACH = "coach"
    TECHNICAL_STAFF = "technical_staff"


class EventStatus(DomainEnum):
    PROVISIONAL = "provisional"
    CONFIRMED = "confirmed"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    OVERTURNED = "overturned"


class StatisticScope(DomainEnum):
    MATCH = "match"
    PARTICIPANT = "participant"
    PLAYER = "player"
    PERIOD = "period"


class StatisticUnit(DomainEnum):
    COUNT = "count"
    PERCENT = "percent"
    SECONDS = "seconds"
    METERS = "meters"
    RATIO = "ratio"
    SCORE = "score"


class InterruptionStatus(DomainEnum):
    ACTIVE = "active"
    RESUMED = "resumed"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class DecisionStatus(DomainEnum):
    PROVISIONAL = "provisional"
    ANNOUNCED = "announced"
    UNDER_APPEAL = "under_appeal"
    CONFIRMED = "confirmed"
    OVERTURNED = "overturned"
    FINAL = "final"


class RevisionStatus(DomainEnum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    REVERTED = "reverted"
