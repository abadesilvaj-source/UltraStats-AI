import re


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

    if market_code == "double_chance":
        home_won = home_score > away_score
        away_won = away_score > home_score
        draw = home_score == away_score
        choices = {
            "home or draw": home_won or draw,
            "home or away": home_won or away_won,
            "draw or away": draw or away_won,
            "1x": home_won or draw,
            "12": home_won or away_won,
            "x2": draw or away_won,
        }
        return (
            "won" if choices[normalized_selection] else "lost"
        ) if normalized_selection in choices else "unsupported"

    if market_code == "draw_no_bet":
        if home_score == away_score:
            return "void"
        if normalized_selection in {"home", "casa", "mandante", "1"}:
            return "won" if home_score > away_score else "lost"
        if normalized_selection in {"away", "fora", "visitante", "2"}:
            return "won" if away_score > home_score else "lost"
        return "unsupported"
    if market_code == "correct_score":
        expected = f"{home_score}-{away_score}"
        if normalized_selection == "other":
            return "won" if home_score > 4 or away_score > 4 else "lost"
        return "won" if normalized_selection == expected else "lost"

    if market_code == "exact_total_goals":
        if normalized_selection == "6+":
            return "won" if total_goals >= 6 else "lost"
        return (
            "won" if normalized_selection == str(total_goals) else "lost"
        )

    if market_code == "goals_odd_even":
        if normalized_selection in {"even", "par"}:
            return "won" if total_goals % 2 == 0 else "lost"
        if normalized_selection in {"odd", "ímpar", "impar"}:
            return "won" if total_goals % 2 == 1 else "lost"
        return "unsupported"

    if market_code in {"home_clean_sheet", "away_clean_sheet"}:
        clean = away_score == 0 if market_code.startswith("home") else home_score == 0
        if normalized_selection in {"yes", "sim"}:
            return "won" if clean else "lost"
        if normalized_selection in {"no", "não", "nao"}:
            return "won" if not clean else "lost"
        return "unsupported"

    goal_total = re.fullmatch(
        r"(?:(home|away)_)?(over|under)_(\d+)_(5)_goals",
        market_code,
    )
    if goal_total:
        side, direction, whole, _ = goal_total.groups()
        value = (
            home_score if side == "home"
            else away_score if side == "away"
            else total_goals
        )
        threshold = int(whole) + .5
        won = value > threshold if direction == "over" else value < threshold
        return "won" if won else "lost"

    event_total = re.fullmatch(
        r"(?:(home|away)_)?(over|under)_(\d+)_(5)_(corners|cards)",
        market_code,
    )
    if event_total:
        side, direction, whole, _, event = event_total.groups()
        if event == "corners":
            values = (corners_home, corners_away)
        else:
            values = (
                None if yellow_cards_home is None or red_cards_home is None
                else yellow_cards_home + red_cards_home,
                None if yellow_cards_away is None or red_cards_away is None
                else yellow_cards_away + red_cards_away,
            )
        if any(value is None for value in values):
            raise ValueError(
                f"Os dados de {event} são obrigatórios para liquidar esse mercado."
            )
        observed = (
            values[0] if side == "home"
            else values[1] if side == "away"
            else values[0] + values[1]
        )
        threshold = int(whole) + .5
        won = (
            observed > threshold
            if direction == "over"
            else observed < threshold
        )
        return "won" if won else "lost"

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
