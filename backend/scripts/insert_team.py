from sqlalchemy.exc import IntegrityError

from app.database.session import SessionLocal
from app.models import Team


def insert_team() -> None:
    session = SessionLocal()

    try:
        team = Team(
            name="Palmeiras",
            country="Brasil",
            league="Campeonato Brasileiro Série A",
            power_rating=75.0,
            attack_rating=76.0,
            defense_rating=74.0,
            corner_rating=72.0,
            card_rating=58.0,
            goal_rating=73.0,
            offside_rating=55.0,
        )

        session.add(team)
        session.commit()
        session.refresh(team)

        print("Equipe cadastrada com sucesso!")
        print(team)

    except IntegrityError:
        session.rollback()
        print("Essa equipe já está cadastrada.")

    except Exception as error:
        session.rollback()
        print(f"Erro ao cadastrar equipe: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    insert_team()