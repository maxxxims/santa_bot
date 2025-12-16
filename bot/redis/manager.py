import redis.asyncio as redis
import json
import os
from typing import Optional, Any, Dict, Union
import logging

logger = logging.getLogger(__name__)

def convert_numbers(obj):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {convert_numbers(k): convert_numbers(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numbers(item) for item in obj]
    elif isinstance(obj, (int, float)):
        return int(obj)
    elif isinstance(obj, str):
        if obj.isnumeric():
            return int(obj)
        else:
            return obj
    else:
        return obj

class RedisManager:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Подключение к Redis"""
        try:
            self.redis = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                password=os.getenv('REDIS_PASSWORD'),  # Опционально
                decode_responses=True,  # Автоматически декодируем в строки
                encoding='utf-8'
            )
            
            # Проверяем подключение
            await self.redis.ping()
            logger.info("✅ Redis connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Закрытие соединения с Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("✅ Redis disconnected")
    
    async def set_key(self, key: str, value: Any, expire: int = None):
        """Установка значения с возможным TTL"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                await self.redis.setex(key, expire, value)
            else:
                await self.redis.set(key, value)
                
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
    
    async def get_key(self, key: str, default: Any = None) -> Union[Dict, None]:
        """Получение значения"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            
            # Пытаемся распарсить JSON
            try:
                return convert_numbers(json.loads(value))
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return default
    
    async def delete_key(self, key: str) -> bool:
        """Удаление ключа"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> list:
        """Получение ключей по паттерну"""
        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Redis keys error for pattern {pattern}: {e}")
            return []
    
    async def incr(self, key: str) -> int:
        """Инкремент значения"""
        try:
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Redis incr error for key {key}: {e}")
            return 0

    async def flush_all(self):
        """Очистить всю базу Redis"""
        if self.redis:
            await self.redis.flushdb()
            logger.info("✅ Redis flushed")
    
    
# Глобальный инстанс Redis
redis_manager = RedisManager()