from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from .config import settings, get_database_url

# Create async engine based on database type
def create_engine():
    """Create database engine based on DATABASE_URL."""
    db_url = get_database_url()

    if "postgresql" in db_url:
        # PostgreSQL/Supabase configuration
        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            future=True,
        )
    else:
        # SQLite configuration
        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            future=True,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )

    return engine

# Create engine
engine = create_engine()

# Create session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)

async def init_db():
    """Initialize database tables."""
    from .models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Dependency for getting database session."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def close_db():
    """Close database connections."""
    await engine.dispose()

# Test connection function
async def test_connection():
    """Test database connection."""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
