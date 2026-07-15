from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Competition, Match, Team


def list_matches() -> None:
    session = SessionLocal()

    try:
        statement = (
            select(
                Match,
                Competition.name,
                Team.name,
            )
            .join(
                Competition,
                Match.competition_id == Competition.id,
            )
            .join(
                Team,
                Match.home_team_id == Team.id,
            )
        )

        rows = session.execute(statement).all()

        if not rows:
            print("Nenhuma partida cadastrada.")
            return

        print("\nPartidas cadastradas:\n")

        for match, competition_name, home_team_name in rows:
            away_team = session.get(Team, match.away_team_id)

            print(
                f"ID: {match.id} | "
                f"Competição: {competition_name} | "
                f"Jogo: {home_team_name} x {away_team.name} | "
                f"Data: {match.kickoff_at} | "
                f"Status: {match.status}"
            )

    except Exception as error:
        print(f"Erro ao consultar partidas: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    list_matches()