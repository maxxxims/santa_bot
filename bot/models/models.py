from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Boolean, Text, DateTime, ForeignKey, DECIMAL, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import func
import os
from datetime import datetime
from typing import List, Optional
from bot.db import Base
from uuid import uuid4

# Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(100))
    full_name = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    
    # Отношения
    groups = relationship("UserGroup", back_populates="user")
    admin_groups = relationship("Group", back_populates="admin")
    given_pairs = relationship("SantaPair", foreign_keys="SantaPair.giver_id", back_populates="giver")
    received_pairs = relationship("SantaPair", foreign_keys="SantaPair.receiver_id", back_populates="receiver")

class Group(Base):
    __tablename__ = 'groups'
    
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    description = Column(String(210), nullable=False)
    admin_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    is_active = Column(Boolean, default=True)
    is_shuffled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    invite_link = Column(UUID, nullable=False, default=uuid4)
    is_extended = Column(Boolean, default=False)
    
    # Отношения
    admin = relationship("User", back_populates="admin_groups")
    participants = relationship("UserGroup", back_populates="group", cascade="all, delete-orphan")
    santa_pairs = relationship("SantaPair", back_populates="group", cascade="all, delete-orphan")

class UserGroup(Base):
    __tablename__ = 'user_group'
    
    user_id = Column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'), primary_key=True)
    joined_at = Column(DateTime, default=func.now())
    wishlist = Column(String(500), nullable=True, default=None)
    
    # Отношения
    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="participants")

class SantaPair(Base):
    __tablename__ = 'santa_pairs'
    
    group_id = Column(Integer, ForeignKey('groups.group_id'), primary_key=True)
    giver_id = Column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
    receiver_id = Column(BigInteger, ForeignKey('users.user_id'))
    created_at = Column(DateTime, default=func.now())
    msg_counter = Column(Integer, default=0)
    
    # Отношения
    group = relationship("Group", back_populates="santa_pairs")
    giver = relationship("User", foreign_keys=[giver_id], back_populates="given_pairs")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_pairs")