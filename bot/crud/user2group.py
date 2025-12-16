from bot.db import async_session
from bot.models import User, Group, UserGroup
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import List, Union, Dict


async def add(user_id: int, group_id: int) -> int:
    async with async_session() as session:
        query = insert(UserGroup).values(user_id=user_id, group_id=group_id)
        await session.execute(query)
        await session.commit()
        
        
async def get_all() -> List[UserGroup]:
    async with async_session() as session:
        query = select(UserGroup)
        result = (await session.execute(query)).scalars().all()
        return result
    
async def get_wishlist(user_id: int, group_id: int) -> Union[str, None]:
    async with async_session() as session:
        query = select(UserGroup).where(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
        result = (await session.execute(query)).scalar_one_or_none()
        return result.wishlist
        

async def update_wishlist(user_id: int, group_id: int, wishlist: str) -> None:
    async with async_session() as session:
        query = update(UserGroup).where(UserGroup.user_id == user_id, UserGroup.group_id == group_id).values(wishlist=wishlist)
        await session.execute(query)
        await session.commit()
        
    
async def is_exist(user_id: int) -> bool:
    async with async_session() as session:
        query = select(UserGroup).where(UserGroup.user_id == user_id)
        result = (await session.execute(query)).scalar_one_or_none()
        return result is not None
    
    
async def get_user_groups(user_id: int) -> Dict[int, str]:
    async with async_session() as session:
        query = select(UserGroup).where(UserGroup.user_id == user_id).options(joinedload(UserGroup.group))
        result = (await session.execute(query)).scalars().all()
        if result is None or len(result) == 0:
            return {}
        # groups_info = [{'group_id': el.group_id, 'group_name': el.group.name} for el in result]
        groups_info = {el.group_id: el.group.name for el in result}
        return groups_info
        
        
    
async def delete_users_from_group(user_ids: List[int], group_id: int) -> None:
    async with async_session() as session:
        query = delete(UserGroup).where(UserGroup.user_id.in_(user_ids), UserGroup.group_id == group_id)
        await session.execute(query)
        await session.commit()
        
        
        
async def get_group_members(group_id: int) -> List[UserGroup]:
    async with async_session() as session:
        query = select(UserGroup).where(UserGroup.group_id == group_id)
        result = (await session.execute(query)).scalars().all()
        return result