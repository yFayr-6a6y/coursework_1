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


def card_info(data: Any) -> list[str]:
    """
    возвращает список уникальных номеров карт пользователя.
    """
    if data is not None:
        unique_cards = list(set(transaction["Номер карты"] for transaction in data))
        logger.info("Результат 'card_info' - %s" % unique_cards)
        return unique_cards
    else:
        logger.info("Данных не найдено")
        return []


def sum_amount_of_card(data: Any, card: str, start_date: str = None, end_date: str = None) -> float:
    """
    возвращает общую сумму транзакций для указанной карты за указанный период.
    """
    total = 0
    if card and data:
        for transaction in data:
            transaction_date = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            # Проверяем, попадает ли дата транзакции в указанный период
            if start_date and end_date:
                start = datetime.strptime(start_date, "%d.%m.%Y")
                end = datetime.strptime(end_date, "%d.%m.%Y")
                if not (start <= transaction_date <= end):
                    continue
            if transaction["Номер карты"] == card:
                total += transaction["Сумма операции"]
    logger.info("Результат 'sum_amount_of_card' для карты %s - %s" % (card, total))
    return round(total, 2)


def total_cashback(sum: int) -> int:
    """
    возвращает весь кешбек
    """
    total = sum // 100
    logger.info("Результат 'total_cashback' - %s" % total)
    return total


def top_5_transactions(data: Any, start_date: str = None, end_date: str = None) -> list[dict[str, Any]] | None:
    """
    возвращает топ-5 транзакций пользователя по сумме за указанный период.
    """
    if data is not None:
        filtered_data = []
        if start_date and end_date:
            start = datetime.strptime(start_date, "%d.%m.%Y")
            end = datetime.strptime(end_date, "%d.%m.%Y")
            for transaction in data:
                transaction_date = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
                if start <= transaction_date <= end:
                    filtered_data.append(transaction)
        else:
            filtered_data = data

        def sum_of_operation(transaction: Any) -> Any:
            return transaction["Сумма операции"]

        filtered_data.sort(key=sum_of_operation, reverse=True)

        result = []
        for operation in filtered_data:
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


def create_operations(greetin: str, cards: list[str], data: Any, start_date: str = None, end_date: str = None) -> dict:
    """
    возвращает словарь с данными пользователя, включая группировку по картам.
    """
    result = {
        "greeting": greetin,
        "cards": [],
        "top_transactions": [],
        "currency_rates": [],
        "stock_prices": [],
    }

    # Добавляем информацию по каждой карте
    for card in cards:
        total_sum = sum_amount_of_card(data, card, start_date, end_date)
        cashback = total_cashback(total_sum)
        result["cards"].append(
            {
                "last_digits": card,
                "total_spent": total_sum,
                "cashback": cashback,
            }
        )

    # Топ-5 транзакций (фильтруем по периоду, если указан)
    result["top_transactions"] = top_5_transactions(data, start_date, end_date)

    result["currency_rates"].append(
        (
            {"currency": "USD", "rate": round(currency_rate("USD"), 2)},
            {"currency": "EUR", "rate": round(currency_rate("EUR"), 2)},
        )
    )
    result["stock_prices"].append(
        [
            {"stock": "AAPL", "price": round(stock_currency("AAPL"), 2)},
            {"stock": "AMZN", "price": round(stock_currency("AMZN"), 2)},
            {"stock": "GOOGL", "price": round(stock_currency("GOOGL"), 2)},
            {"stock": "MSFT", "price": round(stock_currency("MSFT"), 2)},
            {"stock": "TSLA", "price": round(stock_currency("TSLA"), 2)},
        ]
    )

    logger.info("Результат 'create_operations' - %s" % result)
    return result


def views_() -> None:
    time = input("Введите время (в формате - DD.MM.YYYY HH:MM): ")
    start_date = input("Введите дату начала периода (в формате - DD.MM.YYYY): ")
    end_date = input("Введите дату конца периода (в формате - DD.MM.YYYY): ")

    greetin = send_greeting(time if time else None)
    data = read_files("../data/operations.xlsx")
    card_numbers = card_info(data)
    created = create_operations(greetin, card_numbers, data, start_date, end_date)
    write_data("views.json", created)
    print(f'Главная: {read_files("views.json")}')
