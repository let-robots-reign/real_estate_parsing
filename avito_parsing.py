import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from pytesseract import image_to_string
import pytesseract
import os
import sys


def get_html(url):
    return requests.get(url, headers={"User-Agent": UserAgent().chrome}).text


def get_total_pages(html):
    soup = BeautifulSoup(html, "lxml")
    try:
        pages = soup.find("div", class_="pagination-pages clearfix").find_all("a", class_="pagination-page")[-1].get("href")
        total_pages = int(pages.split("=")[1].split("&")[0])
    except Exception as e:
        print("Ошибка в get_total_pages")
        print(e)
        sys.exit(0)
    return total_pages


def get_title(soup):
    try:
        title = soup.find("span", class_="title-info-title-text").text.strip()
    except:
        title = "Не указано"
    return title


def get_address(soup):
    try:
        address = soup.find("span", itemprop="streetAddress").text.strip()
    except:
        address = "Не указано"
    return address


def get_selling_info(soup):
    try:
        per_meter = False
        price = soup.find("span", class_="price-value-string js-price-value-string").text.strip()
        if "за сутки" in price:
            sell_type = "Аренда: посуточно"
        elif "в месяц" in price:
            sell_type = "Аренда: длительный срок"
            if "за " in price:
                per_meter = True
        else:
            sell_type = "Продажа"
        price = soup.find("span", class_="js-item-price").text.strip()
        # ошибка кодировки при записи, собираем сообщение вручную
        if sell_type == "Аренда: посуточно":
            price = "от " + price + " за сутки"
        elif sell_type == "Аренда: длительный срок":
            if per_meter:
                price = price + " в месяц за м2"
            else:
                price = price + " в месяц"
    except:
        sell_type = "Не указано"
        price = "Не указано"
    return sell_type, price


def get_deposit(soup):
    try:
        deposit = soup.find("div", class_="item-price-sub-price").text.strip()
    except:
        deposit = "Не указано"
    return deposit


def get_seller_type(soup):
    try:
        seller_type = soup.find("div", class_="seller-info-prop seller-info-prop_short_margin")
        if seller_type is not None:
            seller_type = "Посредник"
        else:
            seller_type = "Собственник"
    except:
        seller_type = "Не указано"
    return seller_type


def get_seller_name(soup):
    try:
        seller_name = soup.find("div", class_="seller-info-name").find("a").text.strip()
    except:
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
        except:
            images = "Не указано"
    return images


def get_description(soup):
    try:
        description = soup.find("div", class_="item-description-text").find("p").text.strip()
    except:
        description = "Не указано"
    return description


def get_seller_phone(url):
    # телефон показывается в виде картинки, используем selenium и pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"D:\Programs\Tesseract-OCR\tesseract.exe"

    driver = webdriver.Chrome(executable_path=chrome_driver)

    driver.get(url)
    button = driver.find_element_by_xpath('//a[@class="button item-phone-button js-item-phone-button '
                                          'button-origin button-origin-blue button-origin_full-width '
                                          'button-origin_large-extra item-phone-button_hide-phone '
                                          'item-phone-button_card js-item-phone-button_card"]')
    button.click()
    driver.implicitly_wait(5)
    driver.save_screenshot("phone_number.png")

    image = driver.find_element_by_xpath('//div[@class="item-phone-big-number js-item-phone-big-number"]//*')

    cropped = Image.open("phone_number.png")
    x, y = image.location["x"], image.location["y"]
    width, height = image.size["width"], image.size["height"]
    cropped.crop((x - 50, y, x - 50 + width, y + height)).save("phone.gif")

    phone = Image.open("phone.gif")
    phone_text = image_to_string(phone)

    driver.quit()

    return phone_text


def get_apartment_params(soup):
    rooms_number, floor_number, total_floors, block_type, total_area, kitchen_area, living_area = ["Не указано"] * 7
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
                block_type = info.split(":")[1].strip()
            elif "Общая площадь" in info:
                total_area = info.split(":")[1].split("м²")[0].strip()
            elif "Площадь кухни" in info:
                kitchen_area = info.split(":")[1].split("м²")[0].strip()
            elif "Жилая площадь" in info:
                living_area = info.split(":")[1].split("м²")[0].strip()
    except:
        pass
    return rooms_number, floor_number, total_floors, block_type, total_area, kitchen_area, living_area


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
    except:
        pass
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
                distance = info.split("км")[0].strip() + " км"
            elif "Площадь" in label:
                area = info.split("сот")[0].strip() + " сот"
    except:
        pass
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
    except:
        pass
    return office_class, area


