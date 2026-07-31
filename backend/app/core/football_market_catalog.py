from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FootballMarket:
    code: str
    name: str
    category: str


def football_markets() -> tuple[FootballMarket, ...]:
    markets = [
        FootballMarket("match_winner", "Resultado da Partida", "result"),
        FootballMarket("double_chance", "Chance Dupla", "result"),
        FootballMarket("draw_no_bet", "Empate Anula", "result"),
        FootballMarket(
            "both_teams_to_score", "Ambas as Equipes Marcam", "goals"
        ),
        FootballMarket("exact_total_goals", "Total Exato de Gols", "goals"),
        FootballMarket("goals_odd_even", "Total de Gols Ímpar/Par", "goals"),
        FootballMarket("correct_score", "Placar Exato", "score"),
        FootballMarket("home_clean_sheet", "Mandante sem Sofrer Gol", "goals"),
        FootballMarket("away_clean_sheet", "Visitante sem Sofrer Gol", "goals"),
    ]
    for value in range(0, 6):
        line = f"{value}_5"
        label = f"{value}.5"
        markets.extend((
            FootballMarket(
                f"over_{line}_goals", f"Mais de {label} Gols", "goals"
            ),
            FootballMarket(
                f"under_{line}_goals", f"Menos de {label} Gols", "goals"
            ),
        ))
    for side, side_label in (("home", "Mandante"), ("away", "Visitante")):
        for value in range(0, 4):
            line = f"{value}_5"
            label = f"{value}.5"
            markets.extend((
                FootballMarket(
                    f"{side}_over_{line}_goals",
                    f"{side_label} Mais de {label} Gols",
                    "team_goals",
                ),
                FootballMarket(
                    f"{side}_under_{line}_goals",
                    f"{side_label} Menos de {label} Gols",
                    "team_goals",
                ),
            ))
    for value in range(5, 14):
        line = f"{value}_5"
        label = f"{value}.5"
        markets.extend((
            FootballMarket(
                f"over_{line}_corners",
                f"Mais de {label} Escanteios",
                "corners",
            ),
            FootballMarket(
                f"under_{line}_corners",
                f"Menos de {label} Escanteios",
                "corners",
            ),
        ))
    for side, side_label in (("home", "Mandante"), ("away", "Visitante")):
        for value in range(1, 8):
            line = f"{value}_5"
            label = f"{value}.5"
            markets.extend((
                FootballMarket(
                    f"{side}_over_{line}_corners",
                    f"{side_label} Mais de {label} Escanteios",
                    "team_corners",
                ),
                FootballMarket(
                    f"{side}_under_{line}_corners",
                    f"{side_label} Menos de {label} Escanteios",
                    "team_corners",
                ),
            ))
    for value in range(0, 9):
        line = f"{value}_5"
        label = f"{value}.5"
        markets.extend((
            FootballMarket(
                f"over_{line}_cards", f"Mais de {label} Cartões", "cards"
            ),
            FootballMarket(
                f"under_{line}_cards", f"Menos de {label} Cartões", "cards"
            ),
        ))
    for side, side_label in (("home", "Mandante"), ("away", "Visitante")):
        for value in range(0, 6):
            line = f"{value}_5"
            label = f"{value}.5"
            markets.extend((
                FootballMarket(
                    f"{side}_over_{line}_cards",
                    f"{side_label} Mais de {label} Cartões",
                    "team_cards",
                ),
                FootballMarket(
                    f"{side}_under_{line}_cards",
                    f"{side_label} Menos de {label} Cartões",
                    "team_cards",
                ),
            ))
    return tuple(markets)


FOOTBALL_MARKETS = football_markets()
