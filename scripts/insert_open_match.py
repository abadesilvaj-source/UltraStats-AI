from datetime import datetime

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Competition, Match, Team


def main() -> None:
    session = SessionLocal()

    try:
        competition = session.scalar(
            select(Competition).where(
                Competition.name
                == "Campeonato Brasileiro Série A",
                Competition.season == "2026",
            )
        )

        home_team = session.scalar(
            select(Team).where(
                Team.name == "Flamengo"
            )
        )

        away_team = session.scalar(
            select(Team).where(
                Team.name == "Palmeiras"
            )
        )

        if not competition:
            print(
                "Competição não encontrada."
            )
            return

        if not home_team or not away_team:
            print(
                "Equipes não encontradas."
            )
            return

        external_id = (
            "test-flamengo-palmeiras-open-2026"
        )

        existing_match = session.scalar(
            select(Match).where(
                Match.external_id
                == external_id
            )
        )

        if existing_match:
            print(
                "A partida já existe."
            )
            return

        match = Match(
            competition_id=competition.id,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            kickoff_at=datetime(
                2026,
                8,
                10,
                20,
                0,
            ),
            status="scheduled",
            home_score=None,
            away_score=None,
            venue="Maracanã",
            source="manual",
            external_id=external_id,
        )

        session.add(match)
        session.commit()
        session.refresh(match)

        print(
            "Partida aberta criada com sucesso!"
        )

        print(match)

    except Exception as error:
        session.rollback()

        print(
            f"Erro ao criar partida: {error}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()