from datetime import datetime
import pandas as pd


file_path = PATH_DATA
def greating():
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


def read_xlsx(file_path: str) -> pd.DataFrame:
    """
    Функция, которая принимает на вход путь до XLSX-файла и возвращает дата-фрейм
    """
    try:
        df = pd.read_excel(file_path)
        return df
    except (Exception, FileNotFoundError):
        return None


print(PATH_DATA)
