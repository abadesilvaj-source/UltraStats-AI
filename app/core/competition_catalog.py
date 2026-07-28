"""Catálogo canônico das competições operadas pelo UltraStats."""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True, slots=True)
class CompetitionPolicy:
    code: str
    name: str
    group: str
    country: str | None
    aliases: tuple[str, ...]

    @property
    def recommendations_enabled(self) -> bool:
        return self.group in {"core", "national_teams"}


COMPETITION_POLICIES = (
    CompetitionPolicy(
        "BSA", "Campeonato Brasileiro Série A", "core", "Brasil",
        ("brasileirao serie a", "brasileiro serie a", "serie a brazil"),
    ),
    CompetitionPolicy(
        "BSB", "Campeonato Brasileiro Série B", "core", "Brasil",
        ("brasileirao serie b", "brasileiro serie b", "serie b brazil"),
    ),
    CompetitionPolicy(
        "LIB", "Copa Libertadores da América", "core", "América do Sul",
        ("copa libertadores", "conmebol libertadores", "libertadores"),
    ),
    CompetitionPolicy(
        "SUD", "Copa Sul-Americana", "core", "América do Sul",
        (
            "copa sul americana",
            "conmebol sudamericana",
            "copa sudamericana",
            "sudamericana",
        ),
    ),
    CompetitionPolicy(
        "PL", "Premier League", "core", "Inglaterra",
        ("english premier league", "premier league england"),
    ),
    CompetitionPolicy(
        "PD", "La Liga", "core", "Espanha",
        ("primera division", "laliga", "la liga spain"),
    ),
    CompetitionPolicy(
        "CL", "UEFA Champions League", "core", "Europa",
        ("champions league", "uefa champions league"),
    ),
    CompetitionPolicy(
        "EL", "UEFA Europa League", "core", "Europa",
        ("europa league", "uefa europa league"),
    ),
    CompetitionPolicy(
        "BL1", "Bundesliga", "core", "Alemanha",
        ("bundesliga germany", "german bundesliga"),
    ),
    CompetitionPolicy(
        "SA", "Serie A", "core", "Itália",
        ("serie a italy", "italian serie a"),
    ),
    CompetitionPolicy(
        "FL1", "Ligue 1", "core", "França",
        ("ligue 1 france", "french ligue 1"),
    ),
    CompetitionPolicy(
        "DED", "Eredivisie", "core", "Países Baixos",
        ("eredivisie netherlands", "dutch eredivisie"),
    ),
    CompetitionPolicy(
        "PPL", "Primeira Liga", "core", "Portugal",
        ("liga portugal", "portuguese primeira liga"),
    ),
    CompetitionPolicy(
        "WC", "Copa do Mundo FIFA", "national_teams", "Internacional",
        ("fifa world cup", "world cup", "copa do mundo"),
    ),
    CompetitionPolicy(
        "WQ", "Eliminatórias da Copa do Mundo", "national_teams",
        "Internacional",
        (
            "world cup qualification",
            "world cup qualifiers",
            "wc qualification",
            "eliminatorias da copa",
        ),
    ),
    CompetitionPolicy(
        "CA", "Copa América", "national_teams", "América do Sul",
        ("copa america", "conmebol copa america"),
    ),
    CompetitionPolicy(
        "EURO", "Eurocopa", "national_teams", "Europa",
        ("uefa european championship", "european championship", "euro"),
    ),
    CompetitionPolicy(
        "UNL", "UEFA Nations League", "national_teams", "Europa",
        ("uefa nations league", "nations league"),
    ),
    CompetitionPolicy(
        "AFCON", "Copa Africana de Nações", "national_teams", "África",
        ("africa cup of nations", "afcon", "copa africana de nacoes"),
    ),
    CompetitionPolicy(
        "AC", "Copa da Ásia", "national_teams", "Ásia",
        ("afc asian cup", "asian cup", "copa da asia"),
    ),
    CompetitionPolicy(
        "GC", "Copa Ouro da CONCACAF", "national_teams",
        "América do Norte",
        ("concacaf gold cup", "gold cup", "copa ouro"),
    ),
    CompetitionPolicy(
        "CNL", "CONCACAF Nations League", "national_teams",
        "América do Norte",
        ("concacaf nations league",),
    ),
)


def normalize_competition_name(value: str) -> str:
    plain = unicodedata.normalize("NFKD", value).encode(
        "ascii", "ignore"
    ).decode().casefold()
    return re.sub(r"[^a-z0-9]+", " ", plain).strip()


def competition_policy(
    name: str,
    country: str | None = None,
) -> CompetitionPolicy | None:
    normalized = normalize_competition_name(name)
    normalized_country = normalize_competition_name(country or "")
    if normalized in {"serie a", "serie a brazil"} and (
        normalized_country in {"brazil", "brasil"}
    ):
        return next(
            item for item in COMPETITION_POLICIES if item.code == "BSA"
        )
    if normalized in {"serie b", "serie b brazil"} and (
        normalized_country in {"brazil", "brasil"}
    ):
        return next(
            item for item in COMPETITION_POLICIES if item.code == "BSB"
        )
    for policy in COMPETITION_POLICIES:
        candidates = (
            normalize_competition_name(policy.name),
            *(normalize_competition_name(item) for item in policy.aliases),
        )
        if normalized in candidates:
            return policy
        if any(
            len(candidate) >= 5 and candidate in normalized
            for candidate in candidates
        ):
            if policy.code == "SA" and normalized_country in {
                "brazil", "brasil",
            }:
                continue
            return policy
    return None


def competition_metadata(
    name: str,
    country: str | None = None,
) -> dict[str, str | bool | None]:
    policy = competition_policy(name, country)
    if policy is None:
        return {
            "code": None,
            "canonical_name": name,
            "group": "observation",
            "recommendations_enabled": False,
        }
    return {
        "code": policy.code,
        "canonical_name": policy.name,
        "group": policy.group,
        "recommendations_enabled": policy.recommendations_enabled,
    }
