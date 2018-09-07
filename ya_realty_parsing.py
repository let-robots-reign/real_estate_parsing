# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import datetime
from selenium import webdriver
from xvfbwrapper import Xvfb
from selenium.webdriver.chrome.options import Options
from database import DataBase

# на каких записях останавливаться
with open("breakpoints/ya.txt", "r", encoding="utf8") as file:
    breakpoints = file.readlines()
    try:
        break_apartment_sell = tuple(breakpoints[0].strip().split("--"))
    except:
        break_apartment_sell = None
    try:
        break_apartment_rent = tuple(breakpoints[1].strip().split("--"))
    except:
        break_apartment_rent = None
    try:
        break_cottage_sell = tuple(breakpoints[2].strip().split("--"))
    except:
        break_cottage_sell = None
    try:
        break_cottage_rent = tuple(breakpoints[3].strip().split("--"))
    except:
        break_cottage_rent = None
    try:
        break_commercial_sell = tuple(breakpoints[4].strip().split("--"))
    except:
        break_commercial_sell = None
    try:
        break_commercial_rent = tuple(breakpoints[5].strip().split("--"))
    except:
        break_commercial_rent = None

# defining chrome options for selenium
options = Options()
options.add_argument("--no-sandbox")

db = DataBase()
visited_urls = []


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
        # separating data from the address string
        district, street = "Не указано", "Не указано"
        city = address.split(",")[0]
        block_number = address.split(",")[-1].strip()
        if "ул " in block_number.lower() or "ул." in block_number.lower() or "улица" in block_number.lower() \
                or " пер" in block_number.lower() or "проспект" in block_number.lower() or "проезд" in block_number.lower():
            street = block_number
            block_number = "Не указано"

        for param in address.split(",")[1:-1]:
            if "ул " in param.lower() or "ул." in param.lower() or "улица" in param.lower() \
                    or " пер" in param.lower() or "проспект" in param.lower() or "проезд" in param.lower():
                street = param.strip()
            elif "район" in param.lower() or "р-н" in param.lower():
                district = param.strip()

        if street.split()[-1].strip().isdigit():
            block_number = street.split()[-1].strip()
            street = " ".join(street.split()[:-1]).strip()

        return city, district, street, block_number

    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_address\n")
    return ["Не указано"] * 4


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


def get_seller_name(soup):
    try:
        name = soup.find("div", class_="offer-card__author-name").text.strip()
    except:
        name = "Не указано"
    return name


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


def get_date(soup, which_page):
    # 0 - page with offers, 1 - offer itself
    try:
        if which_page == 0:
            date = soup.find("div", class_="OffersSerpItem__publish-date").text.strip()
        else:
            date = soup.find("div", class_="offer-card__lot-date").text.strip()
        if "назад" in date:
            time_passed = int(date.split()[0])
            if "минут" in date:
                date = str(datetime.datetime.today() - datetime.timedelta(minutes=time_passed)).split()[0]
            elif "часов" in date or "часа" in date or "час" in date:
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
        vdisplay = Xvfb()
        vdisplay.start()
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
        driver.get(url)

        button = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[2]/div[2]/div/div[1]/div[3]/div[1]/span/button")
        button.click()
        time.sleep(2)
        phone = driver.find_element_by_xpath('//div[@class="helpful-info__contact-phones-string"]').text
        driver.quit()
        vdisplay.stop()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_seller_phone\n")
    return phone


def get_apartment_params(soup):
    rooms_number, floor, total_floors, total_area, material, year, kitchen_area, living_area = ["Не указано"] * 8
    try:
        params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-name")]
        values = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-value")]
        for i in range(len(params)):
            if "Количество комнат" in params[i]:
                rooms_number = values[i]
            elif "Год постройки" in params[i]:
                year = values[i]
            elif "Этаж" in params[i]:
                floor, total_floors = values[i].split(" из ")
            elif "Общая площадь" in params[i]:
                total_area = values[i]
            elif "Кухня" in params[i]:
                total_area = values[i]
            elif "Жилая" in params[i]:
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
    return rooms_number, floor, total_floors, total_area, material, year, kitchen_area, living_area


def get_cottage_params(soup):
    total_area, land_area, comforts, year, material, total_floors, land_status = ["Не указано"] * 7
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
            elif "Тип дома" in params[i]:
                material = values[i]
            elif "Количество этажей" in params[i]:
                total_floors = values[i]
            elif "Тип участка" in params[i]:
                land_status = values[i]
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
    return total_area, land_area, comforts, year, material, total_floors, land_status


def get_commercial_params(soup):
    entrance, furniture, additions, area = ["Не указано"] * 4
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

            new_params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__main-feature-note")]
            values = [x.text.strip() for x in soup.find_all("div", class_="offer-card__main-feature-title")]
            for j in range(len(new_params)):
                if "общая" in new_params[j]:
                    area = values[j]
                    break
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " ya get_commercial_params\n")
    return entrance, furniture, additions, area


def get_apartment_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    #title = get_title(soup)
    city, district, street, block_number = get_address(soup)
    block_type = get_block_type(soup)
    price = get_price(soup)
    rooms_number, floor, total_floors, total_area, material, year, kitchen_area, living_area = get_apartment_params(soup)
    selling_detail = get_selling_type(soup)
    if "продажа" in selling_detail.lower() or "ипотека" in selling_detail.lower():
        rent_info = "Не аренда"
    else:
        rent_info = selling_detail
        selling_detail = "Не указано"

    #seller_type = get_seller_type(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(url)
    date = get_date(soup, 1)

    return [city, district, street, block_number, rent_info, price, block_type,
            rooms_number, total_area, total_floors, material, selling_detail, images,
            description, date, phone, kitchen_area, living_area, floor]


