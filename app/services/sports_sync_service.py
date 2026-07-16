from sqlalchemy.orm import Session

from app.collectors import (
    SportsDataCollector,
)
from app.models import (
    Competition,
    Match,
    Team,
)
from app.repositories import (
    CompetitionRepository,
    MatchRepository,
    TeamRepository,
)


class SportsSyncService:
    """
    Sincroniza dados de um provedor
    externo com o banco local.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

        self.competition_repository = (
            CompetitionRepository(session)
        )

        self.team_repository = (
            TeamRepository(session)
        )

        self.match_repository = (
            MatchRepository(session)
        )

    def sync_competitions(
        self,
        collector: SportsDataCollector,
    ) -> dict:
        """
        Sincroniza competições do provedor.

        Primeiro procura pelo identificador externo.
        Depois procura pelo nome e temporada.
        """

        created = 0
        updated = 0
        linked = 0

        rows = collector.fetch_competitions()

        for row in rows:
            competition = (
                self.competition_repository
                .find_by_source_and_external_id(
                    source=row.source,
                    external_id=row.external_id,
                )
            )

            if competition:
                competition.name = row.name
                competition.country = row.country
                competition.season = row.season
                competition.sport = row.sport
                competition.active = True

                self.competition_repository.update(
                    competition
                )

                updated += 1
                continue

            competition = (
                self.competition_repository
                .find_by_name_and_season(
                    name=row.name,
                    season=row.season,
                )
            )

            if competition:
                competition.country = row.country
                competition.sport = row.sport
                competition.source = row.source
                competition.external_id = row.external_id
                competition.active = True

                self.competition_repository.update(
                    competition
                )

                linked += 1
                continue

            competition = Competition(
                name=row.name,
                country=row.country,
                season=row.season,
                sport=row.sport,
                source=row.source,
                external_id=row.external_id,
                active=True,
            )

            self.competition_repository.create(
                competition
            )

            created += 1

        return {
            "created": created,
            "updated": updated,
            "linked": linked,
            "total": len(rows),
        }

    def sync_teams(
        self,
        collector: SportsDataCollector,
    ) -> dict:
        """
        Sincroniza equipes do provedor.

        Ordem de procura:

        1. source + external_id;
        2. nome da equipe;
        3. criação de uma nova equipe.
        """

        created = 0
        updated = 0
        linked = 0

        rows = collector.fetch_teams()

        for row in rows:
            # Primeiro procura pelo identificador do provedor.
            team = (
                self.team_repository
                .find_by_source_and_external_id(
                    source=row.source,
                    external_id=row.external_id,
                )
            )

            if team:
                team.name = row.name
                team.country = row.country
                team.league = row.league

                self.team_repository.update(
                    team
                )

                updated += 1
                continue

            # Se não encontrou pelo provedor,
            # procura uma equipe criada manualmente
            # com o mesmo nome.
            team = self.team_repository.find_by_name(
                row.name
            )

            if team:
                team.country = row.country
                team.league = row.league
                team.source = row.source
                team.external_id = row.external_id

                self.team_repository.update(
                    team
                )

                linked += 1
                continue

            # Se não encontrou por nenhum critério,
            # cria uma nova equipe.
            team = Team(
                name=row.name,
                country=row.country,
                league=row.league,
                source=row.source,
                external_id=row.external_id,
            )

            self.team_repository.create(
                team
            )

            created += 1

        return {
            "created": created,
            "updated": updated,
            "linked": linked,
            "total": len(rows),
        }

    def sync_matches(
        self,
        collector: SportsDataCollector,
    ) -> dict:
        created = 0
        updated = 0
        skipped = 0

        rows = collector.fetch_matches()

        for row in rows:
            competition = (
                self.competition_repository
                .find_by_source_and_external_id(
                    source=row.source,
                    external_id=(
                        row.competition_external_id
                    ),
                )
            )

            home_team = (
                self.team_repository
                .find_by_source_and_external_id(
                    source=row.source,
                    external_id=(
                        row.home_team_external_id
                    ),
                )
            )

            away_team = (
                self.team_repository
                .find_by_source_and_external_id(
                    source=row.source,
                    external_id=(
                        row.away_team_external_id
                    ),
                )
            )

            if (
                not competition
                or not home_team
                or not away_team
            ):
                skipped += 1
                continue

            match = (
                self.match_repository
                .find_by_source_and_external_id(
                    source=row.source,
                    external_id=row.external_id,
                )
            )

            if not match:
                match = Match(
                    competition_id=(
                        competition.id
                    ),
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    kickoff_at=row.kickoff_at,
                    status=row.status,
                    home_score=row.home_score,
                    away_score=row.away_score,
                    venue=row.venue,
                    source=row.source,
                    external_id=row.external_id,
                )

                self.match_repository.create(
                    match
                )

                created += 1

            else:
                match.competition_id = (
                    competition.id
                )
                match.home_team_id = (
                    home_team.id
                )
                match.away_team_id = (
                    away_team.id
                )
                match.kickoff_at = (
                    row.kickoff_at
                )
                match.status = row.status
                match.home_score = row.home_score
                match.away_score = row.away_score
                match.venue = row.venue

                self.match_repository.update(
                    match
                )

                updated += 1

        return {
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "total": len(rows),
        }

    def sync_all(
        self,
        collector: SportsDataCollector,
    ) -> dict:
        """
        Sincroniza tudo em uma transação.
        """

        try:
            competition_result = (
                self.sync_competitions(
                    collector
                )
            )

            team_result = self.sync_teams(
                collector
            )

            match_result = self.sync_matches(
                collector
            )

            self.session.commit()

            return {
                "source": collector.source_name,
                "competitions": (
                    competition_result
                ),
                "teams": team_result,
                "matches": match_result,
            }

        except Exception:
            self.session.rollback()
            raise