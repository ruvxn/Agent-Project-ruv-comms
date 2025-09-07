from langchain.text_splitter import RecursiveCharacterTextSplitter

from Controller.db_setup.mysql_setup import *


def load_data_to_raw_review_table() -> None:
    """Load raw user comments from text file and insert into DB"""
    create_or_get_mysql_cursor()
    create_or_get_review_table()

    with open("./Model/data/small_test.txt", "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = line.replace("__label__2", "")
        line = line.replace("__label__1", "")
        if ":" in line:
            review_title, review_body = line.split(":", 1)
        else:
            review_title, review_body = "", line

        try:
            insert_into_raw_review_table(
                review_title.strip(), review_body.strip())
        except Exception as e:
            print(
                f"review_title: {review_title} and review_body {review_body} insert unsuccessfully. {e}")


def chunking(data: str) -> list[str]:
    """Data chuncking"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=50,
        chunk_overlap=10
    )
    chunks = splitter.split_text(data)
    print(f"Chunk size: {len(chunks)}")
    print(chunks[:3])
    return chunks
