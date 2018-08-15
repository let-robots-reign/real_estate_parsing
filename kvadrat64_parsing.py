import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from fake_useragent import UserAgent
import os
import datetime
import base64


def get_html(url):
    # сайт использует кодировку windows-1251, поэтому меняем на utf-8
    req = requests.get(url, headers={"User-Agent": UserAgent().chrome})
    return req.text.encode(req.encoding)


def get_total_pages(html):
    soup = BeautifulSoup(html, "lxml")
    total_pages = soup.find("div", class_="a t100")
    if total_pages is not None:
        total_pages = total_pages.find_all("a", class_="phase")[-1].text.strip()
    else:
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


def get_selling_type(soup):
    try:
        selling_type = "; ".join([x.text.strip() for x in soup.find("td", class_="tddec2").find_all("span", class_="d")])
    except:
        selling_type = "Не указано"
    return selling_type


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
                total_area = param.split(":")[1].split("м²")[0] + " м2"
            elif "этажей в доме" in param:
                total_floors = param.split(":")[1].split("/")[1]
            elif "cтроение" in param:
                material = param.split(":")[1]
            elif "Застройщик" in param or "Дата сдачи" in param or "Стадия строительства" in param:
                new_block = True
                add_info += param.split(":")[1] + ";"

        if new_block:
            block_type = "Новостройка " + add_info
        else:
            block_type = "Вторичка"
    except Exception as e:
        print(e)
    return block_type, total_area, total_floors, material


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


def get_apartment_data(html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    address = "".join(title.split(",")[1:]).strip()
    rooms_number = title.split(",")[0]
    block_type, total_area, total_floors, material = get_apartment_params(soup)
    price = get_price(soup)
    selling_type = get_selling_type(soup)  # чистая продажа/ипотека/без посредников
    # images = get_photos(soup)
    # description = get_description(soup)
    # phone = get_seller_phone(soup)
    # date = get_date(soup)

    return [address, price, selling_type, block_type, rooms_number, total_area, total_floors, material]


def crawl_page(html, category, sell_type):
    soup = BeautifulSoup(html, "lxml")
    offers = soup.find_all("a", class_="site3adv")
    for offer in offers:
        try:
            url = "http://kvadrat64.ru/" + offer.get("href")
            data = []
            if category == "apartments":
                data = get_apartment_data(get_html(url))
            # elif category == "commercials":
            #     data = get_commercial_data(get_html(url))
            # elif category == "cottages":
            #     data = get_cottage_data(get_html(url))

            data.insert(1, sell_type)
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
        url_gen = category_url[:category_url.rfind("-") + 1] + str(page) + ".html"
        crawl_page(get_html(url_gen), category_name, sell_type)


def main():
    with open("kvadrat_apartments.csv", "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(["Адрес", "Тип сделки", "Тип дома", "Количество комнат", "Цена",
                         "Общая площадь", "Количество этажей", "Материал стен", "Тип продажи"
                         "Фотографии", "Описание", "Номер телефона", "Дата"])

    url_apartments_sell = "http://kvadrat64.ru/sellflatbank-50-1.html"
    parse(url_apartments_sell, "apartments", "Продажа")


if __name__ == "__main__":
    main()
