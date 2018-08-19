import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


def get_html(url):
    req = requests.get(url, headers={"User-Agent": UserAgent().chrome, "Referer": url,
                                     "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                                     "Connection": "keep-alive", "Origin": "https://realty.yandex.ru",
                                     "DNT": "1"})
    return req.text.encode(req.encoding)


def get_title(soup):
    try:
        title = soup.find("div", class_="card__info").text.strip()
    except:
        title = "Не указано"
    return title


def get_address(soup):
    try:
        address = soup.find("div", class_="address__text").text.strip()
    except Exception as e:
        print(str(e) + " address")
        address = "Не указано"
    return address


def get_block_type(soup):
    try:
        specs_headers = soup.find_all("th", class_="specs__header-cell")
        block_type = "Вторичка"
        for spec in specs_headers:
            spec = spec.find("div").text.strip()
            if spec is not None:
                if "ЖК" in spec:
                    block_type = "Новостройка"
    except Exception as e:
        print(e, " block_type")
        block_type = "Не указано"
    return block_type


def get_price(soup):
    try:
        price = soup.find("h2", class_="card__name").text.strip()
    except Exception as e:
        print(str(e) + " price")
        price = "Не указано"
    return price


def get_selling_type(soup):
    try:
        selling_type = soup.find("div", class_="card__terms").text.strip()
    except Exception as e:
        print(str(e) + " selling_type")
        selling_type = "Не указано"
    return selling_type


def get_seller_type(soup):
    try:
        seller_type = soup.find("div", class_="card__author-category").text.strip()
    except Exception as e:
        print(str(e) + " seller_type")
        seller_type = "Не указано"
    return seller_type


def get_photos(soup):
    try:
        images = []
        images_list = soup.find_all("div", class_="card__image-wrapper")
        for image in images_list:
            link = image.find("div", class_="image").get("src")
            images.append(link)
        images = "\n".join(images)
    except Exception as e:
        print(str(e) + " images")
        images = "Не указано"
    return images


def get_description(soup):
    try:
        description = soup.find("div", class_="shorter__full").text.strip()
    except Exception as e:
        print(str(e) + " description")
        description = "Не указано"
    return description


def get_date(soup):
    try:
        date = soup.find("div", class_="card__date").text.strip()
        if "назад" in date:
            time_passed = int(date.split()[0])
            if "минут" in date:
                date = str(datetime.datetime.today() - datetime.timedelta(minutes=time_passed)).split()[0]
            elif "часов" in date:
                date = str(datetime.datetime.today() - datetime.timedelta(hours=time_passed))
    except Exception as e:
        print(str(e) + " date")
        date = "Не указано"
    return date


def get_seller_phone(soup):
    phone = "Не указано"
    try:
        phone = soup.find("div", class_="phone__wrapper")
    except Exception as e:
        print(str(e) + " phone")
    return phone


def get_apartment_params(soup):
    rooms_number, total_floors, total_area, material, year = ["Не указано"] * 5
    try:
        params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-name")]
        values = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-value")]
        for i in range(len(params)):
            if "Количество комнат" in params[i]:
                rooms_number = values[i]
            elif "Год постройки" in params[i]:
                year = values[i]
            elif "Этаж" in params[i]:
                total_floors = values[i]
            elif "Общая площадь" in params[i]:
                total_area = values[i]
            elif "Тип здания" in params[i]:
                material = values[i]

        if year == "Не указано":
            new_block_params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__site-subtitle-item")]
            for param in new_block_params:
                if "строится" in param:
                    year = param
    except Exception as e:
        print(str(e) + " apartment params")
    return rooms_number, total_floors, total_area, material, year


def get_cottage_params(soup):
    total_area, land_area, comforts, year = ["Не указано"] * 4
    try:
        params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-name")]
        values = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-value")]
        for i in range(len(params)):
            if "Год постройки" in params[i]:
                year = values[i]
            elif "Общая площадь" in params[i]:
                total_area = values[i]
            elif "Площадь участка" in params[i]:
                land_area = values[i]
            elif any(x in params[i].lower() for x in ["отапливаемый", "отопление", "водопровод", "канализация",
                                                      "электроснабжение", "свет", "газ", "вода", "интернет",
                                                      "телефон", "душ"]):
                if comforts == "Не указано":
                    comforts = params[i].strip()
                else:
                    comforts += "; " + params[i].strip()

        if year == "Не указано":
            new_block_params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__site-subtitle-item")]
            for param in new_block_params:
                if "строится" in param:
                    year = param
    except Exception as e:
        print(str(e) + " cottage params")
    return total_area, land_area, comforts, year


