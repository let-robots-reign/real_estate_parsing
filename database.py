# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

# using sensitive data placeholders, replace it with passwords
host = "host"
database = "db"
user = "user"
password = "pass"


class DataBase:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
            self.cursor = self.conn.cursor()
        except Error as error:
            print("Error while connecting to database", error)

    def close(self):
        self.cursor.close()
        self.conn.close()

    def create_table(self, category):
        if category == "Квартиры":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Квартиры"
                                "(Город TEXT, Район TEXT, Улица TEXT, Номер_дома TEXT, "
                                "Тип_сделки TEXT, Срок_аренды TEXT, Цена TEXT, Тип_дома TEXT, Количество_комнат TEXT, "
                                "Общая_площадь TEXT, Количество_этажей TEXT, Материал_стен TEXT, Тип_продажи TEXT, "
                                "Фото TEXT, Описание TEXT, Дата TEXT, Телефон TEXT, Площадь_кухни TEXT, Жилая_площадь TEXT, "
                                "Этаж TEXT);")

        elif category == "Дома":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Дома"
                                "(Город TEXT, Район TEXT, Улица TEXT, Номер_дома TEXT, Тип_сделки TEXT, Срок_аренды TEXT, "
                                "Цена TEXT, Тип_дома TEXT, Площадь_дома TEXT, Удобства TEXT, Тип_продажи TEXT, "
                                "Фото TEXT, Описание TEXT, Дата TEXT, Телефон TEXT, Материал_стен TEXT, "
                                "Количество_этажей TEXT, Площадь_участка TEXT, Статус_участка TEXT, Имя_продавца TEXT);")

        elif category == "Коммерческая_недвижимость":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Коммерческая_недвижимость"
                                "(Город TEXT, Район TEXT, Улица TEXT, Номер_дома TEXT, Тип_сделки TEXT, Цена TEXT, "
                                "Тип_недвижимости TEXT, Класс_здания TEXT, Мебель TEXT, Вход TEXT, Общая_площадь TEXT, "
                                "Дата TEXT, Телефон TEXT, Фото TEXT, Описание TEXT, Имя_продавца TEXT);")

        elif category == "Участки":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Участки"
                                "(Город TEXT, Район TEXT, Улица TEXT, Тип_сделки TEXT, Залог TEXT, Статус_участка TEXT, "
                                "Расстояние_до_города TEXT, Площадь_участка TEXT, Цена TEXT, Право_собственности TEXT, "
                                "Фото TEXT, Описание TEXT, Имя_продавца TEXT, Телефон TEXT, Дата TEXT);")

        elif category == "Дубликаты":
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Дубликаты (Заголовок TEXT, URLs TEXT);")

    def insert_data(self, table_name, data):
        data_string = ', '.join(['%s'] * len(data))
        query = "INSERT INTO %s VALUES (%s);" % (table_name, data_string)
        self.cursor.execute(query, data)
        self.conn.commit()
