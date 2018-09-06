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


db = DataBase()
visited_urls = []

# defining chrome options for selenium
options = Options()
options.add_argument("--no-sandbox")


def get_html(url):
    req = requests.get(url, headers={"User-Agent": UserAgent().chrome})
    return req.text.encode(req.encoding)


def get_title(soup):
    try:
        title = soup.find("h1").text.strip()
    except Exception as e:
        #print(str(e) + " title")
        title = "Не указано"
    return title


def get_address(soup):
    try:
        address = soup.find("address").text.strip()
        if "На карте" in address:
            address = address[:address.rfind("На карте")]
        # separating data from the address string
        district, street = "Не указано", "Не указано"
        city = address.split(",")[1].strip()
        block_number = address.split(",")[-1].strip()
        if "ул " in block_number.lower() or "ул." in block_number.lower() or "улица" in block_number.lower() \
                or " пер" in block_number.lower() or "проезд" in block_number.lower() or "проспект" in block_number.lower():
            street = block_number
            block_number = "Не указано"

        for param in address.split(",")[1:-1]:
            if "ул " in param.lower() or "ул." in param.lower() or "улица" in param.lower() or " пер" in param.lower() \
                    or "проезд" in param.lower() or "проспект" in param.lower():
                street = param.strip()
            elif "район" in param.lower() or "р-н" in param.lower():
                district = param.strip()

        if street.split()[-1].strip().isdigit():
            block_number = street.split()[-1].strip()
            street = " ".join(street.split()[:-1]).strip()

        return city, district, street, block_number
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_title\n")
    return ["Не указано"] * 4


def get_price(soup):
    try:
        price = soup.find("span", {"itemprop": "price"})
        if price is not None:
            price = price.text.strip()
        else:
            price = "от " + soup.find("span", {"itemprop": "lowPrice"}).text.strip() + \
                    " до " + soup.find("span", {"itemprop": "highPrice"}).text.strip() + "/мес."
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_price\n")
        price = "Не указано"
    return price


def get_selling_type(soup):
    try:
        paragraphs = [x for x in soup.find_all("p") if x.get("class") is not None
                      and len(x.get("class")) == 1 and "description--" in x.get("class")[0]]
        if paragraphs:
            selling_type = paragraphs[0].text.strip()
        else:
            selling_type = "Не указано"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_selling_type\n")
        selling_type = "Не указано"
    return selling_type


def get_seller_type(soup):
    try:
        divs = [x for x in soup.find_all("div") if x.get("class") is not None
                and len(x.get("class")) == 1 and "honest-container" in x.get("class")[0]]
        if not divs:
            seller_type = "Не указано"
        else:
            seller_type = divs[0].text.strip()
            if seller_type is not None and seller_type.lower() == "собственник":
                seller_type = "Собственник"
            else:
                seller_type = "Посредник"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_seller_type\n")
        seller_type = "Не указано"
    return seller_type


def get_seller_name(soup):
    try:
        name = [x for x in soup.find_all("h2") if x.get("class") is not None and len(x.get("class")) == 1
                and "title--" in x.get("class")[0]]
        if name:
            name = name[0].text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_seller_name\n")
        name = "Не указано"
    return name


def get_photos(url):
    try:
        driver = webdriver.Chrome()
        driver.get(url)

        images = []
        images_list = driver.find_elements_by_class_name("fotorama__img")
        images_list = [x.get_attribute("src") for x in images_list if "-2." in x.get_attribute("src")]
        for image in images_list:
            link = image.replace("-2.", "-1.")
            images.append(link)
        images = "\n".join(images)
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_photos\n")
        images = "Не указано"
    return images


def get_description(soup):
    try:
        paragraphs = [x for x in soup.find_all("p") if x.get("class") is not None
                      and len(x.get("class")) == 1 and "description-text--" in x.get("class")[0]]
        description = paragraphs[0].text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_description\n")
        description = "Не указано"
    return description


def get_date(soup):
    try:
        date = soup.find("div", id="frontend-offer-card").find("main").find_all("div")[4].text.strip()
        if "вчера" in date:
            date = str(datetime.datetime.today() - datetime.timedelta(days=1)).split()[0]
        elif "сегодня" in date:
            date = str(datetime.datetime.today()).split()[0]
        else:
            date = "too old"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_date\n")
        date = "Не указано"
    return date


