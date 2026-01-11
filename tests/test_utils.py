import os
from unittest.mock import patch, mock_open

import pandas as pd
from dotenv import load_dotenv
from freezegun import freeze_time

from src.utils import greeting, currency_rates, read_xlsx, get_operation_with_range, \
    get_operation_with_range_three_month, cards, top_transactions, open_json, stock_prices

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_2 = os.getenv("API_KEY_2")


def test_utils():
    """Тест функции вывода приветствия в зависимости от времени суток"""
    with freeze_time("2025-01-01 01:00:00"):
        assert greeting() == "Доброй ночи!"
    with freeze_time("2025-01-01 07:00:00"):
        assert greeting() == "Доброе утро!"
    with freeze_time("2025-01-01 13:00:00"):
        assert greeting() == "Добрый день!"
    with freeze_time("2025-01-01 19:00:00"):
        assert greeting() == "Доброй вечер!"


@patch('pandas.read_excel')
def test_read_xlsx(mock_pd, test_df_expected):
    mock_pd.return_value = test_df_expected
    result = read_xlsx('fake_file.xlsx')
    assert type(result) is pd.DataFrame
    mock_pd.assert_called_once_with('fake_file.xlsx')


def test_read_xlsx_not():
    assert read_xlsx('fake_file.xlsx') is None


@patch('requests.get')
def test_currency_rates(mock_get, user_set):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"result": 80}
    assert currency_rates(user_set) == [{'currency': 'USD', 'rate': 80.0}, {'currency': 'EUR', 'rate': 80.0}]
    mock_get.assert_called()


@patch('requests.get')
def test_currency_rates_not_status_cod(mock_get, user_set):
    mock_get.return_value.json.return_value = {"result": 80}
    assert currency_rates(user_set) == []
    mock_get.assert_called()


@patch('requests.get')
def test_stock_prices(mock_get, user_set):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"Meta Data": {"3. Last Refreshed": "2025-09-22"},
                                               "Time Series (Daily)": {"2025-09-22": {"1. open": 80.0}}}
    assert stock_prices(user_set) == [{'stock': 'AAPL', 'price': 80.0}, {'stock': 'AMZN', 'price': 80.0}]
    mock_get.assert_called()


@patch('requests.get')
def test_stock_prices_not_status_cod(mock_get, user_set):
    mock_get.return_value.json.return_value = {"Meta Data": {"3. Last Refreshed": "2025-09-22"},
                                               "Time Series (Daily)": {"2025-09-22": {"1. open": 80.0}}}
    assert stock_prices(user_set) == []
    mock_get.assert_called()


def test_get_operation_with_range():
    assert get_operation_with_range("2021-12-12 12:12:21") == "2021-12-01 00:00:00"


def test_get_operation_with_range_three_month():
    assert get_operation_with_range_three_month("2021-12-12 12:12:21") == "2021-09-12 12:12:21"


@patch('src.utils.read_xlsx')
def test_cards_not_date(mock_read, test_df):
    mock_read.return_value = test_df
    assert cards() == []
    mock_read.assert_called_once()


@patch('src.utils.read_xlsx')
def test_cards(mock_read, test_df):
    mock_read.return_value = test_df
    assert cards('2021-10-31 18:44:39') == [{'last_digits': '*4393', 'total_spent': -118.12, 'cashback': 0.0},
                                            {'last_digits': '*7197', 'total_spent': -302.94, 'cashback': 0.0}]
    mock_read.assert_called_once()


@patch('src.utils.read_xlsx')
def test_top_transactions(mock_read, test_df):
    mock_read.return_value = test_df
    assert top_transactions('2021-10-31 18:44:39') == [
        {'data': '31.10.2021', 'total_spent': -160.89, 'category': 'Супермаркеты', 'description': 'Колхоз'},
        {'data': '30.10.2021', 'total_spent': -118.12, 'category': 'Переводы', 'description': 'Магнит'},
        {'data': '30.10.2021', 'total_spent': -78.05, 'category': 'Супермаркеты', 'description': 'Колхоз'},
        {'data': '30.10.2021', 'total_spent': -64.0, 'category': 'Переводы', 'description': 'Колхоз'}]
    mock_read.assert_called_once()


@patch('src.utils.read_xlsx')
def test_top_transactions_not_date(mock_read, test_df):
    mock_read.return_value = test_df
    assert top_transactions() == []


@patch('builtins.open', new_callable=mock_open, read_data='[1, 2, 3]')
@patch('json.load')
def test_open_json(mock_json_load, mock_open_in):
    mock_json_load.return_value = {1: 2, 2: 3}
    result = open_json('fake_file.json')
    assert result == {1: 2, 2: 3}
    mock_open_in.assert_called_once_with('fake_file.json', encoding="utf-8")
    mock_json_load.assert_called_once()


@patch('builtins.open', new_callable=mock_open, read_data='[1, 2, 3]')
@patch('json.load')
def test_open_json_not_list(mock_json_load, mock_open_in):
    mock_json_load.return_value = [1, 2, 3]
    result = open_json('fake_file.json')
    assert result == {}
    mock_open_in.assert_called_once_with('fake_file.json', encoding="utf-8")
    mock_json_load.assert_called_once()


def test_open_json_not():
    assert open_json('not_file.json') == {}
