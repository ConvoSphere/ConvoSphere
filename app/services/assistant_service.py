from sqlalchemy import and_, or_

class AssistantService:
    def __init__(self, db):
        self.db = db

    def get_assistants(self, user_id):
        query = self.db.query(Assistant).filter(
            or_(
                Assistant.creator_id == user_id,
                and_(Assistant.is_public, Assistant.status == AssistantStatus.ACTIVE)
            )
        )
        return query.all()

    def get_public_assistants(self):
        query = self.db.query(Assistant).filter(
            and_(
                Assistant.is_public,
                Assistant.status == AssistantStatus.ACTIVE
            )
        )
        return query.all() 