from typing import Annotated

from db_manager import get_db_session
from fastapi import Depends
from sqlalchemy.orm import Session

# Using Depends to inject a database session into each endpoint
DBSessionDep = Annotated[Session, Depends(get_db_session)]
