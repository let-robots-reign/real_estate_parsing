import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


def get_html(url):
    req = requests.get(url, headers={"User-Agent": UserAgent().chrome})
    return req.text.encode(req.encoding)


def get_title(soup):
    try:
        title = soup.find("h1", class_="offer-card__header-text").text.strip()
    except:
        title = "Не указано"
    return title


def get_address(soup):
    try:
        address = soup.find("h2", class_="offer-card__address ellipsis").text.strip()
    except Exception as e:
        print(str(e) + " address")
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
        print(e, " block_type")
        block_type = "Не указано"
    return block_type


def get_price(soup):
    try:
        price = soup.find("h3", class_="offer-price offer-card__price offer-card__price").get("title")
    except Exception as e:
        print(str(e) + " price")
        price = "Не указано"
    return price


def get_selling_type(soup):
    try:
        selling_type = soup.find("div", class_="offer-card__terms").text.strip()
    except Exception as e:
        print(str(e) + " selling_type")
        selling_type = "Не указано"
    return selling_type


def get_seller_type(soup):
    try:
        seller_type = soup.find("div", class_="offer-card__author-note").text.strip()
    except Exception as e:
        print(str(e) + " seller_type")
        seller_type = "Не указано"
    return seller_type


def get_photos(soup):
    try:
        images = []
        images_list = soup.find("div", class_="offer-card__photos-wrapper").find_all("a", class_="offer-card__react-gallery-photo")
        for image in images_list:
            link = "https://realty.yandex.ru" + image.get("href")
            images.append(link)
        images = "\n".join(images)
    except Exception as e:
        print(str(e) + " images")
        images = "Не указано"
    return images


def get_description(soup):
    try:
        description = soup.find("div", class_="offer-card__desc-text").text.strip()
    except Exception as e:
        print(str(e) + " description")
        description = "Не указано"
    return description


def get_date(soup):
    try:
        date = soup.find("div", class_="OffersSerpItem__publish-date").text.strip()
        if "назад" in date:
            time_passed = int(date.split()[0])
            if "минут" in date:
                date = str(datetime.datetime.today() - datetime.timedelta(minutes=time_passed)).split()[0]
            elif "часов" in date:
                date = str(datetime.datetime.today() - datetime.timedelta(hours=time_passed))
    except Exception as e:
        print(str(e) + " date")
        date = "Не указано"
    return date


def get_seller_phone(url):
    phone = "Не указано"
    # телефон появляется динамически, используем selenium
    try:
        driver = webdriver.Chrome(executable_path=chrome_driver)

        driver.get(url)
        button = driver.find_element_by_xpath('//button[@class="button button_theme_new-action stat phones__button '
                                              'i-bem stat_ecommerce_yes stat_conversion_yes stat_criteo_yes '
                                              'stat_goal_yes stat_js_inited button_js_inited"]')
        button.click()
        time.sleep(3)
        phone = driver.find_element_by_xpath('//div[@class="helpful-info__contact-phones-string"').text
    except Exception as e:
        print(str(e) + " phone")
    return phone


def get_apartment_params(soup):
    rooms_number, total_floors, total_area, material, year = ["Не указано"] * 5
    try:
        params = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-name")]
        values = [x.text.strip() for x in soup.find_all("div", class_="offer-card__feature-value")]
        pairs = dict(zip(params, values))
        for param, value in pairs:
            if "Количество комнат" in param:
                rooms_number = value
            elif "Год постройки" in param:
                year = value
            elif "Этаж" in param:
                total_floors = value
            elif "Общая площадь" in param:
                total_area = value
            elif "Тип здания" in param:
                material = value
    except Exception as e:
        print(str(e) + " params")
    return rooms_number, total_floors, total_area, material, year


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

    return [address, block_type, rooms_number, price, total_area, total_floors, material,
            year, selling_type, images, description, seller_type, phone]


def crawl_page(html, category, sell_type):
    soup = BeautifulSoup(html, "lxml")
    # так как пагинация динамическая и мы не можем получить число страниц, проверяем, есть ли на странице объявления
    no_records = soup.find("div", class_="OffersSerpNotFound")
    if no_records is not None:
        print("Страницы закончились")
        return

    offers = soup.find("ol", class_="OffersSerp__list").find_all("li", class_="OffersSerp__list-item_type_offer")
    for offer in offers:
        try:
            # TODO: проверить еще на дубликат
            if offer.find("div", class_="OffersSerpItem__publish-date").text.strip() == break_point:
                print("Парсинг завершен")
                return
            url = "https://realty.yandex.ru" + offer.find("a", class_="OffersSerpItem__link").get("href")

            data = []
            if category == "apartments":
                data = get_apartment_data(get_html(url), url)
            # elif category == "commercials":
            #     data = get_commercial_data(get_html(url))
            # elif category == "cottages":
            #     data = get_cottage_data(get_html(url))

            date = get_date(soup)
            data.append(date)
            data.insert(1, sell_type)
            print(*data, sep="\n")
            print("--------------------------------------")

        except Exception as e:
            print(e)
            print("Ошибка в crawl_page")

        time.sleep(random.uniform(8, 11))


def parse(category_url, category_name, sell_type):

    # for page in range(1, total_pages + 1):
    #     url_gen = base_url + page_part + str(page) + parameters_part
    #     crawl_page(get_html(url_gen))

    for page in range(2):
        url_gen = category_url[:category_url.rfind("=") + 1] + str(page)
        crawl_page(get_html(url_gen), category_name, sell_type)


def main():
    url_apartments_sell = "https://realty.yandex.ru/saratovskaya_oblast/kupit/kvartira/?sort=DATE_DESC&page=0"
    parse(url_apartments_sell, "apartments", "Продажа")


if __name__ == "__main__":
    break_point = "вчера"  # на каких записях останавливаться

    # defining chrome options for selenium
    # options = Options()
    # options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    # options.add_argument('--disable-gpu')
    # options.add_argument('--headless')
    #
    chrome_driver = os.getcwd() + "\\chromedriver.exe"

    main()
