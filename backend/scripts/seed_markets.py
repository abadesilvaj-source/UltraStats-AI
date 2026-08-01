from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Market


MARKETS = [
    {
        "code": "match_winner",
        "name": "Resultado da Partida",
        "category": "result",
    },
    {
        "code": "double_chance",
        "name": "Dupla Chance",
        "category": "result",
    },
    {
        "code": "draw_no_bet",
        "name": "Empate Anula",
        "category": "result",
    },
    {
        "code": "over_2_5_goals",
        "name": "Mais de 2.5 Gols",
        "category": "goals",
    },
    {
        "code": "under_2_5_goals",
        "name": "Menos de 2.5 Gols",
        "category": "goals",
    },
    {
        "code": "under_3_5_goals",
        "name": "Menos de 3.5 Gols",
        "category": "goals",
    },
    {
        "code": "both_teams_to_score",
        "name": "Ambas as Equipes Marcam",
        "category": "goals",
    },
    {
        "code": "over_8_5_corners",
        "name": "Mais de 8.5 Escanteios",
        "category": "corners",
    },
    {
        "code": "over_9_5_corners",
        "name": "Mais de 9.5 Escanteios",
        "category": "corners",
    },
    {
        "code": "over_4_5_cards",
        "name": "Mais de 4.5 Cartões",
        "category": "cards",
    },
    {
        "code": "asian_handicap",
        "name": "Handicap Asiático",
        "category": "handicap",
    },
]


def seed_markets() -> None:
    session = SessionLocal()

    try:
        for market_data in MARKETS:
            statement = select(Market).where(
                Market.code == market_data["code"]
            )

            existing_market = session.scalar(statement)

            if existing_market:
                print(f"Mercado já existe: {existing_market.name}")
                continue

            market = Market(**market_data)
            session.add(market)

            print(f"Adicionando mercado: {market.name}")

        session.commit()

        print("Mercados cadastrados com sucesso!")

    except Exception as error:
        session.rollback()
        print(f"Erro ao cadastrar mercados: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    seed_markets()