def driver_get_phone_and_images(url):
    vdisplay = Xvfb()
    vdisplay.start()
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get(url)

    try:
        images = []
        images_list = driver.find_elements_by_class_name("fotorama__img")
        images_list = [x.get_attribute("src") for x in images_list if "-2." in x.get_attribute("src")]
        for image in images_list:
            link = image.replace("-2.", "-1.")
            images.append(link)
        images = "\n".join(images)
        if not images:
            # берем с обложки
            images = driver.find_element_by_class_name("fotorama__img").get_attribute("src")
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_images\n")
        images = "Не указано"

    try:
        button = [x for x in driver.find_elements_by_tag_name("button") if x.text.strip() == "Показать телефон"][-1]
        button.click()
        phone = "\n".join([x.text.strip() for x in driver.find_elements_by_tag_name("a") if x.get_attribute("class") is not None
                           and "phone--" in x.get_attribute("class")])
    except Exception as e:
        phone = "Не указано"
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_phone\n")
    driver.quit()
    vdisplay.stop()
    return images, phone


def get_apartment_params(soup):
    block_type, rooms_number, total_floors, total_area, material, year, kitchen_area, living_area, floor = ["Не указано"] * 9
    try:
        main_params = [x.text.strip() for x in soup.find_all("div") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "info-title--" in x.get("class")[0]]
        main_values = [x.text.strip() for x in soup.find_all("div") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "info-text--" in x.get("class")[0]]
        for i in range(len(main_params)):
            if "Общая" in main_params[i]:
                total_area = main_values[i]
            elif "Построен" in main_params[i]:
                year = main_values[i]
            elif "Кухня" in main_params[i]:
                kitchen_area = main_values[i]
            elif "Жилая" in main_params[i]:
                living_area = main_values[i]

        desc_params = [x.text.strip() for x in soup.find_all("span") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "name--" in x.get("class")[0]]
        desc_values = [x.text.strip() for x in soup.find_all("span") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "value--" in x.get("class")[0]]
        for i in range(len(desc_params)):
            if "Тип жилья" in desc_params[i]:
                block_type = desc_values[i]
            elif "Количество комнат" in desc_params[i]:
                rooms_number = desc_values[i]
            elif "Этаж" in desc_params[i]:
                floor = desc_values[i]
            elif "Этажей в доме" in desc_params[i]:
                total_floors = desc_values[i]
            elif "Тип дома" in desc_params[i]:
                material = desc_values[i]

        if year == "Не указано":
            building_params = [x.text.strip() for x in soup.find_all("div") if x.get("class") is not None
                               and len(x.get("class")) == 1 and "name--" in x.get("class")[0]]
            building_values = [x.text.strip() for x in soup.find_all("div") if x.get("class") is not None
                               and len(x.get("class")) == 1 and "value--" in x.get("class")[0]]
            for i in range(len(building_params)):
                if "Год постройки" in building_params[i]:
                    year = building_values[i]
                    break
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_apartment_params\n")
    return block_type, rooms_number, total_floors, total_area, material, year, kitchen_area, living_area, floor


def get_cottage_params(soup):
    total_area, material, land_area, status, comforts, total_floors = ["Не указано"] * 6
    try:
        main_params = [x.text.strip() for x in soup.find_all("div") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "info-title--" in x.get("class")[0]]
        main_values = [x.text.strip() for x in soup.find_all("div") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "info-text--" in x.get("class")[0]]
        for i in range(len(main_params)):
            if "Общая" in main_params[i]:
                total_area = main_values[i]
            elif "Участок" in main_params[i]:
                land_area = main_values[i]
            elif "Тип дома" in main_params[i]:
                material = main_values[i]
            elif "Этажей в доме" in main_params[i]:
                total_floors = main_values[i]

        comforts_list = [x.text.strip() for x in soup.find_all("li") if x.get("class") is not None
                         and len(x.get("class")) == 2 and "item--" in x.get("class")[0]]
        if comforts:
            comforts = "; ".join(comforts_list)

        desc_params = [x.text.strip() for x in soup.find_all("span") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "name--" in x.get("class")[0]]
        desc_values = [x.text.strip() for x in soup.find_all("span") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "value--" in x.get("class")[0]]
        for i in range(len(desc_params)):
            if "Статус участка" in desc_params[i]:
                status = desc_values[i]
            elif land_area == "Не указано" and "Площадь участка" in desc_params[i]:
                land_area = desc_values[i]
            elif material == "Не указано" and "Тип дома" in desc_params[i]:
                material = desc_values[i]
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_cottage_params\n")
    return total_area, material, land_area, status, comforts, total_floors


