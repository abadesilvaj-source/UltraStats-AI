"""Tipos canônicos de mercados."""

from ultrastats_ai.domain.shared.enums.domain_enum import DomainEnum


class MarketType(DomainEnum):
    """Representa um mercado de aposta."""

    MATCH_WINNER = "match_winner"
    DOUBLE_CHANCE = "double_chance"
    DRAW_NO_BET = "draw_no_bet"
    BOTH_TEAMS_TO_SCORE = "both_teams_to_score"
    OVER_UNDER_GOALS = "over_under_goals"
    CORRECT_SCORE = "correct_score"
    HALF_TIME = "half_time"
    HALF_TIME_FULL_TIME = "half_time_full_time"
    ASIAN_HANDICAP = "asian_handicap"
    EUROPEAN_HANDICAP = "european_handicap"
    CORNERS = "corners"
    CARDS = "cards"
    SHOTS = "shots"
    PLAYER_PROPS = "player_props"
    TEAM_PROPS = "team_props"
    OTHER = "other"