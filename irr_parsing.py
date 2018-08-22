import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import datetime
import base64


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
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_address\n")
        address = "Не указано"
    return address


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
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_price\n")
        price = "Не указано"
    return price


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
        relative_date = soup.find("div", class_="productPage__createDate").find("span").text.strip().split(",")
        if relative_date[0] == "сегодня":
            date = str(datetime.datetime.today()).split()[0] + relative_date[1]
        else:
            date = str(datetime.datetime.today() - datetime.timedelta(days=2)).split()[0] + relative_date[1]
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
    rooms_number, floor, total_area, kitchen_area, living_area, furnish = ["Не указано"] * 6
    try:
        building_params = []
        divs = soup.find_all("div", class_="productPage__infoColumnBlock js-columnBlock")
        for i in range(len(divs)):
            building_params.extend(divs[i].find_all("li", class_="productPage__infoColumnBlockText"))

        for i in range(len(building_params)):
            info = building_params[i].text.strip()
            if "Этаж:" in info:
                floor = info.split(":")[1].strip()
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
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_apartment_params\n")
    return rooms_number, floor, total_area, kitchen_area, living_area, furnish


def get_commercial_params(soup):
    building_type, parking, ceilings, area = ["Не указано"] * 4
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
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_commercial_params\n")
    return building_type, parking, ceilings, area


def get_cottage_params(soup):
    house_area, material, total_floors, land_area, status, comforts = ["Не указано"] * 6
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
    except Exception as e:
        with open("logs.txt", "a", encoding="utf8") as file:
            file.write(str(e) + " irr get_cottage_params\n")
    return house_area, material, total_floors, land_area, status, comforts


def get_apartment_data(html):
    soup = BeautifulSoup(html, "lxml")

    #title = get_title(soup)
    address = get_address(soup)
    material = get_material(soup)
    rooms_number, floor, total_area, kitchen_area, living_area, furnish = get_apartment_params(soup)
    price = get_price(soup)
    seller_type, seller_name = get_seller_info(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(soup)

    return [address, price, material, rooms_number, floor, total_area, kitchen_area, living_area, furnish,
            seller_type, images, description, seller_name, phone]


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

    address = get_address(soup)
    building_type, parking, ceilings, area = get_commercial_params(soup)
    price = get_price(soup)
    seller_type, seller_name = get_seller_info(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(soup)

    return [address, price, object_type, building_type, parking, ceilings, area, seller_type, images,
            description, seller_name, phone]


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

    address = get_address(soup)
    price = get_price(soup)
    house_area, material, total_floors, land_area, status, comforts = get_cottage_params(soup)
    _, seller_name = get_seller_info(soup)
    date = get_date(soup)
    images = get_photos(soup)
    description = get_description(soup)
    phone = get_seller_phone(soup)

    return [address, price, object_type, house_area, material, total_floors, land_area, status, comforts,
            images, description, date, seller_name, phone]


def crawl_page(first_offer, html, category, sell_type):
    soup = BeautifulSoup(html, "lxml")
    offers = soup.find("div", class_="listing js-productGrid ").find_all("div", class_="listing__item")
    for offer in offers:
        try:
            date = offer.find("span", class_="listing__itemDate").find("div", class_="updateProduct").text.strip()
            if date == date_break_point:
                print("Парсинг завершен")
                return True

            url = offer.find("div", class_="listing__itemTitleWrapper").find("a", class_="listing__itemTitle").get("href")
            print(url)

            data = []
            if category == "apartments":
                data = get_apartment_data(get_html(url))
                # записываем ключевую информацию, чтобы потом найти дубликаты
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s\n" % (data[0], data[3], data[5], url))
            elif category == "cottages":
                data = get_cottage_data(get_html(url))
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s--%s\n" % (data[0], data[5], data[3], url))
            elif category == "commercials":
                data = get_commercial_data(get_html(url))
                with open("total_data.txt", "a", encoding="utf8") as file:
                    file.write("%s--%s--%s\n" % (data[0], data[2], url))

            if first_offer:
                # сохраняем самую первую запись как точку выхода
                modifier = "w" if (category == "apartments" and sell_type == "Продажа") else "a"
                with open("breakpoints/irr.txt", modifier, encoding="utf8") as file:
                    file.write("%s--%s\n" % (data[0], data[1]))
                first_offer = False

            key_info = (data[0], data[1])

            if any(x == key_info for x in [break_apartment_sell, break_apartment_rent, break_commercials_sell,
                                           break_commercial_rent, break_cottage_sell, break_cottage_rent]):
                print("Парсинг завершен")
                return True

            data.insert(1, sell_type)
            print(data)

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
    # на сайте есть разделения продажа/аренда
    # сначала парсим страницу с предложениями продажи
    url_apartments_sell = "https://saratovskaya-obl.irr.ru/real-estate/apartments-sale/sort/date_sort:desc/"
    parse(url_apartments_sell, "apartments", "Продажа")

    url_apartments_rent = "https://saratovskaya-obl.irr.ru/real-estate/rent/sort/date_sort:desc/"
    parse(url_apartments_rent, "apartments", "Аренда")

    url_commercials_sell = "https://saratovskaya-obl.irr.ru/real-estate/commercial-sale/sort/date_sort:desc/"
    parse(url_commercials_sell, "commercials", "Продажа")

    url_commercials_rent = "https://saratovskaya-obl.irr.ru/real-estate/commercial/sort/date_sort:desc/"
    parse(url_commercials_rent, "commercials", "Аренда")

    url_cottages_sell = "https://saratovskaya-obl.irr.ru/real-estate/out-of-town/sort/date_sort:desc/"
    parse(url_cottages_sell, "cottages", "Продажа")

    url_cottages_rent = "https://saratovskaya-obl.irr.ru/real-estate/out-of-town-rent/sort/date_sort:desc/"
    parse(url_cottages_rent, "cottages", "Аренда")


if __name__ == "__main__":
    # на каких записях останавливаться
    with open("breakpoints/irr.txt", "r", encoding="utf8") as file:
        break_apartment_sell, break_apartment_rent, break_commercials_sell, break_commercial_rent, break_cottage_sell, break_cottage_rent = [tuple(x.strip().split("--")) for x in file.readlines()]

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

    main()
