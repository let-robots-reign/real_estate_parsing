# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import datetime
import base64
from database import DataBase


# на каких записях останавливаться
with open("breakpoints/irr.txt", "r", encoding="utf8") as file:
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
        break_commercial_sell = tuple(breakpoints[2].strip().split("--"))
    except:
        break_commercial_sell = None
    try:
        break_commercial_rent = tuple(breakpoints[3].strip().split("--"))
    except:
        break_commercial_rent = None
    try:
        break_cottage_sell = tuple(breakpoints[4].strip().split("--"))
    except:
        break_cottage_sell = None
    try:
        break_cottage_rent = tuple(breakpoints[5].strip().split("--"))
    except:
        break_cottage_rent = None

# получаем вчерашнюю дату
today = datetime.datetime.today()
yesterday = str(today - datetime.timedelta(days=2)).split()[0].split("-")
if yesterday[1][0] == "0":
    yesterday[1] = yesterday[1][1:]
if yesterday[2][0] == "0":
    yesterday[2] = yesterday[2][1:]
months = {
    "1": "января",
    "2": "февраля",
    "3": "марта",
    "4": "апреля",
    "5": "мая",
    "6": "июня",
    "7": "июля",
    "8": "августа",
    "9": "сентября",
    "10": "октября",
    "11": "ноября",
    "12": "декабря"
}
date_break_point = yesterday[2] + " " + months[yesterday[1]]

db = DataBase()
visited_urls = []


def get_html(url):
    req = requests.get(url, headers={"User-Agent": UserAgent().chrome})
    return req.text.encode(req.encoding)


def get_total_pages(html):
    soup = BeautifulSoup(html, "lxml")
    total_pages = soup.find("div", class_="pagination__pages")
    if total_pages is not None:
        total_pages = total_pages.find_all("a", class_="pagination__pagesLink")[-1].text.strip()
    else:
        total_pages = 1
    return int(total_pages)


def get_title(soup):
    try:
        title = soup.find("h1", class_="productPage__title").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_title\n")
        title = "Не указано"
    return title


def get_address(soup):
    try:
        address = soup.find("div", class_="productPage__infoTextBold js-scrollToMap").text.strip()
        city = address.split(",")[0]
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_address\n")
        city = "Не указано"
    return city


def get_material(soup):
    try:
        material = "Не указано"
        building_params = soup.find_all("div", class_="productPage__infoColumnBlock js-columnBlock")[-1].find_all("li", class_="productPage__infoColumnBlockText")
        for i in range(len(building_params)):
            info = building_params[i].text.strip()
            if "Материал стен" in info:
                material = info.split(":")[1].strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_material\n")
        material = "Не указано"
    return material


def get_price(soup):
    try:
        price = " ".join(soup.find("div", class_="productPage__price").text.strip().split("\xa0"))
        fee = soup.find("div", class_="productPage__fee")
        if fee is not None:
            price += " (" + fee.text.strip() + ")"

        if "в месяц" in price:
            rent_info = "длительный срок"
        elif "за сутки" in price:
            rent_info = "посуточно"
        else:
            rent_info = "Не аренда"

    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_price\n")
        price, rent_info = "Не указано", "Не указано"
    return price, rent_info


def get_block_type(soup):
    block_type = "Вторичка"
    try:
        seller_site = soup.find("a", class_="js-sellerSiteLink")
        if seller_site is not None:
            block_type = "Новостройка"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_block_type\n")
    return block_type


def get_seller_info(soup):
    try:
        company_name = soup.find("div", class_="productPage__infoTextBold productPage__infoTextBold_inline").find("a")
        if company_name is not None:
            seller_type = "Компания"
            seller_name = company_name.text.strip()
        else:
            seller_type = "Частное лицо"
            seller_name = soup.find("div", class_="productPage__infoTextBold productPage__infoTextBold_inline").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_seller_info\n")
        seller_name, seller_type = "Не указано", "Не указано"
    return seller_type, seller_name


