from config import PATH_XLSX
from src.reports import spending_by_category
from src.services import pd_search
from src.utils import read_xlsx
from src.views import views

data_df_f = read_xlsx(PATH_XLSX)
print(views("2021-12-12 12:12:21"))
print(pd_search(data_df_f, "жк"))
print(spending_by_category(data_df_f, "Переводы", "2021-12-12 12:12:21"))