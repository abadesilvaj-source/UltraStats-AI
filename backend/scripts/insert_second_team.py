from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Team


def insert_second_team() -> None:
    session = SessionLocal()

    try:
        statement = select(Team).where(
            Team.name == "Flamengo"
        )

        existing_team = session.scalar(statement)

        if existing_team:
            print("O Flamengo já está cadastrado.")
            return

        team = Team(
            name="Flamengo",
            country="Brasil",
            league="Campeonato Brasileiro Série A",
            power_rating=76.0,
            attack_rating=78.0,
            defense_rating=73.0,
            corner_rating=74.0,
            card_rating=60.0,
            goal_rating=77.0,
            offside_rating=57.0,
        )

        session.add(team)
        session.commit()
        session.refresh(team)

        print("Equipe cadastrada com sucesso!")
        print(team)

    except Exception as error:
        session.rollback()
        print(f"Erro ao cadastrar equipe: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    insert_second_team()