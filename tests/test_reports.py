from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd

from src.reports import search_category


def test_search_category() -> None:
    test_data = {
        "Дата операции": ["2022-01-01", "2022-02-01", "2022-03-01"],
        "Сумма операции": [100, 200, 300],
        "Категория": ["еда", "транспорт"],
    }
    transactions = pd.DataFrame(test_data)
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"])

    with patch("builtins.open", new_callable=MagicMock()) as mock_open:
        result = search_category(transactions, "еда", datetime(2022, 1, 10))
        assert result["category"] == "еда"
        assert result["total"] == -100