import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from fake_useragent import UserAgent
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


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
        print(e, "total_pages")
        total_pages = 0
    return int(total_pages)


def get_title(soup):
    title = soup.find("td", class_="hh").text.strip()
    return title


def get_price(soup):
    try:
        price = soup.find("td", class_="thprice").text.strip()
    except:
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
        print(e)
    return price


def get_selling_type(soup):
    try:
        # если продажа, ищем тип продажи
        selling_type = "; ".join([x.text.strip() for x in soup.find("td", class_="tddec2").find_all("span", class_="d")])
        # если аренда - срок аренды
        rent_info = [x.text.strip() for x in soup.find_all("td", class_="tddec2")[-2].find_all("span", class_="d")]
        for info in rent_info:
            if "аренда" in info:
                rent_info = info
                break
    except:
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
    except:
        images = "Не указано"
    return images


def get_description(soup):
    try:
        description = soup.find("p", class_="dinfo").text.strip().replace("\r", "")
    except:
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
        print(e, "date")
        date = "Не указано"
    return date


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

            driver = webdriver.Chrome(executable_path=chrome_driver)

            driver.get(url)
            button = driver.find_element_by_xpath('//span[@class="showphone"]')
            button.click()
            time.sleep(3)
            seller_info = driver.find_elements_by_xpath('//td[@class="tddec2"]')[-1].text
            for info in seller_info.split("\n"):
                if "Контактный телефон" in info:
                    phone = info.split(":")[1].strip()
    except Exception as e:
        print(e, "seller phone")
        phone = "Не указано"
    return phone


def get_apartment_params(soup):
    block_type, total_area, total_floors, material = ["Не указано"] * 4
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
            elif "этажей в доме" in param:
                total_floors = param.split(":")[1].split("/")[1]
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
        print(e, "apartment params")
    return block_type, total_area, total_floors, material


def get_cottage_params(soup):
    total_area, material = ["Не указано"] * 2
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
    except Exception as e:
        print(e, "cottage params")
    return total_area, material


def get_commercial_params(soup):
    object_type = "Не указано"
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
    except Exception as e:
        print(e, "cottage params")
    return object_type


def write_csv(data, category):
    if category == "apartments":
        with open("kvadrat_apartments.csv", "a") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(data)
    elif category == "cottages":
        with open("kvadrat_cottages.csv", "a") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(data)
    elif category == "commercials":
        with open("kvadrat_commercials.csv", "a") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(data)


def get_apartment_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower():
        address = "".join(title.split(",")[1:]).strip()
        address = address[:address.rfind(" на карте")]
        if "сдам" in address.lower():
            address = " ".join(address.split()[1:])
        rooms_number = title.split(",")[0]
        block_type, total_area, total_floors, material = get_apartment_params(soup)
        price = get_price(soup)
        selling_type, rent_info = get_selling_type(soup)  # чистая продажа/ипотека/без посредников; если аренда, срок аренды
        if not selling_type:
            selling_type = "Не продажа"
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url, soup)
        date = get_date(soup)

        return [address, rent_info, block_type, rooms_number, price, total_area, total_floors, material, selling_type,
                images, description, phone, date]
    return None


def get_cottage_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower():
        address = "".join(title.split(",")[1:]).strip()
        address = address[:address.rfind(" на карте")]
        cottage_type = title.split(",")[0]
        if "сдам" in cottage_type.lower():
            cottage_type = " ".join(cottage_type.split()[1:])
        price = get_price(soup)
        total_area, material = get_cottage_params(soup)
        selling_type, rent_info = get_selling_type(soup)  # чистая продажа/ипотека/без посредников; если аренда, срок аренды
        if not selling_type:
            selling_type = "Не продажа"
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url, soup)
        date = get_date(soup)

        return [address, rent_info, cottage_type, price, total_area, selling_type, material,
                images, description, phone, date]
    return None


def get_commercial_data(html, url):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower():
        address = "".join(title.split(",")[1:]).strip()
        address = address[:address.rfind(" на карте")]
        object_type = get_commercial_params(soup)
        price = get_commercial_price(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url, soup)
        date = get_date(soup)

        return [address, object_type, price, images, description, phone, date]
    return None


def crawl_page(html, category, sell_type):
    soup = BeautifulSoup(html, "lxml")
    offers = soup.find_all("a", class_="site3adv") + soup.find_all("a", class_="site3")
    for offer in offers:
        try:
            url = "http://kvadrat64.ru/" + offer.get("href")
            data = []
            if category == "apartments":
                data = get_apartment_data(get_html(url), url)
            elif category == "commercials":
                data = get_commercial_data(get_html(url), url)
            elif category == "cottages":
                data = get_cottage_data(get_html(url), url)

            if category == "apartments" or category == "cottages":
                if sell_type == "Аренда":
                    data.insert(1, sell_type + "; " + data[1])  # прибавляем срок аренды
                else:
                    data.insert(1, sell_type)
                data.pop(2)  # и удаляем срок аренды как отдельный элемент списка

            # if data[-1] < datetime.datetime.today():
            #     # сраниваем форматы datetime, чтобы знать, когда закончить парсинг
            #     print("Парсинг завершен")
            #     break
            # else:
            #     # переводим в строковый формат
            #     data[-1] = str(data[-1])

            data[-1] = str(data[-1]).split()[0]  # форматируем дату после проверки
            print(data)

            write_csv(data, category)

            time.sleep(random.uniform(5, 8))
        except Exception as e:
            print(e, "crawl_page")


def parse(category_url, category_name, sell_type):

    total_pages = get_total_pages(get_html(category_url))

    print(total_pages)

    # for page in range(1, total_pages + 1):
    #     url_gen = base_url + page_part + str(page) + parameters_part
    #     crawl_page(get_html(url_gen))

    for page in range(1, 2):
        if category_name == "cottages" and sell_type == "Продажа":
            url = category_url.split("-")
            url_gen = "-".join(url[:2]) + "-" + str(page) + "-" + url[3]
        else:
            url_gen = category_url[:category_url.rfind("-") + 1] + str(page) + ".html"

        crawl_page(get_html(url_gen), category_name, sell_type)


def main():
    url_apartments_sell = "http://kvadrat64.ru/sellflatbank-50-1.html"
    parse(url_apartments_sell, "apartments", "Продажа")

    url_apartments_rent = "https://kvadrat64.ru/giveflatbank-50-1.html"
    parse(url_apartments_rent, "apartments", "Аренда")

    url_cottages_sell = "https://kvadrat64.ru/search-103-1-50664.html"
    parse(url_cottages_sell, "cottages", "Продажа")

    url_cottages_rent = "https://kvadrat64.ru/giveflatbank-9-1.html"
    parse(url_cottages_rent, "cottages", "Аренда")

    url_commercials_sell = "https://kvadrat64.ru/sellcombank-1000-1.html"
    parse(url_commercials_sell, "commercials", "Продажа")

    url_commercials_rent = "https://kvadrat64.ru/givecombank-1000-1.html"
    parse(url_commercials_rent, "commercials", "Аренда")


if __name__ == "__main__":
    # defining chrome options for selenium
    options = Options()
    options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')

    chrome_driver = os.getcwd() + "\\chromedriver.exe"

    main()