def get_photos(soup):
    try:
        images = []
        images_list = soup.find("div", class_="lineGallery js-lineProductGallery").find_all("meta")
        for image in images_list:
            link = image.get("content")
            images.append(link)
        images = "\n".join(images)
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_photos\n")
        images = "Не указано"
    return images


def get_description(soup):
    try:
        description = " ".join(soup.find("p", class_="productPage__descriptionText js-productPageDescription").text.strip().split())
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_description\n")
        description = "Не указано"
    return description


def get_date(soup):
    try:
        relative_date = soup.find("div", class_="productPage__createDate").find("span").text.strip()
        if "," in relative_date:
            if relative_date.split(",")[0] == "сегодня":
                date = str(datetime.datetime.today()).split()[0] + relative_date.split(",")[1]
            else:
                date = str(datetime.datetime.today() - datetime.timedelta(days=2)).split()[0] + relative_date.split(",")[1]
        else:
            date = relative_date
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_date\n")
        date = "Не указано"
    return date


def get_seller_phone(soup):
    try:
        ciphered_phone = soup.find("input", {"class": "js-backendVar", "name": "phoneBase64"}).get("value")
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_seller-phone\n")
        ciphered_phone = "Не указано"
    return base64.b64decode(ciphered_phone).decode("utf-8")


def get_apartment_params(soup):
    rooms_number, floor, total_floors, total_area, kitchen_area, living_area, furnish, district, street, block_number = ["Не указано"] * 10
    try:
        building_params = []
        divs = soup.find_all("div", class_="productPage__infoColumnBlock js-columnBlock")
        for i in range(len(divs)):
            building_params.extend(divs[i].find_all("li", class_="productPage__infoColumnBlockText"))

        for i in range(len(building_params)):
            info = building_params[i].text.strip()
            if "Этаж:" in info:
                floor = info.split(":")[1].strip()
            elif "Этажей в здании" in info:
                total_floors = info.split(":")[1].strip()
            elif "Комнат в квартире" in info:
                rooms_number = info.split(":")[1].strip()
            elif "Общая площадь" in info:
                total_area = info.split(":")[1].strip()
            elif "Жилая площадь" in info:
                living_area = info.split(":")[1].strip()
            elif "Площадь кухни" in info:
                kitchen_area = info.split(":")[1].strip()
            elif "Ремонт" in info:
                furnish = info.split(":")[1].strip()
                if furnish == "1":
                    # иногда выводит "1", хотя на странице не указан
                    furnish = "Не указано"
            elif "Улица" in info:
                street = info.split(":")[1].strip()
            elif "Район города" in info:
                district = info.split(":")[1].strip()
            elif "Дом" in info:
                block_number = info.split(":")[1].strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_apartment_params\n")
    return rooms_number, floor, total_floors, total_area, kitchen_area, living_area, furnish, district, street, block_number


def get_commercial_params(soup):
    building_type, parking, ceilings, area, entrance, district, street, block_number = ["Не указано"] * 8
    try:
        building_params = []
        divs = soup.find_all("div", class_="productPage__infoColumnBlock js-columnBlock")
        for i in range(len(divs)):
            building_params.extend(divs[i].find_all("li", class_="productPage__infoColumnBlockText"))

        for i in range(len(building_params)):
            info = building_params[i].text.strip()
            if "Тип здания" in info:
                building_type = info.split(":")[1].strip()
            elif "Общая площадь" in info:
                area = info.split(":")[1].strip()
            elif "Парковка" in info:
                parking = "Парковка есть"
            elif "Высота потолков" in info:
                ceilings = info.split(":")[1].strip()
            elif "Вход" in info:
                entrance = info.strip()
            elif "Улица" in info:
                street = info.split(":")[1].strip()
            elif "Район города" in info:
                district = info.split(":")[1].strip()
            elif "Дом" in info:
                block_number = info.split(":")[1].strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_commercial_params\n")
    return building_type, parking, ceilings, area, entrance, district, street, block_number


