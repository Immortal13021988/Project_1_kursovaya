import json
from datetime import datetime
from typing import Optional

import pandas as pd

from config import PATH_LOGS, PATH_XLSX
from src.utils import get_operation_with_range_three_month, read_xlsx


def decorator_with_args(file: str):  # pragma: no cover
    """Функция, которая записывает результаты из spending_by_category в логи"""

    def my_decorator(func):  # type: ignore
        def wrapper(*args, **kwargs):  # type: ignore
            try:
                result = func(*args, **kwargs)
                with open(file, "w", encoding="utf-8") as file_2:
                    file_2.write(result)
                return result
            except FileNotFoundError:
                print("Не получилось записать информацию в файл")

        return wrapper

    return my_decorator


@decorator_with_args(PATH_LOGS / "report.json")  # type: ignore
def spending_by_category(data_df: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """Функция, которая возвращает Json- ответ с тратами по заданной категории
    за последние три месяца (от переданной даты)."""
    if not date:
        date = datetime.now()  # type: ignore
        date = date.strftime("%Y-%m-%d %H:%M:%S")  # type: ignore
    data_df = data_df[
        (data_df["Дата операции"] >= get_operation_with_range_three_month(date))
        & (data_df["Дата операции"] <= date)
        & (data_df["Категория"] == category)
    ]
    data_df = data_df[(data_df["Сумма платежа"] < 0) & (data_df["Статус"] == "OK")]
    total_df = data_df[["Сумма платежа", "Категория"]].groupby("Категория").sum().reset_index()
    total_df.rename(columns={"Сумма платежа": "total_spent", "Категория": "category"}, inplace=True)

    json_ans = total_df.to_dict("records")
    return json.dumps(json_ans, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    data_df_f = read_xlsx(PATH_XLSX)  # type: ignore
    print(spending_by_category(data_df_f, "Переводы", "2021-12-12 12:12:21"))
