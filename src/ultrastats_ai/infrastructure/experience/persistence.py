"""Persistência de preferências e interações da experiência."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ultrastats_ai.domain.experience import (
    AlertRule,
    Favorite,
    Notification,
    UserExperienceProfile,
)
from ultrastats_ai.infrastructure.database.models import (
    AutomaticReportRecord,
    PushSubscriptionRecord,
    UserAlertRecord,
    UserExperienceProfileRecord,
    UserFavoriteRecord,
    UserNotificationRecord,
)


class ExperienceStore:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_profile(
        self,
        profile: UserExperienceProfile,
        updated_at: datetime,
    ) -> UserExperienceProfileRecord:
        record = self.session.get(UserExperienceProfileRecord, profile.user_id)
        if record is None:
            record = UserExperienceProfileRecord(user_id=profile.user_id)
            self.session.add(record)
        record.mode = profile.mode.value
        record.locale = profile.locale
        record.accessibility = {
            "reduced_motion": profile.reduced_motion,
            "high_contrast": profile.high_contrast,
        }
        record.updated_at = updated_at
        return record

    def add_favorite(self, favorite: Favorite, created_at: datetime) -> UserFavoriteRecord:
        existing = self.session.scalar(
            select(UserFavoriteRecord).where(
                UserFavoriteRecord.user_id == favorite.user_id,
                UserFavoriteRecord.entity_type == favorite.entity_type,
                UserFavoriteRecord.entity_id == favorite.entity_id,
            )
        )
        if existing is not None:
            existing.label = favorite.label
            return existing
        record = UserFavoriteRecord(
            user_id=favorite.user_id,
            entity_type=favorite.entity_type,
            entity_id=favorite.entity_id,
            label=favorite.label,
            created_at=created_at,
        )
        self.session.add(record)
        return record

    def remove_favorite(self, user_id: str, entity_type: str, entity_id: str) -> int:
        result = self.session.execute(
            delete(UserFavoriteRecord).where(
                UserFavoriteRecord.user_id == user_id,
                UserFavoriteRecord.entity_type == entity_type,
                UserFavoriteRecord.entity_id == entity_id,
            )
        )
        return result.rowcount

    def favorites(self, user_id: str) -> tuple[UserFavoriteRecord, ...]:
        return tuple(
            self.session.scalars(
                select(UserFavoriteRecord)
                .where(UserFavoriteRecord.user_id == user_id)
                .order_by(UserFavoriteRecord.label, UserFavoriteRecord.entity_id)
            ).all()
        )

    def save_alert(self, alert: AlertRule) -> UserAlertRecord:
        record = self.session.get(UserAlertRecord, alert.alert_id)
        if record is None:
            record = UserAlertRecord(id=alert.alert_id)
            self.session.add(record)
        record.user_id = alert.user_id
        record.metric = alert.metric
        record.operator = alert.operator
        record.threshold = str(alert.threshold)
        record.channel = alert.channel.value
        record.active = True
        return record

    def notify(self, notification: Notification) -> UserNotificationRecord:
        record = UserNotificationRecord(
            id=notification.notification_id,
            user_id=notification.user_id,
            title=notification.title,
            body=notification.body,
            channel=notification.channel.value,
            read=notification.read,
            created_at=notification.created_at,
        )
        self.session.add(record)
        return record

    def mark_read(self, notification_id: str) -> bool:
        record = self.session.get(UserNotificationRecord, notification_id)
        if record is None:
            return False
        record.read = True
        return True

    def notification_feed(self, user_id: str) -> tuple[UserNotificationRecord, ...]:
        return tuple(
            self.session.scalars(
                select(UserNotificationRecord)
                .where(UserNotificationRecord.user_id == user_id)
                .order_by(UserNotificationRecord.created_at.desc())
            ).all()
        )

    def subscribe_push(
        self,
        user_id: str,
        endpoint: str,
        public_key: str,
        created_at: datetime,
    ) -> PushSubscriptionRecord:
        if not user_id.strip() or not endpoint.startswith("https://") or not public_key.strip():
            raise ValueError("Push exige usuário, endpoint HTTPS e chave pública.")
        existing = self.session.scalar(
            select(PushSubscriptionRecord).where(
                PushSubscriptionRecord.user_id == user_id,
                PushSubscriptionRecord.endpoint == endpoint,
            )
        )
        if existing is not None:
            existing.public_key = public_key
            existing.active = True
            return existing
        record = PushSubscriptionRecord(
            user_id=user_id,
            endpoint=endpoint,
            public_key=public_key,
            active=True,
            created_at=created_at,
        )
        self.session.add(record)
        return record

    def save_report(
        self,
        user_id: str,
        title: str,
        content: str,
        generated_at: datetime,
    ) -> AutomaticReportRecord:
        if not all(value.strip() for value in (user_id, title, content)):
            raise ValueError("Relatório persistente exige usuário, título e conteúdo.")
        record = AutomaticReportRecord(
            user_id=user_id,
            title=title,
            content=content,
            generated_at=generated_at,
        )
        self.session.add(record)
        return record