def get_commercial_params(soup):
    area, office_class, floor, furniture, entrance = ["Не указано"] * 5
    try:
        main_params = [x.text.strip() for x in soup.find_all("div") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "info-title--" in x.get("class")[0]]
        main_values = [x.text.strip() for x in soup.find_all("div") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "info-text--" in x.get("class")[0]]
        for i in range(len(main_params)):
            if "Класс" in main_params[i]:
                office_class = main_values[i]
            elif "Этаж" in main_params[i]:
                floor = main_values[i]
            elif "Площадь" in main_params[i]:
                area = main_values[i]

        desc_params = [x.text.strip() for x in soup.find_all("span") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "name--" in x.get("class")[0]]
        desc_values = [x.text.strip() for x in soup.find_all("span") if x.get("class") is not None
                       and len(x.get("class")) == 1 and "value--" in x.get("class")[0]]
        for i in range(len(desc_params)):
            if "Вход" in desc_params[i]:
                entrance = desc_values[i]
            elif "Мебель" in desc_params[i]:
                furniture = desc_values[i]
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " cian get_commercial_params\n")
    return area, office_class, floor, furniture, entrance


def get_apartment_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    # title = get_title(soup)
    city, district, street, block_number = get_address(soup)
    price = get_price(soup)
    block_type, rooms_number, total_floors, total_area, material, year, kitchen_area, living_area, floor = get_apartment_params(soup)
    selling_detail = get_selling_type(soup)
    if "продажа" in selling_detail.lower() or "ипотека" in selling_detail.lower():
        rent_info = "Не аренда"
    else:
        rent_info = selling_detail
        selling_detail = "Не продажа"
    #seller_type = get_seller_type(soup)
    description = get_description(soup)
    date = get_date(soup)
    images, phone = driver_get_phone_and_images(url)

    return [city, district, street, block_number, rent_info, price, block_type,
            rooms_number, total_area, total_floors, material, selling_detail, images,
            description, date, phone, kitchen_area, living_area, floor]


def get_cottage_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    city, district, street, block_number = get_address(soup)
    price = get_price(soup)
    cottage_type = title.split(",")[0]
    total_area, material, land_area, status, comforts, total_floors = get_cottage_params(soup)
    selling_detail = get_selling_type(soup)
    if "продажа" in selling_detail.lower() or "ипотека" in selling_detail.lower():
        rent_info = "Не аренда"
    else:
        rent_info = selling_detail
        selling_detail = "Не продажа"
    description = get_description(soup)
    date = get_date(soup)
    images, phone = driver_get_phone_and_images(url)
    seller_name = get_seller_name(soup)

    return [city, district, street, block_number, rent_info, price, cottage_type,
            total_area, comforts, selling_detail, images, description, date, phone, material,
            total_floors, land_area, status, seller_name]


def get_commercial_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    city, district, street, block_number = get_address(soup)
    price = get_price(soup)

    if "офис" in title.lower():
        object_type = "Офисное помещение"
    elif "торговая площадь" in title.lower():
        object_type = "Торговая площадь"
    elif "склад" in title.lower():
        object_type = "Склад"
    elif "своб. назнач." in title.lower() or "свободное назначение" in title.lower():
        object_type = "Свободного назначения"
    elif "гараж" in title.lower():
        object_type = "Гараж"
    elif "автосервис" in title.lower():
        object_type = "Автосервис"
    elif "производство" in title.lower():
        object_type = "Производство"
    elif "готовый бизнес" in title.lower():
        object_type = "Готовый бизнес"
    else:
        object_type = "Не указано"

    area, office_class, floor, furniture, entrance = get_commercial_params(soup)
    if object_type != "Офисное помещение":
        office_class = "Не офис"
    description = get_description(soup)
    date = get_date(soup)
    images, phone = driver_get_phone_and_images(url)
    seller_name = get_seller_name(soup)

    return [city, district, street, block_number, price, object_type, office_class,
            furniture, entrance, area, date, phone, images, description, seller_name]


