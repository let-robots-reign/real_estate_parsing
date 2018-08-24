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

if os.path.isfile("total_data.txt"):
    os.remove("total_data.txt")

if os.path.isfile("logs.txt"):
    os.remove("logs.txt")

t1 = Process(target=kvadrat64_parsing.main).start()
t2 = Process(target=irr_parsing.main).start()
t3 = Process(target=youla_parsing.main).start()
t4 = Process(target=ya_realty_parsing.main).start()
t5 = Process(target=cian_parsing.main).start()
t6 = Process(target=avito_parsing.main).start()

total_data = {}

with open("total_data.txt", "r", encoding="utf8") as file:
    for line in file.readlines():
        data = line.strip().split("--")
        params = tuple(data[:-1])
        url = data[-1]
        total_data[params] = list(set(total_data.get(params, []) + [url]))

for data in total_data:
    if len(total_data[data]) > 1:
        db.insert_data("dublicates", [", ".join(data), "\n".join(total_data[data])])