def get_cottage_params(soup):
    house_area, material, total_floors, land_area, status, comforts, district, street, block_number = ["Не указано"] * 9
    try:
        building_params = []
        divs = soup.find_all("div", class_="productPage__infoColumnBlock js-columnBlock")
        for i in range(len(divs)):
            building_params.extend(divs[i].find_all("li", class_="productPage__infoColumnBlockText"))
        for i in range(len(building_params)):
            info = building_params[i].text.strip()
            if "Площадь участка" in info:
                land_area = info.split(":")[1].strip()
            elif "Площадь строения" in info:
                house_area = info.split(":")[1].strip()
            elif "Материал стен" in info:
                material = info.split(":")[1].strip()
            elif "Количество этажей" in info:
                total_floors = info.split(":")[1].strip()
            elif "Вид разрешенного использования" in info:
                status = info.split(":")[1].strip()
            elif any(x in info.lower() for x in ["отапливаемый", "отопление", "водопровод", "канализация",
                                                 "свет", "газ", "вода", "интернет", "телефон"]):
                if comforts == "Не указано":
                    comforts = info.strip()
                else:
                    comforts += "; " + info.strip()
            elif "Улица" in info:
                street = info.split(":")[1].strip()
            elif "Район города" in info:
                district = info.split(":")[1].strip()
            elif "Дом" in info:
                block_number = info.split(":")[1].strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_cottage_params\n")
    return house_area, material, total_floors, land_area, status, comforts, district, street, block_number


def get_apartment_data(html):
    soup = BeautifulSoup(html, "lxml")

    #title = get_title(soup)
    city = get_address(soup)
    material = get_material(soup)
    rooms_number, floor, total_floors, total_area, kitchen_area, living_area, furnish, district, street, block_number = get_apartment_params(soup)
    price, rent_info = get_price(soup)
    block_type = get_block_type(soup)
    #seller_type, seller_name = get_seller_info(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(soup)
    date = get_date(soup)
    selling_detail = "Не указано"  # на irr нет этой информации

    return [city, district, street, block_number, rent_info, price, block_type,
            rooms_number, total_area, total_floors, material, selling_detail, images,
            description, date, phone, kitchen_area, living_area, floor]


