from peewee import Model, SqliteDatabase, CharField, IntegerField

db = SqliteDatabase('data.db')

class DataEntry(Model):
    name = CharField()
    age = IntegerField()
    country = CharField()

    class Meta:
        database = db