def get_apartment_data(url, html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower() and "куплю" not in title.lower():
        address = get_address(soup)
        sell_type, price = get_selling_info(soup)
        rooms_number, floor_number, total_floors, block_type, total_area, kitchen_area, living_area = get_apartment_params(soup)
        seller_type = get_seller_type(soup)
        seller_name = get_seller_name(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url)

        return (address, sell_type, block_type, rooms_number, floor_number, total_floors, total_area,
                kitchen_area, living_area, price, seller_type, images, description, seller_name, phone)
    return None


def get_cottage_data(url, html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower() and "куплю" not in title.lower():
        address = get_address(soup)
        sell_type, price = get_selling_info(soup)
        house_type, total_floors, distance, material, total_area, land_area = get_cottage_params(soup)
        seller_type = get_seller_type(soup)
        seller_name = get_seller_name(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url)

        return (address, sell_type, material, total_floors, total_area, land_area, price, distance,
                seller_type, images, description, seller_name, phone)
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

        address = get_address(soup)
        sell_type, price = get_selling_info(soup)

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

        return (address, sell_type, deposit, land_type, distance, area, price, seller_type, images,
                description, seller_name, phone)
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

        address = get_address(soup)
        sell_type, price = get_selling_info(soup)

        if "Аренда" in sell_type:
            deposit = get_deposit(soup)
        else:
            deposit = "Не аренда"

        # если не офис, не заполняем поле office_class
        if object_type == "Офисное помещение":
            office_class, area = get_commercial_params(soup)
        else:
            _, area = get_commercial_params(soup)
            office_class = "Не офис"

        seller_type = get_seller_type(soup)
        seller_name = get_seller_name(soup)
        images = get_photos(soup)
        description = get_description(soup)
        phone = get_seller_phone(url)

        return (address, sell_type, deposit, object_type, office_class, area, price, seller_type,
                images, description, seller_name, phone)
    return None


def crawl_page(html, category):
    soup = BeautifulSoup(html, "lxml")
    offers = soup.find("div", class_="catalog-list").find_all("div", class_="item_table")
    for offer in offers:
        try:
            # TODO: проверить еще на дубликат
            if offer.find("div", class_="js-item-date c-2").text.strip() == break_point:
                print("Парсинг завершен")
                break
            url = "https://avito.ru" + offer.find("div", class_="description").find("h3").find("a").get("href")

            data = []
            if category == "apartments":
                data = get_apartment_data(url, get_html(url))
            elif category == "cottages":
                data = get_cottage_data(url, get_html(url))
            elif category == "lands":
                data = get_land_data(url, get_html(url))
            elif category == "commercials":
                data = get_commercial_data(url, get_html(url))

            print(data)

            time.sleep(random.uniform(5, 8))
        except Exception as e:
            print("Ошибка в crawl_page")
            print(e)
            #sys.exit(0)


def parse(category_url, base_url, category_name):
    page_part = "p="
    parameters_part = "&s=104&s_trg=3&bt=1"

    total_pages = get_total_pages(get_html(category_url))

    # for page in range(1, total_pages + 1):
    #     url_gen = base_url + page_part + str(page) + parameters_part
    #     crawl_page(get_html(url_gen))

    for page in range(1):
        url_gen = base_url + page_part + str(page) + parameters_part
        crawl_page(get_html(url_gen), category_name)

    #print(total_pages)


def main():
    url_apartments = "https://www.avito.ru/saratovskaya_oblast/kvartiry?p=1&s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/kvartiry?"
    parse(url_apartments, base_url, "apartments")

    url_cottages = "https://www.avito.ru/saratovskaya_oblast/doma_dachi_kottedzhi?s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/doma_dachi_kottedzhi?"
    parse(url_cottages, base_url, "cottages")

    url_lands = "https://www.avito.ru/saratovskaya_oblast/zemelnye_uchastki?s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/zemelnye_uchastki?"
    parse(url_lands, base_url, "lands")

    url_commercials = "https://www.avito.ru/saratovskaya_oblast/kommercheskaya_nedvizhimost?s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/kommercheskaya_nedvizhimost?"
    parse(url_commercials, base_url, "commercials")


if __name__ == "__main__":
    break_point = "1 день назад"  # на каких записях останавливаться

    # defining chrome options for selenium
    # options = Options()
    # options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    # options.add_argument('--disable-gpu')
    # options.add_argument('--headless')
    #
    chrome_driver = os.getcwd() + "\\chromedriver.exe"

    main()
