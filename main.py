# -*- coding: utf-8 -*-
import gc
from multiprocessing import Process
import os
import datetime
from database import DataBase

t1, t2, t3, t4, t5, t6 = [None] * 6


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    global t1, t2, t3, t4, t5, t6
    if all(p is not None for p in [t1, t2, t3, t4, t5, t6]):
        for p in [t1, t2, t3, t4, t5, t6]:
            if p.is_alive():
                p.terminate()
                p.join()

    import avito_parsing
    import irr_parsing
    import kvadrat64_parsing
    import ya_realty_parsing
    import cian_parsing
    import youla_parsing

    cls()
    print("Job started", datetime.datetime.today())

    db = DataBase()
    db.create_table("Квартиры")
    db.create_table("Дома")
    db.create_table("Коммерческая_недвижимость")
    db.create_table("Участки")
    db.create_table("Дубликаты")

    if os.path.isfile("logs.txt"):
        os.remove("logs.txt")

    total_data = {}
    try:
        if os.path.isfile("total_data.txt"):
            with open("total_data.txt", "r", encoding="utf8") as file:
                for line in file.readlines():
                    data = line.strip().split("--")
                    params = tuple(data[:-1])
                    url = data[-1]
                    total_data[params] = list(set(total_data.get(params, []) + [url]))

            for data in total_data:
                if all(x != "Не указано" for x in data):  # avoid writing dummy records
                    if len(total_data[data]) > 1:
                        db.insert_data("Дубликаты", [", ".join(data), "\n".join(total_data[data])])
    except Exception as e:
        print(e)

    if os.path.isfile("total_data.txt"):
        os.remove("total_data.txt")

    t1 = Process(target=ya_realty_parsing.main)
    t2 = Process(target=irr_parsing.main)
    t3 = Process(target=youla_parsing.main)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()

    t4 = Process(target=kvadrat64_parsing.main)
    t5 = Process(target=cian_parsing.main)
    t6 = Process(target=avito_parsing.main)
    t4.start()
    t5.start()
    t6.start()
    t4.join()
    t5.join()
    t6.join()

    db.close()
    gc.collect()
    print("Job finished", datetime.datetime.today())


if __name__ == '__main__':
    import schedule
    import time

    schedule.every().day.at("10:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
