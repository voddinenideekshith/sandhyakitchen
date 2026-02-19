from core.config import settings
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker

DATABASE_URL = str(settings.DATABASE_URL)

if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL must be set in .env or environment')

# Handle `sslmode` query param (common with managed Postgres providers like Neon).
# asyncpg does not accept `sslmode` keyword; translate it into connect_args ssl.
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

parts = urlsplit(DATABASE_URL)
qs = dict(parse_qsl(parts.query))
connect_args = {}
# Remove known asyncpg-incompatible params and enable ssl via connect_args
removed = False
for k in ('sslmode', 'channel_binding'):
    if k in qs:
        qs.pop(k, None)
        removed = True
if removed:
    new_query = urlencode(qs, doseq=True)
    DATABASE_URL = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    connect_args = {"ssl": True}

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def init_db():
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
