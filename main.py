import avito_parsing
import irr_parsing
import kvadrat64_parsing
import ya_realty_parsing
import cian_parsing
import youla_parsing
from multiprocessing import Process
import os

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
