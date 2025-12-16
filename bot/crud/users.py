from bot.db import async_session
from bot.models import User
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import List, Union

async def add(user_id: int, username: str, full_name: str) -> None:
    async with async_session() as session:
        query = insert(User).values(user_id=user_id, username=username, full_name=full_name)
        await session.execute(query)
        await session.commit()
        
        
async def get_all() -> List[User]:
    async with async_session() as session:
        query = select(User)
        result = (await session.execute(query)).scalars().all()
        return result
    
async def get(user_id: int) -> User:
    async with async_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = (await session.execute(query)).scalar_one_or_none()
        return result
    
    
async def is_exist(user_id: int) -> bool:
    async with async_session() as session:
        query = select(User).where(User.user_id == user_id)
        result = (await session.execute(query)).scalar_one_or_none()
        return result is not None
    

async def get_user_and_group_info(user_id: int) -> Union[User, None]:
    async with async_session() as session:
        query = select(User).where(User.user_id == user_id).options(joinedload(User.groups))
        result = (await session.execute(query)).scalar_one_or_none()
        return result
