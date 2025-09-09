from ast import List
from dataclasses import asdict
import os
import uuid
import mysql.connector
from dotenv import load_dotenv
from Model.DTO.JSONResponseDTO import JSONResponseDTO
from Model.DTO.RawReviewDTO import RawReviewDTO
from Model.DTO.ReviewSummaryDTO import ReviewSummaryDTO

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER_NAME = os.getenv("MYSQL_USER_NAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_RAW_REVIEW_TABLE = os.getenv("MYSQL_RAW_REVIEW_TABLE")


def create_or_get_mysql_cursor() -> tuple:

    mysql_connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER_NAME,
        password=MYSQL_PASSWORD
    )
    cursor = mysql_connection.cursor()

    cursor.execute(
        "SHOW DATABASES LIKE %s", (MYSQL_DATABASE,))

    result = cursor.fetchone()

    if not result:
        cursor.execute(f"CREATE DATABASE {MYSQL_DATABASE}")

    try:
        cursor.execute(f"use {MYSQL_DATABASE}")
        return cursor, mysql_connection
    except Exception as e:
        raise Exception("Fail to get cursor") from e


def db_wrapper(function):
    def wrapper(*args, **kwargs):
        (cursor, db_connection) = create_or_get_mysql_cursor()
        try:
            result = function(cursor, db_connection, *args, **kwargs)
            db_connection.commit()
            # print(f"{function.__name__} successful")
            return JSONResponseDTO(success=True, data=result, message=f"{function.__name__} successful")
        except Exception as e:
            db_connection.rollback()
            # print(f"{function.__name__} failed. {e}")
            return JSONResponseDTO(success=False, message=f"{function.__name__} failed.", error=str(e))
        finally:
            cursor.close()
            db_connection.close()
    return wrapper


@db_wrapper
def create_or_get_review_table(cursor, db_connection) -> None:

    cursor.execute(f"SHOW TABLES LIKE '{MYSQL_RAW_REVIEW_TABLE}'")

    result = cursor.fetchone()

    if not result:
        cursor.execute(f"""
            CREATE TABLE `{MYSQL_RAW_REVIEW_TABLE}` (
                id CHAR(36) NOT NULL PRIMARY KEY,
                user_id CHAR(36),
                purchase_id CHAR(36),
                review_title TEXT,
                review_body TEXT,
                create_time_stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                insert_time_stamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    return result


@db_wrapper
def insert_into_raw_review_table(cursor, db_connection, review_title: str, review_body: str):
    id = str(uuid.uuid4())

    insert_query = f"""INSERT INTO `{MYSQL_RAW_REVIEW_TABLE}`
        (id, user_id, purchase_id, review_title, review_body)
        VALUES (%s, %s, %s, %s,%s)
    """

    cursor.execute(insert_query, (id, None, None, review_title,
                   review_body))


@db_wrapper
def get_raw_review_data_by_id(cursor, db_connection, id: str) -> dict:

    cursor.execute(
        f"""SELECT id, user_id, purchase_id, review_title, review_body,
           create_time_stamp, insert_time_stamp FROM `{MYSQL_RAW_REVIEW_TABLE}` WHERE id = %s""", (id,))

    raw_review_data = cursor.fetchone()

    if not raw_review_data:
        return None

    raw_review_data_response = RawReviewDTO(
        id=raw_review_data[0],
        user_id=raw_review_data[1],
        purchase_id=raw_review_data[2],
        review_title=raw_review_data[3],
        review_body=raw_review_data[4],
        create_time_stamp=raw_review_data[5],
        insert_time_stamp=raw_review_data[6]
    )

    return asdict(raw_review_data_response)


@db_wrapper
def get_all_raw_review_data(cursor, db_connection) -> dict:
    cursor.execute(f"""SELECT * FROM `{MYSQL_RAW_REVIEW_TABLE}`""")
    raw_review_data = cursor.fetchall()

    if not raw_review_data:
        return None

    all_raw_review_data = []

    for entry in raw_review_data:
        all_raw_review_data.append(asdict(RawReviewDTO(id=entry[0],
                                                       user_id=entry[1],
                                                       purchase_id=entry[2],
                                                       review_title=entry[3],
                                                       review_body=entry[4],
                                                       create_time_stamp=entry[5],
                                                       insert_time_stamp=entry[6])))
    return all_raw_review_data


@db_wrapper
def get_clean_review_from_table(cursor, db_connection):
    all_raw_review_data = get_all_raw_review_data()

    review_list = []

    for entry in all_raw_review_data.data:
        review_list.append(asdict(ReviewSummaryDTO(
            review=f"review_title: {entry['review_title']}; review_body: {entry['review_body']}",
            review_id=entry['id']
        )))
    return review_list


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


# TODO - get_user_table()

# TODO - get_product_table()
