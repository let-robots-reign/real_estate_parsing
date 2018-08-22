import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


def transform_date(date):
    """
    Преобразуем дату, чтобы сравнить datetime-объекты
    """
    day, month, year = date.split()
    months = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12
    }

    date = datetime.datetime(int(year), months[month], int(day))
    return date


def get_html(url):
    req = requests.get(url, headers={"User-Agent": UserAgent().chrome, "Referer": url,
                                     "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                                     "Connection": "keep-alive", "Origin": "https://realty.yandex.ru",
                                     "DNT": "1"})
    return req.text.encode(req.encoding)


def get_title(soup):
    try:
        title = soup.find("h1", class_="offer-card__header-text").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_title\n")
        title = "Не указано"
    return title


def get_address(soup):
    try:
        address = soup.find("h2", class_="offer-card__address ellipsis").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_address\n")
        address = "Не указано"
    return address


def get_block_type(soup):
    try:
        block_type = soup.find("div", class_="offer-card__building-type")
        if block_type is None:
            block_type = "Вторичка"
        else:
            block_type = block_type.text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_block_type\n")
        block_type = "Не указано"
    return block_type


def get_price(soup):
    try:
        price = soup.find("h3", class_="offer-price offer-card__price offer-card__price").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_price\n")
        price = "Не указано"
    return price


def get_selling_type(soup):
    try:
        selling_type = soup.find("div", class_="offer-card__terms").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_selling_type\n")
        selling_type = "Не указано"
    return selling_type


def get_seller_type(soup):
    try:
        seller_type = soup.find("div", class_="offer-card__author-note").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_seller_type\n")
        seller_type = "Не указано"
    return seller_type


def get_photos(soup):
    try:
        images = []
        images_list = soup.find("div", class_="offer-card__photos-wrapper").find_all("a")
        for image in images_list:
            link = "https://realty.yandex.ru" + image.get("href")
            images.append(link)
        images = "\n".join(images)
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_photos\n")
        images = "Не указано"
    return images


def get_description(soup):
    try:
        description = soup.find("div", class_="offer-card__desc-text").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_description\n")
        description = "Не указано"
    return description


def get_date(soup):
    try:
        date = soup.find("div", class_="OffersSerpItem__publish-date").text.strip()
        if "назад" in date:
            time_passed = int(date.split()[0])
            if "минут" in date:
                date = str(datetime.datetime.today() - datetime.timedelta(minutes=time_passed)).split()[0]
            elif "часов" in date or "часа" in date:
                date = str(datetime.datetime.today() - datetime.timedelta(hours=time_passed)).split()[0]
            elif "сейчас" in date:
                date = str(datetime.datetime.today()).split()[0]
        elif date == "вчера":
            date = str(datetime.datetime.today() - datetime.timedelta(days=1)).split()[0]
        elif len(date.split()) >= 3:
            transformed_date = transform_date(date)
            days_passed = str(datetime.datetime.today() - transformed_date).split()[0]
            if int(days_passed) > 1:
                date = "too old"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_date\n")
        date = "Не указано"
    return date


def get_seller_phone(url):
    phone = "Не указано"
    try:
        driver = webdriver.Chrome(executable_path=chrome_driver)
        driver.get(url)
        button = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/div[1]/div[3]/div[1]/span/button")
        button.click()
        time.sleep(3)
        phone = driver.find_element_by_xpath('//div[@class="helpful-info__contact-phones-string"]').text
        driver.quit()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_seller_phone\n")
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
                    break

        if year == "Не указано":
            new_params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__main-feature-note")]
            values = [x.text.strip() for x in soup.find_all("div", class_="offer-card__main-feature-title")]
            for i in range(len(new_params)):
                if "год постройки" in new_params[i]:
                    year = values[i]
                    break

    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_apartment_params\n")
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
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_cottage_params\n")
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
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_commercial_params\n")
    return entrance, furniture, additions


