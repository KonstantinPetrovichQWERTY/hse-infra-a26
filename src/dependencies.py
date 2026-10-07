from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]
