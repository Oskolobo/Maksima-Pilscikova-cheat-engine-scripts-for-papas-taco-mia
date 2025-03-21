from peewee import Model, SqliteDatabase, FloatField, IntegerField

db = SqliteDatabase('data.db')

class DataEntry(Model):
    name = FloatField()
    age = IntegerField()
    country = FloatField()

    class Meta:
        database = db