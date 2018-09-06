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
with open("breakpoints/kvadrat.txt", "r", encoding="utf8") as file:
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
    try:
        break_dacha_sell = tuple(breakpoints[6].strip().split("--"))
    except:
        break_dacha_sell = None
    try:
        break_saratov_land_sell = tuple(breakpoints[7].strip().split("--"))
    except:
        break_saratov_land_sell = None
    try:
        break_region_land_sell = tuple(breakpoints[8].strip().split("--"))
    except:
        break_region_land_sell = None

# defining chrome options for selenium
options = Options()
options.add_argument("--no-sandbox")

db = DataBase()
visited_urls = []


def transform_date(date_str):
    """
    Преобразуем дату, чтобы сравнить datetime-объекты
    """
    day, month, year = date_str.split("-")
    if day[0] == "0":
        day = day[1]
    if month[0] == "0":
        month = month[1]

    date = datetime.datetime(int(year), int(month), int(day))
    return date


def get_html(url):
    # сайт использует кодировку windows-1251, поэтому меняем на utf-8
    req = requests.get(url, headers={"User-Agent": UserAgent().chrome})
    return req.text.encode(req.encoding)


def get_total_pages(html):
    soup = BeautifulSoup(html, "lxml")
    try:
        total_pages = soup.find("div", class_="a t100")
        if total_pages is not None:
            total_pages = total_pages.find_all("a", class_="phase")[-1].text.strip()
        else:
            total_pages = 0
    except Exception as e:
        total_pages = 0
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_total_pages\n")
    return int(total_pages)


def get_title(soup):
    try:
        title = soup.find("td", class_="hh").text.strip()
    except Exception as e:
        title = "Не указано"
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_title\n")
    return title


def get_price(soup):
    try:
        price = soup.find("td", class_="thprice").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_price\n")
        price = "Не указано"
    return price


def get_commercial_price(soup):
    price = "Не указано"
    try:
        aggregated = [x.find_all("span", class_="d") for x in soup.find_all("td", class_="tddec2")]  # список из всех ссылок из tddec2
        flat_aggregated = [item for sublist in aggregated for item in sublist]  # из двумерного списка делаем одномерный
        price_params = [x.text.strip() for x in flat_aggregated]
        for param in price_params:
            if "за м²" in param:
                price = "м2".join(param.split("м²"))
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_price\n")
    return price


def get_selling_type(soup):
    try:
        # если продажа, ищем тип продажи
        selling_type = "; ".join([x.text.strip() for x in soup.find("td", class_="tddec2").find_all("span", class_="d")])
        if not selling_type:
            selling_type = "Не продажа"
        # если аренда - срок аренды
        rent_info = [x.text.strip() for x in soup.find_all("td", class_="tddec2")[-2].find_all("span", class_="d")]
        for info in rent_info:
            if "аренда" in info:
                rent_info = info
                break
        if not rent_info:
            rent_info = "Не аренда"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_selling_type\n")
        selling_type = "Не указано"
        rent_info = "Не указано"
    return selling_type, rent_info


def get_photos(soup):
    try:
        images = []
        # список ссылок на картинки в полном размере
        td_images = soup.find("td", class_="tdimg").find_all("a")
        for image_item in td_images:
            link = "https://kvadrat64.ru/" + image_item.get("href")
            html_gallery = BeautifulSoup(get_html(link), "lxml")
            image = html_gallery.find("img", {"style": "cursor:pointer;"})
            if image is not None:
                images.append("https://kvadrat64.ru/" + image.get("src"))
        images = "\n".join(images)
        # если нет картинок в галерее, пытаемся вытащить с облоджки
        if not images:
            images = "https://kvadrat64.ru/" + soup.find("div", id="mainfotoid").find("img").get("src")
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_photos\n")
        images = "Не указано"
    return images


def get_description(soup):
    try:
        description = soup.find("p", class_="dinfo").text.strip().replace("\r", "")
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_description\n")
        description = "Не указано"
    return description


