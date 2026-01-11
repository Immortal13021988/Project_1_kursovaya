import json

from src.reports import spending_by_category


def test_spending_by_category(test_df):
    assert spending_by_category(test_df, "Переводы", "2021-12-12 12:12:21") == json.dumps(
        [{"category": "Переводы", "total_spent": -182.12}], ensure_ascii=False, indent=4)


def test_spending_by_category_not_date(test_df):
    assert spending_by_category(test_df, "Переводы") == json.dumps(
        [], ensure_ascii=False, indent=4)