def get_commercial_params(soup):
    entrance, furniture, additions = ["Не указано"] * 3
    try:
        params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-name")]
        values = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-value")]
        for i in range(len(params)):
            if "Мебель" in params[i]:
                furniture = values[i]
            elif "Вход" in params[i]:
                entrance = values[i]
            elif any(x in params[i].lower() for x in ["кондиционер", "интернет", "пожарная сигнализация",
                                                      "вентиляция", "охраняемая парковка", "сигнализация", "лифт"])\
                    and values[i].strip() == "да":
                if additions == "Не указано":
                    additions = params[i].strip()
                else:
                    additions += "; " + params[i].strip()
    except Exception as e:
        print(str(e) + " cottage params")
    return entrance, furniture, additions


def get_apartment_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    #title = get_title(soup)
    address = get_address(soup)
    block_type = get_block_type(soup)
    price = get_price(soup)
    #rooms_number, total_floors, total_area, material, year = get_apartment_params(soup)
    selling_type = get_selling_type(soup)
    seller_type = get_seller_type(soup)
    images = get_photos(soup)
    description = get_description(soup)
    #phone = get_seller_phone(soup)

    return [address, block_type, price, selling_type, seller_type, images, description, phone]
    #return [address, block_type, rooms_number, price, total_area, total_floors, material,
     #       year, selling_type, images, description, seller_type, phone]


def get_cottage_data(html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    address = get_address(soup)
    cottage_type = title
    price = get_price(soup)
    total_area, land_area, comforts, year = get_cottage_params(soup)
    selling_type = get_selling_type(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(soup)

    return [address, cottage_type, price, total_area, land_area, comforts, year, selling_type,
            images, description, phone]


def get_commercial_data(html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    address = get_address(soup)
    object_type = title.split(",")[0]
    entrance, furniture, additions = get_commercial_params(soup)
    phone = get_seller_phone(soup)

    return [address, object_type, furniture, entrance, additions, phone]


def crawl_page(html, category, sell_type):
    soup = BeautifulSoup(html, "lxml")

    offers = [x.find("a", class_="link") for x in soup.find_all("div", class_="serp-item__media-wrapper")]
    for offer in offers:
        try:
            # TODO: проверить еще на дубликат
            url = "https://m.realty.yandex.ru" + offer.get("href")

            data = []
            if category == "apartments":
                data = get_apartment_data(get_html(url), url)
            elif category == "commercials":
                data = get_commercial_data(get_html(url))
            elif category == "cottages":
                data = get_cottage_data(get_html(url))

            date = get_date(soup)
            data.append(date)
            data.insert(1, sell_type)
            print(*data, sep="\n")
            print("--------------------------------------")

        except Exception as e:
            print(e)
            print("Ошибка в crawl_page")

        time.sleep(random.uniform(15, 20))


def parse(category_url, category_name, sell_type):

    # for page in range(1, total_pages + 1):
    #     url_gen = base_url + page_part + str(page) + parameters_part
    #     crawl_page(get_html(url_gen))

    for page in range(2):
        url_gen = category_url[:category_url.rfind("=") + 1] + str(page)
        crawl_page(get_html(url_gen), category_name, sell_type)


def main():
    url_apartments_sell = "https://m.realty.yandex.ru/saratovskaya_oblast/kupit/kvartira/?sort=DATE_DESC&page=0"
    parse(url_apartments_sell, "apartments", "Продажа")

    # url_apartments_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/kvartira/?sort=DATE_DESC&page=0"
    # parse(url_apartments_rent, "apartments", "Аренда")
    #
    # url_cottages_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/dom/?sort=DATE_DESC&page=0"
    # parse(url_cottages_sell, "cottages", "Продажа")
    #
    # url_cottages_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/dom/?sort=DATE_DESC&page=0"
    # parse(url_cottages_rent, "cottages", "Аренда")
    #
    # url_commercials_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/kommercheskaya-nedvizhimost/?sort=DATE_DESC&page=0"
    # parse(url_commercials_sell, "commercials", "Продажа")
    #
    # url_commercials_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/kommercheskaya-nedvizhimost/?sort=DATE_DESC&page=0"
    # parse(url_commercials_rent, "commercials", "Аренда")


if __name__ == "__main__":
    break_point = "вчера"  # на каких записях останавливаться

    # defining chrome options for selenium
    # options = Options()
    # options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    # options.add_argument('--disable-gpu')
    # options.add_argument('--headless')
    #
    chrome_driver = os.getcwd() + "\\chromedriver.exe"

    main()