def get_date(soup):
    try:
        date = soup.find("div", class_="tdate").text.strip().split(",")[1]
        if "сделать" in date:
            date = date.split("сделать")[0].split("создано")[1].strip()
        else:
            date = date.split("VIP")[0].split("создано")[1].strip()
        date = transform_date(date)
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_date\n")
        date = "Не указано"
    return date


def get_seller_name(soup):
    try:
        name = soup.find_all("td", class_="tddec2")[-1].find("span").text.strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_seller_name\n")
        name = "Не указано"
    return name


def get_seller_phone(url, soup):
    phone = "Не указано"
    # телефон появляется динамически, используем selenium
    try:
        # иногда посредники указывают телефон в самом тексте; проверяем это
        tddec = soup.find_all("td", class_="tddec2")[-1].find_all(text=True)
        found = False
        for i in range(len(tddec)):
            if "Персона для контактов" in tddec[i]:
                phone = tddec[i + 1].split(",")[-1].strip()
                found = True
            elif "Контактный телефон" in tddec[i]:
                found = False

        if "".join(phone.split()).isalpha():
            phone = "Не указано"

        if not found:
            vdisplay = Xvfb()
            vdisplay.start()
            driver = webdriver.Chrome(options=options)
            driver.set_window_size(1920, 1080)
            driver.get(url)

            button = driver.find_element_by_xpath('//span[@class="showphone"]')
            button.click()
            time.sleep(3)
            seller_info = driver.find_elements_by_xpath('//td[@class="tddec2"]')[-1].text
            for info in seller_info.split("\n"):
                if "Контактный телефон" in info:
                    phone = info.split(":")[1].strip()
            driver.quit()
            vdisplay.stop()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_seller_phone\n")
        phone = "Не указано"
    return phone


def get_apartment_params(soup):
    block_type, total_area, kitchen_area, living_area, floor, total_floors, material = ["Не указано"] * 7
    try:
        ###
        # из-за кривой структуры сайта, формируем все сами в удобный формат
        params_raw = str(soup.find("td", class_="tddec")).split("<br/>")
        params = BeautifulSoup(params_raw[0], "lxml").find("td", class_="tddec").text.strip().split("\xa0")
        for param in params_raw[1:]:
            params.append(BeautifulSoup(param, "lxml").text.strip())
        ###
        new_block = False  # в новостройке ли квартира
        add_info = ""  # дата сдачи, застройщик (указываем в одноц графе)
        for param in params:
            if "Площадь общая" in param:
                total_area = param.split(":")[1].split("м²")[0].strip() + " м2"
            elif "Кухня" in param:
                kitchen_area = param.split(":")[1].split("м²")[0].strip() + " м2"
            elif "Жилая" in param:
                living_area = param.split(":")[1].split("м²")[0].strip() + " м2"
            elif "этажей в доме" in param:
                total_floors = param.split(":")[1].split("/")[1]
                floor = param.split(":")[1].split("/")[0].split()[1]
            elif "cтроение" in param:
                material = param.split(":")[1].strip()
            elif "Застройщик" in param or "Дата сдачи" in param or "Стадия строительства" in param:
                new_block = True
                add_info += param.split(":")[1] + ";"

        if new_block:
            block_type = "Новостройка " + add_info
        else:
            block_type = "Вторичка"
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_apartment_params\n")
    return block_type, total_area, kitchen_area, living_area, floor, total_floors, material


