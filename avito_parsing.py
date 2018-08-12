import requests
from bs4 import BeautifulSoup
import csv
import time
import random
#from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from urllib.parse import urljoin
from fake_useragent import UserAgent


def get_html(url):
    #request = req_proxy.generate_proxied_request(url)
    return requests.get(url, headers={"User-Agent": UserAgent().chrome}).text


def get_total_pages(html):
    soup = BeautifulSoup(html, "lxml")
    pages = soup.find("div", class_="pagination-pages clearfix").find_all("a", class_="pagination-page")[-1].get("href")
    total_pages = int(pages.split("=")[1].split("&")[0])
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
        price = soup.find("span", class_="price-value-string js-price-value-string").text.strip()
        if "за сутки" in price:
            sell_type = "Аренда: посуточно"
        elif "в месяц" in price:
            sell_type = "Аренда: длительный срок"
        else:
            sell_type = "Продажа"
            price = soup.find("span", class_="js-item-price").text.strip() + " ₽"
    except:
        sell_type = "Не указано"
        price = "Не указано"
    return sell_type, price


def get_params(soup):
    params = soup.find_all("li", class_="item-params-list-item")
    try:
        rooms_number = params[0].text.split(":")[1].strip()
    except:
        rooms_number = "Не указано"
    try:
        floor_number = params[1].text.split(":")[1].strip()
    except:
        floor_number = "Не указано"
    try:
        total_floors = params[2].text.split(":")[1].strip()
    except:
        total_floors = "Не указано"
    try:
        block_type = params[3].text.split(":")[1].strip()
    except:
        block_type = "Не указано"
    try:
        total_area = params[4].text.split(":")[1].strip()
    except:
        total_area = "Не указано"
    try:
        kitchen_area = params[5].text.split(":")[1].strip()
    except:
        kitchen_area = "Не указано"
    try:
        living_area = params[6].text.split(":")[1].strip()
    except:
        living_area = "Не указано"
    return rooms_number, floor_number, total_floors, block_type, total_area, kitchen_area, living_area


def get_seller_info(soup):
    try:
        seller_type = soup.find("div", class_="seller-info-value").find_all("div")[-1].text.strip()
        seller_name = seller_type.find("div", class_="seller-info-name").find("a").text.strip()
        if seller_type != "Частное лицо":
            seller_type = "Посредник"
        else:
            seller_type = "Собственник"
    except:
        seller_type = "Не указано"
        seller_name = "Не указано"
    return seller_type, seller_name


def get_photos(soup):
    try:
        images = []
        images_list = soup.find("ul", class_="gallery-list js-gallery-list").find_all("li", class_="gallery-list-item js-gallery-list-item")
        for image in images_list:
            link = image.find("span").get("style").split(":")[1].strip()[4:-2]
            images.append(link)
        images = "\n".join(images)
    except:
        images = "Не указано"
    return images


def get_description(soup):
    try:
        description = soup.find("div", class_="item-description-text").find("p").text.strip()
    except:
        description = "Не указано"
    return description


def get_seller_phone(soup):
    pass


def crawl_page(html):
    soup = BeautifulSoup(html, "lxml")
    offers = soup.find("div", class_="catalog-list").find_all("div", class_="item_table")
    for offer in offers:
        try:
            if offer.find("div", class_="js-item-date c-2").text.strip() == break_point:
                print("Парсинг квартир с avito завершен")
                break
            url = "https://avito.ru" + offer.find("div", class_="description").find("h3").find("a").get("href")
            data = get_apartment_data(get_html(url))
            if data is not None:
                write_csv(data)
            time.sleep(random.uniform(7, 10))

            # querying phone
            # url = "https://m.avito.ru/balakovo/kvartiry/2-k_kvartira_87_m_58_et._1653308606"
            # headers = {
            #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'}
            #
            # session = requests.session()
            # resp = session.get(url, headers=headers)
            #
            # html = get_html(resp.content)
            # href = html.xpath(".//*[@class='clearfix']/a[1]/@href")[0]
            #
            # url = urljoin(resp.url, href + '?async')
            # headers["Referer"] = url
            # resp = session.get(url, headers=headers)
            #
            # html = get_html(resp.content)
            # phone = html.xpath(".//*[@class='clearfix']/a[1]/span/text()")[0]
            # print(phone)
            # break
        except:
            url = "Не указано"


def get_apartment_data(html):
    soup = BeautifulSoup(html, "lxml")

    title = get_title(soup)
    if "сниму" not in title.lower():
        address = get_address(soup)
        sell_type, price = get_selling_info(soup)
        rooms_number, floor_number, total_floors, block_type, total_area, kitchen_area, living_area = get_params(soup)
        seller_type, seller_name = get_seller_info(soup)
        images = get_photos(soup)
        description = get_description(soup)

        return (address, sell_type, block_type, rooms_number, floor_number, total_floors,
              total_area, kitchen_area, living_area, price, seller_type, images,
              description, seller_name)
    return None


def write_csv(data):
    with open("avito_apartments.csv", "a") as csv_file:
        writer = csv.writer(csv_file)
        writer.write_row(data)


def main():
    url_apartments = "https://www.avito.ru/saratovskaya_oblast/kvartiry?p=1&s=104&s_trg=3&bt=1"
    base_url = "https://www.avito.ru/saratovskaya_oblast/kvartiry?"
    page_part = "p="
    parameters_part = "&s=104&s_trg=3&bt=1"

    total_pages = get_total_pages(get_html(url_apartments))

    # for page in range(1, total_pages + 1):
    #     url_gen = base_url + page_part + str(page) + parameters_part
    #     crawl_page(get_html(url_gen))

    for page in range(1):
        url_gen = base_url + page_part + str(page) + parameters_part
        crawl_page(get_html(url_gen))

    #print(total_pages)


if __name__ == "__main__":
    #req_proxy = RequestProxy()
    break_point = "1 день назад"
    main()
