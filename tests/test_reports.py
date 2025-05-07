from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.reports import search_category


def test_search_category() -> None:
    test_data = {
        "Дата операции": ["2022-01-01", "2022-02-01", "2022-03-01"],
        "Сумма операции": [100, 200, 300],
        "Категория": ["еда", "транспорт", "еда"],
    }
    transactions = pd.DataFrame(test_data)
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"])

    with patch("builtins.open", new_callable=MagicMock()) as mock_open:
        result = search_category(transactions, "еда", datetime(2022, 4, 10))
        assert result["category"] == "еда"
        assert result["total"] == -400  # 100 + 300 = 400 (с учетом инверсии)
        assert "amount" not in result  # Проверяем, что лишний ключ отсутствует
        assert list(result.keys()) == ["category", "total"]  # Проверяем все ключи


def test_search_category_empty_result() -> None:
    test_data = {
        "Дата операции": ["2022-01-01"],
        "Сумма операции": [100],
        "Категория": ["транспорт"],
    }
    transactions = pd.DataFrame(test_data)
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"])

    with patch("builtins.open", new_callable=MagicMock()) as mock_open:
        result = search_category(transactions, "еда", datetime(2022, 4, 10))
        assert result["category"] == "еда"
        assert result["total"] == 0.0
        assert "amount" not in result
