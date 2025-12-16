from bot.db import async_session
from bot.models import User, Group, UserGroup
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime
from typing import List, Union, Tuple
from uuid import uuid4, UUID
import logging

async def add(user_id: int, group_name: str, group_description: str, is_extended: bool = False) -> Tuple[int, UUID]:
    async with async_session() as session:
        query = insert(Group).values(admin_id=user_id, is_active=True, name=group_name, description=group_description, is_extended=is_extended).returning(Group.group_id, Group.invite_link)
        result = await session.execute(query)
        row = result.fetchone()
        await session.commit()
        group_id, link = row.group_id, row.invite_link
        return group_id, link
    

async def get_all() -> List[Group]:
    async with async_session() as session:
        query = select(Group)
        result = (await session.execute(query)).scalars().all()
        return result
    
    
async def get(group_id: int) -> Group:
    async with async_session() as session:
        query = select(Group).options(selectinload(Group.participants)).where(Group.group_id == group_id)
        result = (await session.execute(query)).scalar_one()
        return result
    

async def get_by_link(invite_link: Union[str, UUID]) -> Union[Group, None]:
    _invite_link = invite_link
    if isinstance(invite_link, str):
        _invite_link = UUID(invite_link)
    async with async_session() as session:
        # query = select(Group).where(Group.invite_link == _invite_link)
        query = (
            select(Group)
            .options(selectinload(Group.participants))
            .where(Group.invite_link == _invite_link)
        )
        
        result = (await session.execute(query)).scalar_one_or_none()
        return result
    
    
    
async def set_shuffle_status(group_id: int, is_shuffled: bool) -> None:
    async with async_session() as session:
        query = update(Group).where(Group.group_id == group_id).values(is_shuffled=is_shuffled)
        await session.execute(query)
        await session.commit()
        
        
async def remove(group_id: int) -> None:
    async with async_session() as session:
        query = delete(Group).where(Group.group_id == group_id)
        await session.execute(query)
        await session.commit()
        

async def get_user_groups(user_id: int) -> List[Group]:
    async with async_session() as session:
        query = (
            select(Group)
            .join(UserGroup, Group.group_id == UserGroup.group_id)
            .where(UserGroup.user_id == user_id)
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    
async def extend(group_id: int, is_extended: bool = True) -> None:
    async with async_session() as session:
        query = update(Group).where(Group.group_id == group_id).values(is_extended=is_extended)
        await session.execute(query)
        await session.commit()