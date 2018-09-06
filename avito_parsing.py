# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import random
import datetime
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from xvfbwrapper import Xvfb
from PIL import Image
from pytesseract import image_to_string
import sys
from database import DataBase

# на каких записях останавливаться
with open("breakpoints/avito.txt", "r", encoding="utf8") as file:
    breakpoints = file.readlines()
    try:
        break_apartment = tuple(breakpoints[0].strip().split("--"))
    except:
        break_apartment = None
    try:
        break_cottage = tuple(breakpoints[1].strip().split("--"))
    except:
        break_cottage = None
    try:
        break_land = tuple(breakpoints[2].strip().split("--"))
    except:
        break_land = None
    try:
        break_commercial = tuple(breakpoints[3].strip().split("--"))
    except:
        break_commercial = None


#defining chrome options for selenium
options = Options()
options.add_argument('--no-sandbox')

db = DataBase()
visited_urls = []


def get_html(url):
    req = requests.get(url, headers={"User-Agent": UserAgent().chrome})
    return req.text.encode(req.encoding)


def get_total_pages(html):
    soup = BeautifulSoup(html, "lxml")
    try:
        pages = soup.find("div", class_="pagination-pages clearfix").find_all("a", class_="pagination-page")[-1].get("href")
        total_pages = int(pages.split("=")[1].split("&")[0])
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_total_pages\n")
        sys.exit(0)
    return total_pages


def get_title(soup):
    try:
        title = soup.find("span", class_="title-info-title-text").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_title\n")
        title = "Не указано"
    return title


def get_address(soup):
    try:
        address = "{}, {}".format(soup.find("meta", itemprop="addressLocality").get("content").strip(),
                                  soup.find("span", itemprop="streetAddress").text.strip())
        # separating data from the address string
        district, street = "Не указано", "Не указано"
        city = address.split(",")[0]
        block_number = address.split(",")[-1].strip()
        if "ул " in block_number.lower() or "ул." in block_number.lower() or "улица" in block_number.lower()\
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
            file.write(str(e) + " avito get_address\n")
        return ["Не указано"] * 4


def get_selling_info(soup):
    try:
        per_meter = False  # если цена указана за квадратный метр
        price = soup.find("span", class_="price-value-string js-price-value-string").text.strip()
        if "за сутки" in price:
            sell_type = "Аренда"
            rent_info = "посуточно"
        elif "в месяц" in price:
            sell_type = "Аренда"
            rent_info = "длительный срок"
            if "за " in price:
                per_meter = True
        else:
            sell_type = "Продажа"
            rent_info = "Не аренда"
        price = soup.find("span", class_="js-item-price").text.strip()
        # ошибка кодировки при записи, собираем сообщение вручную
        if rent_info == "посуточно":
            price = "от " + price + " за сутки"
        elif rent_info == "длительный срок":
            if per_meter:
                price = price + " в месяц за м2"
            else:
                price = price + " в месяц"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_selling info\n")
        sell_type, price, rent_info = ["Не указано"] * 3
    return sell_type, price, rent_info


def get_deposit(soup):
    try:
        deposit = soup.find("div", class_="item-price-sub-price").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_deposit\n")
        deposit = "Не указано"
    return deposit


def get_seller_type(soup):
    try:
        seller_type = soup.find("div", class_="seller-info-prop seller-info-prop_short_margin")
        if seller_type is not None:
            seller_type = "Посредник"
        else:
            seller_type = "Собственник"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_seller_type\n")
        seller_type = "Не указано"
    return seller_type


def get_seller_name(soup):
    try:
        seller_name = soup.find("div", class_="seller-info-name").find("a").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_seller_name\n")
        seller_name = "Не указано"
    return seller_name


def get_photos(soup):
    try:
        images = []
        images_list = soup.find("ul", class_="gallery-list js-gallery-list").find_all("li", class_="gallery-list-item js-gallery-list-item")
        for image in images_list:
            link = image.find("span").get("style").split(":")[1].strip()[4:-2]
            images.append(link)
        images = "\n".join(images)
    except:
        # если нет фото, возьмем фото с "обложки"
        try:
            images = soup.find("span", class_="gallery-img-cover").get("style").split(":")[1].strip()[4:-2]
        except Exception as e:
            with open("logs.txt", "a", encoding="utf8") as file:
                file.write(str(e) + " avito get_photos\n")
            images = "Не указано"
    return images


