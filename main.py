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

kvadrat = kvadrat64_parsing.main()
irr = irr_parsing.main()
youla = youla_parsing.main()
ya = ya_realty_parsing.main()
cian = cian_parsing.main()
avito = avito_parsing.main()

t1 = Process(target=kvadrat).start()
t2 = Process(target=irr).start()
t3 = Process(target=youla).start()
t4 = Process(target=ya).start()
t5 = Process(target=cian).start()
t6 = Process(target=avito).start()

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
