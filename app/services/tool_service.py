from sqlalchemy import and_

class ToolService:
    def get_available_tools(self, user_id, category):
        query = self.db.query(Tool).filter(Tool.is_enabled)
        return self.get_available_tools(user_id=user_id, category=category)

    def search_tools(self, query):
        tools = self.db.query(Tool).filter(
            and_(
                Tool.is_enabled,
                (Tool.name.ilike(f"%{query}%") | Tool.description.ilike(f"%{query}%"))
            )
        )
        return tools 