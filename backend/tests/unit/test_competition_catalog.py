from app.core.competition_catalog import (
    competition_metadata,
    competition_policy,
)


def test_requested_club_competitions_are_operational():
    cases = {
        "Brasileirão Série B": "BSB",
        "CONMEBOL Libertadores": "LIB",
        "Copa Sudamericana": "SUD",
    }
    for name, code in cases.items():
        policy = competition_policy(name)
        assert policy is not None
        assert policy.code == code
        assert policy.recommendations_enabled


def test_national_team_competitions_have_separate_group():
    for name in (
        "FIFA World Cup",
        "Copa América",
        "UEFA Nations League",
        "Africa Cup of Nations",
        "AFC Asian Cup",
        "CONCACAF Gold Cup",
    ):
        policy = competition_policy(name)
        assert policy is not None
        assert policy.group == "national_teams"


def test_unknown_competition_is_observation_only():
    assert competition_metadata("Liga desconhecida") == {
        "code": None,
        "canonical_name": "Liga desconhecida",
        "group": "observation",
        "recommendations_enabled": False,
    }
