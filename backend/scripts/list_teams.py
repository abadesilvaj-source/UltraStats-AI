from app.database.session import SessionLocal
from app.services import TeamService


def main() -> None:
    session = SessionLocal()

    try:
        service = TeamService(session)

        teams = service.list_teams()

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
        print(f"Erro ao listar equipes: {error}")

    finally:
        session.close()


if __name__ == "__main__":
    main()