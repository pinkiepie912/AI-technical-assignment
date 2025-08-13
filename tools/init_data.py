import asyncio
import csv
import json
import logging
import os
from datetime import datetime
from glob import glob
from typing import List

import psycopg2
from dotenv import find_dotenv, load_dotenv
from llama_index.core.node_parser import SentenceSplitter
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from tools.embedding import create_embeddings
from tools.insert_company_data import save_companies
from tools.scrap_news import scrap_news

load_dotenv(find_dotenv(), override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# 데이터베이스 연결 정보
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": os.getenv("POSTGRES_USER", "searchright"),
    "password": os.getenv("POSTGRES_PASSWORD", "searchright"),
    "database": os.getenv("POSTGRES_DB", "searchright"),
}


def connect_to_db():
    """데이터베이스에 연결"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info(f"성공적으로 {DB_CONFIG['database']} 데이터베이스에 연결했습니다.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"데이터베이스 연결 오류: {e}")
        raise


def chunk_text(text: str, chunk_size=320, chunk_overlap=80) -> List[str]:
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)


def get_news_with_vector() -> List[dict]:
    news: List[dict] = []
    if os.path.exists("example_datas/company_news_with_vector.csv"):
        with open(
            "example_datas/company_news_with_vector.csv", "r", encoding="utf-8-sig"
        ) as f:
            reader = csv.DictReader(f)
            for row in reader:
                news.append(row)
    else:
        parsed_news = scrap_news()
        for row in parsed_news:
            chunks = chunk_text(row["content"].replace("\n", " "))
            embeddings = create_embeddings(chunks)

            for i, chunk in enumerate(chunks):
                news.append(
                    {
                        **row,
                        "content": chunk,
                        "vectors": json.dumps(embeddings[i]),
                    }
                )

    with open(
        "example_datas/company_news_with_vector.csv",
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=news[0].keys())
        writer.writeheader()
        writer.writerows(news)

    return news


def get_company_map(conn):
    """회사 이름을 ID로 매핑하는 딕셔너리 생성"""
    try:
        company_map = {}
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM companies")
            for company_id, company_name in cursor.fetchall():
                company_map[company_name] = company_id

        logger.info(f"{len(company_map)}개의 회사 매핑을 로드했습니다.")
        return company_map
    except psycopg2.Error as e:
        logger.error(f"회사 매핑 로드 오류: {e}")
        return {}


def insert_news_data(conn, news_data, company_map):
    """뉴스 데이터를 데이터베이스에 삽입"""
    try:
        inserted_count = 0
        skipped_count = 0
        missing_company_count = 0

        with conn.cursor() as cursor:
            for news in news_data:
                company_name = news["name"]

                # 회사 ID 찾기
                if company_name not in company_map:
                    missing_company_count += 1
                    logger.warning(
                        f"회사 '{company_name}'가 데이터베이스에 존재하지 않습니다. 해당 뉴스를 건너뜁니다."
                    )
                    continue

                year = int(news["year"])
                month = int(news["month"])
                day = int(news["day"])
                news["news_date"] = datetime(year, month, day).strftime("%Y-%m-%d")

                company_id = company_map[company_name]

                # 중복 확인
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM news_chunks 
                    WHERE company_id = %s AND title = %s AND vector = %s AND created_at = %s
                    """,
                    (company_id, news["title"], news["vectors"], news["news_date"]),
                )
                count = cursor.fetchone()[0]

                if count > 0:
                    skipped_count += 1
                    continue

                # 데이터 삽입
                cursor.execute(
                    """
                    INSERT INTO news_chunks (company_id, title, contents, vector, link, created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        company_id,
                        news["title"],
                        news["content"],
                        news["vectors"],
                        news["original_link"],
                        news["news_date"],
                    ),
                )
                inserted_count += 1

                # 로깅 (100개마다)
                if inserted_count % 100 == 0:
                    logger.info(f"{inserted_count}개의 뉴스 데이터가 삽입되었습니다.")

        logger.info(f"총 {inserted_count}개의 뉴스 데이터가 삽입되었습니다.")
        logger.info(f"중복으로 {skipped_count}개의 데이터가 건너뛰어졌습니다.")
        logger.info(
            f"존재하지 않는 회사로 인해 {missing_company_count}개의 데이터가 건너뛰어졌습니다."
        )

        return inserted_count
    except psycopg2.Error as e:
        logger.error(f"데이터 삽입 오류: {e}")
        conn.rollback()
        return 0


def merge_news_data():
    file_list = sorted(glob("./example_datas/vectors/news_vector_*.csv"))

    merged_data = []
    for file in file_list:
        with open(file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                merged_data.append(row)
    if not merged_data:
        return

    with open(
        "./example_datas/company_news_with_vector.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=merged_data[0].keys())
        writer.writeheader()
        writer.writerows(merged_data)


async def main():
    """메인 함수"""

    # Insert company data api call
    await save_companies()
    merge_news_data()

    try:
        # 데이터베이스 연결
        conn = connect_to_db()

        # 회사 매핑 가져오기
        company_map = get_company_map(conn)
        if not company_map:
            logger.error("회사 정보를 가져오지 못했습니다. 프로세스를 중단합니다.")
            return

        # 뉴스 데이터 로드
        news_data = get_news_with_vector()
        if not news_data:
            logger.error("뉴스 데이터를 로드하지 못했습니다. 프로세스를 중단합니다.")
            return

        # 데이터 삽입
        insert_news_data(conn, news_data, company_map)

    except Exception as e:
        logger.error(f"예상치 못한 오류가 발생했습니다: {e}")
        raise e
    finally:
        if "conn" in locals() and conn:
            conn.close()
            logger.info("데이터베이스 연결이 닫혔습니다.")


if __name__ == "__main__":
    asyncio.run(main())