def get_description(soup):
    try:
        description = soup.find("div", class_="item-description-text").find("p").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_description\n")
        description = "Не указано"
    return description


def get_date(soup):
    try:
        date = soup.find("div", class_="title-info-metadata-item").text.split(",")[1].strip()
        if "сегодня" in date:
            date = str(datetime.datetime.today()).split()[0]
        elif "вчера" in date:
            date = str(datetime.datetime.today() - datetime.timedelta(days=1)).split()[0]
        else:
            date = "too old"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_date\n")
        date = "Не указано"
    return date


def get_seller_phone(url):
    # телефон показывается в виде картинки, используем selenium и pytesseract
    vdisplay = Xvfb()
    vdisplay.start()
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get(url)

    try:
        button = driver.find_element_by_xpath('//a[@class="button item-phone-button js-item-phone-button '
                                              'button-origin button-origin-blue button-origin_full-width '
                                              'button-origin_large-extra item-phone-button_hide-phone '
                                              'item-phone-button_card js-item-phone-button_card"]')
        button.click()
        time.sleep(2)
        driver.save_screenshot("phone_number.png")

        image = driver.find_element_by_xpath('//div[@class="item-phone-big-number js-item-phone-big-number"]//*')

        cropped = Image.open("phone_number.png")
        x, y = image.location["x"], image.location["y"]
        width, height = image.size["width"], image.size["height"]
        cropped.crop((x, y, x + width, y + height)).save("phone.gif")

        phone = Image.open("phone.gif")
        phone_text = image_to_string(phone)
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_seller_phone\n")
        phone_text = "Не указано"

    driver.quit()
    vdisplay.stop()

    return phone_text


def get_apartment_params(soup):
    rooms_number, floor_number, total_floors, material, total_area, kitchen_area, living_area = ["Не указано"] * 7
    block_type = "Вторичка"
    try:
        params = soup.find_all("li", class_="item-params-list-item")
        for i in range(len(params)):
            info = params[i].text.strip()
            if "Количество комнат" in info:
                rooms_number = info.split(":")[1].strip()
            elif "Этажей в доме" in info:
                total_floors = info.split(":")[1].strip()
            elif "Этаж" in info:
                floor_number = info.split(":")[1].strip()
            elif "Тип дома" in info:
                material = info.split(":")[1].strip()
            elif "Общая площадь" in info:
                total_area = info.split(":")[1].split("м²")[0].strip()
            elif "Площадь кухни" in info:
                kitchen_area = info.split(":")[1].split("м²")[0].strip()
            elif "Жилая площадь" in info:
                living_area = info.split(":")[1].split("м²")[0].strip()
            elif "Официальный застройщик" in info or "Название объекта недвижимости" in info:
                block_type = "Новостройка"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_apartment_params\n")
    return rooms_number, floor_number, total_floors, material, total_area, kitchen_area, living_area, block_type


def get_cottage_params(soup):
    house_type, total_floors, distance, material, total_area, land_area = ["Не указано"] * 6
    try:
        params = soup.find_all("li", class_="item-params-list-item")
        for i in range(len(params)):
            info = params[i].text.strip()
            if "Вид объекта" in info:
                house_type = info.split(":")[1].strip()
            elif "Этажей в доме" in info:
                total_floors = info.split(":")[1].strip()
            elif "Расстояние до города" in info:
                distance = info.split(":")[1].split("км")[0].strip() + " км"
            elif "Материал стен" in info:
                material = info.split(":")[1].strip()
            elif "Площадь дома" in info:
                total_area = info.split(":")[1].split("м²")[0].strip()
            elif "Площадь участка" in info:
                land_area = info.split(":")[1].split("сот")[0].strip() + " сот"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_cottage_params\n")
    return house_type, total_floors, distance, material, total_area, land_area