def get_commercial_data(html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    # анализируем вид помещения по заголовку
    if "офис" in title.lower():
        object_type = "Офисное помещение"
    elif "торг" in title.lower():
        object_type = "Торговое помещение"
    elif "гостиница" in title.lower():
        object_type = "Гостиница"
    elif "производ" in title.lower():
        object_type = "Производственное помещение"
    elif "склад" in title.lower():
        object_type = "Складское помещение"
    elif "помещение" in title.lower():
        object_type = "Помещение свободного назначения"
    else:
        object_type = "Не указано"

    city = get_address(soup)
    building_type, parking, ceilings, area, entrance, district, street, block_number = get_commercial_params(soup)
    price, rent_info = get_price(soup)
    seller_type, seller_name = get_seller_info(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(soup)
    date = get_date(soup)
    office_class, furniture = "Не указано", "Не указано"  # на irr нет этой информации

    return [city, district, street, block_number, price, object_type, office_class,
            furniture, entrance, area, date, phone, images, description, seller_name]


def get_cottage_data(html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)

    # определим тип объекта по заголовку
    if "дом" in title.lower():
        object_type = "Дом"
    elif "участок" in title.lower():
        object_type = "Участок"
    elif "таунхаус" in title.lower():
        object_type = "Таунхаус"
    else:
        object_type = "Не указано"

    city = get_address(soup)
    price, rent_info = get_price(soup)
    house_area, material, total_floors, land_area, status, comforts, district, street, block_number = get_cottage_params(soup)
    _, seller_name = get_seller_info(soup)
    date = get_date(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(soup)
    selling_detail = "Не указано"  # на irr нет этой информации

    return [city, district, street, block_number, rent_info, price, object_type,
            house_area, comforts, selling_detail, images, description, date, phone, material,
            total_floors, land_area, status, seller_name]


def crawl_page(first_offer, html, category, sell_type):
    global visited_urls, db
    soup = BeautifulSoup(html, "lxml")
    try:
        offers = soup.find("div", class_="listing js-productGrid ").find_all("div", class_="listing__item")
    except:
        offers = []
    if offers is None or not offers:
        print("Парсинг завершен irr")
        return True
    for offer in offers:
        try:
            date = offer.find("span", class_="listing__itemDate").find("div", class_="updateProduct").text.strip()
            if date == date_break_point:
                print("Парсинг завершен irr")
                return True

            url = offer.find("div", class_="listing__itemTitleWrapper").find("a", class_="listing__itemTitle").get("href")
            if url in visited_urls:
                print("irr not unique")
                time.sleep(random.uniform(5, 8))
                continue
            else:
                visited_urls.append(url)
            #print(url)

            data = []
            if category == "Квартиры":
                data = get_apartment_data(get_html(url))
                # записываем ключевую информацию, чтобы потом найти дубликаты
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s--%s\n" % (data[2], data[3], data[4], data[8], data[-1], url))
            elif category == "Дома":
                data = get_cottage_data(get_html(url))
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s\n" % (data[2], data[3], data[7], data[8], url))
            elif category == "Коммерческая_недвижимость":
                data = get_commercial_data(get_html(url))
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s\n" % (data[2], data[3], data[6], data[10], url))

            if first_offer:
                # сохраняем самую первую запись как точку выхода
                modifier = "w" if (category == "Квартиры" and sell_type == "Продажа") else "a"
                with open("breakpoints/irr.txt", modifier, encoding="utf8") as file:
                    file.write("%s--%s\n" % (data[2], data[5]))
                first_offer = False

            key_info = (data[2], data[5])

            if any(x == key_info for x in [break_apartment_sell, break_apartment_rent, break_commercial_sell,
                                           break_commercial_rent, break_cottage_sell, break_cottage_rent]):
                print("Парсинг завершен irr")
                return True

            data.insert(4, sell_type)
            if data[0] != "Не указано":
                try:
                    db.insert_data(category, data)
                except:
                    db.close()
                    db = DataBase()
                    db.insert_data(category, data)
                print("parsed page irr")
            #print(data)

        except Exception as e:
            with open("logs.txt", "a", encoding="utf8") as file:
                file.write(str(e) + " irr crawl_page\n")

        time.sleep(random.uniform(5, 8))


def parse(category_url, category_name, sell_type):
    page_part = "page"

    total_pages = get_total_pages(get_html(category_url))

    for page in range(1, total_pages + 1):
        url_gen = category_url + page_part + str(page)
        if page == 1:
            completed = crawl_page(True, get_html(url_gen), category_name, sell_type)
        else:
            completed = crawl_page(False, get_html(url_gen), category_name, sell_type)
        if completed:
            break


def main():
    global visited_urls
    # на сайте есть разделения продажа/аренда
    # сначала парсим страницу с предложениями продажи
    url_apartments_sell = "https://saratovskaya-obl.irr.ru/real-estate/apartments-sale/sort/date_sort:desc/"
    parse(url_apartments_sell, "Квартиры", "Продажа")

    visited_urls = []
    url_apartments_rent = "https://saratovskaya-obl.irr.ru/real-estate/rent/sort/date_sort:desc/"
    parse(url_apartments_rent, "Квартиры", "Аренда")

    visited_urls = []
    url_commercials_sell = "https://saratovskaya-obl.irr.ru/real-estate/commercial-sale/sort/date_sort:desc/"
    parse(url_commercials_sell, "Коммерческая_недвижимость", "Продажа")

    visited_urls = []
    url_commercials_rent = "https://saratovskaya-obl.irr.ru/real-estate/commercial/sort/date_sort:desc/"
    parse(url_commercials_rent, "Коммерческая_недвижимость", "Аренда")

    visited_urls = []
    url_cottages_sell = "https://saratovskaya-obl.irr.ru/real-estate/out-of-town/sort/date_sort:desc/"
    parse(url_cottages_sell, "Дома", "Продажа")

    visited_urls = []
    url_cottages_rent = "https://saratovskaya-obl.irr.ru/real-estate/out-of-town-rent/sort/date_sort:desc/"
    parse(url_cottages_rent, "Дома", "Аренда")


if __name__ == "__main__":
    main()
    db.close()
