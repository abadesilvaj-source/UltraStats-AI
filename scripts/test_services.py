from datetime import datetime

from app.database.session import SessionLocal
from app.services import MatchService, TeamService


def main() -> None:
    session = SessionLocal()

    try:
        team_service = TeamService(session)
        match_service = MatchService(session)

        teams = team_service.list_teams()

        print("\nEquipes encontradas:")

        for team in teams:
            print(
                f"- {team.name} | "
                f"Power: {team.power_rating}"
            )

        matches = match_service.list_matches()

        print("\nPartidas encontradas:")

        for match in matches:
            print(
                f"- ID: {match.id} | "
                f"Data: {match.kickoff_at} | "
                f"Status: {match.status}"
            )

        print("\nServices funcionando corretamente!")

    except Exception as error:
        print(f"Erro ao testar os services: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    main()