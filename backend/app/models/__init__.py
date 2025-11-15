"""
Import all models here so Alembic can auto-detect them for migrations.
"""
from app.models.user import User
from app.models.query import Query
from app.models.response import QueryResponse
from app.models.activity import QueryActivity

__all__ = ["User", "Query", "QueryResponse", "QueryActivity"]
