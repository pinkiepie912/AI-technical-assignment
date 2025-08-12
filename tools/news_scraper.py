import csv
from typing import List, Tuple

import requests
import trafilatura
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape_news(url: str) -> str:
    try:
        html = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            allow_redirects=True,
        ).text
    except Exception:
        return ""

    text = trafilatura.extract(html, url=url, favor_recall=True) or ""
    return text


def get_selenium_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def scrape_news_fallback(url: str, driver: webdriver.Chrome) -> str:
    try:
        driver.get(url)
        driver.implicitly_wait(3)

        html = driver.page_source
        text = trafilatura.extract(html, url=url, favor_recall=True) or ""
        if not text:
            return ""
        return text

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


def get_data(file_path: str) -> Tuple[list, list]:
    driver = get_selenium_driver()

    parsed_data = []
    fail_data = []

    data = []
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    total = len(data)
    for idx, row in enumerate(data, 1):
        print(f"{idx}/{total} - {row['original_link']}")

        content = scrape_news(row["original_link"])
        if content:
            row["content"] = content
            parsed_data.append(row)
        else:
            content = scrape_news_fallback(row["original_link"], driver)
            if content:
                row["content"] = content
                parsed_data.append(row)
            else:
                fail_data.append(row)

    parsed_data.append(row)
    return parsed_data, fail_data


def save_to_csv(data: List[dict], file_path: str) -> None:
    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=parsed_data[0].keys(), quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    parsed_data, fail_data = get_data("example_datas/company_news.csv")
    save_to_csv(parsed_data, "example_datas/company_news_with_contents.csv")
    save_to_csv(fail_data, "example_datas/company_news_with_contents_fail.csv")
