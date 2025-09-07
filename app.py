from Controller.utils import load_data_to_raw_review_table, chunking
from Controller.db_setup.mysql_setup import get_raw_review_data_by_id

result = get_raw_review_data_by_id("22287554-10b8-4d0b-8370-811078cfb110")

print(result.data["review_title"])
