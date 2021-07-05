from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args={
        'check_same_thread': False,
    },
)


SessionLocal.configure(bind=engine)
