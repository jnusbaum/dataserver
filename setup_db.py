from models import *

db.bind(provider='postgres', host='192.168.0.134',
        database='automation',
        user='rjn',
        password='zaxxon')

db.generate_mapping(check_tables=True)
