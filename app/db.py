import os
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

# Get the database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create an asynchronous engine instance
# `echo=True` enables SQL query logging, useful for debugging
# `future=True` enables 2.0 style usage for SQLAlchemy, ensuring forward compatibility
engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

async def init_db():
    """
    Initialize the database by creating all the tables.
    This function is called at the startup of the application to ensure
    that the database schema is created based on the models defined.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """
    Generate a new asynchronous session for interacting with the database.
    This function is used as a dependency in FastAPI routes to provide
    a session scoped to a single request.
    
    Returns:
        AsyncSession: An asynchronous session object.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
