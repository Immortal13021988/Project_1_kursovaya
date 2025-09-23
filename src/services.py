import json
import logging

import pandas as pd

from config import PATH_XLSX
from src.utils import read_xlsx

logger = logging.getLogger(__name__)


def pd_search(data: pd.DataFrame, search: str) -> str:
    """
    Функция, выполняющая простой поиск по столбцу 'Категория' и 'Описание'
    На вход получает DataFrame и строку поиска
    возвращает JSON-ответ
    """
    data["Дата операции"] = data["Дата операции"].apply(
        lambda x: x.strftime("%Y-%m-%d %H:%M:%S")
    )  # преобразуем дату в строковое значение
    data_df = data[
        (data["Описание"].str.contains(search, case=False)) | (data["Категория"].str.contains(search, case=False))
    ]

    return json.dumps(data_df.to_dict("records"), ensure_ascii=False, indent=4)


if __name__ == "__main__":
    data_df_f = read_xlsx(PATH_XLSX)  # type: ignore
    print(pd_search(data_df_f, "жк"))  # для проверки, что ищет в обоих столбцах
