from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, joinedload
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
import asyncio
import os
import logging
from dotenv import load_dotenv
import logging

load_dotenv()

def get_database_url():
    return f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"


db_url = get_database_url()
engine = create_async_engine(db_url, echo=False)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    ...



async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    logging.info('Dropping database...')
    logging.info(f"IM HERE!")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logging.info('Database dropped!')
            
    except Exception as e:
        logging.error(e)
        logging.warning('Database wasnt dropped!')
        