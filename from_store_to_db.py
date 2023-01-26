import json
from playhouse.reflection import generate_models
from peewee import *


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