def crawl_page(page, html, category, sell_type):
    global visited_urls, db
    soup = BeautifulSoup(html, "lxml")
    if page != 1 and "".join([x.text.strip() for x in soup.find_all("li")
                              if len(x.get("class")) == 2 and "list-item--active" in "".join(x.get("class"))]) == "1":
        print("Парсинг завершен cian")
        return True
    # так как пагинация динамическая и мы не можем получить число страниц, проверяем, есть ли на странице объявления
    try:
        offers = [x for x in soup.find("div", id="frontend-serp").find("div").find_all("div")
                  if x.get("class") is not None and "offer-container" in x.get("class")[0]]
    except:
        offers = []
    if offers is None or not offers:
        print("Парсинг завершен cian")
        return True
    for offer in offers:
        try:
            url = offer.find("a").get("href")
            if url in visited_urls:
                print("cian not unique")
                time.sleep(random.uniform(5, 8))
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

            # на каком месте находится дата объявления
            index_of_date = -1
            if category == "Квартиры" or category == "Коммерческая_недвижимость":
                index_of_date = -5
            elif category == "Дома":
                index_of_date = -7
            elif category == "Участки":
                index_of_date = -1
            if data[index_of_date] == "too old":
                print("Парсинг завершен cian")
                return True

            data.insert(4, sell_type)
            if data[0] != "Не указано":
                try:
                    db.insert_data(category, data)
                except:
                    db.close()
                    db = DataBase()
                    db.insert_data(category, data)
                print("parsed page cian")

            #print(*data, sep="\n")
            #print("--------------------------------------")

        except Exception as e:
            with open("logs.txt", "a", encoding="utf8") as file:
                file.write(str(e) + " cian crawl_page\n")

        time.sleep(random.uniform(5, 8))


def parse(category_url, category_name, sell_type):
    completed = False
    page = 1
    while not completed:
        url_gen = category_url[:category_url.rfind("=") + 1] + str(page)
        completed = crawl_page(page, get_html(url_gen), category_name, sell_type)
        page += 1


def main():
    global visited_urls
    url_cottages_sell = "https://saratov.cian.ru/cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=suburban&region=4609&totime=86400&page=1"
    parse(url_cottages_sell, "Дома", "Продажа")

    visited_urls = []
    url_cottages_rent = "https://saratov.cian.ru/cat.php?deal_type=rent&engine_version=2&object_type%5B0%5D=1&offer_type=suburban&region=4609&totime=86400&page=1"
    parse(url_cottages_rent, "Дома", "Аренда")

    visited_urls = []
    url_commercials_sell = "https://saratov.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=offices&office_type%5B0%5D=1&office_type%5B10%5D=12&office_type%5B1%5D=2&office_type%5B2%5D=3&office_type%5B3%5D=4&office_type%5B4%5D=5&office_type%5B5%5D=6&office_type%5B6%5D=7&office_type%5B7%5D=9&office_type%5B8%5D=10&office_type%5B9%5D=11&region=4609&totime=86400&page=1"
    parse(url_commercials_sell, "Коммерческая_недвижимость", "Продажа")

    visited_urls = []
    url_commercials_rent = "https://saratov.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=1&office_type%5B10%5D=12&office_type%5B1%5D=2&office_type%5B2%5D=3&office_type%5B3%5D=4&office_type%5B4%5D=5&office_type%5B5%5D=6&office_type%5B6%5D=7&office_type%5B7%5D=9&office_type%5B8%5D=10&office_type%5B9%5D=11&region=4609&totime=86400&page=1"
    parse(url_commercials_rent, "Коммерческая_недвижимость", "Аренда")

    visited_urls = []
    url_apartments_sell = "https://saratov.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=4609&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1&totime=86400&page=1"
    parse(url_apartments_sell, "Квартиры", "Продажа")

    visited_urls = []
    url_apartments_rent = "https://saratov.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&region=4609&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1&totime=86400&page=1"
    parse(url_apartments_rent, "Квартиры", "Аренда")


if __name__ == "__main__":
    main()
    db.close()
