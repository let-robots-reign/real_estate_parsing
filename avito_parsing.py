import requests
from bs4 import BeautifulSoup
import csv


def get_html(url):
    return requests.get(url).text


def get_total_pages(html):
    soup = BeautifulSoup(html, "lxml")
    pages = soup.find("div", class_="pagination-pages clearfix").find_all("a", class_="pagination-page")[-1].get("href")
    total_pages = int(pages.split("=")[1].split("&")[0])
    return total_pages


def crawl_page(html):
    soup = BeautifulSoup(html, "lxml")
    offers = soup.find("div", class_="catalog-list").find_all("div", class_="item_table")
    for offer in offers:
        try:
            url = "https://avito.ru" + offer.find("div", class_="description").find("h3").find("a").get("href")
            get_page_data(get_html(url))
        except:
            url = "Не указано"


def get_page_data(html):
    soup = BeautifulSoup(html, "lxml")
    try:
        title = soup.find("span", class_="title-info-title-text").text.strip()
    except:
        title = "Не указано"

    # try:
    #     cost = soup.find("span", class_="js-item-price").text.strip() + " рублей"
    #     try:
    #         period = soup.find("span", class_="price-value-string js-price-value-string").find_all("span")[-1].text.strip()
    #         if_period = True
    #     except:
    #         if_period = False
    #
    #     if if_period:
    #         price = "Аренда: " + cost + period
    #     else:
    #         price = "Продажа: " + cost
    # except:
    #     price = "Не указано"

    try:
        price = soup.find("span", class_="price-value-string js-price-value-string").text.strip()
        if price:
            print(price)
        else:
            price = soup.find("span", class_="js-item-price").text.strip() + " рублей"
            print(price)
    except:
        price = "Не указано"

    try:
        address = soup.find("span", itemprop="streetAddress").text.strip()
    except:
        address = "Не указано"

    print(address, title, price)


def main():
    url_apartments = "https://www.avito.ru/saratovskaya_oblast/kvartiry?p=1&s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/kvartiry?"
    page_part = "p="
    parameters_part = "&s=104&s_trg=3&bt=1"

    total_pages = get_total_pages(get_html(url_apartments))

    # for page in range(1, total_pages + 1):
    #     url_gen = base_url + page_part + str(page) + parameters_part
    #     crawl_page(get_html(url_gen))

    for page in range(1, 3):
        url_gen = base_url + page_part + str(page) + parameters_part
        crawl_page(get_html(url_gen))

    #print(total_pages)


if __name__ == "__main__":
    main()