def get_land_params(soup):
    distance, area = "Не указано", "Не указано"
    try:
        labels = soup.find_all("span", class_="item-params-label")
        params = soup.find("div", class_="item-params").find_all("span")
        for i in range(len(labels)):
            info = params[i * 2].text.strip()
            label = labels[i].text.strip()
            if "Расстояние до города" in label:
                distance = info.split(":")[1].split("км")[0].strip() + " км"
            elif "Площадь" in label:
                area = info.split(":")[1].split("сот")[0].strip() + " сот"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_land_params\n")
    return distance, area


def get_commercial_params(soup):
    office_class, area = "Не указано", "Не указано"
    try:
        labels = soup.find_all("span", class_="item-params-label")
        params = soup.find("div", class_="item-params").find_all("span")
        for i in range(len(labels)):
            info = params[i * 2].text.strip()
            label = labels[i].text.strip()
            if "Площадь" in label:
                area = info.split(":")[1].split("м²")[0].strip()
            elif "Класс здания" in label:
                office_class = info.split(":")[1].strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " avito get_commercial_params\n")
    return office_class, area


def get_apartment_data(url, html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower() and "куплю" not in title.lower():
        city, district, street, block_number = get_address(soup)
        sell_type, price, rent_info = get_selling_info(soup)
        rooms_number, floor_number, total_floors, material, total_area, kitchen_area, living_area, block_type = get_apartment_params(soup)
        #seller_type = get_seller_type(soup)
        #seller_name = get_seller_name(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url)
        date = get_date(soup)
        selling_detail = "Не указано"  # на авито не указывается эта информация

        return [city, district, street, block_number, sell_type, rent_info, price, block_type,
                rooms_number, total_area, total_floors, material, selling_detail, images,
                description, date, phone, kitchen_area, living_area, floor_number]

    return None


def get_cottage_data(url, html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower() and "куплю" not in title.lower():
        city, district, street, block_number = get_address(soup)
        sell_type, price, rent_info = get_selling_info(soup)
        house_type, total_floors, distance, material, total_area, land_area = get_cottage_params(soup)
        #seller_type = get_seller_type(soup)
        seller_name = get_seller_name(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url)
        date = get_date(soup)
        selling_detail, comforts, land_status = ["Не указано"] * 3  # на авито не указывается эта информация

        return [city, district, street, block_number, sell_type, rent_info, price, house_type,
                total_area, comforts, selling_detail, images, description, date, phone, material,
                total_floors, land_area, land_status, seller_name]
    return None


def get_land_data(url, html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower() and "куплю" not in title.lower():
        # категория земель указывается в скобках в названии объявления
        if "(" in title:
            land_type = title[title.find("(") + 1:].split(")")[0]
        else:
            land_type = "Не указано"

        city, district, street, _ = get_address(soup)
        sell_type, price, _ = get_selling_info(soup)

        if "Аренда" in sell_type:
            deposit = get_deposit(soup)
        else:
            deposit = "Не аренда"

        distance, area = get_land_params(soup)
        seller_type = get_seller_type(soup)
        seller_name = get_seller_name(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url)
        date = get_date(soup)

        return [city, district, street, sell_type, deposit, land_type, distance, area, price, seller_type, images,
                description, seller_name, phone, date]
    return None


def get_commercial_data(url, html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower() and "куплю" not in title.lower():
        # анализируем вид помещения по заголовку
        if "офис" in title.lower():
            object_type = "Офисное помещение"
        elif "торг" in title.lower():
            object_type = "Торговое помещение"
        elif "гостиница" in title.lower():
            object_type = "Гостиница"
        elif "свобод" in title.lower():
            object_type = "Помещение свободного назначения"
        elif "производ" in title.lower():
            object_type = "Производственное помещение"
        elif "склад" in title.lower():
            object_type = "Складское помещение"
        else:
            object_type = "Не указано"

        city, district, street, block_number = get_address(soup)
        sell_type, price, _ = get_selling_info(soup)

        # if "Аренда" in sell_type:
        #     deposit = get_deposit(soup)
        # else:
        #     deposit = "Не аренда"

        # если не офис, не заполняем поле office_class
        if object_type == "Офисное помещение":
            office_class, area = get_commercial_params(soup)
        else:
            _, area = get_commercial_params(soup)
            office_class = "Не офис"

        #seller_type = get_seller_type(soup)
        seller_name = get_seller_name(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url)
        date = get_date(soup)
        furniture, entrance = "Не указано", "Не указано"  # на авито не указывается эта информация

        return [city, district, street, block_number, sell_type, price, object_type, office_class,
                furniture, entrance, area, date, phone, images, description, seller_name]
    return None


def crawl_page(first_offer, html, category):
    global visited_urls, db
    soup = BeautifulSoup(html, "lxml")
    try:
        offers = soup.find("div", class_="catalog-list").find_all("div", class_="item_table")
    except:
        offers = []
    if offers is None or not offers:
        print("Парсинг завершен avito")
        return True
    for offer in offers:
        try:
            if first_offer:
                # сохраняем самую первую запись как точку выхода
                modifier = "w" if category == "Квартиры" else "a"
                with open("breakpoints/avito.txt", modifier, encoding="utf8") as file:
                    file.write("%s--%s\n" % (offer.find("a", class_="item-description-title-link").get("title"),
                                                 offer.find("span", {"class": "price", "itemprop": "price"}).get("content")))
                first_offer = False

            if offer.find("div", class_="js-item-date c-2").text.strip() == "2 дня назад":
                print("Парсинг завершен avito")
                return True

            key_info = (offer.find("a", class_="item-description-title-link").get("title"), offer.find("span", {"class": "price", "itemprop": "price"}).get("content"))

            if any(x == key_info for x in [break_apartment, break_cottage, break_land, break_commercial]):
                print("Парсинг завершен avito")
                return True

            url = "https://avito.ru" + offer.find("div", class_="description").find("h3").find("a").get("href")
            if url in visited_urls:
                print("avito not unique")
                time.sleep(random.uniform(5, 8))
                continue
            else:
                visited_urls.append(url)

            data = []
            if category == "Квартиры":
                data = get_apartment_data(url, get_html(url))
                # записываем ключевую информацию, чтобы потом найти дубликаты
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s--%s\n" % (data[2], data[3], data[4], data[8], data[-1], url))
            elif category == "Дома":
                data = get_cottage_data(url, get_html(url))
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s\n" % (data[2], data[3], data[7], data[8], url))
            elif category == "Участки":
                data = get_land_data(url, get_html(url))
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s\n" % (data[2], data[5], data[7], url))
            elif category == "Коммерческая_недвижимость":
                data = get_commercial_data(url, get_html(url))
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s\n" % (data[2], data[3], data[6], data[10], url))

            if data[0] != "Не указано" and data is not None:
                try:
                    db.insert_data(category, data)
                except:
                    db.close()
                    db = DataBase()
                    db.insert_data(category, data)
                print("parsed page avito")

            #print(data)

        except Exception as e:
            with open("logs.txt", "a", encoding="utf8") as file:
                file.write(str(e) + " avito crawl_page\n")
                #print(str(e) + " avito crawl_page")

        time.sleep(random.uniform(5, 8))


def parse(category_url, base_url, category_name):
    page_part = "p="
    parameters_part = "&s=104&s_trg=3&bt=1"

    total_pages = get_total_pages(get_html(category_url))

    for page in range(1, total_pages + 1):
        url_gen = base_url + page_part + str(page) + parameters_part
        if page == 1:
            completed = crawl_page(True, get_html(url_gen), category_name)
        else:
            completed = crawl_page(False, get_html(url_gen), category_name)
        if completed:
            break


def main():
    global visited_urls
    url_apartments = "https://www.avito.ru/saratovskaya_oblast/kvartiry?p=1&s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/kvartiry?"
    parse(url_apartments, base_url, "Квартиры")

    visited_urls = []
    url_cottages = "https://www.avito.ru/saratovskaya_oblast/doma_dachi_kottedzhi?s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/doma_dachi_kottedzhi?"
    parse(url_cottages, base_url, "Дома")

    visited_urls = []
    url_lands = "https://www.avito.ru/saratovskaya_oblast/zemelnye_uchastki?s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/zemelnye_uchastki?"
    parse(url_lands, base_url, "Участки")

    visited_urls = []
    url_commercials = "https://www.avito.ru/saratovskaya_oblast/kommercheskaya_nedvizhimost?s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/kommercheskaya_nedvizhimost?"
    parse(url_commercials, base_url, "Коммерческая_недвижимость")


if __name__ == "__main__":
    main()
    db.close()
