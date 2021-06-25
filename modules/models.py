from peewee import *
import datetime
from credentials import *

db = PostgresqlDatabase(bd_name, host=bd_host, port=5437, user=bd_username, password=bd_password, autorollback=True)


class BaseModel(Model):
    class Meta: database = db
    id = AutoField()


class User(BaseModel):
    phone = CharField(max_length=45, null=True, default=None)
    tg_id = CharField(max_length=45)
    cash = IntegerField(default=0)
    state = TextField(default="{}")
    root_message = IntegerField(default=None, null=True)
    message_list = TextField(default='[]')


class Ticket(BaseModel):
    user = ForeignKeyField(User)
    kind = CharField(max_length=45)
    city_from = CharField(null=True, max_length=45, default=None)
    city_to = CharField(null=True, max_length=45, default=None)
    date = DateField(null=True, default=None)
    time = TimeField(null=True, default=None)
    cost = CharField(null=True, max_length=45, default=None)
    places = IntegerField(default=0) 
    phone = TextField(null=True, default=None)
    comment = TextField(null=True, default=None)
    status = CharField(max_length=45, default="creating") # pending complete creating
    pub_date = DateTimeField(default=lambda: datetime.datetime.now())
    demo_message = IntegerField(null=True, default=None)
    currency = CharField(max_length=2, default="")


with db:
    db.create_tables([User, Ticket])


