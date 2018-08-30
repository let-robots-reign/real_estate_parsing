# -*- coding: utf-8 -*-

import avito_parsing
import irr_parsing
import kvadrat64_parsing
import ya_realty_parsing
import cian_parsing
import youla_parsing
from multiprocessing import Process
import os
from database import DataBase

db = DataBase()
db.create_table("dublicates")

if os.path.isfile("logs.txt"):
    os.remove("logs.txt")


def main():
    print("Job started")
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
                if ", ".join(data) != "Не указано, Не указано, Не указано":  # avoid writing dummy records
                    if len(total_data[data]) > 1:
                        db.insert_data("dublicates", [", ".join(data), "\n".join(total_data[data])])
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

    print("Job finished")


if __name__ == '__main__':
    import schedule
    import time

    schedule.every().day.at("11:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)