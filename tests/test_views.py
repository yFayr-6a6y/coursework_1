import json
from typing import Any
from unittest import mock
from unittest.mock import MagicMock, patch

import pandas as pd
from pytest import fixture, mark

from src.utils import read_files
from src.views import card_info, currency_rate, send_greeting, stock_currency, sum_amount_of_card, total_cashback


@fixture()
def date_with_data() -> Any:
    return read_files("data/operations.xlsx")


@patch("yfinance.Ticker")
def test_stock_currency(mock_yfinance: Any) -> None:
    # Создаем объект DataFrame, который будет возвращен моком
    data = pd.DataFrame({"High": [150]})
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = data
    mock_yfinance.return_value = mock_ticker
    # Теперь вызовем функцию и проверим утверждение
    assert stock_currency("AAPL") == 150


def test_total_sum_amount(date_with_data: Any) -> None:
    assert sum_amount_of_card(date_with_data, "*7197") == -1928562


def test_get_cashback() -> None:
    assert total_cashback(10000) == 100
    assert total_cashback(500) == 5


def test_get_card_number(date_with_data: Any) -> None:
    assert card_info(date_with_data) == "*7197"


def test_get_stock_currency() -> None:
    mock_todays_data = mock.Mock()
    mock_todays_data_dict = [{"High": 500.0}]
    mock_todays_data.to_dict.return_value = mock_todays_data_dict

    with mock.patch("src.views.yf", autospec=True) as mock_yf:
        mock_ticker = mock.Mock()
        mock_yf.Ticker.return_value = mock_ticker
        mock_ticker.history.return_value = mock_todays_data

        result = stock_currency("TSLA")

        assert result == 0.0
        mock_yf.Ticker.assert_called_once_with("TSLA")


@patch("requests.get")
def test_get_currency_rate(mock_get: Any) -> None:
    mock_response = {"rates": {"RUB": 90.0}}
    mock_get.return_value.text = json.dumps(mock_response)
    transaction = {"amount": 100, "currency": "USD"}
    transaction1 = {"amount": 100, "currency": "EUR"}
    assert currency_rate(transaction) == 90.0
    assert currency_rate(transaction1) == 90.0


@mark.parametrize(
    "hour, expected",
    [
        ("30.08.2013 08:59", "Доброе утро!"),
        ("19.07.2012 13:30", "Добрый день!"),
        ("28.09.2020 21:15", "Добрый вечер!"),
        ("20.01.2024 00:01", "Доброй ночи!"),
    ],
)
def test_greeting(hour: str, expected: str) -> None:
    assert send_greeting(hour) == expected


def test_get_card_number(date_with_data: Any) -> None:
    assert "*7197" in card_info(date_with_data)  # Проверяем, что карта присутствует в списке


def test_total_sum_amount(date_with_data: Any) -> None:
    assert sum_amount_of_card(date_with_data, "*7197", "01.01.2023", "31.12.2023") == -1928562  # Укажите нужный период