def get_cottage_params(soup):
    total_area, material, comforts, total_floors, land_area = ["Не указано"] * 5
    try:
        ###
        # из-за кривой структуры сайта, формируем все сами в удобный формат
        params_raw = str(soup.find("td", class_="tddec")).split("<br/>")
        params = BeautifulSoup(params_raw[0], "lxml").find("td", class_="tddec").text.strip().split("\xa0")
        for param in params_raw[1:]:
            params.append(BeautifulSoup(param, "lxml").text.strip())
        ###
        for param in params:
            if "Площадь общая" in param:
                total_area = param.split(":")[1].split("м²")[0].strip() + " м2"
            elif "cтроение" in param:
                material = param.split(":")[1].strip()
            elif "Площадь участка" in param:
                land_area = param.split(":")[1].strip()
            elif "Этажей" in param:
                total_floors = param.split(":")[1].strip()
            elif "Коммуникации" in param:
                comforts = param.split(":")[1].strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_cottage_params\n")
    return total_area, material, comforts, total_floors, land_area


def get_commercial_params(soup):
    object_type, area = ["Не указано"] * 2
    try:
        ###
        # из-за кривой структуры сайта, формируем все сами в удобный формат
        params_raw = str(soup.find("td", class_="tddec")).split("<br/>")
        params = BeautifulSoup(params_raw[0], "lxml").find("td", class_="tddec").text.strip().split("\xa0")
        for param in params_raw[1:]:
            params.append(BeautifulSoup(param, "lxml").text.strip())
        ###
        for param in params:
            if "Объект" in param:
                object_type = param.split(":")[1].strip()
            elif "площадь" in param:
                area = param.split(":")[1].strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_commercial_params\n")
    return object_type, area


def get_dacha_params(soup):
    total_area = "Не указано"
    try:
        ###
        # из-за кривой структуры сайта, формируем все сами в удобный формат
        params_raw = str(soup.find("td", class_="tddec")).split("<br/>")
        params = BeautifulSoup(params_raw[0], "lxml").find("td", class_="tddec").text.strip().split("\xa0")
        for param in params_raw[1:]:
            params.append(BeautifulSoup(param, "lxml").text.strip())
        ###
        for param in params:
            if "Площадь дома" in param:
                total_area = param.split(":")[1].strip()
                break
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_dacha_params\n")
    return total_area


def get_land_params(soup):
    total_area, land_type = ["Не указано"] * 2
    try:
        ###
        # из-за кривой структуры сайта, формируем все сами в удобный формат
        params_raw = str(soup.find("td", class_="tddec")).split("<br/>")
        params = BeautifulSoup(params_raw[0], "lxml").find("td", class_="tddec").text.strip().split("\xa0")
        for param in params_raw[1:]:
            params.append(BeautifulSoup(param, "lxml").text.strip())
        ###
        for param in params:
            if "Площадь участка" in param:
                total_area = param.split(":")[1].strip()
            elif "Тип земли" in params:
                land_type = param.split(":")[1].strip()
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " kvadrat get_land_params\n")
    return total_area, land_type


def get_apartment_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower():
        address = ",".join(title.split(",")[1:]).strip()
        address = address[:address.rfind(" на карте")]
        if "сдам" in address.lower():
            address = " ".join(address.split()[1:])
        if "(" in address:
            address = address[:address.rfind("(")]

        city = address.split(",")[-1].strip()
        district = address.split(",")[-2].strip()
        block_number = address.split(",")[-3].strip()
        street = address.split(",")[-4].strip()

        rooms_number = title.split(",")[0]
        block_type, total_area, kitchen_area, living_area, floor, total_floors, material = get_apartment_params(soup)
        price = get_price(soup)
        selling_detail, rent_info = get_selling_type(soup)  # чистая продажа/ипотека/без посредников; если аренда, срок аренды
        if not selling_detail:
            selling_detail = "Не продажа"
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url, soup)
        date = get_date(soup)

        return [city, district, street, block_number, rent_info, price, block_type,
                rooms_number, total_area, total_floors, material, selling_detail, images,
                description, date, phone, kitchen_area, living_area, floor]
    return None


