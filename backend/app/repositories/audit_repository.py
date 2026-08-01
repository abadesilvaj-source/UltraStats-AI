from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Audit


class AuditRepository:
    """Operações de banco relacionadas às auditorias."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_prediction_id(
        self,
        prediction_id: int,
    ) -> Audit | None:
        statement = select(Audit).where(
            Audit.prediction_id == prediction_id
        )

        return self.session.scalar(statement)

    def create(self, audit: Audit) -> Audit:
        self.session.add(audit)
        self.session.flush()

        return audit

    def update(self, audit: Audit) -> Audit:
        self.session.flush()

        return audit