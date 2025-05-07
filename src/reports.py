import json
import time
from datetime import datetime, timedelta
from typing import Any, Optional, Callable
from functools import wraps

import pandas as pd

from src.utils import read_files, setup_logging

logger = setup_logging()


def log_execution_time(func: Callable) -> Callable:
    """
    Декоратор для логирования времени выполнения функции и обработки ошибок.

    Args:
        func: Декорируемая функция.

    Returns:
        Обёрнутая функция.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Функция {func.__name__} выполнена за {execution_time:.4f} секунд")
            return result
        except Exception as e:
            logger.error(f"Ошибка в функции {func.__name__}: {str(e)}")
            raise

    return wrapper


@log_execution_time
def search_category(transactions: pd.DataFrame, category: str, date: Optional[pd.Timestamp] = None) -> dict[str, Any]:
    """
    Возвращает сумму операций по указанной категории за последние 90 дней.

    Args:
        transactions: DataFrame с данными транзакций.
        category: Категория для фильтрации.
        date: Дата, от которой отсчитывается период (по умолчанию - текущая дата).

    Returns:
        Словарь с категорией и общей суммой операций.
    """
    transactions = pd.DataFrame(transactions)
    if date is None:
        date = pd.to_datetime("today")
    result = {"category": category, "total": 0.0}

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    filtered_transactions = transactions[
        (transactions["Дата операции"] >= date - timedelta(days=90))
        & (transactions["Дата операции"] <= date)
        & (transactions["Категория"] == category)
    ]

    if not filtered_transactions.empty:
        total = -filtered_transactions["Сумма операции"].sum()
        result["total"] = total

    with open("reports.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    logger.info(f"Result - {result}")
    return result


def reports_() -> None:
    print(f'\nОтчет: {search_category(read_files("../data/operations.xlsx"), "еда", datetime(2022, 4, 10))}')
