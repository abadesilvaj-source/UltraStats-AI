from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Competition


def insert_competition() -> None:
    session = SessionLocal()

    try:
        statement = select(Competition).where(
            Competition.name == "Campeonato Brasileiro Série A",
            Competition.season == "2026",
        )

        existing_competition = session.scalar(statement)

        if existing_competition:
            print("Essa competição já está cadastrada.")
            return

        competition = Competition(
            name="Campeonato Brasileiro Série A",
            country="Brasil",
            season="2026",
            sport="football",
            active=True,
        )

        session.add(competition)
        session.commit()
        session.refresh(competition)

        print("Competição cadastrada com sucesso!")
        print(competition)

    except Exception as error:
        session.rollback()
        print(f"Erro ao cadastrar competição: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    insert_competition()