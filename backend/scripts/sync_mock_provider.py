from app.collectors import (
    MockSportsCollector,
)
from app.database.session import (
    SessionLocal,
)
from app.services import (
    CollectorOrchestratorService,
)


def main() -> None:
    session = SessionLocal()

    try:
        collector = MockSportsCollector(
            "data/providers/mock_sports_data.json"
        )

        service = (
            CollectorOrchestratorService(
                session
            )
        )

        execution = service.run(
            collector=collector,
            triggered_by="manual",
        )

        result = execution["result"]

        print("\nSINCRONIZAÇÃO CONCLUÍDA")
        print("=" * 60)

        print(
            f"Execução ID: "
            f"{execution['sync_run_id']}"
        )

        print(
            f"Status: "
            f"{execution['status']}"
        )

        print(
            f"Fonte: "
            f"{execution['source']}"
        )

        print(
            f"Duração: "
            f"{execution['duration_seconds']:.4f}s"
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
        print(
            f"Erro na sincronização: {error}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()