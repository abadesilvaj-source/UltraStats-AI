from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Team


def list_teams() -> None:
    session = SessionLocal()

    try:
        statement = select(Team).order_by(Team.name)
        teams = session.scalars(statement).all()

        if not teams:
            print("Nenhuma equipe cadastrada.")
            return

        print("\nEquipes cadastradas:\n")

        for team in teams:
            print(
                f"ID: {team.id} | "
                f"Nome: {team.name} | "
                f"País: {team.country} | "
                f"Liga: {team.league} | "
                f"Power: {team.power_rating}"
            )

    except Exception as error:
        print(f"Erro ao consultar equipes: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    list_teams()