import mysql.connector
from mysql.connector import Error

host = "51.15.116.198"
database = "real_estate"
user = "root"
password = "root_estate"


class DataBase:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
            self.cursor = self.conn.cursor()
        except Error as error:
            print("Error while connecting to database", error)

    def create_table(self, category):
        if category == "avito_apartments":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS avito_apartments "
                                "(Адрес TEXT, Тип_сделки TEXT, Тип_дома TEXT, Количество_комнат TEXT, Этаж TEXT, "
                                "Количество_этажей TEXT, Общая_площадь TEXT, Площадь_кухни TEXT, Жилая_площадь TEXT, "
                                "Цена TEXT, Право_собственности TEXT, Фото TEXT, Описание TEXT, Имя_продавца TEXT, "
                                "Телефон TEXT);")
        elif category == "avito_cottages":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS avito_cottages "
                                "(Адрес TEXT, Тип_сделки TEXT, Материал_стен TEXT, Количество_этажей TEXT, "
                                "Общая_площадь TEXT, Площадь_участка TEXT, Цена TEXT, Расстояние_до_города TEXT, "
                                "Право_собственности TEXT, Фото TEXT, Описание TEXT, Имя_продавца TEXT, "
                                "Телефон TEXT);")
        elif category == "avito_lands":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS avito_lands "
                                "(Адрес TEXT, Тип_сделки TEXT, Залог TEXT, Категория_участка TEXT, "
                                "Расстояние_до_города TEXT, Площадь_участка TEXT, Цена TEXT, Право_собственности TEXT, "
                                "Фото TEXT, Описание TEXT, Имя_продавца TEXT, Телефон TEXT);")
        elif category == "avito_commercials":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS avito_commercials "
                                "(Адрес TEXT, Тип_сделки TEXT, Залог TEXT, Тип_объекта TEXT, Класс_здания TEXT, "
                                "Общая_площадь TEXT, Цена TEXT, Право_собственности TEXT, Фото TEXT, "
                                "Описание TEXT, Имя_продавца TEXT, Телефон TEXT);")

        elif category == "irr_apartments":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS irr_apartments "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Материал_стен TEXT, Количество_комнат TEXT, "
                                "Этаж TEXT, Общая_площадь TEXT, Площадь_кухни TEXT, Жилая_площадь TEXT, Отделка TEXT, "
                                "Право_собственности TEXT, Фото TEXT, Описание TEXT, Имя_продавца TEXT, Телефон TEXT);")
        elif category == "irr_cottages":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS irr_cottages "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_дома TEXT, Общая_площадь TEXT, "
                                "Материал_стен TEXT, Количество_этажей TEXT, Площадь_участка TEXT, "
                                "Категория_участка TEXT, Удобства TEXT, Фото TEXT, Описание TEXT, Дата TEXT, "
                                "Имя_продавца TEXT, Телефон TEXT);")
        elif category == "irr_commercials":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS irr_commercials "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_объекта TEXT, Тип_здания TEXT, "
                                "Парковка TEXT, Высота_потолков TEXT, Общая_площадь TEXT, Право_собственности TEXT, "
                                "Фото TEXT, Описание TEXT, Имя_продавца TEXT, Телефон TEXT);")

        elif category == "kvardat_apartments":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS kvadrat_apartments "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_дома TEXT, Количество_комнат TEXT, "
                                "Общая_площадь TEXT, Количество_этажей TEXT, Материал_стен TEXT, Тип_продажи TEXT, "
                                "Фото TEXT, Описание TEXT, Телефон TEXT, Дата TEXT);")
        elif category == "kvadrat_cottages":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS kvadrat_cottages "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_дома TEXT, Общая_площадь TEXT, "
                                "Тип_продажи TEXT, Материал_стен TEXT, Фото TEXT, Описание TEXT, "
                                "Телефон TEXT, Дата TEXT);")
        elif category == "kvadrat_commercials":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS kvadrat_commercials "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_объекта TEXT, Фото TEXT, "
                                "Описание TEXT, Телефон TEXT, Дата TEXT);")
        elif category == "kvadrat_dachas":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS kvadrat_dachas "
                                "(Адрес TEXT, Цена TEXT, Расстояние_до_города TEXT, Общая_площадь TEXT, "
                                "Фото TEXT, Описание TEXT, Телефон TEXT, Дата TEXT);")
        elif category == "kvadrat_lands_saratov":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS kvadrat_lands_saratov "
                                "(Адрес TEXT, Цена TEXT, Общая_площадь TEXT, "
                                "Фото TEXT, Описание TEXT, Телефон TEXT, Дата TEXT);")
        elif category == "kvadrat_lands_region":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS kvadrat_lands_region "
                                "(Адрес TEXT, Цена TEXT, Расстояние_до_города TEXT, Общая_площадь TEXT, "
                                "Фото TEXT, Описание TEXT, Телефон TEXT, Дата TEXT);")

        elif category == "ya_apartments":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS ya_apartments "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_дома TEXT, Количество_комнат TEXT, "
                                "Общая_площадь TEXT, Количество_этажей TEXT, Материал_стен TEXT, Год_постройки TEXT, "
                                "Тип_продажи TEXT, Фото TEXT, Описание TEXT, Право_собственности TEXT, Телефон TEXT, "
                                "Дата TEXT);")
        elif category == "ya_cottages":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS ya_cottages "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_дома TEXT, Общая_площадь TEXT, "
                                "Площадь_участка TEXT, Удобства TEXT, Год_постройки TEXT, Тип_продажи TEXT, "
                                "Фото TEXT, Описание TEXT, Телефон TEXT, Дата TEXT);")
        elif category == "ya_commercials":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS ya_commercials "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_объекта TEXT, Мебель TEXT, "
                                "Вход TEXT, Доп_информация TEXT, Телефон TEXT, Дата TEXT);")

        elif category == "cian_apartments":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS cian_apartments "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_дома TEXT, Количество_комнат TEXT, "
                                "Общая_площадь TEXT, Количество_этажей TEXT, Материал_стен TEXT, Год_постройки TEXT, "
                                "Тип_продажи TEXT, Фото TEXT, Описание TEXT, Право_собственности TEXT, Дата TEXT, "
                                "Телефон TEXT);")
        elif category == "cian_cottages":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS cian_cottages "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_дома TEXT, Общая_площадь TEXT, "
                                "Материал_стен TEXT, Площадь_участка TEXT, Категория_участка TEXT, Удобства TEXT, "
                                "Тип_продажи TEXT, Фото TEXT, Описание TEXT, Дата TEXT, Телефон TEXT);")
        elif category == "cian_commercials":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS cian_commercials "
                                "(Адрес TEXT, Тип_сделки TEXT, Цена TEXT, Тип_объекта TEXT, Класс_здания TEXT,"
                                "Этаж TEXT, Мебель TEXT, Вход TEXT, Фото TEXT, Описание TEXT, Дата TEXT, Телефон TEXT);")

        elif category == "youla_apartments":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS youla_apartments "
                                "(Адрес TEXT, Цена TEXT, Тип_сделки TEXT, Материал_стен TEXT, Лифт TEXT, "
                                "Год_постройки TEXT, Количество_комнат TEXT, Этаж TEXT, Количество_этажей TEXT, "
                                "Общая_площадь TEXT, Площадь_кухни TEXT, Ремонт TEXT, Право_собственности TEXT, "
                                "Фото TEXT, Описание TEXT, Имя_продавца TEXT, Телефон TEXT);")
        elif category == "youla_cottages":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS youla_cottages "
                                "(Адрес TEXT, Цена TEXT, Тип_сделки TEXT, Тип_дома TEXT, Общая_площадь TEXT, "
                                "Материал_стен TEXT, Количество_этажей TEXT, Количество_спален TEXT, "
                                "Площадь_участка TEXT, Категория_участка TEXT, Удобства TEXT, Фото TEXT, Описание TEXT,"
                                " Телефон TEXT, Дата TEXT);")

        elif category == "dublicates":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS dublicates (Заголовок TEXT, URL TEXT);")

    def insert_data(self, table_name, data):
        data_string = ', '.join(['%s'] * len(data))
        query = "INSERT INTO %s VALUES (%s);" % (table_name, data_string)
        self.cursor.execute(query, data)
        self.conn.commit()
