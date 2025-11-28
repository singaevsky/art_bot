from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from .config import settings, get_database_url

# Import models to make them available
from .models import User, GalleryItem, Order, OrderEvent

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

# Create engine only when needed
engine = None
session_factory = None

def get_engine():
    global engine
    if engine is None:
        engine = create_engine()
    return engine

def get_session_factory():
    global session_factory
    if session_factory is None:
        session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )
    return session_factory

async def get_session() -> AsyncSession:
    """Dependency for getting database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        await session.close()

async def init_db():
    """Initialize database tables."""
    from .models import Base

    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Close database connections."""
    global engine, session_factory
    if engine:
        await engine.dispose()
        engine = None
    session_factory = None

# Test connection function
async def test_connection():
    """Test database connection."""
    try:
        async with get_engine().begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
