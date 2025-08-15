from src.utils import greating
from freezegun import freeze_time


def test_utils():
    """Тест функции вывода приветствия в зависимости от времени суток"""
    with freeze_time("2025-01-01 01:00:00"):
        assert greating() == "Доброй ночи!"
    with freeze_time("2025-01-01 07:00:00"):
        assert greating() == "Доброе утро!"
    with freeze_time("2025-01-01 13:00:00"):
        assert greating() == "Добрый день!"
    with freeze_time("2025-01-01 19:00:00"):
        assert greating() == "Доброй вечер!"
