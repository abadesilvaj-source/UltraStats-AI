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