def get_cottage_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    city, district, street, block_number = get_address(soup)
    cottage_type = title.split(",")[0]
    price = get_price(soup)
    total_area, land_area, comforts, year, material, total_floors, land_status = get_cottage_params(soup)
    selling_detail = get_selling_type(soup)
    if "продажа" in selling_detail.lower() or "ипотека" in selling_detail.lower():
        rent_info = "Не аренда"
    else:
        rent_info = selling_detail
        selling_detail = "Не указано"

    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(url)
    date = get_date(soup, 1)
    seller_name = get_seller_name(soup)

    return [city, district, street, block_number, rent_info, price, cottage_type,
            total_area, comforts, selling_detail, images, description, date, phone, material,
            total_floors, land_area, land_status, seller_name]


def get_commercial_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    city, district, street, block_number = get_address(soup)
    price = get_price(soup)
    object_type = title.split(",")[0]
    entrance, furniture, additions, area = get_commercial_params(soup)
    phone = get_seller_phone(url)
    images = get_photos(soup)
    description = get_description(soup)
    seller_name = get_seller_name(soup)
    date = get_date(soup, 1)
    office_class = "Не указано"

    return [city, district, street, block_number, price, object_type, office_class,
            furniture, entrance, area, date, phone, images, description, seller_name]


def crawl_page(first_offer, html, category, sell_type):
    global visited_urls, db
    soup = BeautifulSoup(html, "lxml")
    # так как пагинация динамическая и мы не можем получить число страниц, проверяем, есть ли на странице объявления
    try:
        offers = soup.find("ol", class_="OffersSerp__list").find_all("li", class_="OffersSerp__list-item_type_offer")
    except:
        offers = []
    if offers is None or not offers:
        print("Парсинг завершен ya")
        return True
    k = 0
    for offer in offers:
        try:
            date = get_date(soup, 0)
            if date == "too old":
                print("Парсинг завершен ya")
                return True

            url = "https://realty.yandex.ru" + offer.find("a", class_="OffersSerpItem__link").get("href")
            if url in visited_urls:
                print("ya not unique")
                time.sleep(random.uniform(10, 15))
                continue
            else:
                visited_urls.append(url)
            #print(url)

            data = []
            if category == "Квартиры":
                data = get_apartment_data(get_html(url), url)
                # записываем ключевую информацию, чтобы потом найти дубликаты
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s--%s\n" % (data[2], data[3], data[4], data[8], data[-1], url))
            elif category == "Дома":
                data = get_cottage_data(get_html(url), url)
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s\n" % (data[2], data[3], data[7], data[8], url))
            elif category == "Коммерческая_недвижимость":
                data = get_commercial_data(get_html(url), url)
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s\n" % (data[2], data[3], data[6], data[10], url))

            if first_offer:
                # сохраняем самую первую запись как точку выхода
                modifier = "w" if (category == "Квартиры" and sell_type == "Продажа") else "a"
                with open("breakpoints/ya.txt", modifier, encoding="utf8") as file:
                    file.write("%s--%s\n" % (data[2], data[5]))
                first_offer = False

            key_info = (data[2], data[5])

            if any(x == key_info for x in [break_apartment_sell, break_apartment_rent, break_cottage_sell,
                                           break_cottage_rent, break_commercial_sell, break_commercial_rent]):
                print("Парсинг завершен ya")
                return True

            data.insert(4, sell_type)
            #print(*data, sep="\n")
            #print("--------------------------------------")
            if data[0] != "Не указано":
                try:
                    db.insert_data(category, data)
                except:
                    db.close()
                    db = DataBase()
                    db.insert_data(category, data)
            print("parsed page ya")


        except Exception as e:
            with open("logs.txt", "a", encoding="utf8") as file:
                file.write(str(e) + " ya crawl_page\n")
            #print(e)
            #print("Ошибка в crawl_page")

        k += 1
        if k % 5 == 0:  # после каждого пятого запроса, делаем паузу побольше
            time.sleep(100)
        else:
            time.sleep(random.uniform(10, 15))


def parse(category_url, category_name, sell_type):
    completed = False
    page = 0
    while not completed:
        url_gen = category_url[:category_url.rfind("=") + 1] + str(page)
        if page == 0:
            completed = crawl_page(True, get_html(url_gen), category_name, sell_type)
        else:
            completed = crawl_page(False, get_html(url_gen), category_name, sell_type)
        page += 1


def main():
    global visited_urls
    url_apartments_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/kvartira/?sort=DATE_DESC&page=0"
    parse(url_apartments_sell, "Квартиры", "Продажа")

    visited_urls = []
    url_apartments_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/kvartira/?sort=DATE_DESC&page=0"
    parse(url_apartments_rent, "Квартиры", "Аренда")

    visited_urls = []
    url_cottages_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/dom/?sort=DATE_DESC&page=0"
    parse(url_cottages_sell, "Дома", "Продажа")

    visited_urls = []
    url_cottages_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/dom/?sort=DATE_DESC&page=0"
    parse(url_cottages_rent, "Дома", "Аренда")

    visited_urls = []
    url_commercials_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/kommercheskaya-nedvizhimost/?sort=DATE_DESC&page=0"
    parse(url_commercials_sell, "Коммерческая_недвижимость", "Продажа")

    visited_urls = []
    url_commercials_rent = "https://realty.yandex.ru/saratovskaya_oblast/snyat/kommercheskaya-nedvizhimost/?sort=DATE_DESC&page=0"
    parse(url_commercials_rent, "Коммерческая_недвижимость", "Аренда")


if __name__ == "__main__":
    main()
    db.close()
