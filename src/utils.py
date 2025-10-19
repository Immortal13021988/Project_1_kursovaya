import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import requests
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from config import PATH_DATA_USER_SET, PATH_XLSX

load_dotenv()

API_KEY = os.getenv("API_KEY")

API_KEY_2 = os.getenv("API_KEY_2")


logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("../logs/utils.log", "a")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def greeting() -> str:  # type: ignore
    """Функция вывода приветствия в зависимости от времени суток"""
    hour = datetime.now().hour
    if 0 <= hour < 6:
        return "Доброй ночи!"
    elif 6 <= hour < 12:
        return "Доброе утро!"
    elif 12 <= hour < 18:
        return "Добрый день!"
    else:
        return "Доброй вечер!"


def read_xlsx(file_path: Path) -> pd.DataFrame or None:
    """
    Функция, которая принимает на вход путь до XLSX-файла и возвращает дата-фрейм
    """
    try:
        df = pd.read_excel(file_path)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        return df
    except FileNotFoundError:
        return None


def get_operation_with_range(date: str) -> str:
    """Функция получения периода"""
    date_start = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-01 00:00:00")
    return date_start


def get_operation_with_range_three_month(date: str) -> str:
    """Функция получения периода три месяца от переданной даты"""
    date_start = datetime.strptime(date, "%Y-%m-%d %H:%M:%S") - relativedelta(months=3)
    date_start = date_start.strftime("%Y-%m-%d %H:%M:%S")
    return date_start


def cards(date: Optional[str] = None) -> dict:  # type: ignore
    """Функция получения суммы операций по каждой карте в период от начала месяца до переданной даты,
    если дата не передана то до текущей"""
    if not date:
        date_now = datetime.now()
        date = date_now.strftime("%Y-%m-%d %H:%M:%S")
    data_df = read_xlsx(PATH_XLSX)
    data_df = data_df[
        (data_df["Дата операции"] >= get_operation_with_range(date)) & (data_df["Дата операции"] <= date)
        ]
    data_df = data_df[(data_df["Сумма платежа"] < 0) & (data_df["Статус"] == "OK")]
    total_df = data_df[["Номер карты", "Сумма платежа", "Кэшбэк"]].groupby("Номер карты").sum().reset_index()
    total_df.rename(
        columns={"Номер карты": "last_digits", "Сумма платежа": "total_spent", "Кэшбэк": "cashback"}, inplace=True
    )  # Как переименовать столбцы """
    total_dict = total_df.to_dict("records")
    return total_dict


def top_transactions(date: Optional[str] = None) -> dict[Any, Any]:  # type: ignore
    """Функция получения топовых операций в период от начала месяца до переданной даты,
    если дата не передана то до текущей"""
    data_df = read_xlsx(PATH_XLSX)
    if not date:
        date_now = datetime.now()
        date = date_now.strftime("%Y-%m-%d %H:%M:%S")
    data_df = data_df[
        (data_df["Дата операции"] >= get_operation_with_range(date)) & (data_df["Дата операции"] <= date)
        ]
    data_df = data_df[(data_df["Сумма платежа"] < 0) & (data_df["Статус"] == "OK")]
    total_df = (
        data_df[["Дата платежа", "Сумма платежа", "Категория", "Описание"]].sort_values(by="Сумма платежа").head(5)
    )
    total_df.rename(
        columns={
            "Дата платежа": "data",
            "Сумма платежа": "total_spent",
            "Категория": "category",
            "Описание": "description",
        },
        inplace=True,
    )  # Как переименовать столбцы
    total_dict = total_df.to_dict("records")
    return total_dict


def open_json(file_path: str) -> dict:
    """
    Функция, которая принимает на вход путь до JSON-файла и возвращает словарь с данными
    """
    try:
        with open(file_path, encoding="utf-8") as json_file:
            trans = json.load(json_file)
        if type(trans) is dict:
            return trans
        else:
            return {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def stock_prices(user_set: dict) -> list:
    """
    Функция получения стоимости акций согласно файла пользовательских настроек
    """
    try:
        logger.info('Выполняется обращение к API "https://www.alphavantage.co"')
        result_list = []
        for us in user_set["user_stocks"]:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={us}&apikey={API_KEY}"
            headers = {"apikey": API_KEY}
            response = requests.get(url, headers=headers)
            result = response.json()
            data = result["Meta Data"]["3. Last Refreshed"]
            result_list.append({"stock": us, "price": result["Time Series (Daily)"][data]["1. open"]})
            if response.status_code == 200:
                logger.info(f'Успешный запрос к API "https://www.alphavantage.co" по акции "{us}"')
                continue
            else:
                logger.error(f"Пустой ответ")
                return []
        return result_list
    except Exception as ex:
        logger.error(f"Произошла ошибка: {ex}")
        return []


def currency_rates(user_set: dict) -> list:
    """
    Функция получения курсов валют согласно файла пользовательских настроек
    """
    try:
        logger.info('Выполняется обращение к API "https://api.apilayer.com"')
        result_list = []
        for us in user_set["user_currencies"]:
            url = f"https://api.apilayer.com/exchangerates_data/convert?to={'RUB'}&from={us}&amount={1}"
            headers = {"apikey": API_KEY_2}
            response = requests.get(url, headers=headers)
            result = response.json()
            result_list.append({"currency": us, "rate": float(round(result["result"], 2))})
            if response.status_code == 200:
                logger.info(f'Успешный запрос к API "https://api.apilayer.com" по курсу валюты "{us}"')
                continue
            else:
                logger.error(f"Пустой ответ")
                return []
        return result_list
    except Exception as ex:
        logger.error(f"Произошла ошибка: {ex}")
        return []


# def get_sum_by_category(date: str = None) -> dict:
#     """Функция получения всех операций по категориям за 3 месяца от полученной даты"""
#     data_df = read_xlsx(PATH_XLSX)
#     if not date:
#         date = datetime.now()
#         date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
#         data_df = data_df[(data_df["Дата операции"] >= get_operation_with_range_three_month(date)) & (
#                 data_df["Дата операции"] <= date)]
#     data_df = data_df[(data_df["Сумма платежа"] < 0) & (data_df["Статус"] == "OK")]
#     total_df = data_df[["Сумма платежа", "Категория"]].groupby("Категория").sum().reset_index()
#     total_df.rename(columns={"Сумма платежа": "total_spent", "Категория": "category"},
#                     inplace=True)  # Как переименовать столбцы
#     total_dict = total_df.to_dict("records")
#     return total_dict


if __name__ == "__main__":
    # json_ans = get_sum_by_category("2021-12-12 12:12:21")
    dict_user = open_json(PATH_DATA_USER_SET)  # type: ignore
    json_ans = {
        "greeting": greeting(),
        "cards": cards("2021-12-12 12:12:21"),
        "top_transactions": top_transactions()
    }
    print(json.dumps(json_ans, ensure_ascii=False, indent=4))
