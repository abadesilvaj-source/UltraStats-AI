def normalize_selection(selection: str) -> str:
    """
    Normaliza o texto da seleção.

    Isso facilita a comparação entre textos com
    letras maiúsculas, minúsculas e espaços extras.
    """

    return selection.strip().lower()


def evaluate_market(
    market_code: str,
    selection: str,
    home_score: int,
    away_score: int,
    corners_home: int | None = None,
    corners_away: int | None = None,
    yellow_cards_home: int | None = None,
    yellow_cards_away: int | None = None,
    red_cards_home: int | None = None,
    red_cards_away: int | None = None,
) -> str:
    """
    Avalia o resultado de uma seleção.

    Retornos possíveis:

    - "won": aposta vencedora;
    - "lost": aposta perdedora;
    - "void": aposta anulada;
    - "unsupported": mercado ainda não suportado.
    """

    if home_score < 0 or away_score < 0:
        raise ValueError(
            "Os placares não podem ser negativos."
        )

    normalized_selection = normalize_selection(selection)

    total_goals = home_score + away_score

    # ==========================================
    # MERCADOS DE GOLS
    # ==========================================

    if market_code == "over_2_5_goals":
        return "won" if total_goals > 2.5 else "lost"

    if market_code == "under_2_5_goals":
        return "won" if total_goals < 2.5 else "lost"

    if market_code == "under_3_5_goals":
        return "won" if total_goals < 3.5 else "lost"

    if market_code == "both_teams_to_score":
        both_scored = home_score > 0 and away_score > 0

        if normalized_selection in {
            "sim",
            "yes",
            "ambas marcam",
            "ambas as equipes marcam",
        }:
            return "won" if both_scored else "lost"

        if normalized_selection in {
            "não",
            "nao",
            "no",
            "ambas não marcam",
            "ambas nao marcam",
        }:
            return "won" if not both_scored else "lost"

        return "unsupported"

    # ==========================================
    # RESULTADO DA PARTIDA
    # ==========================================

    if market_code == "match_winner":
        if home_score > away_score:
            match_result = "home"
        elif away_score > home_score:
            match_result = "away"
        else:
            match_result = "draw"

        home_selections = {
            "mandante",
            "casa",
            "home",
            "1",
        }

        away_selections = {
            "visitante",
            "fora",
            "away",
            "2",
        }

        draw_selections = {
            "empate",
            "draw",
            "x",
        }

        if normalized_selection in home_selections:
            return "won" if match_result == "home" else "lost"

        if normalized_selection in away_selections:
            return "won" if match_result == "away" else "lost"

        if normalized_selection in draw_selections:
            return "won" if match_result == "draw" else "lost"

        return "unsupported"

    # ==========================================
    # MERCADOS DE ESCANTEIOS
    # ==========================================

    if market_code in {
        "over_8_5_corners",
        "over_9_5_corners",
    }:
        if corners_home is None or corners_away is None:
            raise ValueError(
                "Os dados de escanteios são obrigatórios "
                "para liquidar esse mercado."
            )

        total_corners = corners_home + corners_away

        if market_code == "over_8_5_corners":
            return "won" if total_corners > 8.5 else "lost"

        if market_code == "over_9_5_corners":
            return "won" if total_corners > 9.5 else "lost"

    # ==========================================
    # MERCADO DE CARTÕES
    # ==========================================

    if market_code == "over_4_5_cards":
        card_values = [
            yellow_cards_home,
            yellow_cards_away,
            red_cards_home,
            red_cards_away,
        ]

        if any(value is None for value in card_values):
            raise ValueError(
                "Os dados de cartões são obrigatórios "
                "para liquidar esse mercado."
            )

        total_cards = (
            yellow_cards_home
            + yellow_cards_away
            + red_cards_home
            + red_cards_away
        )

        return "won" if total_cards > 4.5 else "lost"

    return "unsupported"