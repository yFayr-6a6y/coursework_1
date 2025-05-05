import json
from datetime import datetime, timedelta
from typing import Any, Optional

import pandas as pd

from src.utils import read_files, setup_logging

logger = setup_logging()


def search_category(transactions: pd.DataFrame, category: str, date: Optional[pd.Timestamp] = None) -> Any:
    """функция, которая принимает на вход список транзакций
    и возвращает новый список, содержащий только те словари, у которых ключ содержит переданное в функцию значение."""
    transactions = pd.DataFrame(transactions)
    if date is None:
        date = pd.to_datetime("today")
    result = {}
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    total = -transactions[
        (transactions["Дата операции"] >= date - timedelta(days=90))
        & (transactions["Дата операции"] <= date)
        & (transactions["Категория"] == category)
    ]["Сумма операции"]
    if not total.empty:
        result["amount"] = total.to_dict()
        result["category"] = category
        result["total"] = total.sum().item()
        with open("reports.json", "w", encoding="utf8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        logger.info(f"Result - {result}")
        return result


def reports_() -> None:
    print(f'\nОтсчет: {search_category(read_files("../data/operations.xls"), "еда", datetime(2022, 4, 10))}')