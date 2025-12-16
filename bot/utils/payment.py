import aiohttp
import hashlib
import json
from bot.config import TERMINAL_KEY, BOT_URL, TERMINAL_PWD
import logging


def generate_token(request_data, password):
    """
    Генерирует токен (подпись) для запроса к API Тинькофф Эквайринга.
    
    :param request_data: dict - данные запроса (корневые параметры, без вложенных объектов)
    :param password: str - пароль терминала из ЛК
    :return: str - токен SHA-256
    """
    # 1. Копируем данные, добавляем пароль
    data_for_token = request_data.copy()
    data_for_token['Password'] = password
    
    # 2. Преобразуем в список словарей и сортируем по ключу
    items = [{'key': k, 'value': v} for k, v in data_for_token.items()]
    items.sort(key=lambda x: x['key'])
    
    # 3. Конкатенируем значения (ВАЖНО: все значения как строки)
    concatenated = ''.join(str(item['value']) for item in items)
    
    # 4. Вычисляем SHA-256
    token = hashlib.sha256(concatenated.encode('utf-8')).hexdigest()
    return token

async def initialize_payment(order_id: str, SUB_PRICE_RUB: int, username: str, group_name: str) -> str:
    request_body = {
        "TerminalKey": TERMINAL_KEY,
        "Amount": SUB_PRICE_RUB * 100,  # Сумма в копейках (1400 рублей)
        "OrderId": order_id,
        "Description": f"""Оплата подписки пользователя {username} в группе тайного Санты "{group_name}" """,
        # "SuccessURL": BOT_URL,
        # "FailURL": BOT_URL,
        "PayType": "O"
    }
    
    # --- 2. Генерируем токен для этого конкретного запроса ---
    token = generate_token(request_body, TERMINAL_PWD)

    # --- 3. Добавляем токен в запрос ---
    request_body["Token"] = token

    # --- 4. Отправляем запрос ---
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # connector = aiohttp.TCPConnector(ssl=False)  # ⚠️ Отключаем проверку SSL #connector=connector
    try:
        async with aiohttp.ClientSession() as session: 
            async with session.post("https://securepay.tinkoff.ru/v2/Init", headers=headers, json=request_body) as response:
                data = await response.json()
                logging.info(f"request_body = {request_body}")
                logging.info(data)
                url = data['PaymentURL']
                payment_id = data['PaymentId']
                return url, payment_id
    except Exception as e:
        logging.error(f"Ошибка соединения: {e}")
        return None, None
    
    
async def check_payment(payment_id: str, SUB_PRICE_RUB: int):
    request_body = {
        "TerminalKey": TERMINAL_KEY,
        "PaymentId": str(payment_id),
    }
    token = generate_token(request_body, TERMINAL_PWD)

    # --- 3. Добавляем токен в запрос ---
    request_body["Token"] = token
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    URL = "https://securepay.tinkoff.ru/v2/GetState"
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session: 
            async with session.post(URL, headers=headers, json=request_body) as response:
                data = await response.json()
                logging.info(f'CHECK STATUS URL = {URL}')
                logging.info(f'headers = {headers}; request_body = {request_body}')
                logging.info(data)
                assert data['Success'] == True, f"data['Success'] = {data['Success']}"
                assert data["Status"] == "CONFIRMED", f"data['Status'] = {data['Status']}"
                assert data['PaymentId'] == payment_id, f"data['PaymentId'] = {data['PaymentId']}"
                assert data['Amount'] == SUB_PRICE_RUB * 100, f"data['Amount'] = {data['Amount']}"
                
                return True
                
    except Exception as e:
        logging.error(f"Ошибка соединения: {e}")
        return False