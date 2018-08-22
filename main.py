import avito_parsing
import irr_parsing
import kvadrat64_parsing
import ya_realty_parsing
import cian_parsing
import youla_parsing
import threading
import os

if os.path.isfile("total_data.txt"):
    os.remove("total_data.txt")

if os.path.isfile("logs.txt"):
    os.remove("logs.txt")

avito = avito_parsing.main()
irr = irr_parsing.main()
kvadrat = kvadrat64_parsing.main()
ya = ya_realty_parsing.main()
cian = cian_parsing.main()
youla = youla_parsing.main()

t1 = threading.Thread(target=kvadrat)
t2 = threading.Thread(target=irr)
t3 = threading.Thread(target=ya)
t4 = threading.Thread(target=youla)
t5 = threading.Thread(target=cian)
t6 = threading.Thread(target=avito)

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
t6.join()
