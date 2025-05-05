import json
import os
from datetime import datetime
from typing import Any

import requests
import yfinance as yf
from dotenv import load_dotenv

from src.utils import read_files, setup_logging, write_data

load_dotenv()
api_key = os.getenv("API_KEY")
logger = setup_logging()


def send_greeting(h: Any) -> str:
    """
    возвращает приветственное сообщение в зависимости от времени суток.
    """
    if h is None:
        h = datetime.now()
    else:
        h = datetime.strptime(h, "%d.%m.%Y %H:%M")
    h = h.hour
    if 5 < h < 12:
        return "Доброе утро!"
    elif 12 <= h < 18:
        return "Добрый день!"
    elif 18 <= h < 24:
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


def card_info(data: Any) -> Any:
    """
    возвращает номер карты пользователя.
    """
    if data is not None:
        for transaction in data:
            logger.info("Результат 'card_info' - %s" % transaction)
            return transaction["Номер карты"]
    else:
        logger.info("Данных не найдено")
        return None


def sum_amount_of_card(data: Any, card: Any) -> int:
    """
    возвращает общую сумму всех транзакций пользователя.
    """
    total = 0
    if card:
        for transaction in data:
            total += transaction["Сумма операции"]
    logger.info("Результат 'sum_amount_of_card' - %s" % transaction)
    return round(total)


def total_cashback(sum: int) -> int:
    """
    возвращает весь кешбек
    """
    total = sum // 100
    logger.info("Результат 'total_cashback' - %s" % total)
    return total


def top_5_transactions(data: Any) -> list[dict[str, Any]] | None:
    """
    возвращает топ-5 транзакций пользователя по сумме.
    """
    if data is not None:

        def sum_of_operation(transaction: Any) -> Any:
            return transaction["Сумма операции"]

        data.sort(key=sum_of_operation, reverse=True)

        result: list = []
        for operation in data:
            if len(result) < 5:
                result.append(
                    {
                        "date": operation["Дата операции"],
                        "amount": round(operation["Сумма операции"], 2),
                        "category": operation["Категория"],
                        "description": operation["Описание"],
                    }
                )
            else:
                break
        logger.info("Результат 'top_5_transactions' - %s" % result)
        return result
    else:
        logger.error("Данных не найдено")
        return None


def currency_rate(currency: Any) -> Any:
    """
    возвращает курс валюты.
    """
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols=RUB&base={currency}"
    response = requests.get(url, headers={"apikey": api_key}, timeout=15)
    response_data = json.loads(response.text)
    rate = response_data["rates"]
    logger.info("Результат 'currency_rate' - %s" % rate)
    return rate["RUB"]


def stock_currency(stock: str) -> Any:
    """
    возвращает курс акции из S&P 500.
    """
    ticker = yf.Ticker(stock)
    todays_data = ticker.history(period="1d")

    if not todays_data.empty:
        high_price = todays_data["High"].iloc[0]
        return high_price
    else:
        return 0.0


def create_operations(greetin: Any, card_numbers: Any, total_sum: Any, cashbacks: Any, top: Any) -> Any:
    """
    возвращает словарь с данными пользователя.
    """
    data = {"greeting": greetin, "cards": [], "top_transactions": [], "currency_rates": [], "stock_prices": []}
    if card_numbers not in [card["last_digits"] for card in data["cards"]] and card_numbers is not None:
        data["cards"].append({"last_digits": card_numbers, "total_spent": round(total_sum, 2), "cashback": cashbacks})
    data["top_transactions"] = top
    data["currency_rates"].append(
        (
            {"currency": "USD", "rate": round(currency_rate("USD"), 2)},
            {"currency": "EUR", "rate": round(currency_rate("EUR"), 2)},
        )
    )
    data["stock_prices"].append(
        [
            {"stock": "AAPL", "price": round(stock_currency("AAPL"), 2)},
            {"stock": "AMZN", "price": round(stock_currency("AMZN"), 2)},
            {"stock": "GOOGL", "price": round(stock_currency("GOOGL"), 2)},
            {"stock": "MSFT", "price": round(stock_currency("MSFT"), 2)},
            {"stock": "TSLA", "price": round(stock_currency("TSLA"), 2)},
        ]
    )
    logger.info("Результат 'create_operations' - %s" % data)
    return data


def views_() -> None:
    time = input("Введите время(в формате - DD.MM.YYYY HH:MM):")
    greetin = send_greeting(time if time else None)
    card_numbers = card_info(read_files("../data/operations.xls"))
    total_sum = sum_amount_of_card(read_files("../data/operations.xls"), card_numbers)
    cashbacks = total_cashback(total_sum)
    top = top_5_transactions(read_files("../data/operations.xls"))
    created = create_operations(greetin, card_numbers, total_sum, cashbacks, top)
    write_data("views.json", created)
    print(f'Главная:{read_files("views.json")}')