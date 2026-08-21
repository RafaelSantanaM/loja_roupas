"""
app/schemas/auth_schemas.py
=============================
Schema do corpo esperado em /auth/refresh e /auth/logout.
"""

from pydantic import BaseModel


class RefreshRequest(BaseModel):
    refresh_token: str
