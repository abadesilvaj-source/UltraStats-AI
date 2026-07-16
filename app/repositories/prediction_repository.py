from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Prediction


class PredictionRepository:
    """Operações de banco relacionadas às previsões."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        prediction: Prediction,
    ) -> Prediction:
        self.session.add(prediction)
        self.session.flush()

        return prediction

    def find_by_id(
        self,
        prediction_id: int,
    ) -> Prediction | None:
        return self.session.get(
            Prediction,
            prediction_id,
        )

    def list_by_match_id(
        self,
        match_id: int,
    ) -> list[Prediction]:
        statement = select(Prediction).where(
            Prediction.match_id == match_id
        )

        return list(
            self.session.scalars(statement).all()
        )