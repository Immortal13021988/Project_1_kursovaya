import json
import logging

import pandas as pd

from config import PATH_XLSX, PATH_LOGS
from src.utils import read_xlsx

logger = logging.getLogger('service')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f"{PATH_LOGS}/service.log", "a")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def pd_search(data: pd.DataFrame, search: str) -> str:
    """
    Функция, выполняющая простой поиск по столбцу 'Категория' и 'Описание'
    На вход получает DataFrame и строку поиска
    возвращает JSON-ответ
    """
    try:
        logger.info(f'Выполняем поиск в столбцах "Категория" и "Описание" по строке поиска "{search}"')
        data["Дата операции"] = data["Дата операции"].apply(
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S")
        )  # преобразуем дату в строковое значение
        data_df = data[
            (data["Описание"].str.contains(search, case=False)) | (data["Категория"].str.contains(search, case=False))
        ]
        ret_df = json.dumps(data_df.to_dict("records"), ensure_ascii=False, indent=4)
        if data_df.empty:
            logger.info(f'Строка "{search}" не найдена')
            return ret_df
        else:
            logger.info(f'Строка "{search}" найдена')
            return ret_df
    except Exception as ex:
        logger.error(f"Произошла ошибка: {ex}")


if __name__ == "__main__":
    data_df_f = read_xlsx(PATH_XLSX)  # type: ignore
    print(pd_search(data_df_f, "РЖД"))  # для проверки, что ищет в обоих столбцах