def get_cottage_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower():
        address = ",".join(title.split(",")[1:]).strip()
        address = address[:address.rfind(" на карте")]
        if "(" in address:
            address = address[:address.rfind("(")]

        if address == address.upper():
            city, street, block_number = address.split(",") + (["Не указано"] * (3 - len(address.split(","))))
            district = "Не указано"
        else:
            city = address.split(",")[-1].strip()
            district = address.split(",")[-2].strip()
            block_number = address.split(",")[-3].strip()
            street = address.split(",")[-4].strip()

        cottage_type = title.split(",")[0]
        if "сдам" in cottage_type.lower():
            cottage_type = " ".join(cottage_type.split()[1:])
        price = get_price(soup)
        total_area, material, comforts, total_floors, land_area = get_cottage_params(soup)
        selling_detail, rent_info = get_selling_type(soup)  # чистая продажа/ипотека/без посредников; если аренда, срок аренды
        if not selling_detail:
            selling_detail = "Не продажа"
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url, soup)
        seller_name = get_seller_name(soup)
        date = get_date(soup)
        status = "Не указано"  # нет такой информации

        return [city, district, street, block_number, rent_info, price, cottage_type,
                total_area, comforts, selling_detail, images, description, date, phone, material,
                total_floors, land_area, status, seller_name]
    return None


def get_commercial_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower():
        address = ",".join(title.split(",")[1:]).strip()
        address = address[:address.rfind(" на карте")]
        if "(" in address:
            address = address[:address.rfind("(")]

        city = address.split(",")[-1].strip()
        district = address.split(",")[-2].strip()
        block_number = address.split(",")[-3].strip()
        street = address.split(",")[-4].strip()

        object_type, area = get_commercial_params(soup)
        price = get_commercial_price(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url, soup)
        date = get_date(soup)
        seller_name = get_seller_name(soup)
        office_class, furniture, entrance = ["Не указано"] * 3

        return [city, district, street, block_number, price, object_type, office_class,
            furniture, entrance, area, date, phone, images, description, seller_name]
    return None


def get_land_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower():
        address = ",".join(title.split(",")[1:]).strip()
        address = address[:address.rfind("(")].strip()

        city = address.split(",")[0]
        if len(address.split(",")) > 1:
            district = address.split(",")[1].strip()
        else:
            district = "Не указано"
        street = "Не указано"

        if city.lower() == "саратов":
            distance = "В черте города"
        else:
            distance = title[title.find("(") + 1:title.find(")")]

        area, land_type = get_land_params(soup)
        price = get_price(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url, soup)
        date = get_date(soup)
        seller_name = get_seller_name(soup)
        sell_type = "Продажа"
        deposit, seller_type = ["Не указано"] * 2

        return [city, district, street, sell_type, deposit, land_type, distance, area, price, seller_type, images,
                description, seller_name, phone, date]
    return None


