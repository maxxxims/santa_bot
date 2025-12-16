import logging
from bot.db import async_session
from bot.models import SantaPair, User
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import List, Union


async def add_pairs_orm_bulk(pairs: List[SantaPair]) -> None:
    async with async_session() as session:
        session.add_all(pairs)
        await session.commit()
        
        
async def get_reciver_user(giver_id: int, group_id: int) -> SantaPair:
    """
        Возвращает подопечного
    """
    async with async_session() as session:
        query = select(SantaPair).where(SantaPair.giver_id == int(giver_id), SantaPair.group_id == int(group_id)).options(joinedload(SantaPair.receiver))
        result = (await session.execute(query)).scalar_one_or_none()
        return result
    
async def get_giver_user(receiver_id: int, group_id: int) -> SantaPair:
    """
        Возвращает Санту
    """
    async with async_session() as session:
        query = select(SantaPair).where(SantaPair.receiver_id == int(receiver_id), SantaPair.group_id == int(group_id)).options(joinedload(SantaPair.giver))
        result = (await session.execute(query)).scalar_one_or_none()
        return result
    

async def get_by_user(user_id: int, group_id: int) -> SantaPair:
    """
        Возвращает инфу о юзере в группе 
    """
    async with async_session() as session:
        query = select(SantaPair).where(SantaPair.giver_id == int(user_id), SantaPair.group_id == int(group_id)).options(joinedload(SantaPair.giver))
        result = (await session.execute(query)).scalar_one_or_none()
        return result
    
    
async def increment_msg_counter(group_id: int, giver_id: int) -> bool:
    async with async_session() as session:
        query = (
            update(SantaPair)
            .where(
                SantaPair.group_id == group_id,
                SantaPair.giver_id == giver_id
            )
            .values(
                msg_counter=SantaPair.msg_counter + 1,
            )
        )
        
        result = await session.execute(query)
        await session.commit()
        
        # Проверяем, была ли обновлена хотя бы одна строка
        if result.rowcount > 0:
            logging.info(f"Счетчик увеличен для group_id={group_id}, giver_id={giver_id}")
        else:
            logging.info(f"Запись не найдена: group_id={group_id}, giver_id={giver_id}")
        
        return result.rowcount > 0