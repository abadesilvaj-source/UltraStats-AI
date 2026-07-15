from app.database.session import SessionLocal
from app.models import Competition, Team
from app.services import MatchService


def main() -> None:
    session = SessionLocal()

    try:
        service = MatchService(session)

        matches = service.list_matches()

        if not matches:
            print("Nenhuma partida cadastrada.")
            return

        print("\nPartidas cadastradas:\n")

        for match in matches:
            competition = session.get(
                Competition,
                match.competition_id,
            )

            home_team = session.get(
                Team,
                match.home_team_id,
            )

            away_team = session.get(
                Team,
                match.away_team_id,
            )

            print(
                f"ID: {match.id} | "
                f"Competição: {competition.name} | "
                f"Jogo: {home_team.name} x {away_team.name} | "
                f"Data: {match.kickoff_at} | "
                f"Status: {match.status}"
            )

    except Exception as error:
        print(f"Erro ao listar partidas: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    main()