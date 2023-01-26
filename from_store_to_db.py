import json
from playhouse.reflection import generate_models
from peewee import *

db = PostgresqlDatabase('transfers', user='admin', password='admin231415',
                        host='45.143.93.237', port=5432)

models = generate_models(db)
globals().update(models)

data = json.load(open(r'C:\Users\reshi\Projects\pythonProject\transfers\store.json', 'r', encoding='utf-8'))

with db:
    try:
        clubs.insert_many(data['clubs'].values()).execute()
        leagues.insert_many(data['leagues'].values()).execute()
        clubs_leagues.insert_many(data['clubs_leagues'].values()).execute()
    except IntegrityError as ex:
        print(ex)