def get_apartment_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    #title = get_title(soup)
    address = get_address(soup)
    block_type = get_block_type(soup)
    price = get_price(soup)
    rooms_number, total_floors, total_area, material, year = get_apartment_params(soup)
    selling_type = get_selling_type(soup)
    seller_type = get_seller_type(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(url)

    return [address, price, block_type, rooms_number, total_area, total_floors, material,
            year, selling_type, images, description, seller_type, phone]


def get_cottage_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    address = get_address(soup)
    cottage_type = title.split(",")[0]
    price = get_price(soup)
    total_area, land_area, comforts, year = get_cottage_params(soup)
    selling_type = get_selling_type(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(url)

    return [address, price, cottage_type, total_area, land_area, comforts, year, selling_type,
            images, description, phone]


def get_commercial_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    address = get_address(soup)
    price = get_price(soup)
    object_type = title.split(",")[0]
    entrance, furniture, additions = get_commercial_params(soup)
    phone = get_seller_phone(url)

    return [address, price, object_type, furniture, entrance, additions, phone]


def crawl_page(first_offer, html, category, sell_type):
    soup = BeautifulSoup(html, "lxml")
    # так как пагинация динамическая и мы не можем получить число страниц, проверяем, есть ли на странице объявления
    offers = soup.find("ol", class_="OffersSerp__list").find_all("li", class_="OffersSerp__list-item_type_offer")
    if offers is None:
        return True
    k = 0
    for offer in offers:
        try:
            date = get_date(soup)
            if date == "too old":
                print("Парсинг завершен")
                return True

            url = "https://realty.yandex.ru" + offer.find("a", class_="OffersSerpItem__link").get("href")

            data = []
            if category == "apartments":
                data = get_apartment_data(get_html(url), url)
                # записываем ключевую информация, чтобы потом найти дубликаты
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s\n" % (data[0], data[3], data[4], url))
            elif category == "commercials":
                data = get_commercial_data(get_html(url), url)
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s\n" % (data[0], data[2], data[3], url))
            elif category == "cottages":
                data = get_cottage_data(get_html(url), url)
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s\n" % (data[0], data[2], url))

            if first_offer:
                # сохраняем самую первую запись как точку выхода
                modifier = "w" if (category == "apartments" and sell_type == "Продажа") else "a"
                with open("breakpoints/ya.txt", modifier, encoding="utf8") as file:
                    file.write("%s--%s\n" % (data[0], data[1]))
                first_offer = False

            key_info = (data[0], data[1])

            if any(x == key_info for x in [break_apartment_sell, break_apartment_rent, break_cottage_sell,
                                           break_cottage_rent, break_commercials_sell, break_commercial_rent]):
                print("Парсинг завершен")
                return True

            data.append(date)
            data.insert(1, sell_type)
            print(*data, sep="\n")
            print("--------------------------------------")

        except Exception as e:
            print(e)
            print("Ошибка в crawl_page")

        k += 1
        if k % 5 == 0:  # после каждого пятого запроса, делаем паузу побольше
            time.sleep(120)
        else:
            time.sleep(random.uniform(15, 20))


def parse(category_url, category_name, sell_type):
    completed = False
    while not completed:
        page = 1
        url_gen = category_url[:category_url.rfind("=") + 1] + str(page)
        if page == 1:
            completed = crawl_page(True, get_html(url_gen), category_name, sell_type)
        else:
            completed = crawl_page(False, get_html(url_gen), category_name, sell_type)
        page += 1


def main():
    url_apartments_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/kvartira/?sort=DATE_DESC&page=0"
    parse(url_apartments_sell, "apartments", "Продажа")

    url_apartments_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/kvartira/?sort=DATE_DESC&page=0"
    parse(url_apartments_rent, "apartments", "Аренда")

    url_cottages_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/dom/?sort=DATE_DESC&page=0"
    parse(url_cottages_sell, "cottages", "Продажа")

    url_cottages_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/dom/?sort=DATE_DESC&page=0"
    parse(url_cottages_rent, "cottages", "Аренда")

    url_commercials_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/kommercheskaya-nedvizhimost/?sort=DATE_DESC&page=0"
    parse(url_commercials_sell, "commercials", "Продажа")

    url_commercials_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/kommercheskaya-nedvizhimost/?sort=DATE_DESC&page=0"
    parse(url_commercials_rent, "commercials", "Аренда")


if __name__ == "__main__":
    # на каких записях останавливаться
    with open("breakpoints/ya.txt", "r", encoding="utf8") as file:
        break_apartment_sell, break_apartment_rent, break_cottage_sell, break_cottage_rent, break_commercials_sell, break_commercial_rent = [tuple(x.strip().split("--"))
                                                                        for x in file.readlines()]

    # defining chrome options for selenium
    # options = Options()
    # options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    # options.add_argument('--disable-gpu')
    # options.add_argument('--headless')
    #
    chrome_driver = os.getcwd() + "\\chromedriver.exe"

    main()