def crawl_page(first_offer, html, category, sell_type):
    global visited_urls, db
    soup = BeautifulSoup(html, "lxml")
    try:
        #offers = soup.find_all("a", class_="site3adv") + soup.find_all("a", class_="site3")
        offers = soup.find_all("a", class_="site3")
    except:
        offers = []
    if offers is None or not offers:
        print("Парсинг завершен kvadrat")
        return True
    for offer in offers:
        try:
            url = "http://kvadrat64.ru/" + offer.get("href")
            if url in visited_urls:
                print("kvadrat not unique")
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
            elif category == "Участки":
                data = get_land_data(get_html(url), url)
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s\n" % (data[2], data[5], data[7], url))
            elif category == "Коммерческая_недвижимость":
                data = get_commercial_data(get_html(url), url)
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s--%s\n" % (data[2], data[3], data[6], data[10], url))

            if first_offer:
                # сохраняем самую первую запись как точку выхода
                modifier = "w" if (category == "Квартиры" and sell_type == "Продажа") else "a"
                with open("breakpoints/kvadrat.txt", modifier, encoding="utf8") as file:
                    file.write("%s--%s\n" % (data[2], data[5]))
                first_offer = False

            key_info = (data[2], data[5])

            if any(x == key_info for x in [break_apartment_sell, break_apartment_rent, break_cottage_sell,
                                           break_cottage_rent, break_commercial_sell, break_commercial_rent,
                                           break_dacha_sell, break_saratov_land_sell, break_region_land_sell]):
                print("Парсинг завершен kvadrat")
                return True

            data.insert(4, sell_type)

            # на каком месте находится дата объявления
            index_of_date = -1
            if category == "Квартиры" or category == "Коммерческая_недвижимость":
                index_of_date = -5
            elif category == "Дома":
                index_of_date = -7
            elif category == "Участки":
                index_of_date = -1

            if data[index_of_date] != "Не указано" and data[index_of_date] < datetime.datetime.today() - datetime.timedelta(days=1):
                # сраниваем форматы datetime, чтобы знать, когда закончить парсинг
                print("Парсинг завершен kvadrat")
                return True
            else:
                # переводим в строковый формат
                data[index_of_date] = str(data[index_of_date]).split()[0]

            if data[0] != "Не указано" and data is not None:
                try:
                    db.insert_data(category, data)
                except:
                    db.close()
                    db = DataBase()
                    db.insert_data(category, data)
                print("parsed page kvadrat")

            #print(data)

        except Exception as e:
            with open("logs.txt", "a", encoding="utf8") as file:
                file.write(str(e) + " kvadrat crawl_page\n")

        time.sleep(random.uniform(5, 8))


def parse(category_url, category_name, sell_type):

    total_pages = get_total_pages(get_html(category_url))

    for page in range(1, total_pages + 1):
        if (category_name == "Дома" and sell_type == "Продажа" and "sellzagbank" not in category_url) or category_name == "Участки":
            url = category_url.split("-")
            url_gen = "-".join(url[:2]) + "-" + str(page) + "-" + url[3]
        else:
            url_gen = category_url[:category_url.rfind("-") + 1] + str(page) + ".html"

        if page == 1:
            completed = crawl_page(True, get_html(url_gen), category_name, sell_type)
        else:
            completed = crawl_page(False, get_html(url_gen), category_name, sell_type)
        if completed:
            break


def main():
    global visited_urls
    url_apartments_sell = "http://kvadrat64.ru/sellflatbank-50-1.html"
    parse(url_apartments_sell, "Квартиры", "Продажа")

    visited_urls = []
    url_apartments_rent = "https://kvadrat64.ru/giveflatbank-50-1.html"
    parse(url_apartments_rent, "Квартиры", "Аренда")

    visited_urls = []
    url_cottages_sell = "https://kvadrat64.ru/search-103-1-50664.html"
    parse(url_cottages_sell, "Дома", "Продажа")

    visited_urls = []
    url_cottages_rent = "https://kvadrat64.ru/giveflatbank-9-1.html"
    parse(url_cottages_rent, "Дома", "Аренда")

    visited_urls = []
    url_commercials_sell = "https://kvadrat64.ru/sellcombank-1000-1.html"
    parse(url_commercials_sell, "Коммерческая_недвижимость", "Продажа")

    visited_urls = []
    url_commercials_rent = "https://kvadrat64.ru/givecombank-1000-1.html"
    parse(url_commercials_rent, "Коммерческая_недвижимость", "Аренда")

    visited_urls = []
    url_dachas_sell = "https://kvadrat64.ru/sellzagbank-1000-1.html"
    parse(url_dachas_sell, "Дома", "Продажа")

    visited_urls = []
    url_saratov_lands_sell = "https://kvadrat64.ru/search-41-1-24435.html"
    parse(url_saratov_lands_sell, "Участки", "Продажа")

    visited_urls = []
    url_region_lands_sell = "https://kvadrat64.ru/search-412-1-24450.html"
    parse(url_region_lands_sell, "Участки", "Продажа")


if __name__ == "__main__":
    main()
    db.close()
