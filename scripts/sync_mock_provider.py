from app.collectors import MockSportsCollector
from app.database.session import SessionLocal
from app.services import SportsSyncService


def main() -> None:
    session = SessionLocal()

    try:
        collector = MockSportsCollector(
            "data/providers/mock_sports_data.json"
        )

        service = SportsSyncService(
            session
        )

        result = service.sync_all(
            collector
        )

        print("\nSINCRONIZAÇÃO CONCLUÍDA")
        print("=" * 60)

        print(
            f"Fonte: {result['source']}"
        )

        print(
            f"Competições: "
            f"{result['competitions']}"
        )

        print(
            f"Equipes: "
            f"{result['teams']}"
        )

        print(
            f"Partidas: "
            f"{result['matches']}"
        )

    except Exception as error:
        session.rollback()

        print(
            f"Erro na sincronização: {error}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()