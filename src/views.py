import json

from config import PATH_DATA_USER_SET
from src.utils import cards, currency_rates, greeting, open_json, stock_prices, top_transactions


def views(date: str) -> str:  # pragma: no cover
    """Главная функция для страницы "Главная"
    на вход подается нужная дата,
    отдает JSON-ответ с необходимой информацией:
    1. Правильное приветствие в зависимости от времени суток
    2. Сумма по всем картам, от начала месяца до искомой даты
    3. Топ транзакций за период с начала месяца по искомую дату
    4. Курс валют, согласно настроек пользователя
    5. Стоимость акций"""
    dict_user = open_json(PATH_DATA_USER_SET)  # type: ignore
    json_ans = {
        "greeting": greeting(),
        "cards": cards(date),
        "top_transactions": top_transactions(date),
        "currency_rates": currency_rates(dict_user),
        "stock_prices": stock_prices(dict_user),
    }
    return json.dumps(json_ans, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    print(views("2021-12-12 12:12:21"))
