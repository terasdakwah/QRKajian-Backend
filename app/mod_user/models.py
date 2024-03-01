from app import db
from datetime import datetime, timedelta

class User(db.Document):
    '''
    tipe:
    0 = User pasif
    1 = User aktif
    3 = Pemilik
    99 = Superuser
    100 = Blokir
    '''
    password = db.StringField()
    tipe = db.IntField()
    name    = db.StringField()
    no_hp   = db.StringField()
    tanggallahir = db.DateTimeField(default=datetime.strptime("1945-08-17", "%Y-%m-%d"))
    gender = db.StringField(default="")
    provinsi     = db.ObjectIdField(default=None)
    kabupaten    = db.ObjectIdField(default=None)
    kecamatan    = db.ObjectIdField(default=None)
    pekerjaaan = db.StringField(default="")
    instansi = db.StringField(default="")
    hobi = db.StringField(default="")
    poin = db.IntField(default=0)
    sedekah = db.BooleanField(default=False)

    created    = db.DateTimeField(default=datetime.strptime("1945-08-17", "%Y-%m-%d"))
    modified   = db.DateTimeField(default=datetime.strptime("1945-08-17", "%Y-%m-%d"))

class Provinces(db.Document):
    name = db.StringField()
    code = db.IntField()

class Regencies(db.Document):
    province = db.ObjectIdField()
    name = db.StringField()
    code = db.IntField()

class Districts(db.Document):
    regency = db.ObjectIdField()
    name = db.StringField()
    code = db.IntField()