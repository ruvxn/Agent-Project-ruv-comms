import datetime
import os
import uuid
from dotenv import load_dotenv
import mysql.connector

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
            print(f"{function.__name__} successful")
            return result
        except Exception as e:
            db_connection.rollback()
            print(f"{function.__name__} failed. {e}")
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
                user_id INT,
                review_title TEXT,
                review_body TEXT,
                create_time_stamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)


@db_wrapper
def insert_into_raw_review_table(cursor, db_connection, review_title: str, review_body: str):
    id = str(uuid.uuid4())
    create_time_stamp = datetime.datetime.now()

    insert_query = f"""INSERT INTO `{MYSQL_RAW_REVIEW_TABLE}`
        (id, review_title, review_body, create_time_stamp)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(insert_query, (id, review_title,
                   review_body, create_time_stamp))

# TODO - get_user_table()

# TODO - get_product_table()
